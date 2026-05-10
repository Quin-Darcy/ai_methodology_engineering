#!/usr/bin/env python3
"""Pre-flight scan of every source's full.pdf for OCR / pagination quirks.

For each source under docs/sources/, reports:
- Total PDF pages (pdfinfo)
- Whether pdftotext returns nontrivial content on a mid-document page
- Whether the toc.md mentions a reflowable ebook or warns about pagination
- Suggested page_scheme default (book / pdf)

Use this before iteration to identify sources that will need OCR (image-only
PDFs) or special handling (reflowable ebooks, missing pagination).

Usage:
    scan_pdf_quality.py                    # scan all sources
    scan_pdf_quality.py <slug> [<slug>...] # scan specific sources
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "docs" / "sources"

REFLOWABLE_HINTS = (
    "reflowable", "ebook", "epub", "page numbers are not stable",
    "page numbers not stable", "no stable pagination",
)


def get_pdf_pages(pdf: Path) -> int | None:
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


def text_extractable(pdf: Path, total_pages: int) -> tuple[bool, int]:
    """Return (is_extractable, byte_count_on_mid_page)."""
    if total_pages < 5:
        sample = max(1, total_pages // 2)
    else:
        sample = total_pages // 2  # mid-document
    try:
        out = subprocess.run(
            ["pdftotext", "-f", str(sample), "-l", str(sample), str(pdf), "-"],
            capture_output=True, text=True, check=True,
        )
        text = out.stdout.strip()
        return len(text) > 50, len(text)
    except subprocess.CalledProcessError:
        return False, 0


def toc_pagination_hint(toc: Path) -> str | None:
    """Return a snippet from toc.md if it warns about reflowable / unstable pagination."""
    if not toc.exists():
        return None
    text = toc.read_text().lower()
    for hint in REFLOWABLE_HINTS:
        if hint in text:
            # Find the surrounding sentence/line
            idx = text.find(hint)
            start = max(0, text.rfind("\n", 0, idx) + 1)
            end = text.find("\n", idx)
            if end == -1:
                end = len(text)
            return toc.read_text()[start:end].strip()
    return None


def scan_one(slug: str) -> dict:
    src_dir = SOURCES / slug
    pdf = src_dir / "full.pdf"
    toc = src_dir / "toc.md"

    record = {
        "slug": slug,
        "pdf_exists": pdf.exists(),
        "toc_exists": toc.exists(),
    }

    if not pdf.exists():
        record["status"] = "missing_pdf"
        return record

    record["pdf_total_pages"] = get_pdf_pages(pdf)
    if record["pdf_total_pages"] is None:
        record["status"] = "pdfinfo_failed"
        return record

    extractable, byte_count = text_extractable(pdf, record["pdf_total_pages"])
    record["text_extractable"] = extractable
    record["mid_page_bytes"] = byte_count

    record["reflowable_hint"] = toc_pagination_hint(toc)

    # Suggested page_scheme
    if record["reflowable_hint"]:
        record["suggested_scheme"] = "pdf"
        record["status"] = "reflowable"
    elif not extractable:
        record["suggested_scheme"] = "book"
        record["status"] = "image_only"
    else:
        record["suggested_scheme"] = "book"
        record["status"] = "ok"

    return record


def main():
    if len(sys.argv) > 1:
        slugs = sys.argv[1:]
    else:
        slugs = sorted(p.name for p in SOURCES.iterdir() if p.is_dir())

    records = []
    for slug in slugs:
        records.append(scan_one(slug))

    # Print table
    print(f"{'slug':<55} {'pages':>6} {'status':<14} {'mid':>6} {'scheme':<6}")
    print("-" * 95)
    for r in records:
        slug = r["slug"]
        pages = r.get("pdf_total_pages") or "-"
        status = r.get("status", "?")
        mid = r.get("mid_page_bytes") or "-"
        scheme = r.get("suggested_scheme") or "-"
        print(f"{slug:<55} {str(pages):>6} {status:<14} {str(mid):>6} {scheme:<6}")

    # Summary
    counts = {}
    for r in records:
        counts[r.get("status", "?")] = counts.get(r.get("status", "?"), 0) + 1
    print()
    print("Summary:")
    for status, count in sorted(counts.items()):
        print(f"  {status}: {count}")

    # Surface issues
    issues = [r for r in records if r.get("status") in ("image_only", "reflowable", "missing_pdf", "pdfinfo_failed")]
    if issues:
        print()
        print("Sources needing special handling:")
        for r in issues:
            extra = ""
            if r.get("reflowable_hint"):
                extra = f" ({r['reflowable_hint'][:80]})"
            print(f"  - {r['slug']}: {r['status']}{extra}")


if __name__ == "__main__":
    main()
