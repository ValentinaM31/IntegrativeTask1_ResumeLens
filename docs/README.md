# Documentation index

Follow the operating instructions for the current checkout. Verification records contain dated runs and earlier stage results; read the revision and platform associated with each entry before applying its counts or conclusions.

## Current operating instructions

| Document | Purpose |
|---|---|
| [Project README](../README.md) | Installation, browser/CLI usage, verification commands and repository structure |
| [Local interface](local-ui.md) | Loopback server, TXT loading, input fidelity and downloads |
| [Keyboard navigation](keyboard-navigation.md) | Focus behavior, feedback, downloads and optional browser checks |
| [Complete workflow](complete-workflow.md) | Composed API, CLI, validated HTML and four-file bundle |
| [Bundle recovery](bundle-recovery.md) | Prepared exports, backups, controlled failure recovery and termination limits |
| [First-stage API](api.md) | Extraction-result contract and compatibility |
| [First-stage integration](handoff.md) | TXT-to-JSON integration and acceptance for that component |
| [Acceptance matrix](acceptance.md) | Implemented requirements and outstanding submission evidence |

The first-stage guides document `process_resume()` and the original JSON command. Use the complete-workflow and interface guides for later stages; component scope is not the scope of the complete application.

## Design and formal models

| Document | Purpose |
|---|---|
| [Design](design.md) / [module design](module-design.md) | Components, functions, inputs, outputs and relationships |
| [Regular expressions](regex.md) / [negation handling](negation-handling.md) | Exact patterns, bounded context and exclusions |
| [Transducers](transducers.md) / `models/` | Four real FSTs, complete seven-tuples, tables and graphs |
| [Profile recognition](profile-recognition.md) / `automata/` | Four epsilon-NFAs, complete five-tuples, diagrams and canonical order |
| [Requirement alignment](profile-alignment.md) | Assignment criteria, ML alternatives and team-defined extensions |
| [Profile explanations](profile-explanations.md) | Missing groups, incompatible backend pairs and repair alternatives |
| [Candidate language](candidate-language.md) | EBNF, terminals/nonterminals, textX syntax and semantic checks |
| [Data contract](data-contract.md) | JSON 1.0 schema and evidence conventions |
| [Literature review](literature-review.md) / [foundations](fundamentals.md) | Sources, formal concepts and evidence scope |

Exported FST and automaton graphs are versioned model evidence, not disposable output. When models change, regenerate and review their tables and graphs together.

## Evaluation and verification evidence

| Document or dataset | Purpose |
|---|---|
| [Test plan](test-plan.md) | Scenarios and behavior to verify |
| [Verification results](test-results.md) | Dated executions; current and historical entries retain their own revision/platform scope |
| [Skill-mention evaluation](evaluation.md) | Original 23 synthetic cases, exact spans, metrics and limitations |
| [Original fourteen-case workflow regression](workflow-evaluation.md) | Previously executed inputs, expanded annotation units, original draft provenance and export round trips |
| [Preannotated evaluation](preannotated-evaluation.md) | Separate 18-case pipeline dataset, frozen labels, scoring and disagreements |
| [Dataset protocol](../data/preannotated-evaluation/README.md) | Input preservation, annotation provenance and stored-report verification |
| [Profile-alignment examples](../data/profile-alignment/README.md) | Targeted regression inputs and reference bundles |
| [DSL examples](../data/dsl/README.md) | Valid/invalid specifications and validation results |
| [Workflow examples](../data/workflow/README.md) | Eight stored JSON/DSL/HTML bundles and reproduction rules |

Reference files under `data/`, packaged resources under `src/resumelens/`, and contracts are required evidence or test inputs. Keep the evaluations separate and retain recorded errors. Generators may overwrite results; use `tools/evaluate_preannotated.py --check` to verify its stored reports without rewriting them.

## Historical material and presentation status

`data/evaluation/history/` preserves earlier annotations and metrics. The original reserved-case protocol preserves its earlier source fingerprint. These files explain changes and limitations; they are historical evidence, not current installation instructions or a new independent evaluation.

[The complete poster](poster/README.md) provides editable SVG, printable PDF and animated HTML with a guided worked example. Its test figures come from an executed verification snapshot; its three evaluation datasets remain separate.

Older sections in `test-results.md` and component guides describe earlier revisions. Retain them for traceability while following the current operating instructions above. Documentation and messages are in English; quoted bilingual fixtures remain within the tested input scope. The assignment's academic AI-use record must describe actual interactions and student work.
