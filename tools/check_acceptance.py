"""Check API and CLI against samples and documented functional contexts."""
import json
from pathlib import Path
import subprocess
import sys
import uuid
from resumelens import process_resume
from resumelens.first_stage import validate_result

ROOT = Path(__file__).resolve().parents[1]


def main():
    destination = ROOT / "tmp" / ("acceptance-" + uuid.uuid4().hex)
    destination.mkdir(parents=True)
    cases = [{"sample": case, "name": None} for case in
             ("01_full_stack", "06_incomplete", "05_aliases_duplicates", "07_boundaries_negation")]
    cases.extend([
        {"sample": "contrast", "name": "Ana", "text": "Skills: Python, Pandas, Git.\r\nNo tengo experiencia en TensorFlow, pero sí en Java.\r\n",
         "expected": ["GIT", "JAVA", "PANDAS", "PYTHON"]},
        {"sample": "animal", "name": "Sam", "text": "Los pandas viven en China.\r\nI like pandas at the zoo.\r\n", "expected": []}
    ])
    report = []
    for case in cases:
        sample, name = case["sample"], case["name"]
        source = ROOT / "data/samples" / (sample + ".txt")
        if "text" in case:
            source = destination / (sample + ".txt")
            source.write_bytes(case["text"].encode("utf-8"))
        output = destination / (sample + ".json")
        command = [sys.executable, "-m", "resumelens", str(source), "-o", str(output)]
        if name is not None:
            command.extend(["--name", name])
        execution = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        if execution.returncode:
            raise ValueError(execution.stderr)
        with source.open(encoding="utf-8-sig", newline="") as stream:
            text = stream.read()
        actual = json.loads(output.read_text(encoding="utf-8"))
        validate_result(actual, text)
        if actual != process_resume(text, name=name):
            raise ValueError("API and CLI differ: " + sample)
        if "text" in case:
            if actual["normalized_skills"] != case["expected"]:
                raise ValueError("Incorrect symbols: " + sample)
        else:
            expected = json.loads((ROOT / "data/results" / (sample + ".json")).read_text(encoding="utf-8"))
            if actual != expected:
                raise ValueError("Nonreproducible result: " + sample)
        report.append({"sample": sample, "manual_name": name, "api_cli_equal": True, "schema_version": actual["schema_version"],
                       "normalized_skills": actual["normalized_skills"], "excluded_count": len(actual["excluded_mentions"])})
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
