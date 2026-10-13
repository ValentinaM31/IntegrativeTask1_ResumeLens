# ResumeLens research poster

The research poster follows one skill claim through regular-expression extraction,
finite-state transducer normalization, deterministic finite automaton
recognition and textX validation. Three columns follow one sample from original
evidence to profile recognition, validated DSL and a candidate report. Separate
evaluation figures expose the difference between validity and exact annotations.

## Files and presentation modes

- [Vector SVG](resumelens-poster.svg): editable, scalable A1 landscape artwork.
- [Printable PDF](resumelens-poster.pdf): the same vector scene, with embedded fonts.
- [Animated walkthrough](resumelens-poster.html): a local HTML presentation with
  selectable stages, explanations, play/pause and complete-overview controls.
- `verification.json`: actual full-suite outcome, platform, date and runtime/test
  source fingerprints. It is evidence from an executed run, not an accuracy score.
- [Design notes](design-notes.md): layout, physical typography, design references
  and the limits of the readability checks.
- `layout-check.json`: generated paper dimensions, font sizes, column count,
  accents and the word count across all SVG labels.

The HTML starts in the complete overview. Automatic progression occurs only after
selecting Play walkthrough, pauses when the tab is hidden and respects reduced
motion. Stage selection scrolls to its formal-model explanation. An enlargement
control makes detailed diagrams easier to inspect on small screens. Native
buttons support keyboard use. Printing always restores the
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
.\.venv\Scripts\python.exe -m pip install reportlab
.\.venv\Scripts\python.exe tools/build_poster.py --pdf
```

ReportLab is a poster-build dependency, not an application runtime dependency. It
is installed only when rebuilding the PDF. The default print size is **A1 landscape,
841 by 594 mm**. A1 was selected to support readable figures and the suggested
display font sizes; it is not a mandatory size stated by the assignment.

An A2 desk-reading handout can be generated with:

```powershell
.\.venv\Scripts\python.exe tools/build_poster.py --pdf --paper a2
```

This option regenerates the same filenames at a smaller physical size. Its text
is smaller than the A1 display version. Run the default build again to restore
the A1 deliverables. Screen enlargement does not change the PDF's print size.
See the design notes for the intended display font roles. A physical reading test
at four to six feet has not been performed.

## Method and evidence limits

The FST illustrates the accepting JS path with abbreviated state names. Its
empty output consumes the input character; it is not an empty-input transition.
The Full Stack traces use the actual DFA state names `q0` through `q5` and
`q_dead`: the complete sample accepts, while `NODE_JS` from `q1` rejects because
the frontend group is missing. The repeated `q1` in the second trace denotes the
same state. The sink self-loop labelled Σ covers the whole alphabet. Other
transitions and group loops remain in the complete
[transducer models](../transducers.md) and [profile automata](../automata/README.md).
The builder checks the worked transitions against the exported DFA before drawing.

The highlighted JS positions refer to the complete LF Alex Sample input; the
fragment printed on the poster is a visual excerpt. The EBNF `SkillEntry` rule and
DSL accepted-profile excerpt come from the actual
[candidate-language specification](../candidate-language.md). HTML is generated
only after syntax and semantic validation. The displayed candidate outcome matches
the stored sample classification. All four profiles run through the same workflow.

The eighteen-cell grid follows the actual report's case order, left to right and
then top to bottom. Filled checks indicate exact annotation matches; outlined
crosses indicate differences. Counts, reports, evaluator sources and the runtime
are tied to hashes recorded in `verification.json`. Missing or stale verification
shows pending figures instead of successful counts.

The original [23-case extraction evaluation](../evaluation.md),
[14-case workflow regression](../workflow-evaluation.md) and separate
[18-case preannotated evaluation](../preannotated-evaluation.md) retain distinct
labels, protocols and figures. Later comparisons of the current runtime are stored
in each dataset's `visual-update/` directory. The main poster separates 14/14 exact
workflow cases from 14/18 exact preannotated cases; all 18 preannotated pipelines
are structurally valid. These measures have different meanings. The four known
interpretation errors remain visible. Detailed mention and profile metrics and
the historical extraction results stay in the linked reports.
Original freezes are preserved. No population accuracy, proficiency or hiring
outcome is inferred. Additional instructor profile specifications remain unverified.

The former partial poster is superseded; its earlier version remains recoverable
from Git history.
