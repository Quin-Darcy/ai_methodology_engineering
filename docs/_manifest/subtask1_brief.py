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


def parse_chapter_table(toc_text: str) -> list[tuple[str, int]]:
    """Pull out chapter rows from any markdown table that has at least one
    integer-only cell (the page number). Returns [(label, page), ...] sorted
    by page.

    Tolerates several common shapes:
      | 1 | On Communication | 1 |
      | I | Criteria and Judgment | 3 |
      | 26 | Beiser | History of Ideas: A Defense | 505 |
      | 1 | Differences of Opinion | 3 | 1.1 ... · 1.2 ... |   <- 4-col w/ sub-section text
      |  | sub-heading | 332 |
    """
    rows = []
    line_re = re.compile(r"^\s*\|\s*(.+?)\s*\|\s*$")
    for raw in toc_text.splitlines():
        m = line_re.match(raw)
        if not m:
            continue
        cells = [c.strip() for c in m.group(1).split("|")]
        if len(cells) < 2:
            continue
        # Skip header rows (any cell labeled "page" verbatim)
        if any(c.lower() == "page" for c in cells):
            continue
        # Skip alignment rows (---|---)
        if all(set(c) <= set("-: ") for c in cells):
            continue
        # Find a cell that is purely an integer — preferring the rightmost
        # in the standard 3-col case but accepting any integer cell so that
        # "| 1 | Title | 3 | sub-sections... |" still works.
        page = None
        page_idx = None
        for i in range(len(cells) - 1, -1, -1):
            try:
                page = int(cells[i])
                page_idx = i
                break
            except ValueError:
                continue
        if page is None:
            continue
        # Build label from cells other than the page cell, skipping cells
        # that are themselves bare integers (e.g. chapter numbers) or empty.
        label_parts = []
        for i, c in enumerate(cells):
            if i == page_idx or not c:
                continue
            try:
                int(c)
                continue  # bare integer column — chapter number, skip
            except ValueError:
                pass
            label_parts.append(c)
        if not label_parts:
            continue
        # Take the first non-integer cell as the title — sub-section text columns
        # appear in 4-col tables and we only want the chapter title here.
        label = label_parts[0]
        if len(label) > 80:
            label = label[:80] + "…"
        rows.append((label, page))
    # Deduplicate (same label and page)
    seen = set()
    deduped = []
    for label, page in rows:
        key = (label.lower(), page)
        if key in seen:
            continue
        seen.add(key)
        deduped.append((label, page))
    deduped.sort(key=lambda x: x[1])
    return deduped


def compute_page_bounds(rows: list[tuple[str, int]]) -> str:
    """Render a 'computed page bounds' table from chapter rows. Each chapter's
    end = next chapter's start - 1. Last chapter is shown as 'to back matter'.

    Returns markdown bullet list, or empty string if rows is empty.
    """
    if len(rows) < 2:
        return ""
    out = []
    for i, (label, start) in enumerate(rows):
        if i + 1 < len(rows):
            next_start = rows[i + 1][1]
            end = next_start - 1
            if end < start:
                # Same page — likely a sub-section row
                continue
            out.append(f"- {label}: book p. {start}–{end}")
        else:
            out.append(f"- {label}: book p. {start} → end of chapter / back matter (verify in Subtask 2)")
    return "\n".join(out)


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

    # Pre-compute chapter page bounds from the toc's contents table.
    # Skipped silently for sources with non-numeric pagination (Aristotle's
    # Bekker numbers, etc.) where the parser yields nothing usable.
    toc_text = toc.read_text()
    chapter_rows = parse_chapter_table(toc_text)
    page_bounds_section = compute_page_bounds(chapter_rows)

    # Detect reflowable / image-only / unstable-pagination hints
    notes = []
    lower = toc_text.lower()
    if any(h in lower for h in ("reflowable", "epub ebook", "page numbers are not stable", "page numbers not stable")):
        notes.append(
            "**Pagination warning** — toc.md flags this PDF as reflowable / unstable. "
            "Use `page_scheme: pdf` instead of `book`. Subtask 2 will locate sections via "
            "string search on chapter/part headers, not by book pages."
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
        "## Pre-computed page bounds (from toc.md contents table)",
        "",
        (page_bounds_section if page_bounds_section
         else "(no parseable chapter table — agent must derive bounds from toc.md directly)"),
        "",
        ("\n".join(notes) + "\n" if notes else ""),
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
