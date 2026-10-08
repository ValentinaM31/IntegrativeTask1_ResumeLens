# Reproducible skill-mention evaluation

There are 23 synthetic annotated cases: fifteen original cases in `cases.json`, six historically reserved in `holdout.json` and two additional limits in `limitations.json`. They are not real resumes or an external corpus. Original cases guided rule adjustments. Reserved cases were written after freezing earlier behavior; current reuse is regression, not a new blind evaluation.

`holdout_protocol.json` retains the earlier extractor SHA-256. `results.json` reports `rules_unchanged_since_holdout_creation=false`: Pandas corrections and English diagnostics changed the source. The fingerprint is not reset to imply independence. This procedure does not establish independent human evaluation.

## Unit and formulas

Compare sets of exact positive `(start, end, raw)` triples. Zero-based `occurrence` distinguishes repeats. Matching requires original text and positions, not equal list lengths. TP is intersection, FP extra predictions, FN missed annotations. Exclusions are not positive predictions: wrongly excluding a positive is FN; accepting a negative is FP.

Micro metrics sum counts before division: precision=TP/(TP+FP), recall=TP/(TP+FN), F1=2TP/(2TP+FP+FN). A zero denominator produces null, never an artificial 100%. Canonical lists are also compared exactly; this does not evaluate proficiency or profiles.

## Current results

| Group | Cases | TP | FP | FN | Precision | Recall | F1 | Exact canonical lists |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Supported formats | 15 | 25 | 0 | 0 | 1.00 | 1.00 | 1.00 | 15/15 |
| Historical reserved synthetic cases | 6 | 14 | 0 | 0 | 1.00 | 1.00 | 1.00 | 6/6 |
| Stress | 2 | 0 | 0 | 2 | null | 0.00 | 0.00 | 1/2 |

Rust is not extracted because it is outside the catalog. Double negation can incorrectly exclude Python. Annotated animal pandas mentions are now excluded correctly. Rust's expected canonical list is empty despite a missed mention; this explains separate span and symbol metrics.

## Historical results

`history/baseline_cases.json` and `history/baseline_results.json` preserve twelve supported cases (TP25/FP0/FN0) and three stress cases (TP0/FP2/FN1). The react verb and do not use moved into corrected scope, with previous_group and reasons retained.

`history/pre_pandas_results.json` and `history/pre_pandas_limits.json` retain the immediately preceding revision: fourteen admitted, six reserved and three stress cases with one pandas false positive. The animal case moved to supported with unchanged expected annotations and an explicit reclassification reason. Historical raw inputs/spans remain original bilingual fixtures.

## Reproduction

```powershell
.\.venv\Scripts\python.exe tools/evaluate.py
```

Output is `data/evaluation/results.json`. Perfect results on selected synthetic formats do not imply population accuracy. Metrics cover skills; contact, records, contract and CLI use automated tests. A future anonymized real-resume corpus with human annotation would provide stronger evidence.
