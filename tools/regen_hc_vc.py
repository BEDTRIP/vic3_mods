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

HERE = os.path.dirname(os.path.abspath(__file__))
res = lambda p: os.path.normpath(os.path.join(HERE, p))

HC = res("../../vic3_mods_out/for addon/hailcolumbia")
MOH = res("../../vic3_mods_out/for addon/mandateofheaven")
VC = res("../../vic3_mods_out/VC")
OUT = res("../_HC+GoB+MoH/hc+vc wip")
GRID = res("../_HC+GoB+MoH/hc+vc wip/hc_vc_character_traits.xlsx")

DATE = "2026-08-26"
NOTES: list[str] = []


def note(s):
    NOTES.append(s)


def need(cond, msg):
    if not cond:
        raise SystemExit("SOURCE DRIFT: " + msg)


def banner(*lines):
    return "\n".join("### " + l if l else "###" for l in lines) + "\n\n"


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

    out = []
    for key, body in pieces:
        out.append("REPLACE_OR_CREATE:%s = {%s}\n" % (key, body))
    text = "\n".join(out)
    return banner(
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
    return banner(
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
    return banner(
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
    return banner(
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
    return banner(
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
#  driver
# =============================================================================
FILES = {
    "common/character_templates/zz_hcvc_character_templates.txt": build_character_templates,
    "common/dna_data/ecchi_usa_polk.txt": build_polk_dna,
    "common/dynamic_country_names/zz_hcvc_dynamic_country_names.txt": build_dynamic_country_names,
    "common/flag_definitions/zz_hcvc_flag_definitions_chi.txt": build_flag_definitions,
    "common/scripted_buttons/zz_hcvc_opium_buttons.txt": build_opium_buttons,
}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    diffs, written = [], 0
    for rel, build in FILES.items():
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
