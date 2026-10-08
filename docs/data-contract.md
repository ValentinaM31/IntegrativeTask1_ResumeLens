# Extraction and normalization JSON contract

Version 1.0 is defined by `contracts/first_stage.schema.json`; the same folder contains input/output examples. The schema describes JSON and does not replace the later textX DSL.

## Rules

- Input is decoded UTF-8 text. Indices address Python characters, not file bytes. The decoded string is the offset reference.
- `candidate.name` is a string or null. A manual name has no invented offsets; an explicit input name takes priority.
- Emails, phones, links, education and experience are evidence lists `{raw, start, end}`. Records retain text; institution, company and dates are not separate inferred fields.
- `start` is inclusive and `end` exclusive. Always require `text[start:end] == raw`.
- `extracted_skills` retains positive mentions in occurrence order, including repetitions.
- `normalized_skills` contains unique alphabetically sorted symbols. Profile recognition prepares its own input order.
- Each `normalization_evidence` item links an existing `extracted_skills` index to its translated symbol.
- `excluded_mentions` retains evidence and an English reason, including recognized simple negation or unsupported context.
- `unknown_skills` records inputs received by the normalizer without a translation. It does not promise unknown-word discovery across arbitrary resumes.
- `warnings` contains English recoverable diagnostics. Empty text and invalid files produce errors.

`validate_result(result, text)` validates JSON Schema, positions, indices, alphabetical symbols and actual FST translations. The CLI preserves CRLF and removes a UTF-8 BOM; offsets refer to the remaining decoded text.

## Output scope

The 1.0 object does not contain `accepted_profiles`. Those results require automata over profile-specific sequences and a later model. Sample profile expectations are design scenarios, not executed classifications.

## Reference example

`Name: Alex` followed by `Skills: JS, React.js, NodeJS, Postgres, Git.` yields five mentions and GIT, JAVASCRIPT, NODE_JS, POSTGRESQL and REACT. The alphabetical order supports stable comparisons; it does not encode a Full Stack input sequence.
