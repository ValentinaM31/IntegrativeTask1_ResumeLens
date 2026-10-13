# Executable profile automata

Each profile has a complete JSON five-tuple, CSV transition function, DOT graph
and standalone SVG transition diagram. The files are exported from the actual
`pyformlang.finite_automaton.DeterministicFiniteAutomaton` objects.

The tuple fields are `Q`, `Sigma`, `delta`, `q0` and `F`. Metadata identifies
`type: DFA`, `complete: true` and the rejecting sink `q_dead`. Every state/input
pair has exactly one destination: `delta` contains `|Q| × |Sigma|` triples.
There are no epsilon transitions. Symbols outside the finite alphabet reject.

The SVG presents one complete outgoing-transition panel per source state. Commas
on an edge separate alternative input symbols. Identical names in different
panels denote the same state, including self-loops drawn to another occurrence
of that name. All sink transitions are explicit; nothing is omitted. The DOT
file supplies the conventional single-graph view of the same transition function.
The panel format keeps Backend's memory states and long labels readable.

| Profile | States | Alphabet size | Transition triples | Diagram |
|---|---:|---:|---:|---|
| Full Stack | 7 | 13 | 91 | [SVG](FULL_STACK_DEVELOPER.svg) |
| Machine Learning | 7 | 10 | 70 | [SVG](MACHINE_LEARNING_ENGINEER.svg) |
| Backend | 19 | 13 | 247 | [SVG](BACKEND_DEVELOPER.svg) |
| Data Engineer | 6 | 8 | 48 | [SVG](DATA_ENGINEER.svg) |

Regenerate using `python tools/export_automata.py`. SVG generation does not
require Graphviz. See the [complete formal definitions](../profile-recognition.md)
for group progression, Backend memory masks and the recognized languages.
