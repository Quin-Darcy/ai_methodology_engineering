#!/usr/bin/env python3
"""Stage 3 helper: build a self-contained extraction prompt for one chunk.

Reads:
  - docs/_manifest/extraction_prompt_template.md (the prompt template)
  - docs/_manifest/chunking-plan.md (chunk metadata via verify_chunking_plan.parse_plan)
  - docs/sources/<slug>/chunks/<chunk-tail>.txt (the chunk text)

Substitutes the variables {{slug}}, {{chunk_id}}, {{chunk_title}}, {{chunk_pages}},
{{components}}, {{chunk_text}}, {{output_path}} into the template and prints the
fully-substituted prompt to stdout.

The Stage 3 execution pattern:
  python3 docs/_manifest/build_extraction_prompt.py <slug> <chunk-tail> > /tmp/<name>.prompt.md
  (then spawn a Task subagent that runs `cat <path>` and follows the protocol).

Usage:
  build_extraction_prompt.py <slug> <chunk-tail> > <out_prompt_file>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path(__file__).parent
TEMPLATE = MANIFEST / "extraction_prompt_template.md"
PLAN = MANIFEST / "chunking-plan.md"

# Make verify_chunking_plan importable
sys.path.insert(0, str(MANIFEST))

from verify_chunking_plan import parse_plan  # type: ignore  # noqa: E402


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: build_extraction_prompt.py <slug> <chunk-tail>", file=sys.stderr)
        return 2
    slug = sys.argv[1]
    tail = sys.argv[2]

    plan = parse_plan(PLAN.read_text(encoding="utf-8"))
    src = next((s for sl, s, _ in plan if sl == slug), None)
    if src is None:
        print(f"slug not in plan: {slug}", file=sys.stderr)
        return 2
    chunk = next((c for c in src.get("chunks", []) if c["id"].endswith(f"/{tail}")), None)
    if chunk is None:
        print(f"chunk tail not in slug: {tail}", file=sys.stderr)
        return 2

    chunk_text_path = ROOT / "docs" / "sources" / slug / "chunks" / f"{tail}.txt"
    output_yaml_path = ROOT / "docs" / "sources" / slug / "chunks" / f"{tail}.directives.yaml"
    if not chunk_text_path.exists():
        print(f"chunk text not found: {chunk_text_path}", file=sys.stderr)
        return 2

    chunk_text = chunk_text_path.read_text(encoding="utf-8")
    template = TEMPLATE.read_text(encoding="utf-8")

    page_scheme = chunk.get("page_scheme", "pdf")
    pages = f"{chunk.get('page_start')}-{chunk.get('page_end')} ({page_scheme})"
    components_json = json.dumps(chunk.get("components", []))

    substitutions = {
        "{{slug}}": slug,
        "{{chunk_id}}": chunk["id"],
        "{{chunk_title}}": str(chunk.get("title", "")),
        "{{chunk_pages}}": pages,
        "{{components}}": components_json,
        "{{chunk_text}}": chunk_text,
        "{{output_path}}": str(output_yaml_path),
    }
    out = template
    for k, v in substitutions.items():
        out = out.replace(k, v)
    sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
