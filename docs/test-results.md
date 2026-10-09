# Verification results

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

First-stage JSON 1.0 and the original CLI remain compatible. Later DSL, HTML and UI
are not included. The sections below retain the historical first-stage verification.

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

Complete FST exports were regenerated from the executable machines and their components checked by tests. Their visual layout and the existing partial poster were reviewed in an earlier revision. The poster has not been regenerated and retains earlier metrics, identified in its README. This historical first-stage verification did not cover profile automata. Current recognition results are recorded above; textX, UI and HTML remain outside this increment.
