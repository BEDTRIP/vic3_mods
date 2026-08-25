"""
vfs_order.py -- who actually wins a key, and in what order.

Prints every definition of a key across the whole set, in load order, with the
prefix (INJECT / TRY_INJECT / REPLACE / TRY_REPLACE / REPLACE_OR_CREATE / bare),
the body length and the names of the top-level sub-blocks the definition names.

Load-order model (verified in game 2026-08-24): mod order wins; inside one mod,
byte order of the file name. Vanilla counts as the first "mod". A bare full body
in a later mod eats every INJECT that came before it, silently.

Usage:
    python3 vfs_order.py --blocks blocks.json common/buildings building_railway
    python3 vfs_order.py --blocks blocks.json common/cultures han hakka manchu

The block order in blocks.json IS the load order used here, with vanilla and the
frameworks pulled in front. Keep blocks.json ordered the way the game is.
"""

from __future__ import annotations

import argparse
import json
import os
import re

KEY_RE = re.compile(r"^\s*([A-Za-z0-9_.\-:]+)\s*=")


def load_order(cfg_path: str) -> list[tuple[str, str]]:
    cfg = json.load(open(cfg_path, encoding="utf-8-sig"))
    base = os.path.dirname(os.path.abspath(cfg_path))
    resolve = lambda p: p if os.path.isabs(p) else os.path.normpath(os.path.join(base, p))
    out: list[tuple[str, str]] = []
    # "load_order" is the real thing: an explicit list of mod paths in the order
    # the launcher loads them. "order"/"blocks" is only the matrix layout, and
    # using it here gives the wrong winner (Grey's is a column head but loads last).
    if cfg.get("load_order"):
        for p in cfg["load_order"]:
            out.append((os.path.basename(p.rstrip("/")), resolve(p)))
        return out
    for special in ("_vanilla", "_frameworks_не_блоки"):
        for p in cfg["blocks"].get(special, []):
            out.append((os.path.basename(p.rstrip("/")), resolve(p)))
    for block in cfg.get("order") or [b for b in cfg["blocks"] if not b.startswith("_")]:
        for p in cfg["blocks"][block]:
            out.append((os.path.basename(p.rstrip("/")), resolve(p)))
    return out


def parse(path: str):
    """Yield (key, prefix, [sub-block names], body_line_count) for top-level keys."""
    lines = open(path, encoding="utf-8-sig", errors="ignore").read().replace("\r\n", "\n").split("\n")
    depth = 0
    for i, raw in enumerate(lines):
        line = raw.split("#", 1)[0]
        if depth == 0:
            m = KEY_RE.match(line)
            if m:
                token, prefix = m.group(1), ""
                if ":" in token:
                    head, rest = token.split(":", 1)
                    if head.isupper():
                        prefix, token = head, rest
                d, started, j, subs = 0, False, i, []
                while j < len(lines):
                    inner = lines[j].split("#", 1)[0]
                    if d == 1:
                        m2 = KEY_RE.match(inner)
                        if m2:
                            subs.append(m2.group(1))
                    d += inner.count("{") - inner.count("}")
                    if "{" in inner:
                        started = True
                    if started and d <= 0:
                        break
                    j += 1
                yield token, prefix, subs, j - i + 1
        depth += line.count("{") - line.count("}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--blocks", default="blocks.json")
    ap.add_argument("category", help="e.g. common/buildings")
    ap.add_argument("keys", nargs="+")
    ap.add_argument("--subs", type=int, default=14, help="sub-block names to print")
    args = ap.parse_args()

    wanted = set(args.keys)
    found: dict[str, list] = {k: [] for k in args.keys}

    for mod, root in load_order(args.blocks):
        directory = os.path.join(root, args.category)
        if not os.path.isdir(directory):
            continue
        # inside one mod: byte order of the relative path
        entries = []
        for dirpath, _dirnames, filenames in os.walk(directory):
            for name in filenames:
                if name.endswith(".txt"):
                    full = os.path.join(dirpath, name)
                    entries.append((os.path.relpath(full, directory).replace("\\", "/"), full))
        for rel, full in sorted(entries, key=lambda kv: kv[0].encode()):
            for key, prefix, subs, length in parse(full):
                if key in wanted:
                    found[key].append((mod, rel, prefix, subs, length))

    for key in args.keys:
        print("=" * 74)
        print(f"{args.category}/{key}   (в порядке загрузки; последний обычно и побеждает)")
        if not found[key]:
            print("   не определён ни в одном моде набора")
            continue
        for mod, rel, prefix, subs, length in found[key]:
            label = prefix or "(bare)"
            print(f"  {mod:22} {label:18} {length:5}L  {rel}")
            print(f"      sub={subs[:args.subs]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
