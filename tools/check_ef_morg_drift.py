#!/usr/bin/env python3
"""
Drift check for the E&F + Morgenroete compatch.

Why a checker and not a generator
---------------------------------
The E&F + PSC compatch carries whole-file copies, so tools/regen_ef_psc_copies.py
rebuilds them outright. E&F + Morgenroete is built differently: every file is a
`zz_` key-level patch, and each one is upstream content plus a short, deliberate
list of additions. There is nothing to regenerate -- the additions are judgement
calls. What rots is whether upstream still looks the way the patch assumes.

So this script does not write anything. It re-derives what each patch should
contain from the current mods and reports the difference. Run it after every
E&F or Morgenroete update; exit code 1 means something moved.

Comparison is semantic, not textual: for each patched block it extracts the set
of goods / condition lines rather than diffing formatting. That keeps the check
from screaming every time somebody reindents, and makes the real question --
"did upstream add or remove an entry?" -- the only thing it answers.

Source rule
-----------
Load order is E&F -> E&F hotfix -> Morgenroete -> compatch. Where the hotfix
overrides an E&F file, the hotfix's version is the live one, so that is what the
compatch must be measured against. `pick_source()` looks there first.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- declared additions
# What the compatch intentionally adds on top of upstream. Everything else showing
# up as a difference is drift.

MR_GOODS_CONSUMER = ["air_travel", "elgar_music", "manzoni_prints", "elgar_instruments"]
MR_GOODS_RAW = ["good_uranium"]

TESLA_ADDITIONS = {
    "tesla_construction_sector_valid_for_improvement_trigger": [
        "is_building_type = building_ef_private_construction",
    ],
    "tesla_building_valid_for_mechanical_improvement_trigger": [
        "is_building_group = bg_bank",
        "is_building_group = bg_financial_centre",
        "is_building_group = bg_national_stockpile",
        "is_building_group = bg_ef_private_construction",
    ],
}

# Morgenroete buildings the compatch deliberately does NOT give liquidity to.
# Empty today: the patch covers all of them. Kept so an intentional exclusion has
# somewhere to live other than a mismatch report.
LIQUIDITY_EXCLUDE: set[str] = set()


# ---------------------------------------------------------------- parsing helpers
KEY_RE = re.compile(r"^\s*([A-Za-z0-9_.\-:]+)\s*=")


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8-sig", errors="ignore")


def top_level_keys(path: Path) -> dict[str, str]:
    """{bare_key: block_text} for every top-level `key = { ... }`, prefixes stripped."""
    out: dict[str, str] = {}
    depth = 0
    cur: str | None = None
    buf: list[str] = []
    for raw in read(path).split("\n"):
        line = raw.split("#", 1)[0]
        if depth == 0:
            m = KEY_RE.match(line)
            if m:
                cur = m.group(1).split(":")[-1]
                buf = []
        if cur is not None:
            buf.append(raw)
        prev = depth
        depth += line.count("{") - line.count("}")
        if cur is not None and depth == 0 and prev > 0:
            out.setdefault(cur, "\n".join(buf))
            cur = None
    return out


def scan(root: Path, sub: str) -> dict[str, tuple[Path, str]]:
    """{bare_key: (file, block)} across one common/ subfolder."""
    out: dict[str, tuple[Path, str]] = {}
    d = root / "common" / sub
    if not d.is_dir():
        return out
    for f in sorted(d.rglob("*.txt")):
        for k, v in top_level_keys(f).items():
            out.setdefault(k, (f, v))
    return out


def building_keys(root: Path) -> tuple[set[str], set[str]]:
    """(defined_here, injected_into) for common/buildings."""
    own: set[str] = set()
    inj: set[str] = set()
    d = root / "common" / "buildings"
    if not d.is_dir():
        return own, inj
    for f in sorted(d.rglob("*.txt")):
        depth = 0
        for raw in read(f).split("\n"):
            line = raw.split("#", 1)[0]
            if depth == 0:
                m = KEY_RE.match(line)
                if m:
                    tok = m.group(1)
                    if ":" in tok:
                        pre, rest = tok.split(":", 1)
                        (inj if pre.isupper() else own).add(rest)
                    else:
                        own.add(tok)
            depth += line.count("{") - line.count("}")
    return own, inj


def split_inflation(block: str) -> tuple[list[str], list[str]]:
    """
    E&F's inflation values name each good twice: once as `mg:X = { ... }` inside the
    weighted `market = { }` sum, and once as `add = market.mg:X.market_goods_buy_orders`
    in the `divide` block that normalises it. The two lists are NOT always identical --
    E&F's inflation_on_raw_material carries `hardwood` in the divisor only -- so they
    are compared separately rather than merged.
    """
    numerator = [m.group(1) for m in re.finditer(r"^\s*mg:([A-Za-z0-9_]+)\s*=", block, re.M)]
    denominator = re.findall(r"add\s*=\s*market\.mg:([A-Za-z0-9_]+)\.market_goods_buy_orders", block)
    return numerator, denominator


def conditions(block: str) -> list[str]:
    """Normalised one-per-line conditions inside a scripted trigger."""
    out = []
    for raw in block.split("\n"):
        line = re.sub(r"\s+", " ", raw.split("#", 1)[0]).strip()
        if not line or line in {"{", "}"} or line.endswith("= {") or line == "}":
            continue
        out.append(line)
    return out


# ---------------------------------------------------------------- checks
class Report:
    def __init__(self) -> None:
        self.problems = 0

    def ok(self, msg: str) -> None:
        print(f"  [ok]   {msg}")

    def bad(self, msg: str) -> None:
        print(f"  [DRIFT] {msg}")
        self.problems += 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    here = Path(__file__).resolve().parent
    repo = here.parent
    out_root = repo.parent / "vic3_mods_out"
    ap.add_argument("--ef", default=str(out_root / "E&F"))
    ap.add_argument("--mr", default=str(out_root / "Morgenrote"))
    ap.add_argument("--vanilla", default=str(out_root / ".vanillaVIC3"))
    ap.add_argument("--hotfix", default=str(repo / "_ef" / "ef hotfix 1.13"))
    ap.add_argument("--compatch", default=str(repo / "_ef" / "ef+morg done"))
    a = ap.parse_args()

    ef, mr, van = Path(a.ef), Path(a.mr), Path(a.vanilla)
    hotfix, cp = Path(a.hotfix), Path(a.compatch)
    for p, label in ((ef, "--ef"), (mr, "--mr"), (van, "--vanilla"), (cp, "--compatch")):
        if not p.is_dir():
            print(f"ERROR: {label} is not a directory: {p}", file=sys.stderr)
            return 2

    def pick_source(rel: str) -> tuple[Path, str]:
        """Hotfix wins over E&F -- it loads later, so its version is the live one."""
        c = hotfix / rel
        if c.is_file():
            return c, "hotfix"
        return ef / rel, "E&F"

    r = Report()

    # ---- 1. liquidity INJECT list vs Morgenroete's own buildings -------------
    print("1. pmg_market_liquidity injected into every Morgenroete building")
    mr_own, _ = building_keys(mr)
    van_own, _ = building_keys(van)
    mr_new = mr_own - van_own
    _, cp_inj = building_keys(cp)
    want = mr_new - LIQUIDITY_EXCLUDE
    missing = sorted(want - cp_inj)
    extra = sorted(cp_inj - mr_own)
    print(f"         Morgenroete has {len(mr_new)} buildings of its own, compatch injects into {len(cp_inj)}")
    if missing:
        r.bad(f"{len(missing)} new Morgenroete building(s) get no liquidity: {missing}")
    if extra:
        r.bad(f"{len(extra)} building(s) the compatch patches no longer exist in Morgenroete: {extra}")
    if not missing and not extra:
        r.ok("list matches exactly")

    # ---- 2. Morgenroete goods covered by the inflation baskets ---------------
    print("2. Morgenroete goods present in E&F's inflation baskets")
    def goods_of(root: Path) -> set[str]:
        s: set[str] = set()
        d = root / "common" / "goods"
        if d.is_dir():
            for f in sorted(d.rglob("*.txt")):
                s |= {k for k in top_level_keys(f)}
        return s
    mr_goods = goods_of(mr) - goods_of(van)
    infl_file = cp / "common/script_values/zz_ef_mr_inflation_patch.txt"
    covered = set(re.findall(r"mg:([A-Za-z0-9_]+)", read(infl_file)))
    uncovered = sorted(g for g in mr_goods if g not in covered)
    print(f"         Morgenroete adds {len(mr_goods)} goods: {sorted(mr_goods)}")
    if uncovered:
        r.bad(f"not in any basket: {uncovered}")
    else:
        r.ok("all covered")

    # ---- 3. inflation values vs E&F ----------------------------------------
    print("3. inflation values still match E&F apart from the declared additions")
    ef_sv = scan(ef, "script_values")
    cp_infl = top_level_keys(infl_file)
    src, origin = pick_source("common/script_values/00_economic_scripted_value.txt")
    print(f"         source: {origin} -- {src.name}")
    for key, extras in (("inflation_on_consumer_goods", MR_GOODS_CONSUMER),
                        ("inflation_on_raw_material", MR_GOODS_RAW)):
        if key not in ef_sv:
            r.bad(f"{key}: gone from E&F entirely")
            continue
        up_num, up_den = split_inflation(ef_sv[key][1])
        my_num, my_den = split_inflation(cp_infl[key])
        for label, up, mine in (("numerator", up_num, my_num), ("divisor", up_den, my_den)):
            want = list(up) + [g for g in extras if g not in up]
            if sorted(mine) == sorted(want):
                r.ok(f"{key} / {label}: {len(up)} upstream + {len(extras)} ours")
            else:
                r.bad(f"{key} / {label}: upstream-only {sorted(set(up)-set(mine))}, "
                      f"ours-only {sorted(set(mine)-set(up)-set(extras))}")

    # ---- 4. Tesla triggers vs Morgenroete -----------------------------------
    print("4. Tesla triggers still match Morgenroete apart from the declared additions")
    mr_tr = scan(mr, "scripted_triggers")
    cp_tr = top_level_keys(cp / "common/scripted_triggers/zz_ef_mr_tesla_triggers_patch.txt")
    for key, extras in TESLA_ADDITIONS.items():
        if key not in mr_tr:
            r.bad(f"{key}: gone from Morgenroete -- the patch now defines an orphan")
            continue
        up = conditions(mr_tr[key][1])
        mine = conditions(cp_tr[key])
        lost = [c for c in up if c not in mine]
        gained = [c for c in mine if c not in up and c not in extras]
        if lost:
            r.bad(f"{key}: upstream conditions dropped by the patch: {lost}")
        if gained:
            r.bad(f"{key}: conditions in the patch that are neither upstream nor declared: {gained}")
        if not lost and not gained:
            r.ok(f"{key}: {len(up)} upstream conditions + {len(extras)} ours")

    # ---- 5. every referenced building still exists --------------------------
    print("5. buildings named by the compatch still exist")
    alive = set()
    for root in (mr, van, ef):
        o, _ = building_keys(root)
        alive |= o
    refs: set[str] = set()
    for f in sorted((cp / "common").rglob("*.txt")):
        txt = read(f)
        refs |= set(re.findall(r"is_building_type\s*=\s*([A-Za-z0-9_]+)", txt))
        refs |= set(re.findall(r"has_building\s*=\s*([A-Za-z0-9_]+)", txt))
    dead = sorted(b for b in refs if b not in alive)
    if dead:
        r.bad(f"referenced but not defined anywhere: {dead}")
    else:
        r.ok(f"all {len(refs)} referenced building(s) resolve")

    print()
    if r.problems:
        print(f"{r.problems} problem(s) -- the compatch needs a look.")
        return 1
    print("No drift.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
