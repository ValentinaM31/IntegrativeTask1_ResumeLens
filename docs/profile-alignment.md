# Profile requirements and assignment alignment

This review uses `Integrative-Task1-2026-2_CyED3.pdf` and its later uploaded copy
`Integrative-Task1-2026-2_CyED3(1).pdf`. Both have the same extracted seven-page
assignment text. Page 5 of the later copy was also visually inspected because its
automaton labels are not included in the plain-text extraction.

The main assignment names Full Stack Developer and Machine Learning Engineer and
asks the team to define one additional software-engineering profile and one
additional AI/data profile. Page 2 says detailed additional-profile requirements
will be provided separately. No such separate specification is included in this
review; the existing Backend Developer and Data Engineer choices are retained.
This does not claim confirmation of unseen teacher requirements.

## Confirmed mismatch and correction — 2026-10-11

The Machine Learning diagram on page 5 shows the same transition from q2 to q3
with alternatives `SCIKIT_LEARN`, `TENSORFLOW` and `PYTORCH`. Previously, the
configuration placed only the last two in the required learning-library group and
classified Scikit-learn as optional. Consequently, `PYTHON, PANDAS, SCIKIT_LEARN,
POSTGRESQL, GIT` was rejected even though it follows an illustrated accepted path.

Both `config/profiles_design.json` and the packaged
`src/resumelens/profiles_design.json` now admit all three as alternatives in that
one required group. Scikit-learn is removed from the optional list. Python,
Pandas/NumPy, an admitted relational database and Git remain required. ML-model
development and Docker remain informational extras; they cannot replace the
learning-library group. MongoDB alone does not satisfy the Machine Learning
database group.

## Reference criteria versus team choices

| Profile / criterion | Assignment evidence | Current implemented choice |
|---|---|---|
| Four profiles and shared pipeline | Pages 1-3 and 5 | Full Stack, Machine Learning, Backend and Data Engineer use the same extractor, FSTs, automaton builder, DSL and report workflow |
| Full Stack | Page 2 examples; pages 4-5 canonical sequence | JS/TS, React/Angular/Vue, Node/Django/Spring Boot, admitted SQL/NoSQL database and Git; REST API and Docker are optional |
| Machine Learning language/data | Page 2 list and page 5 diagram | Python and at least one of Pandas/NumPy |
| Machine Learning library | Page 5 parallel transition labels | At least one of Scikit-learn/TensorFlow/PyTorch; now matches the illustrated alternatives |
| Machine Learning database/version control | Page 5 SQL/PostgreSQL alternatives and Git edge | SQL or PostgreSQL, plus the retained team extension MySQL; Git required |
| Other illustrative ML qualifications | Page 2 mentions model development | ML model and Docker remain optional; not every example bullet is a mandatory conjunct |
| Backend, selected software profile | Team-defined profile; detailed separate specification unavailable | One admitted language/framework pair, admitted database, REST API and Git; Docker optional |
| Data Engineer, selected AI/data profile | Team-defined profile; detailed separate specification unavailable | Python, SQL/PostgreSQL/MySQL, ETL/Airflow/Apache Spark and Git; Docker/Pandas optional |

The Full Stack example on page 2 contains JS, React.js, NodeJS, Postgres and Git
without an explicit REST API symbol. It still passes the documented minimum
pattern. Backend's compatible pairs remain Java + Spring Boot, Python + Django,
JavaScript + Node.js or TypeScript + Node.js. MySQL and these extra profile
criteria are identified as team choices, not copied requirements from the page 5
Machine Learning diagram.

## Historical model used for the alignment correction — 2026-10-11

The alignment correction originally used an actual `pyformlang` epsilon-NFA. Its
five disjoint ordered buckets were Python; Pandas/NumPy; the three learning
libraries; SQL/PostgreSQL/MySQL; and Git. Canonical preparation retained every
present member in each bucket, sorted within the bucket and deduplicated
qualifications.

The assignment diagram illustrates minimal paths with one symbol per group. That
model also accepted multiple symbols within a bucket, so listing two libraries or
both Pandas and NumPy did not cause rejection. Its loops and before/seen states
implemented those choices. Decisions came from `EpsilonNFA.accepts()`;
explanations were computed afterward from the configuration.

The historical Machine Learning machine retained 12 states while its alphabet
increased from 9 to 10 symbols and its transition relation from 33 to 36 triples.
The added Scikit-learn symbol had a loop before its group's requirement, a
transition to the seen state, and a loop afterward. The alignment revision updated
the JSON, CSV, DOT, SVG and summary exports to that machine. These historical
counts describe the former epsilon-NFA, rather than the current DFA exports.

The extractor and FSTs already supported all three Scikit-learn aliases. Their
26-symbol/56-alias catalog, first-stage JSON contract, offsets and transducers are
unchanged by that correction. Classification diagnostics and standalone reports
for the existing eight samples were regenerated where missing-library alternatives
changed. Their accepted-profile expectations remained unchanged.

## Current deterministic representation

The current recognizer is a complete `pyformlang.finite_automaton.DeterministicFiniteAutomaton`
using the same five Machine Learning buckets and qualification criteria. Its
states are {q0, q1, q2, q3, q4, q5, q_dead}, q0 is initial and q5 is the sole
accepting state. Every state/alphabet-symbol pair has exactly one destination;
invalid ordered sequences reach the nonaccepting sink q_dead. There are no empty
transitions.

The Machine Learning DFA has 7 states, the same 10-symbol alphabet and 70
transitions, including sink transitions. The transition count is `|Q| × |Σ|`
because the function is total. Multiple qualifications from the current bucket
still loop before advancing to the next required bucket. Optional model/Docker
mentions do not replace a required library.

All four profile machines use the deterministic representation. Backend retains
compatible language/framework pairs through finite mask memory; its canonical
preparation does not choose a pair or change candidate evidence. The change in
representation preserves public results, configured criteria and expected
classification decisions. Complete current tuples and exact export links are in
[profile recognition](profile-recognition.md); executed checks are recorded
separately in [verification results](test-results.md).

## Regressions and compatibility

`data/profile-alignment/` adds three explicitly labelled rule regressions:

- Scikit-learn as the only learning library: Machine Learning accepted.
- Model development and Docker without an admitted learning library: rejected.
- Explicitly negated Scikit-learn: rejected; the excluded mention remains traceable.

Each has a TXT input, predefined expected canonical skills/profiles and four
generated report files. These known-rule fixtures are not a blind or independent
resume evaluation dataset and have no claimed general precision metric.

Eight new test methods cover the twelve minimal paths from the reference diagram,
actual machine rejection of missing/out-of-order buckets, all simultaneous library
members, three aliases and three simultaneous profiles, optional/negated cases,
textX semantic rejection, six BOM/LF/CRLF real CLI runs, actual HTTP processing and
ZIP/download byte agreement. Existing alternative tests also retain the MySQL
extension and TensorFlow/PyTorch regressions.

Signatures, file formats and JSON schemas are unchanged, but this is an intentional
acceptance-rule change: previously rejected Scikit-learn-only candidates with all
other requirements now qualify. A previously saved DSL that omits this newly
accepted profile can fail the semantic validator when parsed under the corrected
rules. Regenerate such specifications through the current pipeline rather than
weakening semantic validation. No schema or package-version migration is implied.

Restart any already running local UI server after applying the updated
configuration, because the profile automata are cached within each process.
Use Ctrl+C in its terminal and launch `python -m resumelens.web` again.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_profile_alignment.py -v
.\.venv\Scripts\python.exe tools/generate_profile_alignment_examples.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/check_workflow_acceptance.py
.\.venv\Scripts\python.exe tools/check_web_acceptance.py
```

Current complete-suite counts and recorded Windows/Linux runs are in
[verification results](test-results.md). The eighteen automated browser interaction
groups have recorded Linux and Windows runs, separate from the Python suite and
manual visual checks. See [complete formal definitions](profile-recognition.md).
