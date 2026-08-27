# -*- coding: utf-8 -*-
"""
regen_greys_morg.py -- builds the Grey's x Morgenrote compatch in `_greys/greys+morg done`.

Pair GR.6 of the Grey's addon. 35 shared keys. `grey_usu` ships its own compat
to Morgenroete already (the zMoG_USU_MR_*.txt / mMoG_USU_MR_*.txt files, all
loaded as part of grey_usu itself, sorted late by filename) -- most of the 35
keys are already correctly merged there and need nothing here. Three real
gaps survive after reading every one of the 35 bodies by hand (25-27.08.2026):

1. `building_government_administration`. Morgenrote's own TRY_INJECT: adds
   `pmg_panum_hospital` to the group list; grey_usu's `yMoG_USU_government.txt`
   re-declares the building with REPLACE_OR_CREATE: and does not name that
   group -- USU's author even left the fix commented out in their own file
   ("Done within morgenrote - needs to be re-done because this overwrites
   morgenrote"). Restored here with TRY_INJECT:, matching the commented code.

2. Five `RU_BL_{DP,PP,RP,TP,VP}` Russian-declension routing tables (dative /
   prepositional / genitive / instrumental / accusative -- one customizable
   localization key per case). Morgenrote's `99_mr_ru_custom_loc.txt` does
   REPLACE: with an exhaustive `text = { trigger = { is_building_type = X }
   localization_key = ... } }` list covering every building it knows, 124
   entries per case. grey_usu's `999_MoG_USU_railway_ru_custom_loc.txt` is a
   BARE (no prefix) declaration of the same five keys with its own 96-entry
   list -- a bare full body in a later mod eats an earlier REPLACE: whole, so
   Morgenrote's routing for the 30 buildings it alone knows about (its own
   monuments, dubois nature-reserve buildings, elgar opera, the vanilla
   airport/railway) is gone. Purely text routing, independent of which mod's
   *body* wins for building_airport / building_railway, so all 30 are
   restored here regardless -- including building_railway even though its
   building body is deliberately NOT fixed by this pair (GR.9 / GR.16 / GR.17,
   see the plan). Fixed with TRY_INJECT:, one file, all five keys, verbatim
   `text` blocks copied out of Morgenrote's own file so the localization_key
   spelling can't drift from a hand-retyped copy.

3. `pm_nr_national_park`. Morgenrote sets `state_modifiers.unscaled.
   state_standard_of_living_add = 0.05`; grey_usu's TRY_REPLACE: in
   `mMoG_USU_MR_dubois_pms.txt` adds its own building_modifiers/
   country_modifiers on top but drops that one unscaled field with no
   comment marking it as an intentional change (contrast the elgar PM file
   in the same mod, which marks every rebalance `# was N`). Restored with
   TRY_INJECT:.

NOT fixed here, on purpose:
  * `building_railway` body -- USU turns it into a station and moves the
    line to `building_usu_railway_line`; the winning body belongs to the
    LLWA-addon merge (GR.9 / GR.16 / GR.17), not this pair. Only its RU_BL_*
    routing entries are handled here (see point 2).
  * `pm_nr_royal_reserve` -- `state_upper_strata_standard_of_living_add`:
    Morgenrote 0.1, grey_usu's rewrite 0.2, no comment either way. Decision
    27.08.2026 (asked of the user, not inferred): keep USU's 0.2, nothing to
    write. USU's file already builds out ai_value/building_modifiers/
    country_modifiers for this PM beyond Morgenrote's original, consistent
    with a deliberate (if undocumented) rebalance.
  * everything else in the 35: buildings 4/6, company_types 1/1, pop_needs
    2/2, production_methods 27/29 (aviation 9 + elgar 7 + dubois 1 of 2),
    scripted_effects 2/2, scripted_triggers 1/1 -- checked body by body,
    already correct (additive TRY_INJECT:, or a documented rebalance, or an
    identical stub on both sides, or grey_usu's own compat trigger already
    repoints at the right key). See the plan, GR.6, for the full account.

Usage:
    python3 regen_greys_morg.py            # write the compatch
    python3 regen_greys_morg.py --check    # report only, exit 1 if sources drifted
"""

from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vic3lib as V  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
res = lambda p: os.path.normpath(os.path.join(HERE, p))

MORG = res("../../vic3_mods_out/Morgenrote")
GREYS = res("../../vic3_mods_out/grey_add_alot_of_things")
USU = os.path.join(GREYS, "grey_usu")
OUT = res("../_greys/greys+morg done")

MORG_GOV = os.path.join(MORG, "common/buildings/mr_vanilla_buildings_replace.txt")
USU_GOV = os.path.join(USU, "common/buildings/yMoG_USU_government.txt")
MORG_RU = os.path.join(MORG, "common/customizable_localization/99_mr_ru_custom_loc.txt")
USU_RU = os.path.join(USU, "common/customizable_localization/999_MoG_USU_railway_ru_custom_loc.txt")
MORG_DUBOIS_PM = os.path.join(MORG, "common/production_methods/mr_science_dubois_production_methods.txt")
USU_DUBOIS_PM = os.path.join(USU, "common/production_methods/mMoG_USU_MR_dubois_pms.txt")

DATE = "2026-08-27"
CHECK_ONLY = False
WRITTEN: dict[str, bytes] = {}

HEADER = """# Grey's x Morgenrote compatch (GR.6) -- {what}
# Generated by tools/regen_greys_morg.py on {date}. Do not hand-edit: the next
# run overwrites this file. Change the generator instead.
#
# Load order: ... -> Morgenroete -> ... -> Grey's pack -> THIS.
# Why this file exists: {why}
"""


def write(rel: str, text: str, what: str, why: str, bom: bool | None = None):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    body = HEADER.format(what=what, why=why, date=DATE) + "\n" + text.rstrip("\n") + "\n"
    assert V.brace_balance(body) == 0, f"{rel}: brace balance {V.brace_balance(body)}"
    if bom is None:
        bom = any(ord(ch) > 127 for line in body.split("\n") for ch in line.split("#")[0])
    blob = (("﻿" if bom else "") + body).encode("utf-8")
    WRITTEN[rel] = blob
    if CHECK_ONLY:
        old = open(path, "rb").read() if os.path.isfile(path) else None
        print(f"  {'SAME  ' if old == blob else 'DRIFT '} {rel}")
        return
    V.write(path, body, bom=bom)
    print(f"  wrote {rel}  ({len(body.splitlines())} lines, bom={bom})")


def build_government_administration():
    morg_text = V.read(MORG_GOV)
    _, morg_body = V.entry(morg_text, "building_government_administration", "TRY_INJECT:")
    morg_groups = V.sub_names(morg_body)
    assert morg_groups == ["production_method_groups"], (
        f"Morgenrote's TRY_INJECT:building_government_administration now names "
        f"{morg_groups}, not just production_method_groups -- re-read GR.6")
    grp_block = V.sub(morg_body, "production_method_groups")
    groups = [g for g in re.sub(r"#.*", "", grp_block).strip("{} \n\t").split()]
    assert groups == ["pmg_panum_hospital"], (
        f"Morgenrote now injects {groups} into building_government_administration, "
        f"not just pmg_panum_hospital -- re-read GR.6")

    usu_text = V.read(USU_GOV)
    _, usu_body = V.entry(usu_text, "building_government_administration", "REPLACE_OR_CREATE:")
    have_raw = V.sub(usu_body, "production_method_groups") or ""
    have = re.sub(r"#.*", "", have_raw)
    assert "pmg_panum_hospital" not in have, (
        "grey_usu's own body now actively names pmg_panum_hospital (not just in a "
        "comment) -- the author fixed it, drop this fix from the generator")

    text = ("TRY_INJECT:building_government_administration = {\n"
            "\tproduction_method_groups = {\n"
            "\t\tpmg_panum_hospital\n"
            "\t}\n"
            "}\n")
    write("common/buildings/zz_greys_morg_government.txt", text,
          "put Morgenrote's hospital PM group back on the government-administration building",
          "Morgenrote adds pmg_panum_hospital with TRY_INJECT:. grey_usu re-declares the "
          "whole building with REPLACE_OR_CREATE: in yMoG_USU_government.txt and does not "
          "name that group, so it silently disappears -- USU's own author left the fix "
          "commented out in that file (\"Done within morgenrote - needs to be re-done "
          "because this overwrites morgenrote\"), never applied it. TRY_INJECT: here does "
          "what that comment says.")


RU_CASES = ["RU_BL_DP", "RU_BL_PP", "RU_BL_RP", "RU_BL_TP", "RU_BL_VP"]


def _building_set(body: str) -> dict[str, str]:
    """building type -> verbatim `text = { ... }` statement, keyed by is_building_type.

    Brace-matched via vic3lib's depth-0 walker rather than a regex: entries in
    these files are not perfectly uniformly indented, and a regex anchored on
    a specific indent silently drops entries instead of failing loud.
    """
    out = {}
    for name, start, o, c in V._depth0_iter(body):
        if name != "text":
            continue
        block = body[start:c + 1]
        bm = re.search(r"is_building_type\s*=\s*(\S+)", block)
        if bm:
            out[bm.group(1)] = block
    return out


def build_ru_bl():
    morg_text = V.read(MORG_RU)
    usu_text = V.read(USU_RU)
    expected_lost = None
    records = []
    for key in RU_CASES:
        _, morg_body = V.entry(morg_text, key, "REPLACE:")
        morg_buildings = _building_set(morg_body)
        assert len(morg_buildings) == 124, (
            f"Morgenrote's {key} now lists {len(morg_buildings)} buildings, not 124 -- "
            f"re-read GR.6, the lost set below is probably stale")

        _, usu_body = V.entry(usu_text, key)  # bare, no prefix
        usu_buildings = _building_set(usu_body)
        assert len(usu_buildings) == 96, (
            f"grey_usu's {key} now lists {len(usu_buildings)} buildings, not 96 -- re-read GR.6")

        lost = sorted(set(morg_buildings) - set(usu_buildings))
        assert lost, f"{key}: grey_usu's list already a superset of Morgenrote's -- drop this fix"
        if expected_lost is None:
            expected_lost = lost
        else:
            assert lost == expected_lost, (
                f"{key} loses a different building set than {RU_CASES[0]} "
                f"({lost} vs {expected_lost}) -- the five cases used to be in lockstep, "
                f"re-read GR.6 by hand")

        # indent each verbatim block by one tab so it reads as nested inside the
        # TRY_INJECT: wrapper, whatever the source file's own internal indent style
        blocks = "\n".join(
            "\n".join("\t" + line for line in morg_buildings[b].split("\n"))
            for b in lost)
        records.append(f"TRY_INJECT:{key} = {{\n{blocks}\n}}")

    note = ("# " + str(len(expected_lost)) + " building types Morgenrote routes and grey_usu's "
            "own list (999_MoG_USU_railway_ru_custom_loc.txt, bare, no prefix) does not -- "
            "a bare full body in a later mod eats Morgenrote's REPLACE: whole:\n"
            + "\n".join(f"#   {b}" for b in expected_lost))
    text = note + "\n\n" + "\n\n".join(records)
    write("common/customizable_localization/zz_greys_morg_ru_bl.txt", text,
          "restore Morgenrote's Russian building-name routing for its own buildings, all five cases",
          "RU_BL_{DP,PP,RP,TP,VP} are the five Russian-case routing tables (dative / "
          "prepositional / genitive / instrumental / accusative) that point each building "
          "type at a localization key. Morgenrote's REPLACE: lists 124 buildings per case, "
          "including its own new content (monuments, dubois nature-reserve buildings, elgar "
          "opera) and the vanilla airport/railway. grey_usu's own routing file is a BARE "
          "declaration of the same five keys (96 buildings) loaded later -- a bare body beats "
          "an earlier REPLACE: outright, so Morgenrote's 30 extra buildings get no Russian "
          "declension at all, just the default. Restored verbatim (same text blocks Morgenrote "
          "ships) via TRY_INJECT:, which adds list entries rather than replacing the record. "
          "building_railway and building_airport are included here even though the *building* "
          "body for the former is decided elsewhere (GR.9 / GR.16 / GR.17) -- this routing "
          "entry is independent of which mod's body wins.")


def build_pm_nr_national_park():
    morg_text = V.read(MORG_DUBOIS_PM)
    _, morg_body = V.entry(morg_text, "pm_nr_national_park")
    morg_sm_whole = V.sub(morg_body, "state_modifiers")
    assert morg_sm_whole, "Morgenrote's pm_nr_national_park no longer names state_modifiers"
    # V.sub returns "{ ... }" (braces included) -- strip them before searching inside,
    # or the outer brace throws off _depth0_iter's depth count by one.
    assert morg_sm_whole[0] == "{" and morg_sm_whole[-1] == "}"
    morg_sm = morg_sm_whole[1:-1]
    morg_unscaled = V.sub(morg_sm, "unscaled")
    assert morg_unscaled and "state_standard_of_living_add" in morg_unscaled, (
        "Morgenrote's pm_nr_national_park.state_modifiers.unscaled no longer carries "
        "state_standard_of_living_add -- re-read GR.6")
    val_m = re.search(r"state_standard_of_living_add\s*=\s*([-0-9.]+)", morg_unscaled)
    assert val_m and val_m.group(1) == "0.05", (
        f"Morgenrote's state_standard_of_living_add is now {val_m.group(1) if val_m else '?'}, "
        f"not 0.05 -- re-read GR.6 before trusting the hardcoded value below")

    usu_text = V.read(USU_DUBOIS_PM)
    _, usu_body = V.entry(usu_text, "pm_nr_national_park", "TRY_REPLACE:")
    usu_sm = V.sub(usu_body, "state_modifiers") or ""
    assert "state_standard_of_living_add" not in usu_sm, (
        "grey_usu's pm_nr_national_park now carries state_standard_of_living_add itself -- "
        "the author fixed it, drop this fix from the generator")

    text = ("TRY_INJECT:pm_nr_national_park = {\n"
            "\tstate_modifiers = {\n"
            "\t\tunscaled = {\n"
            "\t\t\tstate_standard_of_living_add = 0.05\n"
            "\t\t}\n"
            "\t}\n"
            "}\n")
    write("common/production_methods/zz_greys_morg_dubois_pms.txt", text,
          "put Morgenrote's standard-of-living bonus back on the national-park PM",
          "Morgenrote's pm_nr_national_park sets state_modifiers.unscaled."
          "state_standard_of_living_add = 0.05. grey_usu's TRY_REPLACE: in "
          "mMoG_USU_MR_dubois_pms.txt adds its own building_modifiers/country_modifiers on "
          "top (workforce, research speed) but the unscaled sub-block is dropped with no "
          "comment marking it intentional -- contrast the elgar PM file in the same mod, "
          "where every rebalance is marked `# was N`. TRY_INJECT: adds unscaled as a new "
          "named sub-block; it does not collide with level_scaled, so nothing else in the "
          "PM is touched. pm_nr_royal_reserve's own state_modifiers dispute (0.1 vs 0.2 on "
          "the neighbouring upper-strata field, same file) is NOT fixed here -- decision "
          "27.08.2026, keep USU's 0.2, see the module docstring.")


def self_check() -> int:
    bad = 0
    seen: dict[tuple[str, str], str] = {}
    for rel, blob in sorted(WRITTEN.items()):
        text = blob.decode("utf-8-sig")
        if V.brace_balance(text) != 0:
            print(f"  FAIL {rel}: brace balance {V.brace_balance(text)}")
            bad += 1
        non_ascii = any(ord(ch) > 127 for line in text.split("\n") for ch in line.split("#")[0])
        if non_ascii and not blob.startswith(b"\xef\xbb\xbf"):
            print(f"  FAIL {rel}: non-ASCII outside a comment, needs a BOM")
            bad += 1
        doubled = re.findall(r"^[A-Z_]+:[A-Z_]+:", text, re.M)
        if doubled:
            print(f"  FAIL {rel}: {len(doubled)} doubled prefix(es), e.g. {doubled[0]}")
            bad += 1
        category, depth = os.path.dirname(rel), 0
        for raw in text.split("\n"):
            code = raw.split("#", 1)[0]
            if depth == 0:
                m = re.match(r"^﻿?([A-Z_]+:)?([A-Za-z0-9_.\-]+)\s*=\s*\{", code)
                if m and (m.group(1) or "").rstrip(":") in ("INJECT", "TRY_INJECT"):
                    m = None
                if m and m.group(2) not in ("COUNTRIES", "GLOBAL", "BUILDINGS", "POPS"):
                    where = (category, m.group(2))
                    if where in seen:
                        print(f"  FAIL duplicate key {m.group(2)} in {category}: "
                              f"{seen[where]} and {rel}")
                        bad += 1
                    seen[where] = rel
            depth += code.count("{") - code.count("}")
    print(f"  self-check: {len(WRITTEN)} files, {len(seen)} top-level keys, {bad} problem(s)")
    return bad


def main() -> int:
    global CHECK_ONLY
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only, do not write")
    args = ap.parse_args()
    CHECK_ONLY = args.check

    print(f"regen_greys_morg.py -> {OUT}")
    for name, fn in (("government administration", build_government_administration),
                      ("RU_BL_* routing", build_ru_bl),
                      ("dubois national park PM", build_pm_nr_national_park)):
        print(f"[{name}]")
        fn()

    print()
    bad = self_check()
    if args.check:
        drifted = [r for r, blob in WRITTEN.items()
                   if (open(os.path.join(OUT, r), "rb").read()
                       if os.path.isfile(os.path.join(OUT, r)) else None) != blob]
        if drifted:
            print(f"\n{len(drifted)} file(s) on disk no longer match the sources:")
            for r in drifted:
                print("  " + r)
            return 1
        print("\nall files match the current Grey's / Morgenrote sources")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
