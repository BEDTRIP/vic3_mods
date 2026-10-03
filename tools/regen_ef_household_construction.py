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

What it writes (all in the E&F hotfix, which depends on PSC)
--------------
1. common/pop_needs/zz_ef_household_construction.txt -- popneed_household_construction:
   the four construction goods, wood first (default); pops buy whichever the state makes.
2. common/buy_packages/zz_ef_household_construction_packages.txt -- INJECT into all 99
   wealth_N: N = round(sum of the wealth level's package x SHARE(w)), SHARE falling from
   SHARE_LOW at wealth 1 to SHARE_HIGH at wealth 50 and flat above. Package values are money
   at base prices (OBSESSION_POP_NEED_EXPENSE_MULT: "total spent on pop needs"), so the
   household spends that share of its basket on building. Sums are TGR's packages (the
   no-VC branch). The VC branch: addon-VC's merged REPLACE_OR_CREATE file wipes this INJECT
   and re-adds the same numbers (tools/regen_addon_vc.py reads this file).
3. common/production_methods/zz_ef_household_construction_pms.txt -- INJECT:
   * natural economies: the five subsistence buildings' home-workshop methods (and the
     collectivized "no home workshops" ones) output SUBSISTENCE_WOOD wood_construction per
     workforce unit (rice farms twice: their level employs 10 000, not 5 000);
   * ЖКХ (REPLACE, full vanilla bodies): each urban-centre amenity method takes the construction
     good of its tier, and the raw materials the sector of that tier processes come out, their value
     at base prices going into the good (the user, 2026-10-03): stalls wood_construction, squares
     iron_construction + glass, covered markets steel_construction, arcades arc_welded_construction
     + electricity (arcades also need arc_welding, the good's technology).
   grey_usu re-issues the amenity methods with REPLACE_OR_CREATE after the hotfix:
   tools/regen_greys_psc.py applies the same swap to USU's bodies (and USU's usu_pm_hv_arcades).
4. localization (english, russian).

Calibration (2026-10-03, run 1 of night G, save 1837.1.1, world): the regulators burn ~9 800
construction goods a week (wood 1 900 + iron 7 800), sectors make ~14 100. Households + ЖКХ at
30% of the total => ~4 200 a week at the start, households ~2 800; subsistence makes ~45 000
x SUBSISTENCE_WOOD a week. ЖКХ is held to ~15% of an urban centre's output value -- at a
third of the households' figure it would cost urban centres more than they make in 1836
(world urban centres make ~5 800 services a week); it grows with the cities instead.
!! TUNING !! SHARE_LOW / SHARE_HIGH, SUBSISTENCE_WOOD, URBAN -- check against runs (Д.7, Д.8).
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

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
HOTFIX = REPO / "_ef" / "ef hotfix 1.13"
TGR_PACKAGES = REPO.parent / "vic3_mods_out/TheGreatRevision/common/buy_packages/TGR_TRADE_buy_packages_aggressive.txt"

NEED = "popneed_household_construction"
SHARE_LOW, SHARE_HIGH = 0.045, 0.0225      # share of the basket spent on building, wealth 1 / 50+
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

OUT_NEED = HOTFIX / "common/pop_needs/zz_ef_household_construction.txt"
OUT_PKG = HOTFIX / "common/buy_packages/zz_ef_household_construction_packages.txt"
OUT_PM = HOTFIX / "common/production_methods/zz_ef_household_construction_pms.txt"

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


def share(w: int) -> float:
    return SHARE_LOW - (SHARE_LOW - SHARE_HIGH) * min(1.0, (w - 1) / 49)


def tgr_package_sums() -> dict[int, float]:
    s = TGR_PACKAGES.read_text(encoding="utf-8-sig")
    out = {}
    for m in re.finditer(r"(?m)^(?:[A-Z_]+:)?wealth_(\d+)\s*=\s*\{(.*?)^\}", s, re.S):
        g = re.search(r"goods\s*=\s*\{(.*?)\}", m.group(2), re.S)
        out[int(m.group(1))] = sum(float(v) for _k, v in re.findall(r"(popneed_\w+)\s*=\s*([\d.]+)", g.group(1)))
    assert sorted(out) == list(range(1, 100)), f"TGR packages: wealth levels {sorted(out)[:3]}..{len(out)}"
    return out


def package_values() -> dict[int, int]:
    return {w: max(1, round(v * share(w))) for w, v in tgr_package_sums().items()}


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


def build_packages(vals: dict[int, int]) -> str:
    out = [HEAD + f"""### {NEED} in every wealth level: {SHARE_LOW:.1%} of the level's basket (TGR's packages,
### money at base prices) at wealth 1, falling to {SHARE_HIGH:.1%} at wealth 50 and flat above.
### The VC branch: addon-VC's REPLACE_OR_CREATE wipes these, tools/regen_addon_vc.py re-adds them.
"""]
    for w in range(1, 100):
        out.append(f"INJECT:wealth_{w} = {{\n\tgoods = {{\n\t\t{NEED} = {vals[w]}\n\t}}\n}}\n")
    return "\n".join(out)


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


def emit(path: Path, text: str, check: bool, bom: bool) -> bool:
    data = (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8")
    old = path.read_bytes() if path.exists() else None
    if check:
        print(f"  {'SAME ' if old == data else 'DRIFT'} {path.relative_to(REPO)}")
        return old == data
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    print(f"  wrote {path.relative_to(REPO)}")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    vals = package_values()
    files = [
        (OUT_NEED, build_need(), True),   # Cyrillic in the header comments: BOM
        (OUT_PKG, build_packages(vals), True),
        (OUT_PM, build_pms(), True),
    ]
    for lang in LOC:
        files.append((HOTFIX / f"localization/{lang}/zz_ef_household_construction_l_{lang}.yml", build_loc(lang), True))
    ok = True
    for path, text, bom in files:
        assert text.count("{") == text.count("}"), path
        ok &= emit(path, text, a.check, bom)
    print(f"  packages: wealth 1 {vals[1]}, 5 {vals[5]}, 10 {vals[10]}, 20 {vals[20]}, 50 {vals[50]}, 99 {vals[99]}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
