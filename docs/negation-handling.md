# Explicit skill negation

The extractor previously accepted React in this supported skills line:

```text
Technical Skills: JS, NodeJS, Postgres, Git; I do not know React
```

That supplied the missing frontend qualification and incorrectly accepted
`FULL_STACK_DEVELOPER`. React is now retained in `excluded_mentions` with reason
`Explicit simple negation`; the other four symbols remain positive, and the
existing profile automaton rejects Full Stack. Adding a positive `I know React`
or `I use Angular` on a later line makes the same automaton accept it.

## Supported phrase families

The previous experience/knowledge phrases and Spanish `no uso` remain supported.
English `do not use/know`, `don't/don’t use/know` and `cannot/can not/can't/can’t use/know`
accept optional `I`. The inability forms prevent `I can't use React` from becoming
positive through the new immediate-use context. Spanish
`no sé`, `no se` and `no conozco` add explicit knowledge negations. Matching ignores
case. These new knowledge/use forms permit horizontal spaces/tabs without joining
different lines. Curly apostrophes are matched directly; input is not rewritten.

Only the immediate known alias or its directly coordinated known-alias list is
negated. List separators are commas, slashes and `and/or/nor/y/o/ni`, including a
comma before a conjunction. The existing clause boundaries remain sentence-ending
dots, `!`, `?`, semicolons, line breaks and `but/however/pero/aunque/sin embargo`.
Dots inside aliases such as `React.js` do not end the clause. Other intervening
words interrupt the alias list and prevent a negative phrase from reaching a new
positive predicate.

| Input | Positive canonical skills | Excluded mentions |
|---|---|---|
| `I do not know React` | None | React |
| `I don’t know React, Angular, or Vue; Python, Git` | GIT, PYTHON | React, Angular, Vue |
| `I do not know React, but I use Angular` | ANGULAR | React |
| `No sé Python ni Git; Java` | JAVA | Python, Git |
| `I know React` | REACT | None |
| `I know how to react to changes` | None | react, without supported technical context |
| `I don't know React. I know React` | REACT | First React mention |

Explicit negation is checked before every technical-context rule. A skills
heading therefore cannot override a negation. Outside headings, unsuffixed React
now also accepts an immediate English `know/use` or Spanish `sé/se/conozco/uso`
predicate, with optional `I/yo`. The development/work and framework/library rules
remain available. Ordinary uses of the verb react remain excluded. Pandas keeps
its existing skills-section or explicit data-analysis/processing requirement.

## Evidence and integration

Every mention keeps its exact `raw`, `start` and `end`; positions refer to the
original decoded Python string, including Unicode characters and CRLF. A later
positive occurrence is still normalized even if an earlier occurrence is
negated. The JSON 1.0 schema, real FST translations, four profile automata, DSL,
HTML renderer and web protocol remain compatible.

`tests/test_negation.py` contains eleven extraction tests with phrase/list/scope
subcases and three complete-workflow tests. Integration checks execute both real
CLIs outside the repository with a BOM/CRLF file, submit an actual loopback HTTP
request and compare all four downloaded ZIP files with their response payloads.
The existing source-text/evidence export validation remains active.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_negation.py -v
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/check_workflow_acceptance.py
.\.venv\Scripts\python.exe tools/check_web_acceptance.py
```

For a manual interface check, paste the first example and process it: Full Stack
must be rejected, and its JSON download must exclude REACT from normalized skills.
Add `I know React` on a new line and process again: Full Stack must be accepted.

## Limits

This is a finite rule extension, not a general language parser. Other negative
phrases, double negation, irony and unknown technologies remain outside scope.
An unknown word can interrupt a negative list, so a later known alias may be
accepted even when a human would interpret it as negated. Context rules admit
mentions, not verified proficiency. The added regression cases are not an
independent evaluation corpus or evidence of accuracy on real candidates.
