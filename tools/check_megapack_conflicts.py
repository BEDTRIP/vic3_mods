from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict


KEY_AT_TOPLEVEL_RE = re.compile(r"^\s*([A-Za-z0-9_.\-:]+)\s*=")
LOC_KEY_RE = re.compile(r'^\s*([^\s:#][^:#]*?)\s*:\s*[0-9]+\s*"')
EVENT_ID_RE = re.compile(r"\bid\s*=\s*([A-Za-z0-9_.\-]+)")

# A small blocklist to reduce obvious false positives when parsing top-level keys.
NON_DEFINITION_KEYS = {
    "if",
    "else",
    "elseif",
    "while",
    "for",
    "limit",
    "modifier",
    "add",
    "remove",
    "set",
    "trigger",
    "effect",
}


def _strip_line_comment(line: str) -> str:
    # Vic3 script comments use '#'
    return line.split("#", 1)[0]


def iter_top_level_keys_txt(path: Path) -> list[str]:
    """
    Extract keys that look like 'foo = ...' only at brace depth 0.
    This is a heuristic parser intended for Vic3-style script files.
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
            m = KEY_AT_TOPLEVEL_RE.match(line)
            if m:
                token = m.group(1)
                # Handle Vic3 script modifiers like REPLACE:foo, INJECT:bar, REPLACE_OR_CREATE:baz, etc.
                # We normalize those to the underlying key ('foo', 'bar', 'baz') so cross-mod duplicates are detected.
                if ":" in token:
                    prefix, rest = token.split(":", 1)
                    if prefix.isupper():
                        token = rest
                k = token
                if k not in NON_DEFINITION_KEYS and not k.startswith("@") and k:
                    keys.append(k)

        # naive brace tracking (good enough for Vic3 mod scripts)
        depth += line.count("{")
        depth -= line.count("}")
        if depth < 0:
            depth = 0

    return keys


def collect_common_keys(mod_root: Path) -> dict[str, dict[str, list[str]]]:
    """
    Returns:
      category_path -> key -> [relative_file_paths...]
    Where category_path is e.g. 'common/buildings' or 'common/technology/technologies'
    """
    by_cat: dict[str, dict[str, list[str]]] = {}
    common_dir = mod_root / "common"
    if not common_dir.exists():
        return by_cat

    for path in common_dir.rglob("*.txt"):
        rel = path.relative_to(mod_root).as_posix()
        cat = "/".join(rel.split("/")[:-1])
        keys = iter_top_level_keys_txt(path)
        if not keys:
            continue
        cat_map = by_cat.setdefault(cat, {})
        for k in keys:
            cat_map.setdefault(k, []).append(rel)

    return by_cat


def collect_localization_keys(mod_root: Path) -> dict[str, list[str]]:
    out: DefaultDict[str, list[str]] = defaultdict(list)
    loc_dir = mod_root / "localization"
    if not loc_dir.exists():
        return dict(out)

    for path in loc_dir.rglob("*.yml"):
        rel = path.relative_to(mod_root).as_posix()
        try:
            lines = path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()
        except Exception:
            lines = path.read_text(errors="ignore").splitlines()

        for ln in lines:
            s = _strip_line_comment(ln).rstrip()
            if not s:
                continue
            if s.lstrip().startswith("l_"):  # header like: l_english:
                continue
            m = LOC_KEY_RE.match(s)
            if m:
                k = m.group(1).strip()
                out[k].append(rel)

    return dict(out)


def collect_event_ids(mod_root: Path) -> dict[str, list[str]]:
    out: DefaultDict[str, list[str]] = defaultdict(list)
    ev_dir = mod_root / "events"
    if not ev_dir.exists():
        return dict(out)

    for path in ev_dir.rglob("*.txt"):
        rel = path.relative_to(mod_root).as_posix()
        try:
            text = path.read_text(encoding="utf-8-sig", errors="ignore")
        except Exception:
            text = path.read_text(errors="ignore")

        # strip single-line comments, then regex-scan
        cleaned = "\n".join(_strip_line_comment(l) for l in text.splitlines())
        for m in EVENT_ID_RE.finditer(cleaned):
            eid = m.group(1)
            # reduce some false positives
            if eid in {"yes", "no"}:
                continue
            out[eid].append(rel)

    return dict(out)


def _write_report(
    report_path: Path,
    *,
    megapack_root: Path,
    common_keys: dict[str, dict[str, list[str]]],
    loc_keys: dict[str, list[str]],
    event_ids: dict[str, list[str]],
) -> None:
    lines: list[str] = []
    lines.append("# Megapack Internal Conflicts Report")
    lines.append("")
    lines.append(f"- Megapack root: `{megapack_root.as_posix()}`")
    lines.append("")
    lines.append(
        "This report finds **duplicate identifiers** (same key/id defined multiple times within the megapack). "
        "It is a heuristic and may include a few false positives."
    )
    lines.append("")

    # common duplicates by category
    lines.append("## common/*: duplicate top-level keys")
    total_common_dups = 0
    for cat in sorted(common_keys.keys()):
        cat_map = common_keys[cat]
        # Find keys that appear in multiple files
        duplicates = {k: files for k, files in cat_map.items() if len(files) > 1}
        if not duplicates:
            continue
        total_common_dups += len(duplicates)
        lines.append("")
        lines.append(f"### {cat} — {len(duplicates)} duplicates")
        for k in sorted(duplicates.keys())[:250]:
            files = sorted(set(duplicates[k]))
            lines.append(f"- `{k}` (defined in {len(files)} files)")
            for f in files[:10]:
                lines.append(f"  - `{f}`")
            if len(files) > 10:
                lines.append(f"  - ... and {len(files) - 10} more files")
        if len(duplicates) > 250:
            lines.append(f"- ... and {len(duplicates) - 250} more duplicates")
    if total_common_dups == 0:
        lines.append("")
        lines.append("- (no duplicates detected by this heuristic)")

    lines.append("")
    lines.append("## localization: duplicate localization keys")
    loc_dup = {k: files for k, files in loc_keys.items() if len(files) > 1}
    lines.append(f"- Total duplicate localization keys: **{len(loc_dup)}**")
    for k in sorted(loc_dup.keys())[:250]:
        files = sorted(set(loc_dup[k]))
        lines.append(f"  - `{k}` (in {len(files)} files)")
        for f in files[:5]:
            lines.append(f"    - `{f}`")
        if len(files) > 5:
            lines.append(f"    - ... and {len(files) - 5} more files")
    if len(loc_dup) > 250:
        lines.append(f"  - ... and {len(loc_dup) - 250} more")

    lines.append("")
    lines.append("## events: duplicate event ids (`id = ...` anywhere in events/*.txt)")
    ev_dup = {k: files for k, files in event_ids.items() if len(files) > 1}
    lines.append(f"- Total duplicate event ids: **{len(ev_dup)}**")
    for eid in sorted(ev_dup.keys())[:250]:
        files = sorted(set(ev_dup[eid]))
        lines.append(f"  - `{eid}` (in {len(files)} files)")
        for f in files[:5]:
            lines.append(f"    - `{f}`")
        if len(files) > 5:
            lines.append(f"    - ... and {len(files) - 5} more files")
    if len(ev_dup) > 250:
        lines.append(f"  - ... and {len(ev_dup) - 250} more")

    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check for internal conflicts within a megapack compatibility patch"
    )
    parser.add_argument(
        "--megapack",
        type=Path,
        default=None,
        help="Path to megapack root (folder containing common/, localization/, etc.).",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="Workspace root (defaults to current dir).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output markdown report path.",
    )
    args = parser.parse_args()

    ws = args.workspace.resolve()
    megapack_root = (args.megapack or (ws / "__megapacks" / "megapack_no_tgr")).resolve()
    out_path = (
        args.out or (megapack_root.parent / f"conflicts_{megapack_root.name}_internal.md")
    ).resolve()

    if not megapack_root.exists():
        raise SystemExit(f"Megapack root not found: {megapack_root}")

    print(f"Checking megapack: {megapack_root}")
    print("Collecting common keys...")
    common_keys = collect_common_keys(megapack_root)
    print("Collecting localization keys...")
    loc_keys = collect_localization_keys(megapack_root)
    print("Collecting event ids...")
    event_ids = collect_event_ids(megapack_root)

    _write_report(
        out_path,
        megapack_root=megapack_root,
        common_keys=common_keys,
        loc_keys=loc_keys,
        event_ids=event_ids,
    )

    # Count duplicates
    total_common_dups = 0
    for cat_map in common_keys.values():
        for files in cat_map.values():
            if len(files) > 1:
                total_common_dups += 1
    loc_dup_count = sum(1 for files in loc_keys.values() if len(files) > 1)
    ev_dup_count = sum(1 for files in event_ids.values() if len(files) > 1)

    print("Wrote report:", out_path)
    print(
        "Summary:",
        "common_key_dups=",
        total_common_dups,
        "loc_key_dups=",
        loc_dup_count,
        "event_id_dups=",
        ev_dup_count,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
