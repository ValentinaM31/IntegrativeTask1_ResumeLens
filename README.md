# ResumeLens

Process UTF-8 TXT resumes using Python `re`, real finite-state transducers, four profile automata and a textX candidate language. Use the local browser interface or CLI to extract evidence, normalize qualifications, recognize profiles and generate a standalone HTML report from a validated specification.

## Installation for the current checkout

Python 3.10 or later. The current preannotated-evaluation extension is verified on Linux with Python 3.12.14. Run the verification commands below after applying it on Windows; historical platform checks are recorded in [test results](docs/test-results.md).

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

Direct dependencies: `pyformlang==1.0.11`, `jsonschema==4.26.0` and `textX==4.4.0`. Normal installation resolves compatible transitive dependencies for the selected Python version. The locked set requires Python 3.12 because some pinned transitive dependencies do not support Python 3.10. To reproduce that environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
```

Activation is unnecessary with the explicit executable. On Linux/macOS create the environment with `python3 -m venv .venv` and use `.venv/bin/python`; macOS has not been verified.

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

Keyboard navigation includes a skip link, focus after loading/processing, field
errors, result navigation and native expandable details with separate downloads.
See [keyboard checks](docs/keyboard-navigation.md) for the manual flow and optional
automated browser checks. Node.js and Playwright are needed only for that optional QA.
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

## Verify the current checkout

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/validate_design.py
.\.venv\Scripts\python.exe tools/check_acceptance.py
.\.venv\Scripts\python.exe tools/check_workflow_acceptance.py
.\.venv\Scripts\python.exe tools/check_web_acceptance.py
.\.venv\Scripts\python.exe tools/evaluate_preannotated.py --check
```

These commands check the current installation. Model, example and evaluation generators can rewrite reference artifacts; run them intentionally after implementation changes and review their diffs. Generator instructions are in the relevant [technical guides](docs/README.md). Recorded test counts below describe specific earlier runs, rather than a new execution on this checkout. The GitHub Actions matrix covers Windows/Linux with Python 3.10/3.12; check actual run outcomes in GitHub Actions.

There are 181 automated tests (39 first-stage, 12 recognition, 16 candidate-language, 24 workflow/rendering/CLI, 23 local-HTTP/UI-entry, 14 focused negation regressions, 17 profile-explanation tests, 15 bundle-recovery tests, 8 profile-alignment tests and 13 evaluation-protocol/scoring tests), eight main English samples and 23 historical annotated synthetic extraction cases: fifteen original, six historically reserved and two additional limit cases. The focused regressions include real CLI and HTTP/ZIP checks; they are not an independently collected evaluation dataset. All eight samples have executed profile classifications in `data/classification/` and validated candidate specifications in `data/dsl/`. Complete JSON/DSL/HTML bundles are in `data/workflow/`. Browser interactions include eighteen reproducible keyboard scenario groups checked with Chrome for Testing on Linux; see [keyboard verification](docs/keyboard-navigation.md). Spanish input fixtures and regex alternatives retain documented bilingual support. See [test results](docs/test-results.md), [profile models](docs/profile-recognition.md), [candidate grammar](docs/candidate-language.md) and [evaluation](docs/evaluation.md).

A separate [preannotated evaluation](docs/preannotated-evaluation.md) adds 18 new
synthetic cases with labels fixed before execution: 14 supported-format cases and
four stress cases. All 18 produce valid pipelines; 14 match all annotations. The
four observed limitations remain in the report. These AI-assisted examples are
independent of predicted outputs, with no external-human or real-resume accuracy
claim. Verify the stored JSON/Markdown reports without rewriting them:

```powershell
.\.venv\Scripts\python.exe tools/evaluate_preannotated.py --check
```

Machine Learning accepts Scikit-learn, TensorFlow or PyTorch as alternatives for
its required learning-library group, following the assignment's page 5 diagram.
See [requirement alignment](docs/profile-alignment.md) for the reference criteria,
team-defined extensions and three targeted regression bundles in
`data/profile-alignment/`. Backend and Data Engineer retain their team-defined
patterns; separate additional teacher specifications are not included here.

Disk bundle exports prepare all four outputs and preserve existing originals before
replacement. Controlled failures restore prior report bytes and file presence;
an incomplete recovery retains backups and reports their location. See
[export protection and recovery](docs/bundle-recovery.md) for concurrent-writer
behavior, manual recovery and limits after abrupt termination.

## Reference evidence and historical material

| Path | Purpose |
|---|---|
| `data/samples/` and `data/expected_samples.json` | Eight reproducible main inputs and skill/profile expectations |
| `data/results/`, `data/classification/`, `data/dsl/`, `data/workflow/` | Versioned reference outputs and valid/invalid specifications used by tests |
| `data/evaluation/` | Original 23-case skill-mention evaluation and its protocol |
| `data/preannotated-evaluation/` | Separate 18-case complete-pipeline dataset, fixed annotations and retained disagreements |
| `data/profile-alignment/` | Targeted requirement regressions and report bundles |
| `data/evaluation/history/` | Earlier annotations and metrics retained for traceability |

The two evaluations remain separate. Historical results and dated sections in [test results](docs/test-results.md) retain their original scope; they do not redefine current expectations or certify a new checkout. Reused reserved cases are not a fresh blind benchmark.

## Project structure

| Directory | Contents |
|---|---|
| src/resumelens | Extraction, FSTs, validation, recognition, textX DSL, reports, CLI commands and local UI |
| config | Catalog of 26 symbols, 56 aliases and profile design patterns |
| contracts | JSON schema 1.0 and input/output example |
| tests | Behavior and integration tests |
| data | Samples, outputs and annotated evaluation |
| docs | Operating guides, formal models, literature, verification records and presentation artifacts |
| tools | Acceptance checks, evaluators, model/example generators and optional browser checks |
| .github/workflows | Automated verification configuration |

Start with the [documentation index](docs/README.md) for current operating instructions, component references, evaluation evidence and historical material. `.gitignore` excludes local environments, caches, execution outputs, dependency directories, patch files, delivery ZIPs and personal settings. Versioned examples, reports, model exports and contracts are intentionally retained for reproducibility and tests. Put private execution outputs under `outputs/` or `tmp/`, and keep personal resumes out of the synthetic datasets.

See [design](docs/design.md), [modules](docs/module-design.md), [integration](docs/handoff.md), [API](docs/api.md), [regex](docs/regex.md), [FSTs](docs/transducers.md) and [contract](docs/data-contract.md). The academic AI-use record is submitted separately from the code.

## Scope

Candidate extraction supports documented contact, education and experience formats. Education and experience retain line records. Explicit negation includes `do not know`, `don't/don’t know/use` and `no sé/se/conozco`, with known-alias lists, clause boundaries and contrast. Negation takes precedence over skills headings and technical context. JS/TS require skills context. Unsuffixed React accepts documented technical context, including immediate `I know React` or `I use React`. Pandas requires skills context or explicit use for data analysis/processing. Other wording, homonyms, double negation, irony and unknown technologies may produce errors. See [negation behavior and examples](docs/negation-handling.md).

Profile recognition uses four epsilon-NFAs and the documented canonical bucket order. Backend requires a compatible language/framework pair. Its explanations now distinguish incompatible pairs from missing languages/frameworks and show what is absent from each configured alternative. All four profiles explain other missing qualification groups in the UI, classification JSON and validated standalone HTML. Profiles can overlap. Classification results remain separate from JSON 1.0. See [explanation fields and examples](docs/profile-explanations.md) and [complete five-tuples and diagrams](docs/profile-recognition.md).

The candidate DSL now has a complete EBNF specification and executable textX grammar. Generate it with `generate_candidate_dsl(first, classification)` and validate it with `parse_candidate_dsl(source)`; see [API and examples](docs/candidate-language.md). Syntax and semantic errors prevent acceptance.

The complete processing API, workflow CLI, HTML reports and interactive local UI are implemented. The currently published [poster](docs/poster/README.md) is an extraction/normalization draft with older metrics; it does not represent complete-project results. Final presentation materials and academic submission evidence still require completion. JSON Schema does not replace textX validation. Alphabetical skill order is not an automaton input sequence.

When changing the catalog or schema, synchronize packaged resources, regenerate models and run tests. `tools/export_models.py` exports complete models; `tools/build_poster.py` is the existing poster generator.
