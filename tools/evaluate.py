"""Reproducible evaluation with synthetic annotations separate from outputs."""
import json
from pathlib import Path
import re
import hashlib
from resumelens import process_resume

ROOT = Path(__file__).resolve().parents[1]


def expected_spans(case):
    spans = set()
    for item in case["mentions"]:
        matches = list(re.finditer(re.escape(item["raw"]), case["text"]))
        index = item.get("occurrence", 0)
        if index >= len(matches):
            raise ValueError("Missing annotation: " + case["id"])
        match = matches[index]
        spans.add((match.start(), match.end(), item["raw"]))
    return spans


def metric(tp, fp, fn):
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None
    return {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1}


def main():
    base = ROOT / "data/evaluation"
    datasets = ("cases.json", "holdout.json", "limitations.json")
    cases = []
    for filename in datasets:
        cases.extend(json.loads((base / filename).read_text(encoding="utf-8"))["cases"])
    if len({case["id"] for case in cases}) != len(cases):
        raise ValueError("Duplicate evaluation identifiers")
    totals, rows = {}, []
    for case in cases:
        result = process_resume(case["text"])
        expected = expected_spans(case)
        actual = {(m["start"], m["end"], m["raw"]) for m in result["extracted_skills"]}
        tp, fp, fn = len(actual & expected), len(actual - expected), len(expected - actual)
        total = totals.setdefault(case["group"], {"tp": 0, "fp": 0, "fn": 0, "cases": 0, "canonical_exact": 0})
        for key, value in (("tp", tp), ("fp", fp), ("fn", fn)):
            total[key] += value
        exact = result["normalized_skills"] == sorted(case["symbols"])
        total["cases"] += 1
        total["canonical_exact"] += int(exact)
        rows.append({"id": case["id"], "group": case["group"], **metric(tp, fp, fn),
                     "canonical_exact": exact, "actual_symbols": result["normalized_skills"],
                     "false_positive_spans": sorted(actual - expected), "missed_spans": sorted(expected - actual)})
    summary = {group: {**values, **metric(values["tp"], values["fp"], values["fn"])} for group, values in totals.items()}
    protocol = json.loads((base / "holdout_protocol.json").read_text(encoding="utf-8"))
    unchanged = protocol["source_sha256"] == hashlib.sha256((ROOT / "src/resumelens/extraction.py").read_bytes()).hexdigest()
    report = {"method": "Exact raw character spans; micro precision/recall/F1 per group. Synthetic annotated cases, no population accuracy claim.",
              "datasets": list(datasets), "rules_unchanged_since_holdout_creation": unchanged,
              "summary": summary, "cases": rows}
    (ROOT / "data/evaluation/results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
