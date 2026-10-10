# Verification results

## Local browser interface increment — 2026-10-09

Verified package 1.4.0 on Linux with Python 3.12.14 and the unchanged pinned
dependencies. The preceding corrected 89-test suite was also reported successful
by the user on Windows, with the symlink-permission test skipped. This new UI
increment has not yet been run on the user's Windows installation.

| Check | Result |
|---|---|
| Full suite in editable installation | 109 tests passed: previous 89 plus 20 HTTP/entry tests |
| Full suite in a fresh pinned environment with installed wheel | 109 tests passed |
| `python tools/check_web_acceptance.py` | All eight real HTTP/API results agree; all four files in each ZIP verified |
| Existing extraction and complete-workflow acceptance | Six extraction scenarios and eight workflow samples still agree with their CLIs |
| Wheel from outside the repository with isolated Python | Version 1.4.0, all four UI resources, processing API and `resumelens-ui` entry point verified |
| `python -m pip check` | No dependency conflicts in editable and wheel environments |
| `node --check src/resumelens/ui/app.js` | JavaScript syntax valid |
| Real browser interaction | 12 scenario groups passed using Chrome Headless Shell 153.0.8010.12 and Playwright 1.63.0 on Linux |
| Desktop and 390px mobile-width screenshots | Visually inspected; no horizontal overflow |

Browser checks covered initial assets, the packaged example, all eight uploaded
samples, four independent decisions, the sandboxed report, ZIP and four individual
downloads, exact BOM/CRLF/emoji offsets, pasted/edited text, fallback name, stale
result removal, invalid files, escaped injection, mobile layout, connection failure,
clearing the form and absence of page exceptions/external requests. ZIP contents
and individual downloads were compared byte for byte. Original file CRLF survives
the text area's LF display until the user edits; Python character offsets remain
unchanged.

The twenty new unittest cases exercise actual loopback HTTP connections, input
validation and request limits, fixed resources/routes, external Host/Origin
rejection, invalid DSL, download consistency, independent concurrent candidates,
port conflicts, browser options and clean shutdown. Processing is serialized
around cached models/parser, and no candidate files or request data are logged or
written by the server. ZIP output uses fixed filenames and timestamps.

Browser QA dependencies and downloaded Chrome were used only in the temporary
verification environment; they are not project dependencies. UI operation uses
the Python standard library and the existing processing dependencies. Windows UI,
macOS and other browser engines still require verification. A local 390px viewport
check is not a test on a physical mobile device. The final poster/presentation,
academic evidence and repository-history audit remain for the fifth increment.

Reproduce runtime checks and the manual browser checklist in [local-ui.md](local-ui.md).
Historical verification from the preceding increments follows.

## Complete-workflow increment — 2026-10-09

Verified on Linux, Python 3.12.14, using the existing pinned pyformlang 1.0.11,
jsonschema 4.26.0 and textX 4.4.0 dependencies. Package version is 1.3.0;
first-stage schema version and composed-result pipeline version remain 1.0.

| Check | Result |
|---|---|
| Full unittest suite in the editable environment | 89 tests passed: previous 67 plus 22 workflow/rendering/CLI tests |
| Full unittest suite in a second fresh environment with pinned dependencies and installed wheel | 89 tests passed |
| `python tools/generate_workflow_examples.py` | Eight complete bundles generated after DSL validation |
| `python tools/check_workflow_acceptance.py` | Real CLI and API agree in all four files for all eight samples; CLI runs from outside the repository |
| `python -m pip check` | No dependency conflicts in editable and pinned wheel environments |
| Installed wheel executed with isolated Python outside the repository | Version 1.3.0, grammar resource, four-stage API, bundle saving and console entry point verified |
| New workflow tests with cp1252 simulated as the default Path text-read encoding | All 22 passed; new fixture reads explicitly specify UTF-8 |
| Rendered HTML inspection | Full Stack, incomplete and multiple-profile examples rendered with WeasyPrint 70.0; incomplete and multiple-record layouts visually inspected |

The reports retain repeated contacts, education/experience records and multiple
accepted profiles. Candidate-derived text is escaped; syntax and semantic failures
prevent HTML generation. Saving checks consistency and all target paths before
writing. Tests cover overwrite rejection, force behavior, preservation of unrelated
files, input hard-link protection, BOM/CRLF, Unicode and malformed inputs.

Visual inspection used a separate QA renderer, not a browser engine. No new runtime
dependency is added. Real Windows execution, mobile browser layout and browser-engine
compatibility remain to be verified. A Windows run and its newline correction are
documented below. Output writes are not a filesystem transaction;
a mid-write operating-system failure can leave a partial bundle. The interactive
input UI, final project-wide documentation/presentation and Git-history requirements
remain outside this increment. Earlier verification is retained below.

### Windows newline correction before publishing this increment

The user ran all 89 tests on Windows. One fixture-comparison test failed in its
eight sample subcases; the symlink-permission test was skipped. The first-stage
JSON fixtures contain offsets for LF input, while the checkout samples contained
CRLF. Every preceding newline therefore shifted subsequent evidence positions.
Converting all eight samples to CRLF in an isolated Linux checkout reproduced
the same eight failures. Production processing correctly preserved those offsets.

Only the synthetic-fixture generator and comparison test now read samples with
universal-newline normalization to their documented LF input. The test additionally
processes CRLF variants, validates evidence against the exact input, checks the
expected offset shifts and compares classification, DSL and HTML with LF results.
The production API/CLI and raw-input acceptance check keep their original behavior.
The corrected 89-test suite and eight-sample acceptance check pass on Linux with
both LF and CRLF sample checkouts; regeneration produces the same stored bundles.
The user must rerun the corrected suite to verify their Windows installation.

## Candidate-language increment — 2026-10-09 UTC

Verified on Linux with Python 3.12.14, pyformlang 1.0.11, jsonschema 4.26.0,
textX 4.4.0 and Arpeggio 2.0.3. A second fresh environment installed the complete
`requirements-lock.txt` followed by the built wheel with `--no-deps`.

| Check | Result |
|---|---|
| `python -m unittest discover -s tests -q` | 67 passed: 39 original + 12 recognition + 16 DSL tests; verified in editable and wheel installations |
| `python tools/generate_dsl_examples.py` | Eight generated/parsed candidate examples accepted; five syntax and three semantic examples rejected |
| `python tools/check_acceptance.py` | Original API/CLI agree in six scenarios; JSON 1.0 evidence remains valid |
| `python tools/validate_design.py` | Catalog, profile criteria and existing sample expectations remain coherent |
| `python -m pip check` in the pinned wheel environment | No dependency conflicts |
| Version 1.2.0 wheel executed with isolated Python from outside the repository | Installed package and grammar resource confirmed; generation, textX parsing and Full Stack recognition passed |

The DSL tests cover string escaping, null/empty sections, repeated records and contacts,
canonical vocabulary, structural errors, duplicate declarations, profile coherence,
multiple accepted profiles, resource access and input immutability. The stored fixtures
are synthetic regression cases. New recognition/DSL behavior has not been executed on
Windows or macOS in this increment. HTML, a combined workflow CLI and UI remain pending.
The following sections preserve verification from earlier increments.

### Windows encoding correction before publishing this increment

A user run on Windows passed the 16 DSL tests and failed one recognition-model
comparison. That test read the UTF-8 automaton JSON using the system's default
encoding. Decoding the same file with cp1252 reproduced the failure on Linux:
the epsilon label became two incorrect characters, so reconstruction inserted
ordinary-symbol transitions in place of epsilon transitions. UTF-8 decoding
restored equality. Recognition tests now explicitly read all JSON fixtures as
UTF-8 and verify the epsilon label; the full transition-dictionary comparison
remains in place. This documents the reported failure and reproduced cause;
the corrected suite still requires execution on the user's Windows installation.

## Recognition increment — 2026-10-08

Verified on Linux, Python 3.12.14, pyformlang 1.0.11 and jsonschema 4.26.0 in a fresh
project environment. No textX or UI dependency is included in this increment.

| Check | Result |
|---|---|
| `python -m unittest discover -s tests -q` | 51 tests passed: 39 original + 12 recognition tests |
| `python tools/export_automata.py` | Four complete JSON/CSV/DOT/SVG epsilon-NFA exports |
| `python tools/classify_examples.py` | Eight executed classifications match existing design expectations |
| `python tools/check_acceptance.py` | Original API/CLI agree in six scenarios, with valid first-stage evidence |
| `python tools/validate_design.py` | Original catalog, profile criteria and eight expectations remain coherent |
| `python -m pip check` | No dependency conflicts in editable and wheel installations |
| Wheel installation in a second fresh environment, executed from outside the project | Version 1.1.0, packaged profiles, first-stage API and compatible-pair rejection verified |
| Four rendered automaton SVGs | Inspected for readable states, transitions, branch requirements and legends |

Recognition tests exercise all 72 minimal Full Stack combinations and missing-group
variants; 12 ML combinations; 9 Data combinations; all 12 single Backend pairs;
multiple-pair candidates; all 120 permutations of one Full Stack pattern; duplicates,
extra skills, invalid inputs, configuration checks and exported relation consistency.
These are deterministic synthetic/regression checks, not a real-resume accuracy estimate.

| Sample | Accepted profiles |
|---|---|
| 01_full_stack | Full Stack |
| 02_machine_learning | Machine Learning |
| 03_backend | Backend |
| 04_data_engineer | Data Engineer |
| 05_aliases_duplicates | Full Stack |
| 06_incomplete | None |
| 07_boundaries_negation | None |
| 08_multiple_records | Backend, Data Engineer, Machine Learning |

First-stage JSON 1.0 and the original CLI remained compatible in this recognition
increment. DSL, HTML and UI were not included in that increment. The sections below
retain the historical first-stage verification.

## Original first-stage verification

A fresh virtual environment was installed without global packages. Imports were verified inside it and consumption outside the project root was checked. Platform: Windows; Python 3.12.14, pyformlang 1.0.11, jsonschema 4.26.0. Tests use standard-library unittest. Other operating systems are unverified.

## Executed commands

| Command | Result |
|---|---|
| python -m venv NEW_PATH | Fresh environment created |
| python -m pip install -r requirements-lock.txt | Locked dependencies installed |
| python -m pip install --no-deps -e . | Local package installed |
| python -m unittest discover -s tests -v | 39 tests, OK |
| python -m pip check | No broken requirements found |
| python tools/check_acceptance.py | API/CLI equal in six scenarios; valid JSON/evidence |
| python tools/validate_design.py | 26 symbols, 56 aliases, four design patterns, eight coherent scenarios |
| python tools/generate_examples.py | Eight outputs regenerated |
| python tools/evaluate.py | 23 cases, metrics separated by group |
| python tools/document_regex.py | Exact patterns and supported scope generated |
| python tools/export_models.py | Four complete JSON/CSV/DOT/SVG machine exports regenerated |

Here python denotes the virtual-environment executable. PyPI supplied dependencies and the build backend was installed in isolation. No textX, UI or recognition models are needed.

## Verified behavior

- Multiple records, sections, absent/manual names and original assignment fragments.
- Unicode, BOM, CRLF, actual positions and no duplicate contained records.
- All 56 aliases under three capitalization variants, literal dots and JavaScript/GitHub boundaries.
- Contextual React, JS/TS and Pandas; animal exclusions without losing technical positives.
- Eight negation patterns, lists and contrast retaining later positive skills.
- Unknown variants, catalog conflicts and rejection of multiple canonical outputs.
- Four FST sizes, output alphabets, formal model exports and cached reuse.
- Corrupted schema version, offsets, indices and translations are rejected.
- Public API, CLI, nested output, --force and invalid-input errors.
- English diagnostics and regenerated English main examples; Spanish regression inputs remain supported.

The previous revision had 35 tests; three Pandas regressions raised the total to 38. A complete English-language regression brought that first-stage total to 39. Eight sample symbol expectations remain unchanged. Profile expectations in `expected_samples.json` remain design annotations; their executed recognition outputs now appear separately in `data/classification/`.

## Evaluation and limits

Fifteen admitted cases yield TP=25/FP=0/FN=0; six historical reserved cases yield TP=14/FP=0/FN=0. Two stress cases yield TP=0/FP=0/FN=2, with undefined precision. Reserved cases now serve as regression after extractor changes. Prior results and reclassification reasons are retained; see `evaluation.md`.

Complete FST exports were regenerated from the executable machines and their components checked by tests. Their visual layout and the existing partial poster were reviewed in an earlier revision. The poster has not been regenerated and retains earlier metrics, identified in its README. This historical first-stage verification did not cover profile automata. Current recognition, DSL, workflow and local UI results are recorded above.
