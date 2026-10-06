#!/usr/bin/env python3
"""
regen_ef_household_construction.py -- СТР.3, households and cities consume construction
materials (ночь Г, decisions Д.3-Д.10 of 2026-10-03).

Why
---
PSC turns construction sectors into factories of four local goods (wood / iron / steel /
arc-welded construction, `local = yes`, like services) that only the construction regulator
buys. Nobody else uses them: no household builds anything, no city maintains anything.
The user (26.09, decided 3.10): households of every stratum build (more with wealth), city
centres maintain (ЖКХ), and natural economies make a little wood_construction themselves.
Real shares: households + ЖКХ ~25-35% of construction materials in the XIX century, ~half by
the end of the game (Feinstein 1978, FIEC 2023 -- research of 26.09).

What it writes (through ld_gen.emit, by entry keys, into the fork «E&F: Ledgerdemain», which depends on PSC)
--------------
1. common/pop_needs/ld_household_construction.txt -- popneed_household_construction:
   the four construction goods, wood first (default); pops buy whichever the state makes.
2. common/production_methods/ld_household_construction_pms.txt -- INJECT:
   * natural economies: the five subsistence buildings' home-workshop methods (and the
     collectivized "no home workshops" ones) output SUBSISTENCE_WOOD wood_construction per
     workforce unit (rice farms twice: their level employs 10 000, not 5 000);
   * ЖКХ (REPLACE, full vanilla bodies): each urban-centre amenity method takes the construction
     good of its tier, and the raw materials the sector of that tier processes come out, their value
     at base prices going into the good (the user, 2026-10-03): stalls wood_construction, squares
     iron_construction + glass, covered markets steel_construction, arcades arc_welded_construction
     + electricity (arcades also need arc_welding, the good's technology).
   grey_usu re-issues the amenity methods with REPLACE_OR_CREATE after the fork:
   tools/regen_greys_psc.py applies the same swap to USU's bodies (and USU's usu_pm_hv_arcades)
   and imports URBAN / urban_block from here.
3. localization/{english,russian}/ld_household_construction_l_<lang>.yml.
The wealth packages (INJECT into wealth_N) and the construction goods' trade fields are merged into
E&F's / PSC's files by hand and are not generated.

Reads vanilla (vic3_mods_out/.vanillaVIC3/common/production_methods/06_urban_center.txt): run --check on the PC.

Calibration (2026-10-03, run 1 of night G, save 1837.1.1, world): the regulators burn ~9 800
construction goods a week (wood 1 900 + iron 7 800), sectors make ~14 100. Households + ЖКХ at
30% of the total => ~4 200 a week at the start, households ~2 800; subsistence makes ~45 000
x SUBSISTENCE_WOOD a week. ЖКХ is held to ~15% of an urban centre's output value -- at a
third of the households' figure it would cost urban centres more than they make in 1836
(world urban centres make ~5 800 services a week); it grows with the cities instead.
!! TUNING !! SUBSISTENCE_WOOD, URBAN -- check against runs (Д.7, Д.8).
Run 2 (3.10, 1836 -> 1841.1, with 3% / 1.5% and 0.1): households took ~4 000 a week in 1837
(~18% of construction goods with ЖКХ, under Д.5's 25-35%) and ~3 100 in 1841, when sectors had
doubled (~9%); prices stayed near base (world 110). Raised x1.5: 4.5% / 2.25% and 0.15.

Usage:  python3 tools/regen_ef_household_construction.py [--check]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vic3lib as V  # noqa: E402
import ld_gen  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

NEED = "popneed_household_construction"
SUBSISTENCE_WOOD = 0.15                   # wood_construction per workforce unit of a subsistence building
SUBSISTENCE = ["farm", "orchard", "pasture", "fishing_village", "rice_farm"]
# ЖКХ, decided by the user 2026-10-03 (after night G): one construction good per amenity tier, and the
# raw materials the construction sector of that tier processes come OUT of the amenity method -- they
# were consumed twice (raw, and again inside the construction good). Their value at base prices is
# added to the construction good on top of the base amount.
URBAN = [  # amenity method, construction good, base amount per workforce unit (night G)
    ("pm_market_stalls", "wood_construction", 0.5),
    ("pm_market_squares", "iron_construction", 0.5),      # + glass (kept)
    ("pm_covered_markets", "steel_construction", 0.75),
    ("pm_arcades", "arc_welded_construction", 1.0),       # + electricity (kept)
]
URBAN_USU = ("usu_pm_hv_arcades", "arc_welded_construction", 1.25)  # Grey's only, regen_greys_psc.py
# what PSC's sector of each tier takes in (PSC/common/production_methods/zz_PSC_construction.txt);
# electricity stays on the arcades (the user: arc-welded + electricity)
SECTOR_INPUTS = {
    "wood_construction": {"wood", "fabric"},
    "iron_construction": {"wood", "fabric", "iron", "tools"},
    "steel_construction": {"steel", "glass", "explosives", "tools"},
    "arc_welded_construction": {"steel", "glass", "explosives", "tools"},
}
COST = {"wood": 20, "fabric": 20, "iron": 40, "tools": 40, "glass": 40, "steel": 50, "explosives": 50,
        "wood_construction": 130, "iron_construction": 92, "steel_construction": 70, "arc_welded_construction": 70}
UNLOCK = {"arc_welded_construction": "arc_welding"}  # PSC: pm_arc_welded_buildings
VANILLA_URBAN =REPO.parent / "vic3_mods_out/.vanillaVIC3/common/production_methods/06_urban_center.txt"

OUT_NEED = "common/pop_needs/zz_ef_household_construction.txt"
OUT_PM = "common/production_methods/zz_ef_household_construction_pms.txt"

LOC = {
    "english": {
        NEED: "Household Construction",
        NEED + "_desc": "Building, extending and repairing their own homes and farmsteads: construction materials bought locally. Wealthier households build more.",
    },
    "russian": {
        NEED: "Строительство домохозяйств",
        NEED + "_desc": "Постройка, достройка и ремонт собственных домов и усадеб: стройматериалы, купленные в своей области. Чем богаче домохозяйство, тем больше строит.",
    },
}

HEAD = """### GENERATED by tools/regen_ef_household_construction.py -- do not edit by hand.
### СТР.3 (ночь Г, 2026-10-03): households and urban centres consume PSC's construction goods.
"""


def build_need() -> str:
    entries = "".join(f"""
	entry = {{
		goods = {g}

		weight = 1
		max_supply_share = 1.0
		min_supply_share = 0.0
	}}
""" for g in ("wood_construction", "iron_construction", "steel_construction", "arc_welded_construction"))
    return HEAD + f"""### Pops buy whichever of the four the state's own market has (all four are local goods):
### wood from natural economies and wooden sectors, iron/steel/arc-welded from later sectors.

{NEED} = {{
	default = wood_construction
{entries}}}
"""


def urban_body(decl: str, pm: str, good: str, base: float, prefix: str) -> str:
    """A full body of an amenity method with the tier's sector inputs swapped for the construction good.

    `decl` is the method's whole declaration from its source (vanilla here, grey_usu in regen_greys_psc.py).
    """
    head, body = decl.split("{", 1)
    removed, value = [], 0.0
    out_lines, placed = [], False
    amount_line = None
    for line in body.split("\n"):
        m = re.match(r"^(\s*)goods_input_(\w+)_add\s*=\s*([\d.]+)", line)
        if m and m.group(2) in SECTOR_INPUTS[good]:
            removed.append(f"{m.group(2)} {m.group(3)}")
            value += float(m.group(3)) * COST[m.group(2)]
            if not placed:
                out_lines.append(m.group(1) + "@@AMOUNT@@")
                placed = True
            continue
        if not placed and re.match(r"^\s*goods_output_\w+_add", line):
            indent = re.match(r"^(\s*)", line).group(1)
            out_lines.append(indent + "@@AMOUNT@@")
            placed = True
        out_lines.append(line)
    assert placed, f"{pm}: no input or output line to place the construction good at"
    amount = round(base + value / COST[good], 2)
    note = (f" # СТР.3 ЖКХ: base {base:g} + removed ({', '.join(removed)}) = {value:g} at base prices"
            if removed else f" # СТР.3 ЖКХ: base {base:g}")
    text = "\n".join(out_lines).replace("@@AMOUNT@@", f"goods_input_{good}_add = {amount:g}{note}")
    # the good's own technology: arcades come with the elevator (era 4), arc-welded construction with
    # arc_welding (era 5) -- without it the method would buy a good nobody makes yet
    tech = UNLOCK.get(good)
    if tech and tech not in text:
        m = re.search(r"unlocking_technologies\s*=\s*\{", text)
        assert m, f"{pm}: no unlocking_technologies to add {tech} to"
        text = text[:m.end()] + f"\n\t\t{tech} # СТР.3: the tier's construction good\n\t\t" + text[m.end():]
    return f"{prefix}{pm} = {{{text}"


def urban_block(items, source_text: str, prefix: str) -> str:
    out = []
    for pm, good, base in items:
        decl, _body = V.entry(source_text, pm)
        out.append(urban_body(decl, pm, good, base, prefix) + "\n")
    return "\n".join(out)


def build_pms() -> str:
    out = [HEAD + f"""### Subsistence: INJECT adds to the method's modifier block (repeated keys add up). Re-diff the target
### methods on a vanilla / VC / Grey's update: a later full body of one of them drops the line.

### --- natural economies: a little wood_construction, the base of households' own building (Д.6, Д.7) ---
"""]
    for b in SUBSISTENCE:
        amount = SUBSISTENCE_WOOD * (2 if b == "rice_farm" else 1)
        for pm in (f"pm_home_workshops_building_subsistence_{b}", f"pm_home_workshops_no_building_subsistence_{b}"):
            out.append(f"""INJECT:{pm} = {{
	building_modifiers = {{
		workforce_scaled = {{
			goods_output_wood_construction_add = {amount:g}
		}}
	}}
}}
""")
    out.append("""### --- ЖКХ: urban centre amenities, full vanilla bodies (REPLACE) ---
### The tier's sector inputs swapped for the construction good, value for value (the user, 2026-10-03).
### No other mod of the set writes these four methods except grey_usu (Grey's branch), which loads later
### with its own bodies: tools/regen_greys_psc.py rebuilds those the same way. Re-run after a vanilla patch.
""")
    out.append(urban_block(URBAN, V.read(VANILLA_URBAN), "REPLACE:"))
    return "\n".join(out)


def build_loc(lang: str) -> str:
    lines = [f"l_{lang}:"] + [f' {k}:0 "{v}"' for k, v in LOC[lang].items()]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.parse_args()
    files = [
        (OUT_NEED, build_need()),
        (OUT_PM, build_pms()),
    ]
    for lang in LOC:
        files.append((f"localization/{lang}/zz_ef_household_construction_l_{lang}.yml", build_loc(lang)))
    for path, text in files:
        assert text.count("{") == text.count("}"), path
        ld_gen.emit(path, text)
    ld_gen.report("regen_ef_household_construction")
    return 0


if __name__ == "__main__":
    sys.exit(main())
