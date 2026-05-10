#!/usr/bin/env python3
"""Stage 3 chunk-text extractor.

Reads chunking-plan.md and produces a .txt file per chunk under
`docs/sources/<slug>/chunks/<chunk-tail>.txt`.

Pipeline:
  pdftotext -layout -f <pdf_start> -l <pdf_end>
  split on form-feed; per page:
    - drop running-header lines (auto-detected via digit-normalized repetition)
    - drop bare page-number lines (with footnote-marker exemption)
    - normalize ligatures
    - rejoin end-of-line hyphens (hunspell en_US-large)
    - collapse 3+ blank lines
  wrap each page with `=== p. <N> ===`
  prepend header metadata block

Two modes:
  --slug <slug>       Batch: extract every chunk for <slug>.
  --slug <slug> --chunk-id <tail>
                       Extract a single chunk for <slug> by tail id.

The page-marker base depends on `page_scheme` from the plan:
  book              -> book page integers (page_start, page_start+1, ...)
  pdf               -> PDF page integers (= page_start for pdf scheme)
  bekker            -> PDF page integers (Bekker refs live in body text)
  section_number    -> PDF page integers (section refs live in body text)
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

# Import the existing plan parser; ROOT comes from that module too.
from verify_chunking_plan import parse_plan, PLAN, ROOT  # type: ignore

# -------------------- text-cleanup helpers --------------------

LIGATURES = {
    "ﬁ": "fi",
    "ﬂ": "fl",
    "ﬀ": "ff",
    "ﬃ": "ffi",
    "ﬄ": "ffl",
    "ﬅ": "ft",
    "ﬆ": "st",
}


def normalize_ligatures(text: str) -> str:
    for k, v in LIGATURES.items():
        text = text.replace(k, v)
    return text


def hunspell_unknown(words: list[str]) -> set[str]:
    """Return the subset of `words` that hunspell en_US-large flags as unknown."""
    if not words:
        return set()
    inp = "\n".join(words).encode("utf-8")
    r = subprocess.run(
        ["hunspell", "-d", "en_US-large", "-l"],
        input=inp, capture_output=True, check=True,
    )
    return {line.decode("utf-8").strip() for line in r.stdout.splitlines() if line.strip()}


HYPHEN_END_RE = re.compile(r"(\S+)-\s*$")
WORD_START_RE = re.compile(r"^(\s*)(\S+)(.*)$")


def collect_hyphen_candidates(text: str) -> list[tuple[str, str]]:
    """Find candidate hyphenated line-end joins. Returns (left_token, right_first_token) pairs."""
    lines = text.split("\n")
    out: list[tuple[str, str]] = []
    for i in range(len(lines) - 1):
        m = HYPHEN_END_RE.search(lines[i])
        if not m:
            continue
        nm = WORD_START_RE.match(lines[i + 1])
        if not nm:
            continue
        out.append((m.group(1), nm.group(2)))
    return out


def apply_dehyphenation(text: str, unknown_joins: set[str]) -> str:
    """Rejoin hyphenated end-of-line tokens unless joined form is in unknown_joins.

    Chains correctly: after a join, if the resulting line still ends in '-',
    re-pair with the following line.
    """
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        consumed = i
        while True:
            m = HYPHEN_END_RE.search(line)
            if not m or consumed + 1 >= len(lines):
                break
            nm = WORD_START_RE.match(lines[consumed + 1])
            if not nm:
                break
            left = m.group(1)
            right_first = nm.group(2)
            right_rest = nm.group(3)
            joined_no_hyphen = left + right_first
            lookup = re.sub(r"[^\w]+$", "", joined_no_hyphen).lower()
            if lookup in unknown_joins:
                new_token = left + "-" + right_first
            else:
                new_token = left + right_first
            prefix = line[: m.start()]
            line = prefix + new_token + right_rest
            consumed += 1
        out.append(line)
        i = consumed + 1
    return "\n".join(out)


DIGIT_RUN_RE = re.compile(r"\d+")


def _header_key(s: str) -> str:
    """Normalize header candidate: collapse digit runs to '#', whitespace to single space."""
    return DIGIT_RUN_RE.sub("#", " ".join(s.split())).strip()


def detect_repeating_headers(pages: list[str], min_pages: int = 2, max_len: int = 80) -> set[str]:
    """Return normalized keys that appear on >= min_pages pages."""
    counter: Counter[str] = Counter()
    for page in pages:
        seen_in_page: set[str] = set()
        for raw_line in page.split("\n"):
            s = raw_line.strip()
            if not s or len(s) > max_len:
                continue
            if re.fullmatch(r"\d+", s):
                continue
            if len(s) < 4:
                continue
            key = _header_key(s)
            if not key or key == "#":
                continue
            if key in seen_in_page:
                continue
            seen_in_page.add(key)
            counter[key] += 1
    return {key for key, n in counter.items() if n >= min_pages}


PAGE_NUMBER_RE = re.compile(r"^\s*\d+\s*$")
FOOTNOTE_BODY_START_RE = re.compile(r"^\s*\[")


def clean_page(page_text: str, header_keys_to_strip: set[str]) -> str:
    lines = page_text.split("\n")
    out_lines: list[str] = []
    for idx, line in enumerate(lines):
        s = line.strip()
        if PAGE_NUMBER_RE.fullmatch(line):
            # Preserve if next non-blank line is a footnote body marker.
            is_footnote_marker = False
            for j in range(idx + 1, min(idx + 3, len(lines))):
                follow = lines[j]
                if not follow.strip():
                    continue
                if FOOTNOTE_BODY_START_RE.match(follow):
                    is_footnote_marker = True
                break
            if not is_footnote_marker:
                continue
        elif s and _header_key(s) in header_keys_to_strip:
            continue
        out_lines.append(line)
    return "\n".join(out_lines)


def collapse_blanks(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text)


# -------------------- extraction --------------------

def _chunk_pdf_range(chunk: dict) -> tuple[int, int]:
    """Return (pdf_start, pdf_end) for a chunk.

    For chunks with explicit pdf_page_start/end, use those. Otherwise fall back to
    page_start/end (valid only when page_scheme == 'pdf', e.g. whole_document chunks).
    """
    if "pdf_page_start" in chunk and "pdf_page_end" in chunk:
        return int(chunk["pdf_page_start"]), int(chunk["pdf_page_end"])
    return int(chunk["page_start"]), int(chunk["page_end"])


def _marker_base(chunk: dict, pdf_start: int) -> tuple[int, str]:
    """Return (marker_start, scheme_label) for page markers.

    For book scheme: marker_start = book page_start.
    For all other schemes (pdf/bekker/section_number): marker_start = pdf_start
    (the scheme's native citation lives in the body text, not in page boundaries).
    """
    scheme = str(chunk.get("page_scheme", "pdf"))
    if scheme == "book":
        return int(chunk["page_start"]), "book"
    return pdf_start, scheme


def extract_chunk_text(
    pdf_path: Path,
    pdf_start: int,
    pdf_end: int,
    marker_start: int,
    scheme_label: str,
    slug: str,
    chunk_id_tail: str,
    title: str,
    chunk_page_start: object,
    chunk_page_end: object,
) -> str:
    r = subprocess.run(
        ["pdftotext", "-layout", "-f", str(pdf_start), "-l", str(pdf_end), str(pdf_path), "-"],
        capture_output=True, check=True,
    )
    raw = r.stdout.decode("utf-8", errors="replace")

    pages_raw = raw.split("\f")
    while pages_raw and not pages_raw[-1].strip():
        pages_raw.pop()

    expected = pdf_end - pdf_start + 1
    extracted = len(pages_raw)
    if extracted != expected:
        print(
            f"  note: {slug}/{chunk_id_tail}: extracted {extracted} pages, plan range {expected}"
            " (trailing blank page trimmed)",
            file=sys.stderr,
        )

    pages_raw = [normalize_ligatures(p) for p in pages_raw]
    repeating = detect_repeating_headers(pages_raw)

    # Build hunspell candidate set across the whole chunk.
    candidates: set[str] = set()
    for p in pages_raw:
        for left, right in collect_hyphen_candidates(p):
            joined = left + right
            lookup = re.sub(r"[^\w]+$", "", joined).lower()
            if lookup:
                candidates.add(lookup)
    unknown = hunspell_unknown(sorted(candidates))

    # Build output.
    rel_pdf = str(pdf_path.relative_to(ROOT)) if pdf_path.is_absolute() else str(pdf_path)
    parts: list[str] = []
    parts.append(f"=== chunk: {slug}/{chunk_id_tail} ===")
    parts.append(f"title: {title}")
    parts.append(f"source_pdf: {rel_pdf}")
    parts.append(f"pdf_pages: {pdf_start}-{pdf_end}")
    parts.append(f"page_scheme: {scheme_label}")
    parts.append(f"plan_page_start: {chunk_page_start}")
    parts.append(f"plan_page_end: {chunk_page_end}")
    if extracted != expected:
        parts.append(f"extracted_pages: {extracted} (plan nominally {expected}; trailing blank trimmed)")
    parts.append(
        "extraction: pdftotext -layout, post-processed "
        "(ligature-normalize, dehyphenate via hunspell en_US-large, page-markers, header-strip)"
    )
    parts.append("")

    for i, page_text in enumerate(pages_raw):
        marker = marker_start + i if scheme_label == "book" else pdf_start + i
        cleaned = clean_page(page_text, repeating)
        dehyphenated = apply_dehyphenation(cleaned, unknown)
        squashed = collapse_blanks(dehyphenated).strip("\n")
        parts.append(f"=== p. {marker} ===\n")
        parts.append(squashed)
        parts.append("")

    return "\n".join(parts) + "\n"


def chunk_tail(chunk_id: str) -> str:
    """Return the chunk-id tail (the part after the last '/')."""
    return chunk_id.rsplit("/", 1)[-1]


def extract_one(source: dict, chunk: dict, out_root: Path) -> Path:
    """Extract one chunk; write to docs/sources/<slug>/chunks/<tail>.txt. Returns the path."""
    slug = chunk["id"].split("/", 1)[0]
    tail = chunk_tail(chunk["id"])
    pdf_path = (ROOT / source["pdf_path"]).resolve()
    if not pdf_path.exists():
        raise FileNotFoundError(f"pdf not found: {pdf_path}")
    pdf_start, pdf_end = _chunk_pdf_range(chunk)
    marker_start, scheme_label = _marker_base(chunk, pdf_start)
    text = extract_chunk_text(
        pdf_path=pdf_path,
        pdf_start=pdf_start,
        pdf_end=pdf_end,
        marker_start=marker_start,
        scheme_label=scheme_label,
        slug=slug,
        chunk_id_tail=tail,
        title=str(chunk.get("title", "")),
        chunk_page_start=chunk.get("page_start"),
        chunk_page_end=chunk.get("page_end"),
    )
    out_dir = out_root / "docs" / "sources" / slug / "chunks"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{tail}.txt"
    out_path.write_text(text, encoding="utf-8")
    return out_path


# -------------------- CLI --------------------

def _load_plan_slugs() -> dict[str, tuple[dict, str]]:
    """Return {slug: (source_dict, raw_block_text)}."""
    parsed = parse_plan(PLAN.read_text(encoding="utf-8"))
    return {slug: (src, raw) for slug, src, raw in parsed}


def main() -> int:
    ap = argparse.ArgumentParser(description="Stage 3 chunk-text extractor.")
    ap.add_argument("--slug", required=True, help="Source slug as in chunking-plan.md")
    ap.add_argument("--chunk-id", default=None,
                    help="Optional: extract only this chunk (by tail id, e.g. ch2-rethought-reperceived)")
    args = ap.parse_args()

    plan = _load_plan_slugs()
    if args.slug not in plan:
        print(f"error: slug not in chunking-plan.md: {args.slug}", file=sys.stderr)
        return 2
    source, _ = plan[args.slug]
    chunks = source.get("chunks", [])
    if args.chunk_id is not None:
        chunks = [c for c in chunks if chunk_tail(c["id"]) == args.chunk_id]
        if not chunks:
            print(f"error: chunk-id not in slug: {args.chunk_id}", file=sys.stderr)
            return 2

    for chunk in chunks:
        try:
            path = extract_one(source, chunk, ROOT)
            size = path.stat().st_size
            print(f"wrote {path.relative_to(ROOT)} ({size:,} bytes)")
        except subprocess.CalledProcessError as e:
            print(f"  FAIL: pdftotext failed for {chunk['id']}: rc={e.returncode}", file=sys.stderr)
            return 1
        except Exception as e:  # pragma: no cover
            print(f"  FAIL: {chunk['id']}: {e}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
