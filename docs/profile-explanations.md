# Explaining profile requirements

Recognition still calls the real epsilon-NFA's `accepts(sequence)` method to
decide each profile. The diagnostic layer describes the configured requirements
after that decision; it does not infer skills, score proficiency or replace the
automaton. The four profile patterns and their exported machines are unchanged.

## Additional classification fields

All previous fields retain their meaning. Each profile adds:

| Field | Meaning |
|---|---|
| `explanations` | English messages describing the actual acceptance or missing requirements |
| `pair_diagnostics` | Null without a compatible-pair rule; otherwise the structured diagnostics below |
| `pair_diagnostics.status` | `matched`, `incompatible`, `missing_language`, `missing_framework` or `missing_both` |
| `languages_present` / `frameworks_present` | Sorted canonical symbols present in the profile's configured pair buckets |
| `alternatives` | One option per configured pair, in configuration order |
| `alternatives[].pair` | Two canonical symbols identifying that language/framework alternative |
| `alternatives[].missing` | Symbols absent from that pair, preserving pair order; empty when complete |
| `alternatives[].message` | Readable present/missing message for that alternative |

Readable skill names come from each catalog entry's first alias. Group and pair
alternatives come from the profile configuration, rather than a separate list in
JavaScript or the renderer. Canonical JSON fields continue using the existing
symbols. Messages describe recognized qualifications, not proof of expertise.

One complete pair is enough. Other incomplete alternatives do not reject a
candidate. A `matched` pair does not guarantee acceptance: the database, REST API
and Git groups are also mandatory for the current Backend pattern. Missing groups
are explained separately. Optional or unrelated skills cannot fill those groups.

## Java and Django example

```text
Name: Ana
Skills: Java, Django, SQL, REST API, Git
```

Backend remains rejected. Both the language and framework buckets contain a
recognized symbol, but the pair is incompatible. Its explanation is:

> Languages found: Java. Frameworks found: Django. These do not form an admitted language/framework pair.

The available alternatives explain exactly what is missing:

| Configured pair | Missing from this candidate |
|---|---|
| Java + Spring Boot | Spring Boot |
| Python + Django | Python |
| JavaScript + Node.js | JavaScript and Node.js |
| TypeScript + Node.js | TypeScript and Node.js |

Adding Spring Boot or Python completes one valid pair. The other required groups
are already present in this example, so Backend becomes accepted. Without SQL or
another permitted database qualification, it remains rejected for that group.

For the other profiles, missing alternatives are also named explicitly: for
example, `Missing one of: React or Angular or Vue.` for Full Stack, or
`Missing one of: TensorFlow or PyTorch.` for Machine Learning. Scikit-learn remains optional
under the current configuration; this extension does not change the profile rules.

## UI, standalone report and exports

The local UI displays `explanations` using text nodes and shows the configured
pair alternatives when a pair is missing. It has no independent acceptance rule.
The standalone HTML adds a **Qualification checks** section with all four
decisions. It parses the DSL first, then recomputes the same classification from
the parsed skills and escapes the explanation text. It accepts no raw candidate
dictionary or unvalidated classification as a rendering shortcut.

`classification.json`, individually downloaded files and ZIP exports include the
additional fields. Existing bundle validation recomputes the full classification;
altering an explanation therefore blocks export before writing. First-stage JSON
1.0, evidence offsets, normalization, grammar and accepted-profile declarations
retain their existing formats. Stored classification/HTML fixtures were regenerated
for all eight samples; their earlier classification fields and decisions are identical.

## Verification

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_profile_explanations.py -v
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/check_workflow_acceptance.py
.\.venv\Scripts\python.exe tools/check_web_acceptance.py
```

Seventeen new tests cover the four profiles, five pair statuses, multiple matches,
optional qualifications, configuration-derived alternatives and fresh results.
Ninety-six Backend pair/remaining-group combinations verify unchanged decisions.
Additional checks exercise an actual workflow CLI outside the repository, BOM/CRLF,
real HTTP and every ZIP file, validated HTML and rejection of mutated explanations.
These are behavioral regressions, not an independent candidate-accuracy evaluation.

For a manual browser replay, process the Java/Django example, read its Backend
card and download the classification/HTML. Then add Spring Boot and process again.
Backend must be accepted without requiring all four pair alternatives. See
[current verification results](test-results.md) and the [UI checklist](local-ui.md).
