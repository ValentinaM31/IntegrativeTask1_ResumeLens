"""Document the exact expressions from the extractor."""
from pathlib import Path
from resumelens.catalog import load_catalog
from resumelens.extraction import PATTERNS, skill_pattern

ROOT = Path(__file__).resolve().parents[1]
DETAILS = {'name': ('Explicit name on a labeled line; keep the first value.',
          'Name: Ana',
          'Ana Example',
          'No first-line name inference. Names are strings/null without contract offsets.'),
 'emails': ('Common user/domain format with an alphabetic suffix of at least two letters.',
            'ana@example.com',
            'ana@localhost',
            'Does not implement complete RFC syntax or reject every malformed address.'),
 'phones': ('Ten-digit Colombian mobile starting with 3; optional +57 and separators in 3-3-4 groups.',
            '+57 300-123-4567',
            '2020-2026',
            'No ownership verification; parentheses, extensions and landlines are excluded.'),
 'links': ('HTTP/HTTPS LinkedIn /in/ or GitHub URL, with optional www.',
           'https://github.com/ana',
           'https://example.com/ana',
           'No existence check; parameters and fragments are outside the matched path.'),
 'education_phrase': ('Bachelor, Master, PhD and supported Spanish degree phrases with bounded complements.',
                      'Bachelor in Computer Science.',
                      'Completed an online workshop',
                      'Does not certify degrees or cover every title; homonyms remain possible.'),
 'experience_phrase': ('Integer/decimal and a supported English or Spanish years-of-experience phrase, up to '
                       'a delimiter.',
                       '3 years of experience building apps.',
                       'Worked from 2020 to 2026',
                       'Does not add periods or convert date ranges.'),
 'skills_header': ('Skills/Technical Skills or a supported Spanish skills heading followed by a colon.',
                   'Technical Skills: JS',
                   'My JS meeting',
                   'Continues across recognized alias lists, bullets and complete single aliases.'),
 'section_header': ('Short label at line start followed by a colon; ends skills context.',
                    'Experience:',
                    'Free text without colon',
                    'Local structure rule, not general section understanding.'),
 'section_title': ('Known English/Spanish section headings, with optional colon and value.',
                   'Work Experience',
                   'A random unlabelled paragraph',
                   'Each education/experience line contributes evidence until another section; fields are '
                   'not inferred.'),
 'negation': ('Explicit negative phrase preceding the immediate skill or its list in the same clause.',
              'I do not use ',
              'I use ',
              'Eight phrases are supported; double negation and irony are not interpreted.'),
 'clause_boundary': ('Closing punctuation and contrast connectors bound negation scope.',
                     'but',
                     'and',
                     'Semicolons end a clause; dots inside React.js do not. No complete sentence parser.'),
 'react_technical': ('Development/build/work verb, up to 80 characters, then using/with or supported Spanish '
                     'equivalents immediately before React.',
                     'Developed web applications using ',
                     'I react quickly ',
                     'Only enumerated forms are supported; other technical wording may be excluded.'),
 'react_after': ('React followed by framework, library or the supported Spanish equivalent.',
                 ' framework',
                 ' quickly',
                 'No proficiency verification or general semantic interpretation.'),
 'pandas_before': ('Use/used/using or supported Spanish use verbs immediately before pandas, with optional '
                   'I.',
                   'I use ',
                   'I like ',
                   'Outside skills sections, also requires pandas_after; capitalization alone is '
                   'insufficient.'),
 'pandas_after': ('Immediate English/Spanish data analysis or processing complement.',
                  ' for data analysis',
                  ' at the zoo',
                  'Outside skills sections, also requires pandas_before. Only enumerated complements are '
                  'admitted.'),
 'url': ('HTTP/HTTPS until whitespace, comma or semicolon; filters skills inside URLs.',
         'https://example.com/Python',
         'example.com/Python',
         'Not a general URL parser; protocol-free paths are not all excluded.')}

def main():
    lines = ["# Extraction regular expressions", "",
             "Generated from `extraction.py`. `finditer` preserves matches and `span` returns character offsets. Input is not modified before extraction. A mention does not prove proficiency.", "",
             "Fixed patterns use `re.IGNORECASE | re.MULTILINE`; skills use `re.IGNORECASE`. The `value` group omits labels. Section records take priority over contained phrases to avoid duplicate evidence. Spanish expressions below are supported input vocabulary.", ""]
    for key, pattern in PATTERNS.items():
        explanation, positive, negative, limit = DETAILS[key]
        lines += [f"## {key}", "", "```regex", pattern, "```", "", explanation, "",
                  f"Accepted: `{positive}`. Rejected by this pattern: `{negative}`.", "", "Limit: " + limit, ""]
    lines += ["## Skills in all four categories", "", "```regex", skill_pattern(load_catalog()).pattern, "```", "",
              "The alternation combines 56 aliases for languages, frameworks/libraries, databases and tools/qualifications. `re.escape` makes aliases literal; descending length and boundaries restrict partial matches. JavaScript does not produce JAVA; GitHub does not produce GIT.", "",
              "Mentions inside protocol URLs or recognized emails are stored in `excluded_mentions`. Negation phrases: no experience with; sin experiencia en; no knowledge of; sin conocimientos de; do not use (optional I); don't use (optional I); no tengo experiencia en/con; no uso. Scope: immediate skill or known-alias list separated by comma, slash or and/or/y/o. Sentence-ending dot, !, ?, semicolon and but/however/pero/aunque/sin embargo end the clause. Positive mentions after contrast are retained.", "",
              "JS/TS require a skills heading and recognized-alias continuations. Unsuffixed React requires that context or react_technical/react_after; React.js/ReactJS remain literal. Pandas requires a skills section or both pandas_before and pandas_after: explicit use for data analysis/processing. Exclusions retain raw/start/end and an English reason. Capitalization does not decide acceptance.", "",
              "Limits: finite vocabulary, no general semantics for other homonyms such as Angular, possible exclusions of other technical Pandas wording, exact internal spacing, unsupported double negation and irony. A short alias may match inside an unknown space-separated phrase. Technologies outside the catalog are not discovered automatically.", "",
              "## Output and verification", "",
              "Evidence: `{raw, start, end}`, inclusive start and exclusive end; `text[start:end] == raw`. Names are strings/null without offsets. The CLI preserves CRLF and removes the BOM; other readers use their decoded string as the reference.", "",
              "Tests cover multiple records, all aliases, capitalization, negation, false positives, context and Unicode offsets. See `test-results.md`. Reference: [Python re](https://docs.python.org/3/library/re.html).", ""]
    (ROOT / "docs/regex.md").write_text("\n".join(lines), encoding="utf-8")
    print("docs/regex.md updated")


if __name__ == "__main__":
    main()
