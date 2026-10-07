# ResumeLens

Extract candidate information and catalog skill mentions from UTF-8 text, preserving original evidence and exclusion reasons.

## Installation

Python 3.10 or later. Runtime extraction uses the Python standard library.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Usage

```python
from resumelens import extract_resume

text = "Name: Ana\nSkills: Python, Pandas, Git.\nNo experience with TensorFlow."
result = extract_resume(text)
candidate = result["candidate"]
mentions = result["extracted_skills"]
excluded = result["excluded_mentions"]
```

The result contains candidate fields, original skill mentions, excluded mentions and warnings. Evidence uses inclusive `start` and exclusive `end` character offsets: `text[start:end] == raw`. Repeated mentions are retained. Missing names are null; other missing candidate fields are empty lists. The optional `name` parameter supplies a fallback when no explicit name line exists.

## Catalog and context

The editable catalog is `config/skills_catalog.json`; its packaged copy is `src/resumelens/skills_catalog.json`. Both contain 26 symbols and 56 aliases. Conflicting casefolded aliases are rejected. Literal boundaries prevent Java inside JavaScript and Git inside GitHub. Mentions inside recognized emails or protocol URLs are excluded.

JS/TS require an explicit skills heading and recognized-alias continuation lists. React requires skills context, a supported development/work phrase or a following framework/library word; React.js and ReactJS remain literal. Pandas requires skills context or explicit use for data analysis/processing. Capitalization alone does not decide acceptance.

Eight explicit negation patterns cover the immediate skill or a known-alias list: `no experience with`, `sin experiencia en`, `no knowledge of`, `sin conocimientos de`, `do not use`, `don't use`, `no tengo experiencia en/con`, and `no uso`. The English use forms admit an optional I. Closing punctuation and contrast delimit scope, preserving later positive mentions.

Candidate formats and regression inputs support English and Spanish. Diagnostics and project documentation are English. Education and experience retain line records without inferred company, institution or accumulated duration. Unsupported wording, other homonyms, double negation and irony remain limitations.
