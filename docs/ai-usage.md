

## ia usage

**Our prompt:**
How should extraction identify qualifications and retain evidence from the
original resume?

**AI proposal:**
Lowercase the entire resume and replace aliases with canonical names before
applying the regular expressions.

**Student correction:**
That combines extraction and normalization. Replacing `JS` with `JAVASCRIPT`
changes the document length and invalidates later character positions. Stage 1
must retain the original spelling and spans. Apply case folding to a copy of an
extracted alias during normalization. Every evidence item must satisfy
`text[start:end] == raw`.

**Revised approach:**
Run case-insensitive patterns on the unchanged input and retain each match's raw
value and half-open span. The transducer receives a separate case-folded alias.
Explicit section records take priority over contained phrases, preventing
education and experience from being duplicated.

**Project evidence:** [extraction](../src/resumelens/extraction.py),
[first-stage contract](data-contract.md) and
[evidence tests](../tests/test_first_stage.py).

## Recognize literal aliases with explicit boundaries

**Our prompt:**
How can we recognize Java, JavaScript, React.js and Git without matching parts of
unrelated words?

**AI proposal:**
Use an alternation such as `Java|JavaScript|React.js|Git`.

**Our correction:**
`Java` can match the beginning of `JavaScript`, and the dot in `React.js` is a
regex metacharacter. `Git` must not become evidence inside `GitHub`. Escape each
catalog alias with `re.escape`, prefer longer alternatives and impose explicit
boundaries. A syntactic match also needs context: the ordinary verb `react` is
not evidence of the React library.

**Revised approach:**
Build escaped alternatives sorted by descending length. Apply the implemented
lookarounds, URL/email exclusions, technical contexts and negation rules. Retain
excluded known mentions with their spans and reasons.

**Project evidence:** [regular expressions](regex.md),
[negation rules](negation-handling.md) and
[boundary/context tests](../tests/test_first_stage.py).

## Execute a real transducer and distinguish empty output from empty input

**Our prompt:**
How should `JS -> JAVASCRIPT` be represented formally?

**AI proposal:**
Use a dictionary lookup and illustrate it with a state diagram, or emit
`JAVASCRIPT` on every transition that recognizes a character of the alias.

**Our correction:**
The implementation must execute a `pyformlang` finite-state transducer, not just
draw one. Define all seven components: states, input alphabet, output alphabet,
transition relation, output relation, initial state and accepting states. The
whole accepted alias must produce one canonical token. For input `js`, the first
edge consumes `j` and emits empty output; the last consumes `s` and emits
`JAVASCRIPT`. Empty output does not mean an empty-input transition. Acceptance
requires consuming the entire alias, so `JSx` must not translate as JavaScript.

**Revised approach:**
Execute character-level paths using `FST.translate`. Earlier edges emit empty
output and the final edge emits the canonical symbol. Independent paths support
shared prefixes through nondeterminism; output uniqueness is checked separately.
Case folding applies to a copy, preserving source evidence.

**Project evidence:** [normalizer](../src/resumelens/normalization.py),
[complete seven-tuples](transducers.md) and
[worked accepting paths](models/examples/README.md).

## Prepare a profile-specific sequence

**Our prompt:**
Can classification remain consistent when candidates list the same skills in
different orders?

**AI proposal:**
Sort all canonical skills alphabetically and pass the same sequence to every
profile recognizer.

**Our correction:**
Alphabetical order in the first-stage JSON is not the order of the profile
language. Full Stack consumes language, frontend, backend, database and version
control groups. Project onto those groups, sort within each group and concatenate
them in that order. Remove duplicate canonical symbols, but retain all relevant
alternatives. Choosing only one language or framework could discard a valid
Backend pair.

**Revised approach:**
Use `canonical_sequence` separately for each profile. Full Stack prepares
`GIT, NODE_JS, JAVASCRIPT, POSTGRESQL, REACT` as
`JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT`. Optional and unrelated known skills
remain in the first-stage result but do not fill required groups. Unknown
canonical API symbols raise an error instead of silently disappearing.

**Project evidence:** [canonical preparation](profile-recognition.md),
[recognizer](../src/resumelens/classification.py) and
[permutation/duplicate tests](../tests/test_classification.py).

## Separate data-processing and learning-library requirements

**Our prompt:**
Which groups should the Machine Learning automaton recognize?

**AI proposal:**
Put Pandas, NumPy, Scikit-learn, TensorFlow and PyTorch in one group; any member can
satisfy the library requirement.

**Our correction:**
That accepts `PYTHON, PANDAS, POSTGRESQL, GIT` without a learning library. The
assignment diagram has two successive groups: Pandas or NumPy, then
Scikit-learn, TensorFlow or PyTorch. Keep them separate. Do not require all three
learning libraries either: they are alternatives. PostgreSQL can satisfy the
configured database group without inventing a separate SQL skill.

**Revised approach:**
Require Python; Pandas/NumPy; Scikit-learn/TensorFlow/PyTorch; an admitted
relational database; and Git. `PYTHON, PANDAS, TENSORFLOW, POSTGRESQL, GIT` accepts.
Removing its learning library rejects; an optional ML-model mention cannot
replace that requirement.

**Project evidence:** [assignment alignment](profile-alignment.md),
[profile configuration](../config/profiles_design.json) and
[reference-diagram regressions](../tests/test_profile_alignment.py).

## Make deterministic recognition explicit

**Our prompt:**
How do we implement a DFA that accepts complete patterns and rejects missing
qualification groups?

**AI proposal:**
Use empty transitions between groups and call the machine deterministic because
its input is already sorted.

**Our correction:**
Canonical ordering does not change the automaton's type. A DFA has one next state
per state/input pair and no empty-input transitions. For our complete DFA
specification, `delta: Q x Sigma -> Q` must be total. Add a nonaccepting `q_dead`
state for invalid transitions, with every alphabet symbol looping at the sink.
Execute the automaton to decide acceptance; missing-group checks should only
explain that decision afterward.

**Revised approach:**
Construct `DeterministicFiniteAutomaton` objects directly. Full Stack and Machine
Learning use `q0` through `q5` plus `q_dead`; Data Engineer uses `q0` through `q4`
plus `q_dead`. Full Stack moves from `q1` to `q_dead` on `NODE_JS` because the
frontend group is missing. Export the actual total transition function and use
`machine.accepts(sequence)` as the acceptance authority.

**Project evidence:** [complete five-tuples](profile-recognition.md),
[transition diagrams](automata/README.md) and
[DFA completeness tests](../tests/test_classification.py).

## Retain memory for compatible Backend pairs

**Our prompt:**
Is any language together with any framework sufficient for Backend?

**AI proposal:**
Accept one language and one framework, then continue with database, REST API and
Git.

**Our correction:**
The choices must form an admitted pair. `JAVA, DJANGO, SQL, REST_API, GIT` must
reject; replacing Django with Spring Boot allows acceptance. With several
languages and frameworks, one incompatible combination does not invalidate a
compatible one. The DFA must remember which frameworks can complete a pair from
the languages actually read, then accept when at least one appears.

**Revised approach:**
Language memory states `L1` through `L7` combine compatible-framework choices.
Waiting states `W1` through `W6` consume frameworks until a compatible member
reaches `pair_seen`. Database, REST API and Git remain mandatory afterward. No
pair is selected or inferred during canonical preparation.

**Project evidence:** [Backend definition](profile-recognition.md),
[DFA constructor](../src/resumelens/classification.py) and
[compatible/incompatible pair tests](../tests/test_classification.py).

## Separate syntactic validation from semantic consistency

**Our prompt:**
Is a candidate specification valid as soon as textX parses it?

**AI proposal:**
Yes. If its braces and keywords are correct, render its declared profiles as
HTML.

**Our correction:**
Parsing validates lexical and structural rules; it cannot prove that a claimed
profile is supported by the skills. Specify the language in EBNF with terminals,
nonterminals and repeated records. After parsing, reject duplicate skill/profile
declarations and recompute acceptance through the DFA. Require an exact set
match, rejecting both invented profiles and omitted accepted profiles. Render
only the validated model and escape candidate-provided text.

**Revised approach:**
Generate the DSL with escaped strings, parse with textX, check semantics and then
render the structured result. Education, experience and contacts permit repeated
records; canonical skills and accepted profiles require unique declarations.

**Project evidence:** [EBNF and semantic rules](candidate-language.md),
[parser](../src/resumelens/dsl.py), [renderer](../src/resumelens/rendering.py)
and [valid/invalid DSL tests](../tests/test_dsl.py).

## Interpret evaluation results without changing expectations

**Ourprompt:**
Can we claim perfect performance when all candidate pipelines validate?

**AI proposal:**
Report 100% accuracy, combine the datasets and change any differing labels to
match the generated results.

**Our correction:**
Internal validity and correct interpretation are different measurements. Keep
the eighteen-case preannotated evaluation separate from the fourteen-case
workflow regression and earlier extraction evaluation. Do not change frozen
inputs or labels to improve results. Synthetic examples do not establish accuracy
on a population of real applicants.

**Revised approach:**
Report eighteen valid pipelines with fourteen exact annotation matches and four
retained disagreements. Report the fourteen exact workflow-regression cases with
their own denominator. Preserve input/annotation hashes, identify later runs as
regression comparisons and show actual per-case outcomes on the poster.

**Project evidence:** [preannotated evaluation](preannotated-evaluation.md),
[workflow regression](workflow-evaluation.md), [poster method](poster/README.md)
and [recorded verification](test-results.md).

