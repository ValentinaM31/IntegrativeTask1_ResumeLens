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

Run `python tools/evaluate_workflow.py --check` from the installed checkout to
verify stored reports without rewriting them. See
[method and results](../../docs/workflow-evaluation.md) for scoring, reproduction
options and limitations.
