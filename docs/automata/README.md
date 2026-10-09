# Executable profile automata

Each profile has a complete JSON five-tuple, a CSV transition relation, a DOT graph
and a standalone SVG transition diagram. `summary.json` contains model sizes.

The tuple fields are `Q`, `Sigma`, `delta`, `q0` and `F`; extra metadata identifies
the profile and epsilon-NFA type. `delta` enumerates all transition triples. Omitted
state/input combinations have an empty destination set. `ε` is an empty-word
transition label and is excluded from `Sigma`.

SVG edges use bucket labels A0, A1, etc., whose complete symbol sets are printed in
each diagram. Backend additionally labels mandatory singleton sets as R(j,i),
defined beneath each branch. Parallel transitions are grouped only for display. State identifiers
match JSON/CSV; the same model provides the DOT export.

| Profile | States | Alphabet size | Transition triples | Diagram |
|---|---:|---:|---:|---|
| Full Stack | 12 | 13 | 45 | [SVG](FULL_STACK_DEVELOPER.svg) |
| Machine Learning | 12 | 9 | 33 | [SVG](MACHINE_LEARNING_ENGINEER.svg) |
| Backend | 42 | 13 | 160 | [SVG](BACKEND_DEVELOPER.svg) |
| Data Engineer | 10 | 8 | 29 | [SVG](DATA_ENGINEER.svg) |

Regenerate using `python tools/export_automata.py`. No Graphviz installation is
required to generate the SVG. See [formal definitions and rationale](../profile-recognition.md).
