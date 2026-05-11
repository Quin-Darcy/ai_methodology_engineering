# Project Summary

## Goal

Build two artifacts for working philosophy as a serious autodidact: (1) a procedural research-and-report tool, and (2) a philosophical interlocutor that supports both open-ended exploration and rigorous pressure-testing. Both artifacts should themselves conform to evidence about LLM instruction-following (Sclar, Hagiwara, Wen, Laban, Truong, Huang, Sharma — already cited in `procedure.md`). The methodology is also a research artifact in its own right: a documented attempt to convert authoritative methodological literature into reliable Claude behavior, with the architecture chosen to make that conversion testable.

## Deliverable 1 — Research project (claude.ai)

**Architecture:** slim-core project custom instructions + long-form procedure document + source corpus, all on claude.ai/projects.

- **Custom instructions (slim core, ~1–3k tokens):** non-negotiables only — anti-sycophancy, citation discipline, refusal to overclaim, "scaffolding not authority" framing, and an instruction to load the procedure document at the start of any research task. Short for a reason: the curse of instructions (Hagiwara) means the always-on layer must be tight to preserve adherence.
- **Procedure document (in project knowledge):** the long form — phase protocols, source-ecology guidance, tradition-selection step, output template. Loaded at the start of each research task.
- **Source corpus (in project knowledge):** sources accumulate across conversations as you acquire them.

**Two-phase workflow per research task:**

- *Phase 1 — discovery + initial report.* Web search identifies the relevant source texts; agent produces an initial report explicitly flagged as provisional. Phase 1 procedures focus on **question formulation, source ecology (SEP-first, journal hierarchy, primary > secondary), and tradition recognition** — the high-impact philosophy-specific moves that don't require having the source texts in hand. Recommendation: write phase 1 procedures *thin* first, test on a few representative questions, and thicken only where you see specific failures.
- *Phase 2 — source-text revision.* You acquire the texts identified in phase 1, add them to project knowledge, and ask the agent to revise. Same conversation, but the v2 prompt explicitly names anchoring bias: "treat the v1 report as a hypothesis to be tested against these texts, not a baseline to confirm; identify where v1 was wrong, vague, or missed nuance." Phase 2 procedures focus on **charitable interpretation, tradition-appropriate close reading, Skinnerian historiographical caution, dialectical synthesis, and final output structure** — the philosophy-specific moves that require primary engagement. Worth writing fully now.

**Tradition stance: question-driven.** No default lens. The procedure includes an early tradition-selection step: given the question, identify which tradition(s) the question lives in (analytic, continental-hermeneutic, historiographical) and adopt those evidentiary norms.

**Report structure (mandatory sections beyond the body):** inline citations with short direct quotation for every nontrivial claim; a "weak claims and remaining uncertainty" section; a "what to read next" section; explicit framing of the report as scaffolding rather than verdict. These instantiate the four verification mechanisms committed to (traceable citation, cross-checking, skeptic flagging, scaffolding-not-authority).

## Deliverable 2 — Discussion project (Claude Code)

**Why Claude Code, not claude.ai:** the discussion project's architecture is exploratory default + four invokable analytical modes. Claude Code's skill mechanism is designed for exactly this — explicit, scoped invocation of a specialized procedure. claude.ai has no equivalent; faking it with trigger-phrases and referenced documents is workable but unreliable, and the agent will drift back to default mid-critique. The cost of the platform split is the cross-platform handoff (export the report and source texts from claude.ai, drop them in a directory, run Claude Code there), but manual handoff between projects was already accepted, so this is the same handoff in a different shape.

**Architecture:**

- **Project CLAUDE.md (exploratory default):** the rigorous-exploration interlocutor. Engages charitably with ill-formed ideas; helps articulate vague intuitions into precise formulations; surfaces implicit assumptions without weaponizing them; suggests what's promising or non-obvious; pushes back as "here's where this might run into trouble," not as adversarial gotcha; refuses pseudo-precision; anti-sycophantic but not adversarial; runs lightweight Dennettian hygiene throughout (the "surely" klaxon, deepity detection — these don't require a thesis to apply). Also holds **mode-management meta-rules** that are always in context: if a critic-mode skill is invoked, the mode persists until the user explicitly exits; do not soften back toward exploration mid-conversation.
- **Four mode-shaped skill files:**
  - `/pragma-dialectical` — van Eemeren's procedural rules + Walton's argumentation schemes and critical questions. Invoked when there's a defendable standpoint with identifiable premises.
  - `/hermeneutic` — Gadamer/Ricoeur close-reading. Invoked when a text or passage is on the table for interpretation.
  - `/skinnerian` — contextual reconstruction. Invoked when a position is being attributed to or interpreted from a historical figure.
  - `/intuition-pump` — Dennett-style thought-experiment stress test. Invoked when the argument leans on a hypothetical.

**Skills authored as mode-shaped, not task-shaped.** Default skill behavior (read body, dump analysis, exit) is not what's wanted. Each skill body must explicitly establish: persistence ("maintain this lens for every subsequent turn until the user explicitly exits"), dialogical behavior ("pose one or two challenges at a time, wait for the user's reply, respond to that reply"), exit conditions ("only exit on signals X, Y, Z"), and a per-turn self-check ("am I still applying the lens? if drifting, recommit"). Reliability is moderate — multi-turn drift is real — and the practical pattern is: invoke, sustained dialogue, occasional re-anchoring as needed, explicit exit.

**Mode transition pattern:** the exploratory interlocutor flags candidate transitions ("this looks articulated enough for pragma-dialectical pressure-testing — want to invoke that?") but never forces them. The user decides and explicitly invokes.

## End-to-end workflow

1. A question or topic emerges.
2. Start a new conversation in the claude.ai research project. Agent loads the procedure document and runs phase 1 — produces an initial report from web sources, with bibliography of texts to acquire.
3. Acquire the source texts. Upload them to the project's knowledge.
4. In the same conversation, ask the agent to run phase 2 with explicit anti-anchoring framing. Agent reads the texts and revises the report, generating a final document with mandatory citation, weak-claims, and further-reading sections.
5. Download the report and source texts. Drop them into a directory on your machine.
6. `cd` into that directory and start Claude Code. CLAUDE.md activates the exploratory interlocutor as default.
7. Discuss, explore, develop ideas. The interlocutor flags moments when ideas are critic-ready.
8. When ready, invoke a mode skill (`/pragma-dialectical`, `/hermeneutic`, `/skinnerian`, or `/intuition-pump`). The agent enters that mode, sustains it dialogically, grills you, you answer and revise. Exit when done.
9. Iterate between exploration and critic modes until the argument meets the standard.

## Failure modes the design addresses

- *Generic textbook summary* — phase 2 source engagement and dialectical synthesis structure force substantive moves over rehearsal.
- *Sycophantic agreement* — anti-sycophancy in slim-core custom instructions; phase 2 anti-anchoring framing; critic-mode skills explicitly designed to push back.
- *Vague hedging* — tradition-selection step forces the agent to commit to evidentiary norms; report structure forces taking positions in the synthesis.
- *Missing critical nuances from skipped reading* — phase 2's hard rule that any claim not traceable to in-context source text is dropped or marked pending verification.
- *Missing canonical authors / distinctions* — phase 1 source-ecology guidance + tradition recognition + the SEP-first heuristic.

## Cross-cutting implementation principles (from the LLM-research-grounded meta-requirement)

- Front-load the slim, always-on layer; push elaboration into referenced documents (Hagiwara on curse of instructions; Sclar on prompt-format brittleness).
- Prefer positive directives over negation (Truong).
- Pick a fixed structural format for each artifact and hold it constant across versions, so format-brittleness doesn't confound A/B tests against the lightweight baseline.
- Test artifacts on the actual task — Stage 8 of `procedure.md` — not on prose quality. They decouple.
- Plan for multi-turn drift (Laban) — re-anchor in long sessions, especially when a mode skill is active.

## Open items, deferred to implementation time

- **Report length norms** — short brief vs. medium vs. long. Probably variable, calibrated to the question, with the procedure suggesting ranges.
- **Format:** essay-style vs. PRISMA-ScR-style explicit method section vs. hybrid. Probably hybrid: short formal method/scope section, essay-style synthesis, formal weak-claims and further-reading sections.
- **Trigger and exit phrasings** for the four skills — pure naming convention, settled when authoring.

## Implementation status (as of 2026-05-11)

- **Stage 1** (acquisition, manifests, TOC summarization): complete for 29 sources. Manifests in `docs/_manifest/`; per-source toc.md files with operational maps.
- **Stage 2** (chunking): **complete — 108 chunks across all 29 sources verified.** Output: `docs/_manifest/chunking-plan.md`. Per-source iteration via `docs/_manifest/chunking-workflow.md` with helper scripts. Iteration checklist (all 29 ticked) at the bottom of `chunking-workflow.md`. 14 verifier warnings remain — all non-blocking.
- **OCR**: complete for all 3 image-only PDFs (`davidson-1984-inquiries`, `eemeren-grootendorst-snoeck-henkemans-2002-argumentation-aep`, `wittgenstein-1953-philosophical-investigations`). Originals at `full.pdf`; OCR'd at `full.ocr.pdf`; chunking-plan.md `pdf_path` updated.
- **Stage 2.8** (chunk-text extraction): **complete — 108 of 108 chunks extracted** to `docs/sources/<slug>/chunks/<chunk-tail>.txt` (~7.4 MB total). Mechanized as `docs/_manifest/extract_chunk_text.py`. Pipeline handles all four page schemes (book/pdf/bekker/section_number) and OCR'd PDFs.
- **Stage 3** (per-chunk directive extraction): **24 of 108 chunks complete** (4 pilot + 20 mass-run across 4 batches). Architecture: Task-tool subagents per chunk, each loading a pre-built prompt file (~30–100K tokens) via `cat`, writing a per-chunk YAML output. Prompt template at `docs/_manifest/extraction_prompt_template.md`; prompt-build helper at `docs/_manifest/build_extraction_prompt.py`. Per-chunk output: `docs/sources/<slug>/chunks/<chunk-tail>.directives.yaml` (deviation from the original spec's single raw-extraction-file; rationale in `procedure.md` 3.5). 84 chunks remain.
- **Stage 4.0 — AI-implementability triage**: **complete for all 16 `proc`-tagged chunks among the 24 done at Stage 3.** New step inserted between extraction and clustering: each directive classified `keep` (AI can perform it) / `adapt` (rephrase for person↔AI context) / `drop` (requires capacities AI lacks). Driven by the user-stated criterion that any final directive must be something an AI agent can actually implement; in-person dialogue / group / embodied directives that don't have a clean person↔AI analogue are dropped. Per-chunk output: `docs/sources/<slug>/chunks/<chunk-tail>.triage.yaml`. Tooling: `triage_prompt_template.md` + `build_triage_prompt.py`. Same per-chunk Task-subagent dispatch pattern as Stage 3. Proc result across 16 chunks / 453 directives: 388 keep / 42 adapt / 23 drop. Drop concentrations are predictable (Davidson's Tarskian truth-theory machinery; Booth-Sutton focus-group / interview directives; two-reviewer screening). Quality reviewed by user, approved.
- **Stage 4 (clustering)**: **complete for `proc` deliverable.** 430 surviving directives → 188 clusters (99 singletons; 4 large 10–12-member clusters representing canonical themes). Single Claude pass over the consolidated input (~70K tokens) with `cluster_prompt_template.md`. Agent organized clusters into 13 thematic sections that map cleanly onto the Stage 6.1 activation-stage framework (sections 1–8 = literature-synthesis procedural; 9–10 = historical/exegetical; 11 = argument-reconstruction (disagreement epistemology); 12 = political-theory methodology; 13 = mixed Davidson). Tooling: `consolidate_for_clustering.py` + `cluster_prompt_template.md` + `build_cluster_prompt.py`. Output: `docs/_manifest/proc-clusters.yaml`. **Note on re-running with new chunks**: Stages 4.0 and 4 are idempotent re-runs against the full current corpus, not append operations. When more chunks complete Stage 3, re-triage just the new chunks, then re-run consolidate + cluster (and downstream Stages 5–7) against the full union.
- **Stages 5–9**: not started. `procedure.md` Stages 1–4 (including new 4.0) reflect implementation; Stages 5–9 retain the original spec.

## Suggested next steps

1. **Complete `proc` through Stages 5–7 to produce a draft custom-instructions document.** Three-pass pipeline: canonicalize the 188 clusters into 188 canonical directives (one per cluster, plus genuine forks); organize into Stages A–E (always-on / historical / synthesis / argument-reconstruction / cross-tradition); compress under the 10-directive-per-stage budget. Each stage gets its own template + builder scaffolding mirroring Stages 3, 4.0, 4. Estimated wall-clock: ~30–60 min for the three LLM passes.
2. **Review the proc draft.** This is the deliverable's first end-to-end deliverable shape from the methodology. Iteration on triage/cluster/canonicalize/compress prompts likely needed before scaling.
3. **Mass-run Stage 3 extraction over the remaining 84 chunks** — only after proc draft methodology is validated, to avoid re-doing Stage 3 against revised prompts. Pattern: same as the existing mass-run, parallel batches of ~5.
4. **Run Stages 4.0 and 4 over the discussion-project components** (`exp`, `m1`, `m2`, `m3`, `m4`). The `exp` deliverable is the highest-value next pilot after proc — it's where the AI-implementability filter is most aggressively tested (Bohm + Cavell sources have the most embodied/group content). `m1` (pragma-dialectical), `m2` (hermeneutic), `m4` (intuition-pump) await chunk extraction; `m3` (Skinnerian) has 3 chunks done.
5. **Author the discussion-track outputs** (Stage 6.2 → 7): CLAUDE.md exploratory default + four mode skills (`/pragma-dialectical`, `/hermeneutic`, `/skinnerian`, `/intuition-pump`).
6. **Run Stage 8 testing** — fixed baseline (lightweight prompt), fixed test queries, structured comparison.
