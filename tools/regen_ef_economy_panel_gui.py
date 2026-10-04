#!/usr/bin/env python3
"""
UI.8 (the user, 4.10: "the trade balance and the CB's reserves in E&F's menus must match the tooltip") --
the "Trade balance" block of "Budget -> Economy" in our numbers.

E&F's block (inside the GUI type `budget_panel_economy_panel_content`, gui/00_ef_deported_gui_1.gui, ~10k
lines) shows E&F's own counters: "current account" = trade_balance_in_gold_fixe_sv (E&F's cumulative trade
balance in gold, frozen at 0 since our model took the trade out of E&F's reserves, night 2), "trade balance
... a month" = E&F's monthly delta, import / export "in gold" from its bilateral-currency counters. The money
tooltip shows something else (the net flow with abroad, the market's trade balance in money), so the two
could not be checked against each other.

Re-issued verbatim from a file that sorts BEFORE E&F's (the first file to register a GUI type wins; see
regen_ef_cb_rate_gui.py), with the block's numbers replaced:
  * current account -> the week's net flow with abroad (zz_ef_v_f_ext_net: budget lines with abroad,
    trade, dividends, bonds -- what Hume settles in the CB's metal), in money;
  * trade balance -> the market's trade balance of the week (zz_ef_v_f_trade: exports - imports at the
    market's prices), in money;
  * import / export -> the week's imports and exports at the market's prices (zz_ef_trade_imports_week /
    zz_ef_trade_exports_week), in money.
The CB's metal block above it (E&F's "metal reserves of the CB", "stored this month") is E&F's and already
the same number as the tooltip's "metal in the standard's metal" -- left as it is. E&F's table "currency in
the trade balance" (its trade reserve, empty since В2.1) shows the CB's foreign currency by currency (П.8).

Output: `_ef/ef hotfix 1.13/gui/00_00_ef_economy_panel.gui`.

Usage:
    py tools/regen_ef_economy_panel_gui.py            # write
    py tools/regen_ef_economy_panel_gui.py --check    # exit 1 if E&F's type drifted
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vic3lib as V  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
res = lambda p: os.path.normpath(os.path.join(HERE, p))

EF_GUI = res(r"..\..\vic3_mods_out\E&F\gui\00_ef_deported_gui_1.gui")
OUT = res(r"..\_ef\ef hotfix 1.13\gui\00_00_ef_economy_panel.gui")
TYPE = "budget_panel_economy_panel_content"
KNOWN_SHA = "f74ae183f4b3"

SV = "[GetPlayer.MakeScope.ScriptValue('{0}')|+D] [GetPlayer.GetCustom('currency_symbol')]"

EDITS = [
    # (E&F's text, ours) -- each must occur exactly once in the type
    ('text = "trade_balance_fixe"', 'text = "zz_ef_ep_current_account"'),
    ('text = "[GetPlayer.MakeScope.ScriptValue(\'trade_balance_in_gold_fixe_sv\')|+D] [GetPlayer.GetCustom(\'monetary_system\')]"',
     'text = "' + SV.format("zz_ef_v_f_ext_net") + '"\n\t\t\t\t\t\t\t\t\ttooltip = "zz_ef_ep_current_account_tt"'),
    ('text = "trade_balance_in_gold_delta_text"', 'text = "' + SV.format("zz_ef_v_f_trade") + '"\n\t\t\t\t\t\t\t\t\ttooltip = "zz_ef_ep_trade_tt"'),
    ("text = \"[GetPlayer.MakeScope.ScriptValue('debt_in_national_currency_in_gold')|-D] [GetPlayer.GetCustom('monetary_system')] "
     "([GetPlayer.MakeScope.ScriptValue('debt_in_national_currency')|+D] [GetPlayer.GetCustom('currency_symbol')])\"",
     'text = "' + SV.format("zz_ef_trade_imports_week") + '"'),
    ('text = "import_value_in_gold_week_fix"', 'text = "zz_ef_ep_week_market_prices"'),
    ('text = "export_value_in_gold_week_fix"', 'text = "zz_ef_ep_week_market_prices"'),
    # П.8 (4.10, В.5): "currency in the trade balance" (E&F's trade reserve, zeroed by В2.1 -- empty) -> the CB's
    # foreign currency by currency (tools/regen_ef_clearing.py: zz_ef_cbfx_*, scripted GUI zz_ef_cbfx_update)
    ('text = "import_export_value_in_currency_in_reeserve_panel"',
     'text = "zz_ef_ep_cbfx_title"\n\t\t\t\t\t\t\t\ttooltip = "zz_ef_ep_cbfx_tt"'),
    # П.16: sorted by value in gold; П.18: the holders of our currency for the pie chart
    ("GetScriptedGui('update_import_export_value_in_currency_in_reeserve_liste').Execute( GuiScope.SetRoot(GetPlayer.MakeScope).End)]\"",
     "GetScriptedGui('zz_ef_cbfx_update_sorted').Execute( GuiScope.SetRoot(GetPlayer.MakeScope).End)]\"\n"
     "\t\t\t\t\t\t\t\tonclick = \"[GetScriptedGui('zz_ef_holders_update').Execute( GuiScope.SetRoot(GetPlayer.MakeScope).End)]\""),
    ("GetGlobalList('import_export_value_in_currency_in_reeserve')", "GetGlobalList('zz_ef_cbfx_list')"),
    ("Scope.GetFlagName,'_money_value'))]\"", "Scope.GetFlagName,'_zz_cbfx_units'))]\""),
    ("Scope.GetFlagName,'_stockpiling_currency_state'))]\"", "Scope.GetFlagName,'_zz_cbfx_money'))]\""),
    ("Scope.GetFlagName,'_currency_state_in_gold'))]\"", "Scope.GetFlagName,'_zz_cbfx_gold'))]\""),
]
# the export value line: E&F's text ends differently, matched by its script value
EXPORT_RE = re.compile(r'text = "\[GetPlayer\.MakeScope\.ScriptValue\(\'excess_foreign_state_currency_in_gold\'\)\|\+D\][^"\n]*"')

def _sv(n):
    return "[GetPlayer.MakeScope.ScriptValue('" + n + "')|D+=] [GetPlayer.GetCustom('currency_symbol')]"


# П.17 (4.10): the balance of payments of the week (the same numbers as the money tooltip's "external sector" card)
BOP_RU = "\\n".join([
    "#b Платёжный баланс за неделю#!",
    "Текущий счёт: " + _sv("zz_ef_bop_current"),
    "  торговля товарами " + _sv("zz_ef_v_f_trade"),
    "  первичные доходы (дивиденды, проценты) " + _sv("zz_ef_bop_primary"),
    "  вторичные доходы (статьи бюджета с заграницей) " + _sv("zz_ef_bop_secondary"),
    "Финансовый счёт (облигации других стран): " + _sv("zz_ef_bop_financial"),
    "#b Сальдо " + _sv("zz_ef_v_f_ext_net") + "#! → мировой клиринг",
    "Резервные активы: " + _sv("zz_ef_v_f_clr_reserves_money") + " (металл " + _sv("zz_ef_v_f_clr_metal_money")
    + ", валюта " + _sv("zz_ef_v_f_clr_fx_money") + ")",
    "  не сведено клирингом " + _sv("zz_ef_v_f_clr_unsettled"),
    "#b Чистая международная позиция " + _sv("zz_ef_abroad_net") + "#!",
])
BOP_EN = "\\n".join([
    "#b Balance of payments this week#!",
    "Current account: " + _sv("zz_ef_bop_current"),
    "  goods trade " + _sv("zz_ef_v_f_trade"),
    "  primary income (dividends, interest) " + _sv("zz_ef_bop_primary"),
    "  secondary income (budget lines with abroad) " + _sv("zz_ef_bop_secondary"),
    "Financial account (other countries' bonds): " + _sv("zz_ef_bop_financial"),
    "#b Balance " + _sv("zz_ef_v_f_ext_net") + "#! → the world clearing",
    "Reserve assets: " + _sv("zz_ef_v_f_clr_reserves_money") + " (metal " + _sv("zz_ef_v_f_clr_metal_money")
    + ", currency " + _sv("zz_ef_v_f_clr_fx_money") + ")",
    "  not settled by the clearing " + _sv("zz_ef_v_f_clr_unsettled"),
    "#b Net international position " + _sv("zz_ef_abroad_net") + "#!",
])

LOC = {
    "russian": {
        "zz_ef_ep_current_account": "Текущий счёт за неделю",
        "zz_ef_ep_current_account_tt": "Чистый поток с заграницей за неделю — то же число, что «итого» в карточке «Заграница» подсказки денежной массы: статьи бюджета с заграницей, торговый баланс рынка, дивиденды из-за рубежа, покупка чужих облигаций. ЦБ сводит его через мировой клиринг на следующем недельном шаге: отток — металлом (доля по доверию к валюте) и нашей валютой, приток — металлом и валютами плательщиков.",
        "zz_ef_ep_trade_tt": "Торговый баланс рынка за неделю: экспорт − импорт всех товаров по ценам рынка (в деньгах движка).",
        "zz_ef_ep_week_market_prices": "за неделю, по ценам рынка",
        "zz_ef_ep_cbfx_units": "Количество",
        "zz_ef_ep_cbfx_money": "В наших деньгах",
        "zz_ef_ep_cbfx_gold": "В золоте (за неделю)",
        "zz_ef_ep_holders_title": "У кого наша валюта",
        "zz_ef_ep_bank_holders_title": "У каких банков наша валюта",
        "zz_ef_ep_bop": BOP_RU,
    },
    "english": {
        "zz_ef_ep_current_account": "Current account, a week",
        "zz_ef_ep_current_account_tt": "The week's net flow with abroad — the same number as the 'net' line of the 'Abroad' card in the money supply tooltip: budget lines with abroad, the market's trade balance, dividends from abroad, foreign bonds bought. The CB settles it through the world clearing at the next weekly step: an outflow in metal (the share by trust in the currency) and our currency, an inflow in the payers' metal and currencies.",
        "zz_ef_ep_trade_tt": "The market's trade balance this week: exports − imports of all goods at the market's prices (engine money).",
        "zz_ef_ep_week_market_prices": "a week, at the market's prices",
        "zz_ef_ep_cbfx_units": "Units",
        "zz_ef_ep_cbfx_money": "In our money",
        "zz_ef_ep_cbfx_gold": "In gold (a week)",
        "zz_ef_ep_holders_title": "Who holds our currency",
        "zz_ef_ep_bank_holders_title": "Which banks hold our currency",
        "zz_ef_ep_bop": BOP_EN,
    },
}
LANGS = ["english", "russian", "braz_por", "french", "german", "japanese",
         "korean", "polish", "simp_chinese", "spanish", "turkish"]


def extract(src: str) -> str:
    m = re.search(r"^\ttype " + TYPE + r" = ", src, re.M)
    assert m, TYPE
    i = src.index("{", m.start())
    d = 0
    for j in range(i, len(src)):
        d += {"{": 1, "}": -1}.get(src[j], 0)
        if d == 0:
            return src[m.start() + 1:j + 1]   # without the leading tab
    raise AssertionError(TYPE)


def block_end(text: str, i: int) -> int:
    """The index after the brace block that starts at the first "{" at or after i."""
    j = text.index("{", i)
    d = 0
    for k in range(j, len(text)):
        d += {"{": 1, "}": -1}.get(text[k], 0)
        if d == 0:
            return k + 1
    raise AssertionError(i)


def post(body: str) -> str:
    # П.16 (4.10): "currency in the trade balance" by currency type (E&F's per-currency counters, zeroed by В2.1 --
    # one group "country without currency -- balance 0.00" was left) -> the balance of payments of the week (П.17)
    i = body.index('text = "trade_routes"')
    w0 = body.rindex("widget = {", 0, i)
    w1 = block_end(body, w0)
    f0 = body.index("flowcontainer = {", w1)
    assert "GetGlobalList('import_export_value_in_currency')" in body[f0:block_end(body, f0)]
    f1 = block_end(body, f0)
    bop = ('textbox = {\n\t\t\t\t\t\t\t\tusing = fontsize_large\n\t\t\t\t\t\t\t\tmultiline = yes\n\t\t\t\t\t\t\t\tautoresize = yes\n'
           '\t\t\t\t\t\t\t\tminimumsize = { 500 -1 }\n\t\t\t\t\t\t\t\tmaximumsize = { 500 -1 }\n\t\t\t\t\t\t\t\tparentanchor = hcenter\n'
           '\t\t\t\t\t\t\t\talign = left|nobaseline\n\t\t\t\t\t\t\t\ttext = "zz_ef_ep_bop"\n\t\t\t\t\t\t\t}')
    body = body[:w0] + bop + body[f1:]
    # П.16: the CB-by-currency table's columns: currency | units | in our money | in gold (week)
    i = body.index('text = "CURRENCY"')
    for old, new in (('text = "in_currency"', 'text = "zz_ef_ep_cbfx_units"'), ('text = "in_currency"', 'text = "zz_ef_ep_cbfx_money"'),
                     ('text = "in_mettal"', 'text = "zz_ef_ep_cbfx_gold"')):
        k = body.index(old, i)
        body = body[:k] + new + body[k + len(old):]
        i = k
    # П.18: the pie chart "who holds our currency" at the top of the CB-by-currency section
    a = ("visible = \"[GetVariableSystem.Exists('import_export_value_in_currency_in_reeserve')]\"\n\n"
         "\t\t\t\t\t\t\tdirection = vertical\n")
    assert body.count(a) == 1, body.count(a)
    # Е.2: under it, the private banks holding our currency
    body = body.replace(a, a + "\n\t\t\t\t\t\t\tzz_ef_holders_piechart = {}\n\t\t\t\t\t\t\tzz_ef_bank_holders_piechart = {}\n")
    # П.18: E&F's "currency reserves" section (its currency-good stocks; the pies were one red square) hidden --
    # the CB's currencies are the table above, the holders of ours the pie
    a = '\tdefault_header = {\n\t\t\t\tblockoverride "text" {\n\t\t\t\t\ttext = "RESERVE_CURRENCY_TITLE"'
    assert body.count(a) == 1
    body = body.replace(a, '\tdefault_header = {\n\t\t\t\tvisible = no\n\t\t\t\tblockoverride "text" {\n\t\t\t\t\ttext = "RESERVE_CURRENCY_TITLE"')
    a = 'flowcontainer  = {\n\t\t\t\tparentanchor = hcenter\n\t\t\t\tdirection = vertical\n\n\t\t\t\t#currency_reserves ok'
    assert body.count(a) == 1
    body = body.replace(a, 'flowcontainer  = {\n\t\t\t\tvisible = no\n\t\t\t\tparentanchor = hcenter\n\t\t\t\tdirection = vertical\n\n\t\t\t\t#currency_reserves ok')
    return body


PIE = """
	# П.18 (4.10): the other CBs holding our currency (scripted GUI zz_ef_holders_update, var:zz_ef_holds_pc)
	type zz_ef_holders_piechart = chart {
		blockoverride "datamodel" {
			datamodel = "[GetGlobalList('zz_ef_holders_list')]"
		}
		blockoverride "heading" {
			text = "zz_ef_ep_holders_title"
		}
		blockoverride "pieslice" {
			# a float, as vanilla's charts (GetCloutAsFloat); a formatted string drew nothing (run clr3) -- E&F's own pies
			# pass one too and drew a red square
			value = "[FixedPointToFloat(Scope.GetCountry.MakeScope.Var('zz_ef_holds_pc').GetValue)]"
		}
		blockoverride "color" {
			color = "[Scope.GetCountry.GetMapColor]"
		}
		blockoverride "leftside_info" {
			raw_text = "[Scope.GetCountry.GetName]"
		}
		blockoverride "rightside1_info" {
			raw_text = "#bold [Scope.GetCountry.MakeScope.Var('zz_ef_holds_pc').GetValue|D]#! [GetPlayer.GetCustom('currency_symbol')]"
		}
		blockoverride "rightside2_info" {
			raw_text = ""
		}
		blockoverride "pie_item_goto_button" {
			button = {
				using = clean_button
				size = { 100% 100% }
			}
		}
		blockoverride "piechartsize" {
			size = { 200 200 }
		}
		blockoverride "minimumsize" {
			minimumsize = { 100 -1 }
		}
		blockoverride "maxverticalslots" {
			maxverticalslots = 10
		}
	}

	# Е.2 (5.10): E&F's private banks holding our currency (zz_ef_holders_update, company var:zz_ef_bank_holds_pc)
	type zz_ef_bank_holders_piechart = chart {
		blockoverride "datamodel" {
			datamodel = "[GetGlobalList('zz_ef_bank_holders_list')]"
		}
		blockoverride "heading" {
			text = "zz_ef_ep_bank_holders_title"
		}
		blockoverride "pieslice" {
			# a float, as vanilla's charts (GetCloutAsFloat); a formatted string drew nothing (run clr3) -- E&F's own pies
			# pass one too and drew a red square
			value = "[FixedPointToFloat(Scope.GetCompany.MakeScope.Var('zz_ef_bank_holds_pc').GetValue)]"
		}
		blockoverride "color" {
			color = "[Scope.GetCompany.GetCountry.GetMapColor]"
		}
		blockoverride "leftside_info" {
			raw_text = "[Scope.GetCompany.GetNameNoIcon]"
		}
		blockoverride "rightside1_info" {
			raw_text = "#bold [Scope.GetCompany.MakeScope.Var('zz_ef_bank_holds_pc').GetValue|D]#! [GetPlayer.GetCustom('currency_symbol')]"
		}
		blockoverride "rightside2_info" {
			raw_text = ""
		}
		blockoverride "pie_item_goto_button" {
			button = {
				using = clean_button
				size = { 100% 100% }
			}
		}
		blockoverride "piechartsize" {
			size = { 200 200 }
		}
		blockoverride "minimumsize" {
			minimumsize = { 100 -1 }
		}
		blockoverride "maxverticalslots" {
			maxverticalslots = 10
		}
	}
"""


def build(src: str):
    body = extract(src)
    sha = hashlib.sha1(body.encode("utf-8")).hexdigest()[:12]
    for a, b in EDITS:
        assert body.count(a) == 1, (body.count(a), a[:80])
        body = body.replace(a, b)
    hits = EXPORT_RE.findall(body)
    assert len(hits) == 1, hits
    body = body.replace(hits[0], 'text = "' + SV.format("zz_ef_trade_exports_week") + '"')
    body = post(body)
    return body, sha


def write_loc():
    for lang in LANGS:
        d = LOC["russian" if lang == "russian" else "english"]
        p = res(rf"..\_ef\ef hotfix 1.13\localization\{lang}\zz_ef_economy_panel_l_{lang}.yml")
        with open(p, "w", encoding="utf-8-sig", newline="\n") as f:
            f.write(f"l_{lang}:\n" + "".join(f' {k}:0 "{v}"\n' for k, v in d.items()))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    body, sha = build(V.read(EF_GUI))
    if args.check:
        if KNOWN_SHA and sha != KNOWN_SHA:
            print(f"DRIFT: E&F's {TYPE} changed ({sha} != {KNOWN_SHA}), re-check the edits")
            return 1
        print(f"ok, {TYPE} sha {sha}")
        return 0
    out = ("# GENERATED by tools/regen_ef_economy_panel_gui.py -- do not edit by hand.\n"
           f"# UI.8 (4.10): E&F's {TYPE} (gui/00_ef_deported_gui_1.gui) re-issued with the trade\n"
           "# balance block in the money model's numbers (the money supply tooltip's).\n"
           f"# Source type sha: {sha}\n\n"
           "@panel_width = 540\n\n"
           "types zz_ef_economy_panel\n{\n\t" + body + "\n" + PIE + "}\n")
    assert V.brace_balance(out) == 0
    V.write(OUT, out)
    write_loc()
    print(f"wrote {OUT} ({out.count(chr(10))} lines), source sha {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
