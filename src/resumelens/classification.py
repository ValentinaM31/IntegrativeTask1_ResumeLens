"""Profile recognition with complete deterministic automata and bucket order."""
from collections import deque
from functools import lru_cache
from importlib.resources import files
import json
from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from .catalog import load_catalog


def load_profiles():
    profiles = json.loads(files("resumelens").joinpath("profiles_design.json").read_text(encoding="utf-8"))
    if len(profiles) != 4 or len({profile["id"] for profile in profiles}) != 4:
        raise ValueError("Four distinct profiles are required")
    for profile in profiles:
        validate_profile(profile)
    return profiles


def validate_profile(profile):
    """Reject configurations that would make canonical ordering ambiguous."""
    known = {skill["canonical"] for skill in load_catalog()["skills"]}
    groups = profile["required_groups"]
    pairs = profile.get("required_pair_alternatives", [])
    if not groups or any(not isinstance(group, list) or not group for group in groups):
        raise ValueError("Required groups must be nonempty lists")
    if any(not isinstance(pair, list) or len(pair) != 2 for pair in pairs):
        raise ValueError("Each compatible pair must contain two symbols")
    buckets = ([{pair[0] for pair in pairs}, {pair[1] for pair in pairs}] if pairs else [])
    buckets += [set(group) for group in groups]
    vocabulary = set.union(*buckets)
    if sum(map(len, buckets)) != len(vocabulary):
        raise ValueError("Canonical ordering requires disjoint buckets")
    if not vocabulary <= known or not set(profile["optional"]) <= known:
        raise ValueError("Profile contains symbols absent from the catalog")
    if vocabulary.intersection(profile["optional"]):
        raise ValueError("Optional symbols must not be required bucket members")


def profile_buckets(profile):
    """Return the disjoint input groups in their canonical profile order."""
    groups = [set(group) for group in profile["required_groups"]]
    pairs = profile.get("required_pair_alternatives", [])
    if not pairs:
        return groups
    languages = {pair[0] for pair in pairs}
    frameworks = {pair[1] for pair in pairs}
    return [languages, frameworks] + groups


def build_profile_automaton(profile):
    """Build a total DFA directly; its state remembers progress and pair choices.

    L states retain frameworks compatible with languages already consumed. W
    states retain that same memory while waiting for a compatible framework.
    Ordering never selects a pair; only the DFA transition can satisfy it.
    """
    validate_profile(profile)
    pairs = profile.get("required_pair_alternatives", [])
    buckets = profile_buckets(profile)
    alphabet = sorted(set.union(*buckets))
    framework_order = sorted(buckets[1]) if pairs else []
    initial, reject = ("initial", None), ("reject", None)

    def name(state):
        phase, value = state
        if phase == "initial":
            return "q0"
        if phase == "reject":
            return "q_dead"
        if phase in ("languages", "pending"):
            mask = sum(1 << index for index, symbol in enumerate(framework_order)
                       if symbol in value)
            return ("L" if phase == "languages" else "W") + str(mask)
        if pairs and value == len(buckets) - 1:
            return "qf"
        return "pair_seen" if pairs and value == 1 else f"q{value + 1}"

    def advance(state, symbol):
        phase, value = state
        if phase == "reject":
            return reject
        if pairs and phase in ("initial", "languages", "pending"):
            compatible = frozenset() if phase == "initial" else value
            if phase != "pending" and symbol in buckets[0]:
                targets = {framework for language, framework in pairs if language == symbol}
                return ("languages", compatible | targets)
            if phase != "initial" and symbol in buckets[1]:
                return ("group", 1) if symbol in compatible else ("pending", compatible)
            return reject
        if phase == "initial":
            return ("group", 0) if symbol in buckets[0] else reject
        if symbol in buckets[value]:
            return state
        if value + 1 < len(buckets) and symbol in buckets[value + 1]:
            return ("group", value + 1)
        return reject

    machine = DeterministicFiniteAutomaton()
    machine.add_start_state("q0")
    machine.add_final_state("qf" if pairs else f"q{len(buckets)}")
    pending = deque([initial])
    visited = {initial}
    while pending:
        state = pending.popleft()
        for symbol in alphabet:
            target = advance(state, symbol)
            machine.add_transition(name(state), symbol, name(target))
            if target not in visited:
                visited.add(target)
                pending.append(target)
    return machine


@lru_cache(maxsize=1)
def _models():
    return {profile["id"]: (profile, build_profile_automaton(profile)) for profile in load_profiles()}


def canonical_sequence(skills, profile):
    """Project all relevant symbols, retaining every member of every bucket.

    This function orders data; it does not select a compatible pair or accept it.
    """
    values = set(skills)
    buckets = profile_buckets(profile)
    return [symbol for bucket in buckets for symbol in sorted(values & bucket)]


def _qualification_explanations(values, profile, accepted, missing, labels):
    """Describe configured requirements after the automaton has made its decision."""
    pairs = profile.get("required_pair_alternatives", [])
    diagnostics = None
    reasons = []
    if pairs:
        languages = sorted(values.intersection(pair[0] for pair in pairs))
        frameworks = sorted(values.intersection(pair[1] for pair in pairs))
        alternatives = []
        for pair in pairs:
            absent = [symbol for symbol in pair if symbol not in values]
            label = " + ".join(labels[symbol] for symbol in pair)
            message = (label + ": missing " + " and ".join(labels[symbol] for symbol in absent)
                       if absent else label + ": present") + "."
            alternatives.append({"pair": list(pair), "missing": absent, "message": message})
        if any(not option["missing"] for option in alternatives):
            status = "matched"
        elif languages and frameworks:
            status = "incompatible"
            reasons.append("Languages found: " + ", ".join(labels[s] for s in languages)
                           + ". Frameworks found: " + ", ".join(labels[s] for s in frameworks)
                           + ". These do not form an admitted language/framework pair.")
        elif languages:
            status = "missing_framework"
            reasons.append("No supported backend framework is present. Languages found: "
                           + ", ".join(labels[s] for s in languages) + ".")
        elif frameworks:
            status = "missing_language"
            reasons.append("No supported backend language is present. Frameworks found: "
                           + ", ".join(labels[s] for s in frameworks) + ".")
        else:
            status = "missing_both"
            reasons.append("No supported backend language or framework is present.")
        diagnostics = {"status": status, "languages_present": languages,
                       "frameworks_present": frameworks, "alternatives": alternatives}
    for group in missing:
        reasons.append(("Missing required qualification: " if len(group) == 1 else "Missing one of: ")
                       + " or ".join(labels[symbol] for symbol in group) + ".")
    if accepted:
        reasons = ["All required qualification groups are present."]
        if diagnostics is not None:
            matched = [option["pair"] for option in diagnostics["alternatives"] if not option["missing"]]
            reasons.append("Compatible pair found: " + "; ".join(
                " + ".join(labels[symbol] for symbol in pair) for pair in matched) + ".")
    elif not reasons:
        reasons.append("The profile automaton rejected the qualification sequence.")
    return reasons, diagnostics


def classify_skills(skills):
    if isinstance(skills, (str, bytes)):
        raise ValueError("Skills must be a collection of canonical symbols")
    try:
        values = set(skills)
    except TypeError as error:
        raise ValueError("Skills must be a collection of canonical symbols") from error
    if any(not isinstance(value, str) for value in values):
        raise ValueError("Canonical symbols must be strings")
    labels = {skill["canonical"]: skill["aliases"][0] for skill in load_catalog()["skills"]}
    known = set(labels)
    if not values <= known:
        raise ValueError("Unknown canonical symbols: " + ", ".join(sorted(values - known)))
    results = []
    for profile, machine in _models().values():
        sequence = canonical_sequence(values, profile)
        accepted = bool(machine.accepts(sequence))
        missing = [list(group) for group in profile["required_groups"] if not values.intersection(group)]
        pairs = profile.get("required_pair_alternatives", [])
        pair_missing = bool(pairs and not any(set(pair) <= values for pair in pairs))
        explanations, diagnostics = _qualification_explanations(values, profile, accepted, missing, labels)
        # These explanations do not decide acceptance; accepts() above does.
        results.append({"profile": profile["id"], "accepted": accepted,
                        "sequence": sequence, "missing_groups": missing,
                        "compatible_pair_missing": pair_missing,
                        "explanations": explanations, "pair_diagnostics": diagnostics,
                        "optional_present": sorted(values.intersection(profile["optional"])),
                        "ignored_for_pattern": sorted(values - set(sequence))})
    return {"accepted_profiles": sorted(row["profile"] for row in results if row["accepted"]),
            "profiles": results}
