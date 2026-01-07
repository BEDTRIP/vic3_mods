from __future__ import annotations

import argparse
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import DefaultDict, Iterable


KEY_AT_TOPLEVEL_RE = re.compile(r"^\s*([A-Za-z0-9_.\-:]+)\s*=")
KEY_AT_TOPLEVEL_BLOCK_RE = re.compile(r"^\s*([A-Za-z0-9_.\-:]+)\s*=\s*\{")
NAMESPACE_RE = re.compile(r"^\s*namespace\s*=\s*([A-Za-z0-9_.\-]+)\s*$")

# Reduce obvious false positives when parsing top-level keys.
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


def _read_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()
    except Exception:
        return path.read_text(errors="ignore").splitlines()


def iter_top_level_keys_txt(path: Path) -> list[str]:
    """
    Extract keys that look like 'foo = ...' only at brace depth 0.
    This is a heuristic parser intended for Vic3-style script files.
    """
    keys: list[str] = []
    depth = 0

    for raw in _read_lines(path):
        line = _strip_line_comment(raw)

        if depth == 0:
            m = KEY_AT_TOPLEVEL_RE.match(line)
            if m:
                token = m.group(1)
                # Normalize Vic3 script patch prefixes like REPLACE:foo, INJECT:bar, REPLACE_OR_CREATE:baz, etc.
                if ":" in token:
                    prefix, rest = token.split(":", 1)
                    if prefix.isupper():
                        token = rest
                if token and token not in NON_DEFINITION_KEYS and not token.startswith("@"):
                    keys.append(token)

        depth += line.count("{")
        depth -= line.count("}")
        if depth < 0:
            depth = 0

    return keys


def iter_top_level_block_keys_txt(path: Path) -> list[str]:
    """
    Extract keys that look like 'foo = { ... }' only at brace depth 0.
    Useful for events definition keys like 'victoria.1 = { ... }'.
    """
    keys: list[str] = []
    depth = 0
    for raw in _read_lines(path):
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


def collect_event_namespaces(path: Path) -> set[str]:
    out: set[str] = set()
    for raw in _read_lines(path):
        line = _strip_line_comment(raw).strip()
        if not line:
            continue
        m = NAMESPACE_RE.match(line)
        if m:
            out.add(m.group(1))
    return out


def iter_files(root: Path, *, exts: Iterable[str]) -> Iterable[Path]:
    exts_l = {e.lower() for e in exts}
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts_l:
            yield p


def rel_to_game_root(mod_root: Path, file_path: Path) -> str:
    return file_path.relative_to(mod_root).as_posix()


@dataclass(frozen=True)
class CatStats:
    mod_files: int
    vanilla_path_overrides: int
    vanilla_path_new: int
    mod_keys: int
    new_keys_vs_vanilla: int
    shared_keys_vs_vanilla: int


def _collect_vanilla_keys_for_cat(vanilla_game_root: Path, cat: str) -> set[str]:
    d = vanilla_game_root / cat
    if not d.exists():
        return set()
    out: set[str] = set()
    for p in d.rglob("*.txt"):
        for k in iter_top_level_keys_txt(p):
            out.add(k)
    return out


def _category_of(rel_path: str) -> str:
    # rel_path like "common/laws/00_bpm_laws.txt"
    parts = rel_path.split("/")
    if len(parts) <= 2:
        return "/".join(parts[:-1])
    return "/".join(parts[:-1])


def build_common_stats(mod_root: Path, vanilla_game_root: Path) -> tuple[dict[str, CatStats], dict[str, dict[str, list[str]]]]:
    """
    Returns:
      stats_by_cat: category -> CatStats
      keys_by_cat: category -> key -> [mod rel file paths...]
    """
    common_dir = mod_root / "common"
    if not common_dir.exists():
        return {}, {}

    mod_files_by_cat: DefaultDict[str, list[Path]] = defaultdict(list)
    mod_keys_by_cat: dict[str, DefaultDict[str, list[str]]] = {}

    for p in common_dir.rglob("*.txt"):
        rel = rel_to_game_root(mod_root, p)
        cat = _category_of(rel)
        mod_files_by_cat[cat].append(p)
        ks = iter_top_level_keys_txt(p)
        if ks:
            m = mod_keys_by_cat.setdefault(cat, defaultdict(list))
            for k in ks:
                m[k].append(rel)

    # collect vanilla keys only for categories used by the mod
    vanilla_keys_by_cat: dict[str, set[str]] = {}
    for cat in mod_files_by_cat:
        vanilla_keys_by_cat[cat] = _collect_vanilla_keys_for_cat(vanilla_game_root, cat)

    stats: dict[str, CatStats] = {}
    for cat, files in mod_files_by_cat.items():
        overrides = 0
        new_paths = 0
        for p in files:
            rel = rel_to_game_root(mod_root, p)
            if (vanilla_game_root / rel).exists():
                overrides += 1
            else:
                new_paths += 1

        mod_key_map = mod_keys_by_cat.get(cat, {})
        mod_keys = set(mod_key_map.keys())
        vanilla_keys = vanilla_keys_by_cat.get(cat, set())
        shared = len(mod_keys & vanilla_keys)
        new_k = len(mod_keys - vanilla_keys)

        stats[cat] = CatStats(
            mod_files=len(files),
            vanilla_path_overrides=overrides,
            vanilla_path_new=new_paths,
            mod_keys=len(mod_keys),
            new_keys_vs_vanilla=new_k,
            shared_keys_vs_vanilla=shared,
        )

    # freeze to plain dict
    keys_by_cat: dict[str, dict[str, list[str]]] = {
        cat: dict(kmap) for cat, kmap in mod_keys_by_cat.items()
    }
    return stats, keys_by_cat


def build_path_stats(mod_root: Path, vanilla_game_root: Path, top: str, exts: Iterable[str]) -> tuple[int, int, int]:
    """
    Returns: (mod_files_count, overrides_count, new_count) for files under mod_root/top
    compared by relative path existence under vanilla_game_root.
    """
    d = mod_root / top
    if not d.exists():
        return 0, 0, 0
    total = 0
    overrides = 0
    for p in iter_files(d, exts=exts):
        total += 1
        rel = rel_to_game_root(mod_root, p)
        if (vanilla_game_root / rel).exists():
            overrides += 1
    return total, overrides, total - overrides


def build_events_stats(mod_root: Path, vanilla_game_root: Path) -> dict[str, object]:
    ev_dir = mod_root / "events"
    if not ev_dir.exists():
        return {
            "files": 0,
            "vanilla_path_overrides": 0,
            "vanilla_path_new": 0,
            "event_def_keys": 0,
            "shared_event_def_keys_vs_vanilla": 0,
            "new_event_def_keys_vs_vanilla": 0,
            "namespaces": [],
        }

    # file-level stats
    files_total, overrides, new_files = build_path_stats(mod_root, vanilla_game_root, "events", exts={".txt"})

    # event definition keys
    mod_defs: set[str] = set()
    mod_namespaces: set[str] = set()
    for p in ev_dir.rglob("*.txt"):
        mod_defs.update(iter_top_level_block_keys_txt(p))
        mod_namespaces |= collect_event_namespaces(p)

    van_dir = vanilla_game_root / "events"
    vanilla_defs: set[str] = set()
    if van_dir.exists():
        for p in van_dir.rglob("*.txt"):
            vanilla_defs.update(iter_top_level_block_keys_txt(p))

    return {
        "files": files_total,
        "vanilla_path_overrides": overrides,
        "vanilla_path_new": new_files,
        "event_def_keys": len(mod_defs),
        "shared_event_def_keys_vs_vanilla": len(mod_defs & vanilla_defs),
        "new_event_def_keys_vs_vanilla": len(mod_defs - vanilla_defs),
        "namespaces": sorted(mod_namespaces),
    }


def write_markdown_report(
    out_path: Path,
    *,
    mod_root: Path,
    vanilla_game_root: Path,
    common_stats: dict[str, CatStats],
    events_stats: dict[str, object],
    other_path_stats: dict[str, tuple[int, int, int]],
) -> None:
    lines: list[str] = []
    lines.append(f"# {mod_root.name} vs vanilla — file/key summary (heuristic)")
    lines.append("")
    lines.append(f"- Mod root: `{mod_root.as_posix()}`")
    lines.append(f"- Vanilla game root: `{vanilla_game_root.as_posix()}`")
    lines.append("")
    lines.append("## common/* overview")
    lines.append("")
    lines.append(
        "| category | mod files | overrides (same path) | new (no vanilla path) | mod keys | new keys | shared keys |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for cat in sorted(common_stats):
        s = common_stats[cat]
        lines.append(
            f"| `{cat}` | {s.mod_files} | {s.vanilla_path_overrides} | {s.vanilla_path_new} | {s.mod_keys} | {s.new_keys_vs_vanilla} | {s.shared_keys_vs_vanilla} |"
        )

    lines.append("")
    lines.append("## events overview")
    lines.append("")
    lines.append(
        f"- Files: **{events_stats['files']}** (overrides by path: **{events_stats['vanilla_path_overrides']}**, new: **{events_stats['vanilla_path_new']}**)"
    )
    lines.append(
        f"- Event definition keys (`X = {{ ... }}`): **{events_stats['event_def_keys']}** (new vs vanilla: **{events_stats['new_event_def_keys_vs_vanilla']}**, shared: **{events_stats['shared_event_def_keys_vs_vanilla']}**)"
    )
    ns = events_stats.get("namespaces") or []
    lines.append(f"- Namespaces: {', '.join(f'`{n}`' for n in ns) if ns else '(none detected)'}")

    lines.append("")
    lines.append("## other top-level folders (file-level path overrides)")
    lines.append("")
    lines.append("| folder | mod files | overrides (same path) | new |")
    lines.append("|---|---:|---:|---:|")
    for top in sorted(other_path_stats):
        total, ov, newf = other_path_stats[top]
        lines.append(f"| `{top}` | {total} | {ov} | {newf} |")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize a Vic3 mod vs vanilla by paths + heuristic keys.")
    parser.add_argument("--mod", type=Path, required=True, help="Path to mod root (contains common/, events/, etc.)")
    parser.add_argument(
        "--vanilla-game",
        type=Path,
        required=True,
        help="Path to vanilla 'game' folder root (contains common/, events/, gui/, localization/, etc.)",
    )
    parser.add_argument("--out", type=Path, required=True, help="Output markdown report path")
    args = parser.parse_args()

    mod_root = args.mod.resolve()
    vanilla_game_root = args.vanilla_game.resolve()
    out_path = args.out.resolve()

    if not mod_root.exists():
        raise SystemExit(f"Mod root not found: {mod_root}")
    if not vanilla_game_root.exists():
        raise SystemExit(f"Vanilla game root not found: {vanilla_game_root}")

    common_stats, _keys_by_cat = build_common_stats(mod_root, vanilla_game_root)
    events_stats = build_events_stats(mod_root, vanilla_game_root)

    other_path_stats: dict[str, tuple[int, int, int]] = {}
    for top, exts in [
        ("gui", {".gui", ".txt"}),
        ("localization", {".yml", ".yaml"}),
        ("gfx", {".dds", ".png", ".jpg", ".tga", ".asset", ".mesh", ".bk2", ".txt"}),
        ("dlc_metadata", {".txt"}),
        ("dlc", {".dlc", ".json", ".dds", ".png", ".txt"}),
        ("map_data", {".txt", ".png", ".csv"}),
    ]:
        other_path_stats[top] = build_path_stats(mod_root, vanilla_game_root, top, exts=exts)

    write_markdown_report(
        out_path,
        mod_root=mod_root,
        vanilla_game_root=vanilla_game_root,
        common_stats=common_stats,
        events_stats=events_stats,
        other_path_stats=other_path_stats,
    )

    print("Wrote:", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

