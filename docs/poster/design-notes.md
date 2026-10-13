# Research poster design

The poster explains how explicit formal models turn resume wording into traceable
skill evidence and profile patterns. The main visual route is a worked skill claim;
the conclusion pairs evidence preservation with the observed interpretation limits.
The research results describe synthetic evaluations, not hiring performance.

## Layout and visual language

The A1 landscape page uses three columns as one continuous worked example:
source evidence and normalization; two deterministic recognition traces; and
validated candidate language, report and results. The six-step pipeline connects
the columns. A restrained header and a clear conclusion support a quick overview.
Short captions explain state labels, transitions, accepting states and source spans.
The FST uses abbreviated state names; the DFA traces use actual names and
transitions from the exported model. Complete executable models are linked below.

Navy and teal are the two accent colors. Dark text sits on light backgrounds.
Results include numerical labels and distinct symbols, so their meaning does not
depend on color alone. White space separates related ideas. Card backgrounds are
not treated as measured graphic coverage or measured empty space.

The design reduces long prose, retains the seven-tuple and five-tuple definitions,
and gives the accepted and rejected traces more room. Acronyms are expanded where introduced. The compact
grammar uses named terminals and nonterminals; it does not replace the complete
language specification.

## Physical typography

The default paper measures **841 by 594 mm**, in landscape orientation. The drawing
uses a 1920 by 1358 coordinate space. The drawing fits uniformly at approximately
**1.240 PDF points per scene unit** at this size. Physical font sizes must be calculated after this
scaling; an SVG font-size value alone is insufficient.

| Display role | Intended scene size | Approximate A1 PDF size |
|---|---:|---:|
| Main title | 82 | 101.7 pt |
| Authors | 49 | 60.8 pt |
| Section headings | 36 | 44.6 pt |
| Main explanatory text | 26 | 32.2 pt |

Diagram labels, formulas and references may use smaller sizes than the main text.
`layout-check.json` records the generated paper dimensions, main font roles,
two accents, three columns and the word count across all SVG labels, including
diagram tokens, formulas and references.
They are supplementary details, and their final size should be checked in the
exported PDF. The `--paper a2` option produces a desk-reading handout with smaller
physical text. Browser zoom is an inspection aid; it does not demonstrate that an
actual print is readable at a distance.

## Design reference and verification limits

The layout follows the [Central Washington University guide to creating effective
posters](https://libguides.lib.cwu.edu/creatingposters). Its suggestions include
three or four columns, a clear question, concise text, labeled graphics, a restrained
palette and attention to readers with color-vision differences. The guide suggests
80–120 point titles, 60–90 point author text, 44–80 point headings and 32–52 point
body text, depending on the poster size.

The guide also suggests approximately 20–25% text, 40–45% graphics and 30–40% empty
space. These are planning targets. No exact area percentages are claimed for this
poster: a reliable measurement would need to distinguish actual text and graphic
content from the unused interior of their containers.

A1 is a design choice for legibility. The guide asks presenters to check event
requirements; it does not establish a mandatory size for this assignment. Digital
inspection can identify clipping, collisions and missing glyphs. It cannot replace
a print reading test at four to six feet or establish that an unfamiliar reader
understands the result in five seconds. Those audience checks remain to be performed.

All poster diagrams are generated for this project. The formal-language literature
is cited on the poster and discussed in the [literature review](../literature-review.md).

## Technical evidence behind the figures

- [Transducers](../transducers.md) and the exported models in `../models/` contain
  the complete alias paths, seven-tuples and transition relations.
- [Profile recognition](../profile-recognition.md) and
  [automaton diagrams](../automata/README.md) contain the four complete DFAs with explicit rejecting sinks.
- [Candidate language](../candidate-language.md) contains the extended Backus-Naur
  form, domain-specific language examples and semantic checks.
- [Workflow evaluation](../workflow-evaluation.md) documents the fourteen-case
  annotated regression and exact export round trips.
- [Preannotated evaluation](../preannotated-evaluation.md) documents the separate
  eighteen-case dataset, exact matches, structurally valid pipelines and errors.
- [Verification results](../test-results.md) document executed checks. The poster's
  test figures come from `verification.json` and are guarded by runtime/test hashes.

The two evaluation figures use separate denominators. Structural pipeline validity
does not mean every annotation agrees. Original inputs and expectations remain
unchanged; known disagreements are reported rather than removed.

## Deterministic-model revision

The Full Stack graphic shows two traces from the complete DFA, rather than a
standalone six-state replacement for the production machine. Its seven states
include the rejecting sink. Backend requires nineteen states to retain compatible
framework choices; its full transition panels remain outside the poster so that
the printed example stays readable. The four professional patterns are preserved.

The right column connects the grammar rule to a generated DSL excerpt and the
validated HTML outcome. The evaluation grid reads actual per-case outcomes and
preserves the four disagreements. A pipeline-valid count has a different meaning
from exact annotation agreement. Results are not combined across datasets.
