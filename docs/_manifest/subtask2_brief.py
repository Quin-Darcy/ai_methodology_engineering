#!/usr/bin/env python3
"""Emit a self-contained Subtask 2 (page-number verification) prompt.

Usage:
    subtask2_brief.py <slug> --block-file <path>
    subtask2_brief.py <slug> --stdin < draft_block.txt
    subtask2_brief.py <slug> --block-file <path> --out path

The brief inlines the draft block (from Subtask 1), the standard verification
procedure, output constraints, and any pre-flight notes about the source's
PDF (image-only / reflowable / etc.). Pasted into an Agent dispatch.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path(__file__).resolve().parent
SOURCES = ROOT / "docs" / "sources"


def get_pdf_total_pages(pdf: Path) -> int | None:
    try:
        out = subprocess.run(
            ["pdfinfo", str(pdf)], capture_output=True, text=True, check=True
        )
        for line in out.stdout.splitlines():
            if line.startswith("Pages:"):
                return int(line.split()[1])
    except (subprocess.CalledProcessError, ValueError):
        pass
    return None


def is_text_extractable(pdf: Path, total_pages: int) -> bool:
    sample = max(1, total_pages // 2)
    try:
        out = subprocess.run(
            ["pdftotext", "-f", str(sample), "-l", str(sample), str(pdf), "-"],
            capture_output=True, text=True, check=True,
        )
        return len(out.stdout.strip()) > 50
    except subprocess.CalledProcessError:
        return False


def detect_reflowable(toc_text: str) -> bool:
    lower = toc_text.lower()
    hints = (
        "reflowable", "page numbers are not stable",
        "page numbers not stable", "no stable pagination",
    )
    return any(h in lower for h in hints)


def detect_first_chapter_anchor(toc_text: str) -> str | None:
    """Heuristic: find a chapter-1 hint in the toc to use as an offset anchor.
    Returns a search string the Subtask 2 agent should grep for in the PDF.
    """
    # Common patterns: "| 1 | <Title> | <page> |" or "Chapter 1 — <title>"
    m = re.search(r"\|\s*1\s*\|\s*([^|]+?)\s*\|\s*\d+\s*\|", toc_text)
    if m:
        return m.group(1).strip()
    m = re.search(r"(?im)^\s*(?:chapter|ch\.?)\s+1\s*[:.\-—]\s*(.+)$", toc_text)
    if m:
        return m.group(1).strip()
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("slug")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--block-file")
    g.add_argument("--stdin", action="store_true")
    p.add_argument("--out", default="-")
    args = p.parse_args()

    slug = args.slug
    src_dir = SOURCES / slug
    pdf = src_dir / "full.pdf"
    toc = src_dir / "toc.md"

    for path, name in [(pdf, "full.pdf"), (toc, "toc.md")]:
        if not path.exists():
            print(f"ERROR: {name} missing for slug '{slug}' at {path}", file=sys.stderr)
            sys.exit(1)

    # Read the draft block
    if args.stdin:
        draft = sys.stdin.read()
    else:
        draft = Path(args.block_file).read_text()
    draft = draft.strip()

    # Pre-flight checks
    pdf_total = get_pdf_total_pages(pdf)
    text_ok = is_text_extractable(pdf, pdf_total) if pdf_total else False
    toc_text = toc.read_text()
    reflowable = detect_reflowable(toc_text)
    ch1_anchor = detect_first_chapter_anchor(toc_text)

    pre_notes = []
    if pdf_total is not None:
        pre_notes.append(f"- `pdfinfo` reports **{pdf_total}** total pages.")
    if not text_ok and pdf_total:
        pre_notes.append(
            "- **Image-only PDF detected** (`pdftotext` returned no extractable text on a mid-document page). "
            "You will need to verify visually by reading rendered pages with the Read tool, NOT by `pdftotext` + grep."
        )
    if reflowable:
        pre_notes.append(
            "- **Reflowable / unstable-pagination PDF detected** in toc.md. Book pages are not stable. "
            "If the draft uses `page_scheme: book`, expect the agent to switch to `page_scheme: pdf` and "
            "locate sections via string search on chapter/part headers."
        )
    if ch1_anchor:
        pre_notes.append(
            f"- **Suggested book→PDF offset anchor**: search the PDF for the Ch. 1 title "
            f'"`{ch1_anchor}`". The PDF page where it appears equals book p. 1 + offset.'
        )

    # Build prompt
    parts = [
        f"# Subtask 2 (Page-Number Verification) — {slug}",
        "",
        "Verify the page ranges in the Subtask 1 draft block against the actual PDF.",
        "",
        "## Pre-flight (computed for you)",
        "",
        ("\n".join(pre_notes) if pre_notes
         else "(no pre-flight observations — proceed with standard procedure)"),
        "",
        "## Inputs",
        "",
        f"- Slug: `{slug}`",
        f"- PDF: `docs/sources/{slug}/full.pdf`",
        f"- TOC: `docs/sources/{slug}/toc.md`",
        "",
        "Tools: `pdfinfo`, `pdftotext`. The Read tool can render PDF pages visually for image-only sources.",
        "",
        "## Draft block (from Subtask 1)",
        "",
        "```",
        draft,
        "```",
        "",
        "## What you must produce",
        "",
        "A finalized source-block as your final response. For each chunk:",
        "",
        "- Keep all fields from the draft (`id`, `title`, `page_scheme`, `page_start`, `page_end`,"
        " `components`, `rationale`).",
        "- **Add** `pdf_page_start` and `pdf_page_end` (integers) — the actual PDF page numbers"
        " corresponding to each chunk. The downstream extractor uses these to drive `pdftk` etc.",
        "- Set `verified: true` if confidently located, else `verified: false`.",
        "",
        f"At source level, fill `pdf_total_pages: {pdf_total or 'TBD'}`.",
        "",
        "If any chunk has `verified: false`, add a single-line `warnings:` field at the source level "
        "(NOT a multi-line list — the parser only handles single-line strings). Join multiple warnings with `; `.",
        "",
        "## Standard procedure",
        "",
        "1. Confirm `pdfinfo` total agrees with the value above.",
        "2. **Find book→PDF offset:**",
        "   - Use `pdftotext -f N -l N full.pdf -` to locate the Ch. 1 / first-chapter heading.",
        "   - `offset = pdf_page_for_book_1 - 1`",
        "   - Compute `pdf_page_start` / `pdf_page_end` for each chunk by adding the offset.",
        "3. **For non-page schemes** (`bekker`, `section_number`, or `pdf` for reflowable):",
        "   - Locate the boundary directly via string search on the section/part identifier.",
        "   - Set `pdf_page_start` and `pdf_page_end` to the actual PDF integers.",
        "4. **Spot-check at least one chunk per source:**",
        "   - Dump the page content at `pdf_page_start` and confirm the section heading or opening text matches.",
        "   - Confirm the page after `pdf_page_end` opens the next section / part / chapter.",
        "5. **Boundary discrepancies:** if a chunk's claimed end-page actually contains content from the next "
        "section (or the next section's start is ≠ end+1), record a warning and consider whether to set "
        "`verified: false` for the affected chunk.",
        "",
        "## Output constraints",
        "",
        "- Single-line `warnings:` string only (no multi-line YAML lists).",
        "- `rationale:` must be a plain string, not `{summary: \"...\"}` YAML object.",
        "- Keep `page_scheme` as in the draft unless you have a specific reason to switch (e.g., a chunk with "
        "Roman-numeral book pages → switch to `page_scheme: pdf`).",
        "- All page integers must be ≥ 1 and `pdf_page_start ≤ pdf_page_end`.",
        "",
        "## Report (≤ 250 words)",
        "",
        "After the finalized block, briefly state:",
        "- pdf_total_pages",
        "- book→PDF offset (or 'n/a' for reflowable / pdf-scheme sources)",
        "- per-chunk PDF page ranges",
        "- spot-check results",
        "- any boundary discrepancies and how you handled them",
        "- any warnings raised",
        "",
        "Read-only on all source files. No file writes.",
    ]

    output = "\n".join(parts)
    if args.out == "-":
        sys.stdout.write(output)
    else:
        Path(args.out).write_text(output)
        print(f"wrote {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
