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
    ef_root: Path,
    vc_root: Path,
    ef_common: dict[str, dict[str, list[str]]],
    vc_common: dict[str, dict[str, list[str]]],
    ef_loc: dict[str, list[str]],
    vc_loc: dict[str, list[str]],
    ef_events: dict[str, list[str]],
    vc_events: dict[str, list[str]],
) -> None:
    lines: list[str] = []
    lines.append("# E&F vs Victorian Century — conflict report (key-level heuristic)")
    lines.append("")
    lines.append(f"- E&F root: `{ef_root.as_posix()}`")
    lines.append(f"- VC root: `{vc_root.as_posix()}`")
    lines.append("")
    lines.append(
        "This report finds **identifier-level duplicates** (same key/id defined by both mods), "
        "even when file paths do not overlap. It is a heuristic and may include a few false positives."
    )
    lines.append("")

    # common duplicates by same category path
    lines.append("## common/*: duplicate top-level keys")
    common_cats = sorted(set(ef_common).intersection(vc_common))
    total_common_dups = 0
    for cat in common_cats:
        ef_keys = set(ef_common[cat])
        vc_keys = set(vc_common[cat])
        dup = sorted(ef_keys & vc_keys)
        if not dup:
            continue
        total_common_dups += len(dup)
        lines.append("")
        lines.append(f"### {cat} — {len(dup)} duplicates")
        for k in dup[:250]:
            lines.append(f"- `{k}`")
            for f in sorted(set(ef_common[cat][k]))[:5]:
                lines.append(f"  - E&F: `{f}`")
            for f in sorted(set(vc_common[cat][k]))[:5]:
                lines.append(f"  - VC: `{f}`")
        if len(dup) > 250:
            lines.append(f"- ... and {len(dup) - 250} more")
    if total_common_dups == 0:
        lines.append("")
        lines.append("- (no duplicates detected by this heuristic)")

    lines.append("")
    lines.append("## localization: duplicate localization keys")
    loc_dup = sorted(set(ef_loc) & set(vc_loc))
    lines.append(f"- Total duplicate localization keys: **{len(loc_dup)}**")
    for k in loc_dup[:250]:
        lines.append(f"  - `{k}`")
        for f in sorted(set(ef_loc[k]))[:3]:
            lines.append(f"    - E&F: `{f}`")
        for f in sorted(set(vc_loc[k]))[:3]:
            lines.append(f"    - VC: `{f}`")
    if len(loc_dup) > 250:
        lines.append(f"  - ... and {len(loc_dup) - 250} more")

    lines.append("")
    lines.append("## events: duplicate event ids (`id = ...` anywhere in events/*.txt)")
    ev_dup = sorted(set(ef_events) & set(vc_events))
    lines.append(f"- Total duplicate event ids: **{len(ev_dup)}**")
    for eid in ev_dup[:250]:
        lines.append(f"  - `{eid}`")
        for f in sorted(set(ef_events[eid]))[:3]:
            lines.append(f"    - E&F: `{f}`")
        for f in sorted(set(vc_events[eid]))[:3]:
            lines.append(f"    - VC: `{f}`")
    if len(ev_dup) > 250:
        lines.append(f"  - ... and {len(ev_dup) - 250} more")

    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="Workspace root (defaults to current dir).",
    )
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
    ef_root = (args.ef or (ws / "E&F" / "e&f")).resolve()
    vc_root = (args.vc or (ws / "Victorian Century")).resolve()
    out_path = (args.out or (ws / "conflicts_ef_vs_vc_report.md")).resolve()

    if not ef_root.exists():
        raise SystemExit(f"E&F root not found: {ef_root}")
    if not vc_root.exists():
        raise SystemExit(f"VC root not found: {vc_root}")

    print("Collecting E&F common keys...")
    ef_common = collect_common_keys(ef_root)
    print("Collecting VC common keys...")
    vc_common = collect_common_keys(vc_root)
    print("Collecting localization keys...")
    ef_loc = collect_localization_keys(ef_root)
    vc_loc = collect_localization_keys(vc_root)
    print("Collecting event ids...")
    ef_events = collect_event_ids(ef_root)
    vc_events = collect_event_ids(vc_root)

    _write_report(
        out_path,
        ef_root=ef_root,
        vc_root=vc_root,
        ef_common=ef_common,
        vc_common=vc_common,
        ef_loc=ef_loc,
        vc_loc=vc_loc,
        ef_events=ef_events,
        vc_events=vc_events,
    )

    common_cats = set(ef_common).intersection(vc_common)
    common_dup_count = 0
    for cat in common_cats:
        common_dup_count += len(set(ef_common[cat]).intersection(vc_common[cat]))
    loc_dup_count = len(set(ef_loc).intersection(vc_loc))
    ev_dup_count = len(set(ef_events).intersection(vc_events))

    print("Wrote report:", out_path)
    print("Summary:",
          "common_categories_intersection=", len(common_cats),
          "common_key_dups=", common_dup_count,
          "loc_key_dups=", loc_dup_count,
          "event_id_dups=", ev_dup_count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

