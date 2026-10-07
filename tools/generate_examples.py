"""Actual examples, separate from the original design expectations."""
import json
from pathlib import Path
from resumelens import process_resume

ROOT = Path(__file__).resolve().parents[1]


def main():
    destination = ROOT / "data" / "results"
    destination.mkdir(parents=True, exist_ok=True)
    for source in sorted((ROOT / "data/samples").glob("*.txt")):
        with source.open(encoding="utf-8-sig", newline="") as stream:
            result = process_resume(stream.read())
        (destination / (source.stem + ".json")).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(source.name, "->", len(result["normalized_skills"]), "symbols")


if __name__ == "__main__":
    main()
