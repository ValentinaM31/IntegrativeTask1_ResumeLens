# Extraction and normalization integration guide

The component receives UTF-8 text, extracts evidence with Python re, normalizes variants using real pyformlang FSTs and returns validated JSON 1.0. The first-stage API does not execute profile recognition, textX validation or UI code; the installed project now includes the dependencies for the later APIs.

## PowerShell installation

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

For the verified Python 3.12 environment, first install `requirements-lock.txt`, then `pip install --no-deps -e .`. Normal installation declares pyformlang 1.0.11, jsonschema 4.26.0 and textX 4.4.0. Activation is unnecessary. The original first stage was verified on Windows; the recognition/DSL increments were verified on Linux with Python 3.12.14.

## CLI

```powershell
.\.venv\Scripts\python.exe -m resumelens data/samples/01_full_stack.txt -o outputs/alex.json
.\.venv\Scripts\python.exe -m resumelens contracts/example_input.txt --name Alex -o outputs/reference.json
```

Destination folders are created. Existing files require `--force`. Input and output must differ. Missing files, invalid UTF-8 and empty input return code 2 with an English diagnostic.

## Public API

```python
from resumelens import process_resume

text = "Name: Alex\nSkills: JS, React.js, NodeJS, Postgres, Git."
result = process_resume(text, name=None)
candidate = result["candidate"]
symbols = result["normalized_skills"]
# candidate["name"] == "Alex"
# symbols == ["GIT", "JAVASCRIPT", "NODE_JS", "POSTGRESQL", "REACT"]
```

`process_resume(text, name=None)` retains the optional fallback name. An explicit input name takes priority. Empty input raises ValueError. Each call returns fresh data while reusing cached machines.

## Structure and positions

`candidate` holds `name` as string/null and lists `emails`, `phones`, `links`, `education`, `experience`. Each item is `{raw, start, end}`; absent lists are `[]`. Education/experience retain line text without separate company, institution, role or date fields, and without summing periods.

Offsets are Python character positions: inclusive start and exclusive end. Always require `text[start:end] == raw`. Match CLI decoding with:

```python
with open("resume.txt", encoding="utf-8-sig", newline="") as stream:
    text = stream.read()
result = process_resume(text)
```

UTF-8-sig removes only the encoding BOM; empty newline preserves CRLF. Offsets refer to decoded text without the BOM, not bytes. A UI must retain the exact input associated with each JSON result.

## Vocabulary and output

`config/skills_catalog.json` contains 26 symbols and 56 aliases. Each FST consumes casefolded characters and emits a complete canonical symbol, preserving original evidence. PostgreSQL does not imply SQL.

The contract retains `schema_version="1.0"`, `candidate`, `extracted_skills`, `normalized_skills`, `normalization_evidence`, `excluded_mentions`, `unknown_skills`, `warnings`. Repeated mentions retain evidence; canonical symbols are unique and alphabetical. `extracted_index` addresses `extracted_skills`. Validation checks schema, offsets, indices and actual translations.

Unknown inputs are recorded only if received by the normalizer. The extractor may miss an uncataloged technology such as Rust; it does not invent evidence to populate that field.

## Later consumption

`profiles_design.json` now supplies four executable epsilon-NFA patterns. Call `classify_skills(result["normalized_skills"])` from the public package to prepare profile-specific input and execute recognition. Alphabetical JSON order is not that sequence. The returned classification is separate from JSON 1.0. Call `generate_candidate_dsl(result, classification)` and then `parse_candidate_dsl(source)` to generate and validate the candidate DSL. The implemented `render_candidate_html(source)` parses the DSL before rendering. `process_complete_resume(text, name=None)` composes all stages, and `save_bundle(result, destination)` writes the four outputs. See [workflow integration](complete-workflow.md). See [stage 3](profile-recognition.md) and the [candidate language](candidate-language.md).

Do not add properties to version 1.0, whose schema forbids them. Keep later results separate or agree on a new contract version. The package exports the existing first-stage, recognition and DSL functions plus `render_candidate_html`, `process_complete_resume` and `save_bundle`. The original CLI retains TXT-to-JSON behavior; `python -m resumelens.workflow_cli` is the complete bundle command.

## Acceptance procedure

Run `python tools/check_acceptance.py` using a freshly installed environment. Six cases cover normal and incomplete resumes, repetitions, exclusions, contrast and animal pandas. It compares API/CLI with identical decoded text and optional name, validates evidence and checks expected symbols.

Sample 07 excludes negated Python/TensorFlow and ambiguous mentions while retaining JavaScript, Git and React.js. Compare persisted outputs with `data/results/`. Call `validate_result(result, text)` to verify spans.

## Local input interface

Run `python -m resumelens.web` from the installed environment to open the local UI.
It adapts loaded/pasted text to `process_complete_resume`, displays all four profile
decisions and the report, and downloads the four validated outputs or a ZIP.
Unedited file uploads preserve CRLF/BOM decoding conventions; edited/pasted text
uses the text area's current content. No server-side candidate persistence is added.
See [local-ui.md](local-ui.md) for PowerShell steps and the manual browser checklist.

## Limits

React and Pandas require supported technical context; other technical wording may be excluded. Immediate know/use predicates now admit React, while explicit knowledge/use negations take precedence. Negation supports straight/curly apostrophes and Spanish no sé/se/conozco, and bounds known-alias lists by clauses and lines; it does not resolve double negation or irony. Angular has possible nontechnical homonyms. Contact formats are limited; education/work records do not establish truth. See `negation-handling.md`, `regex.md` and `evaluation.md`.
