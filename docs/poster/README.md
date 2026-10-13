# Research poster

The three-column A1 landscape poster follows one candidate through source
evidence, FST normalization, accepted/rejected DFA traces, textX validation and
HTML. It presents formal tuples, design decisions and separate evaluation results.

## Files

- [Printable vector PDF](resumelens-poster.pdf).
- [Editable SVG](resumelens-poster.svg).
- [Animated HTML walkthrough](resumelens-poster.html), with stage selection,
  play/pause, overview and enlargement. It starts in overview; animation begins
  after Play and respects reduced motion. Printing uses the complete static scene.
- `verification.json`: executed suite outcome and source/report fingerprints.
- `layout-check.json`: generated dimensions, typography and label word count.

## Rebuild

From an installed checkout:

```powershell
.\.venv\Scripts\python.exe tools/evaluate_workflow.py --allow-changed-rules --output-dir data/workflow-evaluation/visual-update --check
.\.venv\Scripts\python.exe tools/evaluate_preannotated.py --allow-changed-rules --output-dir data/preannotated-evaluation/visual-update --check
.\.venv\Scripts\python.exe tools/verify_poster_results.py
.\.venv\Scripts\python.exe tools/build_poster.py
```

The verifier runs the complete Python suite. Missing, stale or unsuccessful
verification prevents successful figures from being displayed. SVG/HTML generation
uses the standard library. PDF generation additionally requires ReportLab and
Arial or DejaVu TrueType fonts:

```powershell
.\.venv\Scripts\python.exe -m pip install reportlab
.\.venv\Scripts\python.exe tools/build_poster.py --pdf
```

ReportLab is needed only to rebuild the PDF. The default size is **841 × 594 mm**;
A1 is a legibility choice, not an assignment requirement. `--paper a2` produces a
smaller handout at the same filenames; rebuild with the default to restore A1.

## Visual design

Three columns, navy/teal accents, dark text on light backgrounds and short labeled
graphics follow the [CWU poster guide](https://libguides.lib.cwu.edu/creatingposters).
Checks/crosses and numbers distinguish results independently of color. Approximate
A1 physical font sizes are 101.7 pt for the title, 60.8 pt for authors, 44.6 pt for
headings and 32.2 pt for main text; diagram labels and references are smaller.
No exact text/graphic/empty-space percentages or viewing-distance readability are
claimed. Digital inspection checks clipping and glyphs; a physical print check remains useful.

## Evidence and interpretation

The accepting JS FST path abbreviates state names; empty output consumes an input
character. The two Full Stack traces use actual DFA states `q0`–`q5` and `q_dead`.
`NODE_JS` from `q1` enters the sink when frontend evidence is missing. The builder
checks these transitions against the exported DFA. Full models remain in
[transducers](../transducers.md) and [profile automata](../automata/README.md).
The printed resume fragment is an excerpt; its highlighted span addresses the
complete LF sample. The EBNF/DSL example comes from the actual
[candidate language](../candidate-language.md), and HTML follows its validation.

The grid follows the 18-case report order and displays all four disagreements:
**14/18 exact annotation matches**, with **18/18 structurally valid pipelines**.
The separate workflow regression shows **14/14 exact matches**. These results are
not combined. Methods and detailed figures are in the
[18-case evaluation](../preannotated-evaluation.md),
[14-case regression](../workflow-evaluation.md) and
[verification results](../test-results.md), which also retain the original
23-case extraction method. Input/annotation freezes remain unchanged. Selected
synthetic results do not measure population accuracy, proficiency or hiring outcomes.

All diagrams are generated for this project. The poster cites formal-language
sources discussed in the [literature review](../literature-review.md).
