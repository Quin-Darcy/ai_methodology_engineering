#!/usr/bin/env python3
"""Print pdftotext output for one or more individual PDF pages, headed.

Replaces the recurring shell pattern used during Subtask 2 verification:

    for p in 60 61 62; do
        echo "=== PDF page $p ==="
        pdftotext -f $p -l $p some.pdf - | head -10
    done

Usage:
    peek_pdf_pages.py <pdf_path> <page> [<page> ...] [--head N | --tail N | --full] [--layout]

Examples:
    peek_pdf_pages.py docs/sources/foo/full.pdf 32 52 53 63
    peek_pdf_pages.py docs/sources/foo/full.pdf 100 --tail 5
    peek_pdf_pages.py docs/sources/foo/full.pdf 17 --layout --full

Exit codes:
    0  success
    1  argument or pdfinfo error
    2  one or more pdftotext invocations failed
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def get_pdf_total_pages(pdf: Path) -> int:
    out = subprocess.run(
        ["pdfinfo", str(pdf)], capture_output=True, text=True, check=True
    )
    for line in out.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    raise RuntimeError(f"pdfinfo did not report Pages: for {pdf}")


def render_page(pdf: Path, page: int, layout: bool) -> str:
    cmd = ["pdftotext"]
    if layout:
        cmd.append("-layout")
    cmd.extend(["-f", str(page), "-l", str(page), str(pdf), "-"])
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        # pdftotext writes its own diagnostics to stderr; surface them.
        return f"[pdftotext exit {res.returncode}: {res.stderr.strip()}]"
    return res.stdout


def truncate(text: str, head: int | None, tail: int | None) -> str:
    if head is None and tail is None:
        return text
    lines = text.splitlines()
    if head is not None:
        lines = lines[:head]
    elif tail is not None:
        lines = lines[-tail:]
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Print pdftotext output for one or more PDF pages, headed.",
        epilog="See module docstring for examples.",
    )
    p.add_argument("pdf", help="Path to a PDF file.")
    p.add_argument("pages", nargs="+", type=int, help="One or more PDF page numbers (1-based).")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--head", type=int, default=10, help="Print only the first N lines per page (default 10).")
    g.add_argument("--tail", type=int, help="Print only the last N lines per page.")
    g.add_argument("--full", action="store_true", help="Print the whole page (no truncation).")
    p.add_argument("--layout", action="store_true", help="Pass -layout to pdftotext (preserves columns).")
    args = p.parse_args()

    pdf = Path(args.pdf)
    if not pdf.is_file():
        print(f"ERROR: not a file: {pdf}", file=sys.stderr)
        return 1

    try:
        total = get_pdf_total_pages(pdf)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: pdfinfo failed: {e.stderr.strip()}", file=sys.stderr)
        return 1

    head = args.head if (args.tail is None and not args.full) else None
    tail = args.tail
    any_failed = False

    for page in args.pages:
        # Bound check first so out-of-range pages are reported clearly rather
        # than letting pdftotext emit a confusing exit code.
        if page < 1 or page > total:
            print(f"=== PDF page {page} (OUT OF RANGE; total={total}) ===")
            any_failed = True
            continue
        print(f"=== PDF page {page} ===")
        text = render_page(pdf, page, args.layout)
        sys.stdout.write(truncate(text, head, tail))
        if not text.endswith("\n"):
            print()

    return 2 if any_failed else 0


if __name__ == "__main__":
    sys.exit(main())
