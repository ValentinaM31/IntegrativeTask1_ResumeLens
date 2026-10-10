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
| FST | Unknown input, prefix and suffix | No valid translation |
| Catalog | Conflicting alias | Explicit error |
| Integration | Repeated/reordered variants | Unique symbols, retained evidence links |
| Contract | Corrupted fields/indices | Inconsistent output rejected |
| CLI | TXT, BOM, CRLF, existing output | Valid JSON and overwrite protection |
| Language | English CLI/results and examples | English prose; bilingual input compatibility retained |
| Stress | Unknown technology and double negation | Failures reported as limitations |
| Recognition | All Full Stack alternative combinations | Accepted with every group; rejected after removing a group |
| Recognition | ML/Data library, engine, database and pipeline alternatives | Documented alternatives accepted; missing groups rejected |
| Backend | Every single language/framework combination | Only four compatible pairs accepted with remaining requirements |
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

The 20 HTTP/entry tests use only installed runtime dependencies. The real-browser
interaction check is separate QA; reproduce it manually using [local-ui.md](local-ui.md).
