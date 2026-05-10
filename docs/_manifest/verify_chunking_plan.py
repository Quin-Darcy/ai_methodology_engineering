#!/usr/bin/env python3
"""Verifier for chunking-plan.md. See chunking-workflow.md for spec.

Hard-fails on: malformed structure, missing files, pdfinfo disagreement,
PDF-scheme bounds violation, missing TOC anchor.
Warns on: book-page ranges that exceed pdf_total_pages (expected — book
pagination differs from PDF), volume budget overage, missing manifest target.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN = Path(__file__).parent / "chunking-plan.md"
SOURCES = ROOT / "docs" / "sources"
MANIFESTS = Path(__file__).parent
COMPONENT_CODES = {"exp", "m1", "m2", "m3", "m4", "proc"}
PAGE_SCHEMES = {"book", "pdf", "bekker", "section_number"}
SOURCE_BLOCK_BUDGET_BYTES = 2500  # raised from 1500 once pdf_page_start/end became standard fields


# -------------------- Tiny parser --------------------
# The format is narrow: top-level `key: value` lines, plus a `chunks:` field
# whose value is a list of dicts (each with its own `key: value` lines indented).
# We do not need full YAML — a line-state-machine is enough and dependency-free.

def _parse_value(raw: str):
    """Parse a scalar or simple list value."""
    raw = raw.strip()
    if raw == "":
        return ""
    if raw.lower() in ("true", "false"):
        return raw.lower() == "true"
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [x.strip() for x in inner.split(",")]
    try:
        return int(raw)
    except ValueError:
        return raw


def parse_plan(text: str):
    """Return list of (slug, source_dict, raw_block_text)."""
    parts = re.split(r"(?m)^### ", text)
    out = []
    for part in parts[1:]:
        if not part.strip():
            continue
        head, _, body = part.partition("\n")
        slug = head.strip()
        block_raw = body
        # Stop the block at the next top-level marker (defensive — split should handle).
        source = {}
        chunks: list[dict] = []
        cur_chunk: dict | None = None
        in_chunks = False
        for line in body.splitlines():
            if not line.strip():
                continue
            if line.startswith("<!--") or line.startswith("# "):
                continue
            # In `chunks:` list?
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            if not in_chunks:
                if stripped.startswith("chunks:"):
                    in_chunks = True
                    continue
                if ":" in stripped:
                    k, _, v = stripped.partition(":")
                    source[k.strip()] = _parse_value(v)
                continue
            # We are inside chunks list.
            if indent == 0 and ":" in stripped:
                # Back to top level — append last chunk and exit list.
                if cur_chunk is not None:
                    chunks.append(cur_chunk)
                    cur_chunk = None
                in_chunks = False
                k, _, v = stripped.partition(":")
                source[k.strip()] = _parse_value(v)
                continue
            if stripped.startswith("- "):
                if cur_chunk is not None:
                    chunks.append(cur_chunk)
                cur_chunk = {}
                rest = stripped[2:]
                if ":" in rest:
                    k, _, v = rest.partition(":")
                    cur_chunk[k.strip()] = _parse_value(v)
                continue
            if cur_chunk is not None and ":" in stripped:
                k, _, v = stripped.partition(":")
                cur_chunk[k.strip()] = _parse_value(v)
        if cur_chunk is not None:
            chunks.append(cur_chunk)
        source["chunks"] = chunks
        out.append((slug, source, block_raw))
    return out


# -------------------- Checks --------------------

def check_source(slug: str, src: dict, block_raw: str, warnings: list, failures: list):
    required = ("pdf_total_pages", "toc_path", "pdf_path", "whole_document", "chunks")
    for f in required:
        if f not in src:
            failures.append(f"{slug}: missing field '{f}'")
    if any(f not in src for f in required):
        return 0

    toc = ROOT / src["toc_path"]
    pdf = ROOT / src["pdf_path"]
    if not toc.exists():
        failures.append(f"{slug}: toc_path does not exist: {src['toc_path']}")
    if not pdf.exists():
        failures.append(f"{slug}: pdf_path does not exist: {src['pdf_path']}")

    # pdfinfo agreement
    if pdf.exists():
        try:
            out = subprocess.run(
                ["pdfinfo", str(pdf)], capture_output=True, text=True, check=True
            )
            pages_line = next(
                (ln for ln in out.stdout.splitlines() if ln.startswith("Pages:")), None
            )
            if pages_line is None:
                warnings.append(f"{slug}: pdfinfo had no 'Pages:' line")
            else:
                actual = int(pages_line.split()[1])
                declared = src["pdf_total_pages"]
                if actual != declared:
                    failures.append(
                        f"{slug}: pdfinfo says {actual} pages, plan declares {declared}"
                    )
        except subprocess.CalledProcessError as e:
            warnings.append(f"{slug}: pdfinfo failed: {e}")
        except Exception as e:  # noqa
            warnings.append(f"{slug}: pdfinfo error: {e}")

    # Per-chunk
    toc_text = toc.read_text() if toc.exists() else ""
    pdf_total = src.get("pdf_total_pages", 0) or 0
    chunks = src.get("chunks", []) or []
    if not isinstance(chunks, list) or not chunks:
        failures.append(f"{slug}: chunks list is empty or malformed")
        return 0

    chunk_count = 0
    for ch in chunks:
        chid = ch.get("id", "?")
        for k in ("id", "title", "page_scheme", "page_start", "page_end",
                  "components", "verified", "rationale"):
            if k not in ch:
                failures.append(f"{slug}/{chid}: missing key '{k}'")

        scheme = ch.get("page_scheme")
        if scheme not in PAGE_SCHEMES:
            failures.append(f"{slug}/{chid}: invalid page_scheme '{scheme}'")

        comps = ch.get("components", [])
        if not isinstance(comps, list) or not comps:
            failures.append(f"{slug}/{chid}: components must be a non-empty list")
        else:
            for c in comps:
                if c not in COMPONENT_CODES:
                    failures.append(f"{slug}/{chid}: unknown component '{c}'")

        ps, pe = ch.get("page_start"), ch.get("page_end")
        if scheme in ("book", "pdf"):
            if not (isinstance(ps, int) and isinstance(pe, int)):
                failures.append(f"{slug}/{chid}: page_start/page_end must be integers for scheme '{scheme}'")
            else:
                if ps < 1:
                    failures.append(f"{slug}/{chid}: page_start ({ps}) < 1")
                if ps > pe:
                    failures.append(f"{slug}/{chid}: page_start ({ps}) > page_end ({pe})")
                if scheme == "pdf" and pe > pdf_total:
                    failures.append(
                        f"{slug}/{chid}: page_end ({pe}) > pdf_total_pages ({pdf_total})"
                    )
                if scheme == "book" and pe > pdf_total:
                    # Soft: book pages can exceed PDF page count when front matter is small,
                    # but if the gap is large it's likely a typo.
                    if pe - pdf_total > 50:
                        warnings.append(
                            f"{slug}/{chid}: book page_end ({pe}) exceeds pdf_total ({pdf_total}) by > 50; check"
                        )

        # TOC anchor: title fragment, chapter id, or page number must appear in toc.md
        title = str(ch.get("title", ""))
        anchors = []
        # First significant word(s) of title
        first_word = next(
            (w for w in re.split(r"[\s—–\-]+", title) if len(w) > 3), title
        )
        if first_word:
            anchors.append(first_word.lower())
        if isinstance(ps, int):
            anchors.append(str(ps))
        # The chunk id's local part
        local_id = str(chid).split("/")[-1]
        if local_id:
            anchors.append(local_id.lower())

        toc_lower = toc_text.lower()
        if not any(a in toc_lower for a in anchors if a):
            failures.append(
                f"{slug}/{chid}: no TOC anchor — none of {anchors!r} found in toc.md"
            )

        chunk_count += 1

    # Volume budget
    if len(block_raw.encode()) > SOURCE_BLOCK_BUDGET_BYTES:
        warnings.append(
            f"{slug}: source-block is {len(block_raw.encode())} bytes (> {SOURCE_BLOCK_BUDGET_BYTES})"
        )

    return chunk_count


# -------------------- Manifest target coverage --------------------

MANIFEST_FILES = {
    "exp": "exp-exploratory.md",
    "m1": "m1-pragma-dialectical.md",
    "m2": "m2-hermeneutic.md",
    "m3": "m3-skinnerian.md",
    "m4": "m4-dennettian.md",
    "proc": "proc.md",
}


def check_manifest_targets(plan_sources: dict, warnings: list):
    """For each manifest, walk per-slug stanzas and emit a warning when a slug
    declares target chapter(s) — strict (`- target chapters: ...`) or prose-
    embedded (`- Reeve translation ... target chapter is Book Beta ...`) — but
    no chunk tagged with that manifest's component covers it.
    """
    slug_line = re.compile(r"^- `([a-z0-9\-]+)`")
    target_word = re.compile(r"\btarget\b", re.IGNORECASE)
    for code, fname in MANIFEST_FILES.items():
        path = MANIFESTS / fname
        if not path.exists():
            warnings.append(f"manifest {fname} not found; skipping target coverage")
            continue
        lines = path.read_text().splitlines()
        i = 0
        while i < len(lines):
            m = slug_line.match(lines[i])
            if not m:
                i += 1
                continue
            slug = m.group(1)
            target_desc = None
            j = i + 1
            while j < len(lines):
                line = lines[j]
                if not line.strip():
                    break  # blank line — end of stanza
                if not line[0].isspace():
                    break  # unindented — next slug or section
                if target_desc is None and target_word.search(line):
                    target_desc = line.strip().lstrip("- ").strip()
                j += 1
            if target_desc:
                if slug not in plan_sources:
                    warnings.append(
                        f"manifest {code}: source '{slug}' has target '{target_desc[:80]}' but absent from chunking-plan"
                    )
                else:
                    src = plan_sources[slug]
                    chunks_for_code = [
                        ch for ch in src.get("chunks", []) or []
                        if code in (ch.get("components") or [])
                    ]
                    if not chunks_for_code and not src.get("whole_document"):
                        warnings.append(
                            f"manifest {code}: '{slug}' has target '{target_desc[:60]}…' but no chunk tagged {code}"
                        )
            i = j


# -------------------- Main --------------------

def main():
    if not PLAN.exists():
        print(f"FAIL: {PLAN} does not exist")
        sys.exit(1)
    text = PLAN.read_text()
    parsed = parse_plan(text)
    plan_sources = {slug: src for slug, src, _ in parsed}

    warnings: list[str] = []
    failures: list[str] = []
    total_chunks = 0
    for slug, src, raw in parsed:
        total_chunks += check_source(slug, src, raw, warnings, failures)

    check_manifest_targets(plan_sources, warnings)

    for w in warnings:
        print(f"WARN: {w}")
    for f in failures:
        print(f"FAIL: {f}")
    if failures:
        print(
            f"FAIL: {len(failures)} hard failures, {len(warnings)} warnings, "
            f"{total_chunks} chunks across {len(parsed)} sources"
        )
        sys.exit(1)
    print(
        f"OK: {total_chunks} chunks across {len(parsed)} sources verified "
        f"({len(warnings)} warnings)"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
