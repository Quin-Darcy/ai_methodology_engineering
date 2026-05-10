# Procedure: Constructing Custom Instructions for Philosophy Research and Discussion Projects

**Purpose.** Specify the procedure for converting authoritative methodological literature in philosophy and adjacent fields into deployable Claude artifacts: (1) custom instructions for a claude.ai *research project* that produces literature-review-style philosophical research reports, and (2) a Claude Code *discussion project* consisting of a CLAUDE.md exploratory default plus four mode-shaped critic skills (pragma-dialectical, hermeneutic, Skinnerian, Dennettian).

**Scope.** Source acquisition, per-source TOC summarization, chunking, per-chunk directive extraction, clustering, canonicalization. From Stage 6 onward (organization, compression) the procedure splits into a research-project track and a discussion-project track; testing and iteration (Stages 8–9) recombine. The procedure does not cover the choice of which deliverables to build or which methodological traditions to include — that decision is recorded in `summary.md`.

**Status.** Stages 1–2 reflect implementation as it currently stands and are walked end-to-end against an active corpus of 29 sources in `docs/sources/` and six per-deliverable manifests in `docs/_manifest/`. Stages 3–9 retain the original specification; they are revised when their work begins. Replicability requires that manifests, toc.md files, and `chunking-plan.md` carry the canonical pipeline state — not Claude's working memory across conversations.

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

- `subtask1_brief.py <slug>` — emits a self-contained Subtask 1 prompt to stdout. Workflow context inlined; manifest stanzas for this slug grepped in; toc.md inlined. Replaces ~13 redundant file reads per iteration with zero.
- `commit_source_block.py <slug> --stdin` — accepts the verified block on stdin, inserts/replaces at the correct alphabetical position in `chunking-plan.md`, runs the verifier, ticks the workflow checkbox. Idempotent. Exit codes distinguish input-validation failure (1) from verifier failure (2).
- `verify_chunking_plan.py` — parses `chunking-plan.md` and runs the checks in 2.6. Standalone; also invoked automatically inside `commit_source_block.py`.

These scripts mechanize the steps that have no LLM judgment in them. Iteration cost drops from five hand-driven steps per source (dispatch ×2 + edit + verify + tick) to three (dispatch ×2 + commit-CLI), with steps 1 and 3 fully deterministic.

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

For each chunk declared in chunking-plan.md: file opens; text is selectable (not scanned image); pagination intact. OCR any scanned material before extraction. The verifier handles structural checks; OCR quality is a manual confirmation.

### 2.8 Chunk file naming (Stage 3 input)

When chunks are physically extracted at Stage 3, name them `{author_last}_{year}_{shortwork}_ch{N}.pdf` (example: `skinner_2002_visions_ch4.pdf`). Extraction is lazy: chunks are carved from `full.pdf` at Stage 3 time using the page ranges in chunking-plan.md, not preemptively at Stage 2.

---

## Stage 3 — Per-Chunk Directive Extraction

### 3.1 Extraction is one Claude pass per chunk

The chunks to extract are exactly those declared in `chunking-plan.md`. Do not extract from sections not declared there; do not merge chunks. Per-chunk extraction is necessary for accurate source attribution and for staying within useful context limits. It also bounds the multi-turn drift documented in Laban et al. 2025: each extraction is a fresh single-turn task with the full source in front of the model.

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

The prompt to Claude for each chunk should:

1. Be wrapped in XML tags by section (`<source_information>`, `<task>`, `<output_format>`, `<rules>`). Claude is trained to recognize XML tags as a prompt-organizing mechanism (Anthropic documentation; HIGH confidence on Claude, MODERATE on cross-model portability).
2. Specify the source of the chunk being processed.
3. Instruct that only directives explicitly stated or directly entailed by the text be extracted; nothing imported from general knowledge.
4. Require imperative phrasing, faithful to the source.
5. Require the trigger condition to be stated even when the directive is "always-on" — this forces explicit acknowledgement of conditionality.
6. Require qualifications to be lifted from the text itself, not added from elsewhere.
7. Forbid synthesis or merging at this stage. Merging happens in Stage 4.
8. Output as structured records (JSON or a strict markdown table).
9. Place the source chunk content first and the extraction instructions immediately after it; mirror the most critical instruction (faithfulness to source) at the very end of the prompt. This is the documented mitigation for "lost in the middle" attention bias on long inputs (Liu et al. 2024; OpenAI GPT-4.1 prompting guide).
10. Explicitly authorize the model to return zero directives for a chunk that contains none. The default failure mode under sycophancy and pattern-completion pressure is over-extraction (finding "directives" because the user appears to want them). Naming this failure mode in the prompt is a practitioner mitigation; it is not empirically validated as a sycophancy fix.

### 3.4 Extraction quality check

After each chunk:

- **Spot-check three random extracted directives** against the source text to confirm: the directive is genuinely present; the imperative captures the source; no fabrication.
- **Spot-check one chunk per ten that returned zero or near-zero directives** to confirm under-extraction is not the failure mode for this source.
- If any spot check fails, re-run the chunk with a corrected prompt.

The two-sided check matters because sycophancy and pattern-completion produce *over-extraction*, while excessive caution in the prompt produces *under-extraction*. The procedure cannot detect either by inspecting only the extraction output.

### 3.5 Extraction output

Append all extracted directive records into a single file (the "raw extraction file"). This file is the input to Stage 4.

---

## Stage 4 — Clustering

### 4.1 Purpose

Many directives across sources will state the same protocol in different words. Cluster before resolving so that resolution operates on grouped equivalents rather than the full flat list.

### 4.2 Method

Run a Claude pass over the raw extraction file with the instruction to group directives that express the same protocol. The output is a clustered file in which each cluster has:

- A working label (e.g., "principle of charity in interpretation")
- The full set of source-attributed directive records belonging to the cluster
- A short note on whether the cluster contains genuine variants (different conditions or scopes) or only paraphrases

### 4.3 Long-input handling

If the raw extraction file is long (rough threshold: more than ~30 pages of records, or whatever begins to fill more than a third of the working context), do not attempt clustering in a single pass. Either (a) split the file into thematic shards by an initial labeling pass and cluster within shards, then merge across shards in a second pass, or (b) run two independent clustering passes and reconcile differences manually. Single long passes are subject to the "lost in the middle" attention pattern documented by Liu et al. 2024 and can silently drop directives located in the middle of the input.

### 4.4 Clustering caution

Do not collapse clusters that look similar but apply under different conditions. Davidsonian charity (interpretation) and Dennettian Rapoport rules (debate) belong in distinct or sub-clustered groups, not a single cluster, because they trigger differently. The sycophancy literature (Sharma et al. 2024) gives an additional reason for this caution: the model has a documented tendency to merge things that "look agreeable" together. Resist this in cluster review.

### 4.5 Singletons

Directives that match no cluster remain as singletons and proceed to Stage 5 unchanged.

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
