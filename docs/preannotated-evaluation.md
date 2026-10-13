# Preannotated complete-pipeline evaluation

This separate dataset adds eighteen new synthetic resume texts and expected labels
prepared before these inputs were executed. It complements the original 23-case
extraction evaluation and the three profile-alignment regressions without merging
their metrics or relabelling earlier cases as a new holdout.

## Provenance and freeze

The texts and manual annotations were drafted with AI assistance using the
documented qualification criteria. The author knew the project's previous rules
and limitations. There was no external human annotator, independently collected
real-resume corpus or blind test. Independence here means that expected labels
were written separately from predictions before this dataset's first execution.
It does not establish independent human judgement or population accuracy.

The annotation draft used ordinary literal-string matching to locate manually
selected spans; it did not import or call ResumeLens. Profile labels were checked
logically against documented requirements, without executing the recognition
automata. The initial input/annotation hashes and reference snapshots were then
fixed before `tools/evaluate_preannotated.py` processed the cases.

`data/preannotated-evaluation/protocol.json` records:

- The freeze timestamp and baseline commit `6d6ea17`.
- SHA-256 of canonical JSON annotations, unaffected by indentation or checkout
  line endings but sensitive to label changes.
- Exact byte hashes for all eighteen input files, including UTF-8 BOM and CRLF.
- Fingerprints for twenty-one runtime source/resource files, normalizing only
  source-file CRLF to LF for cross-platform checkouts.
- The frozen catalog/profile reference used to validate label consistency and
  the explicit independence limitation.

Hashes detect later changes; they do not independently prove chronology or who
authored a label. The recorded workflow order and preserved original annotations
provide the procedural evidence. Existing application code, profile rules,
catalog, public APIs and runtime dependencies are unchanged in this extension.

## Inputs, annotations and supported units

`annotations.json` references TXT inputs and contains exact positive/excluded
character spans, expected canonical symbols, accepted profile identifiers,
candidate name, and contact/education/experience evidence. Repeated words or
records at different positions are annotated separately. The optional fallback
name is an explicit input, not inferred candidate information.

Fourteen supported-format cases cover aliases, each profile, a compatible and an
incompatible Backend pair, four simultaneous profiles, two simultaneous profiles,
repetitions, English/Spanish negation, contrast, React/Pandas homonyms, multiple
contacts, Unicode, BOM/CRLF and a multiline list with fallback name. Four stress
cases cover an unknown technology, double negation, external job requirements and
a technical Pandas phrase outside admitted context patterns. Groups were fixed
before execution and are not reassigned after seeing a result.

Positions refer to Python characters in decoded `utf-8-sig` text. Only the BOM is
removed; CRLF is retained. Input files use a dataset-local Git text policy that
preserves their original bytes, including the dedicated CRLF case. This avoids
changing offsets or invalidating input hashes on Windows.

When applying this dataset through a patch in a `core.autocrlf=true` checkout,
apply the dataset's Git text policy before the input-file hunks. A single apply
operation can cache the older attributes and convert newly created inputs even
though that operation also creates the new policy. The verified two-step
application preserves every input byte. A normal checkout of the committed
dataset uses the committed attributes. Do not reset hashes or annotations to
accept accidentally converted input files.

Unknown positive technology mentions have `canonical: null`, because the frozen
catalog has no valid enum for them. Their omission counts as a missed extraction
span, but no `RUST` symbol is invented in the first-stage contract. A correct
known-symbol set can coexist with a missed unknown mention; both units are
reported separately.

## Evaluation and formulas

The loader verifies the annotation/input fingerprints before processing any case.
It rejects duplicate IDs, invalid spans, contradictory symbol/profile labels and
changed runtime files, checking both the checkout and the imported package so a
stale virtual environment cannot be misidentified as the baseline. It copies
loaded cases before attaching decoded text so the
frozen annotation object is not modified in memory.

For each case, the evaluator calls `process_complete_resume(text, name=...)` and
uses the existing bundle validator to verify source evidence, actual FST
translations, classification, textX semantics and HTML consistency. These checks
establish internal pipeline validity, not agreement with independent labels.

Predictions are compared with fixed expectations using:

| Unit | Matching rule |
|---|---|
| Positive/excluded skill mentions | Exact `(start, end, raw)` triples, including original case and repeated positions |
| Canonical skills | Unique canonical-symbol sets per case |
| Accepted profiles | Unique profile-identifier sets per case |
| Candidate name | Exact string/null value |
| Contacts, education and experience | Exact evidence triples in each separate field |

TP is the expected/predicted intersection; FP is extra predictions; FN is missed
annotations. Micro metrics add counts before division:

`precision = TP / (TP + FP)`

`recall = TP / (TP + FN)`

`F1 = 2 TP / (2 TP + FP + FN)`

Zero denominators are JSON null and Markdown n/a. Profile confusion matrices also
report TN. Processing exceptions are recorded, with expected positive labels
counted as missed; later cases still run. All baseline cases complete successfully.
Name/contact/record results are sparse coverage checks, not real-resume accuracy
estimates. Per-case disagreements retain exact missing/extra spans and symbols.

## Executed results

Verified on Linux with Python 3.12.14 and the existing locked dependencies.

| Group | Cases | Mention TP | FP | FN | Precision | Recall | F1 | All annotations exact |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Supported | 14 | 76 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 14/14 |
| Stress | 4 | 18 | 3 | 3 | 0.8571 | 0.8571 | 0.8571 | 0/4 |
| Overall | 18 | 94 | 3 | 3 | 0.9691 | 0.9691 | 0.9691 | 14/18 |

All eighteen pipelines validate. Canonical lists and accepted-profile sets each
match in fifteen cases, illustrating why they are not the same measure as exact
mention recovery. Profile totals are TP17/FP1/FN2, with micro F1 0.9189. No
general precision claim is made beyond these selected synthetic inputs.

The four retained disagreements are:

| Case | Observed error | Profile impact |
|---|---|---|
| E15_unknown_rust | Rust is omitted because it is outside the catalog | Backend remains correctly accepted from other explicit skills |
| E16_double_negation | Python is excluded in a sentence denying lack of experience | Machine Learning incorrectly rejected against the annotation |
| E17_external_requirement | Python, NumPy and sklearn quoted as job requirements become positive candidate skills | Machine Learning falsely accepted; Backend still correctly accepted |
| E18_pandas_other_context | `I clean CSV files with pandas.` is excluded by the bounded Pandas rules | Machine Learning incorrectly rejected against the annotation |

These errors are not removed by changing the gold labels, hiding stress rows or
changing the production rules after observing this dataset. Improvements to
negation scope, source attribution, context vocabulary and unknown-technology
coverage would require explicit follow-up work and subsequent regression checks.

The complete generated [JSON](../data/preannotated-evaluation/results.json) and
[Markdown report](../data/preannotated-evaluation/results.md) include every case,
field, profile confusion matrix and disagreement.

## Reproduce and verify

```powershell
.\.venv\Scripts\python.exe tools/evaluate_preannotated.py --allow-changed-rules --output-dir data/preannotated-evaluation/visual-update --check
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/check_workflow_acceptance.py
.\.venv\Scripts\python.exe tools/check_web_acceptance.py
```

`--check` recomputes the evaluation and compares it with the stored current
later-regression JSON/Markdown without rewriting reports. Exit 0 means
measurements are reproduced, including the known disagreements; it does not mean
all cases were interpreted correctly. Malformed/tampered inputs or stale reports
return exit 2. The explicit later-regression flag records changed runtime sources.
A strict check without that flag applies only to the original frozen runtime and
deliberately rejects the current changed sources.

To generate a separate review copy:

```powershell
.\.venv\Scripts\python.exe tools/evaluate_preannotated.py --allow-changed-rules --output-dir outputs/evaluation-review
```

On the original frozen runtime, the command without flags regenerates only the
baseline `results.json` and `results.md`, never annotations or the protocol. On
the current changed runtime, keep the baseline intact by using
`--allow-changed-rules --output-dir outputs/later-regression`. Such a report is
marked `later_regression_comparison`, lists
changed source files and retains the original freeze. Later reuse is regression;
it is not a new prospective or blind evaluation. Changed annotation/input content
requires a separately versioned dataset rather than resetting existing hashes.

Thirteen evaluator tests cover tampering, byte preservation, frozen references,
stale imported packages,
later-regression mode, exact repeat positions, unknown misses, false profile
acceptance/rejection, micro aggregation, empty denominators, pipeline exceptions,
stored-report reproduction and the real evaluation CLI. Complete-suite counts
and recorded Windows/Linux runs are in [verification results](test-results.md).
The eighteen automated browser groups have recorded Linux and Windows runs,
separate from the Python suite and manual visual checks. Presentation materials are
separate from this evaluator.

## Visual-revision regression

The visual revision changes rendering/UI sources and adds bounded Windows file-
lock retries. The original eighteen-case annotations, input bytes, protocol and
baseline reports remain unchanged. Explicit `--allow-changed-rules` execution
creates a later comparison in `data/preannotated-evaluation/visual-update/`.
All eighteen pipelines remain valid; fourteen cases fully match labels and the
same four disagreements remain. The final review additionally corrects the CLI's
hard-link input protection and records its changed source fingerprint in this
comparison. This is later regression, not a new freeze.
