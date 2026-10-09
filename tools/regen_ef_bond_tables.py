#!/usr/bin/env python3
"""
Е.6 (5.10, Д.3) -- the bond tables in "Budget -> Finances": who holds our bonds and whose bonds we hold.

Why this exists
---------------
E&F's two blocks -- "Investments in foreign debt" (gold_lent_to_foreign_countries) and "Foreign gold lent
against our debt" (gold_lent_to_us) -- list only the human player's own purchases (seller_country_general_N,
total_bond_value_N); the bonds the AI buys for a country (ai_buy_bond_1..10: ai_seller_country_general_N,
ai_total_bond_value_N) and the private banks' bonds (ai_privat_bank_*_1..25) were in lists hidden by EF.30
(an E&F check failing every frame). The user (4.10) saw "one Portugal 4.40M" while Britain held ~20M of bonds.

What this does
--------------
A scripted GUI zz_ef_bonds_update (root = the player) fills two global lists of countries:
  zz_ef_bt_in_list  -- who holds OUR bonds: other countries' treasuries (their slots naming us as the seller)
                       and their private banks (bank slots whose seller list has us);
  zz_ef_bt_out_list -- whose bonds WE hold: the sellers of our treasury's slots and of our banks' slots.
Per row (variables on the listed country): treasury sum (engine money), its yearly rate and interest a week; banks'
sum and interest a week. R8б.2: the AI's bonds of the treasury and the banks are the register's maps (zz_ef_rq_tr_b,
zz_ef_rq_bk_b); the player's own E&F slots (seller_country_general_N, total_bond_value_N) are still read.
gui/ld_cb_rate_panel.gui (hand-written) puts a button and the two tables under E&F's headers.

Output (fork «E&F: Ledgerdemain», via ld_gen, by entry keys): common/scripted_guis/ld_bond_tables.txt,
common/script_values/ld_bond_tables_values.txt, localization/{english,russian}/ld_bond_tables_l_*.yml.
Reads nothing.
Usage: python3 tools/regen_ef_bond_tables.py [--check]
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ld_gen  # noqa: E402

# hotfix paths; ld_gen writes into the fork (ld_bond_tables.txt, ld_bond_tables_values.txt, ld_bond_tables_l_*.yml)
OUT_SG = "common/scripted_guis/zz_ef_bond_tables.txt"
OUT_SV = "common/script_values/zz_ef_bond_tables_values.txt"
LANGS = ["english", "russian", "braz_por", "french", "german", "japanese",
         "korean", "polish", "simp_chinese", "spanish", "turkish"]
N_STATE = 10   # ai_buy_bond_1..10 and the player's slots 1..10
N_BANK = 25    # ai_privat_bank_*_1..25
VARS = ["zz_ef_bt_t_amt", "zz_ef_bt_t_week", "zz_ef_bt_b_amt", "zz_ef_bt_b_year",
        "zz_ef_bto_t_amt", "zz_ef_bto_t_week", "zz_ef_bto_b_amt", "zz_ef_bto_b_year"]  # in / out rows


def player_slot(n: int, seller: str) -> str:
    """The player's treasury slot n (E&F's buy buttons, outside the ledger) of the scope country bought from `seller`."""
    return (f"\t\t\tif = {{ limit = {{ has_variable = total_bond_value_{n} var:total_bond_value_{n} > 0 "
            f"has_variable = seller_country_general_{n} var:seller_country_general_{n} = {seller} }}\n"
            f"\t\t\t\tchange_variable = {{ name = zz_ef_bt_t_amt add = var:total_bond_value_{n} }}\n"
            f"\t\t\t\tchange_variable = {{ name = zz_ef_bt_t_week add = {{ value = var:interest_per_month_calculated_{n} multiply = 0.25 }} }}\n"
            f"\t\t\t}}\n")


def held_by_other(h: str, amt: str, week: str) -> str:
    """Scope -- another country: its holding of the player's bonds in its map zz_ef_rq_<h>_b."""
    return (f"\t\t\tif = {{\n\t\t\t\tlimit = {{ has_variable_map = zz_ef_rq_{h}_b is_key_in_variable_map = {{ name = zz_ef_rq_{h}_b target = scope:bt_root }} }}\n"
            f"\t\t\t\tzz_ef_rq_get = {{ MAP = zz_ef_rq_{h}_b D = scope:bt_root }}\n"
            f"\t\t\t\tchange_variable = {{ name = {amt} add = var:zz_ef_rq_h }}\n"
            f"\t\t\t\tchange_variable = {{ name = {week} add = {{ value = var:zz_ef_rq_h multiply = scope:bt_root.zz_ef_bl_int_per_part }} }}\n"
            f"\t\t\t}}\n")


def held_by_us(h: str, amt: str, week: str) -> str:
    """The player's map zz_ef_rq_<h>_b: each holding adds to its seller's row."""
    return (f"\t\tif = {{\n\t\t\tlimit = {{ has_variable_map = zz_ef_rq_{h}_b }}\n"
            f"\t\t\tzz_ef_rq_keys_take = {{ MAP = zz_ef_rq_{h}_b }}\n"
            f"\t\t\tevery_in_list = {{\n\t\t\t\tvariable = zz_ef_rq_keys\n\t\t\t\tsave_temporary_scope_as = zz_ef_bt_k\n"
            f"\t\t\t\tscope:bt_root = {{ zz_ef_rq_get = {{ MAP = zz_ef_rq_{h}_b D = scope:zz_ef_bt_k }} }}\n"
            f"\t\t\t\tchange_variable = {{ name = {amt} add = scope:bt_root.var:zz_ef_rq_h }}\n"
            f"\t\t\t\tchange_variable = {{ name = {week} add = {{ value = scope:bt_root.var:zz_ef_rq_h multiply = zz_ef_bl_int_per_part }} }}\n"
            f"\t\t\t\tif = {{ limit = {{ NOT = {{ is_target_in_global_variable_list = {{ name = zz_ef_bt_out_tmp target = this }} }} }} "
            f"add_to_global_variable_list = {{ name = zz_ef_bt_out_tmp target = this }} }}\n"
            f"\t\t\t}}\n\t\t\tclear_variable_list = zz_ef_rq_keys\n\t\t}}\n")


def sgui() -> str:
    out = ["# GENERATED by tools/regen_ef_bond_tables.py -- do not edit by hand.\n"
           "# who holds our bonds (zz_ef_bt_in_list) and whose bonds we hold (zz_ef_bt_out_list), from the register of\n"
           "# claims (maps zz_ef_rq_tr_b, zz_ef_rq_bk_b; ld_claims.txt) and the player's own E&F slots. Rows: variables on the\n"
           "# listed country -- treasury sum and interest a week; banks' sum and interest a week (money). Filled when the player\n"
           "# opens the table (button in Budget -> Finances).\n"
           "zz_ef_bonds_update = {\n\teffect = {\n\t\tsave_scope_as = bt_root\n"
           "\t\tclear_global_variable_list = zz_ef_bt_in_list\n\t\tclear_global_variable_list = zz_ef_bt_out_list\n"
           "\t\tclear_global_variable_list = zz_ef_bt_in_tmp\n\t\tclear_global_variable_list = zz_ef_bt_out_tmp\n"
           "\t\tevery_country = {\n"]
    for v in VARS:
        out.append(f"\t\t\tset_variable = {{ name = {v} value = 0 }}\n")
    out.append("\t\t}\n")
    out.append("\t\t# 1. other countries holding our bonds: their treasury's and banks' maps, the player's slots naming us\n"
               "\t\tevery_country = {\n\t\t\tlimit = { NOT = { this = scope:bt_root } }\n")
    out.append(held_by_other("tr", "zz_ef_bt_t_amt", "zz_ef_bt_t_week"))
    out.append(held_by_other("bk", "zz_ef_bt_b_amt", "zz_ef_bt_b_year"))
    for n in range(1, N_STATE + 1):
        out.append(player_slot(n, "scope:bt_root"))
    out.append("\t\t\tif = { limit = { OR = { var:zz_ef_bt_t_amt > 0 var:zz_ef_bt_b_amt > 0 } } "
               "add_to_global_variable_list = { name = zz_ef_bt_in_tmp target = this } }\n\t\t}\n")
    out.append("\t\t# 2. our bonds of other countries: our maps and our own E&F slots, on the seller's row\n")
    out.append(held_by_us("tr", "zz_ef_bto_t_amt", "zz_ef_bto_t_week"))
    out.append(held_by_us("bk", "zz_ef_bto_b_amt", "zz_ef_bto_b_year"))
    for n in range(1, N_STATE + 1):
        out.append(f"\t\tif = {{ limit = {{ has_variable = seller_country_general_{n} has_variable = total_bond_value_{n} var:total_bond_value_{n} > 0 }}\n"
                   f"\t\t\tvar:seller_country_general_{n} = {{\n"
                   f"\t\t\t\tchange_variable = {{ name = zz_ef_bto_t_amt add = scope:bt_root.var:total_bond_value_{n} }}\n"
                   f"\t\t\t\tchange_variable = {{ name = zz_ef_bto_t_week add = {{ value = scope:bt_root.var:interest_per_month_calculated_{n} multiply = 0.25 }} }}\n"
                   f"\t\t\t\tif = {{ limit = {{ NOT = {{ is_target_in_global_variable_list = {{ name = zz_ef_bt_out_tmp target = this }} }} }} add_to_global_variable_list = {{ name = zz_ef_bt_out_tmp target = this }} }}\n"
                   f"\t\t\t}}\n\t\t}}\n")
    for k in ("in", "out"):
        out.append(f"\t\tordered_in_global_list = {{ variable = zz_ef_bt_{k}_tmp order_by = zz_ef_bt_{k}_key max = 1000 "
                   f"check_range_bounds = no add_to_global_variable_list = {{ name = zz_ef_bt_{k}_list target = this }} }}\n")
    out.append("\t}\n}\n")
    return "".join(out)


LOC = {
    "russian": {
        "zz_ef_bt_button": "Показать",
        "zz_ef_bt_button_tt": "Собрать таблицу облигаций (на сегодня).",
        "zz_ef_bt_in_title": "Кто держит наши облигации (наш долг)",
        "zz_ef_bt_out_title": "Наши облигации других стран (казна и банки)",
        "zz_ef_bt_head": "#grey Страна: казна — сумма, ставка в год, проценты в неделю; банки — сумма, проценты в неделю#!",
        "zz_ef_bt_t_row": "казна [Scope.GetCountry.MakeScope.Var('zz_ef_bt_t_amt').GetValue|D] ¤, ставка "
                          "[Scope.GetCountry.MakeScope.ScriptValue('zz_ef_bt_t_rate')|%1], в неделю "
                          "[Scope.GetCountry.MakeScope.Var('zz_ef_bt_t_week').GetValue|D] ¤",
        "zz_ef_bt_b_row": "банки [Scope.GetCountry.MakeScope.Var('zz_ef_bt_b_amt').GetValue|D] ¤, в неделю "
                          "[Scope.GetCountry.MakeScope.Var('zz_ef_bt_b_year').GetValue|D] ¤",
        "zz_ef_bto_t_row": "казна [Scope.GetCountry.MakeScope.Var('zz_ef_bto_t_amt').GetValue|D] ¤, ставка "
                          "[Scope.GetCountry.MakeScope.ScriptValue('zz_ef_bto_t_rate')|%1], в неделю "
                          "[Scope.GetCountry.MakeScope.Var('zz_ef_bto_t_week').GetValue|D] ¤",
        "zz_ef_bto_b_row": "банки [Scope.GetCountry.MakeScope.Var('zz_ef_bto_b_amt').GetValue|D] ¤, в неделю "
                          "[Scope.GetCountry.MakeScope.Var('zz_ef_bto_b_year').GetValue|D] ¤",
        "zz_ef_bt_empty": "#grey (нет — или нажмите «Показать»)#!",
    },
    "english": {
        "zz_ef_bt_button": "Show",
        "zz_ef_bt_button_tt": "Fill the bond table (as of today).",
        "zz_ef_bt_in_title": "Who holds our bonds (our debt)",
        "zz_ef_bt_out_title": "Our bonds of other countries (treasury and banks)",
        "zz_ef_bt_head": "#grey Country: treasury — sum, yearly rate, interest a week; banks — sum, interest a week#!",
        "zz_ef_bt_t_row": "treasury [Scope.GetCountry.MakeScope.Var('zz_ef_bt_t_amt').GetValue|D] ¤, rate "
                          "[Scope.GetCountry.MakeScope.ScriptValue('zz_ef_bt_t_rate')|%1], a week "
                          "[Scope.GetCountry.MakeScope.Var('zz_ef_bt_t_week').GetValue|D] ¤",
        "zz_ef_bt_b_row": "banks [Scope.GetCountry.MakeScope.Var('zz_ef_bt_b_amt').GetValue|D] ¤, a week "
                          "[Scope.GetCountry.MakeScope.Var('zz_ef_bt_b_year').GetValue|D] ¤",
        "zz_ef_bto_t_row": "treasury [Scope.GetCountry.MakeScope.Var('zz_ef_bto_t_amt').GetValue|D] ¤, rate "
                          "[Scope.GetCountry.MakeScope.ScriptValue('zz_ef_bto_t_rate')|%1], a week "
                          "[Scope.GetCountry.MakeScope.Var('zz_ef_bto_t_week').GetValue|D] ¤",
        "zz_ef_bto_b_row": "banks [Scope.GetCountry.MakeScope.Var('zz_ef_bto_b_amt').GetValue|D] ¤, a week "
                          "[Scope.GetCountry.MakeScope.Var('zz_ef_bto_b_year').GetValue|D] ¤",
        "zz_ef_bt_empty": "#grey (none — or press 'Show')#!",
    },
}
# the treasury's sums are E&F's purchase prices in the engine's money; the player's currency symbol
CUR = "[GetPlayer.GetCustom('currency_symbol')]"

SV = """
# the rows' order -- treasury sum + banks' sum (money)
zz_ef_bt_in_key = {
	value = 0
	if = { limit = { has_variable = zz_ef_bt_t_amt } add = var:zz_ef_bt_t_amt }
	if = { limit = { has_variable = zz_ef_bt_b_amt } add = var:zz_ef_bt_b_amt }
}
zz_ef_bt_out_key = {
	value = 0
	if = { limit = { has_variable = zz_ef_bto_t_amt } add = var:zz_ef_bto_t_amt }
	if = { limit = { has_variable = zz_ef_bto_b_amt } add = var:zz_ef_bto_b_amt }
}
# the row's yearly rate on the treasury's bonds (interest a week x 52 / sum)
zz_ef_bt_t_rate = {
	value = 0
	if = {
		limit = { has_variable = zz_ef_bt_t_amt var:zz_ef_bt_t_amt > 0 has_variable = zz_ef_bt_t_week }
		value = var:zz_ef_bt_t_week
		multiply = 52
		divide = var:zz_ef_bt_t_amt
	}
}
zz_ef_bto_t_rate = {
	value = 0
	if = {
		limit = { has_variable = zz_ef_bto_t_amt var:zz_ef_bto_t_amt > 0 has_variable = zz_ef_bto_t_week }
		value = var:zz_ef_bto_t_week
		multiply = 52
		divide = var:zz_ef_bto_t_amt
	}
}
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.parse_args()
    text = sgui()
    assert text.count("{") == text.count("}")
    ld_gen.emit(OUT_SG, text)
    ld_gen.emit(OUT_SV, "# GENERATED by tools/regen_ef_bond_tables.py -- do not edit by hand.\n" + SV)
    for lang in LANGS:
        d = LOC["russian" if lang == "russian" else "english"]
        lines = [f"l_{lang}:\n"] + [f' {k}:0 "{v.replace("¤", CUR)}"\n' for k, v in d.items()]
        ld_gen.emit(f"localization/{lang}/zz_ef_bond_tables_l_{lang}.yml", "".join(lines))
    ld_gen.report("regen_ef_bond_tables")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
