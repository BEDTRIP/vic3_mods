#!/usr/bin/env python3
"""
EF.39 / EF.44 / EF.48 -- the "Money Supply" tooltip as M0 / M1 / M2, with a
card per account: every transfer of the week from and to each other account.

E&F's tooltip is 12 localization keys MONEY_SUPPLY_DESC_* (one per monetary
standard, AI and player variants), all the same text except the data context
(Country / GetPlayer). The hotfix changed the composition of the money supply
(script_values/zz_ef_money_model_values.txt), so the text is rewritten. Each
account line is a nested tooltip (#tooltippable;tooltip:[X.GetTooltipTag],key
...#!) with the account's card; the nested keys read Country.* (the tag passes
the country).

EF.48 (2026-09-30, evening revision): everything in the ENGINE'S money.
Money = treasury (M0) + businesses' cash (M1) + the pool (M2) -- exact engine
numbers. Pops, the central bank (in money) and abroad hold no stock: money
passes through them (pops' income goes to taxes and purchases, the rest
becomes wealth, i.e. leaves the money). E&F's central-bank "reserves" and
currency-good flows are counts of a good, shown in a separate card. Each
transfer is ONE entry (FLOWS: from, to, label, value) and shows in both cards
with opposite signs. Values come from the budget through GUI data functions
(GetTrendValue(Country.Get...Trend)) -- exact per budget line, costing
nothing unless the tooltip is open -- and from the model's script values.
"Other" = the account's change minus everything listed, computed in the GUI;
pops close with "purchases and wealth growth".

Per WEEK, as the engine's budget counts (the user, 2026-09-30: a monthly step
against weekly budget lines did not add up -- the pool's card missed ~1M a
month). The model steps weekly right after the budget tick; M0/M1/M2 show the
week's change and % over a month, a year and 5 years. E&F's currency good
moves monthly, its card stays monthly.

The GUI bridge (2026-09-30): the budget's lines outside the accounts are
GUI-only, so gui/zz_ef_money_hook.gui (generated here too, with its
scripted_widgets entry) reads them for every country queued by the weekly
step and executes scripted_guis/zz_ef_money_hook.txt with their sum
(MakeScopeValue) -- BPM's pattern. The script then computes the week's leak.

Writes _ef/ef hotfix 1.13/localization/<lang>/replace/
zz_ef_money_supply_replace_l_<lang>.yml (UTF-8 with BOM; RU and EN written,
the other 9 languages get EN).

Usage:
    py tools/regen_ef_money_supply_loc.py
"""
import collections
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
HOTFIX = os.path.normpath(os.path.join(HERE, r"..\_ef\ef hotfix 1.13"))
ROOT = os.path.join(HOTFIX, "localization")
LANGS = ["english", "russian", "braz_por", "french", "german", "japanese",
         "korean", "polish", "simp_chinese", "spanish", "turkish"]

KEYS_COUNTRY = ["MONEY_SUPPLY_DESC_fiat_standard", "MONEY_SUPPLY_DESC_silver_standard",
                "MONEY_SUPPLY_DESC_bimetallism_standard", "MONEY_SUPPLY_DESC_gold_standard",
                "MONEY_SUPPLY_DESC_MONEY_VALUE_gold_exchange_standard", "MONEY_SUPPLY_DESC_MONEY_VALUE_subject"]
KEYS_PLAYER = ["MONEY_SUPPLY_DESC_fiat_Player", "MONEY_SUPPLY_DESC_silver_Player",
               "MONEY_SUPPLY_DESC_bimetallism_Player", "MONEY_SUPPLY_DESC_gold_Player",
               "MONEY_SUPPLY_DESC_MONEY_VALUE_gold_exchange_standard_Player",
               "MONEY_SUPPLY_DESC_MONEY_VALUE_subject_player"]

ZERO = "'(CFixedPoint)0'"


def ctx(c):
    """Formatting helpers for data context c ('Country' or 'GetPlayer')."""
    cur = f"[{c}.GetCustom('currency_symbol')]"

    def sv(name, fmt="D"):
        return f"[{c}.MakeScope.ScriptValue('{name}')|{fmt}]"

    def money(name):
        return f"{sv(name)} {cur}"

    def delta(name):
        return f"{sv(name, 'D+=')}{cur}"

    def tt(key, text):
        return f"#tooltippable;tooltip:[{c}.GetTooltipTag],{key} {text}#!"

    return cur, sv, money, delta, tt


def main_text(lang, c):
    cur, sv, money, delta, tt = ctx(c)
    gold = "@gold!"
    ru = lang == "russian"
    # The user's aggregates (1.10 evening, run 12 -- as in real statistics): M0 = pops' cash at hand, M1 = +
    # business cash, M2 = + pops' deposits, M3 = + claims on abroad. The treasury, the banks' own funds (the pool)
    # and the CB's reserves are accounts outside the money supply. The currency's value and the inflation read M2.
    if ru:
        L = dict(title="Денежная масса", total="Всего (M3)", week="за неделю",
                 m0="M0 = наличные у населения", cash="Наличные на руках", savall="всего накоплений {0}, во вкладах {1}",
                 m1="M1 = M0 + счета предприятий", bld="Касса предприятий", tc="из них торговые центры",
                 m2="M2 = M1 + вклады населения", dep="Вклады в банках",
                 m3="M3 = M2 + заграница", abroad="Заграница",
                 abf="облигации банков {0}, облигации казны {1}",
                 out="Вне денежной массы:", tr="Казна (счёт правительства)",
                 bank="Средства банков (пул)", bankf="из них вклады {0}, долг перед ЦБ {1}",
                 cb="Резервы ЦБ — покрытие валюты, не деньги",
                 cbf="металл по паритету; покрытие M2 {1} (норма 40%; ниже — кредит ЦБ сжимается, при 20% — ноль, сейчас {2} цели); выпущено ЦБ (долг банков) {3}",
                 circ="Курс и инфляция считаются по M2",
                 infl="Инфляция за год", inflf="индекс цен потребительской корзины {2} (100 = базовые цены); для сравнения: рост M2 {0}, рост ВВП {1}",
                 debt="Долги (не деньги)", debtf="бюджета {0}, банков перед ЦБ {1}, потребкредит {2}, бизнеса {3}",
                 hint="Наведите на счёт — все переводы за неделю.",
                 dyn="месяц {0}, год {1}, 5 лет {2}", gdp="к ВВП")
    else:
        L = dict(title="Money Supply", total="Total (M3)", week="this week",
                 m0="M0 = pops' cash", cash="Cash at hand", savall="all savings {0}, in deposits {1}",
                 m1="M1 = M0 + business accounts", bld="Business cash", tc="of it trade centres",
                 m2="M2 = M1 + pops' deposits", dep="Bank deposits",
                 m3="M3 = M2 + abroad", abroad="Abroad",
                 abf="banks' bonds {0}, treasury's bonds {1}",
                 out="Outside the money supply:", tr="Treasury (the government's account)",
                 bank="Bank funds (the pool)", bankf="of it deposits {0}, debt to the CB {1}",
                 cb="CB reserves — the currency's cover, not money",
                 cbf="metal at parity; cover of M2 {1} (normal 40%; under it the CB's credit shrinks, zero at 20%, now {2} of the target); issued by the CB (banks' debt) {3}",
                 circ="The value and the inflation read M2",
                 infl="Inflation, a year", inflf="consumer price index {2} (100 = base prices); for comparison: M2 growth {0}, GDP growth {1}",
                 debt="Debts (not money)", debtf="budget {0}, banks to the CB {1}, consumer credit {2}, business {3}",
                 hint="Hover an account for all its transfers this week.",
                 dyn="month {0}, year {1}, 5 years {2}", gdp="of GDP")

    def ing(name):
        return f" ≈ {sv(name)} {gold}"

    def dyn(k):
        pc = [sv(f"zz_ef_agg{k}_pct_{p}", "+=1%") for p in ("month", "year", "5y")]
        return f"{delta(f'zz_ef_v_d_agg{k}')} {L['week']}; " + L["dyn"].format(*pc)

    def ratio(k):
        return f"{sv(f'zz_ef_agg_m{k}_to_gdp', '%0')} {L['gdp']}"

    lines = [
        f"{L['title']}:",
        f"{L['total']}: #p {money('zz_ef_agg_m3')}#!{ing('zz_ef_agg_m3_gold')}",
        f" {L['m0']}: #T {money('zz_ef_agg_m0')}#! — {ratio(0)} ({dyn(0)})",
        f"  -> {tt('zz_ef_ms_tt_pops', L['cash'])}: #T {money('zz_ef_pop_cash_held')}#! "
        f"({sv('zz_ef_pop_savings_week', 'D+=')}{cur}; "
        + L["savall"].format(money("zz_ef_pop_savings"), money("zz_ef_pop_deposits")) + ")",
        f" {L['m1']}: #T {money('zz_ef_agg_m1')}#! — {ratio(1)} ({dyn(1)})",
        f"  -> {tt('zz_ef_ms_tt_buildings', L['bld'])}: #T {money('zz_ef_building_cash')}#! ({delta('zz_ef_v_d_buildings')}; "
        f"{L['tc']} {money('zz_ef_tc_cash')})",
        f" {L['m2']}: #T {money('zz_ef_agg_m2')}#!{ing('zz_ef_agg_m2_gold')} — {ratio(2)} ({dyn(2)})",
        f"  -> {tt('zz_ef_ms_tt_banks', L['dep'])}: #T {money('zz_ef_pop_deposits')}#!",
        f" {L['m3']}: #T {money('zz_ef_agg_m3')}#! ({dyn(3)})",
        f"  -> {tt('zz_ef_ms_tt_abroad', L['abroad'])}: #T {money('zz_ef_foreign_assets')}#! ({delta('zz_ef_v_d_abroad')}; "
        + L["abf"].format(money("zz_ef_bank_bonds"), money("zz_ef_treasury_bonds")) + ")",
        f"{L['out']}",
        f"  -> {tt('zz_ef_ms_tt_treasury', L['tr'])}: #T {money('zz_ef_treasury')}#! ({delta('zz_ef_v_d_treasury')})",
        f"  -> {tt('zz_ef_ms_tt_banks', L['bank'])}: #T {money('zz_ef_pool')}#! ({delta('zz_ef_v_d_pool')}; "
        + L["bankf"].format(money("zz_ef_pop_deposits"), money("zz_ef_bank_cb_debt")) + ")",
        f"  -> {tt('zz_ef_ms_tt_cb', L['cb'])}: #T {money('zz_ef_cb_money')}#! ({delta('zz_ef_v_d_cbm')}; "
        + L["cbf"].format("", sv("zz_ef_cb_cover", "%0"), sv("zz_ef_cb_cover_credit_mult", "%0"),
                          money("zz_ef_bank_cb_debt")) + ")",
        f"{L['circ']}.",
        f"{L['infl']}: #T {sv('zz_ef_inflation', '+=1%')}#! (" + L['inflf'].format(
            sv('zz_ef_circ_growth_year', '+=1%'), sv('zz_ef_gdp_growth_year', '+=1%'), sv('zz_ef_price_index', '1')) + ")",
        (f"Признаки пузыря: кредит {money('zz_ef_credit_total')} = {sv('zz_ef_credit_to_gdp', '%0')} ВВП; пул — "
         f"{sv('zz_ef_pool_months', '1')} мес. взносов; накопления — {sv('zz_ef_savings_to_gdp', '%0')} ВВП") if ru else
        (f"Bubble signs: credit {money('zz_ef_credit_total')} = {sv('zz_ef_credit_to_gdp', '%0')} of GDP; the pool — "
         f"{sv('zz_ef_pool_months', '1')} months of contributions; savings — {sv('zz_ef_savings_to_gdp', '%0')} of GDP"),
        f"{L['debt']}: " + L["debtf"].format(money("zz_ef_debt_principal"), money("zz_ef_bank_cb_debt"),
                                              money("zz_ef_cc_debt"), money("zz_ef_bc_debt")),
        f"#italic {L['hint']}#!",
        "",
    ]
    raw = [
        ("fixed_income", "постоянные доходы", "fixed income"),
        ("total_income", "все доходы", "total income"),
        ("minting_week", "чеканка", "minting"),
        ("fixed_expenses", "постоянные расходы", "fixed expenses"),
        ("total_expenses", "все расходы", "total expenses"),
        ("military", "армия", "military"),
        ("pool_gross", "пул: приход", "pool: gross income"),
        ("pool_net", "пул: чистый", "pool: net income"),
    ]
    lines.append("#b Сверка — сырые числа движка, в неделю:#!" if ru else "#b Reconciliation — engine raw numbers, weekly:#!")
    ext_now = ext_expr().replace("Country.", c + ".")
    lines.append((f"мост GUI → скрипт: внешние статьи бюджета записано {sv('zz_ef_v_f_ext')}, сейчас "
                  f"[{ext_now}|D]; утечка M2 за неделю {sv('zz_ef_v_f_leak', 'D+=')} (данные недели: "
                  f"{sv('zz_ef_hook_ok', '0')}; в очереди [GetDataModelSize(GetGlobalList('zz_ef_hook_countries'))]; "
                  f"вызовов моста всего {sv('zz_ef_hook_calls', '0')}, пробных {sv('zz_ef_hook_probe_calls', '0')})") if ru else
                 (f"GUI → script bridge: budget lines outside the accounts recorded {sv('zz_ef_v_f_ext')}, now "
                  f"[{ext_now}|D]; M2 leak this week {sv('zz_ef_v_f_leak', 'D+=')} (this week's data: "
                  f"{sv('zz_ef_hook_ok', '0')}; queued [GetDataModelSize(GetGlobalList('zz_ef_hook_countries'))]; "
                  f"bridge calls in total {sv('zz_ef_hook_calls', '0')}, probe {sv('zz_ef_hook_probe_calls', '0')})"))
    tx_t = f"[GetTrendValue({c}.GetTaxIncomeTrend)|D]"
    tx_n = f"[{c}.GetIncomeTaxIncome|D]"
    lines.append((f"факт / прогноз: подоходный {tx_t} / {tx_n}; все доходы {sv('zz_ef_raw_total_income')} / "
                  f"[{c}.PredictWeeklyIncome|D]; трансфер пула {sv('zz_ef_v_f_transfer')} / "
                  f"{sv('zz_ef_pool_transfer_week')} / [{c}.GetInvestmentIncome|D]") if ru else
                 (f"settled / forecast: income tax {tx_t} / {tx_n}; total income {sv('zz_ef_raw_total_income')} / "
                  f"[{c}.PredictWeeklyIncome|D]; pool transfer {sv('zz_ef_v_f_transfer')} / "
                  f"{sv('zz_ef_pool_transfer_week')} / [{c}.GetInvestmentIncome|D]"))
    lines.append(", ".join(f"{r[1] if ru else r[2]} {sv('zz_ef_raw_' + r[0])}" for r in raw)
                 + (f"; ВВП в год {sv('zz_ef_raw_gdp')}" if ru else f"; GDP per year {sv('zz_ef_raw_gdp')}"))
    return "\\n".join(lines) + "\\n$TOOLTIP_DELIMITER$"


# ---------------------------------------------------------------------------
# Accounts and flows, all in the engine's money.
# ---------------------------------------------------------------------------

# The accounts in the order of M0..M3 (the user, 1.10 day), then the CB: its metal and E&F's currency good
# are reserves, outside the money (1.10 evening); abroad is its own account (claims: bonds) in M3.
ACC_ORDER = ["pops", "buildings", "banks", "abroad", "treasury", "cb"]
TITLES = {
    "treasury": ("Казна", "Treasury"),
    "buildings": ("Касса предприятий", "Business cash"),
    "banks": ("Средства банков", "Bank funds"),
    "pops": ("Население", "Pops"),
    "cb": ("Центральный банк", "Central bank"),
    "abroad": ("Заграница", "Abroad"),
    "ext": ("Вне счетов", "Outside the accounts"),
}
# The account's change over the month; pops, the CB (in money) and abroad hold
# no stock -- money passes through them.
DELTA = {"treasury": "zz_ef_v_d_treasury", "buildings": "zz_ef_v_d_buildings", "banks": "zz_ef_v_d_pool",
         "cb": "zz_ef_v_d_cbm", "abroad": "zz_ef_v_d_abroad"}

K, P, B, N, C, Z, X = "treasury", "buildings", "banks", "pops", "cb", "abroad", "ext"


def gt(fn):
    return ("gt", fn)


def gv(fn):
    return ("gv", fn)


def sv_(name):
    return ("sv", name)


def svp(name):
    return ("svp", name)


def svn(name):
    return ("svn", name)


# (from, to, ru, en, value, only) -- only: the one card to show it in, or None.
FLOWS = [
    # --- budget, exact (GUI), a week ---
    (N, K, "[concept_budget_income_taxes]", "[concept_budget_income_taxes]", gt("GetTaxIncomeTrend"), None),
    (N, K, "[concept_budget_poll_taxes]", "[concept_budget_poll_taxes]", gt("GetPollTaxTrend"), None),
    (N, K, "[concept_budget_consumption_taxes]", "[concept_budget_consumption_taxes]", gt("GetConsumptionTaxTrend"), None),
    (N, K, "[concept_budget_dividends_taxes]", "[concept_budget_dividends_taxes]", gt("GetDividendsTaxTrend"), None),
    (P, K, "[concept_tariffs] (платят импортёры)", "[concept_tariffs] (paid by importers)", gt("GetTariffTrend"), None),
    (P, K, "государственные дивиденды", "government dividends", gt("GetGovernmentShareDividendsTrend"), None),
    (K, P, "убытки государственных предприятий", "losses of state-owned businesses", gt("GetGovernmentShareLossesTrend"), None),
    (K, N, "[concept_budget_government_wages]", "[concept_budget_government_wages]", gt("GetGovernmentWagesExpenseTrend"), None),
    (K, N, "[concept_budget_military_wages]", "[concept_budget_military_wages]", gt("GetMilitaryWagesExpenseTrend"), None),
    (K, N, "[concept_welfare_payments]", "[concept_welfare_payments]", gt("GetWelfarePaymentsTrend"), None),
    (K, P, "[concept_budget_goods_for_government_buildings]", "[concept_budget_goods_for_government_buildings]",
     gt("GetGovernmentGoodsExpenseTrend"), None),
    (K, P, "[concept_budget_goods_for_military_upkeep]", "[concept_budget_goods_for_military_upkeep]",
     gt("GetMilitaryGoodsExpenseTrend"), None),
    (K, P, "[concept_budget_construction_goods]", "[concept_budget_construction_goods]",
     gt("GetConstructionGoodsExpenseTrend"), None),
    (K, P, "[concept_subsidies]", "[concept_subsidies]", gt("GetSubsidiesExpenseTrend"), None),
    (K, P, "[concept_subventions]", "[concept_subventions]", gt("GetSubventionsExpenseTrend"), None),
    (K, P, "[concept_budget_government_slaves]", "[concept_budget_government_slaves]",
     gt("GetGovernmentSlavesExpenseTrend"), None),
    (K, P, "[concept_budget_military_slaves]", "[concept_budget_military_slaves]", gt("GetMilitarySlavesExpenseTrend"), None),
    (K, P, "постройка кораблей снабжения", "supply ship construction", gv("GetSupplyShipConstructionGoodsExpenses"), None),
    (K, P, "содержание кораблей снабжения", "supply ship upkeep", gv("GetSupplyShipMaintenanceExpenses"), None),
    (K, P, "постройка военных кораблей", "warship construction", gv("GetMilitaryShipConstructionGoodsExpenses"), None),
    (K, P, "содержание военных кораблей", "warship upkeep", gv("GetMilitaryShipMaintenanceExpenses"), None),
    # UI.7 (3.10, user + run e0_4): the engine pays nobody for supply routes -- the business card's residual
    # went against this line (r -0.46); as K -> P the money counted as dropped out -> pops' savings
    (K, X, "маршруты поставок — движок никому не платит", "supply routes — the engine pays nobody",
     gv("GetPortConnectionExpenses"), None),
    # the pool's transfer to the budget for construction: pool gross - net income at the step (the budget's
    # GetInvestmentIncomeTrend is a smoothed trend and did not match the pool; GetInvestmentFundTrend is the STOCK)
    (B, K, "[concept_budget_investment_income]: на стройку", "[concept_budget_investment_income]: for construction",
     sv_("zz_ef_v_f_transfer"), None),
    (X, K, "[concept_budget_minting] — новые деньги движка", "[concept_budget_minting] — new engine money",
     gt("GetMintingTrend"), None),
    # vanilla pays the interest to the pops whose buildings' cash reserves back the loans
    (K, N, "[concept_budget_interest] — держателям долга (владельцам резервов зданий)",
     "[concept_budget_interest] — to the debt holders (owners of the buildings' reserves)",
     gt("GetInterestExpenseTrend"), None),
    (Z, K, "[concept_budget_diplomatic_pacts]", "[concept_budget_diplomatic_pacts]", gt("GetDiplomaticPactsIncomeTrend"), None),
    (Z, K, "[concept_budget_treaties]", "[concept_budget_treaties]", gt("GetTreatiesIncomeTrend"), None),
    (Z, K, "[concept_budget_power_bloc]", "[concept_budget_power_bloc]", gt("GetPowerBlocIncomeTrend"), None),
    (Z, K, "[concept_supply_network] (сборы с участников рынка)", "[concept_supply_network] (fees from market members)",
     gv("GetMarketFeesIncome"), None),
    (Z, K, "[concept_tolls]", "[concept_tolls]", gv("PredictTolls"), None),
    (Z, K, "[concept_piracy]", "[concept_piracy]", gt("GetPiracyIncomeTrend"), None),
    (K, Z, "[concept_budget_diplomatic_pacts]", "[concept_budget_diplomatic_pacts]", gt("GetDiplomaticPactsExpenseTrend"), None),
    (K, Z, "[concept_budget_treaties]", "[concept_budget_treaties]", gt("GetTreatiesExpenseTrend"), None),
    (K, Z, "[concept_budget_power_bloc]", "[concept_budget_power_bloc]", gt("GetPowerBlocExpenseTrend"), None),
    (X, K, "[concept_budget_additional_income]", "[concept_budget_additional_income]", gt("GetAdditionalIncomeTrend"), None),
    (K, X, "[concept_budget_additional_expenses]", "[concept_budget_additional_expenses]",
     gt("GetAdditionalExpensesTrend"), None),
    # --- pops: a transit account ---
    (P, N, "зарплаты и дивиденды (оценка: ВВП / 52 − госвыплаты)", "wages and dividends (estimate: GDP / 52 − state pay)",
     ("expr", "WAGES"), None),
    (N, P, "покупки товаров — остаток дохода (оценка)",
     "purchases of goods — the rest of the income (estimate)", ("closing",), None),
    # pops' savings: the money the engine lost this week, exact and merged (the bridge)
    (N, X, "в накопления: остаток дохода — деньги, выпавшие из казны и касс предприятий (точно, по сохранению "
           "денег)",
     "into savings: income left over — money that dropped out of the treasury and business cash (exact, by money "
     "conservation)", svp("zz_ef_v_f_inflow"), None),
    (X, N, "из накоплений: вернулось в деньги движка больше, чем выпало",
     "from savings: more came back into the engine's money than dropped out", svn("zz_ef_v_f_inflow"), None),
    # the coined money goes straight into the owners' savings, not into purchases
    (N, X, "в накопления: чеканка — владельцам металла", "into savings: coinage — to the metal's owners",
     sv_("zz_ef_v_f_mint_own"), N),
    # --- banks ---
    (P, B, "взносы в пул — инвестиции зданий и сбережения богатых (ваниль)",
     "pool contributions — buildings' investment and the rich's saving (vanilla)", sv_("zz_ef_v_f_contrib"), None),
    (B, Z, "покупка облигаций других стран частными банками (E&F)", "foreign bonds bought by private banks (E&F)",
     svp("zz_ef_v_d_bonds"), None),
    (Z, B, "погашение облигаций других стран (E&F)", "foreign bonds run off (E&F)", svn("zz_ef_v_d_bonds"), None),
    # deposits: from the savings, not from the week's income -- banks' card only (window values)
    (N, B, "вклады населения из накоплений (прошедшая неделя: пул отражает их неделей позже)",
     "pops' deposits from their savings (the week just ended: the pool shows them a week later)",
     sv_("zz_ef_v_w_dep_in"), B),
    (B, N, "снятие вкладов (прошедшая неделя)", "deposits withdrawn (the week just ended)", sv_("zz_ef_v_w_dep_out"), B),
    (B, N, "проценты по вкладам (прошедшая неделя)", "interest on deposits (the week just ended)",
     sv_("zz_ef_v_w_dep_int"), B),
    # consumer credit (EF.48 item 4): pool <-> pops through the dependents' surcharge
    # UI.7 (3.10, user): in the pops' card too -- the engine pays the net as the dependents' surcharge, but
    # the three lines read as what they are. Window values = the week just ended in both cards.
    (B, N, "потребительский кредит: выдано (за прошедшую неделю; доходит надбавкой на иждивенцев)",
     "consumer credit: lent (the week just ended; reaches pops as the dependents' surcharge)",
     sv_("zz_ef_v_w_cc_issue"), None),
    (N, B, "потребительский кредит: погашено (за прошедшую неделю)", "consumer credit: repaid (the week just ended)",
     sv_("zz_ef_v_w_cc_repay"), None),
    (N, B, "потребительский кредит: проценты (за прошедшую неделю)", "consumer credit: interest (the week just ended)",
     sv_("zz_ef_v_w_cc_int"), None),
    # --- central bank, in money (a transit account) ---
    (X, C, "выпуск: кредит банкам — новые деньги", "issue: credit to banks — new money", sv_("zz_ef_v_f_cb_borrow"), None),
    (C, B, "кредит банкам под ключевую ставку", "credit to banks at the key rate", sv_("zz_ef_v_f_cb_borrow"), None),
    (B, C, "погашение кредита ЦБ", "repayment of the CB's credit", sv_("zz_ef_v_f_cb_repay"), None),
    (C, X, "погашено — деньги изъяты", "repaid — money withdrawn", sv_("zz_ef_v_f_cb_repay"), None),
    (B, C, "проценты по кредиту ЦБ", "interest on the CB's credit", sv_("zz_ef_v_f_cb_interest"), None),
    (C, K, "прибыль ЦБ: проценты банков", "the CB's profit: banks' interest", sv_("zz_ef_v_f_cb_interest"), None),
    # UI.7 (3.10): what actually moves the CB's account (its metal at parity) -- model flows
    # (zz_ef_money_model_step), CB card only; the residual left is E&F's own metal operations
    (Z, C, "Юм: металл за чистый приход из-за рубежа (прошлая неделя)",
     "Hume: metal for the net inflow from abroad (last week)", svp("zz_ef_v_f_cb_hume_m"), C),
    (C, Z, "Юм: металл за чистый отток за рубеж (прошлая неделя)",
     "Hume: metal for the net outflow abroad (last week)", svn("zz_ef_v_f_cb_hume_m"), C),
    (X, C, "добытый металл, отчеканенный ЦБ, — в резервы", "mined metal coined by the CB — into the reserves",
     sv_("zz_ef_v_f_mint"), C),
    (X, C, "переоценка резервов: паритет снижен (девальвация, перепривязка)",
     "revaluation of the reserves: parity lowered (devaluation, re-anchor)", svp("zz_ef_v_f_cb_reval"), C),
    (C, X, "переоценка резервов: паритет повышен", "revaluation of the reserves: parity raised",
     svn("zz_ef_v_f_cb_reval"), C),
    (X, C, "пересчёт металла до 40% покрытия (начало игры)", "metal rescaled to 40% cover (game start)",
     svp("zz_ef_v_f_cb_rescale"), C),
    (C, X, "пересчёт металла до 40% покрытия (начало игры)", "metal rescaled to 40% cover (game start)",
     svn("zz_ef_v_f_cb_rescale"), C),
    # the CB coins mined metal (В2.3, 2.10): the owners' part and the treasury's brassage
    (X, N, "чеканка ЦБ из добытого металла — владельцам", "the CB coins mined metal — to the owners",
     sv_("zz_ef_v_f_mint_own"), None),
    (X, K, "чеканка ЦБ: брассаж в казну", "the CB coins mined metal: brassage to the treasury",
     sv_("zz_ef_v_f_mint_tr"), None),
    # --- abroad ---
    # trade centres: their cash change is the country's payments abroad (EF.48 item 1)
    (P, Z, "торговые центры: оплата импорта — убыль их кассы", "trade centres: paying for imports — their cash fell",
     svn("zz_ef_v_d_tc"), None),
    (Z, P, "торговые центры: выручка экспорта — прирост их кассы", "trade centres: export revenue — their cash grew",
     svp("zz_ef_v_d_tc"), None),
    # E&F's scripted moves on the treasury (refunds to the CB, bonds bought), 1.10
    (K, C, "E&F: казна гасит долг ЦБ (сверх бюджета)", "E&F: the treasury repays the CB (beyond the budget)",
     svn("zz_ef_tr_to_cb"), None),
    (C, K, "E&F: прочий приход в казну сверх бюджета", "E&F: other income to the treasury beyond the budget",
     svp("zz_ef_tr_to_cb"), None),
    (K, Z, "E&F: казна покупает облигации других стран", "E&F: the treasury buys other countries' bonds",
     svp("zz_ef_v_d_tbonds"), None),
    (Z, K, "E&F: облигации казны погашены", "E&F: the treasury's bonds repaid", svn("zz_ef_v_d_tbonds"), None),
    # the pool's unexplained loss (EF.48 item 2) = companies buying levels from aristocrats and capitalists at the
    # privatization price (В1.2, 3.10): the engine pays the sellers nothing, the model puts it in their savings
    (B, N, "компании выкупают уровни зданий у аристократов и капиталистов (цена приватизации, 15 000 за уровень) — "
           "деньги продавцам",
     "companies buy building levels from aristocrats and capitalists (the privatization price, 15 000 a level) — "
     "money to the sellers", svn("zz_ef_v_f_pool_other"), None),
    (N, X, "в накопления: выручка продавцов уровней", "into savings: the level sellers' proceeds",
     sv_("zz_ef_v_f_buyout"), N),
    (X, B, "необъяснённый приход в пул", "the pool's unexplained gain", svp("zz_ef_v_f_pool_other"), None),
]

NOTES = {
    "treasury": ("Статьи бюджета — точно, за неделю, как в бюджете игры; изменение казны — между недельными "
                 "шагами модели (сразу после недельного расчёта бюджета).",
                 "Budget lines are exact, a week, as in the game's budget; the treasury's change is between the "
                 "model's weekly steps (right after the budget's weekly tick)."),
    "buildings": ("Денежные резервы всех зданий: кредитный лимит − база − доля ВВП (COUNTRY_MIN_CREDIT_*). Прочее — "
                  "закупки у заграницы, налоги с прибыли, разница оценки зарплат и дивидендов.",
                  "Cash reserves of all buildings: credit limit − base − GDP share (COUNTRY_MIN_CREDIT_*). Other: "
                  "purchases abroad, profit taxes, the error of the wages-and-dividends estimate."),
    "banks": ("Инвестиционный пул. Частная стройка идёт через казну: пул → казна (трансфер) → предприятия "
              "(строительные товары). Банки занимают у ЦБ под ключевую ставку — долг идёт к доле ВВП по ставке "
              "(50% при 2%, 0 при 12%): ставка ниже — больше новых денег в пул, выше — банки гасят долг из пула.",
              "The investment pool. Private construction goes through the treasury: pool → treasury (transfer) → "
              "businesses (construction goods). Banks borrow from the CB at the key rate — the debt goes to a share of "
              "GDP by the rate (50% at 2%, 0 at 12%): a lower rate puts more new money into the pool, a higher one "
              "makes banks repay from the pool."),
    "pops": ("Денег у населения в движке нет: остаток дохода движок превращает в достаток (число). Мод ловит "
             "эти деньги в накопления — по сохранению денег (мост GUI → скрипт): что пропало из казны и касс "
             "предприятий сверх известных переводов. Оплата заграницы (касса торговых центров) и необъяснённый "
             "остаток пула (выкуп уровней) сюда не входят. Часть накоплений лежит во вкладах — это снова "
             "деньги движка (пул).",
             "Pops hold no money in the engine: it turns the income left over into wealth (a number). The mod "
             "catches this money into savings by money conservation (the GUI → script bridge): what vanished from "
             "the treasury and business cash beyond the known transfers. Payments abroad (the trade centres' cash) "
             "and the pool's unexplained change (levels bought) are not in it. Part of the savings is "
             "in deposits — engine money again (the pool)."),
    "abroad": ("Заграница — требования страны к другим странам: облигации частных банков и казны (E&F). Все платежи с заграницей идут через ЦБ: чистый отток "
               "списывает его металл (механизм Юма). Платежи требований не меняют — они в «прочее» не входят; "
               "«прочее» — изменение облигаций, не объяснённое покупками и погашениями.",
               "Abroad — the country's claims on other countries: the private banks' and the treasury's bonds (E&F). Every payment with abroad goes through "
               "the CB: a net outflow pays out its metal (Hume's mechanism). Payments do not change the claims and "
               "are not in 'other'; 'other' is the bonds' change not explained by purchases and redemptions."),
    "cb": ("ЦБ — расчётный агент страны: все платежи с заграницей идут через него. Кредит банкам — новые деньги, "
           "погашение их изымает, проценты уходят в казну. Запас счёта — резервы металла (склад товара-валюты "
           "E&F — штуки товара, в резервы не входит): чистый отток за рубеж по курсу списывает металл, приток — добавляет (механизм Юма, "
           "только металлический стандарт с ЦБ). Резервы — покрытие валюты, а не деньги: в M0–M3 не входят, "
           "иначе отток за рубеж считался бы дважды (деньги ушли из пула или касс и тот же металл ушёл из ЦБ). "
           "Отток уменьшает деньги и покрытие на одну сумму; торговый баланс E&F в резервы больше не входит.",
           "The CB is the country's settlement agent: every payment with abroad goes through it. Credit to banks is "
           "new money, repayment withdraws it, interest goes to the treasury. The account's stock is the metal "
           "reserves (E&F's currency-good stock is counts of a good, not in them): a net outflow abroad pays out metal at the "
           "currency's value, an inflow brings it in (Hume's mechanism, metal standards with a CB only). The reserves "
           "are the currency's cover, not money: they are outside M0–M3, else a payment abroad would count twice "
           "(the money left the pool or business cash and the same metal left the CB). An outflow lowers the money "
           "and the cover by one sum; E&F's trade balance is no longer in the reserves."),
}

STATE_PAY = ["GetGovernmentWagesExpenseTrend", "GetMilitaryWagesExpenseTrend", "GetWelfarePaymentsTrend"]
EXPRS = {}


def wages_expr():
    e = "Country.MakeScope.ScriptValue('zz_ef_gdp_week')"
    for fn in STATE_PAY:
        e = f"Subtract_CFixedPoint({e}, Abs_CFixedPoint(GetTrendValue(Country.{fn})))"
    return f"Max_CFixedPoint({e}, {ZERO})"


def expr(v):
    """GUI expression (CFixedPoint, non-negative, a week) for a flow value."""
    if v[0] == "expr":
        return wages_expr()
    if v[0] == "closing":
        return EXPRS["closing"]
    kind, name = v
    if kind == "gt":
        return f"Abs_CFixedPoint(GetTrendValue(Country.{name}))"
    if kind == "gv":
        return f"Abs_CFixedPoint(Country.{name})"
    s = f"Country.MakeScope.ScriptValue('{name}')"
    if kind in ("sv", "svp"):
        return f"Max_CFixedPoint({s}, {ZERO})"
    return f"Max_CFixedPoint(Negate_CFixedPoint({s}), {ZERO})"


def acc_of(a):
    return a


def card_flows(acc):
    """Flows shown in acc's card, as (other, dir, flow)."""
    out = []
    for f in FLOWS:
        frm, to, _, _, _, only = f
        frm, to = acc_of(frm), acc_of(to)
        if only and only != acc:
            continue
        if to == acc:
            out.append((frm, "in", f))
        elif frm == acc:
            out.append((to, "out", f))
    return out


def sum_expr(ins, outs):
    acc = ins[0]
    for x in ins[1:]:
        acc = f"Subtract_CFixedPoint({acc}, Negate_CFixedPoint({x}))"
    for x in outs:
        acc = f"Subtract_CFixedPoint({acc}, {x})"
    return acc


def abr_expr():
    """The budget's lines with other countries (abroad only), in - out, a week."""
    ins = [expr(f[4]) for f in FLOWS if f[1] == K and f[0] == Z]
    outs = [expr(f[4]) for f in FLOWS if f[0] == K and f[1] == Z]
    return sum_expr(ins, outs)


def ext_expr():
    """The budget's lines outside the accounts (outside + abroad), in - out, a week."""
    ins, outs = [], []
    for f in FLOWS:
        frm, to, _, _, v, _ = f
        if to == K and frm in (X, Z):
            ins.append(expr(v))
        elif frm == K and to in (X, Z):
            outs.append(expr(v))
    acc = ins[0]
    for x in ins[1:]:
        acc = f"Subtract_CFixedPoint({acc}, Negate_CFixedPoint({x}))"
    for x in outs:
        acc = f"Subtract_CFixedPoint({acc}, {x})"
    return acc


HOOK_GUI = """# GENERATED by tools/regen_ef_money_supply_loc.py -- do not edit by hand.
# EF.48 GUI bridge: for each country the weekly money step queued in
# global_var list zz_ef_hook_countries, hand the budget's lines outside the
# accounts (GUI-only data) to script (scripted_guis/zz_ef_money_hook.txt).
# CMF's pattern as is (_cmf/gui/com_hidden_trigger.gui, character names):
# a hidden but "visible" widget of real size, an item per list entry whose
# state fires on_finish when trigger_when turns true -- CMF's own trigger,
# [Scope.IsSet] (the item exists). BPM's _show/on_start, trigger_on_create/
# on_start and trigger_when on the country's var never fired here
# (2026-09-30/10-01). The receiver consumes var:zz_ef_hook_pending and takes
# the country off the list, so repeated calls do nothing.
widget = {{
	name = zz_ef_money_hook
	datacontext = "[GetMetaPlayer.GetPlayedOrObservedCountry]"
	visible = "[GetMetaPlayer.GetPlayedOrObservedCountry.IsValid]"
	size = {{ 500 500 }}
	allow_outside = yes
	alwaystransparent = yes
	alpha = 1

	flowcontainer = {{
		visible = "[DataModelHasItems(GetGlobalList('zz_ef_hook_countries'))]"
		datamodel = "[GetGlobalList('zz_ef_hook_countries')]"
		item = {{
			widget = {{
				datacontext = "[Scope.GetCountry]"
				# Probe without a value: tells a failing launch from a failing
				# value expression (global_var:zz_ef_hook_probe_calls).
				state = {{
					trigger_when = "[Scope.IsSet]"
					on_finish = "[GetScriptedGui('zz_ef_money_hook_probe_sg').Execute( GuiScope.SetRoot( Country.MakeScope ).End )]"
				}}
				state = {{
					trigger_when = "[Scope.IsSet]"
					on_finish = "[GetScriptedGui('zz_ef_money_hook_sg').Execute( GuiScope.SetRoot( Country.MakeScope ).AddScope( 'ext', MakeScopeValue( {ext} ) ).AddScope( 'abr', MakeScopeValue( {abr} ) ){probes}.End )]"
				}}
			}}
		}}
	}}
}}
"""


# Engine values the GUI alone sees (docs/data_types, dump_data_types 1.10 night), handed to the receiver
# for the weekly log (var:zz_ef_g_<key>): trade, ownership abroad, the pool's change, the government's rate.
PROBES = [
    ("imp", "Country.GetTotalImportedAmount"),
    ("exp", "Country.GetTotalExportedAmount"),
    ("surplus", "Country.GetMarket.GetTradeSurplus"),
    ("fown", "Country.GetForeignOwnedGDP"),
    ("aown", "Country.GetGDPOwnedInForeignCountries"),
    ("poolchg", "Country.GetInvestmentPoolChange"),
    ("pcons", "Country.GetPrivateConstructionGoodsExpenses"),
    ("grate", "Country.GetYearlyInterestRate"),
    ("maxcred", "Country.GetMaxCredit"),
    ("wgdp", "Country.GetWeeklyGDP"),
    # night 2, item 5 (2.10): the government's rate -- weekly, the interest paid, the debt the
    # country's own pool holds
    ("wrate", "Country.GetWeeklyInterestRate"),
    ("ipay", "Country.GetInterestPayment"),
    ("sdebt", "Country.GetGovernmentSelfDebt"),
    ("sdebtf", "Country.GetGovernmentSelfDebtFraction"),
]


# UI.7 (3.10): the "прочее" of each card, as the tooltip computes it -> the
# weekly log line EFO, so a run shows how big each residual is and when.
RESID = {}
# UI.7 (3.10, runs e0_4/e0_5): what is left in each card's residual, named
OTHER_LAB = {
    "cb": ("прочее — операции E&F с металлом ЦБ (закупки металла, валютные сделки)",
           "other — E&F's operations with the CB's metal (metal purchases, currency deals)"),
    "buildings": ("прочее — сглаженные тренды бюджета против недельного изменения кассы",
                  "other — smoothed budget trends against the weekly change of the cash"),
}
CLAIM_VALUES = {"zz_ef_v_d_bonds", "zz_ef_v_d_tbonds"}


def flow_key(v):
    if v[0] == "expr":
        return "wages"
    if v[0] == "closing":
        return "closing"
    kind, name = v
    name = name.replace("zz_ef_v_", "").replace("Get", "").replace("ExpenseTrend", "_x").replace("IncomeTrend", "_i")
    name = name.replace("Trend", "").replace("Expenses", "_x")
    return name + {"svp": "+", "svn": "-"}.get(kind, "")


def eff_lines():
    """UI.7: one EFF line per card -- the account's change and every flow shown, signed (+ in, - out)."""
    out = []
    for acc in ACC_ORDER:
        if acc not in DELTA:
            continue
        parts = f"|{acc}|d [Country.MakeScope.ScriptValue('{DELTA[acc]}')|0]"
        for other, dr, f in card_flows(acc):
            sign = "" if dr == "in" else "-"
            parts += f"|{sign}{flow_key(f[4])}@{other} [{expr(f[4])}|0]"
        out.append("EFF|[TimeKeeper.GetCurrentDate.GetString]|[THIS.GetCountry.GetNameNoFormatting]"
                   + parts.replace("Country.", "THIS.GetCountry."))
    return out
LOG_KEYS = {"buildings": "b_rest", "banks": "pool_rest", "abroad": "abr_rest", "treasury": "tr_rest", "cb": "cbm_rest"}


def write_log_effect():
    e = os.path.join(HOTFIX, "common", "scripted_effects", "zz_ef_money_log_rest.txt")
    parts = "".join(f"|{LOG_KEYS[a]} [{RESID[a].replace('Country.', 'THIS.GetCountry.')}|0]"
                    for a in ACC_ORDER if a in RESID and a in LOG_KEYS)
    with open(e, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write("# GENERATED by tools/regen_ef_money_supply_loc.py -- do not edit by hand.\n"
                "# UI.7 (3.10): the residual (\"прочее\") of each account card of the Money Supply\n"
                "# tooltip, the same expressions, as a weekly log line EFO. Country scope.\n"
                "zz_ef_money_log_rest = {\n"
                f"\tdebug_log = \"EFO|[TimeKeeper.GetCurrentDate.GetString]|[THIS.GetCountry.GetNameNoFormatting]{parts}\"\n"
                + "".join(f"\tdebug_log = \"{ln}\"\n" for ln in eff_lines())
                + "}\n")


def write_hook():
    g = os.path.join(HOTFIX, "gui", "zz_ef_money_hook.gui")
    probes = "".join(f".AddScope( 'g_{k}', MakeScopeValue( {fn} ) )" for k, fn in PROBES)
    with open(g, "w", encoding="utf-8", newline="\n") as f:
        f.write(HOOK_GUI.format(ext=ext_expr(), abr=abr_expr(), probes=probes))
    w = os.path.join(HOTFIX, "gui", "scripted_widgets", "zz_ef_money_hook.txt")
    os.makedirs(os.path.dirname(w), exist_ok=True)
    with open(w, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write("# GENERATED by tools/regen_ef_money_supply_loc.py. EF.48 GUI bridge.\n"
                "gui/zz_ef_money_hook.gui = zz_ef_money_hook\n")


def closing_expr():
    """Pops' purchases and wealth growth: pops' other income minus their other payments."""
    ins, outs = [], []
    for other, dr, f in card_flows(N):
        if f[4][0] == "closing":
            continue
        (ins if dr == "in" else outs).append(expr(f[4]))
    acc = ins[0]
    for x in ins[1:]:
        acc = f"Subtract_CFixedPoint({acc}, Negate_CFixedPoint({x}))"
    for x in outs:
        acc = f"Subtract_CFixedPoint({acc}, {x})"
    return acc


def fx_card(lang):
    """E&F's currency good in the CB's stock -- counts, not money."""
    cur, sv, money, delta, tt = ctx("Country")
    ru = lang == "russian"
    unit = "шт." if ru else "units"
    rows = [
        ("in", "выпуск: продажи товара-валюты на рынке", "issue: sales of the currency good on the market", "zz_ef_cb_issue_month"),
        ("out", "в обращение: здания и население страны", "into circulation: the country's buildings and pops",
         "zz_ef_cb_demand_own"),
        ("out", "в обращение: другие страны рынка", "into circulation: other countries of the market",
         "zz_ef_cb_demand_others"),
        ("in", "девальвация", "devaluation", "zz_ef_cb_devaluation_month"),
        ("out", "ревальвация", "revaluation", "zz_ef_cb_revaluation_month"),
    ]
    L = [f"#b {'Склад товара-валюты ЦБ (E&F) за месяц' if ru else 'The CB stock of the currency good (E&F) this month'}: "
         f"{sv('zz_ef_v_d_cb', 'D+=')} {unit}#!"]
    for dr, r, e, name in rows:
        v = f"[Country.MakeScope.ScriptValue('{name}')|D]"
        L.append(f"  ← #P +{v}#! {unit} {r if ru else e}" if dr == "in" else f"  → #N −{v}#! {unit} {r if ru else e}")
    L += ["", ("Это не деньги, а штуки товара liquidity_currency (E&F считает их × 4 в месяц и рисует значком валюты). "
               "В деньгах движка ЦБ — обычное здание: его выручка в кассе предприятий.") if ru else
          ("These are not money but counts of the liquidity_currency good (E&F counts them × 4 a month and draws "
           "them with the currency sign). In the engine's money the CB is an ordinary building: its revenue is in "
           "business cash.")]
    return "\\n".join(L)


def nested(lang):
    cur, sv, money, delta, tt = ctx("Country")
    gold = "@gold!"
    EXPRS["closing"] = closing_expr()
    ru = lang == "russian"
    k = 0 if ru else 1
    none = "  нет переводов" if ru else "  no transfers"
    other_lab = "прочее" if ru else "other"
    d = {}
    for acc in ACC_ORDER:
        flows = card_flows(acc)
        head = TITLES[acc][k] + (" за неделю" if ru else " this week")
        L = [f"#b {head}: {delta(DELTA[acc])}#!" if acc in DELTA else f"#b {head}#!"]
        resid = f"Country.MakeScope.ScriptValue('{DELTA[acc]}')" if acc in DELTA else None
        fixed_resid = "Country.MakeScope.ScriptValue('zz_ef_other_treasury_rest')" if acc == K else None
        n = 0
        for other in [a for a in ACC_ORDER if a != acc] + [X]:
            rows = [(dr, f) for o, dr, f in flows if o == other]
            if not rows and not (other == X and resid):
                continue
            n += 1
            L.append(f"{n} {TITLES[other][k]}")
            for dr, f in rows:
                e = expr(f[4])
                lab = f[2] if ru else f[3]
                # UI.7 (3.10): abroad = the country's claims (bonds); payments with abroad do not
                # change them -- the CB settles them in metal (Hume) -- so they stay out of its residual
                # the same for the CB: E&F's treasury moves with the CB do not touch its metal
                counts = (acc != Z or f[4][1] in CLAIM_VALUES) and not (acc == C and f[4][1] == "zz_ef_tr_to_cb")
                if dr == "in":
                    L.append(f"  ← #P +[{e}|D] {cur}#! {lab}")
                    if resid and counts:
                        resid = f"Subtract_CFixedPoint({resid}, {e})"
                else:
                    L.append(f"  → #N −[{e}|D] {cur}#! {lab}")
                    if resid and counts:
                        resid = f"Subtract_CFixedPoint({resid}, Negate_CFixedPoint({e}))"
            if other == X and resid:
                lab_o = OTHER_LAB.get(acc, ("прочее", "other"))[0 if ru else 1]
                L.append(f"  ↔ [{fixed_resid or resid}|D+=] {cur} {lab_o}")
                RESID[acc] = fixed_resid or resid
            if other == X and acc == K:
                bin_, bout = ("Country.MakeScope.ScriptValue('zz_ef_total_income_week')",
                              "Country.MakeScope.ScriptValue('zz_ef_total_expenses_week')")
                for o, dr, f in flows:
                    if f[4][0] in ("gt", "gv") or f[4] == sv_("zz_ef_v_f_transfer"):
                        if dr == "in":
                            bin_ = f"Subtract_CFixedPoint({bin_}, {expr(f[4])})"
                        else:
                            bout = f"Subtract_CFixedPoint({bout}, {expr(f[4])})"
                L.append(("  проверка: доходы бюджета вне строк " if ru else "  check: budget income not in any line ")
                         + f"[{bin_}|D+=] {cur}" + (", расходы вне строк " if ru else ", expenses not in any line ")
                         + f"[{bout}|D+=] {cur}")
        if not n:
            L.append(none)
        L += ["", NOTES[acc][k]]
        if acc == B:
            L.append((f"Долг банков перед ЦБ {money('zz_ef_bank_cb_debt')}; цель {money('zz_ef_cb_credit_target')} = "
                      f"ВВП × {sv('zz_ef_cb_credit_share', '%0')} от 50% при ставке {sv('zz_ef_money_rate', '%1')}; "
                      f"1.15% разрыва в неделю (~5% в месяц), но занимают только недостачу пула до потребности "
                      f"{money('zz_ef_pool_need')} (3 месяца выплат пула), а свободные деньги сверх неё идут на погашение. "
                      f"Пул — {sv('zz_ef_pool_months', '1')} мес. взносов.")
                     if ru else
                     (f"Banks' debt to the CB {money('zz_ef_bank_cb_debt')}; target {money('zz_ef_cb_credit_target')} = "
                      f"GDP × {sv('zz_ef_cb_credit_share', '%0')} of 50% at a rate of {sv('zz_ef_money_rate', '%1')}; "
                      f"1.15% of the gap a week (~5% a month), but they borrow only what the pool lacks of its need "
                      f"{money('zz_ef_pool_need')} (3 months of its payouts), and idle money over it repays the CB. The "
                      f"pool holds {sv('zz_ef_pool_months', '1')} months of contributions."))
        if acc == C:
            L.append((f"#b Резервы металла: {sv('zz_ef_cb_metal')} {gold}#! (за неделю {sv('zz_ef_v_f_hume', 'D+=')}); "
                      f"чистый поток с заграницей {sv('zz_ef_v_f_ext_net', 'D+=')}{cur}; курс {sv('money_value_0', '3')} "
                      f"металла за {cur}; покрытие по паритету {sv('zz_ef_cb_cover', '%0')}. Склад товара-валюты "
                      f"{sv('money_supply_state')} шт.")
                     if ru else
                     (f"#b Metal reserves: {sv('zz_ef_cb_metal')} {gold}#! (this week {sv('zz_ef_v_f_hume', 'D+=')}); "
                      f"net flow with abroad {sv('zz_ef_v_f_ext_net', 'D+=')}{cur}; value {sv('money_value_0', '3')} "
                      f"metal per {cur}; cover at parity {sv('zz_ef_cb_cover', '%0')}. Currency-good stock "
                      f"{sv('money_supply_state')} units."))
        if acc == B:
            L.append((f"#b Кредит бизнесу: долг предприятий {money('zz_ef_bc_debt')}#! "
                      f"({sv('zz_ef_bc_debt_to_gdp', '%1')} ВВП). Частная стройка за неделю оплачена заёмными "
                      f"деньгами банков на {sv('zz_ef_bc_borrowed_share', '%0')} (кредит ЦБ и вклады к пулу): новый "
                      f"долг {money('zz_ef_v_f_bc_new')}; проценты {money('zz_ef_v_f_bc_int')} (ключевая + 3 п.п.), "
                      f"срок 5 лет; из взносов зданий в счёт долга {money('zz_ef_v_f_bc_paid')} "
                      f"({sv('zz_ef_bc_service_share', '%0')} взносов) — деньги из касс в пул. Не хватает взносов — "
                      f"владельцы отдают больше дохода в пул вместо дивидендов: сейчас +{sv('zz_ef_v_bc_svc', '0')}% "
                      f"доли взносов (до +30%).")
                     if ru else
                     (f"#b Business credit: businesses' debt {money('zz_ef_bc_debt')}#! "
                      f"({sv('zz_ef_bc_debt_to_gdp', '%1')} of GDP). This week's private construction was paid with "
                      f"the banks' borrowed money for {sv('zz_ef_bc_borrowed_share', '%0')} (CB credit and deposits "
                      f"to the pool): new debt {money('zz_ef_v_f_bc_new')}; interest {money('zz_ef_v_f_bc_int')} (key "
                      f"+ 3 pp), term 5 years; counted from the buildings' contributions {money('zz_ef_v_f_bc_paid')} "
                      f"({sv('zz_ef_bc_service_share', '%0')} of them) — money from business cash to the pool. When "
                      f"they fall short, owners put more income into the pool instead of dividends: now "
                      f"+{sv('zz_ef_v_bc_svc', '0')}% of the contribution share (up to +30%)."))
        if acc == N:
            L.append((f"#b Потребительский кредит: долг {money('zz_ef_cc_debt')}#! "
                      f"({sv('zz_ef_cc_debt_to_gdp', '%1')} ВВП); предел 4 месяца дохода {money('zz_ef_cc_limit')}, "
                      f"цель {money('zz_ef_cc_target')} ({sv('zz_ef_cc_share', '%0')} предела по ставке: 100% при 2%, "
                      f"0 при 12%); ставка {sv('zz_ef_cc_rate', '%1')} (ключевая + 3 п.п.), срок год. На эту неделю: "
                      f"выдано {money('zz_ef_v_f_cc_issue')}, погашено {money('zz_ef_v_f_cc_repay')}, проценты "
                      f"{money('zz_ef_v_f_cc_int')} — итого населению {sv('zz_ef_v_f_cc_net', 'D+=')}{cur}, надбавка "
                      f"к доходу иждивенцев {sv('zz_ef_cc_wage_add', '+=2')} в год на иждивенца "
                      f"({sv('zz_ef_v_dependents')} иждивенцев).")
                     if ru else
                     (f"#b Consumer credit: debt {money('zz_ef_cc_debt')}#! "
                      f"({sv('zz_ef_cc_debt_to_gdp', '%1')} of GDP); limit 4 months of income {money('zz_ef_cc_limit')}, "
                      f"target {money('zz_ef_cc_target')} ({sv('zz_ef_cc_share', '%0')} of the limit by the rate: 100% "
                      f"at 2%, 0 at 12%); rate {sv('zz_ef_cc_rate', '%1')} (key + 3 pp), term a year. This week: lent "
                      f"{money('zz_ef_v_f_cc_issue')}, repaid {money('zz_ef_v_f_cc_repay')}, interest "
                      f"{money('zz_ef_v_f_cc_int')} — net to pops {sv('zz_ef_v_f_cc_net', 'D+=')}{cur}, dependents' "
                      f"surcharge {sv('zz_ef_cc_wage_add', '+=2')} a year per dependent "
                      f"({sv('zz_ef_v_dependents')} dependents)."))
            L.append((f"Доход населения ≈ ВВП / 52 = {money('zz_ef_gdp_week')}.") if ru else
                     (f"Pops' income ≈ GDP / 52 = {money('zz_ef_gdp_week')}."))
            L.append((f"#b Накопления: {money('zz_ef_pop_savings')}#! ({sv('zz_ef_pop_savings_week', 'D+=')}{cur} за "
                      f"неделю) — во вкладах {money('zz_ef_pop_deposits')}, на руках {money('zz_ef_pop_cash')}. "
                      f"За неделю: выпало из денег движка {sv('zz_ef_v_f_inflow', 'D+=')}{cur}, продажа уровней компаниям "
                      f"{sv('zz_ef_v_f_buyout', 'D+=')}{cur}, проценты по вкладам "
                      f"{sv('zz_ef_v_f_dep_int', 'D+=')}{cur}; внесено {money('zz_ef_v_f_dep_in')}, снято "
                      f"{money('zz_ef_v_f_dep_out')} (в средствах банков — в изменении следующей недели). Норма наличных на руках — {money('zz_ef_pop_cash_norm')} "
                      f"({sv('zz_ef_cash_norm_gdp', '%0')} ВВП: 20% при ставке по вкладам 0%, 12% при 3%, не ниже 6%); "
                      f"сверх неё население вносит во вклады, ниже — снимает, по 10% разрыва в неделю. Ставка по "
                      f"вкладам {sv('zz_ef_deposit_rate', '%1')} = ключевая − маржа банков {sv('zz_ef_deposit_margin', '%1')} "
                      f"(1.5 п.п. + 1 п.п. за каждую потребность пула свободных денег).")
                     if ru else
                     (f"#b Savings: {money('zz_ef_pop_savings')}#! ({sv('zz_ef_pop_savings_week', 'D+=')}{cur} this "
                      f"week) — in deposits {money('zz_ef_pop_deposits')}, at hand {money('zz_ef_pop_cash')}. This "
                      f"week: dropped out of the engine's money {sv('zz_ef_v_f_inflow', 'D+=')}{cur}, levels sold to companies "
                      f"{sv('zz_ef_v_f_buyout', 'D+=')}{cur}, deposit "
                      f"interest {sv('zz_ef_v_f_dep_int', 'D+=')}{cur}; deposited {money('zz_ef_v_f_dep_in')}, "
                      f"withdrawn {money('zz_ef_v_f_dep_out')}. Cash norm at hand {money('zz_ef_pop_cash_norm')} "
                      f"({sv('zz_ef_cash_norm_gdp', '%0')} of GDP: 20% at a 0% deposit rate, 12% at 3%, at least 6%); "
                      f"over it pops deposit, under it they withdraw, 10% of the gap a week. Deposit rate "
                      f"{sv('zz_ef_deposit_rate', '%1')} = key − the banks' margin {sv('zz_ef_deposit_margin', '%1')} "
                      f"(1.5 pp + 1 pp per need of idle money in the pool)."))
        d[f"zz_ef_ms_tt_{acc}"] = "\\n".join(L)
    return d


def build(lang):
    src = "russian" if lang == "russian" else "english"
    d = {}
    for key in KEYS_COUNTRY:
        d[key] = main_text(src, "Country")
    for key in KEYS_PLAYER:
        d[key] = main_text(src, "GetPlayer")
    d.update(nested(src))
    return d


def split_lines(d):
    """UI.6 (3.10): a key per tooltip line, so the file reads and edits line by line. A tooltip key is a chain
    "$<line key>$\\n$<line key>$..."; a line shared by several tooltips (the six standards of E&F's money supply
    text) is written once. Line keys: zz_ef_ms_<group>_<NN>, the group from the first tooltip with the line."""
    def group(key):
        if key in KEYS_PLAYER:
            return "player"
        if key in KEYS_COUNTRY:
            return "country"
        return key.replace("zz_ef_ms_tt_", "")
    seen, sub, comp, count = {}, [], [], collections.Counter()
    for key, v in d.items():
        assert '"' not in v, key
        g = group(key)
        names = []
        for piece in v.split("\\n"):
            if not piece:
                names.append("")
                continue
            if (g, piece) not in seen:
                count[g] += 1
                seen[(g, piece)] = f"zz_ef_ms_{g}_{count[g]:02d}"
                sub.append((g, seen[(g, piece)], piece))
            names.append(f"${seen[(g, piece)]}$")
        chain = "\\n".join(names)
        comp.append(f' {key}:0 "{chain}"\n')
    # the data functions of a line -> a key each, named by the script value they read, so the line keeps the words
    exprs, xnames = {}, set()

    def xname(e):
        p = "p_" if "GetPlayer" in e else ""
        if "ScriptValue" not in e and "currency_symbol" in e:
            return f"zz_ef_ms_{p}cur"
        m = re.search(r"ScriptValue\('(?:zz_ef_)?(\w+)'\)", e) or re.search(r"\.(\w+)\(", e)
        base = f"zz_ef_ms_x_{p}" + (m.group(1) if m else "expr")
        if e.startswith("[Subtract_CFixedPoint("):
            base += "_rest"  # the account's change minus the lines shown: "прочее"
        elif "Negate_CFixedPoint" in e:
            base += "_neg"
        n, i = base, 2
        while n in xnames:
            n, i = f"{base}_{i}", i + 1
        return n

    def repl(m):
        e = m.group(0)
        if "(" not in e or e.startswith("[Concept("):
            return e
        if e not in exprs:
            exprs[e] = xname(e)
            xnames.add(exprs[e])
        return f"${exprs[e]}$"
    sub = [(g, name, re.sub(r"\[[^\[\]]*\]", repl, piece)) for g, name, piece in sub]
    out, last = [" # Tooltips: chains of line keys; the lines are below, a key each.\n"] + comp, None
    for g, name, piece in sub:
        if g != last:
            out.append(f"\n # ---- {g} ----\n")
            last = g
        out.append(f' {name}:0 "{piece}"\n')
    out.append("\n # ---- values: the data functions the lines show ----\n")
    out += [f' {n}:0 "{e}"\n' for e, n in exprs.items()]
    return out


def main():
    for lang in LANGS:
        d = build(lang)
        head = (f"l_{lang}:\n\n # GENERATED by tools/regen_ef_money_supply_loc.py.\n"
                " # EF.39/EF.44/EF.48: E&F's Money Supply tooltip as M0/M1/M2, a card per account.\n"
                " # UI.6: a key per tooltip line. Editing the text here by hand is fine to show what you want --\n"
                " # the next run of the generator overwrites it, so the edit is carried into the generator.\n")
        if lang not in ("english", "russian"):
            head += " # Not translated yet: English text.\n"
        lines = [head, "\n"] + split_lines(d)
        path = os.path.join(ROOT, lang, "replace", f"zz_ef_money_supply_replace_l_{lang}.yml")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path + ".tmp", "w", encoding="utf-8-sig", newline="\n") as f:
            f.write("".join(lines))
        os.replace(path + ".tmp", path)
    write_hook()
    write_log_effect()
    print("ok", len(d), "keys x", len(LANGS), "+ hook gui")


if __name__ == "__main__":
    main()
