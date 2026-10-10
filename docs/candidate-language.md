# Candidate profile language

The candidate-language increment defined the DSL, generated it from stages 1–3
and validated it with textX 4.4.0. HTML is implemented in the following
[complete-workflow increment](complete-workflow.md); the interactive input UI is
provided by the [fourth increment](local-ui.md). The original first-stage JSON 1.0
remains unchanged.

## Representation

```text
candidate {
  name "Alex";
  contacts { email "alex@example.com"; }
  education { record "BSc Computer Science"; }
  experience { record "3 years developing web applications"; }
  skills {
    skill GIT;
    skill JAVASCRIPT;
    skill NODE_JS;
    skill POSTGRESQL;
    skill REACT;
  }
  accepted_profiles { profile FULL_STACK_DEVELOPER; }
}
```

All six sections occur exactly once in a fixed order. Empty repeated lists are
permitted. The name is a JSON-style double-quoted string or the literal `null`.
`"null"` is a real name string and differs from missing-name `null`.

Contact entries carry an explicit `email`, `phone` or `link` kind. Education and
experience retain original textual line records, including several records, without
inventing employers, degrees or dates. Canonical skills and accepted profiles use
their finite symbol vocabularies. Candidate data does not contain proficiency scores.

## EBNF

The following specification uses `,` for concatenation, `|` for alternatives,
`{...}` for zero or more occurrences and quoted values for literal terminals.
Braces inside quotes are actual delimiters; repetition braces outside quotes are
EBNF notation. Whitespace outside strings is ignored.

```ebnf
Candidate = "candidate", "{", Name, Contacts, Education, Experience,
            Skills, AcceptedProfiles, "}" ;
Name = "name", (JSONString | "null"), ";" ;
Contacts = "contacts", "{", {Contact}, "}" ;
Contact = ContactKind, JSONString, ";" ;
ContactKind = "email" | "phone" | "link" ;
Education = "education", "{", {Record}, "}" ;
Experience = "experience", "{", {Record}, "}" ;
Record = "record", JSONString, ";" ;
Skills = "skills", "{", {SkillEntry}, "}" ;
SkillEntry = "skill", SkillSymbol, ";" ;
AcceptedProfiles = "accepted_profiles", "{", {ProfileEntry}, "}" ;
ProfileEntry = "profile", ProfileSymbol, ";" ;
SkillSymbol = "JAVASCRIPT" | "TYPESCRIPT" | "PYTHON" | "JAVA"
            | "REACT" | "ANGULAR" | "VUE" | "NODE_JS" | "DJANGO"
            | "SPRING_BOOT" | "SQL" | "POSTGRESQL" | "MYSQL" | "MONGODB"
            | "PANDAS" | "NUMPY" | "SCIKIT_LEARN" | "TENSORFLOW" | "PYTORCH"
            | "REST_API" | "GIT" | "DOCKER" | "ML_MODEL"
            | "APACHE_SPARK" | "AIRFLOW" | "ETL" ;
ProfileSymbol = "FULL_STACK_DEVELOPER" | "MACHINE_LEARNING_ENGINEER"
              | "BACKEND_DEVELOPER" | "DATA_ENGINEER" ;
JSONString = '"', {Unescaped | Escape}, '"' ;
Unescaped = ? Unicode character except quotation mark, backslash and U+0000–U+001F ? ;
Escape = '\', ('"' | '\' | '/' | 'b' | 'f' | 'n' | 'r' | 't'
               | ('u', Hex, Hex, Hex, Hex)) ;
Hex = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
    | "A" | "B" | "C" | "D" | "E" | "F"
    | "a" | "b" | "c" | "d" | "e" | "f" ;
```

The start nonterminal is `Candidate`. The other nonterminals are all rule names
on the left-hand side above. The terminal alphabet consists of the quoted keywords,
delimiters, finite canonical/profile symbols, string characters and escape characters
defined by these rules. Unicode string content is lexical data rather than a new
qualification symbol. Single-quoted candidate values, bare names, invalid escapes
and unescaped control characters are not permitted.

This is a context-free specification of the structured language. textX executes its
grammar notation using ordered parsing choices; it is not a general CFG parser.
The finite symbol choices and fixed section order make that implementation suitable
for these EBNF productions. The language need not contain arbitrary nested sections
to represent the repeated records required by this assignment.

## Mapping to textX

The packaged [`src/resumelens/candidate.tx`](../src/resumelens/candidate.tx) implements
the EBNF. Root `Candidate` contains the section delimiters inline; the repeated
assignments `contacts*=Contact`, `education*=Record`, `experience*=Record`,
`skills*=SkillEntry` and `profiles*=ProfileEntry` create lists in the parsed model.
`NameValue` implements the name alternatives; the lexical `JsonString` match rule
implements `JSONString` and its character/escape productions.

`metamodel_from_str(..., autokwd=True)` builds a reusable parser/metamodel.
`model_from_str()` validates the whole source. Keyword boundaries prevent a
canonical symbol such as `PYTHON_EXTRA` from being accepted as `PYTHON`.
The custom JSON string token keeps escaping precise; `json.loads` decodes strings
after parsing, while `json.dumps` escapes strings during generation.

## Syntax and semantic validation

`generate_candidate_dsl(first_stage, classification)` creates text. Its inputs are
the valid result of `process_resume()` and the result of `classify_skills()`; it does
not mutate either input. Generation alone is not proof of acceptance.

`parse_candidate_dsl(source)` parses with textX and then verifies semantics:

- textX rejects lexical and structural errors with `TextXSyntaxError`.
- Additional checks reject duplicate skill/profile declarations with ValueError.
- It executes the profile recognizers for the declared skills and requires the
  declared accepted-profile set to match the result exactly. Both invented and
  omitted accepted profiles are rejected with ValueError.
- A non-string source raises ValueError; an empty string is a syntax error.

Repeated contact/education/experience records are structurally allowed, including
identical record text. Canonical skill/profile declarations must be unique. The
semantic constraints are separate from the EBNF: the grammar alone cannot prove
that qualifications satisfy a professional pattern or that a contact value is true.

The public parser returns a fresh dictionary with `name`, `contacts`, `education`,
`experience`, `skills` and `accepted_profiles`. Contact items use `{kind, value}`;
education/experience are string lists. Source offsets remain in the original JSON
1.0; they are not reinterpreted as positions inside the generated DSL.

## API example

```python
from resumelens import (
    process_resume, classify_skills,
    generate_candidate_dsl, parse_candidate_dsl,
)

first = process_resume("Name: Alex\nSkills: JS, React.js, NodeJS, Postgres, Git.")
classification = classify_skills(first["normalized_skills"])
source = generate_candidate_dsl(first, classification)
candidate = parse_candidate_dsl(source)
assert candidate["accepted_profiles"] == ["FULL_STACK_DEVELOPER"]
```

The following [complete-workflow increment](complete-workflow.md) implements HTML
from successfully validated specifications and adds a separate end-to-end CLI.
Those components were not introduced in the candidate-language increment itself.

## Examples and checks

```powershell
.\.venv\Scripts\python.exe tools/generate_dsl_examples.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

`data/dsl/valid/` has the eight existing scenarios represented as DSL and parsed
JSON. `data/dsl/invalid/` has five syntax/lexical errors and three semantic errors.
`data/dsl/validation.json` records expected outcomes and reasons after executing the
checks. These are synthetic/regression examples, not a blind accuracy benchmark.

Sixteen new tests verify records and contacts, empty sections, null/string names,
Unicode and escaping, all 26 skill symbols, errors, duplicates, inconsistent
classification, three simultaneous profiles, resource packaging, input immutability
and every preserved valid/invalid example. That increment brought the suite to 67 tests; the complete workflow adds 22, for 89 total.

## Sources consulted

- textX [grammar](https://textx.github.io/textX/grammar.html), for match/assignment/repetition rules.
- textX [metamodel](https://textx.github.io/textX/metamodel.html), for parser construction.
- textX [parser configuration](https://textx.github.io/textX/parser_config.html), for keyword boundaries.

Official API documentation was consulted before finalizing this increment. The
project pins and checks textX 4.4.0 rather than assuming the latest documentation
identifies the installed version.
