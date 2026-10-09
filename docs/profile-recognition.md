# Qualification-pattern recognition

Stage 3 consumes canonical qualifications from `process_resume()` and executes four
`pyformlang.finite_automaton.EpsilonNFA` instances. `classify_skills()` returns a separate
classification object; the first-stage JSON 1.0 contract is unchanged. No scores,
proficiency estimates or hiring decisions are produced.

## Patterns and their origin

The implementation follows the existing `config/profiles_design.json`. The assignment
describes possible qualifications and examples; these are the team's explicit minimum
patterns, not an assertion that every illustrative qualification is mandatory.
Requirements for the two additional profiles were announced separately but are not
included in this repository. Backend and Data Engineer therefore retain the documented
team-defined criteria, subject to any later teacher specification.

| Profile | Mandatory pattern | Optional, informational only |
|---|---|---|
| Full Stack | JS/TS; React/Angular/Vue; Node/Django/Spring Boot; SQL/PostgreSQL/MySQL/MongoDB; Git | REST API, Docker |
| Machine Learning | Python; Pandas/NumPy; TensorFlow/PyTorch; SQL/PostgreSQL/MySQL; Git | Scikit-learn, ML model, Docker |
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
automaton rejects: preparation does not insert substitutes or epsilon placeholders.

## Complete formal definitions

Every model is M = (Q, Σ, δ, q0, F). For a profile with B branches and n buckets:

- Q = {q0, qf} ∪ {b(j)_g(i)_before, b(j)_g(i)_seen | 0 ≤ j < B, 0 ≤ i < n}.
- Σ = A0 ∪ ... ∪ A(n−1). Each alphabet member is a whole canonical token, not a character.
- q0 is the unique initial state; F = {qf}.
- For each branch j, δ(q0, ε) contains b(j)_g(0)_before.
- For every a ∈ Ai, δ(b(j)_g(i)_before, a) contains that same `before` state,
  and δ(b(j)_g(i)_seen, a) contains that same `seen` state.
- For every a ∈ R(j,i), δ(b(j)_g(i)_before, a) also contains b(j)_g(i)_seen.
- For i < n−1, δ(b(j)_g(i)_seen, ε) contains b(j)_g(i+1)_before.
- δ(b(j)_g(n−1)_seen, ε) contains qf.
- All transitions not listed above have the empty destination set.

R(j,i) is the mandatory subset of bucket Ai on branch j. Epsilon is the empty word,
not a member of Σ. There is no epsilon edge from `before` to `seen`, so a missing
requirement cannot be bypassed. `before` loops allow other bucket members before a
required member; `seen` loops allow additional bucket members afterward.

These definitions become complete individual tuples by substituting the following
finite sets. Fully enumerated states and transitions are also supplied in
[`automata/`](automata/README.md), exported from the executable objects.

### Full Stack Developer

B = 1, n = 5, R(0,i) = Ai for all i.

| i | Ai |
|---|---|
| 0 | {JAVASCRIPT, TYPESCRIPT} |
| 1 | {REACT, ANGULAR, VUE} |
| 2 | {NODE_JS, DJANGO, SPRING_BOOT} |
| 3 | {SQL, POSTGRESQL, MYSQL, MONGODB} |
| 4 | {GIT} |

The language is A0+ A1+ A2+ A3+ A4+. There are 12 states, 13 alphabet symbols and
45 transition triples. [Complete tuple](automata/FULL_STACK_DEVELOPER.json),
[diagram](automata/FULL_STACK_DEVELOPER.svg).

### Machine Learning Engineer

B = 1, n = 5, R(0,i) = Ai for all i.

| i | Ai |
|---|---|
| 0 | {PYTHON} |
| 1 | {PANDAS, NUMPY} |
| 2 | {TENSORFLOW, PYTORCH} |
| 3 | {SQL, POSTGRESQL, MYSQL} |
| 4 | {GIT} |

The language is A0+ A1+ A2+ A3+ A4+. There are 12 states, 9 alphabet symbols and
33 transition triples. [Complete tuple](automata/MACHINE_LEARNING_ENGINEER.json),
[diagram](automata/MACHINE_LEARNING_ENGINEER.svg).

### Backend Developer

B = 4, n = 5.

| i | Ai |
|---|---|
| 0 | {JAVA, PYTHON, JAVASCRIPT, TYPESCRIPT} |
| 1 | {SPRING_BOOT, DJANGO, NODE_JS} |
| 2 | {SQL, POSTGRESQL, MYSQL, MONGODB} |
| 3 | {REST_API} |
| 4 | {GIT} |

| j | R(j,0) | R(j,1) |
|---|---|---|
| 0 | {JAVA} | {SPRING_BOOT} |
| 1 | {PYTHON} | {DJANGO} |
| 2 | {JAVASCRIPT} | {NODE_JS} |
| 3 | {TYPESCRIPT} | {NODE_JS} |

For i = 2, 3, 4, R(j,i) = Ai on every branch. The language is the union over j of
`A0* R(j,0) A0* A1* R(j,1) A1* A2+ A3+ A4+`.
Branches share alphabets, but acceptance requires both members of one compatible pair.
There are 42 states, 13 alphabet symbols and 160 transition triples.
[Complete tuple](automata/BACKEND_DEVELOPER.json), [diagram](automata/BACKEND_DEVELOPER.svg).

### Data Engineer

B = 1, n = 4, R(0,i) = Ai for all i.

| i | Ai |
|---|---|
| 0 | {PYTHON} |
| 1 | {SQL, POSTGRESQL, MYSQL} |
| 2 | {ETL, AIRFLOW, APACHE_SPARK} |
| 3 | {GIT} |

The language is A0+ A1+ A2+ A3+. There are 10 states, 8 alphabet symbols and
29 transition triples. [Complete tuple](automata/DATA_ENGINEER.json),
[diagram](automata/DATA_ENGINEER.svg).

## Why epsilon-NFAs?

Each automaton has epsilon transitions between bucket submachines. A required symbol
can also have two destinations from `before`: its loop and `seen`. The transition
relation therefore maps a state and symbol to a set of destinations. These are
epsilon-NFAs, not DFAs or NFAs without epsilon. The Backend model uses the additional
epsilon branches to express a union of compatible-pair languages directly.

The general constructor builds all four models using the same rules. Other automaton
types could express equivalent regular languages; epsilon-NFAs keep the pattern
composition and compatible-pair choices explicit without a large product of states.
Acceptance is obtained only from `machine.accepts(sequence)`. Missing-group checks
produce explanations afterward and do not replace automaton execution.

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
`ignored_for_pattern`. Groups preserve their configured alternative order. Empty
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

## Limits and next stages

Recognition assesses these finite team-defined patterns using the extracted evidence.
It cannot recover an omitted/negated skill, prove expertise or detect arbitrary new
technologies. Education and experience are retained by stage 1 but are not numerical
requirements in these profile patterns. The separate textX grammar and candidate DSL are provided by the following
[candidate-language increment](candidate-language.md). The following
[complete-workflow increment](complete-workflow.md) generates HTML; the interactive
UI remains pending. Neither component decides profile recognition.

The official [pyformlang finite-automaton API](https://pyformlang.readthedocs.io/en/latest/modules/finite_automaton.html)
documents epsilon-NFAs and acceptance execution. The implementation is verified with
the project's pinned pyformlang 1.0.11, rather than assuming the documentation's
displayed version number matches the installed package.
