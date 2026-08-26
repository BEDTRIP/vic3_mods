# -*- coding: utf-8 -*-
"""regen_hc_vc.py -- builds the (partial, so far) HC+GoB+MoH x VC compatch in
`_HC+GoB+MoH/hc+vc wip`.

The pair: analysis is `conflicts_hcgobmoh_vs_vc_report.md` in this same folder --
39 shared keys, 8 shared paths. This generator covers everything that report
closed as either mechanical (no editorial decision needed) or decided by a human
via `hc_vc_character_traits.xlsx`. It does NOT yet cover the five items the
report flagged as large, not-started content merges: ig_landowners,
ig_rural_folk, chi - china.txt, tur - ottoman empire.txt, usa - usa.txt. Folder
stays "wip", not "done", until those are closed too.

What's built here:
  * common/character_templates/zz_hcvc_character_templates.txt -- 15 characters,
    HC's body kept (commander_usage/executive_usage/on_created untouched),
    traits swapped for the human decision recorded in
    hc_vc_character_traits.xlsx (sheet "Трейты", column M, itself a formula
    over column K "РЕШЕНИЕ"). chi_daoguang_template is NOT in this file: MoH's
    INJECT: on_created lands on VC's REPLACE_OR_CREATE: body untouched, already
    confirmed noneed in the pair report.
  * common/dna_data/ecchi_usa_polk.txt -- HC's body plus VC's one extra gene
    (coats), the two are otherwise byte-identical.
  * common/dynamic_country_names/{ahu,mch,xin,chi}... -- MoH's REPLACE: body
    (owns the path) with VC's entries appended. Zero name collisions on AHU/MCH/
    XIN. CHI has three shared names (dyn_c_great_qing, dyn_c_empire_of_china,
    dyn_c_peoples_republic_of_china) -- kept from both sides regardless, the
    same way MoH's own MCH list already carries a duplicate name
    (dyn_c_dongbei_army twice) with different triggers. Not a bug, just how this
    system does alternates.
  * common/flag_definitions/zz_hcvc_flag_definitions_chi.txt -- MoH's 19-entry
    REPLACE: body (owns the path) plus VC's one truly new entry
    (CHI_dictatorship). Two of VC's other entries collide by `coa` with
    content that genuinely differs (CHI_minguo, CHI_republic): both keep
    MoH's version, on purpose -- see EDITORIAL_NOTES below, this is a real
    decision, not a mechanical one.
  * common/scripted_buttons/zz_hcvc_opium_buttons.txt -- MoH's body (richer:
    China-specific Opium War victory branching, an extra trigger_event) with
    VC's own journal-entry gate (common_opium_war) OR'd into visible/possible
    alongside MoH's (je_opium_obsession/je_opium_communism), VC's
    has_law_or_variant fix adopted over MoH's stale has_law, and VC's
    allow_ban_opium_timer escape kept in ban_opium_button's tooltip gate.

Usage:
    python3 regen_hc_vc.py            # write the files
    python3 regen_hc_vc.py --check    # report only, exit 1 if sources drifted
"""

from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vic3lib import read, write, entry, sub, sub_names, sub_span, replace_sub, brace_balance
import regen_addon1 as ra1

HERE = os.path.dirname(os.path.abspath(__file__))
res = lambda p: os.path.normpath(os.path.join(HERE, p))

HC = res("../../vic3_mods_out/for addon/hailcolumbia")
MOH = res("../../vic3_mods_out/for addon/mandateofheaven")
VC = res("../../vic3_mods_out/VC")
OUT = res("../_HC+GoB+MoH/hc+vc done")
GRID = res("../_HC+GoB+MoH/hc+vc done/hc_vc_character_traits.xlsx")

# regen_addon1.py's own root layout (its `P` class) so its base-body builders
# (_ig_landowners_body, _ig_rural_folk_body, _jacksonian_tgr_body) can be
# reused verbatim -- guarantees this compatch's non-VC base byte-matches what
# addon1 actually ships, since both come from the same function call.
ROOT = res("../../vic3_mods_out")
ROOT_OUT = res("..")
_p = ra1.P(ROOT)

# The VC x TGR compatch's own output -- Jacksonian Democrat needs VC's law
# stances already reconciled against TGR's ideology set, which only that
# compatch's generator (regen_vc_tgr.py) computes.
VC_TGR_STANCES = os.path.join(ROOT_OUT, "_vc", "tgr+vc done", "common", "ideologies",
                               "zz_vc_tgr_stances_on_vc_laws.txt")

DATE = "2026-08-26"
NOTES: list[str] = []


def note(s):
    NOTES.append(s)


def need(cond, msg):
    if not cond:
        raise SystemExit("SOURCE DRIFT: " + msg)


def banner(*lines):
    return "\n".join("### " + l if l else "###" for l in lines) + "\n\n"


def vc_tag_delete_only(filename):
    """Every file in this compatch exists ONLY to carry Victorian Century
    content -- no other compatch in the addon needs it. Tagged so a player who
    wants to drop VC can find and delete these files by skimming the top line,
    without reading the rest of the banner."""
    return banner(
        '=== VC-ONLY FILE === delete "%s" to play without' % filename,
        'Victorian Century. This whole compatch is the VC layer -- deleting',
        'this file changes nothing else. To drop VC entirely, delete this',
        'whole compatch folder (_HC+GoB+MoH/hc+vc done) and nothing else --',
        'addon1 and the other pair compatches never reference it.')


def _merge_vc_into_ig(van_body, body, vc_body, names, label):
    """Layer Victorian Century's REPLACE_OR_CREATE: rework of an interest group
    on top of an already-built (HC[+TGR][+MoH]) body, one named sub-block at a
    time, three-way against vanilla -- so a real overlap stops the build
    instead of one side's edit silently winning. Reuses regen_addon1's own
    merge3/resolve policy so the conflict semantics match the base build
    exactly."""
    for nm in names:
        merged = ra1.merge3(sub(van_body, nm), sub(body, nm), sub(vc_body, nm),
                             "%s/%s x VC" % (label, nm), resolve=ra1._ig_resolve)
        body = replace_sub(body, nm, merged)
    return body


# =============================================================================
#  1. character_templates
# =============================================================================
CHAR_KEYS_COUNTRY_USA = [
    "USA_william_cramp", "USA_winfield_scott", "usa_admiral_dewey", "usa_admiral_perry",
    "usa_general_grant", "usa_general_jackson", "usa_general_jesup", "usa_general_longstreet",
    "usa_general_sherman", "usa_lincoln_character_template",
]
CHAR_KEYS_HISTORICAL = [
    "usa_admiral_porter", "usa_admiral_sampson", "usa_admiral_sigsbee",
    "usa_general_bell", "usa_general_miles",
]


def read_grid_decisions():
    import openpyxl
    wb = openpyxl.load_workbook(GRID, data_only=True)
    ws = wb["Трейты"]
    out = {}
    for row in ws.iter_rows(min_row=2, max_row=16, values_only=True):
        key, final = row[0], row[12]
        need(key, "hc_vc_character_traits.xlsx: blank key in the Трейты sheet")
        need(final and str(final).strip(), "%s: column M (финальный список) is empty -- open the grid in Excel and let it recalculate, then re-save" % key)
        traits = [t.strip() for t in str(final).split(",") if t.strip()]
        need(traits, "%s: could not parse any traits out of %r" % (key, final))
        out[key] = traits
    expected = set(CHAR_KEYS_COUNTRY_USA + CHAR_KEYS_HISTORICAL)
    need(set(out) == expected,
         "hc_vc_character_traits.xlsx now lists a different key set than the generator expects: "
         "grid has %s, generator wants %s" % (sorted(out), sorted(expected)))
    return out


def _traits_block(traits):
    inner = "\n\t\t".join(traits)
    return "{\n\t\t" + inner + "\n\t}"


def _with_traits(body, traits):
    new_block = _traits_block(traits)
    if sub(body, "traits") is not None:
        return replace_sub(body, "traits", new_block)
    # No traits sub-block at all (usa_admiral_porter/sampson/sigsbee) -- add one.
    return "\n\ttraits = " + new_block + "\n" + body


def build_character_templates():
    decisions = read_grid_decisions()
    country_usa = read(os.path.join(HC, "common/character_templates/country_usa.txt"))
    historical = read(os.path.join(HC, "common/character_templates/historical_commanders_usa.txt"))

    pieces = []
    for key in CHAR_KEYS_COUNTRY_USA:
        decl, body = entry(country_usa, key)
        pieces.append((key, _with_traits(body, decisions[key])))
    for key in CHAR_KEYS_HISTORICAL:
        decl, body = entry(historical, key)
        pieces.append((key, _with_traits(body, decisions[key])))
    note("character_templates: 15 keys, HC body kept, traits swapped per hc_vc_character_traits.xlsx")

    pieces_out = []
    for key, body in pieces:
        pieces_out.append("REPLACE_OR_CREATE:%s = {%s}\n" % (key, body))
    text = "\n".join(pieces_out)
    return vc_tag_delete_only("zz_hcvc_character_templates.txt") + banner(
        "ComPatch HC+GoB+MoH x Victorian Century -- 15 character_templates",
        "",
        "HC and VC both rewrite these 15 keys independently (10 are vanilla",
        "commander/executive templates, 5 are HC's own with no vanilla ancestor).",
        "Traits chosen per-character in hc_vc_character_traits.xlsx (sheet",
        "\"Трейты\") -- see that file's \"заметка\" column for the reasoning behind",
        "each pick. Everything except traits is HC's body, unchanged: commander_usage",
        "/ executive_usage / interest_group_leader_usage weights and on_created hooks",
        "are HC's balance, not decided by this grid.",
        "",
        "chi_daoguang_template is NOT here on purpose -- MoH only INJECT:s on_created",
        "into it, VC's REPLACE_OR_CREATE: body (traits only) survives untouched.",
        "Confirmed noneed in conflicts_hcgobmoh_vs_vc_report.md.",
        "",
        "!! MAINTENANCE !! Re-run this generator after hc_vc_character_traits.xlsx",
        "changes, or after HC/VC update these templates -- do not hand-edit the",
        "traits lists here.") + text


# =============================================================================
#  2. DNA -- ecchi_usa_polk.txt
# =============================================================================
def build_polk_dna():
    hc = read(os.path.join(HC, "common/dna_data/ecchi_usa_polk.txt"))
    vc = read(os.path.join(VC, "common/dna_data/ecchi_usa_polk.txt"))
    hc_lines = hc.split("\n")
    vc_lines = vc.split("\n")
    need(len(hc_lines) == len(vc_lines),
         "ecchi_usa_polk.txt: HC and VC no longer have the same line count -- re-diff by hand")
    diffs = [i for i, (a, b) in enumerate(zip(hc_lines, vc_lines)) if a != b]
    need(diffs == [111],
         "ecchi_usa_polk.txt: HC and VC now differ on lines %s, not just the coats gene "
         "(0-indexed line 111) -- re-diff by hand" % diffs)
    need("coats=" in vc_lines[111] and "coats=" not in hc_lines[111],
         "ecchi_usa_polk.txt: line 111 no longer looks like the missing coats gene")
    merged = hc_lines[:]
    merged[111] = vc_lines[111]
    decl, body = entry("\n".join(merged), "ecchi_dna_james_k_polk")
    note("ecchi_usa_polk.txt: HC body + VC's one extra gene (coats)")
    return vc_tag_delete_only("ecchi_usa_polk.txt") + banner(
        "ComPatch HC+GoB+MoH x Victorian Century -- ecchi_usa_polk.txt",
        "",
        "HC and VC ship the same 122-line DNA body at the same path (common",
        "external source), byte-identical but for one line: VC carries an extra",
        "gene, coats = { \"american_uniform_coats\" 255 \"all_coats\" 0 }, that HC",
        "does not. HC loads later and wins the path outright, so Polk quietly loses",
        "that gene with both mods installed.",
        "",
        "Below: HC's body with VC's one extra line restored.") + \
        "REPLACE_OR_CREATE:ecchi_dna_james_k_polk = {%s}\n" % body


# =============================================================================
#  3. dynamic_country_names
# =============================================================================
DCN_TAGS = ["AHU", "MCH", "XIN", "CHI"]
DCN_MOH_PREFIX = "REPLACE:"
DCN_VC_PREFIX = {"AHU": "REPLACE_OR_CREATE:", "MCH": "REPLACE_OR_CREATE:",
                 "XIN": "REPLACE_OR_CREATE:", "CHI": "TRY_INJECT:"}


def _append_entries(moh_body, vc_body):
    """MoH's body (statements only, no outer braces) plus VC's statements
    appended -- both sides are just repeated `dynamic_country_name = { ... }`
    blocks, a plain additive list, so concatenation is the whole merge."""
    return moh_body.rstrip() + "\n" + vc_body.strip() + "\n"


def build_dynamic_country_names():
    moh = read(os.path.join(MOH, "common/dynamic_country_names/moh_dynamic_country_names.txt"))
    vc = read(os.path.join(VC, "common/dynamic_country_names/joi_dynamic_country_names.txt"))
    parts = []
    for tag in DCN_TAGS:
        mdecl, mbody = entry(moh, tag, prefix=DCN_MOH_PREFIX)
        vdecl, vbody = entry(vc, tag, prefix=DCN_VC_PREFIX[tag])
        merged = _append_entries(mbody, vbody)
        parts.append("REPLACE_OR_CREATE:%s = {\n%s}\n" % (tag, merged))
    note("dynamic_country_names: AHU/MCH/XIN/CHI, MoH's list + VC's list appended (plain additive container)")
    text = "\n".join(parts)
    return vc_tag_delete_only("zz_hcvc_dynamic_country_names.txt") + banner(
        "ComPatch HC+GoB+MoH x Victorian Century -- dynamic_country_names",
        "",
        "AHU, MCH, XIN, CHI: MoH REPLACE:s the whole entry (owns the path), VC",
        "REPLACE_OR_CREATE:s (or, for CHI, TRY_INJECT:s) its own -- either way MoH",
        "wins outright and VC's alternate names for these four tags vanish.",
        "",
        "dynamic_country_name is a plain repeated list, not a keyed record: the two",
        "sides' entries never share an id (AHU/MCH/XIN) or, on CHI, share three ids",
        "(dyn_c_great_qing, dyn_c_empire_of_china, dyn_c_peoples_republic_of_china)",
        "with different triggers -- which is not a conflict, it's how this file",
        "already works: MoH's own MCH list carries dyn_c_dongbei_army twice with two",
        "different triggers. Below: MoH's list, VC's list appended after it.") + text


# =============================================================================
#  4. flag_definitions CHI
# =============================================================================
EDITORIAL_NOTES = {
    "CHI_minguo": (
        "MoH: priority 5, trigger coa_def_republic_flag_trigger (MoH's own shared "
        "republic trigger). VC: priority 3000, trigger coa_def_chi_minguo_trigger "
        "(VC's own, tied to VC's parallel Chinese civil-war system). Kept MoH's: "
        "MoH's history/journal chain is what actually runs China's politics in this "
        "composition (see chi - china.txt), VC's trigger is written for VC's own "
        "chain and is not established to fire under MoH's."),
    "CHI_republic": (
        "MoH: subject_canton CHI_anguo, priority 5, excludes on MoH's own "
        "china_shatters variable. VC: subject_canton CHI_republic, priority 20, "
        "excludes on VC's own northern_expedition_name_var / "
        "chinese_revolution_republic_name_var. Same reasoning as CHI_minguo: kept "
        "MoH's, VC's exclusion variables belong to VC's own parallel chain."),
}


def build_flag_definitions():
    moh = read(os.path.join(MOH, "common/flag_definitions/moh_flag_definitions.txt"))
    vc = read(os.path.join(VC, "common/flag_definitions/joi_flag_definitions.txt"))
    mdecl, mbody = entry(moh, "CHI", prefix="REPLACE:")
    vdecl, vbody = entry(vc, "CHI", prefix="REPLACE_OR_CREATE:")

    def split_entries(body):
        chunks = re.split(r"(?=flag_definition\s*=\s*\{)", body)
        out = {}
        order = []
        for c in chunks:
            m = re.search(r"coa\s*=\s*([A-Za-z0-9_]+)", c)
            if m and c.strip():
                out[m.group(1)] = c.rstrip()
                order.append(m.group(1))
        return out, order

    m_entries, m_order = split_entries(mbody)
    v_entries, v_order = split_entries(vbody)
    overlap = set(m_entries) & set(v_entries)
    need(overlap == set(EDITORIAL_NOTES) | {"CHI", "CHI_absolute_monarchy", "CHI_communist", "CHI_han_empire", "CHI_theocracy"},
         "flag_definitions CHI: overlap between MoH and VC changed (%s) -- re-check by hand, "
         "editorial notes may be stale" % sorted(overlap))
    new_from_vc = [k for k in v_order if k not in m_entries]
    need(new_from_vc == ["CHI_dictatorship"],
         "flag_definitions CHI: VC's truly-new entries changed (%s), was just CHI_dictatorship" % new_from_vc)

    body = mbody.rstrip() + "\n\t" + v_entries["CHI_dictatorship"].strip() + "\n"
    note("flag_definitions CHI: MoH's 19 entries + VC's 1 new one (CHI_dictatorship); "
         "CHI_minguo/CHI_republic collide in content, kept MoH's (see EDITORIAL_NOTES)")
    return vc_tag_delete_only("zz_hcvc_flag_definitions_chi.txt") + banner(
        "ComPatch HC+GoB+MoH x Victorian Century -- common/flag_definitions CHI",
        "",
        "MoH REPLACE:s the whole CHI flag list (19 entries), VC REPLACE_OR_CREATE:s",
        "its own (8 entries) -- MoH wins the path outright. Seven of VC's eight",
        "share a `coa` id with one of MoH's: five are functionally identical or a",
        "strict subset (CHI, CHI_absolute_monarchy, CHI_communist, CHI_han_empire,",
        "CHI_theocracy -- kept MoH's, no content lost). Two genuinely differ",
        "(CHI_minguo, CHI_republic) -- both sides wrote real content, this is a",
        "decision, not a merge:",
        "  * CHI_minguo -- " + EDITORIAL_NOTES["CHI_minguo"],
        "  * CHI_republic -- " + EDITORIAL_NOTES["CHI_republic"],
        "",
        "Below: MoH's 19 entries plus VC's one truly new one, CHI_dictatorship.") + \
        "REPLACE_OR_CREATE:CHI = {\n%s}\n" % body


# =============================================================================
#  5. scripted_buttons -- opium
# =============================================================================
def build_opium_buttons():
    moh = read(os.path.join(MOH, "common/scripted_buttons/moh_china_buttons.txt"))
    vc = read(os.path.join(VC, "common/scripted_buttons/joi_china_buttons.txt"))

    # -- ban_opium_button ------------------------------------------------
    mdecl, mbody = entry(moh, "ban_opium_button", prefix="REPLACE:")
    vdecl, vbody = entry(vc, "ban_opium_button", prefix="REPLACE:")

    m_visible = sub(mbody, "visible")
    need("je_opium_communism" in m_visible and "je_opium_obsession" in m_visible,
         "ban_opium_button: MoH's visible no longer names both journal entries")
    v_visible = sub(vbody, "visible")
    need("common_opium_war" in v_visible, "ban_opium_button: VC's visible no longer names common_opium_war")
    new_visible = m_visible.replace(
        "has_journal_entry = je_opium_communism",
        "has_journal_entry = je_opium_communism\n\t\t\thas_journal_entry = common_opium_war")
    need(new_visible != m_visible, "ban_opium_button: visible OR-splice was a no-op -- indentation drifted, check by hand")

    m_possible = sub(mbody, "possible")
    need("has_law = law_type:law_free_trade" in m_possible,
         "ban_opium_button: MoH's possible no longer has the strict has_law free-trade check")
    need("has_journal_entry = je_opium_communism" in m_possible,
         "ban_opium_button: MoH's possible no longer names je_opium_communism")
    v_possible = sub(vbody, "possible")
    need(v_possible is not None and "has_variable = allow_ban_opium_timer" in v_possible,
         "ban_opium_button: VC's possible no longer has the allow_ban_opium_timer escape")
    step1 = m_possible.replace(
        "has_journal_entry = je_opium_communism",
        "has_journal_entry = je_opium_communism\n\t\t\thas_journal_entry = common_opium_war")
    need(step1 != m_possible, "ban_opium_button: possible OR-splice was a no-op -- indentation drifted, check by hand")
    step2 = step1.replace(
        "has_law = law_type:law_free_trade", "has_law_or_variant = law_type:law_free_trade")
    need(step2 != step1, "ban_opium_button: has_law_or_variant swap was a no-op -- check by hand")
    step3 = re.sub(
        r"NOT = \{\s*\n\s*has_variable = lost_opium_wars\s*\n\s*\}",
        "OR = {\n\t\t\t\tNOT = { has_variable = lost_opium_wars }\n\t\t\t\thas_variable = allow_ban_opium_timer\n\t\t\t}",
        step2)
    need(step3 != step2, "ban_opium_button: allow_ban_opium_timer splice was a no-op -- indentation drifted, check by hand")
    new_possible = step3

    ban_body = replace_sub(mbody, "visible", new_visible)
    ban_body = replace_sub(ban_body, "possible", new_possible)

    # -- unban_opium_button ------------------------------------------------
    mdecl2, mbody2 = entry(moh, "unban_opium_button", prefix="REPLACE:")
    vdecl2, vbody2 = entry(vc, "unban_opium_button", prefix="REPLACE:")
    m_visible2 = sub(mbody2, "visible")
    need("je_opium_communism" in m_visible2, "unban_opium_button: MoH's visible no longer names je_opium_communism")
    v_visible2 = sub(vbody2, "visible")
    need("common_opium_war" in v_visible2, "unban_opium_button: VC's visible no longer names common_opium_war")
    new_visible2 = m_visible2.replace(
        "has_journal_entry = je_opium_communism",
        "has_journal_entry = je_opium_communism\n\t\t\thas_journal_entry = common_opium_war")
    need(new_visible2 != m_visible2, "unban_opium_button: visible OR-splice was a no-op -- indentation drifted, check by hand")
    unban_body = replace_sub(mbody2, "visible", new_visible2)

    note("scripted_buttons: ban/unban_opium_button, MoH's body + VC's common_opium_war journal gate "
         "OR'd in, VC's has_law_or_variant fix and allow_ban_opium_timer escape adopted")
    return vc_tag_delete_only("zz_hcvc_opium_buttons.txt") + banner(
        "ComPatch HC+GoB+MoH x Victorian Century -- ban_opium_button / unban_opium_button",
        "",
        "Both mods REPLACE: the same two vanilla buttons; MoH loads later and wins",
        "outright. MoH's body is the richer one -- China-specific Opium War",
        "victory-condition branching in `possible`, an extra trigger_event in",
        "`effect` -- so it stays the base. Three things of VC's are folded in:",
        "  * visible/possible gate on VC's own journal entry (common_opium_war) too,",
        "    alongside MoH's (je_opium_obsession / je_opium_communism) -- OR, so this",
        "    only widens when the button can appear, never narrows it;",
        "  * VC's has_law_or_variant (the correct 1.13 form) replaces MoH's stale",
        "    has_law on the free-trade check -- same fix already documented for",
        "    moh_rural_folk.txt in HC.2;",
        "  * VC's allow_ban_opium_timer escape kept alongside MoH's",
        "    lost_opium_wars check in ban_opium_button's tooltip gate.",
        "",
        "effect and ai_chance are MoH's, unchanged -- VC's are a strict subset",
        "(unban_opium_button) or missing the China-specific branch entirely",
        "(ban_opium_button).") + \
        "REPLACE:ban_opium_button = {%s}\n\nREPLACE:unban_opium_button = {%s}\n" % (ban_body, unban_body)


# =============================================================================
#  6. ig_landowners  (REPLACE:s addon1's own hc+tgr output -- load after addon1)
# =============================================================================
def build_ig_landowners():
    van = read(os.path.join(_p.van, "common/interest_groups/00_landowners.txt"))
    tgr = read(os.path.join(_p.tgr, "common/interest_groups/TGR_POLITICS_landowners.txt"))
    hc = read(os.path.join(_p.hc, "common/interest_groups/00_landowners.txt"))
    vc = read(os.path.join(VC, "common/interest_groups/joi_landowners.txt"))

    v = entry(van, "ig_landowners")[1]
    vc_body = entry(vc, "ig_landowners", prefix="REPLACE_OR_CREATE:")[1]

    base_body = ra1._ig_landowners_body(van, tgr, hc)
    body = _merge_vc_into_ig(v, base_body, vc_body, ("on_enable", "pop_potential", "pop_weight"),
                              "ig_landowners")
    oe, pp, pw = sub(body, "on_enable"), sub(body, "pop_potential"), sub(body, "pop_weight")
    need("ig_trait_owner_of_land" in oe, "VC no longer reworks ig_landowners on_enable (Russian nobles trait missing)")
    need("usfp_country_is_american" in oe and "cu:yankee" not in oe,
         "ig_landowners on_enable: HC's usfp_country_is_american swap was lost merging in VC")
    need("is_pop_type = capitalists" in pp and "is_pop_type = bureaucrats" in pp and "is_pop_type = peasants" in pp,
         "VC no longer widens ig_landowners pop_potential to capitalists/bureaucrats/peasants")
    need("POP_PRUSSIAN_NOBLES_CAP" in pw, "VC no longer adds its Prussian-nobles pop_weight rules to ig_landowners")
    need("0.030" in pw and "No more Southern Planters" in pw,
         "ig_landowners pop_weight lost TGR's multiplier or HC's Southern-planters rule merging in VC")
    body = replace_sub(body, "pop_weight", ra1._safe_scope(pw, "ig_landowners/pop_weight"))

    note("ig_landowners: HC+TGR base (regen_addon1._ig_landowners_body) + VC's on_enable/"
         "pop_potential/pop_weight rework merged in on top, three-way against vanilla per sub-block")
    return vc_tag_delete_only("zz_hcvc_ig_landowners.txt") + banner(
        "ComPatch HC+GoB+MoH x The Great Revision x Victorian Century -- ig_landowners",
        "",
        "REPLACE:s the same path addon1's hc+tgr compatch already owns "
        "(_HC+GoB+MoH/hc+tgr done/common/interest_groups/zz_hct_ig_landowners.txt) -- "
        "this compatch must load after addon1, and after Victorian Century.",
        "",
        "TGR reworks this interest group from TGR_POLITICS_landowners.txt with",
        "REPLACE_OR_CREATE:. Its one real change (LEADER_POPULARITY 0.0025 -> 0.030 in",
        "pop_weight) is already merged into HC's body by regen_addon1.py -- this file",
        "imports that exact base (regen_addon1._ig_landowners_body) rather than",
        "recomputing it, so the two can never drift apart.",
        "",
        "What Victorian Century changes, in three sub-blocks: on_enable gets",
        "nation-specific noble trait sets for Russia, Japan, Prussia, Austria, China,",
        "Turkey and Spain (in place of vanilla's shared noble_privileges/family_ties",
        "pair), a German-nobles ideology switch, and reworked Prussian/Turkish/British",
        "blocks; pop_potential widens from {aristocrats, clergymen, officers, farmers}",
        "to also allow capitalists, bureaucrats and peasants; pop_weight adds weight",
        "rules for Prussian capitalists/farmers/peasants \"joining the Junkers\", a",
        "European (non-French) freeman bonus, and a Chinese-officer bonus.",
        "",
        "Merged below: the HC+TGR base with VC's rework of on_enable/pop_potential/",
        "pop_weight folded in on top, each sub-block three-way against vanilla, so a",
        "future edit by any of the three authors conflicts loudly instead of being",
        "dropped. VC does not touch the American-culture branch in on_enable, so HC's",
        "usfp_country_is_american swap survives untouched; VC does not touch",
        "pop_potential's vanilla types, so its three new ones are a pure addition; VC",
        "does not touch farmers/peasants/aristocrats/clergymen/officers in pop_weight,",
        "so TGR's multiplier and HC's Southern-planters rule both survive untouched",
        "next to VC's new rules.",
        "",
        "VC's own `scope:interest_group ?= {` -> `= {` downgrade in the same",
        "LEADER_POPULARITY block is not carried, same reasoning as the HC+TGR base --",
        "restored to `?=` throughout.",
        "",
        "VARIANTS: this whole compatch is the VC layer -- without VC, do not install",
        "this file, addon1's own hc+tgr output already stands alone.") + \
        "REPLACE:ig_landowners = {" + body + "}\n"


# =============================================================================
#  7. ig_rural_folk  (same load-order note as ig_landowners)
# =============================================================================
def build_ig_rural_folk():
    van = read(os.path.join(_p.van, "common/interest_groups/00_rural_folk.txt"))
    tgr = read(os.path.join(_p.tgr, "common/interest_groups/TGR_POLITICS_rural_folk.txt"))
    hc = read(os.path.join(_p.hc, "common/interest_groups/00_rural_folk.txt"))
    moh = read(os.path.join(_p.moh, "common/interest_groups/moh_rural_folk.txt"))
    vc = read(os.path.join(VC, "common/interest_groups/joi_rural_folk.txt"))

    v = entry(van, "ig_rural_folk")[1]
    vc_body = entry(vc, "ig_rural_folk", prefix="REPLACE_OR_CREATE:")[1]

    base_body = ra1._ig_rural_folk_body(van, tgr, hc, moh)
    body = _merge_vc_into_ig(v, base_body, vc_body, ("on_enable", "pop_potential", "pop_weight"),
                              "ig_rural_folk")
    oe, pp, pw = sub(body, "on_enable"), sub(body, "pop_potential"), sub(body, "pop_weight")
    need("ideology_agrarian_russian" in oe and "ideology_british_tory_conservatism_old" in oe
         and "ideology_indian_farmer_sovereignist" in oe,
         "VC no longer adds its three ideology-switch blocks to ig_rural_folk on_enable")
    need("usfp_country_is_american" in oe, "HC's Jeffersonian block was lost merging VC into ig_rural_folk on_enable")
    need("Nongmin" in oe, "MoH's Nongmin rename was lost merging VC into ig_rural_folk on_enable")
    need("exists = c:CHI" in pp, "VC no longer adds its China-officer clause to ig_rural_folk pop_potential")
    need("cu:usfp_american_indian" in pp, "HC's American-culture exemption was lost merging VC into ig_rural_folk pop_potential")
    need(pw.count("POP_CHINESE_OFFICER") == 2, "VC no longer adds its two Chinese-officer pop_weight rules to ig_rural_folk")
    need("value = 250" in pw and "value = 150" in pw, "ig_rural_folk pop_weight lost TGR's farmer/peasant numbers merging in VC")
    body = replace_sub(body, "pop_weight", ra1._safe_scope(pw, "ig_rural_folk/pop_weight"))

    note("ig_rural_folk: HC+TGR+MoH base (regen_addon1._ig_rural_folk_body) + VC's on_enable/"
         "pop_potential/pop_weight rework merged in on top, three-way against vanilla per sub-block")
    return vc_tag_delete_only("zz_hcvc_ig_rural_folk.txt") + banner(
        "ComPatch HC+GoB+MoH x The Great Revision x Victorian Century -- ig_rural_folk",
        "",
        "REPLACE:s the same path addon1's hc+tgr compatch already owns "
        "(_HC+GoB+MoH/hc+tgr done/common/interest_groups/zz_hct_ig_rural_folk.txt) -- "
        "this compatch must load after addon1, and after Victorian Century.",
        "",
        "TGR's real change here is three pop_weight numbers (POP_FARMERS 200 -> 250,",
        "POP_PEASANTS 200 -> 150, LEADER_POPULARITY 0.0025 -> 0.030); MoH INJECT:s",
        "ideology_moh_kmt and a Nongmin rename on top. Both are already merged into",
        "HC's body by regen_addon1.py -- this file imports that exact base",
        "(regen_addon1._ig_rural_folk_body) rather than recomputing it, so the two can",
        "never drift apart.",
        "",
        "What Victorian Century adds, in three sub-blocks: on_enable gets three",
        "ideology-switch blocks (Russia, Britain, the British East India Company);",
        "pop_potential gets a China-officers/soldiers clause; pop_weight gets two",
        "Chinese-officer bonuses (desc \"POP_CHINESE_OFFICER\" twice -- VC's own",
        "naming, not a bug introduced here).",
        "",
        "Merged below: the HC+TGR+MoH base with VC's rework of on_enable/",
        "pop_potential/pop_weight folded in on top, each sub-block three-way against",
        "vanilla. VC does not touch the American-culture/Nongmin branches in",
        "on_enable, so HC's and MoH's additions survive untouched; VC does not touch",
        "pop_potential's vanilla types or farmers/peasants/aristocrats in pop_weight,",
        "so TGR's numbers survive untouched next to VC's new rules.",
        "",
        "VC's own `scope:interest_group ?= {` -> `= {` downgrade is not carried, same",
        "reasoning as ig_landowners -- restored to `?=` throughout.",
        "",
        "VARIANTS: this whole compatch is the VC layer -- without VC, do not install",
        "this file, addon1's own hc+tgr output already stands alone.") + \
        "REPLACE:ig_rural_folk = {" + body + "}\n"


# =============================================================================
#  8. ideology_jacksonian_democrat  (needs the tgr+vc compatch's own output)
# =============================================================================
def build_jacksonian():
    vc = read(VC_TGR_STANCES)
    tgr_body = ra1._jacksonian_tgr_body(_p)
    # _jacksonian_tgr_body returns the REPLACE_OR_CREATE: body (with HC's block
    # plus TGR's two appended stances) as a bare `{...}`-free string ending in
    # a trailing "}\n"-less block -- re-open it the same way _jacksonian(p) does.
    h_merged = ra1._open_block("{" + tgr_body + "}")[1:-1]

    v = entry(vc, "ideology_jacksonian_democrat", prefix="INJECT:")[1]
    vc_groups = sub_names(v)
    need(vc_groups == ["lawgroup_taxation", "lawgroup_education_system", "lawgroup_economic_system",
                        "lawgroup_bureaucracy", "lawgroup_trade_policy", "lawgroup_citizenship",
                        "lawgroup_policing", "lawgroup_distribution_of_power"],
         "VC x TGR now injects %s into ideology_jacksonian_democrat -- update the merge" % vc_groups)

    # Two of VC's eight law groups are ones HC (via addon1's base) already has an
    # opinion on (bureaucracy, distribution_of_power) -- VC adds exactly one new
    # law to each, so that line is folded into the existing block instead of
    # creating a second block with the same key, which would be invalid. The
    # other six groups do not exist in the base body and are appended whole,
    # same as TGR's two in addon1.
    vc_merge = [nm for nm in vc_groups if sub(h_merged, nm) is not None]
    vc_new = [nm for nm in vc_groups if sub(h_merged, nm) is None]
    need(vc_merge == ["lawgroup_bureaucracy", "lawgroup_distribution_of_power"],
         "addon1's jacksonian base now overlaps VC on a different set of law groups (%s) "
         "-- update the merge" % vc_merge)

    for nm in vc_merge:
        extra = sub(v, nm)[1:-1].strip()
        need("\n" not in extra, "%s now carries more than one new VC law -- update the merge" % nm)
        new_block = ra1._open_block(sub(h_merged, nm)).rstrip() + "\n        " + extra + "\n    }"
        h_merged = replace_sub(h_merged, nm, new_block)

    vc_lines = ["\n\t# Victorian Century\n\t%s = %s" % (nm, sub(v, nm)) for nm in vc_new]
    tail = "\n".join(vc_lines)
    body = ra1._open_block("{" + h_merged + "}")[1:].rstrip() + "\n" + tail + "\n}"
    note("ideology_jacksonian_democrat: addon1's HC+TGR base (regen_addon1._jacksonian_tgr_body) "
         "+ VC laws folded into bureaucracy/distribution_of_power + VC's six new law-group "
         "stances appended")
    return vc_tag_delete_only("zz_hcvc_jacksonian_democrat.txt") + banner(
        "ComPatch HC+GoB+MoH x The Great Revision x Victorian Century -- ideology_jacksonian_democrat",
        "",
        "REPLACE_OR_CREATE:s the same entry addon1's hc+tgr compatch already owns "
        "(_HC+GoB+MoH/hc+tgr done/common/ideologies/zz_hct_jacksonian_democrat.txt) -- "
        "this compatch must load after addon1, and after Victorian Century.",
        "",
        "TGR's two law stances (lawgroup_election_system, lawgroup_legislative_process)",
        "are already appended to HC's body by regen_addon1.py -- this file imports that",
        "exact base (regen_addon1._jacksonian_tgr_body) rather than recomputing it.",
        "",
        "Victorian Century INJECT:s eight more law-group stances into this ideology:",
        "one new law apiece in lawgroup_bureaucracy and lawgroup_distribution_of_power",
        "(both of which the base already has an opinion on), plus six whole new groups",
        "for its own new laws (taxation, education_system, economic_system,",
        "trade_policy, citizenship, policing).",
        "",
        "Merged below: the base body, with VC's two new laws folded into the",
        "lawgroup_bureaucracy and lawgroup_distribution_of_power blocks it already had,",
        "then VC's six new stance blocks appended. None of these overlap TGR's two --",
        "the base names governance_principles, distribution_of_power, bureaucracy,",
        "colonization, land_reform, election_system and legislative_process; VC falls",
        "outside that list except for the two folded-in laws.",
        "",
        "Source for VC's stances: _vc/tgr+vc done/common/ideologies/",
        "zz_vc_tgr_stances_on_vc_laws.txt, itself generated by regen_vc_tgr.py against",
        "vc_tgr_ideology_grid.xlsx (sheet \"Обратно\", row ideology_jacksonian_democrat)",
        "-- needs that compatch already built, same as addon1 needs it.",
        "",
        "VARIANTS: this whole compatch is the VC layer -- without VC, do not install",
        "this file, addon1's own hc+tgr output already stands alone.") + \
        "REPLACE_OR_CREATE:ideology_jacksonian_democrat = {" + body[:-1] + "}\n"


# =============================================================================
#  9. tur - ottoman empire.txt  (REPLACE:s addon1's own hc+tgr output)
# =============================================================================
def _splice_vc_into_ottoman(win):
    """Add VC's law_madrasa activation and its two amendments into the base
    (GoB+TGR) body -- verified safe: law_madrasa's own prerequisite
    (law_millet_system) is already active in GoB's list, and both amendments
    target law groups GoB never touches, whose active law (law_monarchy,
    law_land_based_taxation) is already active in every version of this file."""
    anchor1 = "\t\tactivate_law = law_type:law_migration_controls\n"
    need(win.count(anchor1) == 1,
         "ottoman: GoB's law_migration_controls line moved or duplicated -- fix the VC splice anchor")
    win = win.replace(anchor1, anchor1 + "\t\tactivate_law = law_type:law_madrasa   # Victorian Century\n", 1)

    anchor2 = "\t\t# The Sick Man of Europe\n"
    need(win.count(anchor2) == 1, "ottoman: GoB's \"# The Sick Man of Europe\" comment moved -- fix the VC splice anchor")
    vc_block = (
        "\t\t# Victorian Century\n"
        "\t\tactive_law:lawgroup_taxation ?= {\n"
        "\t\t\tadd_amendment = {\n"
        "\t\t\t\ttype = amendment_salt_monopoly\n"
        "\t\t\t\tsponsor = prev.ig:ig_landowners\n"
        "\t\t\t}\n"
        "\t\t}\n"
        "\t\tactive_law:lawgroup_governance_principles ?= {\n"
        "\t\t\tadd_amendment = {\n"
        "\t\t\t\ttype = amendment_kanunname_law\n"
        "\t\t\t\tsponsor = prev.ig:ig_landowners\n"
        "\t\t\t}\n"
        "\t\t}\n\n"
    )
    return win.replace(anchor2, vc_block + anchor2, 1)


def _check_ottoman_laws_vs_vc():
    """Unlike China, most of what VC does to the Ottomans' file turns out to be
    a clean, verified-safe addition rather than a competing rework -- see the
    banner in build_ottoman for the reasoning. Asserted here so a future update
    to either file re-opens the decision instead of drifting under it."""
    gob = read(os.path.join(_p.gob, "common/history/countries/tur - ottoman empire.txt"))
    vc = read(os.path.join(VC, "common/history/countries/tur - ottoman empire.txt"))
    vc_laws = re.findall(r"activate_law = law_type:(\S+)", vc)
    need(vc_laws == ["law_monarchy", "law_autocracy", "law_millet_system", "law_subjecthood",
                      "law_traditionalism", "law_censorship", "law_land_based_taxation",
                      "law_slave_trade", "law_madrasa"],
         "VC tur - ottoman empire.txt activate_law list is now %s -- re-check the ottoman VC-vs-GoB write-up" % vc_laws)
    need("active_law:lawgroup_taxation" in vc and "amendment_salt_monopoly" in vc,
         "VC ottoman file no longer amends lawgroup_taxation with amendment_salt_monopoly")
    need("active_law:lawgroup_governance_principles" in vc and "amendment_kanunname_law" in vc,
         "VC ottoman file no longer amends lawgroup_governance_principles with amendment_kanunname_law")
    gob_laws = re.findall(r"activate_law = law_type:(\S+)", gob)
    need(gob_laws == ["law_monarchy", "law_imperial_divan", "law_scribal_bureaucrats", "law_millet_system",
                       "law_subjecthood", "law_traditionalism", "law_censorship", "law_land_based_taxation",
                       "law_debt_slavery", "law_migration_controls"],
         "GoB ottoman file activate_law list is now %s -- re-check the ottoman VC-vs-GoB write-up" % gob_laws)
    need("active_law:lawgroup_education_system" in gob and "amendment_gbbf_elifba" in gob,
         "GoB ottoman file no longer amends lawgroup_education_system -- re-check why VC's law_madrasa is added")
    madrasa = read(os.path.join(VC, "common/laws/joi_education_system.txt"))
    need("law_madrasa" in madrasa and "requires_law_or" in madrasa and "law_millet_system" in madrasa,
         "VC's law_madrasa prerequisite changed -- re-check the ottoman VC-vs-GoB write-up")


def build_ottoman():
    _check_ottoman_laws_vs_vc()
    relpath = "common/history/countries/tur - ottoman empire.txt"
    gob = read(os.path.join(_p.gob, relpath))
    win = _splice_vc_into_ottoman(gob)
    tgr = read(os.path.join(_p.tgr, relpath))
    m = re.search(r"(?ms)^(\t*)add_company = company_type:company_imperial_arsenal\b.*?\n\1\}\n", tgr)
    need(m is not None, "TGR no longer adds company_imperial_arsenal in " + relpath)
    block = m.group(0).rstrip("\n")
    need("company_imperial_arsenal" not in win,
         "Gates of the Bosphorus already adds company_imperial_arsenal -- the merge below is stale")
    w = win.rstrip("\n")
    i = w.rindex("}")
    j = w[:i].rindex("}")
    line_start = w.rfind("\n", 0, j) + 1
    body = w[:line_start].rstrip("\n") + "\n\n" + block + "\n" + w[line_start:] + "\n"

    note("tur - ottoman empire.txt: GoB+TGR base (same merge as regen_addon1._history_ottoman) "
         "+ VC's law_madrasa activation and two amendments spliced in")
    return vc_tag_delete_only("tur - ottoman empire.txt") + banner(
        "ComPatch HC+GoB+MoH x The Great Revision x Victorian Century -- the Ottomans at 1836",
        "",
        "REPLACE:s the same path addon1's hc+tgr compatch already owns "
        "(_HC+GoB+MoH/hc+tgr done/common/history/countries/tur - ottoman empire.txt) -- "
        "this compatch must load after addon1, and after Victorian Century.",
        "",
        "Gates of the Bosphorus and TGR's add_company block (the Imperial Arsenal",
        "company) are merged the same way as addon1's own hc+tgr compatch -- see that",
        "compatch's README for the GoB/TGR write-up.",
        "",
        "Victorian Century ships this same path too. Unlike its China file, most of",
        "what VC does here is much closer to vanilla than GoB's own rework -- VC keeps",
        "vanilla's law_autocracy and law_slave_trade where GoB swaps in",
        "law_imperial_divan/law_scribal_bureaucrats and law_debt_slavery, and adds no",
        "migration_controls law. Checked line by line 26.08.2026:",
        "",
        "  * VC adds exactly one law GoB does not have: law_madrasa, in",
        "    lawgroup_education_system. Its own requires_law_or gate is",
        "    law_state_religion OR law_millet_system OR law_people_of_the_book --",
        "    law_millet_system is active in every version of this file, so the",
        "    prerequisite holds. GoB itself already amends lawgroup_education_system",
        "    (amendment_gbbf_elifba) but never explicitly activates a law there, so",
        "    without VC that amendment attaches to whatever the engine's silent",
        "    default is. Added: gives GoB's own amendment something explicit and",
        "    thematically fitting to attach to instead.",
        "  * VC adds two amendments of its own, to lawgroup_taxation",
        "    (amendment_salt_monopoly) and lawgroup_governance_principles",
        "    (amendment_kanunname_law). GoB's four amendments are in different",
        "    groups (army_model, education_system, land_reform, slavery) -- no",
        "    overlap. Both target laws already active in GoB's own list",
        "    (law_land_based_taxation, law_monarchy). Added.",
        "  * The rest of VC's file -- three extra starting techs, its own",
        "    Sublime-Porte/Peter-the-Great-of-Turkey journal chain (seven entries),",
        "    great_ottomanism_var, an extra modifier -- is VC's own parallel Ottoman",
        "    political-flavor system, same class as GoB's Sick-Man/Tanzimat chain.",
        "    Left out for the same reason as China's parallel chain: running two",
        "    independent political systems on the same country is not something",
        "    either author designed for.",
        "",
        "Merged below: GoB's file with VC's law_madrasa activation and two amendments",
        "spliced in, then TGR's add_company block appended.",
        "",
        "VARIANTS: this whole compatch is the VC layer -- without VC, do not install",
        "this file, addon1's own hc+tgr output already stands alone.") + body


# =============================================================================
#  10. china.txt -- documentation-only check, no file produced
# =============================================================================
def check_china_no_op():
    """China's activate_law list is the one place where MoH's and VC's rewrites
    of this file look, on a skim, like they might need reconciling. They do
    not: every VC choice is either identical to MoH's, a competing pick for a
    law group MoH's own chain already has a load-bearing reason to own, or an
    addition whose own prerequisite MoH's choices leave unmet. Asserted here so
    a future update to either file re-opens this decision. Produces no output
    file -- MoH's file (merged with TGR's company by addon1's hc+tgr compatch)
    is left completely alone; this function exists only so the assertions run
    as part of a normal build and a source drift stops it loudly."""
    moh = read(os.path.join(_p.moh, "common/history/countries/chi - china.txt"))
    vc = read(os.path.join(VC, "common/history/countries/chi - china.txt"))
    vc_laws = re.findall(r"activate_law = law_type:(\S+)", vc)
    need(vc_laws == ["law_monarchy", "law_autocracy", "law_serfdom", "law_land_based_taxation",
                      "law_imperial_examination", "law_subjecthood", "law_traditionalism",
                      "law_censorship", "law_closed_borders", "law_canton_system",
                      "law_freedom_of_conscience", "law_classical_learning"],
         "VC china.txt activate_law list is now %s -- re-check the china.txt VC-vs-MoH write-up" % vc_laws)
    moh_laws = re.findall(r"activate_law = law_type:(\S+)", moh)
    need(moh_laws == ["law_monarchy", "law_autocracy", "law_tenant_farmers", "law_land_based_taxation",
                       "law_imperial_examinations", "law_subjecthood", "law_traditionalism",
                       "law_censorship", "law_closed_borders", "law_freedom_of_conscience",
                       "law_canton_system", "law_night_watchmen"],
         "MoH china.txt activate_law list is now %s -- re-check the china.txt VC-vs-MoH write-up" % moh_laws)
    need("active_law:lawgroup_land_reform" in moh and "amendment_chinese_traditional_land_system" in moh,
         "MoH china.txt no longer amends lawgroup_land_reform -- re-check why law_tenant_farmers is kept")
    vc_edu = read(os.path.join(VC, "common/laws/joi_education_system.txt"))
    need("law_classical_learning" in vc_edu and "requires_law_or" in vc_edu
         and "law_serfdom" in vc_edu and "law_imperial_examination" in vc_edu,
         "VC's law_classical_learning prerequisite changed -- re-check the china.txt VC-vs-MoH write-up")
    note("chi - china.txt: checked line by line, VC adds nothing worth carrying against MoH's "
         "choices here -- no file produced, MoH+TGR (addon1's own output) is left alone")


# =============================================================================
#  11. usa - usa.txt  (pure HC + VC, TGR never touches this file)
# =============================================================================
def _extract_lawgroup_amendments(text):
    """Every `active_law:lawgroup_X ?= { add_amendment = { type = ...
    sponsor = ... } }` block in a country history file, as (group, amendment
    type, exact original text) triples, in file order."""
    pattern = re.compile(
        r"active_law:lawgroup_(\w+) \?= \{[^\n]*\n"
        r"\t\t\tadd_amendment = \{\n\t\t\t\ttype = (\S+)\n\t\t\t\tsponsor = \S+\n\t\t\t\}\n\t\t\}")
    return [(m.group(1), m.group(2), m.group(0)) for m in pattern.finditer(text)]


def _check_usa_laws_vs_vc():
    """usa - usa.txt is Hail Columbia's flagship file. Five law groups
    (trade_policy, economic_system, free_speech, taxation, church_and_state) are
    genuine competitions between HC's own custom historical laws and VC's more
    vanilla-adjacent picks -- HC's choices win, same principle as everywhere
    else in this addon. What VC adds beyond that is a clean, additive
    Bill-of-Rights amendment chain: fourteen active_law:lawgroup_X blocks, of
    which two are byte-identical to ones HC's file already has and twelve are
    new. Asserted here so a future update to either file re-opens the decision
    instead of drifting under the write-up in the banner below."""
    hc = read(os.path.join(_p.hc, "common/history/countries/usa - usa.txt"))
    vc = read(os.path.join(VC, "common/history/countries/usa - usa.txt"))

    hc_laws = re.findall(r"activate_law = law_type:(\S+)", hc)
    need(hc_laws == ["law_public_schools", "law_legacy_slavery", "law_racial_segregation",
                      "law_usfp_american_system", "law_agrarianism", "law_frontier_colonization",
                      "law_right_of_assembly", "law_no_workers_rights", "law_usfp_devolved_taxation",
                      "law_national_militia", "law_local_police", "law_no_womens_rights",
                      "law_usfp_nominal_separation", "law_homesteading"],
         "HC usa.txt activate_law list is now %s -- re-check the usa.txt VC-vs-HC write-up" % hc_laws)
    need("start_enactment = law_type:law_universal_suffrage" in hc,
         "HC no longer start_enactments law_universal_suffrage in usa.txt -- re-check the usa.txt VC-vs-HC write-up")

    vc_laws = re.findall(r"activate_law = law_type:(\S+)", vc)
    need(vc_laws == ["law_public_schools", "law_legacy_slavery", "law_racial_segregation",
                      "law_homesteading", "law_protectionism", "law_interventionism",
                      "law_frontier_colonization", "law_protected_speech", "law_no_workers_rights",
                      "law_per_capita_based_taxation", "law_national_militia", "law_local_police",
                      "law_no_womens_rights", "law_total_separation"],
         "VC usa.txt activate_law list is now %s -- re-check the usa.txt VC-vs-HC write-up" % vc_laws)

    amendments = _extract_lawgroup_amendments(vc)
    need(len(amendments) == 14,
         "VC usa.txt now has %d lawgroup amendments (expected 14) -- re-check the usa.txt VC-vs-HC write-up"
         % len(amendments))
    dup_types = {"amendment_american_second_amendment", "amendment_tradition_of_free_elections"}
    dups = [(g, t) for g, t, _ in amendments if t in dup_types]
    need(dups == [("governance_principles", "amendment_american_second_amendment")]
         or ("distribution_of_power", "amendment_tradition_of_free_elections") in dups,
         "VC usa.txt amendment duplicates changed -- re-check the usa.txt VC-vs-HC write-up")
    for t in dup_types:
        need(t in hc, "HC usa.txt no longer has VC's supposedly-duplicate %s -- re-check the usa.txt VC-vs-HC write-up" % t)
    new_amendments = [(g, t, blk) for g, t, blk in amendments if t not in dup_types]
    need(len(new_amendments) == 12,
         "%d new (non-duplicate) VC amendments found, expected 12 -- re-check the usa.txt VC-vs-HC write-up"
         % len(new_amendments))
    need(sorted(t for _, t, _ in new_amendments) == sorted([
        "amendment_american_third_amendment", "amendment_american_forth_amendment",
        "amendment_american_fifth_amendment", "amendment_american_sixth_amendment",
        "amendment_american_seventh_amendment", "amendment_american_eighth_amendment",
        "amendment_american_ninth_amendment", "amendment_american_tenth_amendment",
        "amendment_usa_declaration_of_independence", "amendment_american_first_amendment",
        "amendment_common_law", "amendment_american_fugitive_slaves_act"]),
         "VC usa.txt's twelve new amendment types changed -- re-check the usa.txt VC-vs-HC write-up")
    return new_amendments


def _splice_vc_amendments_into_usa(hc, new_amendments):
    anchor = ("active_law:lawgroup_governance_principles ?= { # Presidential Republic\n"
              "\t\t\tadd_amendment = {\n"
              "\t\t\t\ttype = amendment_american_second_amendment\n"
              "\t\t\t\tsponsor = PREV.ig:ig_rural_folk\n"
              "\t\t\t}\n"
              "\t\t}\n")
    need(hc.count(anchor) == 1, "usa.txt: HC's Presidential Republic amendment block moved -- fix the VC splice anchor")
    block = "\n\t\t# Victorian Century -- see the banner above\n" + "\n".join(blk for _, _, blk in new_amendments) + "\n"
    return hc.replace(anchor, anchor + block, 1)


def build_usa():
    new_amendments = _check_usa_laws_vs_vc()
    hc = read(os.path.join(_p.hc, "common/history/countries/usa - usa.txt"))
    out = _splice_vc_amendments_into_usa(hc, new_amendments)
    note("usa - usa.txt: HC body (its own law choices kept for the five groups VC competes on) "
         "+ 12 of VC's 14 lawgroup amendments spliced in (2 were already byte-identical in HC's file)")
    return vc_tag_delete_only("usa - usa.txt") + banner(
        "ComPatch HC+GoB+MoH x Victorian Century -- the USA at 1836",
        "",
        "Hail, Columbia! and Victorian Century both ship",
        "common/history/countries/usa - usa.txt at the vanilla path -- this is HC's",
        "flagship file, the one the whole \"United States Flavor Pack\" is built around,",
        "and HC loads later so it wins the path outright. TGR never touches this path,",
        "so unlike the other four items in this compatch, this one is NOT a second",
        "REPLACE: over addon1's output -- it just ships HC's file with VC's amendments",
        "spliced in directly. Checked line by line 26.08.2026.",
        "",
        "Fifteen law groups are explicitly activated by one or both files. Ten agree",
        "(education_system, slavery, citizenship, colonization, labor_rights,",
        "army_model, policing, rights_of_women, land_reform, and distribution_of_power",
        "left to start_enactment/vanilla default by both). Five are genuine",
        "competitions, and every one of HC's three own custom laws is in this list:",
        "",
        "  * trade_policy: HC's own law_usfp_american_system vs VC's law_protectionism.",
        "  * economic_system: HC's law_agrarianism vs VC's law_interventionism.",
        "  * free_speech: HC's law_right_of_assembly vs VC's law_protected_speech.",
        "  * taxation: HC's own law_usfp_devolved_taxation vs VC's",
        "    law_per_capita_based_taxation.",
        "  * church_and_state: HC's own law_usfp_nominal_separation vs VC's",
        "    law_total_separation.",
        "",
        "HC's picks win all five, same principle as everywhere else in this addon: a",
        "flavor pack's own signature content is what stays, and three of these five",
        "are laws HC wrote for itself. Also kept as HC-only, untouched by VC: the",
        "`start_enactment = law_type:law_universal_suffrage` (HC deliberately starts",
        "the USA mid-transition, \"states are in the middle of piecemeal removing tax",
        "obligations\"), and HC's entire USFP journal-entry/ideology/interest-group",
        "chain.",
        "",
        "What VC adds beyond the law list is a clean Bill-of-Rights amendment chain --",
        "fourteen `active_law:lawgroup_X ?= { add_amendment = {...} }` blocks, one to",
        "ten amendments plus the Declaration of Independence and common law. Two are",
        "byte-identical to blocks HC's file already has",
        "(amendment_american_second_amendment on governance_principles,",
        "amendment_tradition_of_free_elections on distribution_of_power) -- both mods",
        "clearly draw from the same shared amendment set. The other twelve are new,",
        "and every one is safe to add regardless of which side won the law list above:",
        "an amendment attaches to whatever law is active in its group, not to a",
        "specific one, and (per the checks in _check_usa_laws_vs_vc) every targeted",
        "group already has an active law under HC's own choices, or -- for",
        "governance_principles/bureaucracy/internal_security, which no activate_law in",
        "either file ever explicitly sets -- the same implicit-default mechanic HC's",
        "own file already relies on for its pre-existing governance_principles and",
        "bureaucracy amendments.",
        "",
        "NOT merged: VC's competing law picks (see above); VC's own tariff setting",
        "(g:fabric, tied to VC's trade-law assumptions, not HC's); and VC's entire",
        "parallel USA political/flavor chain -- its own \"real manifest destiny\"",
        "tracking variables and an active je_texas_usa (HC's own manifest_destiny.txt",
        "already deliberately suppresses the vanilla decision in favor of its own",
        "1100-line journal chain; a second, VC-driven Manifest Destiny system would",
        "double up), plus VC's own missouri_compromise modifier (HC already has",
        "usfp_missouri_compromise_decaying), us_second_bank,",
        "failed_assassination_on_aj_president, and six of VC's own journal entries",
        "(before_us_civil_war, supreme_court, united_states_congress,",
        "westward_movement, je_seminole_wars, joi_flavor_usa.1). Same class of",
        "decision as China's and the Ottomans' parallel chains.",
        "",
        "add_company = company_type:company_william_cramp is byte-identical in both",
        "files (same date, same state) -- nothing to merge.",
        "",
        "VARIANTS: this whole compatch is the VC layer -- without VC, do not install",
        "this file, ship HC's own usa - usa.txt unchanged.") + out


# =============================================================================
#  driver
# =============================================================================
FILES = {
    "common/character_templates/zz_hcvc_character_templates.txt": build_character_templates,
    "common/dna_data/ecchi_usa_polk.txt": build_polk_dna,
    "common/dynamic_country_names/zz_hcvc_dynamic_country_names.txt": build_dynamic_country_names,
    "common/flag_definitions/zz_hcvc_flag_definitions_chi.txt": build_flag_definitions,
    "common/scripted_buttons/zz_hcvc_opium_buttons.txt": build_opium_buttons,
    "common/interest_groups/zz_hcvc_ig_landowners.txt": build_ig_landowners,
    "common/interest_groups/zz_hcvc_ig_rural_folk.txt": build_ig_rural_folk,
    "common/ideologies/zz_hcvc_jacksonian_democrat.txt": build_jacksonian,
    "common/history/countries/tur - ottoman empire.txt": build_ottoman,
    "common/history/countries/usa - usa.txt": build_usa,
}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    china_checked = [False]

    diffs, written = [], 0
    for rel, build in FILES.items():
        if build is build_ottoman and not china_checked[0]:
            check_china_no_op()
            china_checked[0] = True
        text = build()
        bal = brace_balance(text)
        if bal:
            raise SystemExit("brace balance %+d in %s" % (bal, rel))
        path = os.path.join(OUT, rel)
        if args.check:
            if not os.path.exists(path):
                diffs.append("missing: " + rel)
            elif read(path) != text:
                diffs.append("differs: " + rel)
        else:
            write(path, text)
            written += 1

    print("--- what this run merged ---")
    for n in NOTES:
        print("  * " + n)
    if args.check:
        for d in diffs:
            print("  ! " + d)
        print("%d file(s) out of date" % len(diffs))
        return 1 if diffs else 0
    print("%d file(s) written under %s" % (written, OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
