#!/usr/bin/env python3
"""Stage 5 helper: build a self-contained canonicalization prompt for one component.

Reads:
  - docs/_manifest/canonicalize_prompt_template.md
  - docs/_manifest/<component>-canonical-input.yaml  (output of consolidate_for_canonicalization.py)

Substitutes {{component}}, {{cluster_count}}, {{directive_count}}, {{clusters_yaml}},
{{output_path}} into the template. Prints the fully-substituted prompt to stdout.

Usage:
  build_canonical_prompt.py <component> > <out_prompt_file>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

MANIFEST = Path(__file__).parent
TEMPLATE = MANIFEST / "canonicalize_prompt_template.md"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: build_canonical_prompt.py <component>", file=sys.stderr)
        return 2
    component = sys.argv[1]

    input_path = MANIFEST / f"{component}-canonical-input.yaml"
    if not input_path.exists():
        print(f"canonical input not found: {input_path}", file=sys.stderr)
        print(f"  run: consolidate_for_canonicalization.py {component}", file=sys.stderr)
        return 2

    output_yaml_path = MANIFEST / f"{component}-canonical.yaml"
    consolidated = input_path.read_text(encoding="utf-8")

    cluster_count = "?"
    directive_count = "?"
    m = re.search(r"^cluster_count:\s*(\d+)", consolidated, re.MULTILINE)
    if m:
        cluster_count = m.group(1)
    m = re.search(r"^directive_count:\s*(\d+)", consolidated, re.MULTILINE)
    if m:
        directive_count = m.group(1)

    template = TEMPLATE.read_text(encoding="utf-8")
    substitutions = {
        "{{component}}": component,
        "{{cluster_count}}": cluster_count,
        "{{directive_count}}": directive_count,
        "{{clusters_yaml}}": consolidated,
        "{{output_path}}": str(output_yaml_path),
    }
    out = template
    for k, v in substitutions.items():
        out = out.replace(k, v)
    sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
