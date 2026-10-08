# Processing API

`process_resume(text, name=None)` returns a fresh contract 1.0 object. It can be consumed by another component or the CLI without profile models or textX.

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

`ValueError` reports empty input or semantic inconsistency. File/encoding errors are reported by the CLI. Unknown terms are recorded only when passed to the normalizer; extraction does not discover arbitrary technologies. Program diagnostics are in English.

## Contract changes

Changing a symbol affects the catalog, FSTs, schema enum and profile configuration. Incompatible changes require a new version. Added aliases must remain unique after casefold; regenerate formalizations and regex documentation, then run tests.
