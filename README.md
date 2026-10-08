# ResumeLens

Process UTF-8 TXT resumes using Python `re` and real finite-state transducers. Extract candidate information and normalize skill variants into JSON with verifiable evidence.

## Installation

Python 3.10 or later. Verified platform: Windows with Python 3.12.14.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

Dependencies: `pyformlang==1.0.11` and `jsonschema==4.26.0`. `requirements-lock.txt` records the verified Python 3.12 environment. To reproduce it, install that file and then run `pip install --no-deps -e .`. On Linux/macOS use `.venv/bin/python`; these platforms have not been verified.

## Usage

```powershell
.\.venv\Scripts\python.exe -m resumelens data/samples/01_full_stack.txt -o outputs/alex.json
```

`--name` supplies a name if no explicit name line exists. `--force` permits replacing existing output. The CLI creates destination folders, preserves CRLF and accepts a UTF-8 BOM. Invalid input returns exit code 2 and an English error message.

```python
from resumelens import process_resume

with open("resume.txt", encoding="utf-8-sig", newline="") as stream:
    text = stream.read()
result = process_resume(text, name=None)
candidate = result["candidate"]
skills = result["normalized_skills"]
```

Offsets refer to the exact decoded input. Results include positive mentions, exclusions, unique symbols, translation links and warnings. No proficiency scores or hiring decisions are inferred.

## Verification

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/validate_design.py
.\.venv\Scripts\python.exe tools/check_acceptance.py
.\.venv\Scripts\python.exe tools/evaluate.py
```

There are 39 automated tests, eight main English samples and 23 annotated synthetic cases: fifteen original, six historically reserved and two additional limit cases. Spanish input fixtures and regex alternatives retain documented bilingual support. See [test results](docs/test-results.md) and [evaluation](docs/evaluation.md).

## Structure

| Directory | Contents |
|---|---|
| src/resumelens | Extraction, FSTs, validation and CLI |
| config | Catalog of 26 symbols, 56 aliases and profile design patterns |
| contracts | JSON schema 1.0 and input/output example |
| tests | Behavior and integration tests |
| data | Samples, outputs and annotated evaluation |
| docs | Technical design, formal models, literature and results |
| tools | Model, example, regex and poster generators |

See [design](docs/design.md), [modules](docs/module-design.md), [integration](docs/handoff.md), [API](docs/api.md), [regex](docs/regex.md), [FSTs](docs/transducers.md) and [contract](docs/data-contract.md). The academic AI-use record is submitted separately from the code.

## Scope

Candidate extraction supports documented contact, education and experience formats. Education and experience retain line records. Eight explicit negation patterns support lists, clause boundaries and contrast. JS/TS require skills context. Unsuffixed React requires documented technical context. Pandas requires skills context or explicit use for data analysis/processing. Other wording, homonyms, double negation, irony and unknown technologies may produce errors.

Profile automata, classification, textX DSL, UI and HTML are not implemented. JSON Schema does not replace a textX grammar. Alphabetical skill order is not an automaton input sequence.

When changing the catalog or schema, synchronize packaged resources, regenerate models and run tests. `tools/export_models.py` exports complete models; `tools/build_poster.py` is the existing poster generator.
