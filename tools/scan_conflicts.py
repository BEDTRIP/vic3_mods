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
    a_root: Path,
    b_root: Path,
    a_name: str,
    b_name: str,
    a_common: dict[str, dict[str, list[str]]],
    b_common: dict[str, dict[str, list[str]]],
    a_loc: dict[str, list[str]],
    b_loc: dict[str, list[str]],
    a_events: dict[str, list[str]],
    b_events: dict[str, list[str]],
) -> None:
    lines: list[str] = []
    lines.append(f"# {a_name} vs {b_name} — conflict report (key-level heuristic)")
    lines.append("")
    lines.append(f"- {a_name} root: `{a_root.as_posix()}`")
    lines.append(f"- {b_name} root: `{b_root.as_posix()}`")
    lines.append("")
    lines.append(
        "This report finds **identifier-level duplicates** (same key/id defined by both mods), "
        "even when file paths do not overlap. It is a heuristic and may include a few false positives."
    )
    lines.append("")

    # common duplicates by same category path
    lines.append("## common/*: duplicate top-level keys")
    common_cats = sorted(set(a_common).intersection(b_common))
    total_common_dups = 0
    for cat in common_cats:
        a_keys = set(a_common[cat])
        b_keys = set(b_common[cat])
        dup = sorted(a_keys & b_keys)
        if not dup:
            continue
        total_common_dups += len(dup)
        lines.append("")
        lines.append(f"### {cat} — {len(dup)} duplicates")
        for k in dup[:250]:
            lines.append(f"- `{k}`")
            for f in sorted(set(a_common[cat][k]))[:5]:
                lines.append(f"  - {a_name}: `{f}`")
            for f in sorted(set(b_common[cat][k]))[:5]:
                lines.append(f"  - {b_name}: `{f}`")
        if len(dup) > 250:
            lines.append(f"- ... and {len(dup) - 250} more")
    if total_common_dups == 0:
        lines.append("")
        lines.append("- (no duplicates detected by this heuristic)")

    lines.append("")
    lines.append("## localization: duplicate localization keys")
    loc_dup = sorted(set(a_loc) & set(b_loc))
    lines.append(f"- Total duplicate localization keys: **{len(loc_dup)}**")
    for k in loc_dup[:250]:
        lines.append(f"  - `{k}`")
        for f in sorted(set(a_loc[k]))[:3]:
            lines.append(f"    - {a_name}: `{f}`")
        for f in sorted(set(b_loc[k]))[:3]:
            lines.append(f"    - {b_name}: `{f}`")
    if len(loc_dup) > 250:
        lines.append(f"  - ... and {len(loc_dup) - 250} more")

    lines.append("")
    lines.append("## events: duplicate event ids (`id = ...` anywhere in events/*.txt)")
    ev_dup = sorted(set(a_events) & set(b_events))
    lines.append(f"- Total duplicate event ids: **{len(ev_dup)}**")
    for eid in ev_dup[:250]:
        lines.append(f"  - `{eid}`")
        for f in sorted(set(a_events[eid]))[:3]:
            lines.append(f"    - {a_name}: `{f}`")
        for f in sorted(set(b_events[eid]))[:3]:
            lines.append(f"    - {b_name}: `{f}`")
    if len(ev_dup) > 250:
        lines.append(f"  - ... and {len(ev_dup) - 250} more")

    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare two Vic3 mods and report identifier-level duplicates (common keys, localization keys, event ids). "
            "Heuristic, may include false positives. "
            "Back-compat: --ef/--vc defaults still supported."
        )
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="Workspace root (defaults to current dir).",
    )
    parser.add_argument("--a", type=Path, default=None, help="Path to mod A root (generic mode).")
    parser.add_argument("--b", type=Path, default=None, help="Path to mod B root (generic mode).")
    parser.add_argument("--a-name", type=str, default=None, help="Display name for mod A.")
    parser.add_argument("--b-name", type=str, default=None, help="Display name for mod B.")
    parser.add_argument(
        "--ef",
        type=Path,
        default=None,
        help="Path to E&F mod root (folder containing common/, localization/, etc.).",
    )
    parser.add_argument(
        "--vc",
        type=Path,
        default=None,
        help="Path to Victorian Century mod root.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output markdown report path.",
    )
    args = parser.parse_args()

    ws = args.workspace.resolve()
    # Generic mode (preferred): --a/--b
    if args.a is not None or args.b is not None:
        if args.a is None or args.b is None:
            raise SystemExit("Provide both --a and --b (or use legacy --ef/--vc mode).")
        a_root = args.a.resolve()
        b_root = args.b.resolve()
        a_name = args.a_name or a_root.name
        b_name = args.b_name or b_root.name
        out_path = (args.out or (ws / f"conflicts_{a_name}_vs_{b_name}_report.md")).resolve()
    else:
        # Legacy mode: keep prior defaults for E&F vs VC
        a_root = (args.ef or (ws / "E&F" / "e&f")).resolve()
        b_root = (args.vc or (ws / "Victorian Century")).resolve()
        a_name = args.a_name or "E&F"
        b_name = args.b_name or "VC"
        out_path = (args.out or (ws / "conflicts_ef_vs_vc_report.md")).resolve()

    if not a_root.exists():
        raise SystemExit(f"Mod A root not found: {a_root}")
    if not b_root.exists():
        raise SystemExit(f"Mod B root not found: {b_root}")

    print(f"Collecting {a_name} common keys...")
    a_common = collect_common_keys(a_root)
    print(f"Collecting {b_name} common keys...")
    b_common = collect_common_keys(b_root)
    print("Collecting localization keys...")
    a_loc = collect_localization_keys(a_root)
    b_loc = collect_localization_keys(b_root)
    print("Collecting event ids...")
    a_events = collect_event_ids(a_root)
    b_events = collect_event_ids(b_root)

    _write_report(
        out_path,
        a_root=a_root,
        b_root=b_root,
        a_name=a_name,
        b_name=b_name,
        a_common=a_common,
        b_common=b_common,
        a_loc=a_loc,
        b_loc=b_loc,
        a_events=a_events,
        b_events=b_events,
    )

    common_cats = set(a_common).intersection(b_common)
    common_dup_count = 0
    for cat in common_cats:
        common_dup_count += len(set(a_common[cat]).intersection(b_common[cat]))
    loc_dup_count = len(set(a_loc).intersection(b_loc))
    ev_dup_count = len(set(a_events).intersection(b_events))

    print("Wrote report:", out_path)
    print("Summary:",
          "common_categories_intersection=", len(common_cats),
          "common_key_dups=", common_dup_count,
          "loc_key_dups=", loc_dup_count,
          "event_id_dups=", ev_dup_count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

