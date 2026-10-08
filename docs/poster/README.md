# Extraction and normalization poster

`first-stage-poster.svg` is an English landscape A2 vector artifact covering the problem, method, FST path, extraction results, limits and references. Open in a browser/vector editor or print without losing resolution.

```powershell
.\.venv\Scripts\python.exe tools/evaluate.py
.\.venv\Scripts\python.exe tools/build_poster.py
```

This is a partial ResumeLens poster: it does not present automata, DSL, UI or HTML results. A2 was a design choice; the external linked poster guide was not verified.

The retained SVG reflects the earlier 35-test revision and metrics before the Pandas correction. It has not been regenerated. Current results are in `../test-results.md` and `../evaluation.md`. Spanish quoted alias text is an actual supported vocabulary example.
