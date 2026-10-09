# Executed complete workflow examples

Each of the eight sample directories contains `first_stage.json`,
`classification.json`, `candidate.rl` and `candidate.html`. Open `candidate.html`
directly in a browser to inspect the report. These are synthetic course examples.

`validation.json` records the executed workflow and expected accepted profiles.
The generator checks profile expectations before saving, and the tests compare
persisted outputs with actual processing and the earlier stage fixtures.

These stored synthetic fixtures are defined against LF-normalized sample input.
The generator and fixture-comparison test use universal-newline UTF-8 reads, so
their evidence offsets are reproducible even when a checkout contains CRLF.
The production API/CLI still preserves original input line endings and reports
offsets against that exact input. Tests separately validate CRLF evidence, and
the acceptance tool compares the CLI with the API using unmodified input text.

Regenerate with `python tools/generate_workflow_examples.py` from an installed
environment. This tool intentionally replaces the four generated files in each
sample directory; unrelated files remain untouched.
