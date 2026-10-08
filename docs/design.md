# Extraction and normalization design

ResumeLens turns resume text into candidate information and canonical symbols. Regex locates original expressions; FSTs model equivalences. Every transformation retains verifiable evidence.

## Flow

UTF-8 TXT → Python re extraction → pyformlang FST normalization → validation → JSON 1.0.

The overall architecture also includes profile recognition with automata and a textX-validated representation DSL. Only extraction and normalization are implemented; their JSON supplies later recognition and representation.

## Technical decisions

| Aspect | Design | Reason |
|---|---|---|
| Input | UTF-8 text | Keeps OCR and document-layout parsing outside formal recognition |
| Languages | Documented English and Spanish input formats | Preserves explicit technology variants |
| Evidence | raw, start, end | Verifies fragments without changing input |
| Skills | Finite catalog | Auditable equivalences and no conflicting aliases |
| Normalization | One FST per category | Common implementation with separate formal vocabularies |
| Preparation | casefold of a copy | Ignores capitalization without changing evidence |
| Output | Schema-validated JSON 1.0 | Structured, reproducible exchange |
| Ordering | Unique alphabetical symbols | Stable comparison; profile ordering is prepared later |

Four categories cover languages, frameworks/libraries, databases and tools/qualifications. Longer aliases precede shorter ones. Normalization consumes the complete variant and emits one symbol. PostgreSQL does not imply SQL; PySpark does not imply Apache Spark.

Documentation, code comments, CLI messages and main examples are English. Spanish input patterns and regression fixtures retain bilingual compatibility.

## Profile patterns

`config/profiles_design.json` describes Full Stack Developer, Machine Learning Engineer, Backend Developer and Data Engineer. Every required group must be satisfied, with alternatives inside groups. Backend additionally requires a compatible language/framework pair. Extra skills must not cause rejection.

These configurable patterns are design criteria, not hiring decisions. Assignment examples motivate documented minimums. Additional profile requirements must be checked against their specifications before implementing recognition.

## Limits

A mention does not establish proficiency. Explicit sections, contextual React/Pandas/JS/TS rules and bounded negation provide traceability, not general language understanding. Education/experience retain text without inferring institution, company or accumulated duration. Other homonyms, double negation and unknown vocabulary are documented in `evaluation.md`.
