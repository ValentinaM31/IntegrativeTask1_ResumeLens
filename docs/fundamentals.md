# Regular expressions and transducers

A regular expression describes a language of textual patterns. `re.finditer` locates matches and `Match.span` yields positions. `React\.js` matches a literal dot; boundaries prevent Java inside JavaScript.

Extraction preserves spelling. Equivalence between React.js and ReactJS is then modeled by an FST with states, input transitions and output symbols. A casefolded copy is used; evidence stays unchanged.

## Translation example

| State | Input | Destination | Output |
|---|---|---|---|
| q0 | j | q1 | ε |
| q1 | s | q2 | JAVASCRIPT |

Here Q={q0,q1,q2}, Σ={j,s}, Γ={JAVASCRIPT}, δ={(q0,j,q1),(q1,s,q2)}, initial state q0 and F={q2}. ω assigns ε to the first transition and JAVASCRIPT to the second. Empty output is not an epsilon input transition: both edges consume a character.

Valid translation consumes all input and ends in a final state. JSx fails because there is no transition for x. In complete machines, paths sharing an initial character can lead to different states, so nondeterminism is supported. See `transducers.md` and `models/` for complete septuples, tables and diagrams.
