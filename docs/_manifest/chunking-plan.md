# Chunking Plan

Per-source reference for downstream extraction (Stage 3 of `procedure.md`). Each source-block lists which chapters/sections to carve out of `full.pdf`, with verified page ranges and project-component tags.

The per-source pipeline that produces this file is documented in `chunking-workflow.md`. The verifier that gates each iteration is `verify_chunking_plan.py`.

## Format

Each source is a `### {slug}` heading followed by an indented YAML-fragment body. Top-level fields:

- `pdf_total_pages` — integer; matches `pdfinfo full.pdf`'s `Pages:` line.
- `toc_path`, `pdf_path` — repo-relative paths.
- `whole_document` — boolean. `true` for journal articles and single-essay sources.
- `chunks` — list of chunk dicts. Each chunk has `id`, `title`, `page_scheme` (one of `book`, `pdf`, `bekker`, `section_number`), `page_start`, `page_end`, `components` (list of `{exp, m1, m2, m3, m4, proc}`), `verified` (bool), and `rationale` (≤ 15 words).
- `warnings` — optional list; only present when one or more chunks have `verified: false`.

Component codes:

| Code | Deliverable |
|---|---|
| `exp` | Exploratory-default interlocutor (Claude Code CLAUDE.md) |
| `m1` | Pragma-dialectical critic skill |
| `m2` | Hermeneutic close-reading critic skill |
| `m3` | Skinnerian historiographical critic skill |
| `m4` | Dennettian intuition-pump critic skill |
| `proc` | Research procedure (claude.ai project) |

## Sources

<!-- per-source blocks appended below this line, slug-alphabetical -->

### aristotle-metaphysics
pdf_total_pages: 1015
toc_path: docs/sources/aristotle-metaphysics/toc.md
pdf_path: docs/sources/aristotle-metaphysics/full.pdf
whole_document: false
chunks:
  - id: aristotle-metaphysics/book-beta
    title: Book Beta (III) — the fourteen aporiai
    page_scheme: bekker
    page_start: '995a24'
    page_end: '1003a17'
    pdf_page_start: 106
    pdf_page_end: 124
    components: [exp]
    verified: true
    rationale: Locus classicus for aporia/diaporesai/euporia; procedural template for exploratory-default disposition.

### arksey-omalley-2005-scoping-studies
pdf_total_pages: 15
toc_path: docs/sources/arksey-omalley-2005-scoping-studies/toc.md
pdf_path: docs/sources/arksey-omalley-2005-scoping-studies/full.pdf
whole_document: true
chunks:
  - id: arksey-omalley-2005-scoping-studies/whole
    title: Scoping Studies: Towards a Methodological Framework
    page_scheme: pdf
    page_start: 1
    page_end: 15
    components: [proc]
    verified: true
    rationale: Foundational scoping-review framework; 14-page article, treat as single unit per manifest.

### bohm-1996-on-dialogue
pdf_total_pages: 132
toc_path: docs/sources/bohm-1996-on-dialogue/toc.md
pdf_path: docs/sources/bohm-1996-on-dialogue/full.pdf
whole_document: false
warnings: ch5/ch6 boundary off-by-one vs toc.md; PDF p. 92 (book p. 72) is Ch. 5 spillover prose; Ch. 6 heading is on PDF p. 93 (book p. 73). Ch. 5 is 4 pages, not 3.
chunks:
  - id: bohm-1996-on-dialogue/ch2-on-dialogue
    title: On Dialogue
    page_scheme: book
    page_start: 6
    page_end: 47
    pdf_page_start: 26
    pdf_page_end: 67
    components: [exp]
    verified: true
    rationale: Canonical dialogue/discussion distinction; no pre-set agenda; attending to one's blocks.
  - id: bohm-1996-on-dialogue/ch5-observer-observed
    title: The Observer and the Observed
    page_scheme: book
    page_start: 69
    page_end: 71
    pdf_page_start: 89
    pdf_page_end: 91
    components: [exp]
    verified: false
    rationale: Discipline of noticing how assumptions structure observation; anti-sycophancy adjacent.
  - id: bohm-1996-on-dialogue/ch6-suspension-proprioception
    title: Suspension, the Body, and Proprioception
    page_scheme: book
    page_start: 72
    page_end: 83
    pdf_page_start: 92
    pdf_page_end: 103
    components: [exp]
    verified: false
    rationale: Acting-on vs. suppressing vs. suspending a reaction; most operationally specific chapter.

### booth-sutton-2022-systematic-approaches
pdf_total_pages: 425
toc_path: docs/sources/booth-sutton-2022-systematic-approaches/toc.md
pdf_path: docs/sources/booth-sutton-2022-systematic-approaches/full.pdf
whole_document: false
warnings: Ch.10 page_end revised from book p.350 to p.340 (PDF 375); References begin at book p.341/PDF 376, so original draft end-page included reference list.
chunks:
  - id: booth-sutton-2022-systematic-approaches/ch4-defining-scope
    title: Defining Your Scope (PICO, SPIDER, protocols)
    page_scheme: book
    page_start: 93
    page_end: 123
    pdf_page_start: 128
    pdf_page_end: 158
    components: [proc]
    verified: true
    rationale: Manifest-mandated SPIDER chapter; question-formulation frameworks for procedure.
  - id: booth-sutton-2022-systematic-approaches/ch5-searching-literature
    title: Searching the Literature (eight-stage search process)
    page_scheme: book
    page_start: 124
    page_end: 157
    pdf_page_start: 159
    pdf_page_end: 192
    components: [proc]
    verified: true
    rationale: Manifest-mandated search-strategy chapter; core procedural directives.
  - id: booth-sutton-2022-systematic-approaches/ch6-assessing-evidence
    title: Assessing the Evidence Base (quality, validity, hierarchies)
    page_scheme: book
    page_start: 158
    page_end: 193
    pdf_page_start: 193
    pdf_page_end: 228
    components: [proc]
    verified: true
    rationale: Source-quality criteria for procedure's appraisal stage.
  - id: booth-sutton-2022-systematic-approaches/ch8-qualitative-synthesis
    title: Synthesising and Analysing Qualitative Studies
    page_scheme: book
    page_start: 235
    page_end: 273
    pdf_page_start: 270
    pdf_page_end: 308
    components: [proc]
    verified: true
    rationale: Thematic/framework synthesis methods adaptable to philosophical synthesis.
  - id: booth-sutton-2022-systematic-approaches/ch10-writing-prisma
    title: Writing Up, Presenting and Disseminating (PRISMA 2020, PRISMA-ScR)
    page_scheme: book
    page_start: 309
    page_end: 340
    pdf_page_start: 344
    pdf_page_end: 375
    components: [proc]
    verified: true
    rationale: PRISMA-ScR reporting standard structurally models the procedure document.

### cappelen-gendler-hawthorne-2016-oxford-handbook
pdf_total_pages: 769
toc_path: docs/sources/cappelen-gendler-hawthorne-2016-oxford-handbook/toc.md
pdf_path: docs/sources/cappelen-gendler-hawthorne-2016-oxford-handbook/full.pdf
whole_document: false
chunks:
  - id: cappelen-gendler-hawthorne-2016-oxford-handbook/ch1-dever-what-is-philosophical-methodology
    title: Dever, "What is Philosophical Methodology?"
    page_scheme: book
    page_start: 3
    page_end: 26
    pdf_page_start: 20
    pdf_page_end: 43
    components: [proc]
    verified: true
    rationale: Meta-methodology framing; anchors the volume's procedural vocabulary.
  - id: cappelen-gendler-hawthorne-2016-oxford-handbook/ch2-normore-methodology-history-of-philosophy
    title: Normore, "The Methodology of the History of Philosophy"
    page_scheme: book
    page_start: 27
    page_end: 48
    pdf_page_start: 44
    pdf_page_end: 65
    components: [proc, m3]
    verified: true
    rationale: Historiography of philosophy; direct feed for Skinnerian critic.
  - id: cappelen-gendler-hawthorne-2016-oxford-handbook/ch19-hajek-philosophical-heuristics
    title: Hájek, "Philosophical Heuristics and Methodology"
    page_scheme: book
    page_start: 348
    page_end: 373
    pdf_page_start: 365
    pdf_page_end: 390
    components: [proc]
    verified: true
    rationale: Concrete procedural heuristics; most directly actionable for research procedure.
  - id: cappelen-gendler-hawthorne-2016-oxford-handbook/ch20-kelly-disagreement-in-philosophy
    title: Kelly, "Disagreement in Philosophy: Its Epistemic Significance"
    page_scheme: book
    page_start: 374
    page_end: 394
    pdf_page_start: 391
    pdf_page_end: 411
    components: [proc]
    verified: true
    rationale: Disagreement epistemics; governs how procedure handles peer dissent.
  - id: cappelen-gendler-hawthorne-2016-oxford-handbook/ch26-beiser-history-of-ideas-defense
    title: Beiser, "History of Ideas: A Defense"
    page_scheme: book
    page_start: 505
    page_end: 524
    pdf_page_start: 522
    pdf_page_end: 541
    components: [proc, m3]
    verified: true
    rationale: Manifest-mandated; defends history-of-ideas method, pairs with Skinnerian critic.
  - id: cappelen-gendler-hawthorne-2016-oxford-handbook/ch27-list-valentini-methodology-political-theory
    title: List & Valentini, "Methodology of Political Theory"
    page_scheme: book
    page_start: 525
    page_end: 553
    pdf_page_start: 542
    pdf_page_end: 570
    components: [proc]
    verified: true
    rationale: Manifest-mandated; methodology survey for normative theorizing.

### cavell-1979-claim-of-reason
pdf_total_pages: 538
toc_path: docs/sources/cavell-1979-claim-of-reason/toc.md
pdf_path: docs/sources/cavell-1979-claim-of-reason/full.pdf
whole_document: false
chunks:
  - id: cavell-1979-claim-of-reason/ch13a-framing-and-seeing-humans
    title: Framing acknowledgment/avoidance through "perfecting an automaton"
    page_scheme: book
    page_start: 329
    page_end: 407
    pdf_page_start: 356
    pdf_page_end: 434
    components: [exp]
    verified: true
    rationale: Opens Part IV; private language, allegory of words, seeing humans, automaton.
  - id: cavell-1979-claim-of-reason/ch13b-feelings-and-confinement
    title: Feelings, the Outsider, confinement and exposure
    page_scheme: book
    page_start: 408
    page_end: 436
    pdf_page_start: 435
    pdf_page_end: 463
    components: [exp]
    verified: true
    rationale: Affective register of knowing others; horror, exposure, unrestricted acknowledgment.
  - id: cavell-1979-claim-of-reason/ch13c-living-skepticism-asymmetries
    title: Living skepticism, asymmetries, Friend and Confessor
    page_scheme: book
    page_start: 437
    page_end: 462
    pdf_page_start: 464
    pdf_page_end: 489
    components: [exp]
    verified: true
    rationale: Core existential thesis; passive recital, asymmetries, relational vocabulary.
  - id: cavell-1979-claim-of-reason/ch13d-romanticism-and-vanishing
    title: Romanticism, narcissism, vanishing of the human
    page_scheme: book
    page_start: 463
    page_end: 496
    pdf_page_start: 490
    pdf_page_end: 523
    components: [exp]
    verified: true
    rationale: Closing arc; history of the problem, literature as Outsider's knowledge.

### davidson-1984-inquiries
pdf_total_pages: 315
toc_path: docs/sources/davidson-1984-inquiries/toc.md
pdf_path: docs/sources/davidson-1984-inquiries/full.pdf
whole_document: false
warnings: PDF is image-only (no embedded text); verification done visually, not via pdftotext. OCR required before Stage 3 extraction.
chunks:
  - id: davidson-1984-inquiries/introduction
    title: Introduction
    page_scheme: pdf
    page_start: 16
    page_end: 23
    pdf_page_start: 16
    pdf_page_end: 23
    components: [proc, exp]
    verified: true
    rationale: Most concise statement of the principle of charity per toc.
  - id: davidson-1984-inquiries/radical-interpretation
    title: Radical Interpretation (Essay 9)
    page_scheme: book
    page_start: 125
    page_end: 140
    pdf_page_start: 148
    pdf_page_end: 163
    components: [proc, exp]
    verified: true
    rationale: Foundational charity-driven interpretation procedure; manifest-mandated for both deliverables.
  - id: davidson-1984-inquiries/conceptual-scheme
    title: On the Very Idea of a Conceptual Scheme (Essay 13)
    page_scheme: book
    page_start: 183
    page_end: 198
    pdf_page_start: 206
    pdf_page_end: 221
    components: [proc, exp]
    verified: true
    rationale: Argues against scheme-content dualism; manifest-mandated for both deliverables.

### dennett-1991-consciousness-explained
pdf_total_pages: 530
toc_path: docs/sources/dennett-1991-consciousness-explained/toc.md
pdf_path: docs/sources/dennett-1991-consciousness-explained/full.pdf
whole_document: false
chunks:
  - id: dennett-1991-consciousness-explained/ch4-method-phenomenology
    title: A Method for Phenomenology
    page_scheme: book
    page_start: 66
    page_end: 100
    pdf_page_start: 81
    pdf_page_end: 115
    components: [m4]
    verified: true
    rationale: Heterophenomenology methodology — operational key for reading later chapters.
  - id: dennett-1991-consciousness-explained/ch10-show-and-tell
    title: Show and Tell
    page_scheme: book
    page_start: 285
    page_end: 320
    pdf_page_start: 300
    pdf_page_end: 335
    components: [m4]
    verified: true
    rationale: Worked examples of report-versus-experience dissociation.
  - id: dennett-1991-consciousness-explained/ch11-dismantling-witness-protection
    title: Dismantling the Witness Protection Program
    page_scheme: book
    page_start: 321
    page_end: 368
    pdf_page_start: 336
    pdf_page_end: 383
    components: [m4]
    verified: true
    rationale: Cartesian Theater dismantled; Multiple Drafts argued positively.
  - id: dennett-1991-consciousness-explained/ch12-qualia-disqualified
    title: Qualia Disqualified
    page_scheme: book
    page_start: 369
    page_end: 411
    pdf_page_start: 384
    pdf_page_end: 426
    components: [m4]
    verified: true
    rationale: Canonical anti-qualia arguments and intuition pumps.
  - id: dennett-1991-consciousness-explained/ch14-consciousness-imagined
    title: Consciousness Imagined
    page_scheme: book
    page_start: 431
    page_end: 456
    pdf_page_start: 446
    pdf_page_end: 471
    components: [m4]
    verified: true
    rationale: Zombie thought experiments dismantled; imaginability-versus-possibility.

### dennett-2013-intuition-pumps
pdf_total_pages: 506
toc_path: docs/sources/dennett-2013-intuition-pumps/toc.md
pdf_path: docs/sources/dennett-2013-intuition-pumps/full.pdf
whole_document: false
chunks:
  - id: dennett-2013-intuition-pumps/part-ii-thinking-tools
    title: Part II — A Dozen General Thinking Tools (Chs. 1–12)
    page_scheme: pdf
    page_start: 23
    page_end: 59
    pdf_page_start: 23
    pdf_page_end: 59
    components: [exp, m4]
    verified: true
    rationale: Procedural core; Rapoport, Sturgeon, "surely", deepity — direct diagnostics.
  - id: dennett-2013-intuition-pumps/part-vii-consciousness
    title: Part VII — Tools for Thinking about Consciousness (Chs. 53–64)
    page_scheme: pdf
    page_start: 248
    page_end: 310
    pdf_page_start: 248
    pdf_page_end: 310
    components: [m4]
    verified: true
    rationale: Applied stress-tests: Chinese Room, Mary, zombies, heterophenomenology.
  - id: dennett-2013-intuition-pumps/part-viii-free-will
    title: Part VIII — Tools for Thinking about Free Will (Chs. 65–73)
    page_scheme: pdf
    page_start: 311
    page_end: 359
    pdf_page_start: 311
    pdf_page_end: 359
    components: [m4]
    verified: true
    rationale: Knob-turning demos: Game of Life, Boys from Brazil.
  - id: dennett-2013-intuition-pumps/part-ix-disposition
    title: Part IX subset — Chs. 75–76 (Naïve Auto-anthropology; Chmess)
    page_scheme: pdf
    page_start: 364
    page_end: 372
    pdf_page_start: 364
    pdf_page_end: 372
    components: [exp]
    verified: true
    rationale: Disposition pieces for exploratory mode; small, combinable.

### eemeren-grootendorst-2004-systematic-theory
pdf_total_pages: 226
toc_path: docs/sources/eemeren-grootendorst-2004-systematic-theory/toc.md
pdf_path: docs/sources/eemeren-grootendorst-2004-systematic-theory/full.pdf
whole_document: false
chunks:
  - id: eemeren-grootendorst-2004-systematic-theory/ch3-critical-discussion-model
    title: A Model of a Critical Discussion (four-stage dialectical model)
    page_scheme: book
    page_start: 42
    page_end: 68
    pdf_page_start: 52
    pdf_page_end: 78
    components: [m1]
    verified: true
    rationale: Defines the ideal model whose stages frame the rules and fallacies.
  - id: eemeren-grootendorst-2004-systematic-theory/ch6-ten-rules
    title: Rules for a Critical Discussion (the ten rules)
    page_scheme: book
    page_start: 123
    page_end: 157
    pdf_page_start: 133
    pdf_page_end: 167
    components: [m1]
    verified: true
    rationale: Core normative rules; primary directive source for argumentation conduct.
  - id: eemeren-grootendorst-2004-systematic-theory/ch7-fallacies-as-violations
    title: Fallacies as Violations of the Rules for a Critical Discussion
    page_scheme: book
    page_start: 158
    page_end: 186
    pdf_page_start: 168
    pdf_page_end: 196
    components: [m1]
    verified: true
    rationale: Maps each fallacy to a rule violation; supplies anti-patterns.
  - id: eemeren-grootendorst-2004-systematic-theory/ch8-code-of-conduct
    title: Code of Conduct for Reasonable Discussants (ten commandments)
    page_scheme: book
    page_start: 187
    page_end: 196
    pdf_page_start: 197
    pdf_page_end: 206
    components: [m1]
    verified: true
    rationale: Compressed imperative restatement; reads as candidate directives directly.

### eemeren-grootendorst-snoeck-henkemans-2002-argumentation-aep
pdf_total_pages: 210
toc_path: docs/sources/eemeren-grootendorst-snoeck-henkemans-2002-argumentation-aep/toc.md
pdf_path: docs/sources/eemeren-grootendorst-snoeck-henkemans-2002-argumentation-aep/full.pdf
whole_document: false
chunks:
  - id: eemeren-grootendorst-snoeck-henkemans-2002-argumentation-aep/ch1-differences-of-opinion
    title: Differences of Opinion
    page_scheme: book
    page_start: 3
    page_end: 22
    pdf_page_start: 18
    pdf_page_end: 37
    components: [m1]
    verified: true
    rationale: Recognizing what is in dispute; trigger condition for the pragma-dialectical procedure.
  - id: eemeren-grootendorst-snoeck-henkemans-2002-argumentation-aep/ch2-argumentation-and-discussion
    title: Argumentation and Discussion
    page_scheme: book
    page_start: 23
    page_end: 36
    pdf_page_start: 38
    pdf_page_end: 51
    components: [m1]
    verified: true
    rationale: Four-stage critical-discussion model (confrontation, opening, argumentation, concluding).
  - id: eemeren-grootendorst-snoeck-henkemans-2002-argumentation-aep/ch4-unexpressed-standpoints-and-premises
    title: Unexpressed Standpoints and Unexpressed Premises
    page_scheme: book
    page_start: 49
    page_end: 62
    pdf_page_start: 64
    pdf_page_end: 77
    components: [m1]
    verified: true
    rationale: Reconstruction moves surfacing implicit content; most directly extractable dialogical-move chapter.
  - id: eemeren-grootendorst-snoeck-henkemans-2002-argumentation-aep/ch5-structure-of-argumentation
    title: The Structure of Argumentation
    page_scheme: book
    page_start: 63
    page_end: 90
    pdf_page_start: 78
    pdf_page_end: 105
    components: [m1]
    verified: true
    rationale: Multiple/coordinative/subordinative analysis; schematic representation of complex argumentation.
  - id: eemeren-grootendorst-snoeck-henkemans-2002-argumentation-aep/ch7-fallacies-1
    title: Fallacies (1)
    page_scheme: book
    page_start: 109
    page_end: 126
    pdf_page_start: 124
    pdf_page_end: 141
    components: [m1]
    verified: true
    rationale: Fallacies as violations of rules 1–5 (freedom, burden, standpoint, relevance, unexpressed premise).
  - id: eemeren-grootendorst-snoeck-henkemans-2002-argumentation-aep/ch8-fallacies-2
    title: Fallacies (2)
    page_scheme: book
    page_start: 127
    page_end: 156
    pdf_page_start: 142
    pdf_page_end: 171
    components: [m1]
    verified: true
    rationale: Fallacies as violations of rules 6–10 (starting point, scheme, validity, closure, usage).
warnings: PDF is image-only (no embedded text); OCR required before Stage 3; Subtask 2 must verify pdf-page mapping visually.

### gadamer-1960-truth-and-method
pdf_total_pages: 639
toc_path: docs/sources/gadamer-1960-truth-and-method/toc.md
pdf_path: docs/sources/gadamer-1960-truth-and-method/full.pdf
whole_document: false
chunks:
  - id: gadamer-1960-truth-and-method/ch4-s1-prejudices
    title: Ch. 4 §1 — Historicity of understanding; prejudices as conditions
    page_scheme: book
    page_start: 267
    page_end: 304
    pdf_page_start: 305
    pdf_page_end: 342
    components: [m2, exp]
    verified: true
    rationale: Hermeneutic circle, prejudice/authority/tradition, Wirkungsgeschichte — core of both manifest targets.
  - id: gadamer-1960-truth-and-method/ch4-s2-application
    title: Ch. 4 §2 — Recovery of the fundamental hermeneutic problem (application)
    page_scheme: book
    page_start: 305
    page_end: 334
    pdf_page_start: 343
    pdf_page_end: 372
    components: [m2]
    verified: true
    rationale: Application problem, Aristotelian phronesis, legal hermeneutics as exemplar.
  - id: gadamer-1960-truth-and-method/ch4-s3-effected-consciousness
    title: Ch. 4 §3 — Historically effected consciousness; logic of question and answer
    page_scheme: book
    page_start: 335
    page_end: 383
    pdf_page_start: 373
    pdf_page_end: 419
    components: [m2, exp]
    verified: true
    rationale: Erfahrung, fusion of horizons, Platonic dialectic — primary dialogical-move source.
  - id: gadamer-1960-truth-and-method/ch5-s1-language-medium
    title: Ch. 5 §1 — Language as the medium of hermeneutic experience
    page_scheme: book
    page_start: 384
    page_end: 404
    pdf_page_start: 422
    pdf_page_end: 442
    components: [m2]
    verified: true
    rationale: Linguistic-ontological extension; secondary depth for hermeneutic critic.

### gendler-2010-intuition-imagination-philosophical-methodology
pdf_total_pages: 373
toc_path: docs/sources/gendler-2010-intuition-imagination-philosophical-methodology/toc.md
pdf_path: docs/sources/gendler-2010-intuition-imagination-philosophical-methodology/full.pdf
whole_document: false
chunks:
  - id: gendler-2010-intuition-imagination-philosophical-methodology/ch1-galileo
    title: Galileo and the Indispensability of Scientific Thought Experiment
    page_scheme: book
    page_start: 21
    page_end: 41
    pdf_page_start: 32
    pdf_page_end: 52
    components: [exp, m4]
    verified: true
    rationale: Worked Galileo case; thought experiments as cognitively contentful, not merely rhetorical.
  - id: gendler-2010-intuition-imagination-philosophical-methodology/ch2-rethought-reperceived
    title: Thought Experiments Rethought — and Reperceived
    page_scheme: book
    page_start: 42
    page_end: 52
    pdf_page_start: 53
    pdf_page_end: 63
    components: [exp, m4]
    verified: true
    rationale: Primary exp target; thought experiments as mental simulation, not pure rational insight.
  - id: gendler-2010-intuition-imagination-philosophical-methodology/ch3-exceptional-persons
    title: Exceptional Persons: On the Limits of Imaginary Cases
    page_scheme: book
    page_start: 53
    page_end: 73
    pdf_page_start: 64
    pdf_page_end: 84
    components: [exp, m4]
    verified: true
    rationale: Limits-of-thought-experiments analysis; direct support for Dennettian stress-testing.
  - id: gendler-2010-intuition-imagination-philosophical-methodology/ch5-fake-barns
    title: The Real Guide to Fake Barns: A Catalogue (with Hawthorne)
    page_scheme: book
    page_start: 98
    page_end: 115
    pdf_page_start: 109
    pdf_page_end: 126
    components: [exp, m4]
    verified: true
    rationale: Catalogues how thought experiments degrade when imaginative load is misjudged.
  - id: gendler-2010-intuition-imagination-philosophical-methodology/ch6-cognitive-equilibrium
    title: Philosophical Thought Experiments, Intuitions, and Cognitive Equilibrium
    page_scheme: book
    page_start: 116
    page_end: 134
    pdf_page_start: 127
    pdf_page_end: 143
    components: [exp, m4]
    verified: false
    rationale: Most general statement of the volume's position on what intuitions provide.
warnings: ch6 book page_end 134 overshoots actual content end (book p. 132 = PDF 143); PDF 144 is Part II divider, 145 blank, Ch.7 opens at PDF 146; pdf_page_end set to 143 to exclude divider+blank.

### hadot-1995-philosophy-as-a-way-of-life
pdf_total_pages: 321
toc_path: docs/sources/hadot-1995-philosophy-as-a-way-of-life/toc.md
pdf_path: docs/sources/hadot-1995-philosophy-as-a-way-of-life/full.pdf
whole_document: false
chunks:
  - id: hadot-1995-philosophy-as-a-way-of-life/ch1-forms-of-life
    title: Forms of Life and Forms of Discourse in Ancient Philosophy
    page_scheme: book
    page_start: 49
    page_end: 70
    pdf_page_start: 60
    pdf_page_end: 81
    components: [exp]
    verified: true
    rationale: Methodological core; texts composed for forms of life, not as decontextualized doctrine.
  - id: hadot-1995-philosophy-as-a-way-of-life/ch3-spiritual-exercises
    title: Spiritual Exercises
    page_scheme: book
    page_start: 81
    page_end: 125
    pdf_page_start: 92
    pdf_page_end: 136
    components: [exp]
    verified: true
    rationale: Canonical catalog of practices; operational backbone for practice-level directives.
  - id: hadot-1995-philosophy-as-a-way-of-life/ch5-figure-of-socrates
    title: The Figure of Socrates
    page_scheme: book
    page_start: 147
    page_end: 178
    pdf_page_start: 158
    pdf_page_end: 189
    components: [exp]
    verified: true
    rationale: Elenchus as care of the self; grounds dialogical disposition.
  - id: hadot-1995-philosophy-as-a-way-of-life/ch9-view-from-above
    title: The View from Above
    page_scheme: book
    page_start: 238
    page_end: 250
    pdf_page_start: 249
    pdf_page_end: 261
    components: [exp]
    verified: true
    rationale: Cosmic-perspectival exercise; concise, supports stepping outside own framing.
  - id: hadot-1995-philosophy-as-a-way-of-life/ch10-sage-and-world
    title: The Sage and the World
    page_scheme: book
    page_start: 251
    page_end: 263
    pdf_page_start: 262
    pdf_page_end: 274
    components: [exp]
    verified: true
    rationale: Mature stance the practices aim at; formal endpoint.
  - id: hadot-1995-philosophy-as-a-way-of-life/ch11-philosophy-as-way-of-life
    title: Philosophy as a Way of Life
    page_scheme: book
    page_start: 264
    page_end: 276
    pdf_page_start: 275
    pdf_page_end: 287
    components: [exp]
    verified: true
    rationale: Title essay; most general statement of the position.
