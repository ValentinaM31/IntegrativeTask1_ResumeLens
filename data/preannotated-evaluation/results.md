# Preannotated synthetic evaluation

Labels and inputs were frozen before this dataset was executed. Texts and labels are AI-assisted synthetic work; no external human annotator or real-resume accuracy is claimed.

Baseline: `6d6ea17a37385d872f49925569db847777b01948`. Annotation SHA-256: `16bc5bbe5ec874806d1e6ceac77e9d6b30da0350312d584034501aa52344928e`.

Runtime unchanged since freeze: **true**. Comparison: `frozen_baseline_comparison`.

## Positive skill mentions

| Group | Cases | TP | FP | FN | Precision | Recall | F1 | Exact cases |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| supported | 14 | 76 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 14/14 |
| stress | 4 | 18 | 3 | 3 | 0.8571 | 0.8571 | 0.8571 | 0/4 |
| overall | 18 | 94 | 3 | 3 | 0.9691 | 0.9691 | 0.9691 | 14/18 |

## Separate outcomes

| Unit | TP | FP | FN | Precision | Recall | F1 | Exact cases |
|---|---:|---:|---:|---:|---:|---:|---:|
| excluded_mentions | 5 | 2 | 3 | 0.7143 | 0.6250 | 0.6667 | 15/18 |
| canonical_skills | 92 | 3 | 2 | 0.9684 | 0.9787 | 0.9735 | 15/18 |
| accepted_profiles | 17 | 1 | 2 | 0.9444 | 0.8947 | 0.9189 | 15/18 |

Pipeline/schema/DSL/HTML integrity: **18/18**. All annotation units exact: **14/18**.

Unknown positive technology spans missed: **1**. Unknown annotations have no invented canonical enum; span misses and canonical agreement are different units.

## Candidate data

| Field | TP | FP | FN | Exact cases |
|---|---:|---:|---:|---:|
| name (exact value) | n/a | n/a | n/a | 18/18 |
| emails | 2 | 0 | 0 | 18/18 |
| phones | 1 | 0 | 0 | 18/18 |
| links | 1 | 0 | 0 | 18/18 |
| education | 2 | 0 | 0 | 18/18 |
| experience | 2 | 0 | 0 | 18/18 |

These sparse fields are coverage checks, not estimates of contact/record accuracy on real resumes.

## Profile decisions

| Profile | TP | FP | FN | TN |
|---|---:|---:|---:|---:|
| FULL_STACK_DEVELOPER | 4 | 0 | 0 | 14 |
| MACHINE_LEARNING_ENGINEER | 5 | 1 | 2 | 10 |
| BACKEND_DEVELOPER | 5 | 0 | 0 | 13 |
| DATA_ENGINEER | 3 | 0 | 0 | 15 |

## Every case

| Case | Group | Mention TP/FP/FN | Actual profiles | All labels exact |
|---|---|---|---|---|
| E01_alias_full_stack | supported | 5/0/0 | FULL_STACK_DEVELOPER | true |
| E02_scikit_learning | supported | 5/0/0 | MACHINE_LEARNING_ENGINEER | true |
| E03_incompatible_backend | supported | 5/0/0 | none | true |
| E04_compatible_backend | supported | 6/0/0 | BACKEND_DEVELOPER | true |
| E05_data_pipeline | supported | 4/0/0 | DATA_ENGINEER | true |
| E06_four_profiles | supported | 10/0/0 | BACKEND_DEVELOPER, DATA_ENGINEER, FULL_STACK_DEVELOPER, MACHINE_LEARNING_ENGINEER | true |
| E07_repeated_records | supported | 7/0/0 | FULL_STACK_DEVELOPER | true |
| E08_negative_contrast | supported | 5/0/0 | FULL_STACK_DEVELOPER | true |
| E09_spanish_negation | supported | 4/0/0 | none | true |
| E10_two_profiles | supported | 6/0/0 | BACKEND_DEVELOPER, DATA_ENGINEER | true |
| E11_animal_pandas | supported | 4/0/0 | none | true |
| E12_react_verb | supported | 5/0/0 | MACHINE_LEARNING_ENGINEER | true |
| E13_unicode_bom_crlf | supported | 5/0/0 | MACHINE_LEARNING_ENGINEER | true |
| E14_fallback_name | supported | 5/0/0 | MACHINE_LEARNING_ENGINEER | true |
| E15_unknown_rust | stress | 5/0/1 | BACKEND_DEVELOPER | false |
| E16_double_negation | stress | 4/0/1 | none | false |
| E17_external_requirement | stress | 5/3/0 | BACKEND_DEVELOPER, MACHINE_LEARNING_ENGINEER | false |
| E18_pandas_other_context | stress | 4/0/1 | none | false |

## Observed disagreements

### E15_unknown_rust

Input: `inputs/E15_unknown_rust.txt`; tags: unknown_technology.

positive_mentions: `{"false_positive": [], "missed": [[24, 28, "Rust"]]}`.

### E16_double_negation

Input: `inputs/E16_double_negation.txt`; tags: double_negation.

positive_mentions: `{"false_positive": [], "missed": [[93, 99, "Python"]]}`.

excluded_mentions: `{"false_positive": [[93, 99, "Python"]], "missed": []}`.

canonical_skills: `{"false_positive": [], "missed": ["PYTHON"]}`.

accepted_profiles: `{"false_positive": [], "missed": ["MACHINE_LEARNING_ENGINEER"]}`.

### E17_external_requirement

Input: `inputs/E17_external_requirement.txt`; tags: source_attribution.

positive_mentions: `{"false_positive": [[92, 98, "Python"], [100, 105, "NumPy"], [110, 117, "sklearn"]], "missed": []}`.

excluded_mentions: `{"false_positive": [], "missed": [[92, 98, "Python"], [100, 105, "NumPy"], [110, 117, "sklearn"]]}`.

canonical_skills: `{"false_positive": ["NUMPY", "PYTHON", "SCIKIT_LEARN"], "missed": []}`.

accepted_profiles: `{"false_positive": ["MACHINE_LEARNING_ENGINEER"], "missed": []}`.

### E18_pandas_other_context

Input: `inputs/E18_pandas_other_context.txt`; tags: pandas_context, technical_prose.

positive_mentions: `{"false_positive": [], "missed": [[74, 80, "pandas"]]}`.

excluded_mentions: `{"false_positive": [[74, 80, "pandas"]], "missed": []}`.

canonical_skills: `{"false_positive": [], "missed": ["PANDAS"]}`.

accepted_profiles: `{"false_positive": [], "missed": ["MACHINE_LEARNING_ENGINEER"]}`.

## Interpretation and reuse

Micro precision = TP/(TP+FP), recall = TP/(TP+FN), F1 = 2TP/(2TP+FP+FN); zero denominators are n/a. Positions refer to decoded UTF-8-sig text, preserving CRLF. Repeated raw words at different positions are distinct mentions.

Internal pipeline validity does not establish correct interpretation of a resume. Dataset construction was informed by prior project behavior. Selected supported/stress cases are not representative of a population; later reuse is regression. Expectations, unsupported cases and observed errors are retained rather than adjusted to match outputs.

See `docs/preannotated-evaluation.md` for protocol, formulas, limitations and reproduction.
