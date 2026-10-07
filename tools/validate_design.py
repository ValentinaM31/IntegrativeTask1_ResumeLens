"""Check design files; this does not process resumes."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def require(condition, message):
    if not condition:
        raise ValueError(message)

def main():
    catalog = load("config/skills_catalog.json")
    canonical_symbols = set()
    aliases_seen = {}
    for skill in catalog["skills"]:
        canonical = skill["canonical"]
        require(re.fullmatch(r"[A-Z][A-Z0-9_]*", canonical), "Invalid symbol: " + canonical)
        require(canonical not in canonical_symbols, "Duplicate symbol: " + canonical)
        canonical_symbols.add(canonical)
        require(skill["aliases"], "Symbol without variants: " + canonical)
        for alias in skill["aliases"]:
            require(alias.strip() == alias and bool(alias), "Empty alias or surrounding whitespace")
            key = alias.casefold()
            require(key not in aliases_seen, "Duplicate or conflicting alias: " + alias)
            aliases_seen[key] = canonical
    for alias in catalog["ambiguous_aliases"]:
        require(alias.casefold() in aliases_seen, "Undefined ambiguous alias")

    profiles = load("config/profiles_design.json")
    profile_ids = {p["id"] for p in profiles}
    require(len(profiles) == len(profile_ids) == 4, "Four distinct profiles are required")
    for profile in profiles:
        require(profile["required_groups"], "Profile without required groups")
        groups = profile["required_groups"] + profile.get("required_pair_alternatives", [])
        for group in groups:
            require(bool(group), "Empty profile group")
            require(set(group) <= canonical_symbols, "Profile contains symbols absent from the catalog")
        require(set(profile["optional"]) <= canonical_symbols, "Optional symbols absent from the catalog")

    expectations = load("data/expected_samples.json")
    require(expectations["status"] == "design_expectations_not_execution_results", "Incorrectly identified expectations")
    for case in expectations["cases"]:
        require((ROOT / case["file"]).read_text(encoding="utf-8").strip(), "Empty sample")
        require(case["normalized_skills"] == sorted(set(case["normalized_skills"])), "Expected list is unsorted or contains duplicates")
        require(set(case["normalized_skills"]) <= canonical_symbols, "Expectation contains an unknown symbol")
        skills = set(case["normalized_skills"])
        expected_profiles = []
        for profile in profiles:
            groups_ok = all(skills.intersection(group) for group in profile["required_groups"])
            pairs = profile.get("required_pair_alternatives")
            pairs_ok = pairs is None or any(set(pair) <= skills for pair in pairs)
            if groups_ok and pairs_ok:
                expected_profiles.append(profile["id"])
        require(set(expected_profiles) == set(case["accepted_profiles_expected_later"]), "Inconsistent profile expectation: " + case["file"])

    schema = load("contracts/first_stage.schema.json")
    example = load("contracts/example_output.json")
    require(set(example) == set(schema["required"]), "Example fields differ from the contract")
    require(example["schema_version"] == "1.0", "Incorrect contract version")
    text = (ROOT / "contracts/example_input.txt").read_text(encoding="utf-8")
    for match in example["extracted_skills"]:
        require(0 <= match["start"] < match["end"] <= len(text), "Indices outside the text")
        require(text[match["start"]:match["end"]] == match["raw"], "Evidence does not match the text")
    for link in example["normalization_evidence"]:
        require(0 <= link["extracted_index"] < len(example["extracted_skills"]), "Invalid link")
        raw = example["extracted_skills"][link["extracted_index"]]["raw"]
        require(aliases_seen.get(raw.casefold()) == link["canonical"], "Inconsistent expected translation")
    require(example["normalized_skills"] == sorted({link["canonical"] for link in example["normalization_evidence"]}), "Inconsistent canonical list")

    print("Consistent design:")
    print(f"- {len(canonical_symbols)} symbols and {len(aliases_seen)} aliases without conflicts.")
    print(f"- {len(profiles)} profiles with compatible vocabulary.")
    print(f"- {len(expectations['cases'])} synthetic resumes and compatible expectations.")
    print("- JSON example with consistent fields, positions and links.")
    print("This check does not execute extraction, FSTs or automata, and does not validate the complete JSON schema.")

if __name__ == "__main__":
    main()
