# Extraction regular expressions

Generated from `extraction.py`. `finditer` preserves matches and `span` returns character offsets. Input is not modified before extraction. A mention does not prove proficiency.

Fixed patterns use `re.IGNORECASE | re.MULTILINE`; skills use `re.IGNORECASE`. The `value` group omits labels. Section records take priority over contained phrases to avoid duplicate evidence. Spanish expressions below are supported input vocabulary.

## name

```regex
^[ \t]*(?:Name|Nombre)[ \t]*:[ \t]*(?P<value>[^\r\n]+)
```

Explicit name on a labeled line; keep the first value.

Accepted: `Name: Ana`. Rejected by this pattern: `Ana Example`.

Limit: No first-line name inference. Names are strings/null without contract offsets.

## emails

```regex
(?<![\w.+-])[A-Z0-9_%+-]+(?:\.[A-Z0-9_%+-]+)*@(?:[A-Z0-9](?:[A-Z0-9-]*[A-Z0-9])?\.)+[A-Z]{2,}(?![\w-]|\.[A-Z0-9])
```

Common user/domain format with an alphabetic suffix of at least two letters.

Accepted: `ana@example.com`. Rejected by this pattern: `ana@localhost`.

Limit: Does not implement complete RFC syntax or reject every malformed address.

## phones

```regex
(?<![\w+\d])(?:\+57[ -]?)?3\d{2}[ -]?\d{3}[ -]?\d{4}(?![\w\d])
```

Ten-digit Colombian mobile starting with 3; optional +57 and separators in 3-3-4 groups.

Accepted: `+57 300-123-4567`. Rejected by this pattern: `2020-2026`.

Limit: No ownership verification; parentheses, extensions and landlines are excluded.

## links

```regex
https?://(?:www\.)?(?:linkedin\.com/in|github\.com)/[A-Z0-9_-]+(?:/[A-Z0-9_.-]+)*(?![\w/-])
```

HTTP/HTTPS LinkedIn /in/ or GitHub URL, with optional www.

Accepted: `https://github.com/ana`. Rejected by this pattern: `https://example.com/ana`.

Limit: No existence check; parameters and fragments are outside the matched path.

## education_phrase

```regex
(?<!\w)(?:(?:Bachelor|Master)(?:'s)?(?: degree(?: (?:in|of) [^\r\n.;]+)?| (?:in|of) [^\r\n.;]+)|PhD(?: in [^\r\n.;]+)?|Ingeniería(?: de| en)? [^\r\n.;]+|Maestría(?: de| en)? [^\r\n.;]+|Doctorado(?: de| en)? [^\r\n.;]+)(?!\w)
```

Bachelor, Master, PhD and supported Spanish degree phrases with bounded complements.

Accepted: `Bachelor in Computer Science.`. Rejected by this pattern: `Completed an online workshop`.

Limit: Does not certify degrees or cover every title; homonyms remain possible.

## experience_phrase

```regex
(?<!\w)\d+(?:[.,]\d+)?[ \t]+(?:years? of experience|años? de experiencia)(?:[^\r\n.;]*)(?!\w)
```

Integer/decimal and a supported English or Spanish years-of-experience phrase, up to a delimiter.

Accepted: `3 years of experience building apps.`. Rejected by this pattern: `Worked from 2020 to 2026`.

Limit: Does not add periods or convert date ranges.

## skills_header

```regex
^[ \t]*(?:Technical Skills|Skills|Habilidades(?: técnicas)?|Tecnologías|Tecnologias|Competencias)[ \t]*:
```

Skills/Technical Skills or a supported Spanish skills heading followed by a colon.

Accepted: `Technical Skills: JS`. Rejected by this pattern: `My JS meeting`.

Limit: Continues across recognized alias lists, bullets and complete single aliases.

## section_header

```regex
^[ \t]*(?:[A-ZÁÉÍÓÚÑ][\w ÁÉÍÓÚÑáéíóúñ/-]{0,45})[ \t]*:
```

Short label at line start followed by a colon; ends skills context.

Accepted: `Experience:`. Rejected by this pattern: `Free text without colon`.

Limit: Local structure rule, not general section understanding.

## section_title

```regex
^[ \t]*(?P<label>Education|Educación|Educacion|Degree|Título|Titulo|Experience|Experiencia|Work Experience|Professional Experience|Experiencia laboral|Technical Skills|Skills|Habilidades(?: técnicas)?|Tecnologías|Tecnologias|Competencias|Projects|Proyectos|Summary|Resumen|Contact|Contacto|Languages|Idiomas|Certifications|Certificaciones)(?:[ \t]*:[ \t]*(?P<value>[^\r\n]*))?[ \t]*$
```

Known English/Spanish section headings, with optional colon and value.

Accepted: `Work Experience`. Rejected by this pattern: `A random unlabelled paragraph`.

Limit: Each education/experience line contributes evidence until another section; fields are not inferred.

## negation

```regex
(?<!\w)(?:no experience with|sin experiencia en|no knowledge of|sin conocimientos de|(?:I[ \t]+)?do not use|(?:I[ \t]+)?don't use|no tengo experiencia (?:en|con)|no uso)[ \t]+
```

Explicit negative phrase preceding the immediate skill or its list in the same clause.

Accepted: `I do not use `. Rejected by this pattern: `I use `.

Limit: Eight phrases are supported; double negation and irony are not interpreted.

## clause_boundary

```regex
[!?;\r\n]|\.(?=[ \t]|$)|(?<!\w)(?:but|however|pero|aunque|sin[ \t]+embargo)(?!\w)
```

Closing punctuation and contrast connectors bound negation scope.

Accepted: `but`. Rejected by this pattern: `and`.

Limit: Semicolons end a clause; dots inside React.js do not. No complete sentence parser.

## react_technical

```regex
(?<!\w)(?:develop(?:ed|ing|s)?|build(?:ing|s)?|built|work(?:ed|ing|s)?|desarroll(?:o|é|amos|ando)|trabaj(?:o|é|amos|ando))[^\r\n.!?;]{0,80}(?<!\w)(?:using|with|usando|con)[ \t]+$
```

Development/build/work verb, up to 80 characters, then using/with or supported Spanish equivalents immediately before React.

Accepted: `Developed web applications using `. Rejected by this pattern: `I react quickly `.

Limit: Only enumerated forms are supported; other technical wording may be excluded.

## react_after

```regex
^[ \t]+(?:framework|library|biblioteca)(?!\w)
```

React followed by framework, library or the supported Spanish equivalent.

Accepted: ` framework`. Rejected by this pattern: ` quickly`.

Limit: No proficiency verification or general semantic interpretation.

## pandas_before

```regex
(?<!\w)(?:I[ \t]+)?(?:use|used|using|uso|usé|usando|utilizo|utilicé|utilizando)[ \t]+$
```

Use/used/using or supported Spanish use verbs immediately before pandas, with optional I.

Accepted: `I use `. Rejected by this pattern: `I like `.

Limit: Outside skills sections, also requires pandas_after; capitalization alone is insufficient.

## pandas_after

```regex
^[ \t]+(?:for[ \t]+(?:data[ \t]+(?:analysis|processing)|processing[ \t]+data|analysing[ \t]+data)|para[ \t]+(?:procesar[ \t]+datos|analizar[ \t]+datos|análisis[ \t]+de[ \t]+datos|procesamiento[ \t]+de[ \t]+datos))(?!\w)
```

Immediate English/Spanish data analysis or processing complement.

Accepted: ` for data analysis`. Rejected by this pattern: ` at the zoo`.

Limit: Outside skills sections, also requires pandas_before. Only enumerated complements are admitted.

## url

```regex
https?://[^\s,;]+
```

HTTP/HTTPS until whitespace, comma or semicolon; filters skills inside URLs.

Accepted: `https://example.com/Python`. Rejected by this pattern: `example.com/Python`.

Limit: Not a general URL parser; protocol-free paths are not all excluded.

## Skills in all four categories

```regex
(?<![\w.+-])(?:extracción\ transformación\ carga|Structured\ Query\ Language|machine\ learning\ models|extract\ transform\ load|modelos\ predictivos|predictive\ models|Apache\ Airflow|Docker\ Desktop|Apache\ Spark|scikit\ learn|Scikit\-learn|RESTful\ API|Spring\ Boot|Tensor\ Flow|Type\ Script|ECMAScript|JavaScript|PostgreSQL|SpringBoot|TensorFlow|TypeScript|REST\ APIs|Mongo\ DB|Postgres|Py\ Torch|Python\ 3|React\.js|REST\ API|Airflow|Angular|Git\ SCM|Java\ SE|MongoDB|Node\.js|Python3|PyTorch|ReactJS|sklearn|Django|Docker|NodeJS|Num\ Py|Pandas|Python|Vue\.js|MySQL|NumPy|React|VueJS|Java|ETL|Git|SQL|Vue|JS|TS)(?![\w+-]|\.[\w])
```

The alternation combines 56 aliases for languages, frameworks/libraries, databases and tools/qualifications. `re.escape` makes aliases literal; descending length and boundaries restrict partial matches. JavaScript does not produce JAVA; GitHub does not produce GIT.

Mentions inside protocol URLs or recognized emails are stored in `excluded_mentions`. Negation phrases: no experience with; sin experiencia en; no knowledge of; sin conocimientos de; do not use (optional I); don't use (optional I); no tengo experiencia en/con; no uso. Scope: immediate skill or known-alias list separated by comma, slash or and/or/y/o. Sentence-ending dot, !, ?, semicolon and but/however/pero/aunque/sin embargo end the clause. Positive mentions after contrast are retained.

JS/TS require a skills heading and recognized-alias continuations. Unsuffixed React requires that context or react_technical/react_after; React.js/ReactJS remain literal. Pandas requires a skills section or both pandas_before and pandas_after: explicit use for data analysis/processing. Exclusions retain raw/start/end and an English reason. Capitalization does not decide acceptance.

Limits: finite vocabulary, no general semantics for other homonyms such as Angular, possible exclusions of other technical Pandas wording, exact internal spacing, unsupported double negation and irony. A short alias may match inside an unknown space-separated phrase. Technologies outside the catalog are not discovered automatically.

## Output and verification

Evidence: `{raw, start, end}`, inclusive start and exclusive end; `text[start:end] == raw`. Names are strings/null without offsets. The CLI preserves CRLF and removes the BOM; other readers use their decoded string as the reference.

Tests cover multiple records, all aliases, capitalization, negation, false positives, context and Unicode offsets. See `test-results.md`. Reference: [Python re](https://docs.python.org/3/library/re.html).
