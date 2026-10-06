#!/usr/bin/env python3
"""
Д2.4 (5.10.2026) -- the banks' seed: scripted_effects/ld_bank_seed.txt of the fork «E&F: Ledgerdemain» (via ld_gen:
written by entry keys).

Banks (building_zz_ef_bank) make the bank settlements (the former E&F currency good) that used to come from the
central bank from day one. The user (5.10): enough banks to cover the initial demand; spread over the states with
trade centres, not only the capital; owned by the population and by companies.

How (once per market, by its owner, in the owner's first monthly pulse):
  * levels wanted L = (the market's buy orders of liquidity_currency x 1.2 - its sell orders) / 500 (Д2.8, 5.10: the
    counting house's 500 a level -- a new bank starts with the money changer, 300, and the AI moves it to a counting
    house where there is paper; until 5.10 the divisor was 300 and the seed overshot; the sell orders are what trade
    centres already make -- they produce settlements too);
  * spread over the market's states (every country on the market) by their trade centre levels; a market with no
    trade centre -- the owner's capital;
  * in each state one create_building, the largest ladder size not above its share (calling create_building
    again on a standing building adds no levels -- run r1005_192418);
  * owners: 40% an E&F bank company of the state's owner if it has one, the rest the state -- sold by the AI to
    private owners (ai_nationalization_desire -5 on the building; run r1005_194935: in a year and a half 339 of
    1097 state levels went to financial districts and companies). A company type cannot be a variable, so the
    company is a macro argument: one ladder per bank company (the 98 of zz_ef_cm_companies.txt).
    The financial district cannot be the seed's owner: it needs a literal region -- `region = scope:...` is
    refused ("Failed to read key reference", run r1005_201105), and the state's region would take a dispatcher of
    ~700 regions x 98 companies x the ladder.
Reads the fork: the bank companies are the ones of common/company_types/00_ef_companies.txt that list
building_zz_ef_bank (the 98).
Logged per state: EFK|date|country|state|want N|tc T|built B.

Usage:
    py tools/regen_ef_bank_seed.py            # write
    py tools/regen_ef_bank_seed.py --check    # exit 1 if the fork file differs
"""

from __future__ import annotations

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ld_gen  # noqa: E402

OUT = "common/scripted_effects/zz_ef_bank_seed.txt"      # путь хотфикса; ld_gen пишет в форк ld_bank_seed.txt
COMPANIES = os.path.join(ld_gen.FORK, "common", "company_types", "00_ef_companies.txt")

BANKS = [
    "company_BancoNacionArgentina",
    "company_BancoProvincia",
    "company_OesterreichischeNationalbank",
    "company_BayerischeHypothekenUndWechselBank",
    "company_BanqueNationaleDeBelgique",
    "company_ImperialBankofIndia",
    "company_BancoNacionalDeBolivia",
    "company_BancoDoBrasil",
    "company_CanadianImperialBankOfCommerce",
    "company_DaQingBank",
    "company_BankHSBC",
    "company_BancoEstado",
    "company_BancoDeValparaiso",
    "company_BancoRepublicaColombia",
    "company_BancoCentralDeCostaRica",
    "company_BancoEspanolDeLaHabana",
    "company_LandmandsBanken",
    "company_BanqueEgyptienne",
    "company_BanqueDeFrance",
    "company_BankofEngland",
    "company_Reichsbank",
    "company_PreussischeSeehandlung",
    "company_bankofgreec",
    "company_BancoCentralDeGuatemala",
    "company_BancoCentralDeHonduras",
    "company_BancaDItalia",
    "company_Rothschild_Bank_ita",
    "company_BankOfJapan",
    "company_Mitsubishiexchangehousebank",
    "company_BancoDeMexico",
    "company_DeNederlandscheBank",
    "company_ChristianiaBank",
    "company_ColonialBankOfAustralia",
    "company_RoyalBankofCanada",
    "company_BancoNacionalDePanama",
    "company_BankMelliIran",
    "company_ImperialBankofPersia",
    "company_BancoDePortugal",
    "company_BancoNacionalDelParaguay",
    "company_BankOfMontreal",
    "company_StateBankRussianEmpire",
    "company_BankSBoBSA",
    "company_CassaDiRisparmioDiTorino",
    "company_BankofSpain",
    "company_HandelsBanken",
    "company_Bankenverein",
    "company_OttomanBank",
    "company_BancoCentralDelUruguay",
    "company_BancoCentralDeVenezuela",
    "company_BankJPMorgan",
    "company_BankGoldmanSachs",
    "company_ChaseBank",
    "company_BankWellsFargo",
    "company_BankAmericanExpress",
    "company_amsterdamschebank",
    "company_RotterdamscheBankvereeniging",
    "company_SocieteGeneraledeBelgique",
    "company_BanqueDeBruxelles",
    "company_BancoDeBilbao",
    "company_BancoHispanoColonial",
    "company_BancoCommercialPortugues",
    "company_Bank_Ultramarino",
    "company_BancaCommercialeItaliana",
    "company_LloydsBank",
    "company_barclaysBank",
    "company_NationalWestminsterBank",
    "company_RoyalBankOfScotland",
    "company_Rothschild_Bank_gbr",
    "company_BankCreditLyonnais",
    "company_SocieteGenerale",
    "company_BanqueDeParisEtDesPaysBas",
    "company_Rothschild_Bank_fra",
    "saint_petersburg_international_commercial_bank",
    "russo_chinese_bank",
    "company_DeutscheBank",
    "company_Rothschild_Bank_ger",
    "company_OesterreichischeCreditAnstalt",
    "company_WienerBankverein",
    "company_Rothschild_Bank_aus",
    "company_TurkishZiraatBankasi",
    "company_BanqueImperialeOttomane",
    "company_BankTejaratPersia",
    "company_BankAngloPersian",
    "company_ChohungBank",
    "company_BankIBC",
    "company_BankBOCOM",
    "company_SumitomoBank",
    "company_BankOfIndiaCompany",
    "company_BankOfBombay",
    "company_BankDesjardins",
    "company_NationalBankOfAustralia",
    "company_SouthAustralianBank",
    "company_bancodelondresmexico",
    "company_BancoMercantilMexicano",
    "company_BancoMercantil",
    "company_BancoCommercialDoBrasil",
    "company_BancoHipotecarioNacional",
    "company_BancoDeChile",
]

SIZES = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 18, 22, 26, 30, 35, 40, 50, 60, 70, 80, 100, 120, 150, 200]
COMPANY_SHARE = 0.4

HEADER = """\
# GENERATED by tools/regen_ef_bank_seed.py -- do not edit by hand.
#############################################
# Д2.4 (5.10.2026) -- the banks' seed, once per market, by its owner (on_actions/zz_ef_bank_on_actions.txt):
# bank settlements (the former currency good) used to come from the central bank from day one. Levels = (the
# market's buy orders x 1.2 - sell orders, trade centres make some) / 500, spread over the market's states by trade centre levels; owners 40% the owner's
# E&F bank company, the rest the state (the AI sells it to private owners). Why so: the generator's docstring.
#############################################

"""


def banks() -> list[str]:
    """BANKS (the order is the seed's: the first company the owner has gets the bank), checked against the fork's
    00_ef_companies.txt: exactly its companies that list building_zz_ef_bank."""
    s = open(COMPANIES, encoding="utf-8-sig").read()
    found = set()
    for m in re.finditer(r"(?m)^(\w+)\s*=\s*\{", s):
        nxt = re.search(r"(?m)^\S", s[m.end():])
        body = s[m.end(): m.end() + nxt.start()] if nxt else s[m.end():]
        if re.search(r"(?m)^\s*building_zz_ef_bank\b", body):
            found.add(m.group(1))
    assert found == set(BANKS) and len(BANKS) == 98, (found ^ set(BANKS))
    return BANKS


def split(size: int, with_company: bool) -> tuple[int, int]:
    """(company, state) levels."""
    if not with_company:
        return 0, size
    c = int(size * COMPANY_SHARE)
    return c, size - c


def ladder(owner_block) -> str:
    """Flat if/else_if over SIZES (largest first) on scope:zz_ef_bank_s.var:zz_ef_bank_n -- state scope."""
    out = []
    for i, size in enumerate(sorted(SIZES, reverse=True)):
        kw = "if" if i == 0 else "else_if"
        out.append(f"\t{kw} = {{\n\t\tlimit = {{ var:zz_ef_bank_n >= {size} }}\n"
                   f"\t\tcreate_building = {{\n\t\t\tbuilding = building_zz_ef_bank\n\t\t\treserves = 0\n"
                   f"\t\t\tadd_ownership = {{\n{owner_block(size)}\t\t\t}}\n\t\t}}\n\t}}\n")
    return "".join(out)


def company(levels: int) -> str:
    return ("\t\t\t\tcompany = {\n\t\t\t\t\ttype = $COMPANY$\n\t\t\t\t\tcountry = scope:zz_ef_bank_o\n"
            f"\t\t\t\t\tlevels = {levels}\n\t\t\t\t}}\n")


def country(levels: int) -> str:
    return f"\t\t\t\tcountry = {{\n\t\t\t\t\tcountry = scope:zz_ef_bank_o\n\t\t\t\t\tlevels = {levels}\n\t\t\t\t}}\n"


def with_company_block(size: int) -> str:
    c, f = split(size, True)
    return (company(c) if c else "") + country(f)


def build() -> str:
    keys = banks()
    o = [HEADER]

    # market owner: the market's levels and trade centre weight, then every state of the market
    o.append("""\
### COUNTRY scope (the market owner), monthly; once.
zz_ef_bank_seed_step = {
	if = {
		limit = {
			NOT = { has_variable = zz_ef_bank_seeded }
			exists = market
			market.owner = this
		}
		set_variable = zz_ef_bank_seeded
		save_scope_as = zz_ef_bank_m
		set_variable = {
			name = zz_ef_bank_l
			value = {
				value = market.mg:liquidity_currency.market_goods_buy_orders
				multiply = 1.2
				subtract = market.mg:liquidity_currency.market_goods_sell_orders
				min = 0
				divide = 500
			}
		}
		set_variable = { name = zz_ef_bank_w value = 0 }
		every_country = {
			limit = { exists = market market.owner = scope:zz_ef_bank_m }
			every_scope_state = {
				scope:zz_ef_bank_m = { change_variable = { name = zz_ef_bank_w add = prev.zz_ef_bank_tc_levels } }
			}
		}
		debug_log = "EFK|[TimeKeeper.GetCurrentDate.GetString]|[THIS.GetCountry.GetNameNoFormatting]|market|levels [THIS.GetCountry.MakeScope.Var('zz_ef_bank_l').GetValue|1]|tc [THIS.GetCountry.MakeScope.Var('zz_ef_bank_w').GetValue|0]"
		if = {
			limit = { var:zz_ef_bank_w > 0 }
			every_country = {
				limit = { exists = market market.owner = scope:zz_ef_bank_m }
				every_scope_state = {
					limit = { zz_ef_bank_tc_levels > 0 }
					set_variable = {
						name = zz_ef_bank_n
						value = {
							value = scope:zz_ef_bank_m.var:zz_ef_bank_l
							multiply = zz_ef_bank_tc_levels
							divide = scope:zz_ef_bank_m.var:zz_ef_bank_w
						}
					}
					zz_ef_bank_seed_state = yes
				}
			}
		}
		else = {
			capital = {
				set_variable = { name = zz_ef_bank_n value = scope:zz_ef_bank_m.var:zz_ef_bank_l }
				zz_ef_bank_seed_state = yes
			}
		}
	}
}

### STATE scope, var:zz_ef_bank_n = the levels wanted here.
zz_ef_bank_seed_state = {
	if = {
		limit = { var:zz_ef_bank_n >= 1 }
		save_scope_as = zz_ef_bank_s
		owner = { save_scope_as = zz_ef_bank_o }
		owner = { set_variable = zz_ef_bank_nocomp }
""")
    for k in keys:
        o.append(f"""\
		if = {{
			limit = {{ owner = {{ has_variable = zz_ef_bank_nocomp has_company = company_type:{k} }} }}
			owner = {{ remove_variable = zz_ef_bank_nocomp }}
			zz_ef_bank_seed_company = {{ COMPANY = {k} }}
		}}
""")
    o.append("""\
		if = {
			limit = { owner = { has_variable = zz_ef_bank_nocomp } }
			owner = { remove_variable = zz_ef_bank_nocomp }
			zz_ef_bank_seed_state_owned = yes
		}
		if = {
			limit = { NOT = { has_building = building_zz_ef_bank } }
			zz_ef_bank_seed_state_owned = yes
		}
		debug_log = "EFK|[TimeKeeper.GetCurrentDate.GetString]|[THIS.GetState.GetOwner.GetNameNoFormatting]|[THIS.GetState.GetNameNoFormatting]|want [THIS.GetState.MakeScope.Var('zz_ef_bank_n').GetValue|1]|tc [THIS.GetState.MakeScope.ScriptValue('zz_ef_bank_tc_levels')|0]|built [THIS.GetState.MakeScope.ScriptValue('zz_ef_bank_levels')|0]"
	}
	remove_variable = zz_ef_bank_n
}

""")
    o.append("### STATE scope; $COMPANY$ = an E&F bank company of the owner.\nzz_ef_bank_seed_company = {\n")
    o.append(ladder(with_company_block))
    o.append("}\n\n### STATE scope; no bank company (and the fallback): state-owned, sold by the AI.\nzz_ef_bank_seed_state_owned = {\n")
    o.append(ladder(lambda s: country(s)))
    o.append("}\n")
    return "".join(o)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.parse_args()
    text = build()
    assert text.count("{") == text.count("}")
    ld_gen.emit(OUT, text)
    ld_gen.report("regen_ef_bank_seed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
