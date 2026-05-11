#!/usr/bin/env python3
"""Stage 4 helper: build a self-contained clustering prompt for one component.

Reads:
  - docs/_manifest/cluster_prompt_template.md (the prompt template)
  - docs/_manifest/<component>-clustering-input.yaml (Stage 4.0 consolidator output)

Substitutes the variables {{component}}, {{surviving_count}}, {{chunks_in}},
{{consolidated_yaml}}, {{output_path}} into the template and prints the
fully-substituted prompt to stdout.

Usage:
  build_cluster_prompt.py <component> > <out_prompt_file>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path(__file__).parent
TEMPLATE = MANIFEST / "cluster_prompt_template.md"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: build_cluster_prompt.py <component>", file=sys.stderr)
        return 2
    component = sys.argv[1]

    input_path = MANIFEST / f"{component}-clustering-input.yaml"
    if not input_path.exists():
        print(f"clustering input not found: {input_path}", file=sys.stderr)
        print(f"  run: consolidate_for_clustering.py {component}", file=sys.stderr)
        return 2

    output_yaml_path = MANIFEST / f"{component}-clusters.yaml"
    consolidated = input_path.read_text(encoding="utf-8")

    surviving_count = "?"
    chunks_in = "?"
    m = re.search(r"^surviving_count:\s*(\d+)", consolidated, re.MULTILINE)
    if m:
        surviving_count = m.group(1)
    m = re.search(r"^chunks_in:\s*(\d+)", consolidated, re.MULTILINE)
    if m:
        chunks_in = m.group(1)

    template = TEMPLATE.read_text(encoding="utf-8")
    substitutions = {
        "{{component}}": component,
        "{{surviving_count}}": surviving_count,
        "{{chunks_in}}": chunks_in,
        "{{consolidated_yaml}}": consolidated,
        "{{output_path}}": str(output_yaml_path),
    }
    out = template
    for k, v in substitutions.items():
        out = out.replace(k, v)
    sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
