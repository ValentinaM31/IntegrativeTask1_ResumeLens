"""Profile recognition with actual epsilon-NFAs and canonical bucket order."""
from functools import lru_cache
from importlib.resources import files
import json
from pyformlang.finite_automaton import Epsilon, EpsilonNFA
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


def profile_branches(profile):
    """Each branch is a list of (allowed bucket, mandatory alternatives)."""
    groups = [set(group) for group in profile["required_groups"]]
    pairs = profile.get("required_pair_alternatives", [])
    if not pairs:
        return [[(group, group) for group in groups]]
    languages = {pair[0] for pair in pairs}
    frameworks = {pair[1] for pair in pairs}
    return [[(languages, {language}), (frameworks, {framework})]
            + [(group, group) for group in groups]
            for language, framework in pairs]


def build_profile_automaton(profile):
    """Never bypass a requirement: each bucket must enter its 'seen' state.

    Backend branches share bucket alphabets but require different compatible pairs.
    Non-mandatory members in a bucket may precede/follow the required member.
    """
    validate_profile(profile)
    machine = EpsilonNFA()
    machine.add_start_state("q0")
    machine.add_final_state("qf")
    for branch_index, groups in enumerate(profile_branches(profile)):
        previous = "q0"
        for group_index, (allowed, mandatory) in enumerate(groups):
            before = f"b{branch_index}_g{group_index}_before"
            seen = f"b{branch_index}_g{group_index}_seen"
            machine.add_transition(previous, Epsilon(), before)
            for symbol in sorted(allowed):
                machine.add_transition(before, symbol, before)
                machine.add_transition(seen, symbol, seen)
                if symbol in mandatory:
                    machine.add_transition(before, symbol, seen)
            previous = seen
        machine.add_transition(previous, Epsilon(), "qf")
    return machine


@lru_cache(maxsize=1)
def _models():
    return {profile["id"]: (profile, build_profile_automaton(profile)) for profile in load_profiles()}


def canonical_sequence(skills, profile):
    """Project all relevant symbols, retaining every member of every bucket.

    This function orders data; it does not select a compatible pair or accept it.
    """
    values = set(skills)
    buckets = [allowed for allowed, _ in profile_branches(profile)[0]]
    return [symbol for bucket in buckets for symbol in sorted(values & bucket)]


def classify_skills(skills):
    if isinstance(skills, (str, bytes)):
        raise ValueError("Skills must be a collection of canonical symbols")
    try:
        values = set(skills)
    except TypeError as error:
        raise ValueError("Skills must be a collection of canonical symbols") from error
    if any(not isinstance(value, str) for value in values):
        raise ValueError("Canonical symbols must be strings")
    known = {skill["canonical"] for skill in load_catalog()["skills"]}
    if not values <= known:
        raise ValueError("Unknown canonical symbols: " + ", ".join(sorted(values - known)))
    results = []
    for profile, machine in _models().values():
        sequence = canonical_sequence(values, profile)
        accepted = bool(machine.accepts(sequence))
        missing = [list(group) for group in profile["required_groups"] if not values.intersection(group)]
        pairs = profile.get("required_pair_alternatives", [])
        pair_missing = bool(pairs and not any(set(pair) <= values for pair in pairs))
        # These explanations do not decide acceptance; accepts() above does.
        results.append({"profile": profile["id"], "accepted": accepted,
                        "sequence": sequence, "missing_groups": missing,
                        "compatible_pair_missing": pair_missing,
                        "optional_present": sorted(values.intersection(profile["optional"])),
                        "ignored_for_pattern": sorted(values - set(sequence))})
    return {"accepted_profiles": sorted(row["profile"] for row in results if row["accepted"]),
            "profiles": results}
