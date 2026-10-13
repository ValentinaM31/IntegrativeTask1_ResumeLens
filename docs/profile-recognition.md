# Qualification-pattern recognition

Stage 3 consumes canonical qualifications from `process_resume()` and executes four
`pyformlang.finite_automaton.DeterministicFiniteAutomaton` instances. `classify_skills()` returns a separate
classification object; the first-stage JSON 1.0 contract is unchanged. No scores,
proficiency estimates or hiring decisions are produced.

## Patterns and their origin

The implementation follows `config/profiles_design.json`. The assignment
describes possible qualifications and examples; these are the team's explicit minimum
patterns, not an assertion that every illustrative qualification is mandatory.
The Machine Learning diagram on page 5 admits Scikit-learn, TensorFlow or PyTorch
in the same alternative group; this is now reflected in the executable pattern.
See [requirement alignment](profile-alignment.md) for the reference mapping.
Detailed requirements for the two additional profiles were announced separately but are not
included in this repository. Backend and Data Engineer retain the documented
team-defined criteria, subject to any later teacher specification.

| Profile | Mandatory pattern | Optional, informational only |
|---|---|---|
| Full Stack | JS/TS; React/Angular/Vue; Node/Django/Spring Boot; SQL/PostgreSQL/MySQL/MongoDB; Git | REST API, Docker |
| Machine Learning | Python; Pandas/NumPy; Scikit-learn/TensorFlow/PyTorch; SQL/PostgreSQL/MySQL; Git | ML model, Docker |
| Backend | A compatible language/framework pair; SQL/PostgreSQL/MySQL/MongoDB; REST API; Git | Docker |
| Data Engineer | Python; SQL/PostgreSQL/MySQL; ETL/Airflow/Apache Spark; Git | Docker, Pandas |

Backend pairs are Java + Spring Boot, Python + Django, JavaScript + Node.js, or
TypeScript + Node.js. A slash above means an alternative, not a conjunction.
PostgreSQL satisfies an explicit database alternative; it does not create a SQL symbol.

## Canonical preparation

For each profile, define disjoint buckets A0, ..., A(n−1). The preparation function
deduplicates the input and concatenates the alphabetical intersection with each bucket:

`sort(S ∩ A0) · sort(S ∩ A1) · ... · sort(S ∩ A(n−1))`.

Every relevant symbol is retained. Backend preparation does not pick a compatible
pair; all language and backend-framework candidates remain for the automaton to read.
Optional and unrelated known qualifications are not in the projected sequence. They
remain in the first-stage result and are identified in `optional_present` and
`ignored_for_pattern`. Unknown canonical symbols are rejected, not silently discarded.

For example, `GIT, NODE_JS, JAVASCRIPT, POSTGRESQL, REACT` becomes
`JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT` for Full Stack. Alphabetical first-stage
order alone is insufficient. An empty mandatory bucket contributes no symbols and the
automaton rejects: preparation does not insert substitute qualifications.

## Complete formal definitions

Every model is M = (Q, Σ, δ, q0, F), where δ is a total function
`Q × Σ → Q`. Each alphabet member is a whole canonical token, not a character.
There is exactly one destination for every state/symbol pair and no empty
transition. `q_dead` is an explicit nonaccepting sink:
`δ(q_dead, a) = q_dead` for every `a ∈ Σ`.

For Full Stack, Machine Learning and Data Engineer, let A0, ..., A(n−1) be the
nonempty, disjoint required buckets listed below. Their complete construction is:

- Q = {q0, q1, ..., qn, q_dead}.
- Σ = A0 ∪ ... ∪ A(n−1).
- q0 is the unique initial state; F = {qn}.
- δ(q0, a) = q1 when `a ∈ A0`; every other symbol goes to q_dead.
- For `1 ≤ k < n`, δ(qk, a) = qk when `a ∈ A(k−1)` and q(k+1)
  when `a ∈ Ak`; every other symbol goes to q_dead.
- δ(qn, a) = qn when `a ∈ A(n−1)`; every other symbol goes to q_dead.
- δ(q_dead, a) = q_dead for every alphabet symbol.

State qk records that the first k buckets have been satisfied. Its loop permits
additional symbols from the most recently satisfied bucket. Advancing requires a
symbol from the immediately following bucket; missing a bucket, returning to an
earlier bucket or using a later one prematurely reaches q_dead. The recognized
language is `A0+ A1+ ... A(n−1)+`, with no inserted qualifications.

Backend uses the deterministic memory construction defined in its section below.
Fully enumerated states and transitions are supplied in
[`automata/`](automata/README.md), exported from the executable objects. Because
the transition function is total, each model has exactly `|Q| × |Σ|` transition
triples, including sink transitions. The construction is not claimed to be minimal.

### Full Stack Developer

n = 5; Q = {q0, q1, q2, q3, q4, q5, q_dead}; F = {q5}.

| i | Ai |
|---|---|
| 0 | {JAVASCRIPT, TYPESCRIPT} |
| 1 | {REACT, ANGULAR, VUE} |
| 2 | {NODE_JS, DJANGO, SPRING_BOOT} |
| 3 | {SQL, POSTGRESQL, MYSQL, MONGODB} |
| 4 | {GIT} |

The language is A0+ A1+ A2+ A3+ A4+. There are 7 states, 13 alphabet symbols and
91 transition triples. [Complete tuple](automata/FULL_STACK_DEVELOPER.json),
[diagram](automata/FULL_STACK_DEVELOPER.svg).

### Machine Learning Engineer

n = 5; Q = {q0, q1, q2, q3, q4, q5, q_dead}; F = {q5}.

| i | Ai |
|---|---|
| 0 | {PYTHON} |
| 1 | {PANDAS, NUMPY} |
| 2 | {SCIKIT_LEARN, TENSORFLOW, PYTORCH} |
| 3 | {SQL, POSTGRESQL, MYSQL} |
| 4 | {GIT} |

The language is A0+ A1+ A2+ A3+ A4+. There are 7 states, 10 alphabet symbols and
70 transition triples. [Complete tuple](automata/MACHINE_LEARNING_ENGINEER.json),
[diagram](automata/MACHINE_LEARNING_ENGINEER.svg).

### Backend Developer

n = 5. Q = {q0} ∪ {L1, ..., L7} ∪ {W1, ..., W6}
∪ {pair_seen, q3, q4, qf, q_dead}; F = {qf}.

| i | Ai |
|---|---|
| 0 | {JAVA, PYTHON, JAVASCRIPT, TYPESCRIPT} |
| 1 | {SPRING_BOOT, DJANGO, NODE_JS} |
| 2 | {SQL, POSTGRESQL, MYSQL, MONGODB} |
| 3 | {REST_API} |
| 4 | {GIT} |

| Alternative | Language | Compatible framework |
|---|---|---|
| 0 | JAVA | SPRING_BOOT |
| 1 | PYTHON | DJANGO |
| 2 | JAVASCRIPT | NODE_JS |
| 3 | TYPESCRIPT | NODE_JS |

Σ = A0 ∪ A1 ∪ A2 ∪ A3 ∪ A4, and q0 is the unique initial state. A language
creates a mask of the frameworks it can satisfy: DJANGO = 1, NODE_JS = 2 and
SPRING_BOOT = 4. Thus `λ(PYTHON)=1`, `λ(JAVASCRIPT)=λ(TYPESCRIPT)=2` and
`λ(JAVA)=4`. Let `μ` map each framework to its corresponding bit.

`Lm` records the union of compatible-framework bits after reading languages.
`Wm` records the same mask after entering the framework bucket without yet finding
a compatible pair. W7 is unnecessary: mask 7 admits every framework, so its first
framework always completes a pair. The complete transition function is:

- From q0, a language `a ∈ A0` reaches `Lλ(a)`.
- From Lm, another language a reaches `L(m OR λ(a))`.
- From Lm, a framework b reaches pair_seen if `m AND μ(b) ≠ 0`;
  otherwise it reaches Wm.
- From Wm, a framework b reaches pair_seen if `m AND μ(b) ≠ 0`;
  otherwise it remains in Wm.
- From pair_seen, frameworks loop; a database in A2 reaches q3.
- From q3, databases loop; REST_API in A3 reaches q4.
- From q4, REST_API loops; GIT in A4 reaches qf.
- From qf, GIT loops.
- Every transition not listed above reaches q_dead; every alphabet symbol loops
  at q_dead.

The mask is recognition state, not inferred candidate data. It stores which pairs
could be completed from the actual languages already read. After one compatible
framework appears, other incomplete alternatives do not cause rejection. A
database cannot bypass the compatible-pair requirement.

For a compatible pair `(l, f)`, the corresponding language is
`A0* l A0* A1* f A1* A2+ A3+ A4+`. Backend recognizes the union over the four
configured pairs. It has 19 states, 13 alphabet symbols and 247 transition triples.
[Complete tuple](automata/BACKEND_DEVELOPER.json), [diagram](automata/BACKEND_DEVELOPER.svg).

### Data Engineer

n = 4; Q = {q0, q1, q2, q3, q4, q_dead}; F = {q4}.

| i | Ai |
|---|---|
| 0 | {PYTHON} |
| 1 | {SQL, POSTGRESQL, MYSQL} |
| 2 | {ETL, AIRFLOW, APACHE_SPARK} |
| 3 | {GIT} |

The language is A0+ A1+ A2+ A3+. There are 6 states, 8 alphabet symbols and
48 transition triples. [Complete tuple](automata/DATA_ENGINEER.json),
[diagram](automata/DATA_ENGINEER.svg).

## Why complete DFAs?

Each machine has one initial state, consumes one canonical symbol per transition
and has exactly one next state for every state/alphabet-symbol pair. There are no
epsilon transitions and no multiple-successor choices. The explicit sink makes
all invalid in-alphabet transitions visible in the formal definition and exports.
These properties establish that the current recognizers are complete DFAs.

Canonical bucket order permits a direct group-progress construction. Backend
adds finite mask memory for compatible pairs instead of nondeterministic branches.
This representation makes an individual trace easy to follow while preserving
the previously configured qualification languages. It does not tighten the
profile criteria or infer missing skills. Earlier verification records describe
the former epsilon-NFA implementation and retain their historical scope.

Acceptance is obtained only from `machine.accepts(sequence)`. Missing-group checks
produce explanations afterward and do not replace automaton execution. Current
execution and equivalence-check outcomes are in [verification results](test-results.md).

## API and reproducibility

```python
from resumelens import process_resume, classify_skills

text = "Name: Alex\nSkills: Git, NodeJS, JS, Postgres, React.js."
first = process_resume(text)
classification = classify_skills(first["normalized_skills"])
assert classification["accepted_profiles"] == ["FULL_STACK_DEVELOPER"]
```

The return object has `accepted_profiles` (unique, alphabetical) and `profiles`
(one result for each configured profile). Each result includes `profile`, `accepted`,
`sequence`, `missing_groups`, `compatible_pair_missing`, `optional_present` and
`ignored_for_pattern`, plus `explanations` and `pair_diagnostics`. The latter fields
describe missing groups and configured compatible-pair alternatives after the
automaton decision. They neither infer new skills nor change the accepted language.
See [diagnostic fields and examples](profile-explanations.md).
Groups preserve their configured alternative order. Empty
skills are valid and reject all four profiles. Invalid symbols/collections raise ValueError.

```powershell
.\.venv\Scripts\python.exe tools/export_automata.py
.\.venv\Scripts\python.exe tools/classify_examples.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Classification outputs are in `data/classification/`; eight scenarios match the
pre-existing design expectations. Tests cover missing groups, all Full Stack
alternative combinations, ML and Data alternatives, compatible and incompatible
Backend pairs, order permutations, duplicates, optional skills, multiple profiles,
invalid configurations and the equivalence of exported transition relations.
The deterministic checks additionally cover total transitions, the rejecting sink,
compatible-pair memory and equivalence with the earlier qualification language.

## Limits and next stages

Recognition assesses these finite team-defined patterns using the extracted evidence.
It cannot recover an omitted/negated skill, prove expertise or detect arbitrary new
technologies. Education and experience are retained by stage 1 but are not numerical
requirements in these profile patterns. The separate textX grammar and candidate DSL are provided by the following
[candidate-language increment](candidate-language.md). The following
[complete-workflow increment](complete-workflow.md) generates HTML; the
[fourth increment](local-ui.md) adds the interactive UI. Both consume the executed
profile recognition results.

The official [pyformlang finite-automaton API](https://pyformlang.readthedocs.io/en/latest/modules/finite_automaton.html)
documents deterministic automata and acceptance execution. The project pins
pyformlang 1.0.11, rather than assuming the documentation's
displayed version number matches the installed package.
