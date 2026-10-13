# Original fourteen-case workflow regression

`inputs/` contains the eight original samples and six prepared additional texts.
`annotations.json` defines candidate data, positive/excluded spans, canonical
symbols, normalization links and accepted profiles. `protocol.json` records their
hashes and provenance. `history/` preserves the original selection and narrower
profile/export report.

These are previously executed regression cases. Expanded labels were added during
integration; do not describe this dataset as a new blind or independently human
annotated evaluation. The separate eighteen-case dataset retains its own protocol
and results.

Run from the installed checkout to verify current later-regression reports
without rewriting them:

```powershell
.\.venv\Scripts\python.exe tools/evaluate_workflow.py --allow-changed-rules --output-dir data/workflow-evaluation/visual-update --check
```

The explicit later-regression flag records changed runtime sources while
preserving the original inputs, annotation freeze and baseline reports. Strict
checking without that flag applies only to the original frozen runtime. See
[method and results](../../docs/workflow-evaluation.md) for scoring, reproduction
options and limitations.
