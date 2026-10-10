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

Writes, through ld_gen.emit (by entry keys, into the fork «E&F: Ledgerdemain»):
  localization/<lang>/replace/ld_money_supply_replace_l_<lang>.yml (the tooltip's line keys and nested cards;
    english and russian, the other languages are copies of english: ld_loc_langs.py),
  gui/ld_money_hook.gui, common/scripted_effects/ld_money_log_rest.txt.
E&F's own MONEY_SUPPLY_DESC_* keys (chains of the line keys) live in E&F's files and are not generated.
Reads nothing outside this file.

Usage:
    py tools/regen_ef_money_supply_loc.py [--check]
"""
import collections
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ld_gen  # noqa: E402
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


def bop_lines(ru, c):
    """Е.3–Е.4 (5.10, Д.1): the week's balance of payments in two groups -- green "+" received, red "−" paid out --
    and one line of what it moves; shared by the 'external sector' card and Budget -> Economy (gui/ld_economy_panel.gui форка)."""
    cur, sv, money, delta, tt = ctx(c)

    def p(name, lab):
        return f"  #P +{sv(name)} {cur}#! {lab}"

    def n(name, lab):
        return f"  #N −{sv(name)} {cur}#! {lab}"
    if ru:
        return [
            "#b Платёжный баланс за неделю#!",
            f"#P Получено / у нас: +{sv('zz_ef_bop_in_total')} {cur}#!",
            p("zz_ef_bop_exp", "экспорт товаров (по ценам рынка)"),
            p("zz_ef_bop_div_in", "дивиденды из-за рубежа (оценка)"),
            p("zz_ef_bop_int_in", "проценты по облигациям"),
            p("zz_ef_bop_sec_in", "статьи бюджета с заграницей"),
            p("zz_ef_bop_fin_in", "продано / погашено облигаций других стран"),
            p("zz_ef_bop_oth_in", "прочее"),
            f"#N Отдано / мы должны: −{sv('zz_ef_bop_out_total')} {cur}#!",
            n("zz_ef_v_f_imp", "импорт товаров (по ценам рынка)"),
            n("zz_ef_bop_div_out", "дивиденды за рубеж (оценка)"),
            n("zz_ef_bop_int_out", "проценты по облигациям"),
            n("zz_ef_bop_sec_out", "статьи бюджета с заграницей"),
            n("zz_ef_bop_fin_out", "куплено облигаций других стран"),
            n("zz_ef_bop_oth_out", "прочее"),
            f"#b Сальдо {sv('zz_ef_v_f_ext_net', 'D+=')} {cur}#!",
            f"На что влияет: сальдо → мировой клиринг → резервы ЦБ {sv('zz_ef_v_f_clr_reserves_money', 'D+=')} {cur} "
            f"(металл {sv('zz_ef_v_f_clr_metal_money', 'D+=')}, валюта {sv('zz_ef_v_f_clr_fx_money', 'D+=')}) → покрытие "
            f"{sv('zz_ef_cb_cover', '%0')} → курс (сила к эталону {sv('zz_ef_currency_strength', '2')})",
            f"  не сведено клирингом {sv('zz_ef_v_f_clr_unsettled', 'D+=')} {cur} — платежи без оплаты",
        ]
    return [
        "#b Balance of payments this week#!",
        f"#P Received / ours: +{sv('zz_ef_bop_in_total')} {cur}#!",
        p("zz_ef_bop_exp", "goods exports (market prices)"),
        p("zz_ef_bop_div_in", "dividends from abroad (estimate)"),
        p("zz_ef_bop_int_in", "bond interest"),
        p("zz_ef_bop_sec_in", "budget lines with abroad"),
        p("zz_ef_bop_fin_in", "other countries' bonds sold / repaid"),
        p("zz_ef_bop_oth_in", "other"),
        f"#N Paid out / we owe: −{sv('zz_ef_bop_out_total')} {cur}#!",
        n("zz_ef_v_f_imp", "goods imports (market prices)"),
        n("zz_ef_bop_div_out", "dividends abroad (estimate)"),
        n("zz_ef_bop_int_out", "bond interest"),
        n("zz_ef_bop_sec_out", "budget lines with abroad"),
        n("zz_ef_bop_fin_out", "other countries' bonds bought"),
        n("zz_ef_bop_oth_out", "other"),
        f"#b Balance {sv('zz_ef_v_f_ext_net', 'D+=')} {cur}#!",
        f"What it moves: balance → the world clearing → CB reserves {sv('zz_ef_v_f_clr_reserves_money', 'D+=')} {cur} "
        f"(metal {sv('zz_ef_v_f_clr_metal_money', 'D+=')}, currency {sv('zz_ef_v_f_clr_fx_money', 'D+=')}) → cover "
        f"{sv('zz_ef_cb_cover', '%0')} → the rate (strength to the reference {sv('zz_ef_currency_strength', '2')})",
        f"  not settled by the clearing {sv('zz_ef_v_f_clr_unsettled', 'D+=')} {cur} — payments without settlement",
    ]


def main_text(lang, c):
    cur, sv, money, delta, tt = ctx(c)
    gold = "@gold!"
    ru = lang == "russian"
    # The user's aggregates (1.10 evening, run 12 -- as in real statistics): M0 = pops' cash at hand, M1 = +
    # business cash (without the Banks' cash -- the banks' own money, В2 7.10), M2 = + pops' deposits, M3 = + claims on abroad. The treasury, the banks' own funds (the pool)
    # and the CB's reserves are accounts outside the money supply. The currency's value and the inflation read M2.
    if ru:
        L = dict(title="Денежная масса", total="Всего (#b M3#!)", week="за неделю", wk="неделя", mo="мес.", yr="год", y5="5л.",
                 m0="наличные", cash="Наличные на руках", cashf="{0} в накопления, {1} во вклады = {3};\\n       (всего накоплений {2})",
                 m1="M0 + счета", bld="Касса предприятий", tc="из них торговые центры",
                 m2="M1 + вклады", dep="Вклады в банках", check="Сверка с движком",
                 m3="M2 + облигации других стран", abroad="Внешний сектор — чистая международная позиция", bonds="Облигации других стран",
                 abf="банки {0}, казна {1}",
                 abrf="облигации {0} + валюта в ЦБ {1} − наша валюта за рубежом {2}",
                 out="Вне денежной массы:", tr="Казна (счёт правительства)",
                 bank="Резервы банков (пул)", bankf="банки должны вкладчикам {0} и ЦБ {1}, выдали кредитов {2}; капитал банков {3} {4}; касса зданий «Банк» {5} — деньги банков, не в M1",
                 cb="Резервы ЦБ — покрытие валюты, не деньги",
                 cbf="металл; с чужой валютой {3} (счёт «Заграница») покрытие M2 {0}, норма 40%",
                 circ="Курс и инфляция считаются по M2",
                 infl="Инфляция за год", inflf="индекс цен потребительской корзины {2} (100 = базовые цены); для сравнения: рост M2 {0}, рост ВВП {1}",
                 debt="Долги (не деньги)", debtf="бюджета {0}, банков перед ЦБ {1}, потребкредит {2}, бизнеса {3}",
                 hint="Наведите на счёт — все переводы за неделю.",
                 dyn="месяц {0}, год {1}, 5 лет {2}", gdp="к ВВП")
    else:
        L = dict(title="Money Supply", total="Total (#b M3#!)", week="this week", wk="week", mo="mo", yr="yr", y5="5y",
                 m0="cash", cash="Cash at hand", cashf="{0} into savings, {1} into deposits = {3};\\n       (all savings {2})",
                 m1="M0 + accounts", bld="Business cash", tc="of it trade centres",
                 m2="M1 + deposits", dep="Bank deposits", check="Reconciliation with the engine",
                 m3="M2 + other countries' bonds", abroad="External sector — net international position", bonds="Other countries' bonds",
                 abf="banks {0}, treasury {1}",
                 abrf="bonds {0} + currency in the CB {1} − our currency abroad {2}",
                 out="Outside the money supply:", tr="Treasury (the government's account)",
                 bank="Bank reserves (the pool)", bankf="banks owe depositors {0} and the CB {1}, lent {2}; banks' capital {3} {4}; the Bank buildings' cash {5} — the banks' own money, not in M1",
                 cb="CB reserves — the currency's cover, not money",
                 cbf="metal; with the foreign currency {3} (the 'Abroad' account) cover of M2 {0}, norm 40%",
                 circ="The value and the inflation read M2",
                 infl="Inflation, a year", inflf="consumer price index {2} (100 = base prices); for comparison: M2 growth {0}, GDP growth {1}",
                 debt="Debts (not money)", debtf="budget {0}, banks to the CB {1}, consumer credit {2}, business {3}",
                 hint="Hover an account for all its transfers this week.",
                 dyn="month {0}, year {1}, 5 years {2}", gdp="of GDP")

    # 4.10 (the user edited the tooltip in the game's folder and asked for it short): the money supply and
    # nothing else -- a line per aggregate, its dynamics on a second line; a sub-line per account with its own
    # weekly change; outside the money -- treasury, banks (their liabilities said as liabilities), the CB
    # (its reserves told once, here). The legend of marks, the bubble, the debts and the reconciliation with
    # the engine went to their own nested tooltip (zz_ef_ms_tt_check).
    def dyn(k):
        pc = [sv(f"zz_ef_agg{k}_pct_{p}", "+=1%") for p in ("month", "year", "5y")]
        return (f"{delta(f'zz_ef_v_d_agg{k}')};\\n"
                f"({pc[0]}/{L['mo']}, {pc[1]}/{L['yr']}, {pc[2]}/{L['y5']})")

    def ratio(k):
        return f"{sv(f'zz_ef_agg_m{k}_to_gdp', '%0')} {L['gdp']}"

    ind = "       "
    lines = [
        f"#b {L['title']}#!",
        f"{L['total']}: #p {money('zz_ef_agg_m3')}#!",
        f"#b M0#! = {L['m0']}: #T {money('zz_ef_agg_m0')}#! — {ratio(0)} {dyn(0)}",
        f"→   {tt('zz_ef_ms_tt_pops', L['cash'])}: #T {money('zz_ef_pop_cash_held')}#!{mark('calc', ru)}: "
        + L["cashf"].format(delta("zz_ef_v_d_savings"), delta("zz_ef_v_d_deposits_neg"), money("zz_ef_pop_savings"),
                            delta("zz_ef_v_d_agg0")),
        f"#b M1#! = {L['m1']}: #T {money('zz_ef_agg_m1')}#! — {ratio(1)} {dyn(1)}",
        # В2 (7.10): without the Banks' cash (the banks' own money, below with the banks)
        f"→   {tt('zz_ef_ms_tt_buildings', L['bld'])}: #T {money('zz_ef_circ_business_cash')}#!{mark('eng', ru)} "
        f"{delta('zz_ef_v_d_buildings')}",
        f"#b M2#! = {L['m2']}: #T {money('zz_ef_agg_m2')}#! — {ratio(2)} {dyn(2)}",
        f"→   {tt('zz_ef_ms_tt_deposits', L['dep'])}: #T {money('zz_ef_pop_deposits')}#!{mark('mod', ru)} "
        f"{delta('zz_ef_v_d_deposits')}",
        f"#b M3#! = {L['m3']}: #T {money('zz_ef_agg_m3')}#! {dyn(3)}",
        f"→   {L['bonds']}: #T {money('zz_ef_foreign_assets')}#!{mark('ef', ru)} ("
        + L["abf"].format(money("zz_ef_bank_bonds"), money("zz_ef_treasury_bonds")) + ")",
        f"#b {L['out']}#!",
        f"→   {tt('zz_ef_ms_tt_treasury', L['tr'])}: #T {money('zz_ef_treasury')}#!{mark('eng', ru)} {delta('zz_ef_v_d_treasury')}",
        f"→   {tt('zz_ef_ms_tt_banks', L['bank'])}: #T {money('zz_ef_pool')}#!{mark('eng', ru)} {delta('zz_ef_v_d_pool')};\\n{ind}("
        + L["bankf"].format(money("zz_ef_pop_deposits"), money("zz_ef_bank_cb_debt"), money("zz_ef_bank_loans"),
                            sv("zz_ef_bank_capital", "D+="), cur, money("zz_ef_bank_cash")) + ")",
        f"→   {tt('zz_ef_ms_tt_abroad', L['abroad'])}: #T {sv('zz_ef_abroad_net', 'D+=')} {cur}#!{mark('mod', ru)} "
        f"{delta('zz_ef_v_d_abroad')};\\n{ind}(" + L["abrf"].format(money("zz_ef_foreign_assets"), money("zz_ef_fx_money"),
                                                                 money("zz_ef_fx_liab_all")) + ")",
        f"→   {tt('zz_ef_ms_tt_cb', L['cb'])}: #T {money('zz_ef_cb_money')}#!{mark('mod', ru)} {delta('zz_ef_v_d_cbm')};\\n{ind}("
        + L["cbf"].format(sv("zz_ef_cb_cover", "%0"), money("zz_ef_cb_money"), delta("zz_ef_v_d_cbm"), money("zz_ef_fx_money")) + ")",
        f"{L['infl']}: #T {sv('zz_ef_inflation', '+=1%')}#! (" + L['inflf'].format(
            sv('zz_ef_circ_growth_year', '+=1%'), sv('zz_ef_gdp_growth_year', '+=1%'), sv('zz_ef_price_index', '1')) + ")",
        f"#italic {L['hint']}#! {tt('zz_ef_ms_tt_check', L['check'])}",
    ]
    return "\\n".join(lines) + "\\n$TOOLTIP_DELIMITER$"


def check_text(lang, c):
    """The reconciliation with the engine's raw numbers (until 4.10 the tail of the money tooltip), the
    bubble signs, the debts and the legend of marks -- a nested tooltip of its own."""
    cur, sv, money, delta, tt = ctx(c)
    ru = lang == "russian"
    lines = [
        (f"Признаки пузыря: кредит {money('zz_ef_credit_total')} = {sv('zz_ef_credit_to_gdp', '%0')} ВВП; пул — "
         f"{sv('zz_ef_pool_months', '1')} мес. взносов; накопления — {sv('zz_ef_savings_to_gdp', '%0')} ВВП") if ru else
        (f"Bubble signs: credit {money('zz_ef_credit_total')} = {sv('zz_ef_credit_to_gdp', '%0')} of GDP; the pool — "
         f"{sv('zz_ef_pool_months', '1')} months of contributions; savings — {sv('zz_ef_savings_to_gdp', '%0')} of GDP"),
        ("Долги (не деньги): " if ru else "Debts (not money): ")
        + (("бюджета {0}, банков перед ЦБ {1}, потребкредит {2}, бизнеса {3}" if ru else
            "budget {0}, banks to the CB {1}, consumer credit {2}, business {3}").format(
            money("zz_ef_debt_principal"), money("zz_ef_bank_cb_debt"), money("zz_ef_cc_debt"), money("zz_ef_bc_debt"))),
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
    lines.append("")
    lines.append(SRC_LEGEND[0 if ru else 1])
    return "\\n".join(lines)


# ---------------------------------------------------------------------------
# Accounts and flows, all in the engine's money.
# ---------------------------------------------------------------------------

# The accounts in the order of M0..M3 (the user, 1.10 day), then the CB: its metal and E&F's currency good
# are reserves, outside the money (1.10 evening); abroad is its own account (claims: bonds) in M3.
ACC_ORDER = ["pops", "buildings", "banks", "abroad", "treasury", "cb"]
TITLES = {
    "treasury": ("Казна", "Treasury"),
    "buildings": ("Касса предприятий", "Business cash"),
    "banks": ("Резервы банков (пул)", "Bank reserves (the pool)"),
    "pops": ("Население", "Pops"),
    "cb": ("Центральный банк", "Central bank"),
    "abroad": ("Внешний сектор", "External sector"),
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


def gtx(fn, name):
    """В5.4: a budget trend minus a script value (the part of the line that is not what it says)."""
    return ("gtx", fn, name)


# В5.4 (5.10): interest on the treasury's loan from its own CB -- inside the "additional expenses"
CBL_INT = ("sv", "zz_ef_v_cbl_int")


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
    # minting through the CB (user 3.10): new money is issued by the CB and goes on to the treasury at once;
    # for the bridge (ext_expr) it stays an outside budget line
    (X, C, "выпуск: [concept_budget_minting] — новые деньги движка", "issue: [concept_budget_minting] — new engine money",
     gt("GetMintingTrend"), C),
    (C, K, "[concept_budget_minting] — выпуск ЦБ в казну", "[concept_budget_minting] — the CB's issue to the treasury",
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
    # 4.10 (the user's budget screenshot): E&F puts the treasury's foreign bonds' interest here, weekly --
    # the holder's "interest from investment in foreign debt" (interest_from_foreign_debt_investment) into the
    # additional income, the debtor's (interest_at_the_central_bank) into the additional expenses -- and
    # events' payments between countries (Haiti's independence debt). Payments with abroad: the CB settles
    # them (Hume), they belong to the abroad group, not outside the accounts.
    # В1.6 (the user 5.10 evening, "what about event expenses -- expeditions..."): since В5.5 the bonds' interest is not
    # here (the ledger pays it); what is left are vanilla expeditions (modifier_large_expedition_cost,
    # expedition_extra_expenses_modifier) and DLC events' country_expenses_add / country_tax_income_add -- spending at
    # home, not payments abroad: outside the accounts (was abroad -- the CB's metal paid for an expedition to the Congo,
    # the world's sum +0.3-0.5M a month without a counterpart, run s1h).
    (X, K, "[concept_budget_additional_income] — события и модификаторы (внутри страны)",
     "[concept_budget_additional_income] — events and modifiers (at home)",
     gt("GetAdditionalIncomeTrend"), None),
    # В5.4 (5.10): the additional expenses also hold E&F's interest on the treasury's loan from its own CB
    # (interest_at_the_central_bank) -- a payment inside the country: out of the abroad line, treasury -> CB, and
    # withdrawn there (the treasury is outside the money, the engine's expense destroys it)
    (K, X, "[concept_budget_additional_expenses] — экспедиции, события (внутри страны)",
     "[concept_budget_additional_expenses] — expeditions, events (at home)",
     gtx("GetAdditionalExpensesTrend", "zz_ef_v_cbl_int"), None),
    (K, C, "[concept_budget_additional_expenses] — проценты казны по кредиту ЦБ (E&F)",
     "[concept_budget_additional_expenses] — the treasury's interest on the CB's credit (E&F)", CBL_INT, None),
    (C, X, "проценты казны по кредиту ЦБ — деньги изъяты", "the treasury's interest on the CB's credit — money withdrawn",
     CBL_INT, None),
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
    (Z, C, "клиринг: металл за чистый приток из-за рубежа (прошлая неделя)",
     "clearing: metal for the net inflow from abroad (last week)", svp("zz_ef_v_f_cb_hume_m"), C),
    (C, Z, "клиринг: металл за чистый отток за рубеж (прошлая неделя)",
     "clearing: metal for the net outflow abroad (last week)", svn("zz_ef_v_f_cb_hume_m"), C),
    # П.6 / П.7 (4.10): the clearing's currency -- the abroad account only
    (X, Z, "клиринг: чужая валюта в ЦБ за чистый приток (прошлая неделя)",
     "clearing: foreign currency into the CB for the net inflow (last week)", sv_("zz_ef_v_w_clr_fx_in_money"), Z),
    (Z, X, "клиринг: наша валюта за рубеж за чистый отток — долг (прошлая неделя)",
     "clearing: our currency abroad for the net outflow — a debt (last week)", sv_("zz_ef_v_w_clr_cur_out"), Z),
    (X, Z, "клиринг: наша валюта вернулась — долг погашен (прошлая неделя)",
     "clearing: our currency came home — the debt is gone (last week)", sv_("zz_ef_v_w_clr_own_back"), Z),
    (X, C, "добытый металл, отчеканенный ЦБ, — в резервы", "mined metal coined by the CB — into the reserves",
     sv_("zz_ef_v_f_mint"), C),
    # UI.11 (5.10): E&F's CB building stores the market's gold / silver sell orders once a month
    # stage 2, night 6.10: weekly -- the CB building's purchase on the market, its sale of a surplus, the buy-back from pops
    (X, C, "металл: куплен на рынке и выкуплен у населения (за вычетом проданного)",
     "metal: bought on the market and from pops (net of the sold)", svp("zz_ef_v_f_cb_stock"), C),
    (C, X, "металл: продан на рынке (излишек сверх 60% покрытия)", "metal: sold on the market (the surplus over 60% cover)",
     svn("zz_ef_v_f_cb_stock"), C),
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
    # В5.5 (5.10): bonds as parts of the engine's debt (the bond ledger, tools/regen_ef_bond_ledger.py)
    (Z, K, "проценты по облигациям других стран (наша часть их госдолга)",
     "interest on other countries' bonds (our part of their government debt)", sv_("zz_ef_v_f_bl_int_in"), None),
    (Z, B, "облигации: держатели за рубежом купили часть нашего госдолга — цена в пул",
     "bonds: holders abroad bought a part of our government debt — the price into the pool", sv_("zz_ef_v_f_bl_sold"), None),
    (B, Z, "проценты держателям наших облигаций за рубежом", "interest to the holders of our bonds abroad",
     sv_("zz_ef_v_f_bl_int_out"), None),
    (B, Z, "погашение наших облигаций держателям за рубежом", "our bonds repaid to the holders abroad",
     sv_("zz_ef_v_f_bl_redeem"), None),
    # Д.R8б.21: the investment fund's shares across the border -- our pops and banks pay a fund abroad out of the pool;
    # buyers abroad pay into our fund's deposit, our pool
    (B, Z, "паи инвестиционного фонда за рубежом: население и банки заплатили из пула",
     "investment fund shares abroad: pops and banks paid out of the pool", sv_("zz_ef_v_f_fd_out"), None),
    (Z, B, "паи нашего инвестиционного фонда куплены из-за рубежа — во вклад фонда",
     "our investment fund's shares bought from abroad — into the fund's deposit", sv_("zz_ef_v_f_fd_in"), None),
    # R8б.7: the exchange's deals -- the banks and the pops pay out of the pool / get into it (the treasury's sales of
    # bonds are not a row: a flow of the treasury with abroad would enter the bridge's sums, and ext_net counts it already)
    (B, Z, "биржа: банки и население купили требования — из пула", "exchange: banks and pops bought claims — out of the pool",
     svn("zz_ef_v_f_xch_pool"), None),
    (Z, B, "биржа: банки и население продали требования — в пул", "exchange: banks and pops sold claims — into the pool",
     svp("zz_ef_v_f_xch_pool"), None),
    # the pool's unexplained loss (EF.48 item 2): R1а, 8.10 -- «прочее», nobody's money (was: guessed to be companies
    # buying levels and credited to the pops' savings, В1.2 -- archived, _archive/ld_pop_savings_guesses/)
    (B, X, "необъяснённая убыль пула (прочее)", "the pool's unexplained loss (other)", svn("zz_ef_v_f_pool_other"), None),
    (X, B, "необъяснённый приход в пул", "the pool's unexplained gain", svp("zz_ef_v_f_pool_other"), None),
    # M.3 (4.10): the CB issues money for Hume's inflow of metal into the banks, withdraws it for an outflow
    (C, B, "Юм: ЦБ выпустил деньги под приток металла (прошлая неделя)",
     "Hume: the CB issued money for the metal that came in (last week)", svp("zz_ef_v_w_hume_money"), B),
    (B, C, "Юм: ЦБ изъял деньги под отток металла (прошлая неделя)",
     "Hume: the CB withdrew money for the metal that went out (last week)", svn("zz_ef_v_w_hume_money"), B),
    # Д2.30 (6.10 day): our currency held by other CBs lies in our banks as their deposits
    (X, B, "вклады чужих ЦБ: наша валюта у них лежит в наших банках (прошлая неделя)",
     "other CBs' deposits: our currency they hold lies in our banks (last week)", svp("zz_ef_v_w_nr_dep"), B),
    (B, X, "вклады чужих ЦБ сняты: наша валюта вернулась домой (прошлая неделя)",
     "other CBs' deposits withdrawn: our currency came home (last week)", svn("zz_ef_v_w_nr_dep"), B),
    # Д4.5 (4.10): the treasury's surplus over its limit buys the banks' bonds
    (K, B, "излишек казны сверх потолка — покупка облигаций банков", "the treasury's surplus over its limit — banks' bonds bought",
     sv_("zz_ef_v_f_tr_pool"), None),
    # Д2.7б (5.10): consols -- the CB's bonds sold are the treasury's perpetual debt to pops (zz_ef_consols.txt)
    (K, N, "консоли: проценты держателям облигаций ЦБ (ставка правительства)",
     "consols: interest to the holders of the CB's bonds (the government's rate)", sv_("zz_ef_v_f_cons_int"), None),
    (K, N, "консоли: выкуп из излишка казны сверх потолка", "consols: bought back out of the treasury's surplus over its limit",
     sv_("zz_ef_v_f_cons_buy"), None),
]

NOTES = {
    # 4.10 (the user: the cards are useful but too long): one or two sentences each
    "treasury": ("Статьи бюджета — точно, за неделю, как в бюджете игры.",
                 "Budget lines are exact, a week, as in the game's budget."),
    "buildings": ("Деньги всех зданий. Прочее — сглаженные тренды бюджета против точного недельного изменения.",
                  "The cash of all buildings. Other: smoothed budget trends against the exact weekly change."),
    "banks": ("Резервы банков (инвестиционный пул). Частная стройка идёт через казну: пул → казна → предприятия. "
              "Металл банков (покупает здание «Банк») по паритету — [Country.MakeScope.ScriptValue('zz_ef_bankm_money')|D]; "
              "кредит бизнесу и потребкредит — не больше металл / норма резерва "
              "([Country.MakeScope.ScriptValue('zz_ef_reserve_norm')|%1]) × множитель покрытия: предел "
              "[Country.MakeScope.ScriptValue('zz_ef_credit_limit')|D], выдано [Country.MakeScope.ScriptValue('zz_ef_credit_now')|D].",
              "The banks' reserves (the investment pool). Private construction goes pool → treasury → businesses. "
              "The banks' metal (bought by the Bank building) at parity — [Country.MakeScope.ScriptValue('zz_ef_bankm_money')|D]; "
              "business and consumer credit stay under metal / the reserve norm "
              "([Country.MakeScope.ScriptValue('zz_ef_reserve_norm')|%1]) × the cover multiplier: limit "
              "[Country.MakeScope.ScriptValue('zz_ef_credit_limit')|D], lent [Country.MakeScope.ScriptValue('zz_ef_credit_now')|D]."),
    "abroad": ("Запас счёта — чистая международная позиция: облигации других стран и чужая валюта в ЦБ минус наша валюта у других ЦБ. "
               "Платежи с заграницей сводит мировой клиринг: отток оплачивается металлом ЦБ (доля — по доверию к "
               "валюте) и нашей валютой, приток — долей металла и валют, собранных с плательщиков. Наша валюта у чужих ЦБ лежит "
               "вкладами в наших банках ([Country.MakeScope.ScriptValue('zz_ef_nr_dep_v')|D]) — деньги работают дома.",
               "The account's stock is the net international position: other countries' bonds and foreign currency in the CB minus our currency at "
               "other CBs. Payments with abroad go through the world clearing: an outflow pays in the CB's metal (the "
               "share by trust in the currency) and in our currency, an inflow takes a share of the metal and "
               "currencies the payers brought. Our currency at other CBs lies as deposits in our banks "
               "([Country.MakeScope.ScriptValue('zz_ef_nr_dep_v')|D]) — the money works at home."),
    "cb": ("Запас счёта — металл ЦБ по паритету: покрытие валюты, а не деньги (вне M0–M3). Чужая валюта ЦБ — в счёте "
           "«Заграница», в покрытии учтена.",
           "The account's stock is the CB's metal at parity: the currency's cover, not money (outside M0–M3). The CB's "
           "foreign currency is in the 'Abroad' account and counts in the cover."),
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
    if v[0] == "gtx":
        return (f"Max_CFixedPoint(Subtract_CFixedPoint(Abs_CFixedPoint(GetTrendValue(Country.{v[1]})), "
                f"Country.MakeScope.ScriptValue('{v[2]}')), {ZERO})")
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


MINTING = ("gt", "GetMintingTrend")   # passes through the CB card, still outside for the bridge


def ext_expr():
    """The budget's lines outside the accounts (outside + abroad), in - out, a week."""
    ins, outs = [], []
    for f in FLOWS:
        frm, to, _, _, v, _ = f
        if to == K and (frm in (X, Z) or v == MINTING):
            ins.append(expr(v))
        elif frm == K and (to in (X, Z) or v == CBL_INT):
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
# accounts (GUI-only data) to script (scripted_guis/ld_money_hook.txt).
# CMF's pattern as is (_cmf/gui/com_hidden_trigger.gui, character names):
# a hidden but "visible" widget of real size, an item per list entry whose
# state fires on_finish when trigger_when turns true -- CMF's own trigger,
# [Scope.IsSet] (the item exists). BPM's _show/on_start, trigger_on_create/
# on_start and trigger_when on the country's var never fired here
#. The receiver consumes var:zz_ef_hook_pending and takes
# the country off the list, so repeated calls do nothing. R1а.8: the receiver
# only stores the numbers; the scheduler's step uses the latest it got.
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
				# the player's country takes role A at once (the engine has no on_action for a tag switch)
				state = {{
					trigger_when = "[Scope.IsSet]"
					on_finish = "[GetScriptedGui('zz_ef_player_sg').Execute( GuiScope.SetRoot( GetPlayer.MakeScope ).End )]"
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
    # П.17 (4.10): the BoP's primary income -- E&F puts the treasury bonds' weekly interest into the additional
    # income / expenses (zz_ef_f_aint in the receiver)
    ("aint", "Subtract_CFixedPoint(Abs_CFixedPoint(GetTrendValue(Country.GetAdditionalIncomeTrend)), "
             "Abs_CFixedPoint(GetTrendValue(Country.GetAdditionalExpensesTrend)))"),
    # В1.6 (5.10 evening): the treasury's income the world's trade pays -- market fees, strait tolls, piracy (the world
    # trade pool, zz_ef_wtr_*: the importers' payments are shared by the exporters and these)
    ("tfees", "Subtract_CFixedPoint(Subtract_CFixedPoint(Abs_CFixedPoint(Country.GetMarketFeesIncome), "
              "Negate_CFixedPoint(Abs_CFixedPoint(Country.PredictTolls))), "
              "Negate_CFixedPoint(Abs_CFixedPoint(GetTrendValue(Country.GetPiracyIncomeTrend))))"),
]


# UI.7 (3.10): the "прочее" of each card, as the tooltip computes it -> the
# weekly log line EFO, so a run shows how big each residual is and when.
RESID = {}
# UI.7 (3.10, runs e0_4/e0_5): what is left in each card's residual, named
OTHER_LAB = {
    "cb": ("прочее — валютные сделки E&F, прочие правки металла E&F",
           "other — E&F's currency deals, E&F's other metal edits"),
    "abroad": ("прочее — переоценка валют, валютные сделки E&F, наша валюта у других ЦБ",
               "other — currencies revalued, E&F's currency deals, our currency at other CBs"),
    "buildings": ("прочее — сглаженные тренды бюджета против недельного изменения кассы",
                  "other — smoothed budget trends against the weekly change of the cash"),
}
CLAIM_VALUES = {"zz_ef_v_d_bonds", "zz_ef_v_d_tbonds", "zz_ef_v_w_clr_fx_in_money", "zz_ef_v_w_clr_cur_out",
                "zz_ef_v_w_clr_own_back"}

# UI.9 step 1 (3.10, the user: "I cannot check which information is true"): every number in a card gets
# a grey mark of where it comes from.
#   eng  -- read from the engine as is (budget lines, cash of buildings, the pool's in/out);
#   mod  -- money the mod moved itself (deposits, credit, Hume's metal, coinage) -- real, but our rules;
#   calc -- derived from other numbers (money conservation, a residual, a revaluation);
#   est  -- an estimate (wages = GDP / 52, purchases closing the pops' card);
#   ef   -- an E&F variable (its bonds).
SRC_ENGINE = {"zz_ef_v_d_tc", "zz_ef_v_f_contrib", "zz_ef_v_f_transfer"}
SRC_MOD = {"zz_ef_v_f_cons_int", "zz_ef_v_f_cons_buy", "zz_ef_v_f_fd_out", "zz_ef_v_f_fd_in", "zz_ef_v_f_xch_pool", "zz_ef_v_f_bl_int_in", "zz_ef_v_f_bl_sold", "zz_ef_v_f_bl_int_out", "zz_ef_v_f_bl_redeem", "zz_ef_v_w_clr_fx_in_money", "zz_ef_v_w_clr_cur_out", "zz_ef_v_w_clr_own_back", "zz_ef_v_w_hume_money", "zz_ef_v_w_nr_dep", "zz_ef_v_f_tr_pool", "zz_ef_v_w_dep_int", "zz_ef_v_w_cc_issue", "zz_ef_v_w_cc_repay",
           "zz_ef_v_w_cc_int", "zz_ef_v_f_cb_borrow", "zz_ef_v_f_cb_repay", "zz_ef_v_f_cb_interest", "zz_ef_v_f_mint",
           "zz_ef_v_f_mint_own", "zz_ef_v_f_mint_tr", "zz_ef_v_f_cb_hume_m"}
SRC_CALC = {"zz_ef_v_f_inflow", "zz_ef_v_f_pool_other", "zz_ef_v_f_cb_reval",
            "zz_ef_v_f_cb_rescale", "zz_ef_tr_to_cb"}
SRC_EF = {"zz_ef_v_d_bonds", "zz_ef_v_d_tbonds", "zz_ef_v_cbl_int", "zz_ef_v_f_cb_stock"}
SRC_LAB = {"eng": ("дв", "eng"), "mod": ("мод", "mod"), "calc": ("расч", "calc"), "est": ("оц", "est"),
           "ef": ("E&F", "E&F")}
# the account's own change: engine stocks, our CB metal, E&F's bonds
SRC_ACC = {"treasury": "eng", "buildings": "eng", "banks": "eng", "cb": "mod", "abroad": "mod"}
SRC_LEGEND = ("#grey Метки: дв — число движка как есть (бюджет, кассы, пул); мод — деньги, которые перевёл мод (вклады, "
              "кредиты, металл); расч — выведено из других чисел (сохранение денег, остаток, переоценка); оц — оценка "
              "(зарплаты = ВВП / 52); E&F — переменная E&F (облигации).#!",
              "#grey Marks: eng — the engine's number as is (budget, cash, pool); mod — money the mod moved (deposits, "
              "credit, metal); calc — derived from other numbers (money conservation, residual, revaluation); est — "
              "an estimate (wages = GDP / 52); E&F — an E&F variable (bonds).#!")


def src_of(v):
    kind = v[0]
    if kind in ("gt", "gv"):
        return "eng"
    if kind == "gtx":
        return "calc"
    if kind in ("expr", "closing"):
        return "est"
    name = v[1]
    for key, names in (("eng", SRC_ENGINE), ("mod", SRC_MOD), ("calc", SRC_CALC), ("ef", SRC_EF)):
        if name in names:
            return key
    raise SystemExit(f"UI.9: no source mark for {name} -- add it to SRC_*")


def mark(key, ru):
    return f" #grey {SRC_LAB[key][0 if ru else 1]}#!"


def flow_key(v):
    if v[0] == "expr":
        return "wages"
    if v[0] == "closing":
        return "closing"
    if v[0] == "gtx":
        v = ("gt", v[1])
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
    e = "common/scripted_effects/zz_ef_money_log_rest.txt"
    parts = "".join(f"|{LOG_KEYS[a]} [{RESID[a].replace('Country.', 'THIS.GetCountry.')}|0]"
                    for a in ACC_ORDER if a in RESID and a in LOG_KEYS)
    ld_gen.emit(e, ("# GENERATED by tools/regen_ef_money_supply_loc.py -- do not edit by hand.\n"
                "# UI.7 (3.10): the residual (\"прочее\") of each account card of the Money Supply\n"
                "# tooltip, the same expressions, as a weekly log line EFO. Country scope.\n"
                "zz_ef_money_log_rest = {\n"
                f"\tdebug_log = \"EFO|[TimeKeeper.GetCurrentDate.GetString]|[THIS.GetCountry.GetNameNoFormatting]{parts}\"\n"
                + "".join(f"\tdebug_log = \"{ln}\"\n" for ln in eff_lines())
                + "}\n"))


def write_hook():
    probes = "".join(f".AddScope( 'g_{k}', MakeScopeValue( {fn} ) )" for k, fn in PROBES)
    ld_gen.emit("gui/zz_ef_money_hook.gui", HOOK_GUI.format(ext=ext_expr(), abr=abr_expr(), probes=probes))


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


def pops_card(lang):
    """4.10: cash at hand -- the head is M0's weekly change (the money tooltip's), the rows add up to it: what
    went into savings and what went into / out of deposits at the last receiver (the window of the ledger).
    The pops' income and spending of the week (transit, estimates) follow, not in the sum."""
    cur, sv, money, delta, tt = ctx("Country")
    ru = lang == "russian"
    k = 0 if ru else 1
    v = lambda n: f"Country.MakeScope.ScriptValue('{n}')"
    L = [f"#b {'Наличные на руках за неделю' if ru else 'Cash at hand this week'}: {delta('zz_ef_v_d_agg0')}#!{mark('calc', ru)}",
         "1 " + ("В накопления" if ru else "Into savings"),
         f"  ↔ {sv('zz_ef_v_w_inflow', 'D+=')} {cur}{mark('calc', ru)} " + ("взносы в пул по движку (вклады) за вычетом стройки из вкладов"
                                                                         if ru else "contributions to the pool by the engine (deposits) less construction paid from them"),
         # stage 2, night 6.10: the mint is gone (М); the CB's buy-back of the pops' metal and the savings over their norm
         f"  ← #P +{money('zz_ef_v_f_buyback_m')}#!{mark('mod', ru)} " + ("ЦБ выкупил металл населения (паритет + 2%, новые деньги)" if ru else "the CB bought the pops' metal (parity + 2%, new money)"),
         ]
    resid = v("zz_ef_v_d_agg0")
    for n_, sign in (("zz_ef_v_w_inflow", -1), ("zz_ef_v_f_buyback_m", -1)):
        resid = (f"Subtract_CFixedPoint({resid}, {v(n_)})" if sign < 0 else
                 f"Subtract_CFixedPoint({resid}, Negate_CFixedPoint({v(n_)}))")
    L.append("2 " + ("Вне счетов" if ru else "Outside the accounts"))
    L.append(f"  ↔ [{resid}|D+=] {cur}{mark('calc', ru)} " + ("прочее" if ru else "other"))
    L.append("")
    L.append("#b " + ("Доходы и траты населения за неделю (транзит, оценка — в сумму не входят):" if ru else
                      "Pops' income and spending this week (transit, estimates — not in the sum):") + "#!")
    for other, dr, f in card_flows(N):
        if other == X:
            continue
        e = expr(f[4])
        lab = (f[2] if ru else f[3]) + f" ({TITLES[other][k].lower()})"
        L.append(f"  ← #P +[{e}|D] {cur}#! {lab}" if dr == "in" else f"  → #N −[{e}|D] {cur}#! {lab}")
    L.append("")
    L.append((f"Накопления {money('zz_ef_pop_savings')}: во вкладах {money('zz_ef_pop_deposits')}, на руках "
              f"{money('zz_ef_pop_cash')} — банкноты, долг ЦБ населению (двигают только проводки: консоли, выкуп металла); "
              f"норма накоплений {money('zz_ef_sav_norm')}. Потребкредит: долг {money('zz_ef_cc_debt')}, "
              f"ставка {sv('zz_ef_cc_rate', '%1')}. Металл населения: золото {sv('zz_ef_popm_gold', 'D')}, серебро "
              f"{sv('zz_ef_popm_silver', 'D')} ед. — по паритету {money('zz_ef_popm_money')}.")
             if ru else
             (f"Savings {money('zz_ef_pop_savings')}: in deposits {money('zz_ef_pop_deposits')}, at hand "
              f"{money('zz_ef_pop_cash')} — banknotes, the CB's debt to pops (moved by postings only: consols, the metal "
              f"buy-back); savings norm {money('zz_ef_sav_norm')}. Consumer credit: debt {money('zz_ef_cc_debt')}, "
              f"rate {sv('zz_ef_cc_rate', '%1')}. Pops' metal: gold {sv('zz_ef_popm_gold', 'D')}, silver "
              f"{sv('zz_ef_popm_silver', 'D')} units — {money('zz_ef_popm_money')} at parity."))
    return "\\n".join(L)


def deposits_card(lang):
    """4.10: pops' deposits -- the head is the ledger's weekly change, the rows of the last receiver add up to it."""
    cur, sv, money, delta, tt = ctx("Country")
    ru = lang == "russian"
    v = lambda n: f"Country.MakeScope.ScriptValue('{n}')"
    resid = v("zz_ef_v_d_deposits")
    for n_, sign in (("zz_ef_v_w_dep_int", -1), ("zz_ef_v_f_fd_pp", 1), ("zz_ef_v_f_xch_pp", -1)):
        resid = (f"Subtract_CFixedPoint({resid}, {v(n_)})" if sign < 0 else
                 f"Subtract_CFixedPoint({resid}, Negate_CFixedPoint({v(n_)}))")
    L = [f"#b {'Вклады в банках за неделю' if ru else 'Bank deposits this week'}: {delta('zz_ef_v_d_deposits')}#!{mark('mod', ru)}",
         f"  ← #P +{money('zz_ef_v_w_dep_int')}#!{mark('mod', ru)} " + ("проценты (платят банки из пула)" if ru else "interest (the banks pay it from the pool)"),
         f"  → #N −{money('zz_ef_v_f_fd_pp')}#!{mark('mod', ru)} " + ("паи инвестиционного фонда: население купило из вкладов"
                                                                     if ru else "investment fund shares: pops bought them out of deposits"),
         f"  ↔ {sv('zz_ef_v_f_xch_pp', 'D+=')} {cur}{mark('mod', ru)} " + ("биржа: население продало (+) и купило (−) требования"
                                                                       if ru else "exchange: pops sold (+) and bought (−) claims"),
         f"  ↔ [{resid}|D+=] {cur}{mark('calc', ru)} " + ("прочее" if ru else "other"),
         "",
         (f"Вклады — долг банков населению; деньги лежат в резервах банков (пул) и в выданных кредитах. Ставка по "
          f"вкладам {sv('zz_ef_deposit_rate', '%1')} = ключевая − маржа банков {sv('zz_ef_deposit_margin', '%1')}.")
         if ru else
         (f"Deposits are the banks' debt to pops; the money is in the banks' reserves (the pool) and in their loans. "
          f"Deposit rate {sv('zz_ef_deposit_rate', '%1')} = key − the banks' margin {sv('zz_ef_deposit_margin', '%1')}.")]
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
        if acc == N:
            d["zz_ef_ms_tt_pops"] = pops_card(lang)
            continue
        flows = card_flows(acc)
        pays = []
        head = TITLES[acc][k] + (" за неделю" if ru else " this week")
        if acc == Z:
            head = ("Чистая международная позиция за неделю" if ru else "Net international position this week")
        L = [f"#b {head}: {delta(DELTA[acc])}#!{mark(SRC_ACC[acc], ru)}" if acc in DELTA else f"#b {head}#!"]
        resid = f"Country.MakeScope.ScriptValue('{DELTA[acc]}')" if acc in DELTA else None
        fixed_resid = "Country.MakeScope.ScriptValue('zz_ef_other_treasury_rest')" if acc == K else None
        n = 0
        for other in [a for a in ACC_ORDER if a != acc] + [X]:
            rows = [(dr, f) for o, dr, f in flows if o == other]
            if not rows and not (other == X and resid):
                continue
            n += 1
            L.append(f"{n} {TITLES[other][k]}")
            if acc == Z:
                # 4.10: payments with abroad do not move the claims -- listed apart, under the groups
                pays += [(other, dr, f) for dr, f in rows if f[4][1] not in CLAIM_VALUES]
                rows = [(dr, f) for dr, f in rows if f[4][1] in CLAIM_VALUES]
                if not rows and other != X:
                    n -= 1
                    L.pop()
                    continue
            for dr, f in rows:
                e = expr(f[4])
                lab = f[2] if ru else f[3]
                # UI.7 (3.10): abroad = the country's claims (bonds); payments with abroad do not
                # change them -- the CB settles them in metal (Hume) -- so they stay out of its residual
                # the same for the CB: E&F's treasury moves with the CB do not touch its metal
                counts = (acc != Z or f[4][1] in CLAIM_VALUES) and not (acc == C and f[4][1] == "zz_ef_tr_to_cb")
                if dr == "in":
                    L.append(f"  ← #P +[{e}|D] {cur}#!{mark(src_of(f[4]), ru)} {lab}")
                    if resid and counts:
                        resid = f"Subtract_CFixedPoint({resid}, {e})"
                else:
                    L.append(f"  → #N −[{e}|D] {cur}#!{mark(src_of(f[4]), ru)} {lab}")
                    if resid and counts:
                        resid = f"Subtract_CFixedPoint({resid}, Negate_CFixedPoint({e}))"
            if other == X and resid:
                lab_o = OTHER_LAB.get(acc, ("прочее", "other"))[0 if ru else 1]
                L.append(f"  ↔ [{fixed_resid or resid}|D+=] {cur}{mark('calc', ru)} {lab_o}")
                RESID[acc] = fixed_resid or resid
            if other == X and acc == K:
                bin_, bout = ("Country.MakeScope.ScriptValue('zz_ef_total_income_week')",
                              "Country.MakeScope.ScriptValue('zz_ef_total_expenses_week')")
                for o, dr, f in flows:
                    if f[4][0] in ("gt", "gv", "gtx") or f[4] in (sv_("zz_ef_v_f_transfer"), CBL_INT):
                        if dr == "in":
                            bin_ = f"Subtract_CFixedPoint({bin_}, {expr(f[4])})"
                        else:
                            bout = f"Subtract_CFixedPoint({bout}, {expr(f[4])})"
                L.append(("  проверка: доходы бюджета вне строк " if ru else "  check: budget income not in any line ")
                         + f"[{bin_}|D+=] {cur}" + (", расходы вне строк " if ru else ", expenses not in any line ")
                         + f"[{bout}|D+=] {cur}")
        if not n:
            L.append(none)
        if acc == Z:
            # 4.10 (the user: "where does +108K come from if the lines do not add up"): the block lists exactly the
            # parts of the net flow the step records (zz_ef_ext_net_week); the budget lines with abroad are the
            # breakdown of its first part, the trade centres' cash is not in it since night 2
            # П.17 (4.10, the user: "the abroad account in an academic form"): the balance of payments of the week,
            # its standard parts; current + financial = the net flow the step records; the clearing settles it in
            # reserve assets; what it did not settle is the BoP's errors and omissions
            if ru:
                # Е.3–Е.4 (5.10, Д.1): two groups and what it moves (bop_lines); the budget lines -- only here
                L += bop_lines(True, "Country") + [
                      "#grey Статьи бюджета с заграницей сейчас (+ в страну, − за рубеж):#!"]
                clr = [f"Клиринг: платёж — набор: {sv('zz_ef_clr_own_share', '%0')} нашей валютой — по доверию к ней "
                       f"(сила к эталону {sv('zz_ef_currency_strength', '2')}), остальное по стандарту получателя — "
                       f"металлом, его валютой из наших резервов или нашим долгом; за неделю заплачено "
                       f"{sv('zz_ef_v_f_clr_paid')} @gold!, получено {sv('zz_ef_v_f_clr_got')} @gold!"]
            else:
                L += bop_lines(False, "Country") + [
                      "#grey Budget lines with abroad now (+ in, − out):#!"]
                clr = [f"Clearing: a payment is a set: {sv('zz_ef_clr_own_share', '%0')} in our currency — by trust in "
                       f"it (strength to the reference {sv('zz_ef_currency_strength', '2')}), the rest by the receiver's "
                       f"standard — metal, its currency out of our reserves or our debt; this week paid "
                       f"{sv('zz_ef_v_f_clr_paid')} @gold!, received {sv('zz_ef_v_f_clr_got')} @gold!"]
            for other, dr, f in pays:
                if other != K:
                    continue
                e = expr(f[4])
                lab = f[2] if ru else f[3]
                L.append(f"    #grey +[{e}|D] {cur} {lab}#!" if dr == "out" else f"    #grey −[{e}|D] {cur} {lab}#!")
            L += clr
        L += ["", NOTES[acc][k]]
        if acc == B:
            # Ф.1 (В7.3) and the CB's credit, a line per item (the user 4.10: one paragraph does not read)
            if ru:
                L += [f"#b Баланс банков#!",
                      f"  активы {money('zz_ef_bank_assets')}: резервы (пул) {money('zz_ef_pool')}, кредит бизнесу "
                      f"{money('zz_ef_bc_debt')}, потребкредит {money('zz_ef_cc_debt')}, облигации {money('zz_ef_bank_bonds')}",
                      f"  обязательства {money('zz_ef_bank_liabilities')}: вклады {money('zz_ef_pop_deposits')}, вклад "
                      f"инвестиционного фонда {money('zz_ef_fd_dep_v')}, долг ЦБ "
                      f"{money('zz_ef_bank_cb_debt')}, вклады чужих ЦБ {money('zz_ef_nr_dep_v')}",
                      f"  #b капитал банков {sv('zz_ef_bank_capital', 'D+=')} {cur}#! (меньше нуля — вклады не покрыты)",
                      f"#b Кредит бизнесу#! {money('zz_ef_bc_debt')} ({sv('zz_ef_bc_debt_to_gdp', '%1')} ВВП): за неделю выдано "
                      f"{money('zz_ef_v_f_bc_new')}, проценты {money('zz_ef_v_f_bc_int')}, погашено {money('zz_ef_v_f_bc_paid')}",
                      f"#b Кредит ЦБ банкам#! {money('zz_ef_bank_cb_debt')}, цель {money('zz_ef_cb_credit_target')}; "
                      f"пул — {sv('zz_ef_pool_months', '1')} мес. взносов"]
            else:
                L += [f"#b Banks' balance sheet#!",
                      f"  assets {money('zz_ef_bank_assets')}: reserves (the pool) {money('zz_ef_pool')}, business credit "
                      f"{money('zz_ef_bc_debt')}, consumer credit {money('zz_ef_cc_debt')}, bonds {money('zz_ef_bank_bonds')}",
                      f"  liabilities {money('zz_ef_bank_liabilities')}: deposits {money('zz_ef_pop_deposits')}, the investment "
                      f"fund's deposit {money('zz_ef_fd_dep_v')}, CB debt "
                      f"{money('zz_ef_bank_cb_debt')}, other CBs' deposits {money('zz_ef_nr_dep_v')}",
                      f"  #b banks' capital {sv('zz_ef_bank_capital', 'D+=')} {cur}#! (under zero — deposits not covered)",
                      f"#b Business credit#! {money('zz_ef_bc_debt')} ({sv('zz_ef_bc_debt_to_gdp', '%1')} of GDP): this week lent "
                      f"{money('zz_ef_v_f_bc_new')}, interest {money('zz_ef_v_f_bc_int')}, repaid {money('zz_ef_v_f_bc_paid')}",
                      f"#b CB credit to banks#! {money('zz_ef_bank_cb_debt')}, target {money('zz_ef_cb_credit_target')}; "
                      f"the pool holds {sv('zz_ef_pool_months', '1')} months of contributions"]
        if acc == C:
            if ru:
                L += [f"#b Резервы ЦБ {money('zz_ef_cb_money')}#! по паритету {sv('zz_ef_cb_valuation', '4')}:",
                      f"  металл {money('zz_ef_cb_money')}: золото {sv('gold_state_native_for_stockpile')} @gold! + серебро "
                      f"{sv('silver_state_native_for_stockpile')} @silver! (в металле стандарта "
                      f"{sv('central_bank_metal_reserves_state')})",
                      f"  + чужая валюта {money('zz_ef_fx_money')} (в металле {sv('zz_ef_v_fx_metal')}) — в счёте «Заграница»",
                      f"Покрытие M2 {sv('zz_ef_cb_cover', '%0')} (металл и валюта); чистый поток с заграницей этой недели "
                      f"{sv('zz_ef_v_f_ext_net', 'D+=')} {cur} — в клиринг на следующем шаге."]
            else:
                L += [f"#b CB reserves {money('zz_ef_cb_money')}#! at parity {sv('zz_ef_cb_valuation', '4')}:",
                      f"  metal {money('zz_ef_cb_money')}: gold {sv('gold_state_native_for_stockpile')} @gold! + silver "
                      f"{sv('silver_state_native_for_stockpile')} @silver! (in the standard's metal "
                      f"{sv('central_bank_metal_reserves_state')})",
                      f"  + foreign currency {money('zz_ef_fx_money')} (in metal {sv('zz_ef_v_fx_metal')}) — in the 'Abroad' account",
                      f"Cover of M2 {sv('zz_ef_cb_cover', '%0')} (metal and currency); this week's net flow with abroad "
                      f"{sv('zz_ef_v_f_ext_net', 'D+=')} {cur} — into the clearing at the next step."]
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
    d["zz_ef_ms_tt_check"] = check_text(src, "Country")
    d["zz_ef_ms_tt_deposits"] = deposits_card(src)
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
        if key in KEYS_COUNTRY or key in KEYS_PLAYER:
            continue  # E&F's own MONEY_SUPPLY_DESC_* keys (replaced in E&F's files); the lines they chain stay here
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
                " # E&F's Money Supply tooltip as M0/M1/M2, a card per account.\n"
                " # a key per tooltip line. Editing the text here by hand is fine to show what you want --\n"
                " # the next run of the generator overwrites it, so the edit is carried into the generator.\n")
        if lang not in ("english", "russian"):
            head += " # Not translated yet: English text.\n"
        lines = [head, "\n"] + split_lines(d)
        ld_gen.emit(f"localization/{lang}/replace/zz_ef_money_supply_replace_l_{lang}.yml", "".join(lines))
    write_hook()
    write_log_effect()
    ld_gen.report("regen_ef_money_supply_loc")


if __name__ == "__main__":
    main()
