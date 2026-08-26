"""
scan_prestige_goods.py -- census of prestige-good declarations per base good,
across the target load-order chain, for VC.7 in `План проекта.md`.

Max 3 prestige goods per base good become real slots (number in the exe, no
define -- see rules section on Компании/здания/товары). This walks
common/prestige_goods/*.txt for every mod that has one, in target chain
order (vanilla -> E&F+hotfix -> Morgenrote -> VC -> HC -> MoH -> LLWA;
TGR/PSC/KAI/PBE/GoB have no such folder, verified by directory listing),
and reports which declaration is 1st/2nd/3rd (real) vs 4th+ (dead, never
used -- confirmed empirically, not just by rule-of-thumb: see the header of
_ef/ef hotfix 1.13/common/prestige_goods/zz_ef_cm_prestige_currencies.txt,
which documents three separate in-game tests of this exact cap).

Detects prestige-good records by structure (any top-level record in one of
these files with a `base_good = X` field inside), not by naming convention
-- E&F names its own records with no prefix at all (manufacture_stock_gbr,
railroad_stock_usa...), MoH uses `prestige_` instead of `prestige_good_`.
Skips fully-commented records (E&F comments out manufacture_stock_usa in its
main file, then redeclares it active in a second file -- both are handled
correctly: the commented one is invisible, the active one counts).

Usage:
    python3 scan_prestige_goods.py
"""

import re, os

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../vic3_mods_out"))

# (mod display name, path relative to ROOT) in target chain order.
# TGR/PSC/KAI/PBE/GoB have no common/prestige_goods -- omitted (verified by directory listing).
CHAIN = [
    ("ваниль", [".vanillaVIC3/common/prestige_goods/00_prestige_goods.txt"]),
    ("E&F+hotfix", sorted([
        "E&F/common/prestige_goods/00_ef_prestige_goods.txt",
        "E&F/common/prestige_goods/00_ef_prestige_goods_2.txt",
    ])),
    ("Morgenrote", ["Morgenrote/common/prestige_goods/mr_prestige_goods.txt"]),
    ("VC", ["VC/common/prestige_goods/joi_prestige_goods.txt"]),
    ("HC", ["for addon/hailcolumbia/common/prestige_goods/usfp_prestige_goods.txt"]),
    ("MoH", ["for addon/mandateofheaven/common/prestige_goods/moh_prestige_goods.txt"]),
    ("LLWA", ["llwa/common/prestige_goods/LLWA_prestige_goods.txt"]),
]

rec_pat = re.compile(r"^(?:[A-Z_]+:)?([A-Za-z0-9_]+)\s*=\s*\{")
base_pat = re.compile(r"^\s*base_good\s*=\s*([A-Za-z0-9_]+)")

def parse(path):
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8-sig", errors="replace") as fh:
        lines = fh.readlines()
    out = []
    i = 0
    while i < len(lines):
        code0 = lines[i].split("#", 1)[0]
        m = rec_pat.match(code0.lstrip(chr(0xfeff)))
        if m:
            name = m.group(1)
            depth = code0.count("{") - code0.count("}")
            j = i + 1
            base = None
            while j < len(lines) and depth > 0:
                code = lines[j].split("#", 1)[0]
                bm = base_pat.match(code)
                if bm:
                    base = bm.group(1)
                depth += code.count("{") - code.count("}")
                j += 1
            if base is not None:
                out.append((name, base))
            i = max(j, i + 1)
        else:
            i += 1
    return out

by_base = {}  # base_good -> list of (order_index, mod, prestige_good_name)
order_index = 0
for mod, paths in CHAIN:
    for rel in paths:
        full = os.path.join(ROOT, rel)
        entries = parse(full)
        for name, base in entries:
            order_index += 1
            by_base.setdefault(base, []).append((order_index, mod, name, rel))

TARGETS = ["small_arms", "engines", "artillery", "automobiles", "groceries",
           "fine_art", "liquor", "grain", "manufacture_stock", "railroad_stock"]

print(f"{'base_good':22} {'count':5}  declarations in load order (winner marked *)")
print("=" * 100)
for base in TARGETS:
    entries = by_base.get(base, [])
    print(f"\n{base}  ({len(entries)} declarations)")
    for rank, (idx, mod, name, rel) in enumerate(entries, start=1):
        mark = "*WIN*" if rank <= 3 else "dead "
        print(f"  {rank:2}. [{mark}] {mod:12} {name}")

print("\n\n--- full base_good census (all goods with count != 3, sanity check against vanilla's own 17x1/14x2/9x3) ---""")
for base, entries in sorted(by_base.items()):
    if len(entries) != 3:
        print(f"  {base:22} {len(entries)}")
