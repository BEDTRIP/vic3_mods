"""
pair_matrix.py -- block-level compatibility matrix for a Victoria 3 mod set.

Why this exists: scan_conflicts.py compares two mods. Once the set grew to nine
blocks (36 pairs) doing that by hand stopped scaling, and half the "conflicts" it
reported were additive categories that are never conflicts. This walks every pair
once, filters the additive noise, and prints a matrix plus per-pair detail.

Load-order model (verified in game 2026-08-24, see the rules file):
    mod order wins; inside one mod, byte order of the file name.
So a key defined bare by a later mod eats everything earlier, whatever the file
is called. This script does NOT resolve who wins -- it finds the pairs worth
looking at. Use vfs_order.py on a single key to see the actual chain.

Usage:
    python3 pair_matrix.py --blocks blocks.json [--pair "A,B"] [--rebuild]

blocks.json:
    {"cache": "/abs/path/for/index/cache",
     "blocks": {"BlockName": ["/abs/path/mod1", "/abs/path/mod2"], ...},
     "order":  ["BlockName", ...]}          # optional, for matrix column order

Indexes are cached as JSON per mod path; --rebuild forces a re-scan. Indexing a
big mod over the device mount takes 10-40 s, so the cache matters: device_bash
has a 45 s timeout and a full nine-block run will not fit in one call otherwise.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from collections import defaultdict

KEY_RE = re.compile(r"^\s*([A-Za-z0-9_.\-:]+)\s*=")
LOC_RE = re.compile(r'^\s*([^\s:#][^:#]*?)\s*:\s*[0-9]*\s*"')
EVT_RE = re.compile(r"\bid\s*=\s*([A-Za-z0-9_.\-]+)")
GUI_TYPE_RE = re.compile(r"^\s*type\s+([A-Za-z0-9_.:-]+)\s*=")
SCRIPT_EXT = {".txt", ".yml", ".gui"}

# Keys inside these categories are lists the engine concatenates, or plain data
# with no winner. A shared key here is not a conflict and must not be reported
# as one -- on_actions alone would otherwise flag seven mods against each other.
ADDITIVE_CATEGORIES = {
    "common",
    "common/on_actions",
    "common/named_colors",
    "common/modifier_type_definitions",  # decimals/color/percent are display only
    "events",
    "music/main_themes",
    "tools/scripted_tests",
    "gfx/map/map_object_data",
}
ADDITIVE_PREFIXES = ("common/history/",)

# Container keys, not definitions.
NOISE_KEYS = {
    "namespace", "group", "object", "game_object_locator", "colors", "tests",
    "last_date", "BUILDINGS", "GLOBAL", "POPS", "STATES", "COUNTRIES",
    "CHARACTERS", "DIPLOMACY", "DIPLOMATIC_PLAYS", "MILITARY_DEPLOYMENTS",
    "MILITARY_FORMATIONS", "GOVERNMENTS", "TRADE_ROUTES", "LOBBIES", "TREATIES",
    "POLITICAL_MOVEMENTS", "POWER_BLOCS", "SPLINE_NETWORK", "POPULATION",
}
NON_DEFINITION = {
    "if", "else", "else_if", "elseif", "while", "limit", "modifier", "add",
    "remove", "set", "trigger", "effect", "value", "desc", "picture", "option",
}


def is_additive(category: str) -> bool:
    return category in ADDITIVE_CATEGORIES or category.startswith(ADDITIVE_PREFIXES)


def index_mod(root: str) -> dict:
    """One pass over a mod: file paths, top-level keys per category, loc keys,
    event ids, gui type names."""
    root = os.path.abspath(root)
    files: list[str] = []
    keys: dict[str, list[str]] = {}
    loc: dict[str, list[str]] = {}
    events: dict[str, list[str]] = {}
    gui: dict[str, list[str]] = {}

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in filenames:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root).replace("\\", "/")
            files.append(rel)
            if os.path.splitext(name)[1].lower() not in SCRIPT_EXT:
                continue
            try:
                text = open(full, encoding="utf-8-sig", errors="ignore").read()
            except OSError:
                continue
            text = text.replace("\r\n", "\n")

            if rel.startswith("localization/"):
                for line in text.split("\n"):
                    m = LOC_RE.match(line)
                    if m:
                        k = m.group(1).strip()
                        if not k.startswith("l_"):
                            loc.setdefault(k, []).append(rel)
                continue

            if rel.startswith("gui/"):
                for line in text.split("\n"):
                    m = GUI_TYPE_RE.match(line.split("#", 1)[0])
                    if m:
                        gui.setdefault(m.group(1), []).append(rel)
                continue

            if rel.startswith("events/"):
                for m in EVT_RE.finditer(text):
                    events.setdefault(m.group(1), []).append(rel)

            depth = 0
            category = os.path.dirname(rel)
            for raw in text.split("\n"):
                line = raw.split("#", 1)[0]
                if depth == 0:
                    m = KEY_RE.match(line)
                    if m:
                        token = m.group(1)
                        if ":" in token:
                            prefix, rest = token.split(":", 1)
                            if prefix.isupper():
                                token = rest
                        if token not in NON_DEFINITION:
                            keys.setdefault(category + "|" + token, []).append(rel)
                depth += line.count("{") - line.count("}")

    return {"root": root, "files": files, "keys": keys, "loc": loc,
            "events": events, "gui": gui}


def cached_index(path: str, cache_dir: str, rebuild: bool) -> dict:
    os.makedirs(cache_dir, exist_ok=True)
    tag = hashlib.md5(os.path.abspath(path).encode()).hexdigest()[:12]
    out = os.path.join(cache_dir, f"{os.path.basename(path.rstrip('/'))}.{tag}.json")
    if os.path.isfile(out) and not rebuild:
        return json.load(open(out, encoding="utf-8"))
    data = index_mod(path)
    tmp = out + ".tmp"                      # never write in place: a bad open()
    with open(tmp, "w", encoding="utf-8") as fh:   # truncates before it validates
        json.dump(data, fh)
    os.replace(tmp, out)
    return data


def block_keys(mods: dict[str, dict]) -> dict[str, list[str]]:
    merged: dict[str, list[str]] = {}
    for name, data in mods.items():
        for k in data["keys"]:
            category, key = k.split("|", 1)
            if is_additive(category) or key in NOISE_KEYS:
                continue
            merged.setdefault(k, []).append(name)
    return merged


def block_files(mods: dict[str, dict]) -> dict[str, list[str]]:
    merged: dict[str, list[str]] = {}
    for name, data in mods.items():
        for f in data["files"]:
            if os.path.splitext(f)[1].lower() in SCRIPT_EXT:
                merged.setdefault(f, []).append(name)
    return merged


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--blocks", required=True, help="path to blocks.json")
    ap.add_argument("--pair", default=None, help='detail for one pair: "A,B"')
    ap.add_argument("--rebuild", action="store_true", help="ignore the index cache")
    ap.add_argument("--limit", type=int, default=25, help="keys printed per category")
    args = ap.parse_args()

    cfg = json.load(open(args.blocks, encoding="utf-8-sig"))
    # Paths in blocks.json are relative TO blocks.json, because the mount point
    # under device_bash is session-specific and cannot be hardcoded.
    base = os.path.dirname(os.path.abspath(args.blocks))
    resolve = lambda p: p if os.path.isabs(p) else os.path.normpath(os.path.join(base, p))
    cache_dir = resolve(cfg.get("cache") or "_idx")
    blocks = cfg["blocks"]
    order = cfg.get("order") or [b for b in blocks if not b.startswith("_")]

    indexed: dict[str, dict[str, dict]] = {}
    for block in order:
        indexed[block] = {}
        for path in blocks[block]:
            path = resolve(path)
            label = os.path.basename(path.rstrip("/"))
            indexed[block][label] = cached_index(path, cache_dir, args.rebuild)

    K = {b: block_keys(indexed[b]) for b in order}
    F = {b: block_files(indexed[b]) for b in order}
    E = {b: set().union(*[set(d["events"]) for d in indexed[b].values()]) if indexed[b] else set() for b in order}

    if args.pair:
        a, b = [x.strip() for x in args.pair.split(",", 1)]
        detail(a, b, K, F, E, args.limit)
        return 0

    width = max(len(b) for b in order) + 1
    print("матрица: число не-аддитивных общих ключей / общих путей файлов")
    print(" " * width + "| " + " ".join(f"{b[:11]:>12}" for b in order))
    for a in order:
        row = []
        for b in order:
            if a == b:
                row.append(f"{'-':>12}")
                continue
            nk = len(set(K[a]) & set(K[b]))
            nf = len(set(F[a]) & set(F[b]))
            row.append(f"{str(nk) + '/' + str(nf):>12}")
        print(f"{a:<{width}}| " + " ".join(row))
    print()
    print("детали по паре:  --pair \"A,B\"")
    return 0


def detail(a: str, b: str, K, F, E, limit: int) -> None:
    ko = sorted(set(K[a]) & set(K[b]))
    fo = sorted(set(F[a]) & set(F[b]))
    eo = sorted(E[a] & E[b])
    print("=" * 72)
    print(f"{a}  x  {b}   ключей: {len(ko)}   общих путей: {len(fo)}   общих id событий: {len(eo)}")
    if not ko and not fo and not eo:
        print("  пусто -> кандидат в noneed. Проверить руками то, что скрипт не ловит:")
        print("  товары против 128, группы законов, .gui, наследование building_group,")
        print("  и не держится ли отсутствие конфликта на порядке загрузки.")
        return
    for f in fo:
        print(f"   FILE {f}   [{','.join(F[a][f])}] vs [{','.join(F[b][f])}]")
    if eo:
        print(f"   EVENT IDS {eo[:20]}")
    by_cat = defaultdict(list)
    for k in ko:
        category, key = k.split("|", 1)
        by_cat[category].append((key, K[a][k], K[b][k]))
    for category in sorted(by_cat):
        items = by_cat[category]
        print(f"   {category}: {len(items)}")
        for key, am, bm in items[:limit]:
            print(f"        {key:52} [{','.join(am)}] vs [{','.join(bm)}]")
        if len(items) > limit:
            print(f"        ... +{len(items) - limit}")


if __name__ == "__main__":
    raise SystemExit(main())
