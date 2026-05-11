<source_information>
You are canonicalizing directives clustered (Stage 4) from a corpus of philosophical and methodological texts. They are being assembled into custom instructions for a Claude-based agent for the **{{component}}** deliverable. Your job is to produce one **canonical directive** per cluster — the imperative an LLM agent will actually execute downstream.

  Component:        {{component}}
  Clusters:         {{cluster_count}}
  Source directives: {{directive_count}}

The full clustered input is in `<clusters>` below. Each cluster carries:
- `id` — stable cluster id (used in your output)
- `section` — the broader thematic section the cluster sits under (informational; do not bin into stages — that is Stage 6's job)
- `label` — the clustering agent's working label
- `note` — the clustering agent's note (mentions "fork", "variants", "paraphrases", "singleton")
- `fork_hint` — `true` if the clustering agent flagged this cluster as a methodological fork
- `related_to` — optional list of sibling cluster ids the clusterer cross-referenced
- `members` — the directives the cluster contains. Each member has source, decision (keep|adapt), directive (operative phrasing), trigger, qualification, and (for adapts) `original_directive`.

Treat the `directive` field of each member as the operative phrasing.
</source_information>

<clusters>
{{clusters_yaml}}
</clusters>

<task>
For each cluster in `<clusters>`, produce one **canonical directive**. The canonical directive is what an LLM agent following the deliverable's custom instructions will actually read and execute. It must:

1. **Be imperative.** A single sentence (or short conditional) addressed to the agent. The agent reads it and knows what to do.

2. **Use affirmative phrasing wherever the underlying protocol allows.** Convert negative phrasings to affirmative whenever an affirmative paraphrase preserves the protocol. "Do not impose anachronistic categories" → "Use categories the historical figure or their contemporaries would have recognized." Preserve negative phrasing only when (a) the protocol is genuinely a refusal ("Do not fabricate citations"), or (b) affirmative paraphrase distorts the protocol's meaning. Empirical basis: Truong et al. ACL 2023 documents systematic LLM failure to follow negated instructions.

3. **State the trigger condition in surface-verifiable terms where possible.** "When the question contains the word 'consciousness' or its cognates" is more reliably executed than "When phenomenal experience is at issue." If the protocol is genuinely defined by an abstract condition with no clean verifiable proxy, state both: the abstract condition and the best surface proxy. Empirical basis: Wen et al. 2024 (ComplexBench) and Hagiwara & Saparov 2024 (KCIF) — conditional adherence improves when triggers are surface-verifiable.

4. **Preserve qualifications.** If members carry qualifications, the canonical must collectively honor them. Combine compatible qualifications. If members carry incompatible qualifications, that signals a fork (see rule 6).

5. **Cite contributing sources compactly.** List the sources of contributing members in a `sources:` field. One short citation per distinct source (Author Year, page or location). Inline citations *inside* the directive text are not required at this stage; Stage 7 will decide whether to inline-cite or footnote.

6. **Encode genuine forks as conditionals with branch-naming.** If the cluster's `fork_hint` is true, or if member directives genuinely disagree on what to do under the same trigger (rather than just varying in surface phrasing), encode the canonical as a conditional:

   > "If [condition A], do X. If [condition B], do Y. Name the active branch and the trigger that activated it before proceeding."

   The branch-naming requirement is mandatory for every conditional canonical (Wen 2024 / Hagiwara 2024: conditional adherence is the hardest constraint category; surface-verifiable branch naming turns it into checkable behavior). Do not resolve the fork by adopting one side.

7. **Inherit or improve the cluster's working label.** If the clusterer's label captures the protocol well, reuse it. If it's misleading, write a better one. Labels are short (≤ 8 words) and name the operation.

8. **Do not invent protocol content the members do not establish.** The canonical is a summary of what the members collectively say — not what you think they should say. If multiple members disagree subtly, write the canonical at the level of agreement and note the disagreement in `qualification`.

9. **One canonical per cluster.** Forks produce one conditional canonical, not two canonicals. The `is_fork: true` flag plus the conditional phrasing in `directive` carry the fork information forward.

10. **Annotate each canonical with an expected behavioral delta.** Emit `expected_delta` (one of `high | medium | low | platitude`) and a one-line `delta_rationale`. The delta is your estimate of how much an LLM agent's behavior would shift if this directive were included versus omitted, holding everything else constant. The four levels:

    - **high** — modal default behavior is unreliable on this protocol; including the directive substantively shifts what the agent produces. Example: an explicit anti-sycophancy directive against user disagreement pressure, or a specific source-ecology heuristic the model would not invoke unprompted.
    - **medium** — default behavior is partially compliant; the directive sharpens or makes-explicit a tendency that the agent has but inconsistently applies. Example: "cite primary sources for every nontrivial claim" — Claude cites often by default but not reliably for every nontrivial claim.
    - **low** — default behavior is broadly aligned; the directive's value is primarily protective (against drift in long contexts, against sycophancy under pressure, against rare adversarial framings). Example: "give the interlocutor the benefit of the doubt in initial interpretation." Most of the time, Claude already does this; the directive defends the tail.
    - **platitude** — fails *all three* of: (a) surface-verifiable trigger condition, (b) specifiable operation, (c) falsifiable outcome. Example: "be thoughtful," "engage with care." A directive can be vague and still pass — it's only a platitude when nothing in the directive could be checked.

    Be calibrated, not generous: most directives in a methodological corpus are `medium` or `low`. Do not mark everything `high` because the source was authoritative. Do not mark everything `low` because Claude is competent at most things. The annotation drives Stage 7 (compression) decisions and feeds the audit trail; an inflated rating is more harmful than an honest one.

A small number of clusters carry sub-protocols that pull apart under finer reading. If a single cluster genuinely contains two distinct operations (different trigger, different operation) that the clusterer should have split, you may emit two canonicals from one cluster. Record both with the same `cluster_id` and note `split_from_cluster: true`. Use sparingly — only when forced.
</task>

<output_format>
Write your canonicalization to the path `{{output_path}}` as a YAML file with this structure:

```yaml
component: {{component}}
canonicalized_at: "<ISO-8601 timestamp>"
model: "<your model id>"
input_cluster_count: {{cluster_count}}
canonical_count: <integer, ≥ input_cluster_count>
canonicals:
  - id: k001
    cluster_id: c001
    section: "<the cluster's section, copied through unchanged>"
    label: "<short label, ≤ 8 words>"
    directive: "<the canonical imperative; one sentence or one conditional>"
    trigger: "<surface-verifiable trigger condition where possible; abstract+proxy if not>"
    qualification: "<any limit or caveat the sources collectively impose, or empty string>"
    is_fork: false
    expected_delta: high | medium | low | platitude
    delta_rationale: "<one short line explaining the delta judgment>"
    sources:
      - "<Author Year, location, page>"
      - ...
    member_ids:
      - "<source directive id>"
      - ...
  - id: k002
    cluster_id: c012
    section: "..."
    label: "..."
    directive: "If [condition A], do X. If [condition B], do Y. Name the active branch and the trigger that activated it before proceeding."
    trigger: "..."
    qualification: "..."
    is_fork: true
    expected_delta: medium
    delta_rationale: "..."
    fork_positions:
      - "<position A name, e.g., 'historical reconstruction (Skinner 1969)'>"
      - "<position B name, e.g., 'rational reconstruction (Rorty)'>"
    sources:
      - "..."
    member_ids:
      - "..."
  - id: k003
    cluster_id: c050
    split_from_cluster: true
    section: "..."
    label: "..."
    directive: "..."
    ...
```

Cover every cluster in `<clusters>`. The union of `cluster_id` values across your canonicals must equal the input cluster set (plus any allowed splits). Every input member id must appear in exactly one canonical's `member_ids`.

After writing the file, **re-read it** and confirm: (a) every input cluster id is covered; (b) every input member id appears exactly once across all canonicals; (c) every `is_fork: true` canonical includes "Name the active branch" wording; (d) every canonical has both `expected_delta` and `delta_rationale` populated. Return a one-line summary: `canonicalized: N clusters → C canonicals (F forks, S splits; H high, M medium, L low, P platitude)`.
</output_format>

<rules>
1. **Affirmative > negative wherever the protocol allows.** (Truong 2023.)
2. **Surface-verifiable triggers where possible; both forms when not.** (Wen 2024; Hagiwara 2024.)
3. **Preserve qualifications.** Do not silently drop limits the source imposes.
4. **Cite contributing sources compactly.** Author Year + location + page (or "whole" / "ch X").
5. **Branch-naming is mandatory for every conditional canonical.** No exceptions.
6. **Do not pick sides in forks.** Encode the fork; let downstream activation decide.
7. **Do not invent.** The canonical reflects what the members establish.
8. **Re-use cluster labels unless they mislead.** Don't rewrite for style.
9. **Singletons canonicalize like any other cluster.** They are not special.
10. **Annotate `expected_delta` and `delta_rationale` for every canonical.** Be calibrated; the annotation drives Stage 7 compression and is part of the audit trail. A `platitude` rating must satisfy the strict three-test criterion (no verifiable trigger, no specifiable operation, no falsifiable outcome) — most directives in this corpus will not qualify.
10. **Decision provenance is implicit.** Adapted directives' adapted phrasing is already in the `directive` field of each member; the `original_directive` field is for audit only — you don't need to surface it in the canonical.

CRITICAL: this canonical file is the input to Stage 6 (organize) and Stage 7 (compress + format). Any drift between the source protocols and what you write here propagates into the final deliverable. When a member directive's phrasing is already clean and imperative and represents the cluster well, **prefer light editing over rewriting from scratch.** Rewriting introduces unforced errors.
</rules>
