#!/usr/bin/env python3
"""Stage 4 helper: consolidate per-chunk triage+directives into one clustering-input file.

For a given deliverable component (e.g. "proc"), walks every chunk whose
components tag includes that component, joins the .triage.yaml decisions to the
matching .directives.yaml records, and emits a single flat YAML file with:

  - One entry per surviving directive (KEEP + ADAPT). For ADAPTs, the operative
    `directive` is the adapted phrasing; the original is preserved as
    `original_directive` for audit.
  - A trailing `drops:` section listing the DROPped directive ids with their
    reasons (audit trail).

Output: docs/_manifest/<component>-clustering-input.yaml

Reads triage/directives via plain-text parsing (no PyYAML dependency); both
files have stable, predictable layouts produced by our extraction and triage
templates.

Usage:
  consolidate_for_clustering.py <component>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "docs" / "sources"
MANIFEST = Path(__file__).parent


def iter_triage_files() -> Iterable[Path]:
    return sorted(SOURCES.glob("*/chunks/*.triage.yaml"))


def read_field(text: str, key: str) -> str | None:
    """Read a top-level scalar field from a YAML-ish file (one line, quoted or bare)."""
    m = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*$", text, re.MULTILINE)
    if not m:
        return None
    val = m.group(1).strip()
    if val.startswith('"') and val.endswith('"'):
        val = val[1:-1]
    return val


def read_components(text: str) -> list[str]:
    """Read the components: ["..."] line from a triage or directives YAML."""
    m = re.search(r"^components:\s*\[(.+?)\]\s*$", text, re.MULTILINE)
    if not m:
        return []
    raw = m.group(1)
    return [t.strip().strip('"').strip("'") for t in raw.split(",")]


def parse_triage_records(text: str) -> dict[str, dict]:
    """Parse triage YAML into {id: {decision, reason, adapted_directive}}.

    Triage records have a known fixed shape produced by our template:

      - id: "..."
        decision: keep | adapt | drop
        reason: "..."
        adapted_directive: "..."  (or null)
    """
    records: dict[str, dict] = {}
    chunks = re.split(r"(?m)^  - id: ", text)[1:]
    for ch in chunks:
        m_id = re.match(r'"([^"]+)"', ch.strip().split("\n", 1)[0])
        if not m_id:
            continue
        rid = m_id.group(1)
        decision = _scalar(ch, "decision")
        reason = _scalar(ch, "reason")
        adapted = _scalar(ch, "adapted_directive")
        records[rid] = {
            "decision": decision,
            "reason": reason,
            "adapted_directive": None if adapted in (None, "null", "") else adapted,
        }
    return records


def parse_directive_records(text: str) -> dict[str, dict]:
    """Parse directives YAML into {id: {source, directive, trigger, qualification}}.

    Skips evidence (kept only in the source file as audit trail).
    """
    records: dict[str, dict] = {}
    chunks = re.split(r"(?m)^  - id: ", text)[1:]
    for ch in chunks:
        m_id = re.match(r'"([^"]+)"', ch.strip().split("\n", 1)[0])
        if not m_id:
            continue
        rid = m_id.group(1)
        records[rid] = {
            "source": _scalar(ch, "source") or "",
            "directive": _scalar(ch, "directive") or "",
            "trigger": _scalar(ch, "trigger") or "",
            "qualification": _scalar(ch, "qualification") or "",
        }
    return records


def _scalar(chunk: str, key: str) -> str | None:
    """Read a quoted-string scalar field within an indented YAML record."""
    pattern = rf'^\s+{re.escape(key)}:\s*(?:"((?:[^"\\]|\\.)*)"|(\S.*?))\s*$'
    m = re.search(pattern, chunk, re.MULTILINE)
    if not m:
        return None
    val = m.group(1) if m.group(1) is not None else m.group(2)
    # unescape \" only; we don't try to handle full YAML escape rules
    return val.replace('\\"', '"')


def yaml_quote(s: str) -> str:
    """Emit a YAML double-quoted scalar with quotes and backslashes escaped."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: consolidate_for_clustering.py <component>", file=sys.stderr)
        return 2
    component = sys.argv[1]

    surviving: list[dict] = []
    drops: list[dict] = []
    chunks_seen = 0

    for tpath in iter_triage_files():
        dpath = tpath.with_suffix("").with_suffix(".directives.yaml")
        if not dpath.exists():
            print(f"warn: no directives file for {tpath}", file=sys.stderr)
            continue
        ttext = tpath.read_text(encoding="utf-8")
        dtext = dpath.read_text(encoding="utf-8")
        comps = read_components(dtext) or read_components(ttext)
        if component not in comps:
            continue
        chunks_seen += 1
        triage = parse_triage_records(ttext)
        directives = parse_directive_records(dtext)
        chunk_id = read_field(dtext, "chunk_id") or ""

        for did, drec in directives.items():
            t = triage.get(did)
            if t is None:
                print(f"warn: no triage record for {did}", file=sys.stderr)
                continue
            decision = (t.get("decision") or "").strip()
            if decision == "drop":
                drops.append(
                    {
                        "id": did,
                        "chunk_id": chunk_id,
                        "reason": t.get("reason") or "",
                        "original_directive": drec.get("directive") or "",
                    }
                )
                continue
            if decision not in ("keep", "adapt"):
                print(f"warn: unknown decision '{decision}' on {did}", file=sys.stderr)
                continue
            operative = drec["directive"]
            entry = {
                "id": did,
                "chunk_id": chunk_id,
                "source": drec["source"],
                "decision": decision,
                "directive": operative,
                "trigger": drec["trigger"],
                "qualification": drec["qualification"],
            }
            if decision == "adapt":
                entry["directive"] = t.get("adapted_directive") or operative
                entry["original_directive"] = operative
            surviving.append(entry)

    out: list[str] = []
    out.append(f"component: {component}")
    out.append(f"chunks_in: {chunks_seen}")
    out.append(f"surviving_count: {len(surviving)}")
    out.append(f"drop_count: {len(drops)}")
    out.append(f"directives:")
    for e in surviving:
        out.append(f"  - id: {yaml_quote(e['id'])}")
        out.append(f"    chunk_id: {yaml_quote(e['chunk_id'])}")
        out.append(f"    source: {yaml_quote(e['source'])}")
        out.append(f"    decision: {e['decision']}")
        out.append(f"    directive: {yaml_quote(e['directive'])}")
        out.append(f"    trigger: {yaml_quote(e['trigger'])}")
        out.append(f"    qualification: {yaml_quote(e['qualification'])}")
        if "original_directive" in e:
            out.append(f"    original_directive: {yaml_quote(e['original_directive'])}")
    out.append(f"drops:")
    for d in drops:
        out.append(f"  - id: {yaml_quote(d['id'])}")
        out.append(f"    chunk_id: {yaml_quote(d['chunk_id'])}")
        out.append(f"    reason: {yaml_quote(d['reason'])}")
        out.append(f"    original_directive: {yaml_quote(d['original_directive'])}")

    output_path = MANIFEST / f"{component}-clustering-input.yaml"
    output_path.write_text("\n".join(out) + "\n", encoding="utf-8")

    print(
        f"wrote {output_path}: {len(surviving)} surviving "
        f"({sum(1 for e in surviving if e['decision'] == 'keep')} keep / "
        f"{sum(1 for e in surviving if e['decision'] == 'adapt')} adapt), "
        f"{len(drops)} drops, from {chunks_seen} chunks tagged '{component}'"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
