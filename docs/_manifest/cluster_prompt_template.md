<source_information>
You are clustering behavioral directives extracted (Stage 3) and triaged (Stage 4.0) from a corpus of philosophical and methodological texts. They are being assembled into custom instructions for a Claude-based agent for the **{{component}}** deliverable. Your job is to group directives that express the same protocol so that downstream canonicalization (Stage 5) operates on grouped equivalents rather than the flat list.

  Component:           {{component}}
  Surviving directives: {{surviving_count}} (across {{chunks_in}} chunks)

The full consolidated directive list is in `<directives>` below. Each entry has:
- `id` — a stable identifier
- `source` — short citation (author year, location, page)
- `decision` — `keep` (used as written) or `adapt` (operative phrasing already adapted for AI-side use)
- `directive` — the operative imperative
- `trigger` — the condition under which the directive applies
- `qualification` — any limit the source itself imposes (often empty)
- `original_directive` (only when decision=adapt) — the source's literal phrasing, for reference

Treat the `directive` field as the operative phrasing in all cases.
</source_information>

<directives>
{{consolidated_yaml}}
</directives>

<task>
Read the full directive list above. Group directives that express the same protocol into clusters.

A cluster is **the same protocol** when the directives, despite different surface phrasing, describe the same operation under the same kind of trigger. Examples:

- "Cite primary sources for every nontrivial claim" + "Every substantive assertion needs a traceable citation" + "Do not assert without a source pointer" → one cluster ("inline citation discipline").
- "Reconstruct the question the figure was answering before paraphrasing the answer" + "Recover the problem-context before attributing a doctrine" → one cluster ("question-before-answer historiographical reconstruction").
- "Apply the principle of charity when interpreting the user's wording" + "Hold the speaker's beliefs constant and adjust your reading of what their words mean" → one cluster (Davidsonian charity).

A cluster is **different protocols** — preserve as separate clusters or sub-clusters — when the directives differ in one of:

1. **Trigger condition.** "Apply charity in initial interpretation of an utterance" vs. "Apply charity to standpoints under explicit critique" trigger differently and may belong in distinct clusters.
2. **Operation.** "State the active interpretive branch when conditional reasoning applies" and "Cite the source for every claim" may both be transparency moves but are different operations; keep them separate.
3. **Scope.** "Disclose your interpretive position once at the start of the report" vs. "Disclose interpretive moves inline as they occur" describe the same general value at different scopes; sub-cluster, do not merge.
4. **Genuine methodological fork.** Skinner-style historicist reconstruction vs. rational reconstruction (Rorty); hermeneutics of suspicion vs. hermeneutics of trust; Williamson vs. Cappelen on intuitions as evidence. These are contested; preserve as separate clusters that Stage 5 will encode as conditional forks. Do not pick a side.

**Singletons are valid.** A directive that matches no other entry remains a one-element cluster and proceeds to Stage 5 unchanged.

**Pay equal attention to every part of the directive list.** With 400+ directives, attention naturally weights toward the start and end. Resist this. Cross-source clusters (which are the whole point of clustering) often pair an early Booth/Sutton directive with a much later Davidson or Skinner directive. Sweep through the list multiple times if needed.
</task>

<output_format>
Write your clustering to the path `{{output_path}}` as a YAML file with this structure:

```yaml
component: {{component}}
clustered_at: "<ISO-8601 timestamp>"
model: "<your model id>"
input_count: {{surviving_count}}
cluster_count: <integer>
clusters:
  - id: c001
    label: "<short working label, ≤6 words, names the protocol>"
    note: "<one-line: 'paraphrases' if all members say the same thing in different words, or 'variants' if members differ on trigger/scope/qualification but share the operation; for forks, name the forked positions>"
    member_ids:
      - "<directive id>"
      - "<directive id>"
      ...
  - id: c002
    ...
```

Cover every directive in `<directives>`. The union of `member_ids` across all clusters must equal the full input set. Each id appears in exactly one cluster. Singletons get a one-element `member_ids` list.

After writing the file, **re-read it** and confirm: (a) every input id appears exactly once across all clusters; (b) `cluster_count` matches the actual number of clusters in the file. Return a one-line summary: `clustered: N directives → C clusters (S singletons)`.
</output_format>

<rules>
1. **Group by protocol, not by source.** A Davidson directive on charity and a Skinner directive on historiographical caution are clustered together if they prescribe the same operation, even though they sit in different chapters and traditions.
2. **Resist over-merging.** The sycophancy literature (Sharma et al. ICLR 2024) documents a tendency to collapse things that "look agreeable" together. If you are uncertain whether two directives belong in one cluster or two, prefer **two clusters with a `related_to:` cross-reference** (you may add a `related_to` field listing other cluster ids) over forcing a merge.
3. **Resist under-merging.** Ten paraphrases of "cite your sources" should be one cluster, not ten singletons. The paraphrase-detection criterion: if a Stage 5 canonicalization pass would produce identical canonical text from this group, they cluster.
4. **Preserve forks.** When two directives genuinely disagree on what to do under the same trigger, **encode them as a single cluster with a `fork:` note** describing the contested positions. Do not pick one side. Stage 5 will turn the fork into a conditional directive of the form "If [condition A], do X. If [condition B], do Y."
5. **Working labels matter for downstream readability.** "Inline citation discipline" is a useful label; "various stuff about citing" is not. Name the operation, not the surface words.
6. **Do not edit, rephrase, or omit any directive.** The input is fixed. Your output references directives by id only; do not restate their text.

CRITICAL: this clustering is the substrate Stage 5 (canonicalization) operates on. A wrongly merged cluster produces a single canonical directive that misrepresents two sources; a wrongly split cluster produces redundant canonical directives that bloat the deliverable. When uncertain between merge and split, **prefer split with cross-reference** — Stage 5 can merge two related clusters cheaply, but cannot recover what was wrongly merged here without going back to source.
</rules>
