# `docs/` — source-text storage and pipeline tracking

This directory holds the source texts that feed the project's instruction-document pipeline, organized along two axes.

## Layout

```
docs/
├── README.md                         ← this file
├── _manifest/                        ← deliverable-axis view: which sources serve which artifact
│   ├── proc.md                       ← research-procedure (claude.ai project)
│   ├── m1-pragma-dialectical.md      ← Mode 1 critic skill
│   ├── m2-hermeneutic.md             ← Mode 2 critic skill
│   ├── m3-skinnerian.md              ← Mode 3 critic skill
│   ├── m4-dennettian.md              ← Mode 4 critic skill
│   └── exp-exploratory.md            ← Claude Code exploratory-default interlocutor
└── sources/                          ← source-axis view: each source self-contained
    └── <source-slug>/
        ├── full.pdf                  ← the full source
        ├── toc.md                    ← table of contents + brief preface/foreword (books only)
        ├── chunks/                   ← chapter/section splits (one PDF per chunk)
        └── extracted/                ← extract-directives skill output (markdown)
```

**TOC scope:** the `toc.md` file contains the full contents listing (parts, chapters, subchapters, with printed page numbers verbatim) plus a brief excerpt or summary of any preface/foreword that signals what the book is doing methodologically. Pure list-of-figures, list-of-abbreviations, and acknowledgements are excluded. The goal is to give a future agent enough to decide which chapters are in scope for a given deliverable.

## Source slug convention

`{author-last}-{year}-{short-title-kebab-case}`

For multi-author works, hyphenate the first 1–2 author surnames. For multi-volume works, append `-volN`. Use original publication year, not reprint year. Examples:

- `eemeren-grootendorst-2004-systematic-theory`
- `skinner-2002-visions-of-politics-vol1`
- `ricoeur-1981-hermeneutics-human-sciences`
- `arksey-omalley-2005-scoping-studies`

The slug is the canonical join key: given a slug, an agent can deterministically locate full / toc / chunks / extracted.

## How the two axes work together

- **Working on a single source** (e.g., chunking, extracting) → `sources/<slug>/` is self-contained.
- **Working on a single deliverable** (e.g., compiling Mode 1) → start at `_manifest/m1-pragma-dialectical.md`, which lists the in-scope source slugs and their pipeline status.
- **Multi-purpose sources** (Skinner *Visions* serves `proc` + `m3`; Gadamer *T&M* serves `m2` + `exp`; Dennett *IP* serves `m4` + `exp`) live under one slug in `sources/` and are referenced from each relevant manifest.

## Pipeline stages

A source moves through these stages, each represented by a folder under its slug:

1. **`full.pdf`** — acquired. The full source text.
2. **`toc.md`** — table of contents in markdown (books only). Contents listing with printed page numbers verbatim from the source, plus a brief preface/foreword excerpt. Used to plan which chapters are in scope per deliverable; target chapters are recorded in the relevant `_manifest/<deliverable>.md` entry.
3. **`chunks/`** — chapter/section PDFs, one per chunk. Naming convention within: `NN-short-name.pdf` (e.g., `06-rules-for-critical-discussion.pdf`).
4. **`extracted/`** — output of the `extract-directives` skill (markdown, one file per source).

Empty subfolders mean the corresponding stage is pending.

## Adding a new source

1. Decide the slug per the convention above.
2. `mkdir -p sources/<slug>/{chunks,extracted}`.
3. Drop `full.pdf` into `sources/<slug>/`. For books, also create `toc.md` per the TOC scope above.
4. Add the slug to each `_manifest/<deliverable>.md` it serves, with target chapters/sections noted.

## Related files

- `../sources_to_acquire.md` — the canonical ranked acquisition list across all deliverables. Manifests pull their in-scope sources from here.
- `../refs/` — the three research reports that justify the acquisition list.
- `~/.claude/skills/extract-directives/` — the skill that processes chunks into extracted directives.
- `~/.claude/skills/compile-instructions/` — the skill that compiles extracted directives into a deployable instruction document.
