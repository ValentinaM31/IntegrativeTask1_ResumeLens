"""Preserve valid DSLs, parsed models and intentionally invalid language examples."""
import json
from pathlib import Path
from textx import TextXSyntaxError
from resumelens import process_resume, classify_skills, generate_candidate_dsl, parse_candidate_dsl

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "dsl"


def main():
    (DEST / "valid").mkdir(parents=True, exist_ok=True)
    (DEST / "invalid").mkdir(parents=True, exist_ok=True)
    expectations = json.loads((ROOT / "data/expected_samples.json").read_text(encoding="utf-8"))
    valid = []
    first_source = None
    for case in expectations["cases"]:
        source = ROOT / case["file"]
        with source.open(encoding="utf-8-sig", newline="") as stream:
            first = process_resume(stream.read())
        classification = classify_skills(first["normalized_skills"])
        dsl = generate_candidate_dsl(first, classification)
        parsed = parse_candidate_dsl(dsl)
        if sorted(parsed["accepted_profiles"]) != sorted(case["accepted_profiles_expected_later"]):
            raise ValueError("Unexpected profiles in DSL: " + case["file"])
        destination = DEST / "valid" / (source.stem + ".rl")
        destination.write_text(dsl, encoding="utf-8")
        destination.with_suffix(".json").write_text(json.dumps(parsed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        valid.append({"source": case["file"], "dsl": destination.relative_to(ROOT).as_posix(),
                      "accepted_profiles": parsed["accepted_profiles"]})
        if first_source is None:
            first_source = dsl
    name_line = first_source.splitlines()[1].strip()
    invalid = [
        ("01_missing_brace", first_source.rstrip()[:-1], "syntax", "Closing candidate brace is required"),
        ("02_unquoted_name", first_source.replace(name_line, 'name Alex;'), "syntax", "Names require a JSON string or null"),
        ("03_unknown_skill", first_source.replace('skill GIT;', 'skill RUST;'), "syntax", "Skills use the finite canonical alphabet"),
        ("04_bad_escape", first_source.replace(name_line, 'name "bad\\xZZ";'), "syntax", "Only JSON string escapes are admitted"),
        ("05_wrong_section", first_source.replace('contacts {', 'contact {'), "syntax", "Section keywords are exact"),
        ("06_duplicate_skill", first_source.replace('skill GIT;', 'skill GIT; skill GIT;'), "semantic", "Repeated canonical skill declarations are rejected"),
        ("07_missing_profile", first_source.replace('    profile FULL_STACK_DEVELOPER;\n', ''), "semantic", "Accepted profiles must match recognition"),
        ("08_false_profile", first_source.replace('profile FULL_STACK_DEVELOPER;', 'profile DATA_ENGINEER;'), "semantic", "A declared profile must be recognized")
    ]
    rejected = []
    for name, dsl, kind, reason in invalid:
        expected_error = TextXSyntaxError if kind == "syntax" else ValueError
        try:
            parse_candidate_dsl(dsl)
        except expected_error:
            pass
        else:
            raise ValueError("Invalid example was not rejected as expected: " + name)
        path = DEST / "invalid" / (name + ".rl")
        path.write_text(dsl, encoding="utf-8")
        rejected.append({"dsl": path.relative_to(ROOT).as_posix(), "error_kind": kind, "reason": reason})
    report = {"status": "executed_dsl_validation", "valid": valid, "invalid": rejected}
    (DEST / "validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"DSL validation: {len(valid)} accepted examples and {len(rejected)} expected rejections.")


if __name__ == "__main__":
    main()
