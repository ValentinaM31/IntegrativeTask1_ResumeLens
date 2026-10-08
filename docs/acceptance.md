# Extraction and normalization acceptance matrix

Complete means the documented extraction/normalization scope; it does not certify later recognition, DSL or the complete Git history.

| Requirement | Evidence | Check | Status |
|---|---|---|---|
| Candidate/skills regex | extraction.py, regex.md | Records, contact, aliases, offsets | Complete in supported formats |
| React/Pandas/JS/TS context | extraction.py | Technical cases and nontechnical prose | Complete for explicit rules |
| Negation/contrast | extraction.py, regex.md | Eight patterns, lists, later positives | Complete for explicit rules |
| Real pyformlang FSTs | normalization.py | 56 aliases, case, unknowns, conflicts, ambiguous outputs | Complete |
| Complete formal models | transducers.md, models/ | Matches actual machines and exports | Complete |
| Contract 1.0/evidence | first_stage.py, schema | Version, types, offsets, indices, translations | Complete |
| API/CLI | first_stage.py, cli.py | Fresh environment, six acceptance scenarios | Complete |
| Four design profiles | profiles_design.json | Vocabulary compatibility | Complete as design only |
| Reproducible cases | samples/, results/, evaluation/ | Eight main English samples, 23 annotated cases | Complete; synthetic evaluation |
| English project text | README, docs, source/messages | Tests, regeneration, text review | Complete; quoted bilingual input remains |
| Sources | literature-review.md | Full-paper/abstract distinction | Available foundation, not systematic review |
| Integration guide | handoff.md | API/CLI acceptance | Complete |
| Academic AI-use record | Separate evidence outside code | Submit separately | Available; independent submission required |
| Technical poster | poster/ | Existing rendered SVG | Partial for overall project; earlier metrics |
| Automata, textX, UI, HTML | No implementation | Outside audited component | Pending later stages |

## Verified corrections

Previously, react as a verb produced REACT and some simple negations retained Python. Pandas as an animal also produced PANDAS. Context and clause rules now retain exclusions with reasons, while technical positives survive. JSON structure/version, cached real FSTs, documented contact extraction and formal models were preserved.

Double negation, irony, unsupported technical wording and other homonyms remain outside scope. The catalog does not discover universal vocabulary. Additional profile criteria must be checked against their specifications before recognition is implemented.
