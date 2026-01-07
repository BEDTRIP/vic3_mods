from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict


NAME_RE = re.compile(r'\bname\s*=\s*"([^"]+)"')
ICON_RE = re.compile(r"^\s*icon\s*=\s*([A-Za-z0-9_.:-]+)\s*$")
TYPES_START_RE = re.compile(r"^\s*types\s+([A-Za-z0-9_.:-]+)\s*\{")
TYPE_DEF_RE = re.compile(r"^\s*type\s+([A-Za-z0-9_.:-]+)\s*=")


def _strip_comment(line: str) -> str:
    # GUI files use '#' comments in many projects; keep it simple.
    return line.split("#", 1)[0]


def extract_gui_identifiers(mod_root: Path) -> dict[str, dict[str, list[str]]]:
    """
    Heuristic extraction of GUI identifiers from *.gui:
    - `name = "..."` strings
    - `icon = foo` tokens (useful for texticons)
    - `types <namespace> { ... type <name> = ... }` pairs (stored as "<namespace>::<type>")

    Returns:
      kind -> id -> [relative_gui_file_paths...]
    """
    by_kind: dict[str, DefaultDict[str, list[str]]] = {
        "name": defaultdict(list),
        "icon": defaultdict(list),
        "type": defaultdict(list),
    }

    for p in mod_root.rglob("*.gui"):
        rel = p.relative_to(mod_root).as_posix()
        try:
            lines = p.read_text(encoding="utf-8-sig", errors="ignore").splitlines()
        except Exception:
            lines = p.read_text(errors="ignore").splitlines()

        # Track 'types <namespace> { ... }' blocks by brace depth.
        depth = 0
        cur_types: str | None = None
        cur_types_depth: int | None = None

        for raw in lines:
            line = _strip_comment(raw).rstrip()
            if not line.strip():
                depth += line.count("{") - line.count("}")
                continue

            # record name="..."
            for n in NAME_RE.findall(line):
                by_kind["name"][n].append(rel)

            # record icon = foo
            m_icon = ICON_RE.match(line)
            if m_icon:
                by_kind["icon"][m_icon.group(1)].append(rel)

            # types block enter
            m_types = TYPES_START_RE.match(line)
            if m_types:
                cur_types = m_types.group(1)
                cur_types_depth = depth

            # record type definitions inside current types block
            if cur_types is not None and cur_types_depth is not None and depth >= cur_types_depth + 1:
                m_type = TYPE_DEF_RE.match(line)
                if m_type:
                    key = f"{cur_types}::{m_type.group(1)}"
                    by_kind["type"][key].append(rel)

            # update brace depth and exit types block if needed
            depth += line.count("{")
            depth -= line.count("}")
            if depth < 0:
                depth = 0

            if cur_types is not None and cur_types_depth is not None and depth <= cur_types_depth:
                cur_types = None
                cur_types_depth = None

    return {k: dict(v) for k, v in by_kind.items()}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare GUI identifiers between two Vic3 mods (heuristic)."
    )
    parser.add_argument("--a", type=Path, required=True, help="Path to mod A root")
    parser.add_argument("--b", type=Path, required=True, help="Path to mod B root")
    parser.add_argument("--a-name", type=str, default="A", help="Display name for mod A")
    parser.add_argument("--b-name", type=str, default="B", help="Display name for mod B")
    args = parser.parse_args()

    a_root = args.a.resolve()
    b_root = args.b.resolve()
    if not a_root.exists():
        raise SystemExit(f"Mod A not found: {a_root}")
    if not b_root.exists():
        raise SystemExit(f"Mod B not found: {b_root}")

    a = extract_gui_identifiers(a_root)
    b = extract_gui_identifiers(b_root)

    for kind in ("name", "icon", "type"):
        a_map = a[kind]
        b_map = b[kind]
        inter = sorted(set(a_map) & set(b_map))
        print("")
        print(f"== {kind} ==")
        print(f"{args.a_name} count:", len(a_map))
        print(f"{args.b_name} count:", len(b_map))
        print("Intersect:", len(inter))
        for n in inter[:200]:
            print("-", n)
            for f in sorted(set(a_map[n]))[:8]:
                print(f"  - {args.a_name}: {f}")
            for f in sorted(set(b_map[n]))[:8]:
                print(f"  - {args.b_name}: {f}")
        if len(inter) > 200:
            print(f"... and {len(inter) - 200} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

