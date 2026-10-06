#!/usr/bin/env python3
"""
EF.30 -- the key rate panel in "Budget -> Finances": button tooltips and the
central bank's numbers.

Why this exists
---------------
E&F's rate panel (the -/+ buttons, the big rate, the eight boxes) lives inside
the GUI type `budget_panel_financial_panel_content`
(gui/00_ef_deported_gui_1.gui, ~21k lines, one of the two huge E&F GUI files).
Under EF.30 the rate is set by the central bank from the credit rating, and
the 30.09 test showed the panel does not say any of it: the buttons were
greyed out with no reason (only "-" had a tooltip, a fixed E&F text), and
nothing showed the rating, the bank's target, the next step or the player's
own policy.

What this does
--------------
Re-issues that one type verbatim from a file that sorts BEFORE E&F's (the
first file to register a type wins, see Output below), with three edits:
  1. "-" button: E&F's fixed tooltip -> description + the conditions and the
     effect (BuildTooltip over common/scripted_guis/zz_ef_cb_rate_buttons.txt;
     it already lists the effect, a separate ExecuteTooltip doubled it --
     removed 2026-09-30).
  2. "+" button: the same (it had no tooltip at all).
  3. A third row of four boxes under E&F's two: credit rating (letter and
     note), the policy rule rate (the bank's own rate from the rating; red
     when above the actual rate, green when below), the next step (and in
     how many months), the discretionary adjustment. Each with a tooltip.
Texts are localization keys (localization/*/zz_ef_cb_rate_panel_l_*.yml).
GUI @constants are file-local: the type uses @panel_width only, re-declared.

Output (through ld_gen.emit, the type's entry into the fork «E&F: Ledgerdemain»): gui/ld_cb_rate_panel.gui. The
FIRST file to register a GUI type wins; files are read in ASCII order of their name across all mods, `ld_` sorts
before E&F's `00_ef_...` only through the fork's own files, and the type was cut out of the fork's
gui/00_ef_deported_gui_1.gui, so nothing else defines it. Check after a run: gui.log must not name a duplicate.

Reads E&F's original gui/00_ef_deported_gui_1.gui: the fork's copy if it still holds the type, otherwise
vic3_mods_out/E&F/gui/ (needs vic3_mods_out: run on the PC).

Usage:
    py tools/regen_ef_cb_rate_gui.py            # write
    py tools/regen_ef_cb_rate_gui.py --check    # exit 1 if the fork file differs
"""

from __future__ import annotations

import argparse
import re
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vic3lib as V  # noqa: E402
import ld_gen  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
res = lambda p: os.path.normpath(os.path.join(HERE, p))

# E&F's original file: in the fork the type was cut out of it (it lives only in gui/ld_cb_rate_panel.gui), so the
# source is the untouched E&F copy of vic3_mods_out (run on the PC); the fork's file is tried first.
_GUI_REL = ("gui", "00_ef_deported_gui_1.gui")
_FORK_GUI = os.path.join(ld_gen.FORK, *_GUI_REL)
_OUT_GUI = res(os.path.join("..", "..", "vic3_mods_out", "E&F", *_GUI_REL))
EF_GUI = _FORK_GUI if "type budget_panel_financial_panel_content" in V.read(_FORK_GUI) else _OUT_GUI
OUT = "gui/00_00_ef_cb_rate_panel.gui"   # hotfix path; ld_gen writes the fork's gui/ld_cb_rate_panel.gui
TYPE = "budget_panel_financial_panel_content"

# sha of E&F's type body this generator was written against (--check).
KNOWN_SHA = "249eac13ba49"

SCOPE = "GuiScope.SetRoot(GetPlayer.MakeScope).End"


def button_tooltip(sgui: str, desc_key: str) -> str:
    return (
        f'tooltip = "[Localize(\'{desc_key}\')]'
        f"[Localize('zz_ef_rate_tt_conditions')]"
        f"[GetScriptedGui('{sgui}').BuildTooltip( {SCOPE} )]\""
    )


def value_textbox(key: str, ind: str, visible: str = "") -> str:
    vis = ""
    if visible:
        vis = f"{ind}\tvisible = \"[GetScriptedGui('{visible}').IsShown( {SCOPE} )]\"\n"
    return f"""{ind}textbox = {{
{vis}{ind}	autoresize = yes
{ind}	text = "{key}"
{ind}	align = hcenter|nobaseline
{ind}	parentanchor = hcenter
{ind}	fontsize = 18
{ind}	multiline = yes
{ind}	minimumsize = {{ 115 40 }}
{ind}	maximumsize = {{ 115 -1 }}
{ind}}}
"""


def box(title_key: str, value_key, tooltip_key: str, ind: str) -> str:
    """One box in E&F's style (entry_bg_simple, 100x100). value_key is a
    localization key, or a list of (key, scripted_gui): colour variants, one
    shown at a time."""
    if isinstance(value_key, str):
        values = value_textbox(value_key, ind + "\t")
    else:
        values = "".join(value_textbox(k, ind + "\t", vis) for k, vis in value_key)
    return f"""{ind}flowcontainer = {{
{ind}	spacing = 5
{ind}	direction = vertical
{ind}	tooltip = "{tooltip_key}"
{ind}	using = tooltip_below

{ind}	textbox = {{
{ind}		autoresize = yes
{ind}		text = "{title_key}"
{ind}		fontsize = 15
{ind}		align = hcenter
{ind}		parentanchor = hcenter
{ind}		multiline = yes
{ind}		minimumsize = {{ 115 40 }}
{ind}		maximumsize = {{ 115 -1 }}
{ind}	}}

{values}
{ind}	background = {{
{ind}		using = entry_bg_simple
{ind}		margin = {{ 10 10 }}
{ind}	}}

{ind}	minimumsize = {{ 100 100 }}
{ind}	maximumsize = {{ 100 100 }}
{ind}}}
"""


def cb_row(ind: str) -> str:
    inner = ind + "\t"
    boxes = "".join(
        box(t, v, tt, inner)
        for t, v, tt in (
            ("zz_ef_rate_box_rating", "zz_ef_rate_box_rating_value", "zz_ef_rate_box_rating_tt"),
            ("zz_ef_rate_box_target", [
                ("zz_ef_rate_box_target_value_up", "zz_ef_cb_rule_above_rate"),
                ("zz_ef_rate_box_target_value_down", "zz_ef_cb_rule_below_rate"),
                ("zz_ef_rate_box_target_value", "zz_ef_cb_rule_at_rate"),
            ], "zz_ef_rate_box_target_tt"),
            ("zz_ef_rate_box_step", "zz_ef_rate_box_step_value", "zz_ef_rate_box_step_tt"),
            ("zz_ef_rate_box_policy", "zz_ef_rate_box_policy_value", "zz_ef_rate_box_policy_tt"),
            # EF.48, night 2 item 5 (2.10): the government's rate = key + risk premium
            ("zz_ef_rate_box_gov", "zz_ef_rate_box_gov_value", "zz_ef_rate_box_gov_tt"),
        )
    )
    return (
        f"{ind}### EF.30: the central bank's numbers (tools/regen_ef_cb_rate_gui.py)\n"
        f"{ind}flowcontainer = {{\n"
        f"{ind}\tspacing = 25\n"
        f"{ind}\tdirection = horizontal\n"
        f"{ind}\tparentanchor = hcenter\n\n"
        f"{boxes}"
        f"{ind}}}\n"
    )


SG = "GuiScope.SetRoot(GetPlayer.MakeScope).End"


def sg_button(sgui: str, text_key: str, ind: str) -> str:
    return f"""{ind}button = {{
{ind}	using = default_button
{ind}	size = {{ 45 30 }}
{ind}	text = "{text_key}"
{ind}	using = tooltip_below
{ind}	tooltip = "[GetScriptedGui('{sgui}').BuildTooltip( {SG} )]"
{ind}	onclick = "[GetScriptedGui('{sgui}').Execute( {SG} )]"
{ind}	enabled = "[GetScriptedGui('{sgui}').IsValid( {SG} )]"
{ind}}}
"""


def mp_row(ind: str) -> str:
    """EF.48, В4.1 (2.10): devaluation / revaluation towards a cover target -- shown while one of the
    two laws is in force (tools/regen_ef_monetary_policy.py writes the scripted guis and texts)."""
    i1, i2, i3 = ind + "	", ind + "		", ind + "			"
    targets = "".join(sg_button(f"zz_ef_mp_target_{k}", f"zz_ef_mp_btn_{k}", i2) for k in ("m5", "m1", "p1", "p5"))
    return f"""{ind}### EF.48 V4.1 (plan: B4.1): the monetary policy scale (tools/regen_ef_cb_rate_gui.py, mp_row)
{ind}flowcontainer = {{
{i1}visible = "[GetScriptedGui('zz_ef_mp_visible').IsShown( {SG} )]"
{i1}spacing = 6
{i1}direction = vertical
{i1}parentanchor = hcenter
{i1}margin_top = 10
{i1}tooltip = "zz_ef_mp_tt"
{i1}using = tooltip_below

{i1}textbox = {{
{i2}autoresize = yes
{i2}text = "zz_ef_mp_title"
{i2}fontsize = 16
{i2}align = hcenter|nobaseline
{i2}parentanchor = hcenter
{i2}multiline = yes
{i2}maximumsize = {{ 500 -1 }}
{i1}}}
{i1}default_progressbar_horizontal = {{
{i2}size = {{ 400 16 }}
{i2}parentanchor = hcenter
{i2}blockoverride "values" {{
{i3}min = 0
{i3}max = 1
{i3}value = "[FixedPointToFloat( GetPlayer.MakeScope.ScriptValue('zz_ef_mp_progress') )]"
{i2}}}
{i1}}}
{i1}textbox = {{
{i2}autoresize = yes
{i2}text = "zz_ef_mp_line2"
{i2}fontsize = 14
{i2}align = hcenter|nobaseline
{i2}parentanchor = hcenter
{i2}multiline = yes
{i2}maximumsize = {{ 500 -1 }}
{i1}}}
{i1}flowcontainer = {{
{i2}spacing = 5
{i2}direction = horizontal
{i2}parentanchor = hcenter
{i2}textbox = {{
{i3}autoresize = yes
{i3}text = "zz_ef_mp_target_label"
{i3}align = nobaseline
{i3}parentanchor = vcenter
{i2}}}
{targets}{i1}}}
{i1}flowcontainer = {{
{i2}spacing = 5
{i2}direction = horizontal
{i2}parentanchor = hcenter
{i2}textbox = {{
{i3}autoresize = yes
{i3}text = "zz_ef_mp_pace_label"
{i3}align = nobaseline
{i3}parentanchor = vcenter
{i2}}}
{i2}button_icon_minus_action = {{
{i3}size = {{ 30 30 }}
{i3}parentanchor = vcenter
{i3}using = tooltip_below
{i3}tooltip = "[GetScriptedGui('zz_ef_mp_pace_minus').BuildTooltip( {SG} )]"
{i3}onclick = "[GetScriptedGui('zz_ef_mp_pace_minus').Execute( {SG} )]"
{i3}enabled = "[GetScriptedGui('zz_ef_mp_pace_minus').IsValid( {SG} )]"
{i2}}}
{i2}textbox = {{
{i3}autoresize = yes
{i3}text = "zz_ef_mp_pace_value"
{i3}align = nobaseline
{i3}parentanchor = vcenter
{i2}}}
{i2}button_icon_plus_action = {{
{i3}size = {{ 30 30 }}
{i3}parentanchor = vcenter
{i3}using = tooltip_below
{i3}tooltip = "[GetScriptedGui('zz_ef_mp_pace_plus').BuildTooltip( {SG} )]"
{i3}onclick = "[GetScriptedGui('zz_ef_mp_pace_plus').Execute( {SG} )]"
{i3}enabled = "[GetScriptedGui('zz_ef_mp_pace_plus').IsValid( {SG} )]"
{i2}}}
{i1}}}
{ind}}}
"""


OPEN = re.compile(r"^\s*([A-Za-z_][\w]*)\s*=\s*\{")
PROP = re.compile(r"^\s*([A-Za-z_][\w]*)\s*=\s*[^{]")


def clean_ef_noise(body: str) -> tuple[str, list[int]]:
    """Drop what the engine rejects in E&F's copy of the type (EF.30 cleanup,
    2026-09-30, from logs/error.log + gui.log of the 1848 run: ~900 lines, all
    E&F's own, none in our inserts). Returns the new body and the 0-based
    indices of the lines touched (for the check against the logs):
      - "nobaseline" / typo "nobaselin" in parentanchor ("Unknown anchor");
      - align on icon / flag_icon ("Property 'align' not handled");
      - ignoreinvisible on textbox, elide / default_format where the widget
        does not take them (per the log: widgets other than textbox);
      - a property repeated in the same block ("Duplicate property").
    Nothing visible changes: the engine ignored all of these already."""
    out, touched = [], []
    stack: list[tuple[str, set]] = []
    for i, line in enumerate(body.split("\n")):
        code = line.split("#", 1)[0]
        m_open = OPEN.match(code)
        m_prop = PROP.match(code) if not m_open else None
        drop = False
        if m_prop and stack:
            key = m_prop.group(1)
            widget, seen = stack[-1]
            if key == "parentanchor" and "|nobaselin" in code:
                new = re.sub(r"\|nobaseline?\b", "", line)
                out.append(new)
                touched.append(i)
                seen.add(key)
                continue
            if key == "align" and widget in ("icon", "flag_icon"):
                drop = True
            elif key == "ignoreinvisible" and widget == "textbox":
                drop = True
            elif key in ("elide", "default_format") and widget != "textbox":
                drop = True
            elif key in seen and key not in ("using", "block", "blockoverride", "onclick"):
                drop = True
            if not drop:
                seen.add(key)
        if drop:
            touched.append(i)
        else:
            out.append(line)
        # every "{" opens a block (the first one named, if the line is
        # "name = {"), every "}" closes one
        for k in range(code.count("{")):
            stack.append((m_open.group(1) if (m_open and k == 0) else "?", set()))
        for _ in range(code.count("}")):
            if stack:
                stack.pop()
    return "\n".join(out), touched


def build(src: str) -> tuple[str, str]:
    i = src.find(f"type {TYPE}")
    assert i >= 0, "type not found in E&F"
    j = src.find("{", i)
    k = V._match_brace(src, j)
    body = src[i:k + 1]
    orig_sha = V.sha(body)

    # 0. E&F's own engine-rejected properties (see clean_ef_noise)
    body, touched = clean_ef_noise(body)
    assert len(touched) > 700, f"cleanup hit {len(touched)} lines, expected ~800: E&F's type changed?"

    # 0b. The debt buyer / seller lists (central_bank_debt_buyer_list_N,
    # ai_seller_country_general_N, 20 live, 50 more commented out) are gated on
    # GetScriptedGui('ai_quantity_purchasing_N_visibility') with
    # Country.MakeScope at list level: there is no Country in context there,
    # and E&F defines only _1 of the 19. The check fails every frame -- ~15k
    # log lines, all five error.log rotations filled within a minute (run
    # 2026-09-30, 1848) -- and a failed visible hides the list, so they were
    # never shown. Same look, no spam: visible = no. Showing them is EF.13 / UI.
    body, n = re.subn(
        r"""(?m)^(\s*)visible = "\[GetScriptedGui\('ai_quantity_purchasing_\d+_visibility'\)\.IsShown\( GuiScope\.SetRoot\(Country\.MakeScope\)\.End\)\]"$""",
        r"\1visible = no  # EF.30: E&F's check failed every frame (tools/regen_ef_cb_rate_gui.py)",
        body,
    )
    assert n == 20, f"{n} debt list checks, expected 20"

    # 2. "+" button first: its commented-out line contains the "-" button's
    # line as a substring
    old = '#tooltip = "base_rate_percentage_modification"'
    assert body.count(old) == 1, old
    body = body.replace(
        old, "using = tooltip_below\n" + "\t" * 11 + button_tooltip("base_rate_increase", "zz_ef_rate_tt_increase_desc")
    )

    # 1. "-" button
    old = 'tooltip = "base_rate_percentage_modification"'
    assert body.count(old) == 1, old
    body = body.replace(old, button_tooltip("base_rate_reduce", "zz_ef_rate_tt_reduce_desc"))
    assert body.count("BuildTooltip( " + SCOPE) == 2

    # 3. third row of boxes, before the block with the explanatory sentence
    anchor = 'text = "base_rate_percentage_txt"'
    assert body.count(anchor) == 1, anchor
    a = body.find(anchor)
    fc = body.rfind("flowcontainer  = {", 0, a)
    assert fc > 0 and a - fc < 400, "layout of the rate block changed"
    line_start = body.rfind("\n", 0, fc) + 1
    ind = body[line_start:fc]
    assert ind.strip() == "", repr(ind)
    body = body[:line_start] + cb_row(ind) + mp_row(ind) + body[line_start:]

    # 4. Е.6 (5.10, Д.3): the bond tables under E&F's two headers (tools/regen_ef_bond_tables.py fills the lists)
    for key, lst, pre, title in (("gold_lent_to_foreign_countries", "zz_ef_bt_out_list", "zz_ef_bto", "zz_ef_bt_out_title"),
                                 ("gold_lent_to_us", "zz_ef_bt_in_list", "zz_ef_bt", "zz_ef_bt_in_title")):
        anchor = f'text = "{key}"\n'
        assert body.count(anchor) == 1, anchor
        a = body.index(anchor)
        hdr = body.rfind("default_header = {", 0, a)
        assert a - hdr < 200, key
        line_start = body.rfind("\n", 0, hdr) + 1
        ind = body[line_start:hdr]
        end = V._match_brace(body, body.index("{", hdr)) + 1
        body = body[:end] + "\n" + bond_table(lst, pre, title, ind) + body[end:]

    # 5. EF.36 (э2): the capitalization list (after "divers_index") shows the mining index under the agricultural
    # icon and the agricultural index under the mining one -- E&F swapped the two script values
    for icon, wrong, right in (("agricultural_stock", "mining_stock_index", "agricultural_stock_index"),
                               ("mining_stock", "agricultural_stock_index", "mining_stock_index")):
        old = f"text = \"@{icon}! [Country.MakeScope.ScriptValue('{wrong}')|D]\""
        assert body.count(old) == 1, old
        body = body.replace(old, f"text = \"@{icon}! [Country.MakeScope.ScriptValue('{right}')|D]\"  # EF.36")

    # 6. ФК2 (7.10): a text that is an expression, not a localization key ("Unlocalized text … use the raw_text
    # property", ~200 lines in error.log of r1007_013714) -> raw_text; raw_text evaluates [..] and @icon! the same
    body, n = re.subn(r'(?m)^(\s*)text = "([^"]*[\[@#][^"]*)"', r'\1raw_text = "\2"', body)
    assert n > 50, f"{n} expression texts, expected 100+"

    return body, orig_sha


def bond_table(lst: str, pre: str, title: str, ind: str) -> str:
    """Е.6: a button (zz_ef_bonds_update) and the list of countries with their treasury / banks rows."""
    i1, i2, i3, i4, i5 = (ind + "\t" * k for k in range(1, 6))
    gt = "[GreaterThan_CFixedPoint(Scope.GetCountry.MakeScope.Var('{0}').GetValue, '(CFixedPoint)0')]"
    return f"""{ind}# Е.6 (5.10): {lst} (tools/regen_ef_bond_tables.py)
{ind}flowcontainer = {{
{i1}parentanchor = hcenter
{i1}direction = vertical
{i1}margin_top = 10
{i1}spacing = 4
{i1}flowcontainer = {{
{i2}direction = horizontal
{i2}spacing = 10
{i2}parentanchor = hcenter
{i2}textbox = {{
{i3}using = fontsize_large
{i3}autoresize = yes
{i3}text = "{title}"
{i2}}}
{i2}button = {{
{i3}using = default_button
{i3}size = {{ 120 30 }}
{i3}text = "zz_ef_bt_button"
{i3}tooltip = "zz_ef_bt_button_tt"
{i3}onclick = "[GetScriptedGui('zz_ef_bonds_update').Execute( {SG} )]"
{i2}}}
{i1}}}
{i1}textbox = {{
{i2}autoresize = yes
{i2}multiline = yes
{i2}max_width = 520
{i2}text = "zz_ef_bt_head"
{i1}}}
{i1}textbox = {{
{i2}visible = "[IsDataModelEmpty(GetGlobalList('{lst}'))]"
{i2}autoresize = yes
{i2}text = "zz_ef_bt_empty"
{i1}}}
{i1}flowcontainer = {{
{i2}direction = vertical
{i2}spacing = 2
{i2}datamodel = "[GetGlobalList('{lst}')]"
{i2}item = {{
{i3}flowcontainer = {{
{i4}direction = vertical
{i4}textbox = {{
{i5}autoresize = yes
{i5}raw_text = "[Scope.GetCountry.GetFlagTextIcon] #b [Scope.GetCountry.GetName]#!"
{i4}}}
{i4}textbox = {{
{i5}visible = "{gt.format(pre + '_t_amt')}"
{i5}autoresize = yes
{i5}margin_left = 20
{i5}text = "{pre}_t_row"
{i4}}}
{i4}textbox = {{
{i5}visible = "{gt.format(pre + '_b_amt')}"
{i5}autoresize = yes
{i5}margin_left = 20
{i5}text = "{pre}_b_row"
{i4}}}
{i3}}}
{i2}}}
{i1}}}
{ind}}}
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    src = V.read(EF_GUI)
    body, orig_sha = build(src)

    out = (
        "# GENERATED by tools/regen_ef_cb_rate_gui.py -- do not edit by hand.\n"
        f"# EF.30: E&F's {TYPE} (gui/00_ef_deported_gui_1.gui) re-issued with\n"
        "# the key rate buttons' tooltips and the central bank's boxes.\n"
        f"# Source type sha: {orig_sha}\n\n"
        "@panel_width = 540\n\n"
        "types zz_ef_cb_rate_panel\n{\n\t"
        + body
        + "\n}\n"
    )
    assert V.brace_balance(out) == 0
    ld_gen.emit(OUT, out)
    ld_gen.report("regen_ef_cb_rate_gui")
    return 0


if __name__ == "__main__":
    sys.exit(main())
