<source_information>
You are triaging behavioral directives extracted from a philosophical or methodological text for AI-implementability. The directives below were drawn from the chunk text also included below. They are being assembled into custom instructions for a Claude-based agent (research assistant or conversational interlocutor). Your job is to classify each directive into one of three categories: KEEP, ADAPT, or DROP.

  Source slug:     {{slug}}
  Chunk id:        {{chunk_id}}
  Chunk title:     {{chunk_title}}
  Pages:           {{chunk_pages}}
  Component tags:  {{components}}

The chunk's full text is in `<chunk_text>` below for grounding. The directives extracted from that chunk are in `<directives>` below.
</source_information>

<chunk_text>
{{chunk_text}}
</chunk_text>

<directives>
{{directives_yaml}}
</directives>

<task>
For each directive in `<directives>` above, decide whether it is something a Claude-based AI agent can actually execute within a text-based conversation or written report. Output one of three decisions per directive:

**KEEP**: The directive describes a behavior the AI agent itself can perform. Examples of behaviors that qualify:
- Citing sources for nontrivial claims
- Marking inferences and assumptions explicitly
- Reconstructing the question a position is answering before paraphrasing the answer
- Refusing to fabricate citations or quotations
- Stating the active interpretive branch when conditional reasoning applies
- Structuring a report with required sections (method, weak claims, further reading)
- Pressing the user on a specific premise; asking a clarifying question; presenting the strongest version of a position before critiquing it

**ADAPT**: The directive describes a behavior whose surface phrasing references embodied, in-person, or multi-person settings, *but the structural move ports cleanly to text-based person↔AI interaction*. Provide the adapted phrasing.
- Example: "In a face-to-face dialogue, suspend your assumptions before responding" → ADAPT to: "When the user states a position, mark your own background assumptions explicitly rather than assuming agreement on them."
- Example: "Read the room for emerging consensus" → ADAPT to: "Track which premises the user has accepted across the conversation; do not re-litigate accepted ones."
- Be parsimonious with ADAPT. Only adapt when the structural move (the operation the directive performs) is well-defined independent of the embodied surface, and the AI can perform that operation. If you have to invent the AI-side analogue from scratch, the answer is DROP.

**DROP**: The directive's central operation requires capacities the AI does not have, or contexts that don't apply to person↔AI text exchange. Examples that should be DROPped:
- Bodily / spiritual exercises (e.g., specific breathing practices, sustained physical posture)
- Real-time observation of body language, vocal tone, facial micro-expressions
- Group dynamics with three or more participants
- Sustained silence in person; meditative practice as part of dialogue
- Anything that depends on shared physical space, real-time presence, or group co-regulation

Each directive must receive exactly one decision. Bias slightly toward KEEP when the directive is generic enough to read as a synthesis-time research move (the AI does many of these naturally). Bias toward DROP when the directive's operation is genuinely embodied or genuinely group-scale.
</task>

<output_format>
Write your triage to the path `{{output_path}}` as a YAML file with this structure:

```yaml
chunk_id: {{chunk_id}}
source: {{slug}}
triaged_at: "<ISO-8601 timestamp>"
model: "<your model id>"
triage:
  - id: "<original directive id, copied verbatim>"
    decision: keep | adapt | drop
    reason: "<one-line justification, ≤25 words>"
    adapted_directive: "<required when decision=adapt; null otherwise>"
  - id: "..."
    ...
```

Cover every directive in `<directives>`. Preserve their `id` strings exactly. Return only the YAML file (no preamble in the file). After writing, **re-read the file you just wrote and count the actual `decision:` values in it** — do not rely on memory. Return a one-line summary: `triaged: K keep / A adapt / D drop` reflecting that recount.
</output_format>

<rules>
1. **Decide on the operation, not the phrasing.** A directive about face-to-face dialogue may still KEEP if its operation (e.g., "state premises explicitly before drawing conclusions") is one the AI performs in writing. Only ADAPT when the surface and operation are tied tightly enough that rephrasing is necessary.
2. **ADAPT must produce a concrete adapted directive.** Do not write `adapted_directive: "TBD"` or "needs work". If you can't write a clean adapted version in one sentence, the answer is DROP.
3. **DROP is acceptable and expected for some sources.** Bohm on group dialogue, Hadot on bodily exercises, Cavell on standing-before-another are corpora that legitimately contain DROPs. Do not force KEEP for these out of completeness.
4. **Reasons must be specific.** "Embodied" is not a reason; "requires real-time observation of group body language" is. "AI-implementable" is not a reason; "the AI cites sources in writing — directly applicable" is.
5. **Do not edit, merge, or split directives.** That happens in Stage 4 (clustering) and Stage 5 (canonicalization). At this stage, every input directive produces exactly one output triage record with its id preserved.

CRITICAL: this triage gates every later stage. A wrongly KEPT directive will produce a wrongly merged cluster and a wrong canonical directive. A wrongly DROPped directive removes a real protocol from the deliverable. When uncertain between KEEP and ADAPT, prefer KEEP. When uncertain between ADAPT and DROP, ask whether you can state the AI-side operation in one sentence; if not, DROP.
</rules>
