# Research Request: Source corpus for four philosophical-critique skills

## Project context

I am building a Claude Code project for philosophical discussion. Its structure:
- A CLAUDE.md file establishing a default "rigorous exploration" interlocutor
  that engages charitably with ill-formed ideas.
- Four invokable critic-mode skill files — /pragma-dialectical, /hermeneutic,
  /skinnerian, /intuition-pump — each implementing a specific philosophical
  method for stress-testing arguments under construction.

The skills are mode-shaped (sustained dialogical critique that persists across
turns), not task-shaped (one-shot analysis dumps). To author each skill file
well, I need three categories of source for each mode:

(a) Canonical formulation — the primary source where the method is set out.
(b) Implementation/practice sources (1–3) — texts showing the method applied
    to real arguments or texts, so the skill can produce concrete dialogical
    moves rather than abstract descriptions.
(c) Critique/limits sources (1–3) — the most influential objections to the
    method, so the skill knows where it breaks down and can flag those cases.

## Mode by mode

### Mode 1: Pragma-dialectical critique
- Canonical: van Eemeren & Grootendorst's pragma-dialectical theory (ten
  rules, four stages, fallacy theory) plus Walton, Reed & Macagno on
  argumentation schemes and critical questions.
- Implementation: textbook treatments and case-study applications to real
  arguments.
- Critique: objections that pragma-dialectics is too procedural, that the
  rules are normatively contested, that schemes are not exhaustive.

### Mode 2: Hermeneutic close-reading
- Canonical: Gadamer's *Truth and Method* (Part II) and Ricoeur's
  *Hermeneutics and the Human Sciences* ("What is a Text?", "The Model of the
  Text").
- Implementation: pedagogical treatments showing hermeneutic close reading
  performed on a concrete text.
- Critique: analytic-philosophy critiques, post-structuralist critique of
  hermeneutic closure, contemporary hermeneutics' own self-critique.

### Mode 3: Skinnerian historiographical reconstruction
- Canonical: Skinner, *Visions of Politics* Vol. 1; the methodological essays.
- Implementation: examples of Skinnerian reconstruction applied to historical
  texts (Skinner's own work or successors).
- Critique: critiques of Cambridge-school contextualism (Bevir, LaCapra,
  Pocock variants); charges of methodological narrowness.

### Mode 4: Dennettian intuition-pump stress-testing
- Canonical: Dennett, *Intuition Pumps and Other Tools for Thinking*.
- Implementation: applications of intuition-pump analysis to specific thought
  experiments (Dennett's own work; commentary on his applications).
- Critique: defenses of intuitions against Dennettian deflation; the broader
  debate on intuitions as evidence (Cappelen, *Philosophy without
  Intuitions*; Williamson on thought experiments).

## Existing baseline

procedure.md already lists the canonical primary sources above (van Eemeren
*Systematic Theory of Argumentation*, Walton *Argumentation Schemes*, Gadamer
*Truth and Method*, Ricoeur *Hermeneutics and the Human Sciences*, Skinner
*Visions of Politics*, Dennett *Intuition Pumps*). Validate these and
identify the implementation and critique sources currently missing.

## Output format

For each of the four modes, a section containing:
- Canonical source (confirmed or replaced) with full reference and rationale.
- Implementation/practice sources (1–3, ranked).
- Critique/limits sources (1–3, ranked).
- Brief notes on what each source contributes that the others don't.

A summary section with mode-by-mode acquisition priority — which sources to
acquire first to author each skill file.

Constraints:
- Peer-reviewed or canonical, legitimately obtainable, English unless
  uniquely authoritative.
- Specifically include sources that show *the method in action* — abstract
  methodology alone is insufficient for authoring a dialogical skill.
