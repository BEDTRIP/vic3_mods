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
    ("GetScriptedGui('update_import_export_value_in_currency_in_reeserve_liste')", "GetScriptedGui('zz_ef_cbfx_update')"),
    ("GetGlobalList('import_export_value_in_currency_in_reeserve')", "GetGlobalList('zz_ef_cbfx_list')"),
    ("Scope.GetFlagName,'_money_value'))]\"", "Scope.GetFlagName,'_zz_cbfx_units'))]\""),
    ("Scope.GetFlagName,'_stockpiling_currency_state'))]\"", "Scope.GetFlagName,'_zz_cbfx_money'))]\""),
    ("Scope.GetFlagName,'_currency_state_in_gold'))]\"", "Scope.GetFlagName,'_zz_cbfx_gold'))]\""),
]
# the export value line: E&F's text ends differently, matched by its script value
EXPORT_RE = re.compile(r'text = "\[GetPlayer\.MakeScope\.ScriptValue\(\'excess_foreign_state_currency_in_gold\'\)\|\+D\][^"\n]*"')

LOC = {
    "russian": {
        "zz_ef_ep_current_account": "Текущий счёт за неделю",
        "zz_ef_ep_current_account_tt": "Чистый поток с заграницей за неделю — то же число, что «итого» в карточке «Заграница» подсказки денежной массы: статьи бюджета с заграницей, торговый баланс рынка, дивиденды из-за рубежа, покупка чужих облигаций. ЦБ сводит его через мировой клиринг на следующем недельном шаге: отток — металлом (доля по доверию к валюте) и нашей валютой, приток — металлом и валютами плательщиков.",
        "zz_ef_ep_trade_tt": "Торговый баланс рынка за неделю: экспорт − импорт всех товаров по ценам рынка (в деньгах движка).",
        "zz_ef_ep_week_market_prices": "за неделю, по ценам рынка",
    },
    "english": {
        "zz_ef_ep_current_account": "Current account, a week",
        "zz_ef_ep_current_account_tt": "The week's net flow with abroad — the same number as the 'net' line of the 'Abroad' card in the money supply tooltip: budget lines with abroad, the market's trade balance, dividends from abroad, foreign bonds bought. The CB settles it through the world clearing at the next weekly step: an outflow in metal (the share by trust in the currency) and our currency, an inflow in the payers' metal and currencies.",
        "zz_ef_ep_trade_tt": "The market's trade balance this week: exports − imports of all goods at the market's prices (engine money).",
        "zz_ef_ep_week_market_prices": "a week, at the market's prices",
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


def build(src: str):
    body = extract(src)
    sha = hashlib.sha1(body.encode("utf-8")).hexdigest()[:12]
    for a, b in EDITS:
        assert body.count(a) == 1, (body.count(a), a[:80])
        body = body.replace(a, b)
    hits = EXPORT_RE.findall(body)
    assert len(hits) == 1, hits
    body = body.replace(hits[0], 'text = "' + SV.format("zz_ef_trade_exports_week") + '"')
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
           "types zz_ef_economy_panel\n{\n\t" + body + "\n}\n")
    assert V.brace_balance(out) == 0
    V.write(OUT, out)
    write_loc()
    print(f"wrote {OUT} ({out.count(chr(10))} lines), source sha {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
