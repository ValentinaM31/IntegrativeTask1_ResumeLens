# Literature on resume extraction and transducers

This review connects resume context, regular expressions and transduction models. Official documentation and Yu et al.'s paper were consulted; only published abstracts were available for IEEE and RINX. This is neither a systematic review nor an experimental system comparison.

## Resume extraction

**Yu, Guan and Zhou (2005)** segment resumes into blocks and extract details using context in a hybrid model. This supports considering education, experience and skills sections. ResumeLens uses explicit regex headings and does not reproduce their learned models. [ACL paper](https://aclanthology.org/P05-1062/), pp. 499–506, DOI 10.3115/1219840.1219902.

**Automated Resume Parsing A Natural Language Processing Approach (2023)** describes NER, keywords and regex patterns in its abstract. It provides context for learned versus explicit extraction; the full text was not accessed and its performance claims are not ResumeLens results. [IEEE abstract](https://ieeexplore.ieee.org/abstract/document/10334236), DOI 10.1109/CSITSS60515.2023.10334236.

**RINX (2023)** describes patterns and gazetteers combined with learned techniques for heterogeneous documents. This motivates declaring TXT and finite-catalog scope. Only the abstract was consulted; the system was not reproduced. [Publisher record](https://www.sciencedirect.com/science/article/pii/S0169023X23000629), DOI 10.1016/j.datak.2023.102202.

## Models and tools

| Source | Contribution | Application |
|---|---|---|
| Python re and HOWTO | Matches, offsets, escaping and alternatives | Evidence and alias boundaries |
| Mohri 1997 | States, alphabets and transduction relations | Formal variants/output model |
| pyformlang FST API | Initial/final states, transitions and translate | Real normalization execution |
| JSON Schema 2020-12 | Structure, types and constraints | Exchange contract |
| pyformlang finite-automaton API | Epsilon-NFA transitions and accepts() | Execute shared qualification-pattern recognizers |
| textX grammar/metamodel/parser configuration | Match rules, lists, parsing and keyword boundaries | Candidate representation syntax and validation |

Regex and FSTs provide explicit definitions and verifiable paths. Section context reduces errors in supported formats, while stress cases expose semantic limits. This is a ResumeLens design/evaluation conclusion, not evidence of superiority over learned models.

## References

- Python Software Foundation. [re](https://docs.python.org/3/library/re.html).
- Kuchling, A. M. [Regular Expression HOWTO](https://docs.python.org/3/howto/regex.html).
- Mohri, M. (1997). *Finite-State Transducers in Language and Speech Processing*. Computational Linguistics 23(2), 269–311. [ACL](https://aclanthology.org/J97-2003/).
- [pyformlang FST](https://pyformlang.readthedocs.io/en/latest/modules/fst.html).
- [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/json-schema-core).
- [pyformlang finite automata](https://pyformlang.readthedocs.io/en/latest/modules/finite_automaton.html). Consulted for the recognition increment before finalizing the implementation. Epsilon-NFA composition makes alternatives explicit; its language differs from the character-level alias transducers.

- textX [grammar](https://textx.github.io/textX/grammar.html), [metamodel](https://textx.github.io/textX/metamodel.html) and [parser configuration](https://textx.github.io/textX/parser_config.html). Consulted before finalizing the DSL increment. textX checks candidate-language syntax; separate semantic checks execute recognition to verify accepted-profile declarations. JSON Schema remains the original exchange-contract validator.
