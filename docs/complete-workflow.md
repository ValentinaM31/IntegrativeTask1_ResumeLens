# Complete processing and HTML reports

This increment connects the existing components into one executable workflow:

UTF-8 TXT → `re` extraction → real pyformlang FST translations → JSON 1.0 validation
→ four complete DFA recognizers → candidate DSL → textX syntax and semantic validation
→ standalone HTML report.

The original `process_resume()` API and `python -m resumelens` TXT-to-JSON command
retain their existing behavior. HTML reports represent validated candidate data;
the local browser interface added in the fourth increment consumes this same
workflow. See [local-ui.md](local-ui.md) for interactive input and downloads.

## Run from PowerShell

Install the current editable package to refresh the new console entry point:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m resumelens.workflow_cli data/samples/01_full_stack.txt -o outputs/alex_bundle
Start-Process outputs/alex_bundle/candidate.html
```

After installation, the equivalent script is:

```powershell
.\.venv\Scripts\resumelens-workflow.exe data/samples/01_full_stack.txt -o outputs/alex_bundle
```

On Linux, use `.venv/bin/python` and `.venv/bin/resumelens-workflow`. The command
requires a `.txt` input and an output directory. Add `--name Ana` for a missing
explicit name; an explicit input name still takes precedence. Add `--force` only
when intentionally replacing existing bundle files.

Output directories are created as needed. Successful execution returns exit code 0
and prints accepted profiles and the bundle directory. File, encoding, empty-input,
DSL-validation and overwrite failures return exit code 2 with an English diagnostic.
The original CLI continues to generate one JSON file rather than a bundle.

## Saved bundle

| File | Content and origin |
|---|---|
| `first_stage.json` | Unchanged schema-version 1.0 candidate information, canonical skills, evidence spans, exclusions and warnings |
| `classification.json` | Four executed profile results, sequences, accepted profiles and rejection explanations |
| `candidate.rl` | Generated candidate-language source with contacts, education, experience, canonical skills and accepted profiles |
| `candidate.html` | Candidate report produced only from a successfully textX-validated specification |

All four files use UTF-8 and LF output line endings. Input is decoded with
`encoding="utf-8-sig", newline=""`, preserving CRLF while removing the BOM.
Evidence positions therefore retain the same interpretation as the original API.
The saved bundle does not contain the full original resume text; retain that text
separately when displaying evidence or verifying original spans later.

## Public API

```python
from resumelens import process_complete_resume, save_bundle, render_candidate_html

with open("resume.txt", encoding="utf-8-sig", newline="") as stream:
    text = stream.read()

result = process_complete_resume(text, name=None)
save_bundle(result, "outputs/candidate")
assert render_candidate_html(result["dsl"]) == result["html"]
```

`process_complete_resume(text, name=None)` returns a fresh dictionary:

| Key | Meaning |
|---|---|
| `pipeline_version` | `"1.0"`, the composed-result format, independent of package version 1.4.0 |
| `source_text` | Exact decoded input retained in memory for evidence validation; omitted from saved bundle files |
| `first_stage` | Original validated JSON 1.0 object |
| `classification` | Result of `classify_skills(first_stage["normalized_skills"])` |
| `dsl` | Generated candidate-language source |
| `validated_candidate` | Candidate dictionary reconstructed by `parse_candidate_dsl(dsl)` |
| `html` | Standalone report from `render_candidate_html(dsl)` |

First-stage validation uses the exact input text. Profile recognition still executes
actual automata. DSL parsing rejects syntax errors, duplicates and invented/omitted
accepted profiles. `render_candidate_html(dsl_source)` is independently callable and
always parses and validates its argument before returning HTML; it cannot bypass
textX by accepting an arbitrary candidate dictionary.

The standalone HTML now includes four qualification checks as well as accepted
profiles. Its explanations and compatible-pair alternatives are recomputed from
the parsed DSL skills through the same recognition API used by the web cards.
Classification JSON adds `explanations` and `pair_diagnostics`; all earlier fields,
first-stage JSON 1.0, candidate grammar and profile decisions remain compatible.
See [diagnostics and examples](profile-explanations.md).

`save_bundle(result, destination, force=False)` returns the destination Path. Before
creating any output, it verifies pipeline version, first-stage schema and evidence against `source_text`, actual FST translations,
recognition results, generated DSL, parsed candidate and HTML consistency. It expects
an unmodified result from the processing API, rather than an independently edited
collection of outputs. The result must retain its `source_text`; missing source text or altered evidence
blocks saving before any destination is created. The four exported file formats
remain unchanged.

## Report behavior

The HTML shows a candidate name, accepted professional profiles, normalized
qualifications, contact information, education and experience. Multiple records and
multiple accepted profiles remain visible. Missing data has explicit empty-state
messages, including a missing name and no accepted profile.

Canonical identifiers are displayed with underscores replaced by spaces; the JSON
and DSL retain exact identifiers. All candidate-derived text is escaped using
`html.escape`, including the title and name. Contact links are displayed as text.
There are no scripts, external stylesheets, remote fonts or remote resources.
The report can be opened directly from disk, has a responsive layout and includes
print styling.

The report summarizes qualifications declared in the input and the team's documented
profile patterns. It does not infer proficiency, rank people or establish that
education and experience claims are true. Extraction/catalog limitations remain in
[evaluation.md](evaluation.md).

## Output protection and practical limits

The saver checks all four target filenames before starting writes. Any existing
target blocks the complete save unless `force=True`; a directory or symbolic link
at a target filename is rejected even with force. Unrelated files in the destination
remain intact. The CLI also protects input aliases, including existing hard links,
from being overwritten by a bundle output.

Validation and deterministic target conflicts happen before writing. The saver
then exclusively creates `.resumelens-export.lock` inside the destination,
prepares all four outputs there and copies every existing original before touching
final reports. Cooperating exporters cannot write to the same destination while
that workspace exists. Previously absent filenames are reserved with exclusive
creation before replacing individual outputs.

If a controlled publication failure occurs, touched originals are restored from
their backups and newly created reports are removed. If restoration itself fails,
`BundleRecoveryError` reports the retained backup directory; further exports are
blocked until recovery and cleanup. A cleanup-only failure warns and preserves the
actual success/error outcome. See [recovery instructions](bundle-recovery.md).

Individual replacements do not form an atomic or crash-durable four-file
transaction. Readers can observe intermediate generations or empty reserved
files. Abrupt process termination or power loss requires inspection, and unrelated
programs editing the destination do not honor this coordination mechanism.

## Reproduction and coverage

```powershell
.\.venv\Scripts\python.exe tools/generate_workflow_examples.py
.\.venv\Scripts\python.exe tools/check_workflow_acceptance.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

`data/workflow/` contains eight complete bundles and an executed validation summary.
Their first-stage JSON, classifications and DSL agree with the earlier examples.
Stored synthetic bundles are defined against LF-normalized sample input. Their
generator and fixture-comparison test use universal-newline reads so Windows CRLF
checkouts reproduce the same stored offsets. This applies only to these fixtures:
the production API/CLI preserves original input text. The comparison test also
processes CRLF variants, validates their exact evidence spans and shifted offsets,
and verifies that classification, DSL and HTML remain identical.
The acceptance tool executes the real CLI from another working directory for all
eight samples and compares all four output files with the public API.
This workflow increment added 22 tests to the previous 67. With the fourth
increment's 20 local HTTP/entry tests, that suite contained 109 tests. Subsequent
evidence-validation checks added two workflow tests; fourteen focused negation
regressions brought that total to 125. Seventeen profile-explanation tests and
three rejected-POST transport regressions brought that total to 145. Fifteen
bundle-recovery tests brought that total to 160. Eight profile-alignment tests brought
that total to 168, including LF/CRLF CLI and real HTTP/ZIP checks for the
Scikit-learn alternative. Thirteen evaluation-protocol/scoring tests brought that
historical total to 181. Later workflow-evaluator and Windows-lock regressions are
recorded with current complete-suite results in [verification results](test-results.md).
The separate [preannotated dataset](preannotated-evaluation.md)
compares all stages against fixed labels while retaining observed interpretation
errors. See [current results](test-results.md)
and [negation behavior](negation-handling.md).
Coverage includes HTML escaping, repeated records, three simultaneous profiles,
invalid DSL, mutated outputs, overwrite preflight, force behavior, input aliases,
BOM/CRLF, Unicode and execution outside the repository.

Symlink/hard-link checks run where the filesystem and permissions permit creating
those links; the corresponding tests otherwise report a skip. Historical workflow
verification used Linux with Python 3.12.14. A Windows run exposed a fixture LF/CRLF
offset mismatch, reproduced and corrected using a CRLF checkout on Linux. A
subsequent reported Windows run of the corrected 89-test suite passed with one
symlink-permission skip. Later Windows complete-suite and automated/manual browser checks,
with their precise scope, are in [verification results](test-results.md). Text
fixture reads explicitly use UTF-8, including the earlier recognition correction.

## Sources consulted

- Python [html.escape](https://docs.python.org/3/library/html.html) for safe text presentation.
- Python [pathlib](https://docs.python.org/3/library/pathlib.html) and
  [file opening](https://docs.python.org/3/library/functions.html#open) for output
  paths, exclusive creation and explicit text encoding.
- The existing [candidate-language specification](candidate-language.md) and official
  textX documentation govern parsing; HTML is subsequent to that validation.
