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
Re-issues that one type verbatim from a file that loads after E&F (a type
defined twice is not an error, the later definition wins -- same technique as
GR.21, tools/regen_ef_cmf_gui.py), with three edits:
  1. "-" button: E&F's fixed tooltip -> description + effect
     (ExecuteTooltip: the treasury cost) + the conditions green/red
     (BuildTooltip over the custom_tooltip lines of
     common/scripted_guis/zz_ef_cb_rate_buttons.txt).
  2. "+" button: the same (it had no tooltip at all).
  3. A third row of four boxes under E&F's two: credit rating (letter and
     note), the bank's target rate, the next step (and in how many months),
     the player's policy. Each with a tooltip explaining it.
Texts are localization keys (localization/*/zz_ef_cb_rate_panel_l_*.yml).
GUI @constants are file-local: the type uses @panel_width only, re-declared.

Output: `_ef/ef hotfix 1.13/gui/zz_ef_cb_rate_panel.gui`. The hotfix is a
separate mod loaded after E&F; nothing else in the playset defines this type
(checked 2026-09-30: E&F's budget_panel.gui and the TGR compatch only use it).

Usage:
    py tools/regen_ef_cb_rate_gui.py            # write
    py tools/regen_ef_cb_rate_gui.py --check    # exit 1 if E&F's type drifted
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vic3lib as V  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
res = lambda p: os.path.normpath(os.path.join(HERE, p))

EF_GUI = r"C:\Games\Steam\steamapps\workshop\content\529340\3143591632\gui\00_ef_deported_gui_1.gui"
OUT = res(r"..\_ef\ef hotfix 1.13\gui\zz_ef_cb_rate_panel.gui")
TYPE = "budget_panel_financial_panel_content"

# sha of E&F's type body this generator was written against (--check).
KNOWN_SHA = "249eac13ba49"

SCOPE = "GuiScope.SetRoot(GetPlayer.MakeScope).End"


def button_tooltip(sgui: str, desc_key: str) -> str:
    return (
        f'tooltip = "[Localize(\'{desc_key}\')]'
        f"[GetScriptedGui('{sgui}').ExecuteTooltip( {SCOPE} )]"
        f"[Localize('zz_ef_rate_tt_conditions')]"
        f"[GetScriptedGui('{sgui}').BuildTooltip( {SCOPE} )]\""
    )


def box(title_key: str, value_key: str, tooltip_key: str, ind: str) -> str:
    """One box in E&F's style (entry_bg_simple, 100x100)."""
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

{ind}	textbox = {{
{ind}		autoresize = yes
{ind}		text = "{value_key}"
{ind}		align = hcenter|nobaseline
{ind}		parentanchor = hcenter
{ind}		fontsize = 18
{ind}		multiline = yes
{ind}		minimumsize = {{ 115 40 }}
{ind}		maximumsize = {{ 115 -1 }}
{ind}	}}

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
            ("zz_ef_rate_box_target", "zz_ef_rate_box_target_value", "zz_ef_rate_box_target_tt"),
            ("zz_ef_rate_box_step", "zz_ef_rate_box_step_value", "zz_ef_rate_box_step_tt"),
            ("zz_ef_rate_box_policy", "zz_ef_rate_box_policy_value", "zz_ef_rate_box_policy_tt"),
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


def build(src: str) -> tuple[str, str]:
    i = src.find(f"type {TYPE}")
    assert i >= 0, "type not found in E&F"
    j = src.find("{", i)
    k = V._match_brace(src, j)
    body = src[i:k + 1]
    orig_sha = V.sha(body)

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
    body = body[:line_start] + cb_row(ind) + body[line_start:]

    return body, orig_sha


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    src = V.read(EF_GUI)
    body, orig_sha = build(src)

    if args.check:
        if KNOWN_SHA and orig_sha != KNOWN_SHA:
            print(f"DRIFT: E&F's {TYPE} changed ({orig_sha} != {KNOWN_SHA}), re-check the edits")
            return 1
        print(f"ok, {TYPE} sha {orig_sha}")
        return 0

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
    V.write(OUT, out)
    print(f"wrote {OUT} ({out.count(chr(10))} lines), source sha {orig_sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
