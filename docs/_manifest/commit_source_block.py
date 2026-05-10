#!/usr/bin/env python3
"""Insert or replace a source-block in chunking-plan.md, run verifier, tick workflow.

Usage:
    commit_source_block.py <slug> --block-file <path>
    commit_source_block.py <slug> --stdin < block.txt
    commit_source_block.py <slug> --block-file <path> --dry-run

The block must start with `### <slug>` (matching the slug arg) and contain the
YAML body. See chunking-workflow.md for the format spec.

Exit codes:
    0  committed; verifier passed; checkbox ticked
    1  input validation failed (slug mismatch, missing block, etc.)
    2  verifier failed after commit (block was still written; check manually)
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

MANIFEST = Path(__file__).resolve().parent
PLAN = MANIFEST / "chunking-plan.md"
WORKFLOW = MANIFEST / "chunking-workflow.md"
VERIFIER = MANIFEST / "verify_chunking_plan.py"
SOURCES_HEADING = "## Sources"


def read_block(args) -> str:
    if args.stdin:
        return sys.stdin.read()
    return Path(args.block_file).read_text()


def validate_block(slug: str, block: str):
    block = block.strip()
    if not block.startswith("### "):
        return None, "block does not start with '### ' heading"
    head, _, _ = block.partition("\n")
    actual = head[4:].strip()
    if actual != slug:
        return None, f"block slug '{actual}' does not match argument '{slug}'"
    return block, None


def split_plan(text: str):
    """Return (header, sources_text). sources_text is everything after the
    `## Sources` heading line — that's where source-blocks live.
    """
    idx = text.find(SOURCES_HEADING)
    if idx == -1:
        raise SystemExit(f"chunking-plan.md missing '{SOURCES_HEADING}' heading")
    line_end = text.find("\n", idx) + 1
    return text[:line_end], text[line_end:]


def parse_blocks(sources_text: str):
    """Split sources_text into preamble + ordered list of (slug, raw_block)."""
    parts = re.split(r"(?m)^### ", sources_text)
    preamble = parts[0]
    blocks = []
    for part in parts[1:]:
        head, _, _ = part.partition("\n")
        slug = head.strip()
        blocks.append((slug, "### " + part.rstrip() + "\n"))
    return preamble, blocks


def insert_or_replace(blocks, new_slug: str, new_block: str):
    new_block = new_block.strip() + "\n"
    out = []
    inserted = False
    for slug, raw in blocks:
        if slug == new_slug:
            out.append((slug, new_block))
            inserted = True
        elif not inserted and new_slug < slug:
            out.append((new_slug, new_block))
            out.append((slug, raw))
            inserted = True
        else:
            out.append((slug, raw))
    if not inserted:
        out.append((new_slug, new_block))
    return out


def render(header: str, preamble: str, blocks) -> str:
    body = "\n".join(raw for _, raw in blocks)
    return header + preamble + body


def tick_checkbox(slug: str) -> bool:
    text = WORKFLOW.read_text()
    pending = f"- [ ] {slug}"
    done = f"- [x] {slug}"
    if pending in text:
        WORKFLOW.write_text(text.replace(pending, done))
        return True
    return done in text  # already ticked → idempotent success


def run_verifier():
    res = subprocess.run(
        [sys.executable, str(VERIFIER)], capture_output=True, text=True
    )
    return res.returncode, res.stdout + res.stderr


def main():
    p = argparse.ArgumentParser()
    p.add_argument("slug")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--block-file")
    g.add_argument("--stdin", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    block_raw = read_block(args)
    block, err = validate_block(args.slug, block_raw)
    if err:
        print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    text = PLAN.read_text()
    header, sources_text = split_plan(text)
    preamble, blocks = parse_blocks(sources_text)
    new_blocks = insert_or_replace(blocks, args.slug, block)
    output = render(header, preamble, new_blocks)

    if args.dry_run:
        sys.stdout.write(output)
        sys.exit(0)

    PLAN.write_text(output)
    print(f"committed: {args.slug}")

    rc, out = run_verifier()
    sys.stdout.write(out)
    if rc != 0:
        print(
            f"VERIFIER FAILED (exit {rc}); block was committed; check manually",
            file=sys.stderr,
        )
        sys.exit(2)

    if tick_checkbox(args.slug):
        print(f"checkbox ticked: {args.slug}")
    else:
        print(
            f"WARN: no checklist entry for {args.slug} in chunking-workflow.md",
            file=sys.stderr,
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
