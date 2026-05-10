#!/usr/bin/env python3
"""Emit a self-contained Subtask 1 (selection) prompt for a single source.

Usage:
    subtask1_brief.py <slug>                # to stdout
    subtask1_brief.py <slug> --out path     # to file

The emitted prompt inlines the relevant sections of chunking-workflow.md, the
manifest stanzas for <slug> from each manifest where it appears, and the full
toc.md. Pasted into an Agent dispatch, it lets the selection subagent run with
zero additional file reads.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path(__file__).resolve().parent
WORKFLOW = MANIFEST / "chunking-workflow.md"
SOURCES = ROOT / "docs" / "sources"

MANIFEST_FILES = [
    ("exp", "exp-exploratory.md"),
    ("m1", "m1-pragma-dialectical.md"),
    ("m2", "m2-hermeneutic.md"),
    ("m3", "m3-skinnerian.md"),
    ("m4", "m4-dennettian.md"),
    ("proc", "proc.md"),
]


def get_workflow_section(name: str) -> str:
    """Return the content of a `## ` or `### ` heading whose title matches `name`,
    up to the next heading at the same-or-higher level (or EOF). Heading lines
    inside fenced code blocks are ignored — necessary because the workflow's
    format spec contains an example `chunking-plan.md` with `#`-style headings
    in it.
    """
    lines = WORKFLOW.read_text().splitlines(keepends=True)
    start_pat = re.compile(rf"^(##+)\s+{re.escape(name)}")

    in_fence = False
    start_idx = None
    level = None
    for i, line in enumerate(lines):
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = start_pat.match(line)
        if m:
            start_idx = i
            level = len(m.group(1))
            break
    if start_idx is None:
        return ""

    end_pat = re.compile(rf"^#{{1,{level}}}\s+")
    in_fence = False
    end_idx = len(lines)
    for j in range(start_idx + 1, len(lines)):
        if lines[j].startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if end_pat.match(lines[j]):
            end_idx = j
            break
    return "".join(lines[start_idx:end_idx]).rstrip()


def manifest_stanza(manifest_path: Path, slug: str) -> str:
    """Return the slug's stanza from a manifest: the `- \\`slug\\`` line plus
    its indented sub-bullets, until the next unindented non-blank line.
    """
    if not manifest_path.exists():
        return ""
    lines = manifest_path.read_text().splitlines()
    out: list[str] = []
    capturing = False
    marker = f"- `{slug}`"
    for line in lines:
        if line.startswith(marker):
            out.append(line)
            capturing = True
            continue
        if capturing:
            if not line.strip():
                break  # blank line — end of stanza
            if not line[0].isspace():
                break  # unindented — next slug or new heading
            out.append(line)
    return "\n".join(out).rstrip()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("slug")
    p.add_argument("--out", default="-")
    args = p.parse_args()
    slug = args.slug

    src_dir = SOURCES / slug
    toc = src_dir / "toc.md"
    if not toc.exists():
        print(f"ERROR: toc.md not found at {toc}", file=sys.stderr)
        sys.exit(1)

    manifest_blocks: list[str] = []
    for code, fname in MANIFEST_FILES:
        stanza = manifest_stanza(MANIFEST / fname, slug)
        if stanza:
            manifest_blocks.append(
                f"### From `{fname}` (component `{code}`):\n\n{stanza}"
            )

    if not manifest_blocks:
        print(
            f"WARN: slug '{slug}' not found in any manifest", file=sys.stderr
        )

    parts = [
        f"# Subtask 1 (Selection) — {slug}",
        "",
        "You are running Subtask 1 of the per-source chunking workflow for one source.",
        "Read this brief in full; do NOT consult external files unless told to.",
        "",
        "## Subtask 1 spec (from chunking-workflow.md)",
        "",
        get_workflow_section("Subtask 1 — Selection") or "(spec not found — check chunking-workflow.md)",
        "",
        "## Volume budget",
        "",
        get_workflow_section("Volume budget per source"),
        "",
        "## Project components (deliverables)",
        "",
        get_workflow_section("Project deliverables (the component codes)"),
        "",
        "## Format spec for the draft block",
        "",
        get_workflow_section("Format spec for `chunking-plan.md`"),
        "",
        "## Manifest entries that mention this source",
        "",
        ("\n\n".join(manifest_blocks) if manifest_blocks
         else "(none — slug absent from all six manifests)"),
        "",
        "## Source toc.md",
        "",
        f"Path: `docs/sources/{slug}/toc.md` (full content inlined below)",
        "",
        "```markdown",
        toc.read_text().rstrip(),
        "```",
        "",
        "## Output",
        "",
        f"Emit the draft source-block in your final response, beginning with `### {slug}`.",
        "Leave `verified: false` on every chunk and `pdf_total_pages: TBD_BY_SUBTASK_2`.",
        "After the block, briefly note (≤ 200 words):",
        "- which manifest target chapters you covered,",
        "- any divergence from the toc.md operational map and why,",
        "- any ambiguity Subtask 2 should pay attention to (page-scheme, missing pagination, etc.).",
        "",
        "Do NOT write any files. Read-only. Output only.",
    ]

    output = "\n".join(parts)
    if args.out == "-":
        sys.stdout.write(output)
    else:
        Path(args.out).write_text(output)
        print(f"wrote {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
