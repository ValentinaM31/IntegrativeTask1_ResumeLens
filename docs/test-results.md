# Verification results

## Current implementation

The final installed-package review ran on Windows with Python 3.12.14 on
2026-10-12. Its source/test fingerprints and exact outcome are stored in
[`poster/verification.json`](poster/verification.json).

| Check | Recorded outcome |
|---|---|
| Installed-wheel Python suite | 194 tests: 193 passed, one symlink-permission skip; zero failures/errors |
| Dependencies and design | `pip check`, catalog, profile criteria, contracts and sample expectations pass |
| Original CLI / complete CLI / local HTTP | Six original scenarios and eight complete samples agree with the API; all four bundle/ZIP members match |
| Four complete DFA exports | Full Stack 7 states/13 symbols/91 transitions; ML 7/10/70; Backend 19/13/247; Data 6/8/48 |
| Independent required-skill subsets | All 17,664 combinations agree with configured group/pair conditions |
| Language equivalence with previous models | Product exploration finds no differing acceptance over any profile word; 7/7/121/6 reachable product states for Full Stack/ML/Backend/Data |
| Checkout newline policies | Both `core.autocrlf` modes preserve LF samples and exact hashes for all 32 frozen inputs |
| Windows Chrome 154.0.8037.59 | All 18 keyboard scenario groups pass: source fidelity, downloads, focus, failures, narrow layout, reduced motion and high contrast |
| Poster review | A1 landscape vector PDF inspected; stage controls, play/pause, overview, enlargement and case tooltips work without observed JavaScript errors |

The published commit `55543cb` passed all four GitHub Actions jobs on Windows
and Ubuntu with Python 3.10 and 3.12. See the
[recorded run](https://github.com/ValentinaM31/IntegrativeTask1_ResumeLens/actions/runs/38344457145).
The earlier Windows failure came from CRLF conversion of LF reference samples;
the sample Git attributes fix is included in this passing revision.

The equivalence check explores each reachable pair of previous epsilon-NFA
closures and current DFA states, comparing acceptance and following every symbol.
No disagreeing pair was reachable. The 17,664 subset comparisons separately
verify configured conditions; they are neither additional unit tests nor a
resume-accuracy dataset. Worked FST paths are checked against executable edges by
`tools/export_model_examples.py --check`.

## Separate evaluation results

| Dataset | Scope | Recorded result | Method |
|---|---|---|---|
| Original 23 cases | Skill mentions and canonical lists | Supported 15/15; historical reserved 6/6; two stress cases retain missed mentions | Exact positive spans and symbol sets; extraction only |
| [14-case workflow regression](workflow-evaluation.md) | Candidate fields, skills, exclusions, normalization, profiles and exports | 14/14 exact cases and export round trips | Previously executed inputs; expanded integration annotations |
| [18-case preannotated evaluation](preannotated-evaluation.md) | Same complete pipeline with labels fixed before execution | 14/18 exact cases; 18/18 structurally valid pipelines | Separate synthetic dataset; four disagreements retained |

The current full-pipeline reports are in each dataset's `visual-update/` directory.
Original inputs, annotation freezes, protocols and baseline reports are preserved.
Structural validity does not imply agreement with every annotation. These selected
synthetic cases establish no population, proficiency or hiring accuracy.

### Original extraction evaluation

`data/evaluation/` contains fifteen original cases in `cases.json`, six historically
reserved cases in `holdout.json` and two stress cases in `limitations.json`.
The original cases guided rule changes. Reusing reserved cases after changes is
regression, not a new blind evaluation. `holdout_protocol.json` retains its original
extractor hash; `results.json` records `rules_unchanged_since_holdout_creation=false`.

Positive matches compare exact `(start, end, raw)` sets. The annotation's
zero-based `occurrence` resolves repeated text. TP is the intersection, FP extra
predictions and FN missed annotations. Incorrect exclusions count as FN; accepted
negatives count as FP. Micro precision is `TP/(TP+FP)`, recall `TP/(TP+FN)` and
F1 `2TP/(2TP+FP+FN)`. Zero denominators produce null. Canonical lists are compared
separately; this evaluation does not score candidate fields or profiles.

| Group | Cases | TP | FP | FN | Precision | Recall | F1 | Exact canonical lists |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Supported formats | 15 | 25 | 0 | 0 | 1.00 | 1.00 | 1.00 | 15/15 |
| Historical reserved | 6 | 14 | 0 | 0 | 1.00 | 1.00 | 1.00 | 6/6 |
| Stress | 2 | 0 | 0 | 2 | null | 0.00 | 0.00 | 1/2 |

Rust is outside the catalog and double negation can exclude Python incorrectly.
Rust's expected canonical list is empty despite a missed mention, so its symbol
and span outcomes differ. `history/` preserves the earlier baseline and
pre-Pandas labels/results, including reclassification reasons and unchanged
original annotations. Reproduce this extraction report with
`python tools/evaluate.py`; it writes `data/evaluation/results.json`.

## Reproduction and limits

Use the [README verification commands](../README.md#verification) for a fresh
checkout. [Design](design.md#test-scenarios) lists expected scenarios. Evaluation
guides explain exact scoring and non-writing report checks. The poster builder
uses runtime/test and report/evaluator hashes to reject stale successful figures.

The symlink test requires Windows permissions. Browser checks cover interaction
and DOM semantics, not spoken screen-reader output or a full accessibility audit.
macOS, other browser engines and physical poster readability at four to six feet
remain unverified. Detailed historical execution prose is recoverable in Git;
the original datasets, reports, models and fixtures remain in the repository.
