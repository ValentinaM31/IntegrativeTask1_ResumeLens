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

Automated tests are in `tests/`. Annotated evaluation separates admitted cases and stress limits; see `test-results.md` and `evaluation.md`.
