# Assignment-profile regression bundles

These are targeted, synthetic regressions for the corrected Machine Learning
library group. Their expectations in `cases.json` are defined from the documented
rule, not offered as independently collected or blind resume evaluation.

| TXT input | Expected result | Purpose |
|---|---|---|
| scikit_only.txt | Machine Learning Engineer accepted | Scikit-learn alone fills the learning-library group, with all other groups present |
| model_without_library.txt | No profile accepted | Explicit model development and Docker do not substitute for a required library |
| negated_scikit.txt | No profile accepted | A known negated alias remains excluded instead of qualifying the candidate |

Each corresponding directory contains `first_stage.json`, `classification.json`,
`candidate.rl` and `candidate.html`. Open HTML directly in a browser. The generator
verifies both expected canonical skills and accepted profiles before saving.

```powershell
.\.venv\Scripts\python.exe tools/generate_profile_alignment_examples.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_profile_alignment.py -v
```

Stored fixtures use LF-normalized source, consistent with `data/workflow/`. The
real CLI tests additionally write exact UTF-8 BOM files with LF and CRLF and
compare with the API processing the same decoded text, including evidence offsets.
See [requirement mapping](../../docs/profile-alignment.md).
