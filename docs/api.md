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

Each profile result additionally exposes `explanations` (English messages for the
actual decision) and `pair_diagnostics` (null for profiles without a pair rule;
otherwise status, present languages/frameworks and configured alternatives with
their missing symbols and messages). Existing fields and decisions are preserved.
These explanations are derived after `machine.accepts(sequence)` and do not decide
acceptance. See [field definitions and examples](profile-explanations.md).

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
`render_candidate_html(dsl_source)` always parses before rendering and recomputes
the four profile explanations from the validated candidate skills. `save_bundle(result,
destination, force=False)` verifies consistency before preparing four UTF-8 files;
it rejects existing outputs by default. Disk exports preserve original copies and
restore prior files after controlled publication failures. If restoration is
incomplete, `resumelens.workflow.BundleRecoveryError` (an `OSError` subclass)
provides `recovery_directory` and `rollback_errors`; backups remain available and
the CLI returns exit code 2. A cleanup-only failure issues a `RuntimeWarning`
without replacing the publication outcome. See [complete workflow](complete-workflow.md)
and [recovery](bundle-recovery.md) for fields, errors and practical limits. The
original TXT-to-JSON CLI is unchanged.

## Contract changes

The Machine Learning learning-library group accepts Scikit-learn, TensorFlow or
PyTorch. This changes recognition outcomes for qualifying Scikit-learn-only
inputs without changing JSON schemas or function signatures. Previously saved
DSLs that omit a newly accepted profile must be regenerated to satisfy current
semantic validation. See [profile alignment](profile-alignment.md).

The local UI exposes a separate HTTP adapter documented in [local-ui.md](local-ui.md).
`resumelens.web.process_web_request({"text": text, "name": name})` validates request
types/sizes and returns `result`, four text `downloads` and base64 `bundle_zip`.
It reuses the complete API and bundle consistency checks. No existing API or JSON
schema is changed. `create_server(port)` serves fixed packaged assets and
`POST /api/process` on loopback; these adapter functions are not re-exported from
the first-stage package API.

Changing a symbol affects the catalog, FSTs, schema enum and profile configuration. Incompatible changes require a new version. Added aliases must remain unique after casefold; regenerate formalizations and regex documentation, then run tests.
