#!/usr/bin/env python3
"""
Regenerate the pinned copies that the "E&F + Tech & Res ComPatch Fix" has to carry.

Why this script exists
----------------------
Three things in the Tech & Res + E&F ComPatch cannot be repaired additively:

  1. `REPLACE:building_automotive_industry`, `REPLACE:building_synthetics_plant`
     and `REPLACE:building_power_plant`.
     REPLACE: swaps whole sub-blocks, so the compatch's `production_method_groups`
     wins over T&R's. The compatch's copy is one T&R revision old and therefore
     reverts real changes: the power plant loses `pmg_power_transmission` and gets
     back the `pmg_data_optimization_light_industry` T&R removed; the automotive
     industry falls back from `pmg_data_optimization_heavy_industry_algorithmic_dispatch`
     to plain `pmg_data_optimization_heavy_industry`.
     There is no additive fix: INJECT: could add the missing group but could not
     remove the stale one, and two overlapping data-optimisation groups on one
     building would let the player stack both.

  2. `financial_crash_consequences` and `economic_crisis_consequences`.
     Both are one big `every_scope_building = { limit = { or = { ... } } }`, and
     a scripted_effect cannot be extended from another mod. The compatch rewrote
     eleven vanilla building names into their plural `aliases` form; nine of those
     aliases are real, two are not (`building_artillery_foundries` never existed,
     `building_military_shipyard(s)` was removed from vanilla in 1.13). Using the
     canonical names is correct whether or not aliases resolve in script scopes.

  3. Three of E&F's five inflation baskets.
     Each is a weighted average: sum(price deviation * buy orders) over a basket,
     divided by 0.1 + sum(buy orders) over the same basket. Numerator and divisor
     have to list the same goods, and in the compatch they do not.

Hand-maintaining these copies rots exactly the way the compatch itself rotted.
Run this after every Tech & Res update and after every update of the compatch.

The Morgenroete question
------------------------
The E&F + Morgenroete ComPatch redefines `inflation_on_consumer_goods` and
`inflation_on_raw_material` too, to add air_travel / elgar_music /
elgar_instruments / manzoni_prints / good_uranium. Two mods redefining the same
script value means the later one wins outright and the earlier one's goods drop
out of the basket -- today the T&R compatch loads after and silently wins.

By default this script generates the E&F + T&R basket only, matching what this
mod declares as its dependencies. Pass --morg in a build that also runs the
Morgenroete compatch: the Morgenroete goods are then merged in, and because this
mod loads last, its definition is the one the game keeps.

Usage:
    python3 regen_ef_tr_copies.py                  # E&F + T&R only
    python3 regen_ef_tr_copies.py --morg           # also merge Morgenroete goods
    python3 regen_ef_tr_copies.py --check [--morg] # report drift, write nothing
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# --- layout -----------------------------------------------------------------

DEFAULT_ROOT = Path(__file__).resolve().parent.parent          # vic3_mods/
DEFAULT_OUT_ROOT = DEFAULT_ROOT.parent / "vic3_mods_out"       # vic3_mods_out/

TR = "TechRes+Kuromi/t&r"
COMPATCH = "_ef/ef+tr+kai out outdate"
MORG = "_ef/ef+morg done"
FIX = "_ef/ef+tr fix"

# --- 1. buildings taken from T&R -------------------------------------------

# The two E&F groups the compatch exists to re-add, in the order it used.
EF_GROUPS = ["pmg_market_liquidity", "pmg_private_ownership_manufacture_stock"]

TR_BUILDINGS_FILE = "common/buildings/ztr_vanilla_modified_buildings.txt"
TR_BUILDINGS = [
    "building_automotive_industry",
    "building_synthetics_plant",
    "building_power_plant",
]

# --- 2. crisis effects taken from the compatch ------------------------------

CP_EFFECTS_FILE = "common/scripted_effects/zef_01_financial_scripted_effects.txt"
CP_EFFECTS = ["financial_crash_consequences", "economic_crisis_consequences"]

# Compatch name -> real name in 1.13.10.
# The nine plural forms are declared as `aliases` on the vanilla buildings, so
# they may well resolve; the canonical name is correct either way.
# building_financial_centre_TUS and building_vineyard_plantation are E&F's own
# typos, inherited by the compatch -- fixed here because we re-emit the blocks
# anyway.
RENAMES = {
    "building_textile_mills": "building_textile_mill",
    "building_furniture_manufacturies": "building_furniture_manufactory",
    "building_tooling_workshops": "building_tooling_workshop",
    "building_paper_mills": "building_paper_mill",
    "building_chemical_plants": "building_chemical_plant",
    "building_synthetics_plants": "building_synthetics_plant",
    "building_steel_mills": "building_steel_mill",
    "building_shipyards": "building_shipyard",
    "building_munition_plants": "building_munition_plant",
    "building_artillery_foundries": "building_artillery_foundry",
    "building_financial_centre_TUS": "building_financial_centre_tus",
    "building_vineyard_plantation": "building_vineyard",
}

# Removed from vanilla in 1.13 with nothing to map them onto: drop the line.
DROPPED = {
    "building_military_shipyards",
    "building_military_shipyard",
    "building_naval_base",
}

# T&R industry the compatch does not know about (new in 13.05.2026), added next
# to the sibling it was modelled on.
ADD_AFTER = {
    "building_consumer_electronics_industry": ["building_computer_assembly_plant"],
}

# --- 3. inflation baskets ---------------------------------------------------

CP_VALUES_FILE = "common/script_values/zef_00_economic_scripted_value.txt"
EF_VALUES_FILE = "common/script_values/00_economic_scripted_value.txt"
MORG_VALUES_FILE = "common/script_values/zz_ef_mr_inflation_patch.txt"

# Only the baskets that actually need us.
#   raw_material       -- compatch: bauxite missing from the divisor, hardwood twice
#   manufactured_goods -- compatch: alloys missing from the divisor
#   consumer_goods     -- symmetric in both mods, so nothing to repair; emitted
#                         only under --morg, where the point is to stop the
#                         compatch's definition from swallowing the Morgenroete
#                         goods (it redefines the same key and loads later)
# inflation_on_energy and inflation_on_military_equipment are left to the
# compatch: military is symmetric, and energy only carries E&F's own
# hardwood-in-the-divisor quirk (see below).
CP_VALUES = [
    "inflation_on_raw_material",
    "inflation_on_manufactured_goods",
]
CP_VALUES_MORG_ONLY = ["inflation_on_consumer_goods"]

# E&F divides three baskets by hardwood buy orders without ever adding hardwood
# to their numerators. That only dilutes the result, and it is E&F's, not the
# compatch's -- it belongs in the E&F hotfix, not here. Whitelisted so the
# symmetry pass does not quietly delete it (the compatch already settled the
# raw-material case by adding hardwood to that numerator).
EF_DIVISOR_ONLY_OK = {"hardwood"}


# --- helpers ----------------------------------------------------------------


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def top_block(text: str, key: str) -> str:
    """Return the whole `[PREFIX:]key = { ... }` block, prefix included."""
    m = re.search(r"^((?:\w+:)?)" + re.escape(key) + r"\s*=\s*\{", text, re.M)
    if not m:
        raise KeyError(key)
    depth = 0
    for j in range(m.end() - 1, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[m.start(): j + 1]
    raise ValueError(f"unbalanced braces around {key}")


def add_groups(block: str, groups: list[str]) -> str:
    """Append PM groups to the building's production_method_groups sub-block."""
    m = re.search(r"(production_method_groups\s*=\s*\{)([^}]*)(\})", block)
    if not m:
        raise ValueError("no production_method_groups in block")
    existing = m.group(2).split()
    missing = [g for g in groups if g not in existing]
    if not missing:
        return block
    body = m.group(2).rstrip("\n\t ")
    inserted = body + "\n\n" + "".join(f"\t\t{g} #E&F\n" for g in missing) + "\t"
    return block[: m.start(2)] + inserted + block[m.end(2):]


def fix_names(block: str) -> tuple[str, list[str]]:
    """Apply RENAMES / DROPPED / ADD_AFTER and de-duplicate inside each `or`."""
    notes: list[str] = []
    out: list[str] = []
    seen_stack: list[set[str]] = []
    depth_stack: list[int] = []
    depth = 0

    for line in block.split("\n"):
        opens, closes = line.count("{"), line.count("}")
        m = re.search(r"is_building_type\s*=\s*(building_\w+)", line)

        if m:
            name = m.group(1)
            if name in DROPPED:
                notes.append(f"dropped {name}")
                depth += opens - closes
                continue
            new = RENAMES.get(name, name)
            if new != name:
                notes.append(f"{name} -> {new}")
                line = line.replace(name, new)
            if seen_stack and new in seen_stack[-1]:
                notes.append(f"de-duplicated {new}")
                depth += opens - closes
                continue
            if seen_stack:
                seen_stack[-1].add(new)
            out.append(line)
            for extra in ADD_AFTER.get(new, []):
                if not (seen_stack and extra in seen_stack[-1]):
                    out.append(line.replace(new, extra))
                    if seen_stack:
                        seen_stack[-1].add(extra)
                    notes.append(f"added {extra}")
            depth += opens - closes
            continue

        if re.search(r"\bor\s*=\s*\{", line, re.I):
            seen_stack.append(set())
            depth_stack.append(depth)
        out.append(line)
        depth += opens - closes
        while depth_stack and depth <= depth_stack[-1]:
            depth_stack.pop()
            seen_stack.pop()

    return "\n".join(out), notes


# --- inflation basket surgery ----------------------------------------------

NUM_RE = re.compile(r"^(\s*)mg:(\w+)\s*=\s*\{", re.M)
DIV_RE = re.compile(r"^(\s*)add = market\.mg:(\w+)\.market_goods_buy_orders\s*$", re.M)


def basket(block: str) -> tuple[list[str], list[str]]:
    return [m.group(2) for m in NUM_RE.finditer(block)], [m.group(2) for m in DIV_RE.finditer(block)]


def split_divide(block: str) -> tuple[int, int]:
    m = re.search(r"divide\s*=\s*\{", block)
    if not m:
        raise ValueError("no divide block")
    depth = 0
    for j in range(m.end() - 1, len(block)):
        if block[j] == "{":
            depth += 1
        elif block[j] == "}":
            depth -= 1
            if depth == 0:
                return m.start(), j + 1
    raise ValueError("unbalanced divide block")


def fix_inflation(block: str, extra_goods: list[str], ef_block: str) -> tuple[str, list[str]]:
    """Merge extra goods in, then make numerator and divisor list the same goods.

    Rules, in order:
      * every good in `extra_goods` that is in neither half is appended to both;
      * every numerator good missing from the divisor is appended to the divisor;
      * duplicate divisor lines are dropped;
      * a divisor good with no numerator term is dropped, unless E&F's own
        version has it too (EF_DIVISOR_ONLY_OK) -- that is E&F's business.
    Nothing is ever removed from the numerator.
    """
    notes: list[str] = []
    ef_num, ef_div = basket(ef_block)
    ef_divisor_only = (set(ef_div) - set(ef_num)) & EF_DIVISOR_ONLY_OK

    num, _ = basket(block)
    for g in extra_goods:
        if g in num:
            continue
        m = list(NUM_RE.finditer(block))[-1]
        depth = 0
        for j in range(m.end() - 1, len(block)):
            if block[j] == "{":
                depth += 1
            elif block[j] == "}":
                depth -= 1
                if depth == 0:
                    break
        entry = (
            f"\n{m.group(1)}mg:{g} = {{\n"
            f"{m.group(1)}\tadd = {{\n"
            f"{m.group(1)}\t\tadd = market_goods_pricier\n"
            f"{m.group(1)}\t\tmultiply = market_goods_buy_orders\n"
            f"{m.group(1)}\t}}\n"
            f"{m.group(1)}}}"
        )
        block = block[: j + 1] + entry + block[j + 1:]
        notes.append(f"merged mg:{g} into the numerator")
        num.append(g)

    start, end = split_divide(block)
    head, div, tail = block[:start], block[start:end], block[end:]

    kept, seen = [], set()
    for line in div.split("\n"):
        m = DIV_RE.match(line)
        if not m:
            kept.append(line)
            continue
        g = m.group(2)
        if g in seen:
            notes.append(f"de-duplicated market.mg:{g} in the divisor")
            continue
        if g not in num and g not in ef_divisor_only:
            notes.append(f"dropped market.mg:{g} from the divisor (nothing in the numerator)")
            continue
        seen.add(g)
        kept.append(line)
    div = "\n".join(kept)

    missing = [g for g in num if g not in seen]
    if missing:
        indent = DIV_RE.search(div).group(1)
        add = "".join(f"{indent}add = market.mg:{g}.market_goods_buy_orders\n" for g in missing)
        div = div[: div.rindex("}")] + add + div[div.rindex("}"):]
        notes += [f"added market.mg:{g} to the divisor" for g in missing]

    return head + div + tail, notes


# --- output -----------------------------------------------------------------


def emit(path: Path, header: str, blocks: list[str], check: bool) -> bool:
    # utf-8-sig on write emits the BOM; do not prepend one by hand.
    text = header.rstrip("\n") + "\n\n" + "\n\n".join(b.strip("\n") for b in blocks) + "\n"
    if text.count("{") != text.count("}"):
        raise ValueError(f"{path}: unbalanced braces")
    old = path.read_text(encoding="utf-8-sig") if path.exists() else None
    changed = old != text
    if check:
        print(f"  {'DRIFT' if changed else 'ok   '}  {path.name}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8-sig", newline="\n")
        print(f"  {'written  ' if changed else 'unchanged'}  {path.name}")
    return changed


def note_lines(notes: list[str]) -> str:
    if not notes:
        return "###   none -- already consistent"
    return "".join(f"###   {n}\n" for n in sorted(set(notes))).rstrip("\n")


# --- main -------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="vic3_mods/ root")
    ap.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT, help="vic3_mods_out/ root")
    ap.add_argument("--morg", action="store_true", help="merge Morgenroete goods into the baskets")
    ap.add_argument("--check", action="store_true", help="report drift, write nothing")
    args = ap.parse_args()

    tr, cp, ef, morg, fix = (
        args.out_root / TR,
        args.root / COMPATCH,
        args.out_root / "E&F",
        args.root / MORG,
        args.root / FIX,
    )
    for p in (tr, cp, ef, fix):
        if not p.is_dir():
            print(f"missing: {p}", file=sys.stderr)
            return 2
    if args.morg and not morg.is_dir():
        print(f"--morg given but missing: {morg}", file=sys.stderr)
        return 2

    print(f"mode: {'E&F + T&R + Morgenroete' if args.morg else 'E&F + T&R'}")
    drift = False

    # 1. buildings ----------------------------------------------------------
    src = read(tr / TR_BUILDINGS_FILE)
    blocks = [add_groups(top_block(src, n), EF_GROUPS) for n in TR_BUILDINGS]
    header = (
        "### E&F + Tech & Res ComPatch Fix (Vic3 1.13) -- GENERATED FILE, DO NOT EDIT\n"
        "###\n"
        "### Source: Tech & Res " + TR_BUILDINGS_FILE + ", plus the two E&F PM groups.\n"
        "### Regenerate with tools/regen_ef_tr_copies.py after any T&R update.\n"
        "###\n"
        "### T&R fully REPLACE:s these three vanilla buildings, which wipes E&F's\n"
        "### earlier INJECT: of pmg_market_liquidity. The compatch re-adds it, but its\n"
        "### copy is one T&R revision old, and because REPLACE: swaps whole sub-blocks\n"
        "### its stale production_method_groups wins over T&R's current one. This file\n"
        "### loads after the compatch, carrying T&R's list as it is today."
    )
    drift |= emit(fix / "common/buildings/zzzz_ef_tr_fix_buildings_gen.txt", header, blocks, args.check)

    # 2. crisis effects -----------------------------------------------------
    src = read(cp / CP_EFFECTS_FILE)
    blocks, notes = [], []
    for name in CP_EFFECTS:
        block, n = fix_names(top_block(src, name))
        blocks.append(block)
        notes += [f"{name}: {x}" for x in n]
    header = (
        "### E&F + Tech & Res ComPatch Fix (Vic3 1.13) -- GENERATED FILE, DO NOT EDIT\n"
        "###\n"
        "### Source: the compatch's own " + CP_EFFECTS_FILE + ",\n"
        "### with building names corrected. Regenerate with tools/regen_ef_tr_copies.py\n"
        "### after any update of the compatch.\n"
        "###\n"
        "### A scripted_effect cannot be extended from another mod, so the only way to\n"
        "### repair the `or` list is to re-state the effect. Same key later in load\n"
        "### order wins, and this mod loads after the compatch.\n"
        "###\n"
        "### Corrections applied this run:\n" + note_lines(notes)
    )
    drift |= emit(fix / "common/scripted_effects/zzzz_ef_tr_fix_effects_gen.txt", header, blocks, args.check)

    # 3. inflation baskets --------------------------------------------------
    cp_src, ef_src = read(cp / CP_VALUES_FILE), read(ef / EF_VALUES_FILE)
    morg_src = read(morg / MORG_VALUES_FILE) if args.morg else ""
    blocks, notes = [], []
    for name in (CP_VALUES_MORG_ONLY + CP_VALUES) if args.morg else CP_VALUES:
        extra: list[str] = []
        if morg_src:
            try:
                mnum, _ = basket(top_block(morg_src, name))
                enum, _ = basket(top_block(ef_src, name))
                cnum, _ = basket(top_block(cp_src, name))
                extra = [g for g in mnum if g not in enum and g not in cnum]
            except KeyError:
                pass  # the Morgenroete patch only touches two of the five
        block, n = fix_inflation(top_block(cp_src, name), extra, top_block(ef_src, name))
        block = re.sub(r"^REPLACE:", "", block)  # plain key: later definition wins
        blocks.append(block)
        notes += [f"{name}: {x}" for x in n]
    header = (
        "### E&F + Tech & Res ComPatch Fix (Vic3 1.13) -- GENERATED FILE, DO NOT EDIT\n"
        "###\n"
        "### Source: the compatch's own " + CP_VALUES_FILE + "\n"
        + ("### merged with the E&F + Morgenroete ComPatch's " + MORG_VALUES_FILE + ".\n" if args.morg
           else "### (Morgenroete goods NOT merged -- rerun with --morg for a build with it).\n")
        + "### Regenerate with tools/regen_ef_tr_copies.py after any update of either.\n"
        "###\n"
        "### Each basket is a weighted average: sum(price deviation * buy orders) over\n"
        "### the goods, divided by 0.1 + sum(buy orders) over the same goods. A good in\n"
        "### the numerator but not the divisor pushes the reading up; a good in the\n"
        "### divisor but not the numerator dilutes it towards zero. Both halves must\n"
        "### list the same goods, and in the compatch they do not.\n"
        "###\n"
        "### E&F's own hardwood-in-the-divisor-only quirk is left alone here -- it is\n"
        "### in E&F itself, in three baskets, and belongs in the E&F hotfix.\n"
        "###\n"
        "### Fixes applied this run:\n" + note_lines(notes)
    )
    drift |= emit(fix / "common/script_values/zzzz_ef_tr_fix_inflation_gen.txt", header, blocks, args.check)

    if args.check and drift:
        print("\ndrift detected -- rerun without --check")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
