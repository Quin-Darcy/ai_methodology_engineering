# Per-Source Chunking Workflow

## Purpose

Produce `docs/_manifest/chunking-plan.md` — a single, compact reference file that lists, for each of the 29 acquired sources, which chapters/sections should be carved out of `full.pdf` and which project deliverable(s) each chunk serves. A downstream extraction agent reads this file to drive Stage 3 (per-chunk directive extraction) of `procedure.md`.

The workflow is **iterated one source at a time** with **fresh subagent contexts per subtask** to bound multi-turn drift (Laban et al. 2025) and prevent the failure mode observed earlier in this project — a single agent given 29 sources at once stalls and edits files outside its remit.

## File outputs

- `docs/_manifest/chunking-plan.md` — the shared reference file. Grows by one source-block per iteration.
- `docs/_manifest/verify_chunking_plan.py` — verification script. Written **once** before iteration begins; re-run after every iteration's Subtask 3.

## Constant inputs (read in Subtask 1, not Subtask 2 or 3)

- `summary.md` — project goals; the six deliverables.
- `refs/` — four reference docs on the corpus and on LLM-instruction-design empirical literature.
- `procedure.md` — Stage 2 (Chunking rules) and Stage 3 (Per-Chunk Extraction).
- `docs/_manifest/{exp-exploratory,m1-pragma-dialectical,m2-hermeneutic,m3-skinnerian,m4-dennettian,proc}.md` — six manifest files. The `target chapters:` lines in these manifests are **authoritative** input.

## Per-source inputs

- `docs/sources/{slug}/toc.md` — the source's TOC and (in most cases) an "Operational map" section already containing chunking guidance.
- `docs/sources/{slug}/full.pdf` — the actual PDF (used in Subtask 2 only).

## Project deliverables (the component codes)

| Code | Deliverable |
|---|---|
| `exp` | Exploratory-default interlocutor (Claude Code CLAUDE.md) |
| `m1` | Pragma-dialectical critic skill |
| `m2` | Hermeneutic close-reading critic skill |
| `m3` | Skinnerian historiographical critic skill |
| `m4` | Dennettian intuition-pump critic skill |
| `proc` | Research procedure (claude.ai project) |

A chunk may serve multiple components (multi-tag).

---

## Volume budget per source

Cap each source's block at **2500 bytes** (≈ 600 tokens). Concretely:

- ≤ 6 chunks unless the source genuinely serves many components at distinct sites (rare).
- Rationale: **one line, ≤ 15 words**, per chunk. No prose paragraphs, no quotations.
- Articles and single-essay sources → one `whole_document: true` entry, no per-chapter breakdown.
- Per-source `warnings:` field, when present, must be a single-line string (multi-line lists break the parser); join multiple warnings with `; `.

Across 29 sources this yields a final file of roughly 15–20k tokens — still small enough to ship to the extraction agent in full without lost-in-the-middle pressure, and small enough to lookup-by-slug cheaply.

The 2500-byte limit accommodates the standard format with `pdf_page_start`/`pdf_page_end` fields per chunk. The original 1500-byte limit was too tight once those became required for non-page schemes; raising once and locking is preferable to per-source ad-hoc tuning.

---

## Per-source pipeline (3 subtasks)

Run subtasks **sequentially** for one source. Do not start the next source until Subtask 3 has succeeded for the current one. Each subtask uses a **fresh subagent context** (no carry-over from earlier sources).

### Subtask 1 — Selection

**Role.** Identify which chapters/sections of *this one source* should be chunked, and which deliverable(s) each serves. No PDF inspection; toc.md and manifests are the inputs.

**Reads.**
- `summary.md`
- `refs/*.md` (all four)
- All six files in `docs/_manifest/` *except* `chunking-plan.md` and `chunking-workflow.md`
- `docs/sources/{slug}/toc.md`

**Decides.**
- Which sections (chapters, essays, sub-sections, or `whole_document`) to chunk.
- For each section: a `components` tag set drawn from `{exp, m1, m2, m3, m4, proc}`.
- A one-line rationale explaining relevance.

**Strong defaults (defer unless there is a specific reason to diverge).**
- The toc.md "Operational map" section, if present, encodes prior project-level reasoning about chunking. Treat its recommendations as the default.
- Each manifest's `target chapters:` lines are authoritative scope declarations. Every named target chapter must appear as a chunk for the corresponding component.

**Outputs.** A draft source-block, written **inline in the response** (not yet to disk), in the format spec below — but with `page_*` fields left as the **book-page ranges as they appear in toc.md**, marked `verified: false`.

**Hard constraints.**
- Do NOT modify any file. Subtask 1 is read-only.
- Do NOT read other sources' tocs.
- Do NOT exceed the volume budget. If the source genuinely needs more than 6 chunks, halt and surface to the user.

### Subtask 2 — Page-number verification

**Role.** Verify the page ranges in the draft block against the actual PDF.

**Reads.**
- The draft block from Subtask 1.
- `docs/sources/{slug}/toc.md`
- `docs/sources/{slug}/full.pdf` (via `pdfinfo` and `pdftotext`)

**Tools.** `pdfinfo`, `pdftotext`. Both available on the system.

**Procedure.**
1. Run `pdfinfo full.pdf` once. Record `Pages:` as `pdf_total_pages` for the block.
2. For each chunk in the draft:
   1. Confirm the toc.md actually anchors the chunk: grep for the section title or chapter number near the claimed `page_start`. If no anchor in toc.md, flag `verified: false` and add a warning.
   2. If `page_scheme: book` (default for most sources), the toc-listed book pages are recorded as `page_start` / `page_end`. Note: book pages are not PDF pages — front matter shifts the offset. Record both values when ascertainable; otherwise record only book pages.
   3. If `page_scheme: pdf` (rare; for OCR'd or unpaginated PDFs), `page_end` must be ≤ `pdf_total_pages`.
   4. For non-page schemes (Aristotle's Bekker numbers, Wittgenstein's section numbers), record the scheme value plus a best-estimate book-page span.
3. **Spot-check exactly one chunk per source.** Run `pdftotext -f {page_start} -l {page_start} full.pdf -` (mapping book→PDF page if needed by adding a small offset) and confirm the first ~200 chars match the expected section title or content. Record the result as `spot_check: ok` or `spot_check: failed`.
4. If any chunk's range is suspect (range > 100 pages in a < 300-page book; `page_end` < `page_start`; section name not in toc.md), emit a warning string and set `verified: false` on that chunk.

**Outputs.** The block from Subtask 1 with each chunk's `verified` flag set, `pdf_total_pages` recorded, any warnings inlined.

**Hard constraints.**
- Do NOT modify the PDF, the toc.md, any manifest, or any other source file.
- Do NOT proceed if `pdfinfo` fails — surface the error.

### Subtask 3 — Append + verify

**Role.** Mechanical: append the verified block to `chunking-plan.md` and re-run the verifier.

**Reads.** The verified block from Subtask 2.

**Procedure.**
1. If `chunking-plan.md` does not yet have an entry for this `slug`, append the block in slug-alphabetical position. If it does, replace the existing block (idempotent re-runs).
2. Run `python docs/_manifest/verify_chunking_plan.py`. Confirm exit 0.
3. Mark the source as done in the iteration checklist at the bottom of this file.

This subtask can be done by the main thread (no subagent dispatch) since it is purely mechanical. If dispatched as a subagent, the prompt is one paragraph.

---

## Format spec for `chunking-plan.md`

```
# Chunking Plan
(short prose intro: scope, format, how to read entries, link back to chunking-workflow.md)

## sources

### {slug}
pdf_total_pages: {N}
toc_path: docs/sources/{slug}/toc.md
pdf_path: docs/sources/{slug}/full.pdf
whole_document: false   # or true
chunks:
  - id: {slug}/ch{N}-{shortname}
    title: {section title — short}
    page_scheme: book   # one of: book, pdf, bekker, section_number
    page_start: {N or identifier}
    page_end: {N or identifier}
    components: [m1, exp]   # one or more codes
    verified: true
    rationale: {≤ 15 words}
  - ...
warnings: []   # optional; only if any chunk has verified: false
```

For `whole_document: true` sources, the `chunks` list contains a single entry with `id: {slug}/whole`, `page_start: 1`, `page_end: {pdf_total_pages}`, `page_scheme: pdf`.

The format is intentionally Markdown-with-YAML-fragments rather than pure YAML or pure prose — readable by humans, parseable with a simple line-level state machine for the verifier.

---

## Verification script (`verify_chunking_plan.py`)

Written once before iteration starts. Checks every block in `chunking-plan.md`:

1. **Structural validity.** Each block has the required fields. Each chunk has the required keys. Page values are integers (or recognized identifiers for `bekker` / `section_number`). `page_start` ≤ `page_end` for integer schemes.
2. **File presence.** `toc_path` and `pdf_path` exist on disk.
3. **PDF total agrees with pdfinfo.** Re-run `pdfinfo full.pdf`; the recorded `pdf_total_pages` must match the live value.
4. **PDF-scheme bounds.** Where `page_scheme: pdf`, the range is inside `[1, pdf_total_pages]`. Hard fail.
5. **TOC anchor.** For each chunk, at least one of {chunk title, chapter number, identifier} appears literally in `toc.md`. Hard fail otherwise — catches typos and fabricated entries.
6. **Manifest target coverage.** Parse each manifest's `target chapters:` lines. For every named target, at least one chunk in the corresponding source's block must cover it (substring match on chunk title) and tag the manifest's component. Warning, not hard fail.
7. **Volume budget.** Each source-block ≤ 2500 bytes (≈ 600 tokens). Warning, not hard fail.

The script:
- Prints every warning before the summary.
- Prints `OK: N chunks across M sources verified` or `FAIL: ...`
- Exits 0 on success, non-zero on hard failure.

---

## Iteration mechanics

**Order.** Iterate alphabetically by slug. Alphabetical is arbitrary but reproducible; alternative orderings (Tier 1 first, by-deliverable batching) are not better given the per-source isolation.

**Per-iteration loop.**
1. Pick the next slug from the checklist below where the box is unchecked.
2. **Whole-document shortcut for articles / single essays.** If the source is a journal article or single essay (manifest annotation `(article — no chunks needed)` or toc.md saying "the article is the unit"), skip Subtasks 1 and 2 and run `python3 docs/_manifest/commit_source_block.py <slug> --whole-document --components <comma-list>`. Done.
3. Otherwise, generate the Subtask 1 prompt: `python3 docs/_manifest/subtask1_brief.py <slug>` and dispatch a subagent. Receive draft block.
4. Save the draft to a temp file. Generate the Subtask 2 prompt: `python3 docs/_manifest/subtask2_brief.py <slug> --block-file /tmp/draft.txt`. Dispatch a subagent. Receive verified block.
5. Commit: `cat /tmp/verified.txt | python3 docs/_manifest/commit_source_block.py <slug> --stdin`. This inserts/replaces the block at the correct alphabetical position, runs the verifier, and ticks the checklist box.
6. Pause for user inspection if any warnings or hard failures are emitted.

**Pre-invocation integrity check.** The helper scripts have project-allowlist entries in `.claude/settings.json` that let Claude run them without permission prompts. To preserve auditability, **before each invocation** of any helper script, run:

```bash
sha1sum -c docs/_manifest/SCRIPT_HASHES
```

If any line reports `FAILED`, halt and surface to the user — a script has changed and the pinned hash is stale. After legitimate edits to a helper script, regenerate `SCRIPT_HASHES` with `sha1sum docs/_manifest/*.py > docs/_manifest/SCRIPT_HASHES` and commit both the script and the hash file in the same commit.

**Helper scripts** (in `docs/_manifest/`):
- `scan_pdf_quality.py` — pre-flight scan of all source PDFs. Reports image-only PDFs (need OCR) and reflowable ebooks (need `page_scheme: pdf`). Run once before iteration begins.
- `subtask1_brief.py <slug>` — emits a self-contained Subtask 1 prompt with workflow context, manifest stanzas, **pre-computed page bounds from the toc table** (next-chapter-start − 1 arithmetic), and reflowable-PDF warnings. The agent reads zero additional files.
- `subtask2_brief.py <slug> --block-file <path>` — emits a Subtask 2 prompt with the draft block inlined, plus pre-flight observations: live `pdfinfo` page count, image-only / reflowable detection, and a suggested book→PDF anchor (the Ch. 1 title from the toc).
- `commit_source_block.py <slug> --stdin` — append/replace + verify + tick in one CLI call.
- `commit_source_block.py <slug> --whole-document --components <list> [--rationale "..."]` — for articles / single essays, builds the entire single-chunk block from `pdfinfo` + toc.md and commits it. Replaces both subagent dispatches.
- `verify_chunking_plan.py` — standalone verifier; runs automatically inside `commit_source_block.py` but can be invoked directly.

**Why fresh contexts per subtask.** Subtask 1 needs ~6 manifests + summary + refs + a toc — substantial reading. Subtask 2 needs the PDF tools and one toc. Carrying Subtask 1's context into Subtask 2 wastes tokens and increases drift risk. The handoff between subtasks is the small draft block, not the agent's working memory.

**Why iterate per source, not per batch.** A single agent given all 29 sources stalled at 44 tool calls in the first attempt. Per-source iteration with fresh contexts caps the failure blast radius at one source.

---

## Stop conditions

Halt the iteration and surface to the user when any of:

- Subtask 2 emits a hard verification failure (page_end out of PDF bounds where `page_scheme: pdf`, or toc anchor missing).
- Subtask 3's verifier exits non-zero.
- A source genuinely requires > 6 chunks to honor its manifest commitments.
- Two consecutive iterations on the same slug produce conflicting selections.

---

## Iteration checklist

Mark `[x]` after Subtask 3 succeeds for that slug.

- [x] aristotle-metaphysics
- [x] arksey-omalley-2005-scoping-studies
- [x] bohm-1996-on-dialogue
- [x] booth-sutton-2022-systematic-approaches
- [x] cappelen-gendler-hawthorne-2016-oxford-handbook
- [x] cavell-1979-claim-of-reason
- [x] davidson-1984-inquiries
- [x] dennett-1991-consciousness-explained
- [x] dennett-2013-intuition-pumps
- [x] eemeren-grootendorst-2004-systematic-theory
- [x] eemeren-grootendorst-snoeck-henkemans-2002-argumentation-aep
- [x] gadamer-1960-truth-and-method
- [x] gendler-2010-intuition-imagination-philosophical-methodology
- [x] hadot-1995-philosophy-as-a-way-of-life
- [ ] martinich-2015-philosophical-writing
- [ ] murdoch-1970-sovereignty-of-good
- [ ] palmer-1969-hermeneutics
- [ ] polonioli-2019-minimally-biased-naturalistic-philosophy
- [ ] pryor-guidelines-writing
- [ ] ricoeur-1981-hermeneutics-human-sciences
- [ ] rorty-1984-four-genres
- [ ] skinner-2002-visions-of-politics-vol1
- [ ] sofaer-strech-2012-systematic-reviews-of-reasons
- [ ] tricco-2018-prisma-scr
- [ ] tully-1988-meaning-and-context
- [ ] walton-reed-macagno-2008-argumentation-schemes
- [ ] williamson-2018-doing-philosophy
- [ ] wittgenstein-1953-philosophical-investigations
- [ ] wittgenstein-1998-culture-and-value
