# Original fourteen-case complete-pipeline regression

This integrates the actual fourteen previously prepared cases: eight main sample
resumes and six additional cases. Its dataset is `data/workflow-evaluation/`.
It remains separate from the original 23-case skill-mention evaluation and the
18-case preannotated dataset in `data/preannotated-evaluation/`. Their counts and
metrics must not be merged or described as the same evaluation.

## Provenance and expectations

The original six additional texts and profile expectations were recovered from
the saved draft without modification. The original fourteen-case profile/export
report is preserved under `history/`, alongside the additional-case selection and
eight original sample expectations. The eight sample candidate/span/link labels
reuse existing reference outputs. Candidate, exclusion and normalization labels
for the six additional cases were explicitly drafted during this integration.

These cases were previously executed. The expanded annotations therefore do not
constitute a new blind or pre-run evaluation. This is AI-assisted synthetic
regression informed by prior project behavior, with no independent human
annotation or real-applicant accuracy claim. The annotation timestamp records
the expanded-label snapshot, not the first execution of these inputs.

`protocol.json` records annotation/input hashes, the actual current baseline,
catalog/profile references and runtime-source fingerprints. Inputs have fixed
UTF-8 LF bytes, preserving the original reference-offset convention. Local Git
attributes prevent checkout conversion of these inputs and historical snapshots.
Hash verification detects subsequent edits; it does not prove authorship.

## Compared units

- Candidate name by exact value; emails, phones, links, education and experience
  by exact `(start, end, raw)` evidence spans.
- Positive skill mentions and excluded mentions, scored separately by exact spans.
- Unique normalized symbols and accepted-profile sets, with extra and missed
  predictions recorded independently.
- Ordered normalization evidence, including extracted-mention index and canonical
  output, rather than only the final unique symbol list.
- Internal source/schema/FST/recognition/DSL/HTML integrity and all four exported
  files read back from a temporary directory. The DSL is parsed again.

The evaluator adapts the existing eighteen-case loader/scoring helpers without
modifying that dataset, evaluator or stored results. Expected normalization links
are checked against annotated positive mentions. The original additional texts,
profile decisions and sample symbol expectations must remain unchanged.

## Reproduce

From the installed checkout:

```powershell
.\.venv\Scripts\python.exe tools/evaluate_workflow.py --allow-changed-rules --output-dir data/workflow-evaluation/visual-update --check
```

This executes the current pipeline and verifies the stored later-regression
JSON/Markdown reports without rewriting them. A stale report returns exit code 2.
For an intentional reviewed regeneration, omit `--check`; keep
`--allow-changed-rules` and use `--output-dir outputs/workflow-evaluation` to write
to a separate directory. Running the tool as `python -m tools.evaluate_workflow`
with those arguments is also supported from the checkout root.

A strict `--check` without later-regression mode applies only to the original
frozen runtime. It deliberately rejects the current changed sources.

Later source changes require `--allow-changed-rules`, which marks changed runtime
fingerprints while retaining the original annotation freeze. Do not reset hashes
or change labels to improve results. Known disagreements are legitimate report
content: a successful evaluation command means scoring completed, not that every
prediction matched. Inspect `passed`, per-unit scores and recorded differences.

## Executed results and limits

The expanded integration run produced fourteen valid pipelines; all fourteen
matched the fixed annotation units and export round trips. Full case details and
micro TP/FP/FN metrics are in `results.json` and `results.md` under the dataset.
Zero metric denominators remain null. Empty fields are exact empty-set checks,
not evidence of broad coverage of that field.

The fourteen cases cover missing requirements, incompatible backend pairs,
supported negation, overlapping profiles, irrelevant prose, repeated records and
markup escaping. They overlap existing examples and supported behavior. More
challenging observed errors remain in the separate eighteen-case report; a clean
fourteen-case regression result does not negate those errors.

## Visual-revision regression

The original annotation and runtime freeze is preserved. Run with
`--allow-changed-rules --output-dir data/workflow-evaluation/visual-update --check`
to reproduce the stored later comparison for the visual revision. All fourteen
cases match annotation units and exported report files. Changed runtime sources
are listed in the report; original labels and baseline reports are not reset.
The final review adds the corrected CLI hard-link protection to the recorded
source changes without altering the fourteen cases or their measurements.
