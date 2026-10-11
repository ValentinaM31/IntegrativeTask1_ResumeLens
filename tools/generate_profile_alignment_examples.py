"""Generate targeted Machine Learning rule regressions, not evaluation metrics."""
import json
from pathlib import Path
from resumelens import process_complete_resume, save_bundle

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "profile-alignment"


def main():
    cases = json.loads((DEST / "cases.json").read_text(encoding="utf-8"))["cases"]
    for case in cases:
        source = DEST / case["file"]
        # Stored synthetic fixtures use universal-newline input, as data/workflow.
        result = process_complete_resume(source.read_text(encoding="utf-8"))
        if result["first_stage"]["normalized_skills"] != case["normalized_skills"]:
            raise ValueError("Unexpected normalized skills for " + case["file"])
        if result["classification"]["accepted_profiles"] != case["accepted_profiles"]:
            raise ValueError("Unexpected accepted profiles for " + case["file"])
        save_bundle(result, DEST / source.stem, force=True)
    print(f"Profile alignment: {len(cases)} verified regression bundles generated.")


if __name__ == "__main__":
    main()
