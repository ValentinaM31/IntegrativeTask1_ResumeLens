# Processing and representation acceptance matrix

Complete means the documented extraction, normalization, recognition, candidate-language, HTML and local UI scope; it does not certify final presentation materials or the complete Git history.

| Requirement | Evidence | Check | Status |
|---|---|---|---|
| Candidate/skills regex | extraction.py, regex.md | Records, contact, aliases, offsets | Complete in supported formats |
| React/Pandas/JS/TS context | extraction.py | Technical cases and nontechnical prose | Complete for explicit rules |
| Negation/contrast | extraction.py, regex.md, test_negation.py | Knowledge/use forms, apostrophes, Spanish variants, lists, later positives and false-profile regression through CLI/HTTP | Complete for explicit rules |
| Real pyformlang FSTs | normalization.py | 56 aliases, case, unknowns, conflicts, ambiguous outputs | Complete |
| Complete formal models | transducers.md, models/ | Matches actual machines and exports | Complete |
| Contract 1.0/evidence | first_stage.py, schema | Version, types, offsets, indices, translations | Complete |
| API/CLI | first_stage.py, cli.py | Fresh environment, six acceptance scenarios | Complete |
| Four executable profiles | classification.py, profiles_design.json | Complete DFAs with one transition per state/symbol, rejecting sinks, alternatives, missing groups, compatible pairs and overlap | Implemented for the configured patterns; current verification is recorded in test-results.md |
| Reference-profile alignment | profile-alignment.md, test_profile_alignment.py, automata/MACHINE_LEARNING_ENGINEER.* | Scikit-learn/TensorFlow/PyTorch alternative group from assignment page 5; full API/CLI/HTTP/DSL regression bundles | Reference diagram aligned; separate additional-profile teacher requirements remain unverified |
| Complete automaton five-tuples and diagrams | profile-recognition.md, automata/ | Relations reconstructed and compared with execution | Complete |
| Recognition results | data/classification/ | Eight sample outputs match existing expectations | Complete; synthetic examples |
| Profile explanations | classification.py, profile-explanations.md, test_profile_explanations.py | Missing groups, pair incompatibility, configured alternatives, real CLI/HTTP and shared JSON/HTML messages | Complete for configured requirements |
| Disk export recovery | workflow.py, bundle-recovery.md, test_bundle_recovery.py | Prepared files, original backups, four failure positions across 16 original-presence combinations, failed recovery and retry | Complete for controlled filesystem failures; abrupt termination requires inspection |
| Reproducible cases | samples/, results/, evaluation/ | Eight main English samples, 23 annotated cases | Complete; synthetic evaluation |
| Preannotated pipeline evaluation | preannotated-evaluation.md, data/preannotated-evaluation/, evaluate_preannotated.py | Frozen labels/inputs, 18 valid pipelines, 14 exact cases, retained span/profile errors and reproducible JSON/Markdown | Complete for synthetic evaluation; no external-human or population-accuracy claim |
| English project text | README, docs, source/messages | Tests, regeneration, text review | Complete; quoted bilingual input remains |
| Sources | literature-review.md | Full-paper/abstract distinction | Available foundation, not systematic review |
| Integration guide | handoff.md | API/CLI acceptance | Complete |
| Academic AI-use record | docs/ai-usage.md and original interaction records | Check factual summaries and submit original transcripts | Summary available; original transcripts and independent student review remain submission requirements |
| Technical poster | poster/ | Editable SVG, same-scene PDF render, animated walkthrough, model diagrams and separate evaluation figures | Complete poster artifact; presentation rehearsal remains |
| Candidate DSL and EBNF | candidate.tx, dsl.py, candidate-language.md | Fixed sections, terminals/nonterminals, canonical vocabulary and repeated records | Complete |
| textX syntax and semantic validation | tests/test_dsl.py, data/dsl/ | 16 tests; eight valid and eight invalid examples | Complete |
| Complete four-stage workflow | workflow.py, workflow_cli.py | Eight executed bundles; original JSON/CLI compatibility | Complete |
| HTML after validated DSL | rendering.py, data/workflow/ | Syntax/semantic rejection, escaping, records and multiple profiles | Complete |
| Interactive input UI | web.py, ui/, local-ui.md, keyboard-navigation.md | Paste/load TXT, fallback name, four decisions, reports/downloads, keyboard flow and error recovery | Complete for the documented scope; 18 scenario groups have Linux and Windows Chrome runs; desktop and narrow Windows visual checks recorded |
| Web downloads | web.py, tests/test_web.py | Eight HTTP/API results, ZIP and individually downloaded files | Complete |

## Verified corrections

Previously, react as a verb produced REACT and some simple negations retained Python. Pandas as an animal also produced PANDAS. Context and clause rules now retain exclusions with reasons, while technical positives survive. JSON structure/version, cached real FSTs, documented contact extraction and formal models were preserved.

Double negation, irony, unsupported technical wording and other homonyms remain outside scope. The catalog does not discover universal vocabulary. The implemented Backend/Data patterns follow the existing team criteria; any separately supplied teacher requirements still need to be checked.
