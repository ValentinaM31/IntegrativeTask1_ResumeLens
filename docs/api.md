# Processing API

`process_resume(text, name=None)` returns a fresh contract 1.0 object. It can be consumed by another component or the CLI without running profile recognition or textX validation.

```python
from resumelens import process_resume

with open("resume.txt", encoding="utf-8-sig", newline="") as stream:
    text = stream.read()
result = process_resume(text)
candidate = result["candidate"]
symbols = set(result["normalized_skills"])
```

Retain the exact text to highlight evidence: `text[start:end] == raw`. JSON includes neither full input text nor a file fingerprint; consumers must retain the input/result association.

## Consuming results

`candidate` holds a name and lists of contact, education and experience evidence. An absent name is null; other absent categories are empty lists. `normalization_evidence.extracted_index` addresses `extracted_skills`, not the unique symbol list. One symbol can have multiple evidence records.

Alphabetical `normalized_skills` order is not automaton reading order. Recognition must prepare sequences for each profile and execute its model. Schema 1.0 forbids extra properties; profile results belong in a separate later model.

## Recognition API

`from resumelens import classify_skills` exposes stage 3. Pass `result["normalized_skills"]`;
the returned dictionary has `accepted_profiles` and four `profiles` results, including
the actual input sequence and rejection explanations. It uses real epsilon-NFA
acceptance and leaves `result` unchanged. Several profiles may be accepted. An empty
collection rejects all profiles; unknown/non-string symbols or invalid collections
raise ValueError. See [recognition definitions and examples](profile-recognition.md).

`ValueError` reports empty input or semantic inconsistency. File/encoding errors are reported by the CLI. Unknown terms are recorded only when passed to the normalizer; extraction does not discover arbitrary technologies. Program diagnostics are in English.

## Candidate-language API

`generate_candidate_dsl(first_stage, classification)` returns a candidate specification
string from the unchanged JSON 1.0 and separate recognition result. The public
`parse_candidate_dsl(source)` executes textX, checks duplicate declarations and
profile coherence, and returns a dictionary with name, contacts, education,
experience, skills and accepted_profiles. It supports repeated records and escaping;
syntax errors are textX exceptions and additional semantic failures are ValueError.
See [full grammar and examples](candidate-language.md). These DSL functions do not render HTML; use the separate complete workflow below.

## Complete workflow and rendering API

`process_complete_resume(text, name=None)` returns pipeline version 1.0, the unchanged
first-stage object, recognition results, generated DSL, parsed candidate and HTML.
`render_candidate_html(dsl_source)` always parses before rendering. `save_bundle(result,
destination, force=False)` verifies consistency before writing four UTF-8 files; it
rejects existing outputs by default. See [complete workflow](complete-workflow.md)
for fields, errors and practical limits. The original TXT-to-JSON CLI is unchanged.

## Contract changes

Changing a symbol affects the catalog, FSTs, schema enum and profile configuration. Incompatible changes require a new version. Added aliases must remain unique after casefold; regenerate formalizations and regex documentation, then run tests.
