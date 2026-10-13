# AI collaboration record

## Scope and evidence

AI assistance was used during the design, implementation, evaluation, documentation
and visual presentation of ResumeLens. This document is an English summary of
the available interaction history and repository evidence. It is not a verbatim
transcript. Original interaction records are a separate academic submission item;
the summaries below must not be substituted for original exchanges or presented
as quotations.

The work concerns a deterministic pipeline: regular expressions extract evidence,
finite-state transducers normalize skill aliases, complete DFAs recognize configured
profiles, and a textX candidate language is validated before HTML generation.
The implemented application does not call a language model to process resumes.

## Student direction documented in the interactions

The available requests show that the student set requirements and reviewed the
direction of the work. The following are summaries of those directions:

| Student direction | Effect on the project |
|---|---|
| Check the solution against the assignment and identify missing or inconsistent work. | The assignment was reviewed alongside the formal models, pipeline, tests and deliverables. |
| Use English throughout the submitted project. | User-facing messages, documentation, examples and poster text were revised in English; bilingual fixtures were retained where they test supported input. |
| Keep conversation, personal task allocation and internal planning out of project documentation. | Public documentation was organized around operation, design, methods and results. |
| Make the work easy to continue and inspect. | APIs, input/output contracts, reference examples and reproducible commands were documented. |
| Integrate the prepared fourteen-case evaluation while preserving separate datasets and expectations. | The original cases and reports were preserved, and expanded regression scoring was added with explicit provenance. |
| Improve the interface and make the poster clearer, more visual and didactic. | The interface, evidence explorer, responsive styles, poster diagrams and guided HTML walkthrough were revised. |
| Provide peer formalization and the professor's poster-design guidance for comparison, and allow a horizontal layout. | The model-to-code correspondence was checked, worked paths were generated from actual transitions, and print typography and the poster grid were revised. These references were supplied for review, without attributing their theory to the student. |
| Use deterministic automata while preserving the professional criteria. | Four directly constructed complete DFAs replaced the earlier epsilon-NFAs; original/exported language equivalence and all required-alphabet subsets were checked. |
| Perform a final coherence and functionality review. | Installed-package checks, command/API/HTTP comparisons, browser scenarios and documentation checks were recorded. |

These requests establish student direction and review priorities. They do not
establish that the students independently derived the formal models, wrote every
implementation detail or completed an independent theoretical validation.

## AI-assisted work used in the project

The recorded collaboration includes assistance with the extraction/normalization
stage, contracts and command-line processing, followed by review and targeted
revisions of the integrated recognition, DSL, HTML and browser workflows. It also
includes evidence checks, export recovery, file protection, tests, evaluation
tooling, documentation, formal-model exports and poster assets. This record does
not establish how every original module or the teammate's initial implementation
was authored. Students should review the identifiable contributions against the
committed code rather than treating generated explanations as proof of correctness.

The assistant investigated observed problems and implemented changes followed by
checks. Examples include preserving character offsets for Unicode and newline
variants, rejecting a TXT-to-JSON output that is a hard link to its input, and
adding bounded retries for transient Windows file replacement errors. A Git
attributes policy was added after reproducing reference-offset mismatches caused
by Windows checkout newline conversion. Remote CI outcomes are recorded separately
from local checks; the earlier failed run remains historical evidence.

## Evaluation provenance and limits

The three evaluations remain separate:

- The original 23-case skill-mention evaluation includes supported cases,
  historical reserved cases and stress cases. Reused cases are regression
  evidence rather than a new independent benchmark.
- The fourteen-case complete-pipeline regression integrates previously executed
  synthetic inputs. Existing references were reused and expanded labels were
  prepared with AI assistance during integration. All fourteen match the recorded
  annotation units and export checks; this is not a blind pre-run evaluation.
- The separate eighteen-case dataset contains AI-assisted synthetic texts and
  labels prepared before execution by an author familiar with the existing rules.
  Its annotation freeze was retained. All eighteen pipelines are internally
  valid, but only fourteen fully match their labels. Rust, double negation,
  job-source attribution and bounded Pandas context retain their recorded
  disagreements.

Hashes detect subsequent changes to inputs, annotations and runtime sources.
They do not independently prove authorship or when an annotation was written.
Later-regression mode reports changed sources without resetting original labels
or removing known errors. These evaluations do not establish real-applicant
accuracy or independent external-human annotation.

See [workflow evaluation](workflow-evaluation.md),
[preannotated evaluation](preannotated-evaluation.md) and
[skill-mention evaluation](evaluation.md) for methods and results.

## Executed verification

The latest recorded installed-package review on Windows with Python 3.12.14
reports **194 Python tests: 193 passed and one skipped because creating symlinks
requires permissions**. The command-line/API comparisons, eight complete
workflow bundles, eight HTTP/API/ZIP comparisons, design validation, dependency
consistency and both stored later-regression reports were checked.

The recorded Chrome-on-Windows review passed eighteen keyboard scenario groups,
including file loading, input fidelity, downloads, focus, recovery, narrow layout,
reduced motion and high contrast. Browser groups are separate from the Python
test count. Poster figures are tied to the recorded verification snapshot and
to the separate evaluation reports; visual revisions require their own inspection.

These are recorded assistant-executed checks, not a claim of independent student
execution. Full commands, platform scope, historical runs and outstanding remote
CI evidence are in [verification results](test-results.md).

## Student responsibility before submission

Each student should inspect the final code and sources, reproduce the relevant
commands, and be able to explain the regular-expression boundaries, the complete
FST seven-tuples, DFA five-tuples, canonical symbol ordering, EBNF and
semantic validation. They should also explain the difference between internal
pipeline validity and agreement with annotated expectations.

Any student-authored theoretical corrections, independent reruns or explanations
added to the submission should be supported by actual notes or interactions.
This summary does not claim that those independent activities have already been
completed. Original transcripts and any required disclosure should be submitted
according to the assignment's evidence requirements.
