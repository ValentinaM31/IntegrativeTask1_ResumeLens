# Verification results

## Assignment-profile alignment — 2026-10-11

Based on published `5b4a6a2` (disk export recovery, including the LF/CRLF test
correction). The user confirmed the preceding corrected suite passed on Windows.
Both uploaded assignment copies were read and the page 5 diagram visually checked:
Scikit-learn, TensorFlow and PyTorch label alternative transitions in one group.
Scikit-learn now fills that required group instead of remaining optional.

Verified on Linux with Python 3.12.14 and the unchanged locked dependencies. Native
Windows execution of this new extension is pending. The first-stage JSON 1.0,
public signatures, grammar, catalog and package version 1.4.0 remain unchanged;
the intentional change is the Machine Learning acceptance criterion. The separate
teacher specification for additional profiles was not available for verification.

| Check | Result |
|---|---|
| Full Python suite | 168 passed, including eight new alignment methods |
| Reference diagram paths | All 12 minimal combinations accepted by the real automaton and public classifier |
| Missing/bad order | Direct automaton rejects empty, reversed and each one-group-missing Scikit-learn sequence |
| Extended alternatives | Existing ML test covers 18 data/library/database combinations, including retained MySQL choice; removing each group rejects |
| Canonical preparation | All three learning libraries retained; duplicates collapse and group order remains canonical |
| Alias/overlap/DSL | All three Scikit-learn aliases normalize; Backend, Data Engineer and Machine Learning can qualify together; false/missing DSL profile claims reject |
| Negative evidence | Optional model/Docker and negated English/Spanish library mentions do not fill the learning-library group |
| Dedicated CLI acceptance | Three fixtures with UTF-8 BOM, LF and CRLF (six subprocess runs) agree with API bytes for all four files |
| Dedicated HTTP/ZIP | Three real requests agree with API and every individual/ZIP payload |
| Existing acceptance | Eight workflow API/CLI bundles and eight real HTTP/API/ZIP samples agree |
| Formal exports | ML JSON/CSV/DOT/SVG updated: 12 states, 10 symbols, 36 transition triples; executable/exported relations agree |
| Stored examples | Eight existing classifications/DSL/workflow examples regenerated; accepted-profile expectations unchanged; three targeted alignment bundles added |
| Design/dependencies | Catalog/profile/sample design validation and pip check pass |
| Fresh patch / CRLF checkout | Applies on `5b4a6a2`; all 168 tests also pass with CRLF fixtures; sixty changed files match after newline normalization |
| Targeted bundle reproducibility | All three regression bundles regenerate byte-identically |

These new examples deliberately exercise a confirmed mismatch and its boundaries;
they are regression evidence, not independent resume evaluation or general accuracy
claims. The previous eighteen actual browser groups are unchanged and are not
part of the 168 Python-test count. See [profile alignment](profile-alignment.md) for
reference provenance, retained team choices and saved-DSL compatibility.

Earlier results follow unchanged.

## Bundle recovery CLI fixture correction — 2026-10-11

The user ran the initial bundle-recovery extension on Windows: 160 tests, one
failure in `test_cli_reports_failure_preserves_reports_and_can_retry` and the
expected symlink-permission skip. The mismatch was a skill start position of 25
instead of the test's LF expectation of 24.

The test wrote its TXT through `Path.write_text` with default newline translation.
On Windows, LF becomes CRLF, while the production CLI correctly preserves that
decoded CRLF input. The expected bundle was generated from the original LF string.
The same 24/25 difference was reproduced on Linux by writing explicit CRLF bytes.
A checkout using CRLF fixtures alone did not expose this runtime text-write issue.

The corrected test writes exact UTF-8 bytes and runs both LF and CRLF subcases.
Each compares the CLI's four report files against the API processing that same
decoded input, after an injected export failure, verified restoration and retry.
The saver, CLI and evidence-position behavior are unchanged.

Verification on Linux with Python 3.12.14: all 15 recovery tests and the full
160-test suite pass with both newline subcases. Native Windows verification of
this correction remains pending. This correction belongs to the same disk export
commit and does not require a separate progression commit.

## Disk export protection and recovery — 2026-10-11

Based on published `2f6f9c7` (keyboard navigation and accessible feedback). This
extension changes only disk bundle saving and adds fifteen filesystem regression
tests plus recovery documentation. Processing, profiles, runtime dependencies,
package version 1.4.0 and the four output formats remain unchanged.

Verified on Linux with Python 3.12.14 and the existing locked dependencies. Native
Windows execution of this extension has not been performed in this environment;
run the commands in [bundle-recovery.md](bundle-recovery.md) after applying it.
Historical Windows confirmation below applies to preceding changes.

| Check | Result |
|---|---|
| Full Python suite | 160 passed, including 15 new bundle-recovery methods |
| Original-presence/publication failures | 64 subcases passed: each of four promotion failures across all 16 original-presence combinations; original bytes, timestamps and file presence restored |
| Successful replacement | All 16 original-presence combinations produce the exact four payloads and retain unrelated files and supported original mode bits |
| Preparation errors | Partial staged write, flush, backup and initial recovery-record errors leave final reports unchanged |
| Publication/interruption | Commit-record error and exceptions before/after replacement trigger recovery; caught KeyboardInterrupt restores reports |
| Coordination | Competing exporter is rejected without disturbing its owner; existing workspace and late no-force collision are preserved |
| Incomplete rollback | Explicit error retains all original byte copies; manual recovery is verified and a fresh export succeeds |
| Cleanup errors | RuntimeWarning preserves actual success/failure outcome; retained record identifies prepared or committed state |
| CLI failure and retry | Exit 2 restores old reports; subsequent real CLI export succeeds with exit 0 |
| Workflow acceptance | Eight real CLI/API sample bundles agree in all four files |
| Web acceptance | Eight real HTTP/API samples agree; all four ZIP entries verified |
| First-stage acceptance | Six real API/CLI scenarios agree |
| Design/dependencies | Catalog/profile/sample consistency and pip check pass |
| Fresh patch / CRLF checkout | Patch applies on `2f6f9c7`; all 160 tests also pass with CRLF fixtures; fourteen changed files match after newline normalization |
| Stored bundle regeneration | Eight bundles regenerated with no tracked fixture changes |

Faults are injected around actual filesystem writes, copies and replacements in
temporary directories. Original report fixtures deliberately contain non-UTF-8
bytes and CRLF. These subcases demonstrate controlled error recovery, not power
loss durability, simultaneous reader consistency or independent resume accuracy.
The eighteen browser groups documented below were verified for the preceding UI
commit; browser interaction code is unchanged in this extension.

Earlier results follow unchanged.

## Keyboard navigation and accessible feedback — 2026-10-11

Based on published `a9efc1e` (the profile explanations and rejected-POST correction
included). The user confirmed the preceding checks passed on their Windows setup.
This change updates the three packaged UI assets, adds optional browser QA scripts
and documents the focus/feedback behavior. Processing code, runtime dependencies,
JSON contracts, profile patterns, stored outputs and package version 1.4.0 are
unchanged.

Verified on Linux with Python 3.12.14 and the existing locked dependencies. Browser
interaction used Node.js 24.19.0, Playwright 1.62.1 and Chrome Headless Shell
151.0.7922.34. An isolated wheel installation was used to verify packaged resources
through the actual browser as well as the editable installation.

| Check | Result |
|---|---|
| Existing full Python suite | 145 passed; the browser groups are not included in this count |
| Keyboard browser acceptance | 18 scenario groups passed against the actual local server |
| Installed wheel/browser interaction | The same 18 groups passed using resources from site-packages |
| Entire keyboard-only journey | Skip, load example, name field, process, ZIP download, edit and clear succeed using keyboard navigation |
| Busy operations | File/example/process states disable inputs, expose busy feedback and keep a meaningful focus destination; duplicate submit is ignored |
| Focus after completion | Valid uploads/examples focus text; results focus the named heading; a user who tabs away during a request retains their focus |
| Errors and recovery | Empty/oversized text and invalid files associate an error with the input; failed example/network/server/unreadable-response cases restore controls and a keyboard return path |
| Downloads and details | All five Enter-activated downloads match the actual response bytes; native Enter/Space panels and arrow-key text scrolling work |
| Feedback semantics | Stable status/alert regions, repeated errors, input error cleanup and stale output invalidation verified in the DOM |
| Layout/focus | 390px layout, reduced-motion preference and forced-colors focus checked; mobile screenshot inspected without horizontal overflow |
| Existing acceptance | Eight real HTTP/API samples and all four ZIP entries agree; eight workflow API/CLI bundles agree |
| Design/dependencies/syntax | Design validation, pip check and both JavaScript syntax checks pass |

The eighteen groups are actual browser interactions, not HTML-attribute checks
alone, independent resume evaluation, or a certification of accessibility. They
include controlled delays/failures and a separate full workflow with no mouse or
programmatic focus setup. Spoken announcements with a screen reader and native
Windows keyboard/browser behavior still require local verification. Installation
and manual reproduction are in [keyboard-navigation.md](keyboard-navigation.md).

Earlier results follow unchanged.

## Rejected POST connection correction — 2026-10-11

The user ran the initial profile-explanation extension on Windows with Python
3.14: 142 tests, one connection error in
`test_external_origin_and_host_are_rejected`, and one expected symlink-permission
skip. The error was `ConnectionAbortedError: [WinError 10053]` while receiving the
403 response. It is a transport failure, not a failed profile explanation.

Review found that early POST rejection sent its response and closed while the
request body remained unread. Premature TCP closure can prevent an HTTP response
from reaching its client (RFC 9112 section 9.6). This is a plausible explanation
for the reported failure, not a native Windows reproduction or proof of its
precise OS cause.

The correction flushes the error response first, then discards a clearly framed
body of at most 512 KiB with a one-second total deadline. It never parses or
processes rejected content. Invalid, absent, duplicate, oversized or chunked
framing is not awaited. Cleanup timeout/disconnect does not send a second error.
Ordinary processing and the original Host/Origin rejection remain unchanged.

Verified on Linux with Python 3.12.14 and the existing pinned dependencies:

| Check | Result |
|---|---|
| Complete suite after the transport correction | 145 passed, including 23 HTTP/entry tests |
| Regression against the original HTTP handler | The new delayed-body test fails on its premature close |
| Delayed UTF-8 POST / Expect header | Full 403 received before sending body; clean close after body arrives; no processing |
| Missing or ambiguous rejected body | Cleanup is bounded; invalid or oversized framing is not awaited |
| External Host/Origin with short and larger Unicode bodies | 403 JSON responses; candidate processing never invoked |
| Existing HTTP and complete-workflow acceptance | Eight samples agree with API; all four ZIP/output files verified |
| Dependency check | No broken requirements |

Native Windows/Python 3.14 verification of this correction is still required.
Run the complete suite and both acceptance tools before publishing. The Windows
symlink-permission skip remains expected; a connection error must not be skipped.
The initial 142-test checks below describe the extension before this correction.

## Profile-requirement explanations — 2026-10-10

Based on published commit `11c1d8c`, whose unchanged baseline passed 125 tests on
Linux. The user also reported that baseline passing on Windows with one skipped
test, and both existing CLI and HTTP acceptance checks succeeding. This extension
adds explanations for all four profiles and structured Backend pair diagnostics;
the NFA patterns, original classification fields, first-stage JSON and DSL are
unchanged. Windows execution of this new extension remains to be checked locally.

Verified on Linux, Python 3.12.14, with unchanged pyformlang 1.0.11, jsonschema
4.26.0 and textX 4.4.0 dependencies. Package version remains 1.4.0.

| Check | Result |
|---|---|
| Full editable-install suite | 142 passed: 125 existing plus 17 explanation tests |
| Fresh pinned environment with installed wheel | 142 passed; `pip check` reports no conflicts |
| New explanation tests | Five Backend statuses, four profiles, multiple pairs, optional skills, fresh results, configured alternatives and actual NFA authority |
| Pair/remaining-group combinations | 96 Backend combinations retain their expected accept/reject decisions |
| Existing eight classification outputs | Every original field is identical to the baseline after excluding the two new diagnostic fields |
| Stored examples | Eight classification outputs and eight workflow classification/HTML outputs regenerated; repeat generation produces identical files |
| API/CLI/HTTP acceptance | Six first-stage scenarios, eight complete workflow samples and eight HTTP/ZIP samples agree |
| New CLI/export integration | Actual CLI outside the repository, BOM/CRLF, all four outputs, real HTTP/ZIP and HTML messages verified; changed explanations block export |
| Isolated installed wheel outside the repository | New fields, rejection and standalone HTML execute successfully |
| Design and JavaScript checks | `validate_design.py`, dependency check and `node --check` succeed |
| Browser interaction | Ten explanation scenarios passed in Chrome Headless Shell 151.0.7922.34 using Playwright 1.62.1 |
| Browser downloads | Classification JSON, standalone HTML and ZIP downloaded through the actual UI match their response content byte for byte |
| Layout inspection | Desktop and 390px-width profile cards visually inspected; no horizontal page overflow or JavaScript page exceptions |

Browser scenarios cover incompatible Java/Django, missing language/framework/both,
a valid pair with a missing database group, multiple accepted pairs, missing groups
for Full Stack/ML/Data, and accepted Full Stack. Each visible card and standalone
report message was compared with its shared API explanation. These checks exercise
the added explanations; they are not a complete accessibility audit or tests on a
physical mobile device. The browser tooling is confined to the temporary QA
environment and is not a project dependency.

The seventeen tests include ninety-six pair/group subcases, not a new independent
evaluation dataset. Explanations remain limited to the configured finite patterns
and recognized canonical skills; they cannot verify proficiency or recover omitted
skills. Earlier verification follows unchanged.

## Explicit skill-negation correction — 2026-10-10

Based on `9d0b5f1` (the existing evidence-validation and CI updates included),
the unchanged baseline passed 111 tests. New regression cases reproduced the
incorrect Full Stack acceptance caused by `I do not know React` inside a skills
line, the missing positive `I know React`, and unsupported knowledge/list forms.
The correction extends explicit phrases and list coordination, and adds a narrow
immediate knowledge/use context for React. Negation is checked before context.

Verified on Linux with Python 3.12.14 and the unchanged pinned dependencies:
pyformlang 1.0.11, jsonschema 4.26.0 and textX 4.4.0. Package version stays 1.4.0;
JSON and pipeline versions stay 1.0. Windows execution of this correction must be
checked locally before publication; historical Windows checks below remain valid
for the versions they describe.

| Check | Result |
|---|---|
| Full editable-install suite | 125 passed: 111 existing plus 14 focused negation tests |
| Fresh pinned environment with installed wheel | 125 passed; no dependency conflicts |
| New extraction regressions | English/Spanish knowledge/use negation, straight/curly apostrophes, inability forms, tabs/case, list conjunctions, repeated positives, ordinary react verb, Pandas context and Unicode/CRLF spans |
| New complete-workflow regressions | False Full Stack acceptance corrected; positive React/Angular recovers acceptance through the existing automaton and validated DSL |
| Real CLI and HTTP regressions | BOM/CRLF file agrees with API through both CLIs outside the repository; actual HTTP decision and all four ZIP contents agree |
| Existing acceptance tools | Six extraction scenarios, eight complete CLI/API bundles and eight HTTP/API bundles remain consistent |
| `python tools/validate_design.py` | Catalog, profiles, schema example and eight expectations remain consistent |
| `python tools/document_regex.py` | Documentation regenerated from actual patterns; a repeat run produces identical content |
| `python tools/evaluate.py` | Existing 23-case synthetic results unchanged: 25 supported and 14 historical-reserved true positives; two stress omissions remain |
| Installed wheel with isolated Python outside the repository | Negation, positive recovery and packaged resources execute successfully |

The fourteen tests contain phrase/list/scope subcases rather than fourteen new
independent evaluation examples. They do not establish accuracy on real resumes.
Other negative phrases, unknown aliases in lists, double negation and irony remain
documented limits. No browser-engine interaction was added in this correction;
HTTP/ZIP behavior was tested and a manual UI replay is documented in
[negation-handling.md](negation-handling.md). Earlier results follow unchanged.

## Local browser interface increment — 2026-10-09

Verified package 1.4.0 on Linux with Python 3.12.14 and the unchanged pinned
dependencies. The preceding corrected 89-test suite was also reported successful
by the user on Windows, with the symlink-permission test skipped. This new UI
increment has not yet been run on the user's Windows installation.

| Check | Result |
|---|---|
| Full suite in editable installation | 109 tests passed: previous 89 plus 20 HTTP/entry tests |
| Full suite in a fresh pinned environment with installed wheel | 109 tests passed |
| `python tools/check_web_acceptance.py` | All eight real HTTP/API results agree; all four files in each ZIP verified |
| Existing extraction and complete-workflow acceptance | Six extraction scenarios and eight workflow samples still agree with their CLIs |
| Wheel from outside the repository with isolated Python | Version 1.4.0, all four UI resources, processing API and `resumelens-ui` entry point verified |
| `python -m pip check` | No dependency conflicts in editable and wheel environments |
| `node --check src/resumelens/ui/app.js` | JavaScript syntax valid |
| Real browser interaction | 12 scenario groups passed using Chrome Headless Shell 153.0.8010.12 and Playwright 1.63.0 on Linux |
| Desktop and 390px mobile-width screenshots | Visually inspected; no horizontal overflow |

Browser checks covered initial assets, the packaged example, all eight uploaded
samples, four independent decisions, the sandboxed report, ZIP and four individual
downloads, exact BOM/CRLF/emoji offsets, pasted/edited text, fallback name, stale
result removal, invalid files, escaped injection, mobile layout, connection failure,
clearing the form and absence of page exceptions/external requests. ZIP contents
and individual downloads were compared byte for byte. Original file CRLF survives
the text area's LF display until the user edits; Python character offsets remain
unchanged.

The twenty new unittest cases exercise actual loopback HTTP connections, input
validation and request limits, fixed resources/routes, external Host/Origin
rejection, invalid DSL, download consistency, independent concurrent candidates,
port conflicts, browser options and clean shutdown. Processing is serialized
around cached models/parser, and no candidate files or request data are logged or
written by the server. ZIP output uses fixed filenames and timestamps.

Browser QA dependencies and downloaded Chrome were used only in the temporary
verification environment; they are not project dependencies. UI operation uses
the Python standard library and the existing processing dependencies. Windows UI,
macOS and other browser engines still require verification. A local 390px viewport
check is not a test on a physical mobile device. The final poster/presentation,
academic evidence and repository-history audit remain for the fifth increment.

Reproduce runtime checks and the manual browser checklist in [local-ui.md](local-ui.md).
Historical verification from the preceding increments follows.

## Complete-workflow increment — 2026-10-09

Verified on Linux, Python 3.12.14, using the existing pinned pyformlang 1.0.11,
jsonschema 4.26.0 and textX 4.4.0 dependencies. Package version is 1.3.0;
first-stage schema version and composed-result pipeline version remain 1.0.

| Check | Result |
|---|---|
| Full unittest suite in the editable environment | 89 tests passed: previous 67 plus 22 workflow/rendering/CLI tests |
| Full unittest suite in a second fresh environment with pinned dependencies and installed wheel | 89 tests passed |
| `python tools/generate_workflow_examples.py` | Eight complete bundles generated after DSL validation |
| `python tools/check_workflow_acceptance.py` | Real CLI and API agree in all four files for all eight samples; CLI runs from outside the repository |
| `python -m pip check` | No dependency conflicts in editable and pinned wheel environments |
| Installed wheel executed with isolated Python outside the repository | Version 1.3.0, grammar resource, four-stage API, bundle saving and console entry point verified |
| New workflow tests with cp1252 simulated as the default Path text-read encoding | All 22 passed; new fixture reads explicitly specify UTF-8 |
| Rendered HTML inspection | Full Stack, incomplete and multiple-profile examples rendered with WeasyPrint 70.0; incomplete and multiple-record layouts visually inspected |

The reports retain repeated contacts, education/experience records and multiple
accepted profiles. Candidate-derived text is escaped; syntax and semantic failures
prevent HTML generation. Saving checks consistency and all target paths before
writing. Tests cover overwrite rejection, force behavior, preservation of unrelated
files, input hard-link protection, BOM/CRLF, Unicode and malformed inputs.

Visual inspection used a separate QA renderer, not a browser engine. No new runtime
dependency is added. Real Windows execution, mobile browser layout and browser-engine
compatibility remain to be verified. A Windows run and its newline correction are
documented below. Output writes are not a filesystem transaction;
a mid-write operating-system failure can leave a partial bundle. The interactive
input UI, final project-wide documentation/presentation and Git-history requirements
remain outside this increment. Earlier verification is retained below.

### Windows newline correction before publishing this increment

The user ran all 89 tests on Windows. One fixture-comparison test failed in its
eight sample subcases; the symlink-permission test was skipped. The first-stage
JSON fixtures contain offsets for LF input, while the checkout samples contained
CRLF. Every preceding newline therefore shifted subsequent evidence positions.
Converting all eight samples to CRLF in an isolated Linux checkout reproduced
the same eight failures. Production processing correctly preserved those offsets.

Only the synthetic-fixture generator and comparison test now read samples with
universal-newline normalization to their documented LF input. The test additionally
processes CRLF variants, validates evidence against the exact input, checks the
expected offset shifts and compares classification, DSL and HTML with LF results.
The production API/CLI and raw-input acceptance check keep their original behavior.
The corrected 89-test suite and eight-sample acceptance check pass on Linux with
both LF and CRLF sample checkouts; regeneration produces the same stored bundles.
The user must rerun the corrected suite to verify their Windows installation.

## Candidate-language increment — 2026-10-09 UTC

Verified on Linux with Python 3.12.14, pyformlang 1.0.11, jsonschema 4.26.0,
textX 4.4.0 and Arpeggio 2.0.3. A second fresh environment installed the complete
`requirements-lock.txt` followed by the built wheel with `--no-deps`.

| Check | Result |
|---|---|
| `python -m unittest discover -s tests -q` | 67 passed: 39 original + 12 recognition + 16 DSL tests; verified in editable and wheel installations |
| `python tools/generate_dsl_examples.py` | Eight generated/parsed candidate examples accepted; five syntax and three semantic examples rejected |
| `python tools/check_acceptance.py` | Original API/CLI agree in six scenarios; JSON 1.0 evidence remains valid |
| `python tools/validate_design.py` | Catalog, profile criteria and existing sample expectations remain coherent |
| `python -m pip check` in the pinned wheel environment | No dependency conflicts |
| Version 1.2.0 wheel executed with isolated Python from outside the repository | Installed package and grammar resource confirmed; generation, textX parsing and Full Stack recognition passed |

The DSL tests cover string escaping, null/empty sections, repeated records and contacts,
canonical vocabulary, structural errors, duplicate declarations, profile coherence,
multiple accepted profiles, resource access and input immutability. The stored fixtures
are synthetic regression cases. New recognition/DSL behavior has not been executed on
Windows or macOS in this increment. HTML, a combined workflow CLI and UI remain pending.
The following sections preserve verification from earlier increments.

### Windows encoding correction before publishing this increment

A user run on Windows passed the 16 DSL tests and failed one recognition-model
comparison. That test read the UTF-8 automaton JSON using the system's default
encoding. Decoding the same file with cp1252 reproduced the failure on Linux:
the epsilon label became two incorrect characters, so reconstruction inserted
ordinary-symbol transitions in place of epsilon transitions. UTF-8 decoding
restored equality. Recognition tests now explicitly read all JSON fixtures as
UTF-8 and verify the epsilon label; the full transition-dictionary comparison
remains in place. This documents the reported failure and reproduced cause;
the corrected suite still requires execution on the user's Windows installation.

## Recognition increment — 2026-10-08

Verified on Linux, Python 3.12.14, pyformlang 1.0.11 and jsonschema 4.26.0 in a fresh
project environment. No textX or UI dependency is included in this increment.

| Check | Result |
|---|---|
| `python -m unittest discover -s tests -q` | 51 tests passed: 39 original + 12 recognition tests |
| `python tools/export_automata.py` | Four complete JSON/CSV/DOT/SVG epsilon-NFA exports |
| `python tools/classify_examples.py` | Eight executed classifications match existing design expectations |
| `python tools/check_acceptance.py` | Original API/CLI agree in six scenarios, with valid first-stage evidence |
| `python tools/validate_design.py` | Original catalog, profile criteria and eight expectations remain coherent |
| `python -m pip check` | No dependency conflicts in editable and wheel installations |
| Wheel installation in a second fresh environment, executed from outside the project | Version 1.1.0, packaged profiles, first-stage API and compatible-pair rejection verified |
| Four rendered automaton SVGs | Inspected for readable states, transitions, branch requirements and legends |

Recognition tests exercise all 72 minimal Full Stack combinations and missing-group
variants; 12 ML combinations; 9 Data combinations; all 12 single Backend pairs;
multiple-pair candidates; all 120 permutations of one Full Stack pattern; duplicates,
extra skills, invalid inputs, configuration checks and exported relation consistency.
These are deterministic synthetic/regression checks, not a real-resume accuracy estimate.

| Sample | Accepted profiles |
|---|---|
| 01_full_stack | Full Stack |
| 02_machine_learning | Machine Learning |
| 03_backend | Backend |
| 04_data_engineer | Data Engineer |
| 05_aliases_duplicates | Full Stack |
| 06_incomplete | None |
| 07_boundaries_negation | None |
| 08_multiple_records | Backend, Data Engineer, Machine Learning |

First-stage JSON 1.0 and the original CLI remained compatible in this recognition
increment. DSL, HTML and UI were not included in that increment. The sections below
retain the historical first-stage verification.

## Original first-stage verification

A fresh virtual environment was installed without global packages. Imports were verified inside it and consumption outside the project root was checked. Platform: Windows; Python 3.12.14, pyformlang 1.0.11, jsonschema 4.26.0. Tests use standard-library unittest. Other operating systems are unverified.

## Executed commands

| Command | Result |
|---|---|
| python -m venv NEW_PATH | Fresh environment created |
| python -m pip install -r requirements-lock.txt | Locked dependencies installed |
| python -m pip install --no-deps -e . | Local package installed |
| python -m unittest discover -s tests -v | 39 tests, OK |
| python -m pip check | No broken requirements found |
| python tools/check_acceptance.py | API/CLI equal in six scenarios; valid JSON/evidence |
| python tools/validate_design.py | 26 symbols, 56 aliases, four design patterns, eight coherent scenarios |
| python tools/generate_examples.py | Eight outputs regenerated |
| python tools/evaluate.py | 23 cases, metrics separated by group |
| python tools/document_regex.py | Exact patterns and supported scope generated |
| python tools/export_models.py | Four complete JSON/CSV/DOT/SVG machine exports regenerated |

Here python denotes the virtual-environment executable. PyPI supplied dependencies and the build backend was installed in isolation. No textX, UI or recognition models are needed.

## Verified behavior

- Multiple records, sections, absent/manual names and original assignment fragments.
- Unicode, BOM, CRLF, actual positions and no duplicate contained records.
- All 56 aliases under three capitalization variants, literal dots and JavaScript/GitHub boundaries.
- Contextual React, JS/TS and Pandas; animal exclusions without losing technical positives.
- Eight negation patterns, lists and contrast retaining later positive skills.
- Unknown variants, catalog conflicts and rejection of multiple canonical outputs.
- Four FST sizes, output alphabets, formal model exports and cached reuse.
- Corrupted schema version, offsets, indices and translations are rejected.
- Public API, CLI, nested output, --force and invalid-input errors.
- English diagnostics and regenerated English main examples; Spanish regression inputs remain supported.

The previous revision had 35 tests; three Pandas regressions raised the total to 38. A complete English-language regression brought that first-stage total to 39. Eight sample symbol expectations remain unchanged. Profile expectations in `expected_samples.json` remain design annotations; their executed recognition outputs now appear separately in `data/classification/`.

## Evaluation and limits

Fifteen admitted cases yield TP=25/FP=0/FN=0; six historical reserved cases yield TP=14/FP=0/FN=0. Two stress cases yield TP=0/FP=0/FN=2, with undefined precision. Reserved cases now serve as regression after extractor changes. Prior results and reclassification reasons are retained; see `evaluation.md`.

Complete FST exports were regenerated from the executable machines and their components checked by tests. Their visual layout and the existing partial poster were reviewed in an earlier revision. The poster has not been regenerated and retains earlier metrics, identified in its README. This historical first-stage verification did not cover profile automata. Current recognition, DSL, workflow and local UI results are recorded above.
