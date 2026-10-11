# ResumeLens

Process UTF-8 TXT resumes using Python `re`, real finite-state transducers, four profile automata and a textX candidate language. Use the local browser interface or CLI to extract evidence, normalize qualifications, recognize profiles and generate a standalone HTML report from a validated specification.

## Installation

Python 3.10 or later. The current negation correction is verified on Linux with Python 3.12.14. Run the verification commands below after applying it on Windows; historical platform checks are recorded in [test results](docs/test-results.md).

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

Dependencies: `pyformlang==1.0.11`, `jsonschema==4.26.0` and `textX==4.4.0`. `requirements-lock.txt` retains the original first-stage pins and adds textX/Arpeggio for this increment. Install that file and then run `pip install --no-deps -e .` to reproduce the pinned environment. On Linux/macOS use `.venv/bin/python`; macOS has not been verified.

## Usage

### Browser interface

```powershell
.\.venv\Scripts\python.exe -m resumelens.web
```

Keep the terminal open while using the browser. Load a UTF-8 TXT file or paste a
resume, optionally supply a fallback name, then select **Process resume**. The UI
shows all four profile decisions, rejection reasons and the validated candidate
report. Download the two JSON files, DSL and HTML individually or together as a ZIP.
No candidate files are automatically written by the server.

The printed URL is `http://127.0.0.1:8765`. If browser opening fails, open it manually.
Use `--port 8766` if the port is occupied, or `--no-browser` to open the URL yourself.
Press **Ctrl+C** in the terminal to stop. See [interface guide and limits](docs/local-ui.md).

### Original TXT-to-JSON command

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
.\.venv\Scripts\python.exe tools/check_web_acceptance.py
```

There are 125 automated tests (39 first-stage, 12 recognition, 16 candidate-language, 24 workflow/rendering/CLI, 20 local-HTTP/UI-entry and 14 focused negation regressions), eight main English samples and 23 annotated synthetic extraction cases: fifteen original, six historically reserved and two additional limit cases. The negation regressions include real CLI and HTTP/ZIP checks; they are not an independently collected evaluation dataset. All eight samples have executed profile classifications in `data/classification/` and validated candidate specifications in `data/dsl/`. Complete JSON/DSL/HTML bundles are in `data/workflow/`. Browser interactions were additionally checked with Chrome for Testing on Linux; see the documented manual UI checklist. Spanish input fixtures and regex alternatives retain documented bilingual support. See [test results](docs/test-results.md), [profile models](docs/profile-recognition.md), [candidate grammar](docs/candidate-language.md) and [evaluation](docs/evaluation.md).

## Structure

| Directory | Contents |
|---|---|
| src/resumelens | Extraction, FSTs, validation, recognition, textX DSL, reports, CLI commands and local UI |
| config | Catalog of 26 symbols, 56 aliases and profile design patterns |
| contracts | JSON schema 1.0 and input/output example |
| tests | Behavior and integration tests |
| data | Samples, outputs and annotated evaluation |
| docs | Technical design, formal models, literature and results |
| tools | Model, example, regex and poster generators |

See [design](docs/design.md), [modules](docs/module-design.md), [integration](docs/handoff.md), [API](docs/api.md), [regex](docs/regex.md), [FSTs](docs/transducers.md) and [contract](docs/data-contract.md). The academic AI-use record is submitted separately from the code.

## Scope

Candidate extraction supports documented contact, education and experience formats. Education and experience retain line records. Explicit negation includes `do not know`, `don't/don’t know/use` and `no sé/se/conozco`, with known-alias lists, clause boundaries and contrast. Negation takes precedence over skills headings and technical context. JS/TS require skills context. Unsuffixed React accepts documented technical context, including immediate `I know React` or `I use React`. Pandas requires skills context or explicit use for data analysis/processing. Other wording, homonyms, double negation, irony and unknown technologies may produce errors. See [negation behavior and examples](docs/negation-handling.md).

Profile recognition uses four epsilon-NFAs and the documented canonical bucket order. Backend requires a compatible language/framework pair. Profiles can overlap. Classification results remain separate from JSON 1.0. See [complete five-tuples and diagrams](docs/profile-recognition.md).

The candidate DSL now has a complete EBNF specification and executable textX grammar. Generate it with `generate_candidate_dsl(first, classification)` and validate it with `parse_candidate_dsl(source)`; see [API and examples](docs/candidate-language.md). Syntax and semantic errors prevent acceptance.

The complete processing API, workflow CLI, HTML reports and interactive local UI are implemented. Final poster/presentation updates and the complete requirement/history audit remain for the final increment. JSON Schema does not replace textX validation. Alphabetical skill order is not an automaton input sequence.

When changing the catalog or schema, synchronize packaged resources, regenerate models and run tests. `tools/export_models.py` exports complete models; `tools/build_poster.py` is the existing poster generator.
