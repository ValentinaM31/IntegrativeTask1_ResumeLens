"""Each alias has an independent character path in a real FST."""
from pyformlang.fst import FST
from .catalog import load_catalog, validate_catalog


def build_transducers(catalog=None):
    catalog = load_catalog() if catalog is None else catalog
    validate_catalog(catalog)
    machines = {}
    for index, skill in enumerate(catalog["skills"]):
        category = skill["category"]
        if category not in machines:
            machines[category] = FST()
            machines[category].add_start_state("q0")
        machine = machines[category]
        for alias_index, alias in enumerate(skill["aliases"]):
            word = alias.casefold()
            previous = "q0"
            for position, char in enumerate(word, 1):
                state = f"s{index}_a{alias_index}_{position}"
                output = [skill["canonical"]] if position == len(word) else []
                machine.add_transition(previous, char, state, output)
                previous = state
            machine.add_final_state(previous)
    return machines


def normalize_skills(matches, transducers):
    normalized, links, unknown = set(), [], []
    for index, match in enumerate(matches):
        outputs = {tuple(output) for machine in transducers.values()
                   for output in machine.translate(list(match["raw"].casefold()))}
        if not outputs:
            unknown.append(dict(match))
            continue
        if len(outputs) != 1 or len(next(iter(outputs))) != 1:
            raise ValueError("Ambiguous translation or invalid FST output")
        canonical = next(iter(outputs))[0]
        normalized.add(canonical)
        links.append({"extracted_index": index, "canonical": canonical})
    return {"normalized_skills": sorted(normalized), "normalization_evidence": links, "unknown_skills": unknown}
