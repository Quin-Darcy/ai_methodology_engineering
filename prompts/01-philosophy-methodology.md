# Research Request: Foundational sources for a philosophy research-and-synthesis methodology

## Project context

I am building a Claude project that produces literature-review-style research
reports on philosophical questions. The project lives on claude.ai and consists of:
- Slim-core project custom instructions (anti-sycophancy, citation discipline,
  refusal to overclaim, instruction to load the procedure document at the
  start of any research task).
- A long-form procedure document in project knowledge that the agent loads
  when starting a research task.
- A source corpus accumulated in project knowledge as research proceeds.

The workflow has two phases per research task:
- Phase 1 — discovery + initial report: web search identifies relevant source
  texts; agent produces a provisional report explicitly flagged as such.
- Phase 2 — source-text revision: I acquire the texts identified in Phase 1
  and add them to project knowledge; agent re-reads them and revises the
  report against direct in-context source quotation.

The procedure document needs to ground the agent's behavior in authoritative
methodological literature. I have an existing source baseline (below) from a
prior research pass; this request validates, refines, or extends it.

## What to research

Identify the most authoritative texts on:

1. Philosophical question formulation and refinement — how philosophers turn
   vague topics into researchable questions; what good question structure
   looks like across analytic, continental, and historiographical traditions.
2. The source ecology of philosophy — the role of Stanford Encyclopedia of
   Philosophy, Internet Encyclopedia of Philosophy, Routledge Encyclopedia;
   journal hierarchy; relative weight of monographs, journal articles, and
   anthologies; how philosophy's bibliographic norms differ from STEM and
   social-science norms.
3. Tradition-appropriate research methods — what counts as good research
   differently in analytic vs. continental vs. historiographical traditions;
   what each treats as evidence, exposition, and synthesis.
4. Charitable reading and the principle of charity — the methodological norm
   of engaging the strongest version of an opponent's view; canonical and
   recent treatments.
5. The structural difference between a philosophical literature review and a
   systematic review in the empirical sciences — how synthesis works when the
   field is dialectical rather than empirical; how scoping-review methodology
   (Arksey & O'Malley, Levac, PRISMA-ScR, Booth-Sutton-Papaioannou) does and
   does not transfer to philosophy.

## Existing baseline (treat as candidate canonical sources to confirm, refine, or supplement)

- Pryor, "Guidelines on Writing a Philosophy Paper" (jimpryor.net)
- Martinich, *Philosophical Writing: An Introduction* (Wiley-Blackwell)
- Skinner, *Visions of Politics, Vol. 1: Regarding Method* (CUP 2002)
- Rorty, "The Historiography of Philosophy: Four Genres" (in *Truth and
  Progress*, CUP 1998)
- Booth, Sutton & Papaioannou, *Systematic Approaches to a Successful
  Literature Review* (Sage)
- Williamson, *Doing Philosophy* (OUP VSI 2018)
- Arksey & O'Malley (2005); Levac, Colquhoun & O'Brien (2010); Tricco et al.
  PRISMA-ScR (2018); Thomas & Harden (2008); Noblit & Hare, *Meta-Ethnography*

## Output format

A research report in the style of
`refs/empirical_foundations_of_llm_instruction_design.md` in my project, with:
- TL;DR section.
- Findings organized by research area (1–5 above).
- Each source cited with full reference, evidence level (canonical /
  influential / supplementary), and brief rationale for inclusion.
- Tiered acquisition list: Tier 1 (acquire first), Tier 2 (acquire if Tier 1
  has gaps), Tier 3 (skip unless specific gap).
- Caveats section noting where the literature is thin or contested.

Constraints:
- Primarily peer-reviewed or canonical scholarly works.
- Prefer legitimately obtainable sources (open access, university press,
  mainstream academic publishers).
- English-language unless a non-English source is uniquely authoritative.
- The LLM instruction-design literature is already covered separately
  (see `refs/empirical_foundations_of_llm_instruction_design.md`) — focus on
  philosophical methodology, not on prompt engineering.
