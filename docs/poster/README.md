# ResumeLens research poster

The complete English research poster follows a worked skill list through regex
extraction, FST normalization, epsilon-NFA recognition and textX validation. It
presents the research question, model tuples, state diagrams, profile criteria,
compact DSL syntax, measured results, interpretation limits and references.

## Files and presentation modes

- [Vector SVG](resumelens-poster.svg): editable, scalable A2 landscape artwork.
- [Printable PDF](resumelens-poster.pdf): the same vector scene, with embedded fonts.
- [Animated walkthrough](resumelens-poster.html): a local HTML presentation with
  selectable stages, explanations, play/pause and complete-overview controls.
- `verification.json`: actual full-suite outcome, platform, date and runtime/test
  source fingerprints. It is evidence from an executed run, not an accuracy score.

The HTML starts in the complete overview. Automatic progression occurs only after
selecting Play walkthrough, pauses when the tab is hidden and respects reduced
motion. Native stage buttons support keyboard use. Printing always restores the
complete static poster. The PDF itself is static.

## Rebuild from measured results

Run from an installed checkout:

```powershell
.\.venv\Scripts\python.exe tools/evaluate_workflow.py --allow-changed-rules --output-dir data/workflow-evaluation/visual-update --check
.\.venv\Scripts\python.exe tools/evaluate_preannotated.py --allow-changed-rules --output-dir data/preannotated-evaluation/visual-update --check
.\.venv\Scripts\python.exe tools/verify_poster_results.py
.\.venv\Scripts\python.exe tools/build_poster.py
```

The verifier records an actual complete test run. A stale/missing source fingerprint
or a failed run prevents the builder from presenting successful test counts.
The SVG and HTML generation uses the standard library. PDF generation additionally
requires ReportLab and Arial or DejaVu TrueType fonts:

```powershell
python tools/build_poster.py --pdf
```

ReportLab is a poster-build dependency, not an application runtime dependency. It
was available in the bundled document runtime for the current export. The PDF was
rendered with Poppler and visually inspected; glyphs, diagrams, page bounds and
colors were checked. A2 is a design choice; the assignment does not specify it as
mandatory and the external poster-guide page was not independently verified.

## Method and evidence limits

The FST path and minimal accepting path are explicitly schematic. The production
machines include complete alias paths, epsilon transitions and bucket loops;
full seven-/five-tuples, tables and diagrams remain in `docs/models/` and
`docs/automata/`. The highlighted JS positions come from the LF-normalized Alex Sample
reference input. The candidate-language box is a compact valid syntax example, not a complete
copy of that resume's contact/education/experience records.

The original 23-case extraction evaluation, original 14-case workflow regression
and separate 18-case preannotated evaluation retain distinct labels, protocols and
figures. Later comparisons of the visual revision are stored in each dataset's
`visual-update/` directory. The four known interpretation errors remain visible.
Original freezes are preserved. No population accuracy, proficiency or hiring
outcome is inferred. Additional instructor profile specifications remain unverified.

The former partial poster is superseded; its earlier version remains recoverable
from Git history.
