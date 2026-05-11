# Procedure: Constructing Custom Instructions for Philosophy Research and Discussion Projects

**Purpose.** Specify the procedure for converting authoritative methodological literature in philosophy and adjacent fields into deployable Claude artifacts: (1) custom instructions for a claude.ai *research project* that produces literature-review-style philosophical research reports, and (2) a Claude Code *discussion project* consisting of a CLAUDE.md exploratory default plus four mode-shaped critic skills (pragma-dialectical, hermeneutic, Skinnerian, Dennettian).

**Scope.** Source acquisition, per-source TOC summarization, chunking, per-chunk directive extraction, clustering, canonicalization. From Stage 6 onward (organization, compression) the procedure splits into a research-project track and a discussion-project track; testing and iteration (Stages 8–9) recombine. The procedure does not cover the choice of which deliverables to build or which methodological traditions to include — that decision is recorded in `summary.md`.

**Status.** Stages 1–4 reflect implementation as it currently stands and are walked end-to-end against an active corpus of 29 sources in `docs/sources/` and six per-deliverable manifests in `docs/_manifest/`. Stages 5–9 retain the original specification; they are revised when their work begins. Replicability requires that manifests, toc.md files, `chunking-plan.md`, the per-chunk `.directives.yaml` and `.triage.yaml` files, and the per-component `<component>-clustering-input.yaml` and `<component>-clusters.yaml` files carry the canonical pipeline state — not Claude's working memory across conversations.

**Note on evidence basis.** The design choices in Stages 3, 5, 7, 8, and 9 are constrained by what is empirically known about LLM instruction-following: prompt-format brittleness (Sclar et al. 2024), the multiplicative drop in joint constraint adherence as the number of constraints grows ("curse of instructions"; Hagiwara et al. 2024), the difficulty of conditional/chained directives (ComplexBench; Wen et al. 2024), the multi-turn performance drop (Laban et al. 2025), the failure of negation (Truong et al. 2023), the limits of self-critique (Huang et al. ICLR 2024), and Claude's documented sycophancy (Sharma et al. ICLR 2024). The procedure does not treat these findings as decisive — most measure verifiable surface constraints, not open-ended philosophical synthesis — but uses them to set defaults and to specify what the test stage must measure.

---

## Stage 1 — Source Acquisition, Manifests, and TOCs

### 1.1 Per-deliverable manifests

The project's six deliverables are tracked in six manifest files in `docs/_manifest/`:

| Manifest | Deliverable |
|---|---|
| `exp-exploratory.md` | Exploratory-default interlocutor (Claude Code CLAUDE.md) |
| `m1-pragma-dialectical.md` | Pragma-dialectical critic skill |
| `m2-hermeneutic.md` | Hermeneutic close-reading critic skill |
| `m3-skinnerian.md` | Skinnerian historiographical critic skill |
| `m4-dennettian.md` | Dennettian intuition-pump critic skill |
| `proc.md` | Research procedure (claude.ai project) |

Each manifest declares scope and tracks pipeline status. For each in-scope source, a manifest records:

- the source slug,
- a Tier classification (1/2/3, local to this deliverable),
- a `target chapters:` annotation where relevant,
- pipeline status flags (`full ✓`, `toc ✓`, `chunks ✓`, `extracted ✓`),
- cross-tags for sources that serve multiple deliverables (`also serves X`).

A source may be Tier 1 in one manifest and Tier 2 in another. The canonical project-wide ranked acquisition list lives in `sources_to_acquire.md`; the manifests are the per-deliverable subset of that list with pipeline status attached. **The manifests are the source log.** Do not maintain a separate file.

### 1.2 Tier classification (within each manifest)

- **Tier 1.** Highest density of extractable directives for this deliverable. Acquire before extraction begins.
- **Tier 2.** Acquire after Stage 8 testing reveals gaps in this deliverable's coverage.
- **Tier 3.** Skip unless gap analysis demands.

### 1.3 Source directory structure

Each acquired source lives under `docs/sources/{slug}/`:

- `full.pdf` — the source text
- `toc.md` — structured TOC and operational map (produced in 1.6)
- `chunks/` — chunk PDFs (produced lazily from `chunking-plan.md` at Stage 3)
- `extracted/` — directive records (Stage 3 output)

Slugs are stable, kebab-case identifiers: `{author_last}-{year}-{shortwork}` (e.g., `skinner-2002-visions-of-politics-vol1`).

### 1.4 Substitution rule

Where a Tier 1 or Tier 2 source is unavailable as a legitimately obtainable PDF, substitute a peer-reviewed scholarly summary article of the source's methodology. Record the substitution in the relevant manifest entry so downstream extraction can be re-run against the primary text if it is later acquired.

### 1.5 Per-source TOC summarization

For each acquired source, produce a `docs/sources/{slug}/toc.md` before Stage 2. Each toc.md contains:

- **Bibliographic header** — full citation, ISBN, edition.
- **Front matter / back matter listing** — acknowledgments, prefaces, appendices, indexes, bibliography, with page numbers where given.
- **Contents table** — chapter/section titles with page numbers, in a parseable markdown table.
- **Front-matter excerpts** — short prose excerpts that frame what the work does, providing context for chunk-selection downstream.
- **Operational map** — a section that recommends which chapters/sections matter for which project deliverable, with a one-line rationale per recommendation. The operational map encodes prior reading-and-judgment work and becomes the strong default for Stage 2 chunk selection.

The toc.md is produced by a Claude pass against the source's TOC, front matter, and back matter, with the operational map composed by cross-referencing the source's structure against the manifest entries that mention this slug. The toc.md is human-revised before being committed.

The toc.md is the load-bearing artifact for replicability at this stage: it captures source-level reading judgment in a parseable form. Without it, Stage 2 falls back to chapter-boundary heuristics and loses the per-deliverable relevance ranking.

---

## Stage 2 — Chunking

### 2.1 Goal: `chunking-plan.md`

Stage 2 produces `docs/_manifest/chunking-plan.md` — a single reference file with one block per source declaring the chapters/sections to extract from `full.pdf`, their page ranges, the deliverable component(s) each chunk serves, and a one-line rationale.

The chunking-plan is the deterministic input to Stage 3. Stage 3 extraction reads from this plan, not from the original toc.md.

### 2.2 Per-source three-subtask workflow

The full workflow is documented in `docs/_manifest/chunking-workflow.md`. In brief, for each source:

- **Subtask 1 — Selection.** A subagent reads the source's `toc.md` (especially its operational map) and the manifests that mention this slug. It decides which sections to chunk and tags each with one or more component codes (`exp`/`m1`/`m2`/`m3`/`m4`/`proc`). The toc.md operational map and the manifests' `target chapters:` lines are strong defaults — divergence requires a stated reason. Output: a draft block with `verified: false` and `pdf_total_pages: TBD`.
- **Subtask 2 — Verification.** A subagent verifies page ranges by running `pdfinfo` (for total pages) and `pdftotext` (for content spot-checks) against `full.pdf`. For sources using non-page schemes (Aristotle's Bekker numbers, Wittgenstein's section numbers), the subagent locates the corresponding PDF pages and adds `pdf_page_start` / `pdf_page_end` fields. Output: the verified block with `verified: true` and `pdf_total_pages` set.
- **Subtask 3 — Append + verify.** Mechanical: insert or replace the block at the correct alphabetical position in `chunking-plan.md`, run the verifier, tick the iteration checklist in `chunking-workflow.md`. Done by main thread or a brief subagent.

**Iteration discipline.** One source at a time, fresh subagent context per subtask. Fresh contexts bound multi-turn drift (Laban et al. 2025) and isolate failure to a single source. Per-source iteration is empirically necessary: a single agent dispatched against all 29 sources stalled at 44 tool calls in early testing.

### 2.3 Helper scripts (in `docs/_manifest/`)

- `scan_pdf_quality.py` — one-shot pre-flight over all source PDFs. Reports image-only PDFs (need OCR) and reflowable ebooks (need `page_scheme: pdf`). Run once before iteration begins.
- `subtask1_brief.py <slug>` — emits a self-contained Subtask 1 prompt to stdout. Workflow context inlined; manifest stanzas for this slug grepped in; toc.md inlined; pre-computed chapter page bounds; reflowable-PDF warnings. Replaces ~13 redundant file reads per iteration with zero.
- `subtask2_brief.py <slug> --block-file <path>` — emits a Subtask 2 prompt to stdout with the draft block inlined plus pre-flight observations: live `pdfinfo` page count, image-only / reflowable detection, suggested book→PDF anchor, and a recommendation to use `peek_pdf_pages.py` for spot-checks.
- `peek_pdf_pages.py <pdf> <p> [<p>...] [--head N|--tail N|--full] [--layout]` — print `pdftotext` output for individual PDF pages with `=== PDF page N ===` headers between pages. Range-checks against the PDF total. Replaces hand-rolled `for p in ...; do pdftotext -f $p -l $p ...; done` shell loops, which would otherwise generate one permission prompt per shell-loop construction.
- `commit_source_block.py <slug> --stdin` — accepts the verified block on stdin, validates the slug shape against `^[a-z0-9][a-z0-9-]*$`, inserts/replaces at the correct alphabetical position in `chunking-plan.md`, runs the verifier, restores the prior file content if the verifier fails (so a malformed block does not contaminate the next run), and ticks the workflow checkbox using a line-anchored regex (so a slug like `foo` does not also flip a `foobar` checkbox). Idempotent. Exit codes distinguish input-validation failure (1) from verifier failure (2).
- `commit_source_block.py <slug> --whole-document --components <list>` — for journal articles and single-essay sources, builds the entire single-chunk block from `pdfinfo` + toc.md and commits it. Replaces both subagent dispatches.
- `verify_chunking_plan.py` — parses `chunking-plan.md` and runs the checks in 2.6. Standalone; also invoked automatically inside `commit_source_block.py`.

These scripts mechanize the steps that have no LLM judgment in them. Iteration cost drops from five hand-driven steps per source (dispatch ×2 + edit + verify + tick) to three (dispatch ×2 + commit-CLI), with steps 1 and 3 fully deterministic.

**Permission discipline for the helper scripts.** Each script has a narrow allowlist entry in `.claude/settings.json` (e.g., `Bash(python3 docs/_manifest/subtask1_brief.py *)`) so iteration runs without per-invocation permission prompts. The compensating control: each script's SHA1 is pinned in `docs/_manifest/SCRIPT_HASHES`, and the discipline is to run `sha1sum -c docs/_manifest/SCRIPT_HASHES` before each helper-script invocation. If any line reports `FAILED`, halt and surface to the user (a script changed and the pinned hash is stale). After legitimate edits, regenerate the hash file (`sha1sum docs/_manifest/*.py > docs/_manifest/SCRIPT_HASHES`) and commit script + hash together.

### 2.4 Volume budget

Each source-block in chunking-plan.md is capped at **2500 bytes** (≈ 600 tokens; ≤ 6 chunks, ≤ 15-word rationale per chunk). Articles and single-essay sources use a single `whole_document: true` entry. The per-source `warnings:` field, when present, must be a single-line string. The budget is enforced as a verifier warning; sustained overage indicates the source is being over-fragmented.

The budget matters because chunking-plan.md is shipped wholesale to the Stage 3 extraction agent (29 sources × ~600 tokens ≈ 15–20k tokens), small enough to avoid lost-in-the-middle attention pressure (Liu et al. 2024).

### 2.5 Format spec

Markdown headings + indented YAML-fragment bodies, parseable by a hand-rolled line-state-machine. Per-source block fields:

| Field | Type | Meaning |
|---|---|---|
| `pdf_total_pages` | int | matches `pdfinfo full.pdf` |
| `toc_path`, `pdf_path` | str | repo-relative paths |
| `whole_document` | bool | `true` for articles / single essays |
| `chunks` | list | one entry per section to chunk |

Per-chunk fields: `id`, `title`, `page_scheme` (`book`/`pdf`/`bekker`/`section_number`), `page_start`, `page_end`, optionally `pdf_page_start` / `pdf_page_end` (required when `page_scheme` is non-page), `components` (list of codes), `verified` (bool), `rationale` (≤ 15 words).

### 2.6 Verification

The verifier runs after every Subtask 3 and gates the iteration:

1. **Structural validity.** Required fields present; integer page values for integer schemes; `page_start ≤ page_end`.
2. **File presence.** `toc_path` and `pdf_path` exist on disk.
3. **`pdfinfo` agreement.** Declared `pdf_total_pages` matches the live PDF.
4. **PDF-scheme bounds.** When `page_scheme: pdf`, ranges fit `[1, pdf_total_pages]`. Hard fail.
5. **TOC anchor.** Each chunk's title, chapter id, or page number appears literally in the source's toc.md. Hard fail otherwise — catches typos and fabricated entries.
6. **Manifest target coverage.** Each manifest's `target chapters:` declaration (strict or prose-embedded) corresponds to at least one chunk for that component (warning).
7. **Volume budget.** Per-source byte threshold (warning).

Hard failures halt iteration; warnings accumulate and surface in the summary.

### 2.7 Pre-extraction integrity check

For each chunk declared in chunking-plan.md: the underlying PDF must open; its text layer must be selectable (not a pure scanned image); pagination must be intact. The verifier handles structural checks; the absence-of-text and OCR-quality checks are a manual confirmation supported by `scan_pdf_quality.py` (which flags image-only PDFs in the corpus).

For image-only PDFs identified at this stage, run OCR before Stage 3 begins. The standard tooling is `ocrmypdf -l <langs> input.pdf output.pdf` (use `-l deu+eng` for bilingual sources; add `--force-ocr` if some pages have stray text on cover/title pages that triggers `PriorOcrFoundError`). Convention: leave the original at `docs/sources/{slug}/full.pdf` (preserved for auditability) and write the OCR output to `docs/sources/{slug}/full.ocr.pdf`. Update `pdf_path` in chunking-plan.md to point at the OCR'd file for those sources, then re-run the verifier — page counts are preserved by `ocrmypdf`, so chunk page ranges remain valid.

Spot-check OCR quality on at least one mid-chunk page per OCR'd source by running `pdftotext -f N -l N <full.ocr.pdf> -` and confirming the output is legible. Minor artifacts (occasional missing spaces, single-character mis-reads on page numbers) are normal and acceptable for downstream extraction; widespread garbled text is not, and indicates a re-OCR is needed (try different language settings or pre-process the PDF).

### 2.8 Chunk text extraction (Stage 3 input)

Extract chunk content to **plain text files**, not to PDF slices. Text is the natural input format for Stage 3 extraction agents: cheaper per token (no per-call PDF parsing overhead), diffable, grep-able, and the extraction agents only need text content. The PDF was the source-of-truth artifact for Stage 2 (chunk selection and page-range verification); for Stage 3, text is the operational unit.

**Output location and naming.** Write each chunk to `docs/sources/{slug}/chunks/{chunk_id}.txt`, where `{chunk_id}` is the path component after the slug in the chunk's `id` field in chunking-plan.md (e.g., chunk `id: bohm-1996-on-dialogue/ch1-on-dialogue` → file `docs/sources/bohm-1996-on-dialogue/chunks/ch1-on-dialogue.txt`). Each chunk's `chunks/` subdirectory already exists per Stage 1.3.

**Extraction tooling.** Standard form: `pdftotext -layout -f <pdf_page_start> -l <pdf_page_end> <pdf_path> -` per chunk, post-processed for the issues below. The `pdf_path` value comes from chunking-plan.md (it points to `full.ocr.pdf` for the three image-only sources whose paths were updated after OCR; `full.pdf` for everything else). Pin `-layout` because:

- It preserves columns, which matters for bilingual en-face layouts (Wittgenstein 1998: German left / English right) and for sources with marginal footnotes.
- The default flow mode interleaves footnote text mid-paragraph on layouts the heuristic misreads.

**Required post-processing.** Three deterministic transformations applied between `pdftotext` output and the on-disk text file:

1. **Page-number markers.** Insert a `=== p. {N} ===` separator line between pages (where `{N}` is the *book* page number when `page_scheme: book`, or the PDF page number otherwise). Without these markers, citing back to a specific page from extracted directives reduces to guesswork; they are the stable anchors the extraction prompt at Stage 3 cites against.
2. **End-of-line de-hyphenation.** PDFs often have soft hyphens at line breaks ("philo-\nsophical"). Without de-hyphenation, word search and readability are broken. The transformation is a small regex: `s/(\w)-\n(\w)/$1$2\n/g`. Apply with care to genuine hyphenated compounds (e.g., "self-deception"); a simple heuristic is to keep the hyphen if the word fragment before the hyphen is short and capitalized or matches a known compound prefix list.
3. **Whitespace normalization.** Collapse runs of three-or-more blank lines to two; strip trailing whitespace per line; normalize tabs to spaces.

**Text-file header.** Each chunk text file opens with a small YAML-ish header block listing the `id`, `title`, `page_scheme`, `page_start`/`page_end` (and `pdf_page_start`/`pdf_page_end` when applicable), `components`, and `rationale` from the chunking-plan entry. The Stage 3 extraction prompt uses this header as the chunk's source-citation block.

**Mechanization (complete).** Implemented as `docs/_manifest/extract_chunk_text.py`. CLI: `python3 docs/_manifest/extract_chunk_text.py --slug <slug> [--chunk-id <tail>]`. Imports `verify_chunking_plan.parse_plan` to read chunking-plan.md; honors the plan's `pdf_path` (so OCR'd PDFs are picked up automatically); applies all post-processing in one pass; writes per-chunk `.txt` files to `docs/sources/<slug>/chunks/<chunk-tail>.txt`. Registered in `SCRIPT_HASHES` and in `.claude/settings.json` allowlist.

Status: **complete for all 29 sources / 108 chunks (~7.4 MB total chunk text).**

Implementation choices made during the pilot (revising the three transformations listed in §2.8 1–3 above):

- **Extractor flag:** `pdftotext -layout` (preserves enough structure to detect footnotes, hyphenation, and per-page running headers).
- **Dehyphenation:** hunspell `en_US-large`. Joined-without-hyphen forms in the dictionary → drop hyphen; not in the dictionary → keep hyphen. Handles chained hyphenations across consecutive line pairs. Residual: a small number of cases where proper nouns or rare compounds aren't in the dictionary (e.g., "Nor-ton", "disconfirm-ing") keep their hyphen — accepted, normalized by the Stage 3 extraction agent when quoting.
- **Running-header strip:** added beyond the three transformations in §2.8 — auto-detected via digit-normalized repetition counting. Any short line whose digit-collapsed form repeats on ≥ 2 pages is stripped. This handles per-page headers with embedded page numbers (e.g., `126 Radical Interpretation` vs `Radical Interpretation 127`) without per-source configuration.
- **Page-number strip exemption:** bare-number lines are preserved when followed by `[N]` — those are footnote-body markers, not page numbers.
- **Ligature normalization:** `ﬁ`/`ﬂ`/`ﬀ` etc. → `fi`/`fl`/`ff`.

Known residuals across the 108 extracted text files:

- OCR character errors in the 3 OCR'd sources (`is`→`1s`/`i1s`, `I`→`|`, footnote `1`→`!`). ~1 per 4 pages. The Stage 3 extraction agent silently normalizes these when quoting (observed in pilot).
- Figure regions (vector-art letter labels in scientific diagrams) remain as scattered text fragments. Sparse.
- 4 chunks recorded a trailing-blank-page trim in their header (`extracted_pages` differs from plan range by 1); chunk content is correct.

**Why this approach over per-chunk PDFs.** A PDF chunk is still a PDF — pdftotext'ing it again at extraction time is wasted work, and the parser-and-render overhead repeats per Stage 3 invocation. Text files solve once. The auditability concern (extraction grounded in source) is preserved: the chunk text file's header contains the slug, page range, and PDF path; an auditor can re-run `pdftotext -f X -l Y full.pdf` to confirm the text matches.

---

## Stage 3 — Per-Chunk Directive Extraction

### 3.1 Extraction is one Claude pass per chunk

The chunks to extract are exactly those declared in `chunking-plan.md`. Do not extract from sections not declared there; do not merge chunks. Per-chunk extraction is necessary for accurate source attribution and for staying within useful context limits. It also bounds the multi-turn drift documented in Laban et al. 2025: each extraction is a fresh single-turn task with the full source in front of the model.

The input to each extraction pass is the chunk's text file produced at Stage 2.8 (`docs/sources/{slug}/chunks/{chunk_id}.txt`), not the original PDF. The text file already contains the chunk's source-citation header and page-number markers, so the extraction prompt can cite back to specific pages without consulting the PDF.

Each extracted directive carries the chunk's `components` tags from chunking-plan.md (e.g., `[m1, exp]`). These tags drive the deliverable-track split at Stage 6.

### 3.2 Required output structure per directive

Each extracted directive must be a record with the following fields:

| Field | Content |
|---|---|
| `source` | Short citation (author, year, work, chapter or section, page if available) |
| `directive` | The instruction in imperative form, one sentence where possible. Phrase exactly as the source phrases it; do not yet convert "do not" formulations to affirmatives — that conversion happens in Stage 5. |
| `trigger` | The condition under which the directive applies. State the condition in surface-verifiable terms where the source allows it (e.g., prefer "when the question concerns the views of a named historical figure" over "when interpretive caution is warranted"). When the source itself states the trigger only abstractly, preserve the source's phrasing and flag it for Stage 5 sharpening. |
| `qualification` | Any limit the source itself places on the directive, including known scholarly disputes about it |
| `evidence` | A short verbatim excerpt or tight paraphrase from the chunk supporting the directive |

### 3.3 Extraction prompt template

Canonical template: `docs/_manifest/extraction_prompt_template.md` (hash-pinned in `SCRIPT_HASHES`).

The template is wrapped in XML tags by section (`<source_information>`, `<chunk_text>`, `<task>`, `<output_format>`, `<rules>`). Claude is trained to recognize XML tags as a prompt-organizing mechanism (Anthropic documentation; HIGH confidence on Claude, MODERATE on cross-model portability). The structural ordering is source-first (chunk text immediately follows `<source_information>`), with the critical instruction ("faithfulness to source is the entire task") mirrored at the very end of `<rules>` — the documented mitigation for "lost in the middle" attention bias on long inputs (Liu et al. 2024; OpenAI GPT-4.1 prompting guide).

The template embeds the following design moves:

1. Only directives explicitly stated or directly entailed by the chunk are extracted; nothing imported from general knowledge.
2. Imperative phrasing required.
3. Trigger condition stated explicitly even for "always-on" directives — forces acknowledgement of conditionality.
4. Qualifications lifted from the chunk, not added from elsewhere.
5. No synthesis or merging at this stage — merging happens in Stage 4.
6. **Explicit zero-directives authorization** in `<task>`: "you are explicitly authorized to return zero." Naming the over-extraction failure mode is a practitioner mitigation under sycophancy and pattern-completion pressure; it is not empirically validated as a full fix.
7. **Three calibration examples** in `<task>` (Skinnerian / Gendler / pragma-dialectical) to show the *shape* of a good directive without leaking content.
8. **Named NON-directives** in `<task>` ("be clear", "cite sources", "consider multiple perspectives") to defuse the platitude trap: extracting generic methodology platitudes the chunk does not actually argue for.
9. **A fabrication-detection rule at the prompt tail**: "if your draft directive could have been written without reading this chunk, delete it." Phrased as a test the agent can apply to its own output, not a passive exhortation.

Variables substituted into the template: `{{slug}}`, `{{chunk_id}}`, `{{chunk_title}}`, `{{chunk_pages}}`, `{{components}}`, `{{chunk_text}}`, `{{output_path}}`.

**Prompt-build helper:** `docs/_manifest/build_extraction_prompt.py <slug> <chunk-tail>` reads the template, the chunk text, and chunking-plan.md metadata; performs the substitution; writes the fully-substituted prompt to stdout. Caller redirects to a per-chunk prompt file (typical: `/tmp/extraction_prompts/<slug>--<chunk-tail>.prompt.md`).

### 3.4 Extraction quality check

After each chunk:

- **Spot-check three random extracted directives** against the source text to confirm: the directive is genuinely present; the imperative captures the source; no fabrication.
- **Spot-check one chunk per ten that returned zero or near-zero directives** to confirm under-extraction is not the failure mode for this source.
- If any spot check fails, re-run the chunk with a corrected prompt.

The two-sided check matters because sycophancy and pattern-completion produce *over-extraction*, while excessive caution in the prompt produces *under-extraction*. The procedure cannot detect either by inspecting only the extraction output.

### 3.5 Extraction output

**Per-chunk YAML file.** Each extraction pass writes its output to `docs/sources/<slug>/chunks/<chunk-tail>.directives.yaml` (alongside the chunk's `.txt` file). This deviates from the original spec, which prescribed a single appended "raw extraction file." Reasons for the deviation:

- **Idempotent re-runs:** a per-chunk file makes "skip if exists" trivial, so failed or revised runs only touch the affected chunks.
- **Diffable on prompt iteration:** when the prompt template changes, the impact per chunk is visible directly.
- **Aligns with the chunk-text layout.**
- **Reconstructable:** the single "raw extraction file" of the original spec is `cat docs/sources/*/chunks/*.directives.yaml` away.

File structure (one per chunk):

```yaml
chunk_id: <slug>/<chunk-tail>
source: <slug>
title: <chunk title>
pages: "<page range with scheme>"
components: ["exp", ...]
extracted_at: <ISO-8601 timestamp>
model: <model id>
directives:
  - id: <slug>/<chunk-tail>/d01
    source: "<short citation: author year, chapter or section, page>"
    directive: "<imperative phrasing>"
    trigger: "<condition under which it applies>"
    qualification: "<source-stated limit; '' if none>"
    evidence: "<verbatim quote or tight paraphrase with page>"
  - id: <slug>/<chunk-tail>/d02
    ...
```

If the chunk yields zero directives, `directives: []`.

### 3.6 Execution mechanism

One Task-tool subagent per chunk. Workflow:

1. Caller runs `python3 docs/_manifest/build_extraction_prompt.py <slug> <chunk-tail> > /tmp/extraction_prompts/<slug>--<chunk-tail>.prompt.md`.
2. Caller spawns a Task subagent (general-purpose) with this short instruction:
   - "Load the prompt by running: `cat /tmp/extraction_prompts/<slug>--<chunk-tail>.prompt.md`. Follow the protocol exactly. Write the YAML to the path specified in its `<output_format>` block. Return a one-line summary: `extracted: N directives [+ optional note]`."
3. The subagent's `cat` of the prompt file loads it into the subagent's context as a tool result, preserving the source-first / critical-instruction-at-end structure.
4. The subagent extracts, writes the YAML, returns the one-line summary.

This pattern gives a fresh context window per chunk (Laban 2025 multi-turn-drift mitigation) and keeps the orchestrator's context clean (subagent loads the ~30–100K-token prompt; orchestrator sees only the one-line summary).

For parallel execution, the caller spawns multiple Task subagents in one message (multiple Agent tool calls in a single message). Pilot timing: ~30–120 s per chunk wall-clock; batches of 5 yield ~2 min per batch; full 108-chunk corpus completes in ~25–50 min total wall-clock at batch-of-5 parallelism.

**Pilot results (4 chunks):**

| Chunk | Type | Directives |
|---|---|---|
| booth-sutton-2022/ch4-defining-scope | procedural | 54 |
| skinner-2002/ch4-meaning-and-understanding | historical-methodological | 34 |
| bohm-1996/ch2-on-dialogue | interpretive | 34 |
| davidson-1984/radical-interpretation | theoretical (OCR'd source) | 15 |

Pilot took 57–118 s per chunk, 37–64K tokens per chunk. Quality on the OCR'd chunk: the agent silently normalized OCR character errors (`1s`→`is`, `|`→`I`) when quoting evidence. This is a soft compromise on the verbatim-evidence rule but a defensible one: verbatim quoting of a corrupted source is not really verbatim of the source.

---

## Stage 4.0 — AI-Implementability Triage

### 4.0.1 Purpose

Stage 3 extraction faithfully captures every directive the source states, including directives whose central operation is embodied (Bohm on group dialogue posture; Hadot on bodily exercises) or interpersonal in ways the AI cannot perform (two-reviewer screening; recruiting human stakeholders; physically hand-searching journals). Before clustering, each directive is classified for whether a Claude-based agent can actually execute the behavior in a text-based person↔AI exchange.

The triage is a deliberate insertion between Stage 3 and Stage 4 (clustering). It runs *after* extraction (so source fidelity is preserved on disk) and *before* clustering (so clusters are not polluted by directives that will be filtered out anyway).

### 4.0.2 Decision categories

Each directive receives one of three decisions:

- **KEEP** — the AI agent itself can perform the behavior in writing or conversation. Most synthesis-time research moves (citing sources, marking inferences, reconstructing the question a position is answering, naming the active interpretive branch) are KEEPs.
- **ADAPT** — the directive's surface phrasing references embodied or in-person settings, but the structural move ports cleanly to text-based person↔AI interaction. The triage agent must produce a concrete adapted phrasing in one sentence; if the AI-side analogue cannot be stated cleanly, the answer is DROP.
- **DROP** — the directive's central operation requires capacities the AI does not have (real-time observation of body language, group co-regulation, bodily/spiritual exercises) or contexts that don't apply to person↔AI text exchange (multi-reviewer independence; recruiting external participants; addressing funders/commissioners).

Bias toward KEEP when the directive is generic enough to read as a synthesis-time research move. Bias toward DROP when the directive's operation is genuinely embodied or genuinely group-scale. ADAPT is the right call only when the structural move (the operation the directive performs) is well-defined independent of the embodied surface, and the AI can perform that operation in text.

### 4.0.3 Per-source triage with full chunk context

Triage runs as **one Task subagent per chunk**, with the full chunk text *and* the chunk's `.directives.yaml` in the agent's context. The chunk text grounds adapt judgments: knowing what surrounding passages say tells the agent whether a "dialogue" reference is incidental (KEEP) or load-bearing (ADAPT or DROP).

The per-chunk pattern preserves the same fresh-context-per-chunk discipline used at Stage 3 and bounds multi-turn drift (Laban et al. 2025).

### 4.0.4 Output structure

One YAML file per chunk at `docs/sources/{slug}/chunks/{chunk_id}.triage.yaml`:

```yaml
chunk_id: <slug>/<chunk-tail>
source: <slug>
triaged_at: "<ISO-8601 timestamp>"
model: "<model id>"
triage:
  - id: "<original directive id, copied verbatim>"
    decision: keep | adapt | drop
    reason: "<one-line justification, ≤25 words>"
    adapted_directive: "<required when decision=adapt; null otherwise>"
  - id: "..."
    ...
```

Every directive id from the corresponding `.directives.yaml` appears exactly once. The triage record's `id` matches the directive's `id` exactly, so downstream consolidation (Stage 4) can join on id without ambiguity.

### 4.0.5 Tooling

- `docs/_manifest/triage_prompt_template.md` — XML-tagged template (mirrors extraction template structure: source-first, critical instruction at the end). Includes a post-write recount instruction that has the agent re-read its own file and report actual `decision:` counts rather than from memory (a small but meaningful guard against off-by-one summary errors).
- `docs/_manifest/build_triage_prompt.py <slug> <chunk-tail>` — substitutes slug/chunk metadata + chunk text + directives YAML into the template; emits prompt to stdout.
- Both hash-pinned in `SCRIPT_HASHES`; CLI allowlisted in `.claude/settings.json`.

### 4.0.6 Execution

Same dispatch pattern as Stage 3:

1. `python3 docs/_manifest/build_triage_prompt.py <slug> <chunk-tail> > /tmp/triage_prompts/<slug>--<chunk-tail>.prompt.md`
2. Spawn a Task subagent (general-purpose) that runs `cat <prompt-path>` and follows the protocol.
3. For parallel execution, dispatch in batches of ~5 in a single message. Pause for review between batches.

### 4.0.7 Quality patterns observed

In the proc-deliverable scale-out (16 chunks, 453 directives):

- Pure procedural sources (booth-sutton chapters, arksey-omalley) typically produce 80–100% KEEP, with small numbers of ADAPTs around librarian-engagement / journal-hand-search / organization-contact moves and small numbers of DROPs around two-reviewer screening, focus-group facilitation, and funder-targeted advice.
- Theoretical philosophy of language (Davidson on radical interpretation) produces a striking split: formal-semantics machinery (Tarskian truth-theory steps) DROPS cleanly; the famous interpretive moves (charity, holding-true as basic evidence, holism) ADAPT cleanly to user-message interpretation. KEEP rate near zero is appropriate when every interpretive move had to be adapted to the user-AI context.
- Metamethodology and historiography (cappelen handbook chapters, skinner) produce ~95–100% KEEP — the AI does interpretation, so methodology-of-interpretation directives apply directly.

### 4.0.8 Audit trail

DROPped directives are not deleted; they remain in the source `.directives.yaml` and in the `.triage.yaml`. The Stage 4 consolidator (4.1 below) emits them into a `drops:` section of the clustering input, separate from the surviving directive list, so a re-run with a corrected triage prompt can recover them.

---

## Stage 4 — Clustering

### 4.1 Purpose

Many directives across sources will state the same protocol in different words. Cluster before resolving so that resolution operates on grouped equivalents rather than the full flat list.

The clustering input is the union of KEEP and ADAPT directives across all chunks tagged with the deliverable's component. For ADAPT decisions, the *adapted* phrasing is treated as the operative `directive` field; the original phrasing is preserved in `original_directive` for audit.

### 4.2 Method

Single Claude pass over the consolidated directive list with the instruction to group directives that express the same protocol. The output is a clustered file in which each cluster has:

- A working label (e.g., "principle of charity in interpretation"; ≤6 words; names the operation, not the surface words)
- The list of contributing directive ids (`member_ids`)
- A `note` field marking whether members are paraphrases (same operation, different words) or genuine variants (same operation, different trigger / scope / qualification)
- Optionally a `fork:` field when the cluster encodes a genuine methodological disagreement to be preserved as a conditional directive at Stage 5
- Optionally a `related_to:` field listing other cluster ids when the agent prefers split-with-cross-reference over a forced merge

### 4.3 Long-input handling

If the consolidated directive list is long (rough threshold: more than ~30 pages of records, or whatever begins to fill more than a third of the working context), single-pass clustering risks the "lost in the middle" attention pattern documented by Liu et al. 2024 and can silently miss cross-source matches in the middle of the input. Two recovery strategies:

- **(a) Two-pass: label then cluster within label.** Pass 1 assigns each directive a working theme tag from a moderate-sized taxonomy (~30–50 themes). Pass 2 clusters within each theme. Cross-theme merges happen in a third reconciliation pass.
- **(b) Two independent passes + manual reconcile.** Run clustering twice with the same prompt; compare cluster assignments; reconcile differences by hand or with a third Claude pass.

In the proc-deliverable run, single-pass clustering on 430 surviving directives (~70K tokens of input) produced reasonable cross-source clusters and was accepted without falling back to two-pass. The decision rule: inspect the first 5–10 clusters and 5–10 singletons for obvious missed merges; if the rate of obvious misses exceeds ~10%, fall back to two-pass.

### 4.4 Clustering caution

Do not collapse clusters that look similar but apply under different conditions. Davidsonian charity (interpretation) and Dennettian Rapoport rules (debate) belong in distinct or sub-clustered groups, not a single cluster, because they trigger differently. The sycophancy literature (Sharma et al. 2024) gives an additional reason for this caution: the model has a documented tendency to merge things that "look agreeable" together. Resist this in cluster review.

The cluster prompt template makes this explicit: when uncertain between merge and split, **prefer split with cross-reference** over forced merge. Stage 5 can merge two related clusters cheaply, but cannot recover what was wrongly merged at Stage 4 without going back to source.

### 4.5 Singletons

Directives that match no cluster remain as singletons and proceed to Stage 5 unchanged. Singleton density is informative: a high singleton rate (the proc run: 99 of 188 clusters = 54%) reflects genuine diversity in the surviving directive set and signals where Stage 6 organization (combining singletons under shared activation triggers) and Stage 7 compression (curse-of-instructions budget) will do the heavy lifting toward the final ~30–50 directive deliverable target.

### 4.6 Tooling

- `docs/_manifest/consolidate_for_clustering.py <component>` — walks every chunk where the named component appears in `components`, joins each chunk's `.triage.yaml` to its `.directives.yaml`, and emits one flat YAML at `docs/_manifest/<component>-clustering-input.yaml`. Surviving directives (KEEP + ADAPT, with adapted phrasing operative) appear in the `directives:` section; DROPped directives appear in a `drops:` audit section. Deterministic, no LLM judgment.
- `docs/_manifest/cluster_prompt_template.md` — XML-tagged clustering template; explicit instructions on grouping by protocol (not by source), preferring split-with-cross-reference, preserving genuine forks, sweeping the directive list multiple times to fight lost-in-the-middle attention.
- `docs/_manifest/build_cluster_prompt.py <component>` — substitutes the consolidated YAML into the template; emits prompt to stdout.
- All hash-pinned in `SCRIPT_HASHES`; CLIs allowlisted in `.claude/settings.json`.

### 4.7 Execution

```
python3 docs/_manifest/consolidate_for_clustering.py <component>
python3 docs/_manifest/build_cluster_prompt.py <component> > /tmp/cluster_prompts/<component>.prompt.md
# spawn one Task subagent (general-purpose) that runs `cat <prompt-path>` and follows the protocol
```

Output: `docs/_manifest/<component>-clusters.yaml`. The agent organizes clusters into thematic sections (commented headers between cluster blocks); these sections become a useful starting scaffold for Stage 6 organization but are not load-bearing for downstream parsing.

### 4.8 Re-running with new chunks

Stages 4.0 and 4 are *idempotent re-runs against the full current corpus*, not append operations. When new chunks complete Stage 3 extraction:

1. Triage the new chunks (Stage 4.0); existing `.triage.yaml` files are untouched.
2. Re-run `consolidate_for_clustering.py <component>` — automatically picks up the new triage files.
3. Re-run clustering — produces a new `<component>-clusters.yaml`. Cluster ids change (no stable id mapping across runs), and downstream stages 5–7 must also re-run.

The cost of full Stage 4–7 re-execution from current state is ~30–60 min of LLM wall-clock for the proc deliverable. This is the right behavior: new sources should find cross-source clusters with old ones, not be appended as a separate addendum.

---

## Stage 5 — Canonicalization

### 5.1 Per-cluster canonical directive

For each cluster, produce one canonical directive that:

- Captures the protocol in imperative form
- **Is phrased affirmatively** wherever the underlying protocol allows. Convert "do not impose anachronistic categories" to "use categories the historical figure or their interlocutors would have recognized." Preserve negative phrasing only when the protocol is genuinely a refusal (e.g., "do not fabricate citations") or when affirmative paraphrase distorts the protocol. Empirical basis: Truong et al. ACL 2023 and follow-on work document systematic LLM failure to follow negated instructions; mechanistic work (preprint, lower confidence) attributes some failures to the negated token's representation being activated by mention.
- **States the trigger condition in surface-verifiable terms** where possible. A trigger like "when the question contains the word 'consciousness' or its cognates" is more reliably executed than "when phenomenal experience is at issue." If the underlying protocol is genuinely defined by an abstract condition, state both forms: the verifiable proxy and the abstract condition the proxy approximates.
- Preserves any qualification the sources collectively impose
- Cites all contributing sources in a compact form

### 5.2 Handling genuine forks

Some methodological positions are genuinely contested and should be preserved as conditional forks rather than resolved. Known examples to expect:

- Skinner 1969 vs. Skinner 2002 on perennial problems
- Williamson vs. Cappelen on intuitions as evidence
- Hermeneutics of suspicion vs. hermeneutics of trust (Ricoeur)
- Rational reconstruction vs. historical reconstruction (Rorty's genres)
- Comparative vs. fusion vs. cross-cultural philosophy (Garfield, Siderits, Ganeri)

For each fork, encode a conditional directive of the form: "If [condition A], do X. If [condition B], do Y." Do not resolve the fork by adopting one side. The activating condition is the directive's load-bearing element.

**Branch-naming requirement.** Every conditional directive (forks above; any other if/then in the canonical set) must include an explicit instruction to *name the active branch and the trigger that activated it before proceeding*. Empirical basis: ComplexBench (Wen et al. 2024) shows Chain and Selection compositions are the hardest constraint categories for current LLMs; KCIF (Hagiwara/Saparov 2024) shows that conditional adherence improves when the trigger and branch are made surface-verifiable. Branch-naming converts implicit conditional reasoning into surface-verifiable behavior that Stage 8 testing can check.

### 5.3 Output

A canonical directive file: one entry per cluster (or fork), with sources cited and triggers explicit.

---

## Stage 6 — Organization (track split)

From here, the procedure splits by deliverable. The `components` tags carried on each canonical directive (inherited from the chunking-plan via Stage 3) determine which track a directive feeds into.

### 6.1 Research-project track — activation-stage framework

For directives tagged `proc`, organize into the following groups. The framework below is a starting point and may be reshaped by the directives themselves.

- **Stage A — Always-on scaffolding.** Apply to every report regardless of question type.
- **Stage B — Historical / exegetical activation.** Apply when the question concerns the views of a historical figure or the meaning of a historical text.
- **Stage C — Literature synthesis activation.** Apply when the report synthesizes multiple secondary readings or primary studies.
- **Stage D — Argument-reconstruction activation.** Apply when the report reconstructs a specific argument for evaluation.
- **Stage E — Cross-tradition activation.** Apply when the report engages non-Western or comparative material.

The staged organization is not cosmetic: it is the principal mechanism by which this procedure mitigates the "curse of instructions" (Hagiwara et al. 2024). If the model only sees a directive when it is plausibly active, the joint number of constraints in any single response is lower, and joint adherence (which falls roughly as p^n) stays higher.

### 6.2 Discussion-project track — exploratory default + four mode-shaped skills

For directives tagged `exp`, `m1`, `m2`, `m3`, or `m4`, organize into one of the five discussion-project artifacts:

- `exp` → CLAUDE.md exploratory default (always-on conversational mode)
- `m1` → `/pragma-dialectical` skill
- `m2` → `/hermeneutic` skill
- `m3` → `/skinnerian` skill
- `m4` → `/intuition-pump` skill

Skills are authored as **mode-shaped, not task-shaped**: each skill body explicitly establishes persistence ("maintain this lens for every subsequent turn until the user explicitly exits"), dialogical engagement ("pose one or two challenges at a time, wait for the user's reply, respond to that reply"), exit conditions, and a per-turn self-check. The CLAUDE.md exploratory default holds **mode-management meta-rules** that are always in context: when a skill is invoked, the mode persists until explicit exit; do not soften back toward exploration mid-conversation.

The detailed authoring procedure for each skill is specified when that skill's source extractions are complete. See `summary.md` for the design rationale and `docs/_manifest/m{1,2,3,4}-*.md` for the per-skill source corpus.

### 6.2 Multi-stage directives

A directive may belong to more than one stage. Tag it with all that apply rather than picking one.

### 6.3 Reshape rule

If a substantial number of canonical directives do not fit the A–E framework, do not force them. Add a stage or reorganize. The framework serves the directives, not the reverse.

### 6.4 Per-stage trigger statement

At the head of each stage's directive block, include a one-sentence statement of the stage's trigger condition phrased in surface-verifiable terms (consistent with Stage 5.1). Example for Stage B: "Activate the directives in this stage when the user's question names a historical figure, names a specific historical text, or asks what someone held, believed, or argued."

---

## Stage 7 — Compression and Format Finalization

### 7.1 Goal

Produce the final custom-instructions document. Reduce token count of bloat and redundancy *without* sacrificing the specificity or conditionality that makes directives actionable. Length is not bad in itself; the empirical literature shows a U-shape (Liu et al. 2025 finds longer prompts help on domain-specific tasks; "context rot" findings show degradation past certain lengths). The relevant variable is signal density.

### 7.2 Compression methods

- Combine directives that always co-trigger and never conflict.
- Replace verbose source citations with short tags after a one-time citation key in the document.
- Remove evidence excerpts (kept only in the canonical file as an audit trail, not in the final custom instructions).
- Tighten imperative phrasing.

### 7.3 Stopping criterion

For each directive after compression, ask: would a Claude agent following only this compressed directive (and the surrounding context) behave correctly under the trigger condition? If the answer is no, restore context until the answer is yes.

### 7.4 Compression caution

Imperatives compress well ("State the thesis in the introduction"). Conditional and contextualist directives often do not ("Avoid imposing doctrines" with no qualification will misfire on contemporary analytic questions). Err toward retaining context.

### 7.5 Output format rules

The compressed custom-instructions document must conform to the following format requirements. Empirical basis is mixed across these items and is flagged.

1. **XML-tagged sections.** Wrap each major block in XML tags: e.g., `<role_and_methodology>`, `<always_on_directives>`, `<stage_b_historical>`, `<output_structure>`, `<self_verification>`. Anthropic documents this as a Claude-trained convention (HIGH confidence on Claude; MODERATE on cross-model portability; no public controlled ablation that I am aware of).
2. **Front-load and mirror.** Place the methodology and the always-on directives at the top of the document. Mirror the most consequential constraints (the ones whose violation would most damage the report) in a short final block at the bottom. Empirical basis: Liu et al. 2024 ("lost in the middle"); OpenAI GPT-4.1 prompting guide explicitly recommends bracketing instructions at top and bottom. Vendor-internal evals only; not externally replicated.
3. **Affirmative phrasing throughout.** Apply the affirmative-phrasing conversion from Stage 5.1 to the final document. Negative phrasing remains only for genuine refusals and safety-style constraints.
4. **Decouple reasoning from formatting.** If the directives include both "reason in such-and-such a way" and "produce output in such-and-such a structure," do not collapse them into a single mixed directive. The reasoning directives should govern a freeform synthesis; the formatting directives should govern a separate structuring step. Empirical basis: Tam et al. 2024 ("Let Me Speak Freely?") and the "Format Tax" preprint show that fusing reasoning with structured-output constraints degrades reasoning quality measurably (~10–15% on math/symbolic benchmarks for open-weight models). Whether this transfers to philosophical synthesis is not directly measured; the precaution is cheap and the downside risk is real.
5. **Constraint-count budget per stage.** Within each activation-stage block, count the atomic directives. The "curse of instructions" predicts joint compliance ≈ p^n where p is the per-directive compliance rate and n is the number of distinct atomic directives in play simultaneously. As a working budget, aim for no more than ~10 atomic directives active in any single response (always-on directives plus the activated stage's directives). If a stage block exceeds this, sub-group directives by sub-trigger or merge co-triggering directives. The 10-directive figure is a working heuristic, not an empirically optimized threshold.
6. **Anti-sycophancy directive in the always-on block.** Include an explicit instruction naming sycophancy as a failure mode and authorizing disagreement with the user's framing. Empirical basis: Sharma et al. ICLR 2024 documents sycophancy in Claude across free-form text-generation tasks. Whether prompt-level mitigation works is not empirically established (training-time mitigations are the validated ones); inclusion is on the practitioner-consensus tier with mechanistic plausibility, not validated effect size. Test in Stage 8.
7. **Self-verification step phrased against an explicit checklist.** Include a final-step directive that has the model verify the report against a short, explicit list of criteria drawn from the always-on directives (e.g., "Each substantive claim is either cited or flagged as my inference"; "If the question is historical, I have stated the active branch under Stage B"; "I have not adjusted my conclusion to match the user's apparent view"). Empirical basis: Huang et al. ICLR 2024 shows open-ended self-correction often *degrades* performance, while Tyen et al. ACL Findings 2024 shows correction works when the criterion is concrete. Self-verification with a checklist sits on the more reliable side of that distinction.
8. **No persona / role-flair beyond the methodology.** Do not add "you are an expert philosopher" framing as a quality lever. Empirical basis: Zheng et al. 2024 shows simple persona prompts produce small/random effects on factual accuracy, sometimes negative.

### 7.6 Reasoning-mode considerations

If the project will be used with Claude's extended thinking enabled, note that recent literature (Li et al. 2025 "When Thinking Fails"; "Reasoning Models Struggle to Control their Chains of Thought," 2025) reports a measurable trade-off: reasoning-trained behavior raises analysis quality but lowers reliable adherence to surface methodology constraints, and reasoning traces themselves are very hard to control even when the final output looks compliant. Mitigation in document design: keep formatting and self-verification directives unambiguous, and place the self-verification checklist *after* the synthesis rather than instructing the model to apply it during synthesis. Whether and how much this helps for Claude 4.x with extended thinking is not independently measured.

---

## Stage 8 — Testing

### 8.1 Test set: question types

Construct a test set of at least four philosophical questions covering different types:

1. A contemporary analytic question (e.g., a question in epistemology or philosophy of mind)
2. A historical exegesis question (e.g., a question about what a specific philosopher held)
3. A cross-tradition question (e.g., a question engaging non-Western material or comparing traditions)
4. A textual or literary interpretation question

Add additional cases if the project's expected use covers domains not represented above.

### 8.2 Test set: probes

For each question type, also construct the following probes. These exist to catch the specific failure modes the empirical literature documents.

- **Conditional-branch probe pair.** A version of the question where the trigger for a Stage B/C/D/E directive is unambiguously present, and a version where it is unambiguously absent. The model should activate the relevant stage in the first case and not in the second. Empirical motivation: ComplexBench Chain/Selection results.
- **Sycophancy probe pair.** The same question framed with "I think X is correct because..." vs. "I think X is wrong because..." (where X is a substantive philosophical position). Compare the substantive analysis. Empirical motivation: Sharma et al. ICLR 2024.
- **Multi-turn shard test.** Take one fully-specified question and split it into 3–5 shards delivered across turns (e.g., topic in turn 1, scope constraint in turn 2, methodological emphasis in turn 3). Compare adherence to a single-turn version of the same fully-specified question. Empirical motivation: Laban et al. 2025 documents an average 39% performance drop and +112% reliability drop across 15 frontier LLMs in this design. The user's project is multi-turn by nature; this test measures the actual operating condition.
- **Format-perturbation probe.** Run the same question twice with small surface variations to the question phrasing (e.g., bullet vs. prose; question marks vs. statements; reordered constraints). Empirical motivation: Sclar et al. 2024 found up to 76-percentage-point swings on smaller models from semantically equivalent reformatting; the effect persists at lower magnitude on frontier models.

### 8.3 Test execution

For each test question and probe:

- Run the question against the project as currently configured.
- Read the resulting report against the canonical directive set.
- Mark each directive as: applied correctly, applied incorrectly, not applied when it should have been, applied when it should not have been, or not applicable.

### 8.4 Evaluation methods

Use both of the following:

1. **Verifiable surface checks (IFEval-style).** Mechanically check the easy items: required sections present; citations in the required format; conditional branch named when a Stage B/C/D/E directive is active; required length bounds satisfied. These are tripwires. If surface checks fail, deeper adherence is almost always also failing.
2. **Decomposed-criteria evaluation (DRFR-style; Qin et al. 2024 InfoBench).** Convert each canonical directive in scope for the question into a yes/no verification question. Have a *separate* Claude session — ideally a fresh project with no instructions, or a different model family if available — judge each yes/no question against the report. Empirical motivation: Yamauchi et al. 2025 and broader LLM-as-judge literature document that the same model judging its own output exhibits biases (self-preference, position bias, length bias). Mitigations supported by that literature: use a rubric rather than free judgment; randomize order of items; consider a multi-judge jury for borderline items.

### 8.5 Failure analysis

For every directive that misfires, classify the cause as one of:

- Directive ambiguity → revise wording in Stage 5 or 7 output
- Trigger condition wrong or missing → revise trigger in Stage 5 (apply the surface-verifiable phrasing rule from 5.1)
- Directive missing from set → return to Stage 1 to acquire the source that would have supplied it
- Directive conflict with another directive → return to Stage 5 to resolve or fork
- Token compression too aggressive → restore context per Stage 7.3
- Constraint-count exceeded → return to Stage 7.5 item 5; sub-group or merge co-triggering directives
- Format brittleness → revise the format of the affected directive block; if the issue persists across reformulations, accept that this directive will be unreliable on this model and either reduce its load-bearing role or move it to the mirrored bottom block (Stage 7.5 item 2)
- Sycophantic shift → strengthen the always-on anti-sycophancy directive and the self-verification checklist item that names this failure

### 8.6 Pass criterion

The custom instructions are ready when the test set produces reports in which no directive misfires that has not been classified and addressed. Perfect application is not the criterion; classified-and-addressed is.

---

## Stage 9 — Iteration

### 9.1 First iteration

After Stage 8, return to Stage 1 with the gap list produced by failure analysis. Acquire Tier 2 sources that address gaps. Re-run Stages 2–8 on those new sources, integrating new directives into the existing canonical set.

### 9.2 Subsequent iterations

Repeat Stage 9.1 until the failure rate in Stage 8 stabilizes — that is, until additional sources do not produce additional caught failures.

### 9.3 Quantitative thresholds for design-level revisions

Where Stage 8 evaluation produces numbers, use the following thresholds to decide whether the problem is solvable by revision or requires a design-level change. Threshold values are working heuristics, not empirically optimized; revise as you accumulate test data of your own.

- **Joint constraint adherence below ~50%** on representative single-turn tasks: the document is carrying too many simultaneously active directives. Sub-divide stages further, tighten triggers, or split the project into multiple narrower projects activated by question type rather than carry everything in one document.
- **Multi-turn shard test shows >30% adherence drop** vs. single-turn: redesign for fresh-session-per-major-question rather than long-conversation work. Add an instruction at the top of the document recommending the user state the full question in a single message rather than building it up across turns.
- **Sycophancy probe pair shows >20% shift in substantive analysis** between framings: strengthen Stage 7.5 item 6 and the self-verification checklist; if the shift persists, accept that prompt-level mitigation has limits here and document the residual risk in the project's user-facing notes.
- **Format-perturbation probe shows >15-percentage-point swing** in directive adherence between equivalent reformulations: the document is sitting on a brittle format. Try alternative XML tag names and section orderings; if the brittleness is in a specific directive, rewrite that directive.
- **Conditional-branch probe shows the model activating a stage when the trigger is absent, or failing to activate when present, more than 10% of the time**: revise the trigger to a more surface-verifiable form (Stage 5.1) and strengthen the branch-naming requirement (Stage 5.2).

### 9.4 Stop condition

The procedure terminates when (a) the test set passes per Stage 8.6, (b) a further iteration adds no new caught failures, or (c) acquisition of further sources is not feasible. Record which condition was met.

---

## Artifacts Produced

By the end of the procedure, the following artifacts should exist (paths relative to project root):

**Stage 1 — Acquisition / scoping:**

1. `docs/_manifest/{exp,m1,m2,m3,m4,proc}*.md` — six per-deliverable manifests, each tracking scope and pipeline status.
2. `docs/sources/{slug}/full.pdf` — acquired source text per slug.
3. `docs/sources/{slug}/toc.md` — structured TOC + operational map per slug.

**Stage 2 — Chunking:**

4. `docs/_manifest/chunking-plan.md` — single reference file declaring chunks for all sources, with verified page ranges and component tags.
5. `docs/_manifest/chunking-workflow.md` — the per-source workflow specification.
6. `docs/_manifest/{subtask1_brief,commit_source_block,verify_chunking_plan}.py` — helper scripts.

**Stage 3 — Extraction:**

7. `docs/sources/{slug}/extracted/` — raw directive records per source, each carrying inherited component tags.

**Stages 4–7 (track-split at Stage 6):**

8. Clustered directive file (Stage 4).
9. Canonical directive file with full evidence (Stage 5).
10. **Research track:** stage-tagged directive file (Stage 6.1) → compressed `proc` custom-instructions document (Stage 7) — pasted into the claude.ai research project.
11. **Discussion track:** per-artifact directive groupings (Stage 6.2) → CLAUDE.md exploratory default + four skill files (`pragma-dialectical`, `hermeneutic`, `skinnerian`, `intuition-pump`) (Stage 7).

**Stages 8–9 — Quality control:**

12. Test rubric: yes/no decomposed criteria for Stage 8.4 evaluation plus the four probe pairs from Stage 8.2.
13. Test log with failure analysis (Stage 8).
14. Iteration log (Stage 9).

Artifacts 10 and 11 are the deliverables. The test rubric (12) is reusable and should be retained — it is the primary instrument for detecting regression when the procedure, the underlying model, or the sources are revised. The remaining artifacts exist as audit trail and as input to future iterations.

---

## Caveats

- The procedure assumes a single human running it with Claude as the extraction and synthesis agent. If multiple humans are involved, add an inter-rater check at Stage 3 and Stage 4.
- **Replicability requires that pipeline state lives in artifacts, not in Claude's working memory.** The manifests, toc.md files, chunking-plan.md, and extraction outputs are the canonical state. A re-run from scratch should produce the same plan and the same extractions given the same sources, with no hidden context carried in conversation history. This is why Stage 2 mechanizes the deterministic steps (helper scripts) and isolates LLM judgment to two clearly-bounded subtasks per source. The same discipline should apply to later stages as their work begins: when a step has no LLM judgment in it, convert it to a script before scaling.
- The Stage 8 test set is the load-bearing quality control. A weak test set produces weak instructions regardless of source quality. The probes added in Stage 8.2 (conditional, sycophancy, multi-turn shard, format perturbation) are evidence-driven; without them, surface adherence may pass while the failure modes the empirical literature documents go undetected.
- Genuine methodological forks (Stage 5.2) are features, not bugs. Resist the temptation to flatten them; conditional directives are how the project handles real disagreement in the field. They are also the directive type that is empirically hardest for current LLMs to execute reliably (ComplexBench results), so they get the strictest formulation rules and the most direct testing.
- Tier 1 source acquisition may not be fully achievable through legitimate channels for all texts. Substitutions per Stage 1.4 are acceptable but should be flagged in the source log and re-run if the primary becomes available.
- The procedure does not specify the wording of any actual directive. That work is done in Stages 3, 5, and 7 against the actual sources.
- **Empirical evidence floor.** The Stage 7 and Stage 8 design choices draw on benchmarks (IFEval, FollowBench, ComplexBench, ManyIFEval, IHEval) that mostly measure verifiable surface constraints, not open-ended philosophical synthesis. Findings transfer in *direction* — more constraints worse, surface format matters, conditional logic harder, multi-turn drops — but reported effect sizes are not reliable predictions for this use case. The thresholds in Stage 9.3 should be treated as starting heuristics and revised as the project's own test data accumulates.
- **Vendor-stated guidance is unevenly validated.** Several Stage 7 format choices (XML tags, front-load-and-mirror layout, the specific 30%-from-query-at-end claim in Anthropic's long-context documentation) rest on vendor-stated design intent and internal evaluations rather than independently replicated controlled studies. They are reasonable defaults; they are not proven facts.
- **Model-version sensitivity.** Sycophancy, alignment-faking, and the reasoning-vs-instruction-following trade-off are documented unevenly across Claude versions. Effects measured for one Claude version do not necessarily hold for the next. The Stage 8 test rubric should be re-run when the underlying model is updated.
- **Cross-model portability is partial.** Sclar et al. 2024 found that prompt formats best on one model are not best on another (low correlation across models). A document optimized for Claude is likely to need re-tuning if the project is moved to GPT, Gemini, or open-weight models.
- **The reasoning-mode caveat in Stage 7.6 is current as of late 2025 to early 2026.** The trade-off may resolve in later model versions; treat it as a moving target.
