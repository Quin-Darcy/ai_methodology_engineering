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
- **`procedure.md` restructuring.** Given the platform split (research on claude.ai, discussion on Claude Code) and the slim-core + referenced-document architecture, `procedure.md` needs to (a) reflect the two-artifact extraction (slim core vs. long-form), and (b) extend coverage to discussion-project skills. Recommended structure: shared front matter (acquisition, chunking, extraction framework) + a research-project-specific track + a discussion-project-specific track. Not an immediate decision — flagged for the rewrite.
- **Trigger and exit phrasings** for the four skills — pure naming convention, settled when authoring.

## Suggested next steps

1. Refactor `procedure.md` into the shared + research-track + discussion-track structure, reflecting the two-artifact split and the platform split.
2. Run the cheap empirical test for phase 1 thickness: write a thin phase 1 procedure and try it on three or four representative historical-concept-tracing questions. Document where it fails. Use those failures to decide what philosophy-specific phase 1 procedures are worth writing.
3. Write the phase 2 procedures fully — these are higher-confidence and don't depend on the phase 1 test.
4. Author the discussion-project's CLAUDE.md (exploratory default + mode-management meta-rules).
5. Author the four mode skills, with explicit attention to mode-shaped (not task-shaped) authoring — persistence, dialogical engagement, exit conditions, self-check.
6. Run Stage 8 testing per `procedure.md` — fixed baseline (lightweight prompt), fixed test queries, structured comparison.
