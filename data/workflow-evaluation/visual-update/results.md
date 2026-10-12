# Original fourteen-case workflow regression

Eight existing sample expectations/reference outputs plus six original prepared additional cases, recovered unchanged. Expanded candidate/exclusion/link labels were added after the earlier profile-only execution; AI-assisted regression, not new preannotated or blind evaluation.

Baseline: `477dee97c21897189c8b6dda851ec976f0bad2a4`. Annotation SHA-256: `2b36307edd11e942ed0a75a255b67426730392e7fc44ece146538614b0458a57`.

Fully matching cases and exports: **14/14**. Valid pipelines: **14/14**.

| Unit | Exact cases | TP | FP | FN |
|---|---:|---:|---:|---:|
| positive_mentions | 14/14 | 65 | 0 | 0 |
| excluded_mentions | 14/14 | 7 | 0 | 0 |
| canonical_skills | 14/14 | 62 | 0 | 0 |
| accepted_profiles | 14/14 | 11 | 0 | 0 |
| candidate emails | 14/14 | 7 | 0 | 0 |
| candidate phones | 14/14 | 2 | 0 | 0 |
| candidate links | 14/14 | 2 | 0 | 0 |
| candidate education | 14/14 | 8 | 0 | 0 |
| candidate experience | 14/14 | 10 | 0 | 0 |
| Candidate name | 14/14 | n/a | n/a | n/a |
| Normalization links | 14/14 | n/a | n/a | n/a |
| Export round trip | 14/14 | n/a | n/a | n/a |

## Every case

| Case | Labels exact | Export exact |
|---|---|---|
| 01_full_stack | true | true |
| 02_machine_learning | true | true |
| 03_backend | true | true |
| 04_data_engineer | true | true |
| 05_aliases_duplicates | true | true |
| 06_incomplete | true | true |
| 07_boundaries_negation | true | true |
| 08_multiple_records | true | true |
| missing_data_pipeline | true | true |
| incompatible_backend_pair | true | true |
| negated_framework | true | true |
| multiple_profiles | true | true |
| irrelevant_prose | true | true |
| records_and_escaping | true | true |

## Recorded differences

No differences were observed against the fixed annotations in this execution.

## Limits

This integrates previously executed cases. Eight cases reuse known reference outputs; the six additional cases retain their original texts and profile expectations. Expanded candidate/span/link annotations were added during integration. This is AI-assisted synthetic regression, not a newly blind or independently human-annotated evaluation.

The original 23-case extraction evaluation and the separate 18-case preannotated evaluation retain their own datasets and figures. These results are not population-accuracy estimates. See `docs/workflow-evaluation.md` for provenance, scoring and reproduction.
