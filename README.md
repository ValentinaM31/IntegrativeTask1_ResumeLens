# ResumeLens

Process UTF-8 TXT resumes with Python regular expressions and real pyformlang finite-state transducers, then export validated JSON with original evidence.

## Installation

Python 3.10 or later. Verified platform: Windows with Python 3.12.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

Dependencies: `pyformlang==1.0.11` and `jsonschema==4.26.0`. For the recorded Python 3.12 environment, install `requirements-lock.txt` and then the package with `pip install --no-deps -e .`.

## CLI

```powershell
.\.venv\Scripts\python.exe -m resumelens data/samples/01_full_stack.txt -o outputs/alex.json
```

The CLI accepts UTF-8 with BOM, preserves CRLF and creates destination folders. `--name` supplies a fallback when no explicit name line exists. Existing output requires `--force`; input and output must differ. Invalid files, encoding and empty input return exit code 2.

## API

```python
from resumelens import process_resume

with open("resume.txt", encoding="utf-8-sig", newline="") as stream:
    text = stream.read()
result = process_resume(text, name=None)
candidate = result["candidate"]
skills = result["normalized_skills"]
```

Version 1.0 includes `candidate`, `extracted_skills`, `normalized_skills`, `normalization_evidence`, `excluded_mentions`, `unknown_skills` and `warnings`. Absent names are null; other candidate fields are empty lists. Positive and excluded mentions retain original text and positions. Every evidence item must satisfy `text[start:end] == raw`. Canonical symbols are unique and alphabetical; repeated mentions retain translation links.

Validation checks the JSON schema, evidence positions, normalization indices and actual FST translations. Machines are cached between calls. Schema resources are packaged with the module. The editable schema and example input/output are in `contracts/`.

## Verification

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/check_acceptance.py
.\.venv\Scripts\python.exe tools/validate_design.py
.\.venv\Scripts\python.exe tools/generate_examples.py
```

Tests cover candidate extraction, all 56 aliases, context and negation, real FSTs, contract validation and CLI behavior. Eight sample outputs are in `data/results/`. Acceptance compares API and CLI in six scenarios using the same decoded input and optional name.

## Scope

The component extracts and normalizes candidate information and catalog skills. React, Pandas, JS/TS and eight simple negation patterns use explicit context rules. Unknown vocabulary, double negation, irony and unsupported formats remain limitations. Education/experience preserve line records without inferred institution, employer or duration.

`config/profiles_design.json` contains design patterns, not executed classification. Later components prepare profile-specific sequences for automata, then build and validate a DSL before visualization. Alphabetical JSON order is not an automaton input sequence. JSON version 1.0 does not contain profile decisions and forbids additional properties.
