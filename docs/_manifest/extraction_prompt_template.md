<source_information>
You are extracting actionable behavioral directives from a single chunk of a philosophical or methodological text. The chunk has been selected for this project because it bears on specific Claude-behavior deliverables, identified by the component tags below.

  Source slug:     {{slug}}
  Chunk id:        {{chunk_id}}
  Chunk title:     {{chunk_title}}
  Pages:           {{chunk_pages}}
  Component tags:  {{components}}

The chunk's full text — with its header block and per-page `=== p. N ===` markers — is provided in `<chunk_text>` below.
</source_information>

<chunk_text>
{{chunk_text}}
</chunk_text>

<task>
Read the chunk above carefully. Then extract every behavioral directive — every rule, principle, heuristic, procedure, or disposition — that the text explicitly states or directly entails.

A directive is guidance that could shape how a careful interpreter, philosopher, argument-analyst, or research-assistant acts. Examples drawn from elsewhere in this corpus to calibrate (not to import):

- "When attributing a position to a historical figure, reconstruct the question the figure was answering before paraphrasing the answer." (Skinnerian)
- "If a thought experiment depends on a scenario you cannot imagine in concrete detail, distrust the intuition it elicits." (Gendler)
- "Before challenging a premise, state it back in your interlocutor's own words." (pragma-dialectical)

NON-directives — do not extract these:

- Generic writing or research advice the chunk does not actually argue for ("be clear", "cite sources", "consider multiple perspectives"). The chunk must specifically defend the directive.
- Descriptive claims about what philosophers in fact do.
- Historical or biographical narrative.
- The author's theoretical claims, unless framed as guidance for the reader.

You may return zero directives. A chunk of pure narrative, exposition, or descriptive analysis genuinely contains no directives; the correct extraction in that case is the empty list. **You are explicitly authorized to return zero**; do not invent directives to satisfy an apparent expectation.
</task>

<output_format>
Write your extraction to the path `{{output_path}}` as a YAML file with this structure:

```yaml
chunk_id: {{chunk_id}}
source: {{slug}}
title: {{chunk_title}}
pages: "{{chunk_pages}}"
components: {{components}}
extracted_at: "<ISO-8601 timestamp>"
model: "<your model id>"
directives:
  - id: "{{chunk_id}}/d01"
    source: "<short citation: author year, chapter or section, page>"
    directive: "<imperative, one sentence where possible, phrased as the source phrases it>"
    trigger: "<condition under which the directive applies>"
    qualification: "<any limit the source itself places on the directive; '' if none>"
    evidence: "<verbatim excerpt or tight paraphrase from the chunk, with page reference>"
  - id: "{{chunk_id}}/d02"
    ...
```

If zero directives, write `directives: []`.

After writing the file, return a one-line summary: `extracted: N directives` (and a one-sentence note if you encountered anything notable — e.g. ambiguous attribution, suspected OCR error, chunk content was pure narrative).
</output_format>

<rules>
1. **Imperative phrasing.** "Reconstruct the question before paraphrasing the answer" — correct. "The reader should reconstruct..." — incorrect.
2. **Source phrasing preserved.** Do not convert "do not X" to "do Y" at this stage — that comes later. Keep the source's polarity.
3. **Trigger always stated explicitly**, even for always-on directives. The act of stating the trigger forces acknowledgment of conditionality.
4. **Qualifications come from the chunk**, not from other sources or general knowledge.
5. **No synthesis or merging across directives.** List each separately, even when similar.
6. **Evidence must anchor to the chunk.** A direct quote (with page) or tight paraphrase (with page). If you cannot anchor a directive to a specific passage in this chunk, do not extract it.

CRITICAL: faithfulness to the source is the entire task. Better to extract zero directives than to extract one the chunk does not state. **Generic-sounding directives that could appear in any methodology guide are a strong signal of fabrication** — the chunk was almost certainly saying something more specific. If your draft directive could have been written without reading this chunk, delete it.
</rules>
