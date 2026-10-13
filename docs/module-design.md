# Module design and integration

`tools/evaluate_preannotated.py` is an evaluation adapter, separate from the
runtime pipeline. It loads and validates the frozen labels and fingerprints,
calls `process_complete_resume`, checks cross-stage integrity, scores exact spans,
canonical/profile sets and candidate fields, and produces reproducible reports.
Its `--check` mode reads stored reports without rewriting them. The core API and
formal models are unchanged; see [evaluation protocol](preannotated-evaluation.md).

Modules separate extraction, normalization, validation and execution to preserve the link between input and output.

```mermaid
flowchart TD
    U[ui/: browser input and outputs] --> W[web.py: local HTTP adapter]
    W --> T[UTF-8 TXT or interface text]
    T --> E[extraction.py and re]
    C[Alias catalog] --> E
    C --> F[normalization.py and pyformlang FST]
    E -->|Original evidence| F
    E --> P[first_stage.py]
    F --> P
    P --> V[Schema and semantic validation]
    V --> J[JSON 1.0 or dictionary]
    J --> A[classification.py and four complete DFAs]
    A --> D[dsl.py and packaged textX grammar]
    D --> H[rendering.py: standalone HTML]
    H --> U
```

## Responsibilities

| Module/function | Input | Output | Relevant condition |
|---|---|---|---|
| catalog.load_catalog | None | Configuration dictionary | Reads packaged resource independently of cwd |
| catalog.validate_catalog | Dictionary | None or ValueError | Unique casefolded aliases |
| extraction.skill_pattern | Catalog | re.Pattern | Escaped alternation, longer aliases first |
| extraction.extract_resume | Text, optional name/catalog | candidate, extracted_skills, excluded_mentions, warnings | Preserves text; does not normalize |
| normalization.build_transducers | Optional catalog | Category → FST dictionary | Independent alias paths; output on final transition |
| normalization.normalize_skills | Evidence list, machines | normalized_skills, normalization_evidence, unknown_skills | Executes FST.translate |
| first_stage.process_resume | Text, optional name | Complete 1.0 object | Public entry point |
| first_stage.validate_result | 1.0 object and exact text | None or exception | Schema, spans, indices and actual translations |
| cli.main | CLI arguments | Exit 0/2, JSON or diagnostic | Preserves CRLF; prevents overwrite by default |
| classification.load_profiles / validate_profile | Packaged configuration / profile dictionary | Four profiles / None or ValueError | Known symbols, nonempty requirements and disjoint buckets |
| classification.profile_buckets | Profile dictionary | Disjoint symbol sets in canonical order | Common input structure for all four patterns |
| classification.build_profile_automaton | Profile dictionary | pyformlang DeterministicFiniteAutomaton | Complete symbol transitions, required groups, compatible pairs and a rejecting sink |
| classification.canonical_sequence | Canonical skills and profile | Ordered relevant symbols | Retains all compatible-pair candidates |
| classification.classify_skills | Canonical-symbol collection | accepted_profiles and four detailed results | Executes accepts(); separate from JSON 1.0 |
| dsl.generate_candidate_dsl | JSON 1.0 and recognition result | Candidate DSL string | JSON escaping, canonical symbols and repeated records |
| dsl.parse_candidate_dsl | Candidate DSL string | Validated candidate dictionary | textX syntax, unique declarations and profile coherence |
| rendering.render_candidate_html | Candidate DSL string | Standalone HTML | Parses before rendering; escapes candidate-derived text |
| workflow.process_complete_resume | Exact text, optional name | First-stage result, classification, DSL, parsed candidate and HTML | Connects all four stages without altering JSON 1.0 |
| workflow.save_bundle | Complete result and destination | Four UTF-8 files or filesystem diagnostic | Cross-stage consistency, exclusive workspace, prepared outputs, original backups and controlled rollback |
| workflow_cli.main | CLI arguments | Exit 0/2, bundle or diagnostic | BOM/CRLF compatibility and original-input protection |
| web.process_web_request | JSON text and optional name | Complete result, four downloads and base64 ZIP | Type/size checks and existing bundle validation |
| web.create_server / main | Local port / CLI arguments | Loopback server / exit 0 or 2 | Fixed routes, packaged assets and Ctrl+C shutdown |
| ui/app.js | File bytes, text, keyboard actions and HTTP response | Four decisions, report, downloads, focus destinations and live feedback | Strict UTF-8, exact unedited CRLF, cleared stale results, guarded busy state and preserved user focus |

## Types and evidence

Evidence is `{raw: str, start: int, end: int}` in Python characters, not bytes. ExcludedEvidence adds `reason`. NormalizationEvidence is `{extracted_index: int, canonical: str}`, addressing evidence rather than unique symbols. Names are `str | None`; other candidate fields are evidence lists.

Packaged catalog/schema copies match `config/` and `contracts/`; tests detect divergence. Symbol changes affect schema enum and profile patterns. Incompatible changes require an agreed contract version.

## Education and experience

Known headings, with or without colons, start sections. Each nonempty following line is a record until another heading. Bullets and surrounding whitespace are removed without losing offsets. Explicit section records take priority over contained phrases, preventing duplicates. Outside sections, supported degree and experience phrases are recognized.

A line is one evidence record, not necessarily an entire job. Grouping multiline descriptions into structured positions would require additional rules and a new contract.

## Context and negation

JS/TS require skills headings with recognized-alias continuation lists. Unsuffixed React accepts that context, supported development/work phrases ending in using/with or Spanish equivalents, immediate know/use or sé/se/conozco/uso predicates, or a following framework/library word. Explicit negation is evaluated before these context checks. React.js/ReactJS remain literal.

Pandas accepts skills sections or both an immediate use verb and a data analysis/processing complement. Capitalization alone is insufficient.

Explicit negative phrases include do not know/use, don't/don’t know/use and no sé/se/conozco, in addition to the existing experience/knowledge and no uso forms. They cover the immediate alias or a known-alias list separated by comma, slash or and/or/nor/y/o/ni, including a comma before a conjunction. Other words interrupt the list. Closing punctuation, semicolons, line breaks and contrast connectors end scope. New knowledge/use forms allow horizontal spaces/tabs without crossing lines. Double negation and irony remain unsupported. See [negation examples and limits](negation-handling.md).

## Errors and shared state

Profile recognition also derives `explanations` and `pair_diagnostics` after the
actual DFA decision. Labels come from the catalog and alternatives from the
validated profile configuration. The UI uses those messages as text; standalone
HTML recomputes them from parsed DSL skills and escapes them. Missing alternatives
do not introduce inferred skills or a second acceptance rule. See
[diagnostic structure and examples](profile-explanations.md).

Empty input is rejected. The CLI reports invalid files, encoding and input/output identity in English. Default FSTs are built once and privately cached; results are fresh on every call. There is no persistent candidate state or UI dependency.

JSON is a data boundary, not proof of profile acceptance. Recognition returns its results in a separate object; textX validates the candidate representation before HTML generation. The local UI uses that same complete workflow. Packaged profile configuration matches `config/profiles_design.json`, checked by tests. Private cached machines are reused; callers receive fresh result data. The HTTP adapter serializes processing around cached parser/model access and keeps no candidate history.

The keyboard flow is documented in [keyboard-navigation.md](keyboard-navigation.md).
Native links/details control navigation and downloads. Status/error containers
remain outside the busy form; UI validation associates errors with inputs. The
optional browser acceptance runner starts the installed loopback server and
checks actual interactions independently of the runtime dependency list.
