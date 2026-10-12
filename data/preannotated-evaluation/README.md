# Frozen synthetic evaluation inputs

Eighteen new TXT inputs and expected labels were prepared before running this
dataset: fourteen supported-format cases and four stress cases. Texts/labels are
AI-assisted synthetic work by an author familiar with earlier rules, not real CVs,
external human annotations or a blind test. Expected labels were not derived from
ResumeLens predictions.

`annotations.json` preserves exact mention/record/contact spans, canonical symbols,
profile labels and name/fallback values. `protocol.json` preserves the annotation
and exact input hashes, reference requirements/catalog and twenty-one normalized
runtime-file fingerprints. The local Git input policy retains raw BOM/CRLF bytes.

For patch-based installation with Git's automatic newline conversion enabled,
apply the local input text policy first, then the remaining hunks. This prevents
the patch application from converting inputs before it has loaded the new
attributes. Normal committed checkouts preserve the inputs using that policy.

`results.json` and `results.md` contain the executed metrics, every case and errors.
All eighteen pipelines are internally valid; fourteen fully match their labels.
Four stress cases retain Rust, double-negation, job-source attribution and bounded
Pandas-context errors. They are included in the overall counts rather than hidden.

```powershell
.\.venv\Scripts\python.exe tools/evaluate_preannotated.py --check
```

A successful check reproduces the stored measurements, including those errors.
It does not claim perfect interpretation. To review a separate report, use
`--output-dir outputs/evaluation-review`. After application changes, use explicit
`--allow-changed-rules --output-dir outputs/later-regression`; do not overwrite
the freeze to disguise reused cases as a new evaluation.

The older `data/evaluation/` evidence remains separate. Methods, exact metrics,
limitations and commands are in [the protocol guide](../../docs/preannotated-evaluation.md).
