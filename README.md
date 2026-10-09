# ResumeLens

Process UTF-8 TXT resumes using Python `re`, real finite-state transducers, four profile automata and a textX candidate language. Run the complete workflow to extract evidence, normalize qualifications, recognize profiles and generate a standalone HTML report from a validated specification.

## Installation

Python 3.10 or later. Verified environments: the original Windows first-stage environment and the Linux Python 3.12.14 recognition/DSL/workflow environment. New workflow behavior still needs execution on Windows.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

Dependencies: `pyformlang==1.0.11`, `jsonschema==4.26.0` and `textX==4.4.0`. `requirements-lock.txt` retains the original first-stage pins and adds textX/Arpeggio for this increment. Install that file and then run `pip install --no-deps -e .` to reproduce the pinned environment. On Linux/macOS use `.venv/bin/python`; macOS has not been verified.

## Usage

```powershell
.\.venv\Scripts\python.exe -m resumelens data/samples/01_full_stack.txt -o outputs/alex.json
```

`--name` supplies a name if no explicit name line exists. `--force` permits replacing existing output. The CLI creates destination folders, preserves CRLF and accepts a UTF-8 BOM. Invalid input returns exit code 2 and an English error message.

```python
from resumelens import process_resume, classify_skills

with open("resume.txt", encoding="utf-8-sig", newline="") as stream:
    text = stream.read()
result = process_resume(text, name=None)
candidate = result["candidate"]
skills = result["normalized_skills"]
classification = classify_skills(skills)
accepted_profiles = classification["accepted_profiles"]
```

Offsets refer to the exact decoded input. Results include positive mentions, exclusions, unique symbols, translation links and warnings. No proficiency scores or hiring decisions are inferred.

## Complete workflow and HTML

```powershell
.\.venv\Scripts\python.exe -m resumelens.workflow_cli data/samples/01_full_stack.txt -o outputs/alex_bundle
Start-Process outputs/alex_bundle/candidate.html
```

The directory contains `first_stage.json`, `classification.json`, `candidate.rl` and `candidate.html`. The new workflow command supports `--name` and `--force`; the original `python -m resumelens` command above remains TXT-to-JSON only. See [API, bundle format and validation](docs/complete-workflow.md).

## Verification

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/validate_design.py
.\.venv\Scripts\python.exe tools/check_acceptance.py
.\.venv\Scripts\python.exe tools/evaluate.py
.\.venv\Scripts\python.exe tools/export_automata.py
.\.venv\Scripts\python.exe tools/classify_examples.py
.\.venv\Scripts\python.exe tools/generate_dsl_examples.py
.\.venv\Scripts\python.exe tools/generate_workflow_examples.py
.\.venv\Scripts\python.exe tools/check_workflow_acceptance.py
```

There are 89 automated tests (39 first-stage, 12 recognition, 16 candidate-language and 22 workflow/rendering/CLI tests), eight main English samples and 23 annotated synthetic extraction cases: fifteen original, six historically reserved and two additional limit cases. All eight samples have executed profile classifications in `data/classification/` and validated candidate specifications in `data/dsl/`. Complete JSON/DSL/HTML bundles are in `data/workflow/`. Spanish input fixtures and regex alternatives retain documented bilingual support. See [test results](docs/test-results.md), [profile models](docs/profile-recognition.md), [candidate grammar](docs/candidate-language.md) and [evaluation](docs/evaluation.md).

## Structure

| Directory | Contents |
|---|---|
| src/resumelens | Extraction, FSTs, validation, recognition, textX DSL, HTML and both CLIs |
| config | Catalog of 26 symbols, 56 aliases and profile design patterns |
| contracts | JSON schema 1.0 and input/output example |
| tests | Behavior and integration tests |
| data | Samples, outputs and annotated evaluation |
| docs | Technical design, formal models, literature and results |
| tools | Model, example, regex and poster generators |

See [design](docs/design.md), [modules](docs/module-design.md), [integration](docs/handoff.md), [API](docs/api.md), [regex](docs/regex.md), [FSTs](docs/transducers.md) and [contract](docs/data-contract.md). The academic AI-use record is submitted separately from the code.

## Scope

Candidate extraction supports documented contact, education and experience formats. Education and experience retain line records. Eight explicit negation patterns support lists, clause boundaries and contrast. JS/TS require skills context. Unsuffixed React requires documented technical context. Pandas requires skills context or explicit use for data analysis/processing. Other wording, homonyms, double negation, irony and unknown technologies may produce errors.

Profile recognition uses four epsilon-NFAs and the documented canonical bucket order. Backend requires a compatible language/framework pair. Profiles can overlap. Classification results remain separate from JSON 1.0. See [complete five-tuples and diagrams](docs/profile-recognition.md).

The candidate DSL now has a complete EBNF specification and executable textX grammar. Generate it with `generate_candidate_dsl(first, classification)` and validate it with `parse_candidate_dsl(source)`; see [API and examples](docs/candidate-language.md). Syntax and semantic errors prevent acceptance.

The complete processing API, workflow CLI and HTML reports are implemented. The interactive input UI remains pending for the next increment. JSON Schema does not replace textX validation. Alphabetical skill order is not an automaton input sequence.

When changing the catalog or schema, synchronize packaged resources, regenerate models and run tests. `tools/export_models.py` exports complete models; `tools/build_poster.py` is the existing poster generator.
