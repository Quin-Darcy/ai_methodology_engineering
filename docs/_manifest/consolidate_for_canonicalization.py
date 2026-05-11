#!/usr/bin/env python3
"""Stage 5 helper: join clusters + clustering-input into a canonicalization-input file.

For a given deliverable component (e.g. "proc"), reads:
  - docs/_manifest/<component>-clusters.yaml      (Stage 4 output)
  - docs/_manifest/<component>-clustering-input.yaml  (Stage 4 input; per-directive content)

Joins them so each cluster carries its full member directive content
(source, decision, directive, trigger, qualification, original_directive),
plus the section header the cluster sits under in the clusters file.

Output: docs/_manifest/<component>-canonical-input.yaml

Layout:
  component: ...
  cluster_count: N
  directive_count: M
  clusters:
    - id: c001
      section: "SCOPE / QUESTION DEFINITION"
      label: "..."
      note: "..."
      fork_hint: true|false   # true if note text contains "fork"
      related_to: [...]       # optional
      members:
        - id: "..."
          source: "..."
          decision: keep|adapt
          directive: "..."
          trigger: "..."
          qualification: "..."
          original_directive: "..."  # only if decision == adapt
        ...
    ...

Plain-text YAML parsing (no PyYAML), mirroring consolidate_for_clustering.py.

Usage:
  consolidate_for_canonicalization.py <component>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

MANIFEST = Path(__file__).parent


def yaml_quote(s: str) -> str:
    """Emit a YAML double-quoted scalar with quotes and backslashes escaped."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _scalar(chunk: str, key: str) -> str | None:
    """Read a quoted-string scalar field inside an indented YAML record."""
    pattern = rf'^\s+{re.escape(key)}:\s*(?:"((?:[^"\\]|\\.)*)"|(\S.*?))\s*$'
    m = re.search(pattern, chunk, re.MULTILINE)
    if not m:
        return None
    val = m.group(1) if m.group(1) is not None else m.group(2)
    return val.replace('\\"', '"')


def parse_clustering_input(text: str) -> dict[str, dict]:
    """Parse <component>-clustering-input.yaml directives block into {id: record}.

    Stops at the trailing `drops:` block.
    """
    # Slice off the drops trailer if present so we don't pick up dropped ids.
    drops_marker = re.search(r"^drops:\s*$", text, re.MULTILINE)
    body = text[: drops_marker.start()] if drops_marker else text

    records: dict[str, dict] = {}
    chunks = re.split(r"(?m)^  - id: ", body)[1:]
    for ch in chunks:
        m_id = re.match(r'"([^"]+)"', ch.strip().split("\n", 1)[0])
        if not m_id:
            continue
        rid = m_id.group(1)
        rec = {
            "source": _scalar(ch, "source") or "",
            "decision": (_scalar(ch, "decision") or "").strip(),
            "directive": _scalar(ch, "directive") or "",
            "trigger": _scalar(ch, "trigger") or "",
            "qualification": _scalar(ch, "qualification") or "",
        }
        orig = _scalar(ch, "original_directive")
        if orig is not None:
            rec["original_directive"] = orig
        records[rid] = rec
    return records


def parse_clusters(text: str) -> list[dict]:
    """Parse <component>-clusters.yaml into a list of cluster records, with
    `section` set to the most-recent SECTION header encountered."""
    clusters: list[dict] = []
    current_section: str = ""

    # Iterate lines; SECTION headers are inside `  # SOMETHING` blocks delimited
    # by `# ===...` lines. We pick the header that sits between two === lines.
    lines = text.splitlines()
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        # Detect section header: a `  # ====` line, then `  # NAME`, then `  # ====`.
        if re.match(r"^\s*#\s*=+\s*$", line):
            if i + 2 < n and re.match(r"^\s*#\s*=+\s*$", lines[i + 2]):
                hdr = re.match(r"^\s*#\s*(.+?)\s*$", lines[i + 1])
                if hdr:
                    current_section = hdr.group(1).strip()
                i += 3
                continue
        # Detect cluster start: `  - id: cNNN`
        m = re.match(r"^  - id: (\S+)\s*$", line)
        if m:
            cid = m.group(1).strip()
            # Slurp the cluster record up to the next `  - id:` or end.
            j = i + 1
            while j < n and not re.match(r"^  - id: \S+\s*$", lines[j]) and not re.match(r"^\s*#\s*=+\s*$", lines[j]):
                # Don't break on inline comments like `  # Hajek's heuristics ...`
                if re.match(r"^\s*#", lines[j]) and not re.match(r"^\s+#", lines[j]):
                    break
                j += 1
            body = "\n".join(lines[i:j])

            label = _cluster_field(body, "label") or ""
            note = _cluster_field(body, "note") or ""
            member_ids = _member_ids(body)
            related_to = _related_to(body)
            fork_hint = "fork" in note.lower()

            clusters.append(
                {
                    "id": cid,
                    "section": current_section,
                    "label": label,
                    "note": note,
                    "fork_hint": fork_hint,
                    "related_to": related_to,
                    "member_ids": member_ids,
                }
            )
            i = j
            continue
        i += 1
    return clusters


def _cluster_field(body: str, key: str) -> str | None:
    """Read a top-level cluster scalar field like label/note (indented 4 spaces)."""
    pattern = rf'^    {re.escape(key)}:\s*(?:"((?:[^"\\]|\\.)*)"|(\S.*?))\s*$'
    m = re.search(pattern, body, re.MULTILINE)
    if not m:
        return None
    val = m.group(1) if m.group(1) is not None else m.group(2)
    return val.replace('\\"', '"')


def _member_ids(body: str) -> list[str]:
    """Read the `member_ids:` block of a cluster record."""
    m = re.search(r"^    member_ids:\s*$", body, re.MULTILINE)
    if not m:
        return []
    after = body[m.end():]
    ids: list[str] = []
    for ln in after.splitlines():
        if not ln.strip():
            continue
        mm = re.match(r'^      - "([^"]+)"\s*$', ln)
        if mm:
            ids.append(mm.group(1))
            continue
        # Stop when we leave the member_ids indentation.
        if re.match(r"^    \S", ln) or re.match(r"^  - id:", ln):
            break
    return ids


def _related_to(body: str) -> list[str]:
    """Read the optional `related_to:` block of a cluster record."""
    m = re.search(r"^    related_to:\s*$", body, re.MULTILINE)
    if not m:
        return []
    after = body[m.end():]
    out: list[str] = []
    for ln in after.splitlines():
        if not ln.strip():
            continue
        mm = re.match(r"^      - (\S+)\s*$", ln)
        if mm:
            out.append(mm.group(1))
            continue
        if re.match(r"^    \S", ln) or re.match(r"^  - id:", ln):
            break
    return out


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: consolidate_for_canonicalization.py <component>", file=sys.stderr)
        return 2
    component = sys.argv[1]

    clusters_path = MANIFEST / f"{component}-clusters.yaml"
    input_path = MANIFEST / f"{component}-clustering-input.yaml"
    if not clusters_path.exists():
        print(f"clusters file not found: {clusters_path}", file=sys.stderr)
        return 2
    if not input_path.exists():
        print(f"clustering-input file not found: {input_path}", file=sys.stderr)
        return 2

    directives = parse_clustering_input(input_path.read_text(encoding="utf-8"))
    clusters = parse_clusters(clusters_path.read_text(encoding="utf-8"))

    out: list[str] = []
    out.append(f"component: {component}")
    out.append(f"cluster_count: {len(clusters)}")
    total_members = sum(len(c["member_ids"]) for c in clusters)
    out.append(f"directive_count: {total_members}")
    out.append("clusters:")
    missing: list[str] = []
    for c in clusters:
        out.append(f"  - id: {c['id']}")
        out.append(f"    section: {yaml_quote(c['section'])}")
        out.append(f"    label: {yaml_quote(c['label'])}")
        out.append(f"    note: {yaml_quote(c['note'])}")
        out.append(f"    fork_hint: {'true' if c['fork_hint'] else 'false'}")
        if c["related_to"]:
            out.append("    related_to:")
            for r in c["related_to"]:
                out.append(f"      - {r}")
        out.append("    members:")
        for mid in c["member_ids"]:
            d = directives.get(mid)
            if d is None:
                missing.append(mid)
                continue
            out.append(f"      - id: {yaml_quote(mid)}")
            out.append(f"        source: {yaml_quote(d['source'])}")
            out.append(f"        decision: {d['decision']}")
            out.append(f"        directive: {yaml_quote(d['directive'])}")
            out.append(f"        trigger: {yaml_quote(d['trigger'])}")
            out.append(f"        qualification: {yaml_quote(d['qualification'])}")
            if "original_directive" in d:
                out.append(f"        original_directive: {yaml_quote(d['original_directive'])}")

    output_path = MANIFEST / f"{component}-canonical-input.yaml"
    output_path.write_text("\n".join(out) + "\n", encoding="utf-8")

    if missing:
        print(f"warn: {len(missing)} member ids had no matching directive record:", file=sys.stderr)
        for m in missing[:10]:
            print(f"  - {m}", file=sys.stderr)
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more", file=sys.stderr)
    print(
        f"wrote {output_path}: {len(clusters)} clusters, {total_members} directives"
        f"{f' ({len(missing)} missing)' if missing else ''}"
    )
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
