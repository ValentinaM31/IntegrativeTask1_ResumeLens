# Worked transducer paths

These views show four accepting alias paths taken from the executable
`pyformlang.fst.FST` machines. They retain the real state names and transition
labels. Each is a **subset of a complete category machine**: omitted branches
still exist, and the full machine remains nondeterministic. These are neither
separate production transducers nor minimized replacements.

The input to each FST is `list(raw.casefold())`. Case folding is a separate
preprocessor; it does not collapse separators or internal spaces. In the
labels and tables, `␠` means exactly one space and `ε` means empty **output**.
Every edge consumes its displayed input character. The initial arrow marks
`q0`; a double circle marks an accepting state.

[Complete seven-tuples and full diagrams](../../transducers.md)

Regenerate from an installed checkout with:

```powershell
.\.venv\Scripts\python.exe tools/export_model_examples.py
.\.venv\Scripts\python.exe tools/export_model_examples.py --check
```

The generator verifies each edge, complete input consumption, accepting
state and canonical output against the actual machine before writing. Check
mode also rejects stored views that differ from those verified transitions.

## JS → JAVASCRIPT

Category: `languages`. Raw input: `JS`. FST input: `js`.

![Accepting path for JS](javascript.svg)

```mermaid
flowchart LR
    start(["start"]) --> n0
    n0(("q0"))
    n1(("s0_a1_1"))
    n2((("s0_a1_2")))
    n0 -->|"j / ε"| n1
    n1 -->|"s / JAVASCRIPT"| n2
```

| Step | Raw character | FST input | Source | Target | Output |
|---:|---|---|---|---|---|
| 1 | `J` | `j` | `q0` | `s0_a1_1` | `ε` |
| 2 | `S` | `s` | `s0_a1_1` | `s0_a1_2` | `JAVASCRIPT` |

The complete input is exhausted at `s0_a1_2`; concatenating the
transition outputs produces the single symbol `JAVASCRIPT`.

## React.js → REACT

Category: `frameworks_libraries`. Raw input: `React.js`. FST input: `react.js`.

![Accepting path for React.js](react.svg)

```mermaid
flowchart LR
    start(["start"]) --> n0
    n0(("q0"))
    n1(("s4_a1_1"))
    n2(("s4_a1_2"))
    n3(("s4_a1_3"))
    n4(("s4_a1_4"))
    n5(("s4_a1_5"))
    n6(("s4_a1_6"))
    n7(("s4_a1_7"))
    n8((("s4_a1_8")))
    n0 -->|"r / ε"| n1
    n1 -->|"e / ε"| n2
    n2 -->|"a / ε"| n3
    n3 -->|"c / ε"| n4
    n4 -->|"t / ε"| n5
    n5 -->|". / ε"| n6
    n6 -->|"j / ε"| n7
    n7 -->|"s / REACT"| n8
```

| Step | Raw character | FST input | Source | Target | Output |
|---:|---|---|---|---|---|
| 1 | `R` | `r` | `q0` | `s4_a1_1` | `ε` |
| 2 | `e` | `e` | `s4_a1_1` | `s4_a1_2` | `ε` |
| 3 | `a` | `a` | `s4_a1_2` | `s4_a1_3` | `ε` |
| 4 | `c` | `c` | `s4_a1_3` | `s4_a1_4` | `ε` |
| 5 | `t` | `t` | `s4_a1_4` | `s4_a1_5` | `ε` |
| 6 | `.` | `.` | `s4_a1_5` | `s4_a1_6` | `ε` |
| 7 | `j` | `j` | `s4_a1_6` | `s4_a1_7` | `ε` |
| 8 | `s` | `s` | `s4_a1_7` | `s4_a1_8` | `REACT` |

The complete input is exhausted at `s4_a1_8`; concatenating the
transition outputs produces the single symbol `REACT`.

## Postgres → POSTGRESQL

Category: `databases`. Raw input: `Postgres`. FST input: `postgres`.

![Accepting path for Postgres](postgresql.svg)

```mermaid
flowchart LR
    start(["start"]) --> n0
    n0(("q0"))
    n1(("s11_a1_1"))
    n2(("s11_a1_2"))
    n3(("s11_a1_3"))
    n4(("s11_a1_4"))
    n5(("s11_a1_5"))
    n6(("s11_a1_6"))
    n7(("s11_a1_7"))
    n8((("s11_a1_8")))
    n0 -->|"p / ε"| n1
    n1 -->|"o / ε"| n2
    n2 -->|"s / ε"| n3
    n3 -->|"t / ε"| n4
    n4 -->|"g / ε"| n5
    n5 -->|"r / ε"| n6
    n6 -->|"e / ε"| n7
    n7 -->|"s / POSTGRESQL"| n8
```

| Step | Raw character | FST input | Source | Target | Output |
|---:|---|---|---|---|---|
| 1 | `P` | `p` | `q0` | `s11_a1_1` | `ε` |
| 2 | `o` | `o` | `s11_a1_1` | `s11_a1_2` | `ε` |
| 3 | `s` | `s` | `s11_a1_2` | `s11_a1_3` | `ε` |
| 4 | `t` | `t` | `s11_a1_3` | `s11_a1_4` | `ε` |
| 5 | `g` | `g` | `s11_a1_4` | `s11_a1_5` | `ε` |
| 6 | `r` | `r` | `s11_a1_5` | `s11_a1_6` | `ε` |
| 7 | `e` | `e` | `s11_a1_6` | `s11_a1_7` | `ε` |
| 8 | `s` | `s` | `s11_a1_7` | `s11_a1_8` | `POSTGRESQL` |

The complete input is exhausted at `s11_a1_8`; concatenating the
transition outputs produces the single symbol `POSTGRESQL`.

## Git SCM → GIT

Category: `tools_qualifications`. Raw input: `Git SCM`. FST input: `git scm`.

![Accepting path for Git SCM](git.svg)

```mermaid
flowchart LR
    start(["start"]) --> n0
    n0(("q0"))
    n1(("s20_a1_1"))
    n2(("s20_a1_2"))
    n3(("s20_a1_3"))
    n4(("s20_a1_4"))
    n5(("s20_a1_5"))
    n6(("s20_a1_6"))
    n7((("s20_a1_7")))
    n0 -->|"g / ε"| n1
    n1 -->|"i / ε"| n2
    n2 -->|"t / ε"| n3
    n3 -->|"␠ / ε"| n4
    n4 -->|"s / ε"| n5
    n5 -->|"c / ε"| n6
    n6 -->|"m / GIT"| n7
```

| Step | Raw character | FST input | Source | Target | Output |
|---:|---|---|---|---|---|
| 1 | `G` | `g` | `q0` | `s20_a1_1` | `ε` |
| 2 | `i` | `i` | `s20_a1_1` | `s20_a1_2` | `ε` |
| 3 | `t` | `t` | `s20_a1_2` | `s20_a1_3` | `ε` |
| 4 | `␠` | `␠` | `s20_a1_3` | `s20_a1_4` | `ε` |
| 5 | `S` | `s` | `s20_a1_4` | `s20_a1_5` | `ε` |
| 6 | `C` | `c` | `s20_a1_5` | `s20_a1_6` | `ε` |
| 7 | `M` | `m` | `s20_a1_6` | `s20_a1_7` | `GIT` |

The complete input is exhausted at `s20_a1_7`; concatenating the
transition outputs produces the single symbol `GIT`.

## Boundary examples

Direct FST translation rejects `JSx`, `ReactXjs`, `React-js`, `Git  SCM` and
`Postgres extra`: none is a complete catalog alias. `React.js` keeps its
literal dot, and `Git SCM` consumes exactly one internal space. An extractor
may locate a shorter alias within a larger source string; that is a separate
stage and does not expand the language accepted by the FST.
