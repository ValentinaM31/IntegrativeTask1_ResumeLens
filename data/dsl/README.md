# Candidate-language fixtures

`valid/` contains eight generated candidate specifications (`.rl`) and their parsed
models (`.json`). `invalid/` contains intentionally rejected specifications.
`validation.json` records the executed acceptance/rejection results and error categories.

Regenerate with `python tools/generate_dsl_examples.py`. Invalid files are test
fixtures, not defects accidentally left in the product. A syntax rejection is a
textX `TextXSyntaxError`; semantic inconsistencies raise ValueError afterward.

The source scenarios are the existing files in `data/samples/`. See
[the complete EBNF and validation rules](../../docs/candidate-language.md).
