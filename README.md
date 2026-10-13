# ResumeLens

ResumeLens processes UTF-8 TXT resumes through regular expressions, finite-state
transducers (FSTs), four deterministic finite automata (DFAs) and a textX candidate
language. It preserves source evidence and generates a validated HTML report.

**Team:** Valentina Martinez Franco and Juan Pino.

## Installation

Python 3.10 or later. From the repository root on Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

On Linux/macOS, use `python3 -m venv .venv` and `.venv/bin/python`.
Windows and Linux are verified; macOS has not been tested. Direct dependencies
are pinned in `pyproject.toml`. To reproduce the complete Python 3.12 environment,
create it with `py -3.12 -m venv .venv`, install `requirements-lock.txt`, then
install the project with `pip install --no-deps -e .` using that environment.

## Run the application

```powershell
.\.venv\Scripts\python.exe -m resumelens.web
```

Open `http://127.0.0.1:8765` if the browser does not open automatically. Load a TXT
file, try the example or paste a resume, then select **Process resume**. The results
show source evidence, all four profile decisions and the candidate report. Download
the four files individually or as a ZIP. Editing the input clears previous results.
The server keeps no candidate history. Stop it with **Ctrl+C**. Use `--port 8766`
if the default port is occupied, or `--no-browser` to open the page yourself.

The original TXT-to-JSON command and the complete four-file export are:

```powershell
.\.venv\Scripts\python.exe -m resumelens data/samples/01_full_stack.txt -o outputs/alex.json
.\.venv\Scripts\python.exe -m resumelens.workflow_cli data/samples/01_full_stack.txt -o outputs/alex_bundle
```

The bundle contains `first_stage.json`, `classification.json`, `candidate.rl` and
`candidate.html`. Open the HTML directly in a browser. Both commands accept
`--name` as a fallback name and `--force` to replace output. Invalid input returns
exit code 2. UTF-8 BOM and CRLF are supported; offsets refer to the decoded input.

For Python integration:

```python
from resumelens import process_complete_resume, save_bundle

with open("resume.txt", encoding="utf-8-sig", newline="") as stream:
    result = process_complete_resume(stream.read())
save_bundle(result, "outputs/candidate")
```

Disk exports prepare all four files and back up existing reports before replacing
them. Controlled failures restore previous files. If recovery is incomplete, keep
the reported `.resumelens-export.lock` directory and its `recovery.json`, `previous/`
and `prepared/` contents. Stop other exporters before recovery. For a valid
`prepared` record with complete backups, restore only files listed in `originals`
from `previous/`; remove only the four bundle files that had no original, verify
the restored bytes, then remove the workspace. Inspect incomplete records/backups
before changing files. A `committed` record means publication finished and only
cleanup is pending. Abrupt termination does not guarantee automatic recovery.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/validate_design.py
.\.venv\Scripts\python.exe tools/check_acceptance.py
.\.venv\Scripts\python.exe tools/check_workflow_acceptance.py
.\.venv\Scripts\python.exe tools/check_web_acceptance.py
.\.venv\Scripts\python.exe tools/evaluate_preannotated.py --allow-changed-rules --output-dir data/preannotated-evaluation/visual-update --check
.\.venv\Scripts\python.exe tools/evaluate_workflow.py --allow-changed-rules --output-dir data/workflow-evaluation/visual-update --check
```

The two evaluation commands compare stored reports without rewriting inputs or
expectations. The 14-case regression and 18-case evaluation have separate methods,
results and limitations. Recorded execution outcomes are in
[test results](docs/test-results.md); test scenarios are in [design](docs/design.md#test-scenarios).

For a manual keyboard check, use Tab/Shift+Tab, Enter and Space to load the example,
process it, download the ZIP, open details, edit and clear. Submit empty text and
an invalid file to check focus and recovery; repeat in a narrow window.
Optional automated browser checks require Node.js and Playwright:

```powershell
npm install --prefix .ui-test-deps --no-save --package-lock=false playwright@1.62.1
node .ui-test-deps/node_modules/playwright/cli.js install chromium
.\.venv\Scripts\python.exe tools/check_ui_keyboard.py
```

These 18 browser scenario groups are separate from the Python suite. They cover
downloads, focus, pending operations, errors, reduced motion and high contrast.
They do not establish screen-reader compatibility or full accessibility compliance.

## Documentation and files

| Documentation | Contents |
|---|---|
| [Design](docs/design.md) and [data contract](docs/data-contract.md) | Modules, functions, inputs/outputs, decisions and test scenarios |
| [Regex](docs/regex.md), [negation](docs/negation-handling.md) and [FSTs](docs/transducers.md) | Extraction patterns, supported wording, seven-tuples and diagrams |
| [Profile recognition](docs/profile-recognition.md) and [alignment](docs/profile-alignment.md) | Four DFA five-tuples, diagrams, requirements and explanations |
| [Candidate language](docs/candidate-language.md) | EBNF, textX grammar, examples and validation |
| [14-case regression](docs/workflow-evaluation.md), [18-case evaluation](docs/preannotated-evaluation.md) and [test results](docs/test-results.md) | Separate evaluation protocols, observed differences and verified runs |
| [Literature](docs/literature-review.md), [poster](docs/poster/README.md) and [AI usage](docs/ai-usage.md) | Research references and presentation material |

`src/resumelens/` contains the implementation and packaged resources; `config/`
defines skills and profiles; `contracts/` contains the JSON schema; `tests/` and
`tools/` contain tests, checks and artifact generators. `data/` retains synthetic
inputs, annotations, reference outputs and evaluation history. Valid and invalid
DSL fixtures in `data/dsl/` are intentional test cases. The four evaluation
`results.md` files accompany machine-readable reports and are checked by evaluators.

The catalog has 26 canonical symbols and 56 aliases. Supported English/Spanish
formats and bounded negation provide traceability, with known errors for unknown
technologies and some wording. Mentions do not establish proficiency; profiles
describe configured qualification patterns. Model generators rewrite reference
artifacts, so run them deliberately after model changes and review the output.
Keep personal resumes and local exports in ignored `outputs/` or `tmp/` directories.
