from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict


KEY_AT_TOPLEVEL_BLOCK_RE = re.compile(r"^\s*([A-Za-z0-9_.\-:]+)\s*=\s*\{")


def _strip_line_comment(line: str) -> str:
    # Vic3 script comments use '#'
    return line.split("#", 1)[0]


def iter_top_level_block_keys_txt(path: Path) -> list[str]:
    """
    Extract keys that look like 'foo = { ... }' only at brace depth 0.
    Heuristic parser intended for Vic3 script-ish files.
    """
    try:
        text = path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()
    except Exception:
        text = path.read_text(errors="ignore").splitlines()

    keys: list[str] = []
    depth = 0
    for raw in text:
        line = _strip_line_comment(raw)

        if depth == 0:
            m = KEY_AT_TOPLEVEL_BLOCK_RE.match(line)
            if m:
                token = m.group(1)
                if token and token != "namespace":
                    keys.append(token)

        depth += line.count("{")
        depth -= line.count("}")
        if depth < 0:
            depth = 0

    return keys


def collect_event_definitions(mod_root: Path) -> dict[str, list[str]]:
    """
    Collect event definition keys in events/*.txt by looking for top-level 'X = { ... }'.

    Note: this finds keys like 'victoria.1', 'peoples_springtime.3', etc.
    """
    out: DefaultDict[str, list[str]] = defaultdict(list)
    ev_dir = mod_root / "events"
    if not ev_dir.exists():
        return dict(out)

    for path in ev_dir.rglob("*.txt"):
        rel = path.relative_to(mod_root).as_posix()
        keys = iter_top_level_block_keys_txt(path)
        for k in keys:
            out[k].append(rel)

    return dict(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--a", type=Path, required=True, help="Path to mod A root.")
    parser.add_argument("--b", type=Path, required=True, help="Path to mod B root.")
    parser.add_argument("--a-name", type=str, default=None, help="Display name for mod A.")
    parser.add_argument("--b-name", type=str, default=None, help="Display name for mod B.")
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output markdown report path.",
    )
    args = parser.parse_args()

    a_root = args.a.resolve()
    b_root = args.b.resolve()
    if not a_root.exists():
        raise SystemExit(f"Mod A root not found: {a_root}")
    if not b_root.exists():
        raise SystemExit(f"Mod B root not found: {b_root}")

    a_name = args.a_name or a_root.name
    b_name = args.b_name or b_root.name
    out_path = args.out.resolve()

    a_defs = collect_event_definitions(a_root)
    b_defs = collect_event_definitions(b_root)
    dup = sorted(set(a_defs) & set(b_defs))

    lines: list[str] = []
    lines.append(f"# {a_name} vs {b_name} — duplicate event *definitions* (heuristic)")
    lines.append("")
    lines.append(f"- {a_name} root: `{a_root.as_posix()}`")
    lines.append(f"- {b_name} root: `{b_root.as_posix()}`")
    lines.append("")
    lines.append(f"- Total duplicate event definition keys: **{len(dup)}**")
    lines.append("")

    for k in dup:
        lines.append(f"## `{k}`")
        for f in sorted(set(a_defs[k])):
            lines.append(f"- {a_name}: `{f}`")
        for f in sorted(set(b_defs[k])):
            lines.append(f"- {b_name}: `{f}`")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print("Wrote report:", out_path)
    print("Summary:", "event_definition_dups=", len(dup))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

