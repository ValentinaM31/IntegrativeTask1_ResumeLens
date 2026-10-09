"""Run all sample resumes through stages 1-3 and preserve classifications."""
import json
from pathlib import Path
from resumelens import process_resume, classify_skills

ROOT = Path(__file__).resolve().parents[1]


def main():
    destination = ROOT / "data" / "classification"
    destination.mkdir(parents=True, exist_ok=True)
    expectations = json.loads((ROOT / "data/expected_samples.json").read_text(encoding="utf-8"))
    summary = []
    for case in expectations["cases"]:
        source = ROOT / case["file"]
        with source.open(encoding="utf-8-sig", newline="") as stream:
            first = process_resume(stream.read())
        classification = classify_skills(first["normalized_skills"])
        if classification["accepted_profiles"] != sorted(case["accepted_profiles_expected_later"]):
            raise ValueError("Unexpected profile result: " + case["file"])
        (destination / (source.stem + ".json")).write_text(
            json.dumps(classification, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        summary.append({"file": case["file"], "accepted_profiles": classification["accepted_profiles"]})
    (destination / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Classified {len(summary)} samples; all match the documented expectations.")


if __name__ == "__main__":
    main()
