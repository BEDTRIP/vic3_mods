#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
regen_greys_llwa.py -- builds the Grey's x addon-LLWA compatch in `_greys/greys+llwa`.

Task GR.16, 41 shared keys total (see the plan), plus task GR.9 (the outdated
third-party `usu_llwa` compatch) which turned out to close entirely inside this
same file -- see "4." below.

  1. Eight railway companies: grey_usu's TRY_REPLACE: on each is a full body
     that pre-dates LLWA and has its own extension_building_types list, so
     addon-LLWA's earlier TRY_INJECT: of LLWA_building_roadway is silently gone
     (classic full-body-after-additive-inject loss). Re-issued as a plain
     TRY_INJECT: after the whole Grey's pack -- additive, so it does not matter
     that grey_usu's REPLACE already ran.

  2. Three rail production methods (pm_no_passenger_trains,
     pm_steel_passenger_carriages, pm_wooden_passenger_carriages): the exact
     same shape, `building_modifiers.unscaled.building_job_attractiveness_mult
     = 2` (originally VC's, already restored against LLWA's own body in
     `_llwa/llwa+vc done`) is missing from grey_usu's REPLACE_OR_CREATE bodies
     for these three. grey_usu's own numbers on every other field are kept
     untouched -- this is the same "keep the later mod's design, restore only
     the narrow missing field" rule already applied in llwa+tgr done /
     llwa+vc done.

  3. building_railway / building_airport (GR.9, GR.16, GR.17 all converge on
     these two records -- fixed once, here).

     grey_usu (2026-08-27 update, ~zzzzMoG_USU_railways.txt, 459 lines, was
     226 when the plan was written) SPLIT building_railway into two buildings:
     `building_railway` is now the railway STATION (an AI-subsidy mechanism,
     `pmg_base_building_rail_terminal` + `pmg_logistics_services_railway`),
     and the actual railway is new content, `building_usu_railway_line`
     (`pmg_base_building_railway` + `pmg_passenger_trains` +
     `pmg_automation_building_railway`; `pmg_gaudi_communication` is present
     in the list but commented out). grey_usu has ZERO awareness of LLWA (no
     file anywhere in grey_usu mentions it) -- addon-LLWA's own merged
     building_railway (pre-split: pmg_gaudi_communication MR +
     LLWA_pmg_private_expansion + E&F's pmg_market_liquidity /
     pmg_private_ownership_railroad_stock) is silently gone from both new
     buildings once grey_usu's REPLACE_OR_CREATE: runs.

     Split decided with the user 2026-08-27: building_usu_railway_line gets
     the whole private-ownership economy (LLWA_pmg_private_expansion + both
     E&F groups) -- this is the same building GR.15 already proposes
     railroad_stock for, so this also closes that part of GR.15.
     building_railway (the station) gets only pmg_gaudi_communication back --
     grey_usu's own file carries a commented-out
     `TRY_INJECT:building_railway = { production_method_groups =
     { pmg_gaudi_communication } }` at the bottom, disabled by the author over
     a "PDX REPLACE/INJECT sequence problem" in their own single mod; a
     separate later-loading file (this one) does not hit that problem, so
     their own intended fix is restored verbatim, on the record they targeted.

     building_airport is a plain full-body TRY_REPLACE: by grey_usu
     (zMoG_USU_MR_airports.txt) with no split and no dispute -- it silently
     drops the same three LLWA groups plus E&F's two groups (manufacture_stock
     this time, not railroad_stock -- E&F x Morgenroete's own pairing) that
     addon-LLWA's merged body carries. Restored the same way, additively.

  4. GR.9 (`_greys/usu_llwa out outdate`) audited 2026-08-27 and found to be
     fully superseded -- no file needed for it beyond 3. above:
       * LLWA_building_roadway / LLWA_building_waterway "respecified purely so
         auto-expand rules are properly managed" -- LLWA itself now ships its
         own should_auto_expand on all four transport buildings (roadway,
         waterway, riverway, airway). Fixed upstream since this third-party
         compatch was written.
       * pmg_gaudi_communication, pm_gaudi_no_communication, pmg_tourism_airport
         -- byte-identical to Morgenroete's own current definitions. Stale
         duplicates the old compatch carried for a scenario (USU+LLWA without
         Morgenroete) this pack does not run.
       * pm_luxury_requisitions / pm_travel_agencies -- grey_usu now ships its
         OWN TRY_REPLACE: of both (mMoG_USU_MR_civil_aviation_pms.txt),
         matching Morgenroete's tech gates exactly (curtiss_tourism_tech, not
         the old compatch's mass_propaganda fallback for a no-Morgenroete
         scenario) plus the same goods_input_usu_logistics_add the old
         compatch added by hand. USU absorbed this natively; nothing to do.
       * LLWA_active (`has_game_rule = LLWA_grs_*`) -- superseded by LLWA's own
         `LLWA_is_active_trigger` mechanism (00_LLWA_active_trigger.txt /
         zz_LLWA_active_trigger.txt), a different, official mechanism the old
         compatch predates.
       * LLWA_building_riverway ("отсутствует вовсе" in the old compatch) --
         already fully covered by our own `_llwa/llwa+ef done` (stock
         ownership) and `_llwa/llwa+companies done` (company access), neither
         of which existed when usu_llwa was written.
       * building_airport bare-body variant -- superseded by 3. above, which
         is strictly more complete (also carries E&F).
     Not acted on, left as a note, not a loss: LLWA_building_airway carries no
     potential gate against building_airport anymore (the old compatch's
     `NOT = { morgenrote_is_active }` exclusivity is gone too), so with both
     LLWA and Morgenroete active a player can now build both an airway and an
     airport. Nothing is silently lost here -- it is a possible design/balance
     question, not this project's class of bug -- so no file, no decision
     forced; flag for later if it turns out to matter in play.

NOT in this patch (see the plan's GR.16 bullet for the reasoning):
  * The other seven rail production methods -- grey_usu has its own
    progressively-scaled state_market_access_price_impact design on all
    seven, a genuine numeric dispute, not a silent loss. No file.
  * The six railway companies that ALSO collide with Victorian Century
    (company_great_indian_railway, company_mantetsu, company_orient_express,
    company_panama_company, company_prussian_state_railways,
    company_suez_company) -- these already get a full-body REPLACE_OR_CREATE
    from `_greys/greys+vc done/common/company_types/zz_gvc_companies.txt`.
    Writing a second, separate TRY_INJECT: for them here would do nothing:
    that file's REPLACE_OR_CREATE loads at the same position (after the whole
    Grey's pack) and a full body always wins over an earlier additive INJECT.
    The LLWA fix for those six is folded directly into that file instead --
    see tools/regen_greys_vc.py and its own README section.

Usage:
    python3 regen_greys_llwa.py            # write the compatch
    python3 regen_greys_llwa.py --check    # report only, exit 1 if sources drifted
"""
from __future__ import annotations
import argparse, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vic3lib as V  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
res = lambda p: os.path.normpath(os.path.join(HERE, p))

GREYS = res("../../vic3_mods_out/grey_add_alot_of_things")
USU = os.path.join(GREYS, "grey_usu")
ADDON_LLWA = res("../__addon/addon llwa")
OUT = res("../_greys/greys+llwa done")

DATE = "2026-08-27"
CHECK_ONLY = False
WRITTEN: dict[str, bytes] = {}

HEADER = """### ComPatch Grey's x addon-LLWA -- {what}
###
{why}
### Generated by tools/regen_greys_llwa.py on {date}. Do not hand-edit: the
### next run overwrites this file. Change the generator instead.
### Load order: ... -> addon-LLWA -> ... -> the whole Grey's pack -> THIS.
"""


def write(rel: str, text: str, what: str, why: str):
    body = HEADER.format(what=what, why=why, date=DATE) + "\n" + text.rstrip() + "\n"
    assert V.brace_balance(body) == 0, f"{rel}: unbalanced braces"
    path = os.path.join(OUT, rel)
    if CHECK_ONLY:
        old = V.read(path) if os.path.exists(path) else None
        if old != body:
            print(f"DRIFT: {rel} would change")
            WRITTEN["__drift__"] = b"1"
        return
    V.write(path, body)
    print(f"  wrote {rel} ({len(text.splitlines())} lines)")


# --------------------------------------------------------------------------
# 1. Eight railway companies -- LLWA_building_roadway silently dropped
# --------------------------------------------------------------------------

COMPANIES_ROADWAY = [
    "company_cfr", "company_cordoba_railway", "company_egyptian_rail",
    "company_gwr", "company_imperial_ethiopian_railways",
    "company_iranian_state_railway", "company_sao_paulo_railway",
    "company_tashkent_railroad",
]

RAIL_OVERWRITE_FILES = [
    os.path.join(USU, "common/company_types/yMoG_USU_companies_rail_overwrite.txt"),
    os.path.join(USU, "common/company_types/yMoG_USU_panama_suez.txt"),
]
LLWA_EXT_FILE = os.path.join(ADDON_LLWA, "common/company_types/zz_llwa_companies_extensions.txt")


def build_companies():
    ext_text = V.read(LLWA_EXT_FILE)
    usu_text = "\n".join(V.read(p) for p in RAIL_OVERWRITE_FILES)

    blocks = []
    for k in COMPANIES_ROADWAY:
        # 1. addon-LLWA really does inject exactly LLWA_building_roadway here.
        _decl, ext_body = V.entry(ext_text, k, prefix="TRY_INJECT:")
        ext_list = V.sub(ext_body, "extension_building_types")
        assert ext_list is not None, f"{k}: addon-LLWA no longer injects extension_building_types"
        assert "LLWA_building_roadway" in ext_list, \
            f"{k}: addon-LLWA's inject changed, no longer LLWA_building_roadway: {ext_list}"

        # 2. grey_usu really does re-issue the whole record with its own list,
        #    and that list really does not carry LLWA_building_roadway (else
        #    there is nothing to restore -- fail loudly instead of duplicating).
        _decl, usu_body = V.entry(usu_text, k, prefix="TRY_REPLACE:")
        usu_ext = V.sub(usu_body, "extension_building_types")
        assert usu_ext is not None, f"{k}: grey_usu no longer has extension_building_types at all"
        assert "LLWA_building_roadway" not in usu_ext, \
            f"{k}: grey_usu's own body already carries LLWA_building_roadway -- nothing to restore"

        blocks.append(
            f"# {k} -- grey_usu's TRY_REPLACE: (own extension_building_types list, "
            f"no LLWA_building_roadway) silently drops addon-LLWA's earlier TRY_INJECT:.\n"
            f"# Re-issued additively: does not touch any of grey_usu's own list items.\n"
            f"TRY_INJECT:{k} = {{\n\textension_building_types = {{ LLWA_building_roadway }}\n}}"
        )

    write("common/company_types/zz_greys_llwa_companies.txt", "\n\n".join(blocks),
          "8 railway companies, addon-LLWA's extension_building_types restored",
          "### grey_usu's TRY_REPLACE: on each of these eight companies is a full body\n"
          "### written before addon-LLWA existed. Re-issuing addon-LLWA's own\n"
          "### TRY_INJECT: after the whole Grey's pack restores it additively -- grey_usu's\n"
          "### own extension_building_types items are untouched either way.\n"
          "### The other six railway companies that also collide with Victorian Century\n"
          "### (company_great_indian_railway, company_mantetsu, company_orient_express,\n"
          "### company_panama_company, company_prussian_state_railways,\n"
          "### company_suez_company) are NOT here -- see zz_gvc_companies.txt in\n"
          "### _greys/greys+vc done, which now also carries the LLWA layer for those six.")


# --------------------------------------------------------------------------
# 2. Three rail production methods -- building_job_attractiveness_mult lost
# --------------------------------------------------------------------------

RAIL_PMS = ["pm_no_passenger_trains", "pm_steel_passenger_carriages", "pm_wooden_passenger_carriages"]
RAIL_PM_FILE = os.path.join(USU, "common/production_methods/yMoG_USU_rail_other_pms.txt")


def build_rails():
    text = V.read(RAIL_PM_FILE)
    blocks = []
    for k in RAIL_PMS:
        _decl, body = V.entry(text, k, prefix="REPLACE_OR_CREATE:")
        bm_stmt = V.sub(body, "building_modifiers")
        assert bm_stmt is not None, f"{k}: grey_usu no longer has building_modifiers"
        bm_inner = bm_stmt[bm_stmt.index("{") + 1:-1]
        assert V.sub(bm_inner, "unscaled") is None, \
            f"{k}: grey_usu already has an unscaled sub-block -- check by hand, do not blindly append"

        new_bm_inner = bm_inner.rstrip() + "\n\tunscaled = {\n\t\tbuilding_job_attractiveness_mult = 2\n\t}\n"
        new_bm = "{" + new_bm_inner + "}"
        new_body = V.replace_sub(body, "building_modifiers", new_bm)

        blocks.append(
            f"# {k} -- grey_usu's REPLACE_OR_CREATE:, own numbers kept verbatim,\n"
            f"# only building_modifiers.unscaled.building_job_attractiveness_mult = 2 restored\n"
            f"# (originally VC's; already restored against LLWA's own body in llwa+vc done --\n"
            f"# same field, same value, this time against grey_usu's later body).\n"
            f"REPLACE_OR_CREATE:{k} = {{{new_body}}}"
        )

    write("common/production_methods/zz_greys_llwa_rails.txt", "\n\n".join(blocks),
          "3 rail production methods, building_job_attractiveness_mult restored",
          "### grey_usu's REPLACE_OR_CREATE: on these three keeps its own numbers on every\n"
          "### field it touches -- this restores only the one field it never had:\n"
          "### building_modifiers.unscaled.building_job_attractiveness_mult = 2, originally\n"
          "### VC's, silently dropped the same way on every full-body rewrite since.\n"
          "### The other seven rail production methods are NOT here on purpose: grey_usu has\n"
          "### its own progressively-scaled state_market_access_price_impact design on all\n"
          "### seven (0.02..0.05) -- a genuine numeric dispute, not a silent loss. See the\n"
          "### plan, GR.16.")


# --------------------------------------------------------------------------
# 3. building_railway (station + line) and building_airport -- GR.9/16/17
# --------------------------------------------------------------------------

RAILWAY_FILE = os.path.join(USU, "common/buildings/~zzzzMoG_USU_railways.txt")
AIRPORT_FILE = os.path.join(USU, "common/buildings/zMoG_USU_MR_airports.txt")

STATION_GROUPS = ["pmg_gaudi_communication"]
LINE_GROUPS = ["LLWA_pmg_private_expansion", "pmg_market_liquidity", "pmg_private_ownership_railroad_stock"]
AIRPORT_GROUPS = ["LLWA_pmg_air_base", "LLWA_pmg_air_traffic", "LLWA_pmg_private_expansion",
                  "pmg_market_liquidity", "pmg_private_ownership_manufacture_stock"]


def _assert_missing(body: str, key: str, groups: list[str], source: str):
    pmg = V.sub(body, "production_method_groups")
    assert pmg is not None, f"{key}: {source} has no production_method_groups at all"
    for g in groups:
        assert g not in pmg, f"{key}: {source}'s production_method_groups already carries {g} -- nothing to restore"


def build_railway_and_airport():
    rail_text = V.read(RAILWAY_FILE)
    _decl, station_body = V.entry(rail_text, "building_railway", prefix="REPLACE_OR_CREATE:")
    _decl, line_body = V.entry(rail_text, "building_usu_railway_line", prefix="REPLACE_OR_CREATE:")
    _assert_missing(station_body, "building_railway", STATION_GROUPS, "grey_usu's station body")
    _assert_missing(line_body, "building_usu_railway_line", LINE_GROUPS, "grey_usu's line body")

    rail_blocks = [
        "# building_railway is now USU's railway STATION (an AI-subsidy mechanism --\n"
        "# see grey_usu's own comment \"Now the Railway Station\"), not the railway itself.\n"
        "# grey_usu's own file carries a commented-out TRY_INJECT: of exactly this group,\n"
        "# disabled over a same-mod REPLACE/INJECT ordering problem that does not apply to\n"
        "# a separate, later-loading file -- restoring the author's own intended fix.\n"
        "TRY_INJECT:building_railway = {\n"
        "\tproduction_method_groups = { pmg_gaudi_communication }\n"
        "}",
        "# building_usu_railway_line is the actual railway (USU's 2026-08-27 rework split\n"
        "# building_railway in two -- station above, line here). grey_usu has zero LLWA\n"
        "# awareness (no file in grey_usu mentions LLWA at all) and did not exist when\n"
        "# addon-LLWA's own merged building_railway (LLWA_pmg_private_expansion + E&F's two\n"
        "# groups) was built, so none of that survives the split. Decided with the user\n"
        "# 2026-08-27: the line gets the whole private-ownership economy, the station gets\n"
        "# only the communication group above. Same building GR.15 already proposes\n"
        "# railroad_stock for -- this closes that part of GR.15 too.\n"
        "TRY_INJECT:building_usu_railway_line = {\n"
        "\tproduction_method_groups = {\n"
        "\t\tLLWA_pmg_private_expansion\n"
        "\t\tpmg_market_liquidity\n"
        "\t\tpmg_private_ownership_railroad_stock\n"
        "\t}\n"
        "}",
    ]
    write("common/buildings/zz_greys_llwa_railway.txt", "\n\n".join(rail_blocks),
          "building_railway (station) + building_usu_railway_line (the line), split restored",
          "### GR.9/GR.16/GR.17 all converge on this one pair of records -- see the long\n"
          "### note at the top of this generator for the full 2026-08-27 railway-split\n"
          "### story and the decision behind the station/line split below.")

    air_text = V.read(AIRPORT_FILE)
    _decl, airport_body = V.entry(air_text, "building_airport", prefix="TRY_REPLACE:")
    _assert_missing(airport_body, "building_airport", AIRPORT_GROUPS, "grey_usu's body")

    air_block = (
        "# grey_usu's TRY_REPLACE: (zMoG_USU_MR_airports.txt) is a full body pre-dating\n"
        "# LLWA, silently dropping addon-LLWA's merged production_method_groups: LLWA's own\n"
        "# three (air_base/air_traffic/private_expansion) plus E&F x Morgenroete's two\n"
        "# (market_liquidity/private_ownership_manufacture_stock -- manufacture_stock here,\n"
        "# not railroad_stock: this is the E&F x Morgenroete pairing, matching how E&F\n"
        "# already treats building_power_plant). No split, no dispute -- restored additively.\n"
        "TRY_INJECT:building_airport = {\n"
        "\tproduction_method_groups = {\n"
        "\t\tLLWA_pmg_air_base\n"
        "\t\tLLWA_pmg_air_traffic\n"
        "\t\tLLWA_pmg_private_expansion\n"
        "\t\tpmg_market_liquidity\n"
        "\t\tpmg_private_ownership_manufacture_stock\n"
        "\t}\n"
        "}"
    )
    write("common/buildings/zz_greys_llwa_airport.txt", air_block,
          "building_airport, addon-LLWA's production_method_groups restored",
          "### grey_usu's TRY_REPLACE: keeps its own three groups (pmg_base_building_airport,\n"
          "### pmg_cargo_airport, pmg_tourism_airport) -- this adds back addon-LLWA's five\n"
          "### without touching any of grey_usu's own. See the generator's module docstring,\n"
          "### section 3, for the full GR.9/16/17 story.")


def self_check() -> int:
    problems = 0
    for rel in sorted(WRITTEN):
        pass
    n_files = 0
    n_keys = 0
    for dp, _dn, fs in os.walk(OUT):
        for fn in sorted(fs):
            if not fn.endswith(".txt"):
                continue
            p = os.path.join(dp, fn)
            text = V.read(p)
            n_files += 1
            keys = V.sub_names(text) if False else None
            # top-level key count: count top-level '<PREFIX>:name = {' occurrences
            import re as _re
            n_keys += len(_re.findall(r'(?m)^(?:[A-Z_]+:)?[A-Za-z0-9_]+\s*=\s*\{', text))
            if V.brace_balance(text) != 0:
                print(f"  PROBLEM: {p}: brace imbalance"); problems += 1
            with open(p, 'rb') as f:
                raw = f.read()
            has_bom = raw[:3] == b'\xef\xbb\xbf'
            non_ascii = any(ord(c) > 127 for line in text.split('\n') for c in line.split('#')[0])
            if non_ascii and not has_bom:
                print(f"  PROBLEM: {p}: has non-ASCII but no BOM"); problems += 1
            if re.search(r'\b([A-Z_]+):\1:', text):
                print(f"  PROBLEM: {p}: doubled prefix"); problems += 1
            if re.search(r'\b(\w+)\s*=\s*\1\s*=\s*\{', text):
                print(f"  PROBLEM: {p}: doubled field name (a = a = {{)"); problems += 1
    print(f"self-check: {n_files} files, {n_keys} top-level keys, {problems} problems")
    return problems


def main() -> int:
    global CHECK_ONLY
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    CHECK_ONLY = args.check

    steps = (("companies", build_companies), ("rails", build_rails),
              ("railway+airport", build_railway_and_airport))
    for name, fn in steps:
        print(f"-- {name}")
        fn()

    if CHECK_ONLY:
        return 1 if WRITTEN.get("__drift__") else 0
    return self_check()


if __name__ == "__main__":
    sys.exit(main())
