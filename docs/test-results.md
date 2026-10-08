# Verification results

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

The previous revision had 35 tests; three Pandas regressions raised the total to 38. A complete English-language regression brings the current total to 39. Eight sample symbol expectations remain unchanged. Profile expectations in `expected_samples.json` are design checks, not executed classification.

## Evaluation and limits

Fifteen admitted cases yield TP=25/FP=0/FN=0; six historical reserved cases yield TP=14/FP=0/FN=0. Two stress cases yield TP=0/FP=0/FN=2, with undefined precision. Reserved cases now serve as regression after extractor changes. Prior results and reclassification reasons are retained; see `evaluation.md`.

Complete FST exports were regenerated from the executable machines and their components checked by tests. Their visual layout and the existing partial poster were reviewed in an earlier revision. The poster has not been regenerated and retains earlier metrics, identified in its README. Verification does not cover profile automata, textX, UI or HTML, which remain unimplemented.
