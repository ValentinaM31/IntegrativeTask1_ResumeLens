# Test scenarios

| Component | Scenario | Expected behavior |
|---|---|---|
| Candidate | Explicit, absent or supplied name | String/null without arbitrary inference |
| Contact | Multiple emails, mobile numbers and links | Lists and correct offsets |
| Contact | Malformed email, years and foreign prefix | Rejected formats produce no match |
| Records | Education/experience sections | Line evidence without contained duplicates |
| Education | Scrum Master and verb master | No academic degree inference |
| Skills | Every alias and capitalization | Original evidence and expected symbol |
| Boundaries | JavaScript, GitHub, literal dots | No subword or arbitrary punctuation match |
| Context | JS/TS in lists/prose; React framework/verb | Explicit supported context only |
| Pandas | Technical usage and animals | Technical positives retained, animals excluded |
| Negation | Supported phrases, lists and contrast | Reasoned exclusions, later positives retained |
| Negation knowledge | do not know, don't/don’t know/use, no sé/se/conozco, tabs and case | Negated mentions excluded even inside skills headings |
| Negation lists | nor/ni and a comma before a conjunction; dotted aliases | All directly coordinated known aliases excluded with exact spans |
| Negation scope | Punctuation, contrast, line breaks, new predicates and repeated positive mentions | Other positive skills survive; later positive repetitions normalize normally |
| React predicates | I know/use React versus I know how to react to changes | Immediate technical predicate accepted; ordinary verb excluded |
| Negation workflow | JS, NodeJS, Postgres and Git plus negated React | Full Stack rejected until a positive React/Angular mention is present |
| Negation integration | BOM/CRLF file through both real CLIs and actual HTTP/ZIP | API, classification, parsed DSL, HTML and downloads agree |
| FST | Unknown input, prefix and suffix | No valid translation |
| Catalog | Conflicting alias | Explicit error |
| Integration | Repeated/reordered variants | Unique symbols, retained evidence links |
| Contract | Corrupted fields/indices | Inconsistent output rejected |
| CLI | TXT, BOM, CRLF, existing output | Valid JSON and overwrite protection |
| Language | English CLI/results and examples | English prose; bilingual input compatibility retained |
| Stress | Unknown technology and double negation | Failures reported as limitations |
| Recognition | All Full Stack alternative combinations | Accepted with every group; rejected after removing a group |
| Recognition | ML/Data library, engine, database and pipeline alternatives | Documented alternatives accepted; missing groups rejected |
| Assignment alignment | Three ML library alternatives and two reference databases | All 12 minimal diagram paths accepted by the actual automaton; missing buckets/bad order rejected |
| Scikit-learn integration | Three aliases, simultaneous profiles, model-only/negated library cases | Correct normalization, accepted/rejected DSL claims and visible report decisions |
| Alignment adapters | BOM with explicit LF/CRLF through real CLI; actual HTTP and ZIP | Each of three targeted fixtures agrees with the API across all four payloads |
| Backend | Every single language/framework combination | Only four compatible pairs accepted with remaining requirements |
| Backend explanations | Incompatible pair, missing language, missing framework or neither | Distinct diagnostic and every configured pair's missing symbols |
| Profile explanations | Required groups versus optional skills, valid pair with missing database | Exact missing alternatives; no optional substitution or false incompatibility |
| Diagnostic authority | Configured alternatives, fresh results and automaton rejection | Messages follow configuration and actual NFA decision; mutations do not leak |
| Explanation integration | CLI, real HTTP/ZIP, standalone HTML and tampered messages | Shared explanations survive downloads; inconsistent exports rejected |
| Backend | Multiple languages/frameworks including one valid pair | Accepted without preselecting a pair in ordering |
| Recognition | Order permutations, repeated symbols and extra skills | Stable results; optional/unrelated symbols do not cause rejection |
| Recognition | Empty/invalid input or overlapping configuration buckets | Empty skills reject all; invalid inputs/configurations raise errors |
| Models | Exported complete transition relation | Reconstructed machine matches executable relation |
| Recognition integration | Eight existing sample expectations | All classifications match; three simultaneous profiles in sample 08 |

| DSL structure | Required fixed-order sections, empty lists and whole-input parsing | Valid documents accepted; missing/reordered sections and trailing text rejected |
| DSL strings | Null name, Unicode, quotes, backslashes and controls | Exact round trip for valid JSON-style strings; malformed strings rejected |
| DSL vocabulary | All 26 canonical skills and four profile names | Exact case-sensitive tokens; unknown symbols and prefix extensions rejected |
| DSL semantics | Repeated skill/profile declarations and incompatible profiles | Duplicates, omitted accepted profiles and invented profiles rejected |
| DSL integration | Eight existing resumes, repeated records and three profiles | Generated DSL parses to expected candidate data |
| Packaging | Grammar resource available outside the repository | Installed wheel builds its textX metamodel independently of cwd |

| Workflow | Eight sample inputs through all stages | First-stage/classification/DSL unchanged; stored bundles match actual execution |
| Rendering | Names, records, contacts, empty data and multiple profiles | Complete standalone report with escaped candidate text |
| Rendering gate | Invalid syntax or inconsistent accepted profiles | No HTML result |
| Saving | Modified result, existing targets, target directories and symlinks | Errors before writes for deterministic validation/path conflicts |
| Saving | Force overwrite and unrelated destination files | Replace only the four named bundle files |
| Export preparation | Partial writes, flush, backup and recovery-record failures | Existing reports remain byte-identical before publication |
| Export recovery | All 16 original-presence combinations; failure at each of four replacements | Restore original bytes/timestamps and remove only newly created reports |
| Export coordination | Competing exporter, existing workspace and late no-force collision | Reject collision; preserve workspace owner and unrelated files |
| Export diagnostics | Failed rollback, cleanup failure, caught interruption and CLI retry | Retain complete backups when needed; preserve error outcome and recover/retry |
| Workflow CLI | BOM/CRLF, Unicode, fallback name, invalid files, input aliases | Consistent evidence; code 0/2; no input overwrite |
| Execution | Installed module from a different cwd | Complete output bundle without cwd-dependent resources |

Automated tests are in `tests/`. Annotated evaluation separates admitted cases and stress limits; see `test-results.md` and `evaluation.md`.

## Local UI and HTTP scenarios

| Component | Scenario | Expected behavior |
|---|---|---|
| Local HTTP | Eight samples and simultaneous candidate requests | Exact public API results; candidates remain independent |
| Downloads | In-memory ZIP versus saved CLI bundle | Exactly four UTF-8 files with identical bytes |
| Input | BOM, CRLF, Unicode/emoji and optional name | Original decoded spans; explicit name takes precedence |
| Errors | Wrong types, fields, JSON, encoding, size, content type or length | English JSON error with no result or download |
| Validation | Invalid generated DSL or unexpected processing failure | No HTML/download; no traceback or input content exposed |
| Routes | Unknown/traversal paths and external Host/Origin | Rejected without exposing repository files |
| Entry point | Occupied/invalid port, browser options and Ctrl+C | Diagnostic or clean stop; resources available outside cwd |
| Browser | Paste/upload, edits, repeated processing, example and clear | Current input/results only; no stale downloads |
| Browser | Four decisions, reasons, sandboxed report and untrusted text | Actual profile outcomes; text escaped; no active injected elements |
| Browser | Downloads, narrow viewport and connection failure | Matching ZIP/files, responsive layout and recoverable controls |

The 23 HTTP/entry tests use only installed runtime dependencies. The real-browser
interaction check is separate QA; reproduce it manually using [local-ui.md](local-ui.md).

### Rejected POST connection regressions

Verify a full JSON 403 response before a delayed UTF-8 body arrives, then clean
connection closure after its bytes are discarded. Verify a missing body cannot
hold cleanup indefinitely, and absent/invalid/duplicate/oversized/chunked framing
is not awaited. All rejected requests must bypass candidate processing. Keep
the actual external Host/Origin tests; do not skip connection failures.

## Keyboard and feedback interaction scenarios

Run `tools/check_ui_keyboard.py` with the optional Node.js/Playwright QA tools.
Its eighteen scenario groups exercise actual keyboard events in a browser engine:
input order, a complete keyboard-only workflow, file/example/process busy states,
focus destinations and focus preservation, field errors and recovery, native
details and scrolling, all five actual downloads, retry after network/server
errors, repeated live-region updates and narrow/high contrast layouts. Downloads
must match the real HTTP response byte for byte. See
[keyboard navigation](keyboard-navigation.md) for setup and a manual alternative.
These interaction checks are distinct from the 168 Python unittest cases and
from a screen-reader or full accessibility audit.
