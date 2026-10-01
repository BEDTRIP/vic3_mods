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
import os

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
    if ru:
        L = dict(title="Денежная масса", sub="деньги движка", total="Всего (M2)", month="за неделю",
                 m0="M0 — деньги государства", tr="Казна", m1="M1 = M0 + деньги предприятий",
                 bld="Касса предприятий", tc="из них торговые центры", m2="M2 = M1 + деньги банков", bank="Средства банков",
                 m3="M3 — в обращении: касса предприятий + пул + накопления на руках (без казны)",
                 infl="Инфляция из учёта денег за год", inflf="рост M3 {0} − рост ВВП {1}",
                 pops="Население", cbab="ЦБ и заграница", metal="резервы металла", cover="покрытие по паритету",
                 sav="Накопления населения (счёт мода, вне денег движка)", savd="во вкладах (в пуле)",
                 savc="на руках",
                 debt="Долг (не деньги)", princ="бюджета", dcb="перед ЦБ (E&F)",
                 bdebt="банков перед ЦБ", fx="Товар-валюта E&F (штуки, не деньги)", fxcb="склад ЦБ",
                 fxab="у других стран", hint="Наведите на счёт — все переводы за неделю.",
                 dyn="месяц {0}, год {1}, 5 лет {2}", fxm="за месяц")
    else:
        L = dict(title="Money Supply", sub="the engine's money", total="Total (M2)", month="this week",
                 m0="M0 — state money", tr="Treasury", m1="M1 = M0 + business money", bld="Business cash",
                 tc="of it trade centres",
                 m2="M2 = M1 + bank money", bank="Bank funds",
                 m3="M3 — in circulation: business cash + the pool + savings at hand (no treasury)",
                 infl="Inflation from the money accounting, a year", inflf="M3 growth {0} − GDP growth {1}", cbab="The CB and abroad", metal="metal reserves",
                 cover="cover at parity",
                 pops="Pops", debt="Debt (not money)", princ="budget",
                 sav="Pops' savings (the mod's account, outside the engine's money)", savd="in deposits (in the pool)",
                 savc="at hand",
                 dcb="to the CB (E&F)", bdebt="banks to the CB", fx="E&F currency good (counts, not money)",
                 fxcb="CB stock", fxab="held by other countries", hint="Hover an account for all its transfers this week.",
                 dyn="month {0}, year {1}, 5 years {2}", fxm="this month")

    def ing(name):
        return f" ≈ {sv(name)} {gold}"

    def dyn(m):
        pc = [sv(f"zz_ef_{m}_pct_{p}", "+=1%") for p in ("month", "year", "5y")]
        return f"{delta('zz_ef_v_d_' + m)} {L['month']}; " + L["dyn"].format(*pc)

    lines = [
        f"{L['title']} ({L['sub']}):",
        f"{L['total']}: #p {money('zz_ef_m2')}#!{ing('zz_ef_m2_gold')}",
        f" {L['m0']}: #T {money('zz_ef_m0')}#!{ing('zz_ef_m0_gold')} ({dyn('m0')})",
        f"  -> {tt('zz_ef_ms_tt_treasury', L['tr'])}: #T {money('zz_ef_treasury')}#! ({delta('zz_ef_v_d_treasury')})",
        f" {L['m1']}: #T {money('zz_ef_m1')}#!{ing('zz_ef_m1_gold')} ({dyn('m1')})",
        f"  -> {tt('zz_ef_ms_tt_buildings', L['bld'])}: #T {money('zz_ef_building_cash')}#! ({delta('zz_ef_v_d_buildings')}; "
        f"{L['tc']} {money('zz_ef_tc_cash')}, {delta('zz_ef_v_d_tc')})",
        f" {L['m2']}: #T {money('zz_ef_m2')}#!{ing('zz_ef_m2_gold')} ({dyn('m2')})",
        f"  -> {tt('zz_ef_ms_tt_banks', L['bank'])}: #T {money('zz_ef_pool')}#! ({delta('zz_ef_v_d_pool')})",
        f" {L['m3']}: #T {money('zz_ef_m3')}#!",
        f"{L['infl']}: #T {sv('zz_ef_inflation', '+=1%')}#! (" + L['inflf'].format(
            sv('zz_ef_m3_growth_year', '+=1%'), sv('zz_ef_gdp_growth_year', '+=1%')) + ")",
        (f"Признаки пузыря: кредит {money('zz_ef_credit_total')} = {sv('zz_ef_credit_to_gdp', '%0')} ВВП (ЦБ банкам, "
         f"потребительский, бизнесу); пул — {sv('zz_ef_pool_months', '1')} мес. взносов; накопления — "
         f"{sv('zz_ef_savings_to_gdp', '%0')} ВВП") if ru else
        (f"Bubble signs: credit {money('zz_ef_credit_total')} = {sv('zz_ef_credit_to_gdp', '%0')} of GDP (CB to banks, "
         f"consumer, business); the pool — {sv('zz_ef_pool_months', '1')} months of contributions; savings — "
         f"{sv('zz_ef_savings_to_gdp', '%0')} of GDP"),
        f"{tt('zz_ef_ms_tt_pops', L['sav'])}: #T {money('zz_ef_pop_savings')}#!{ing('zz_ef_savings_gold')} "
        f"({sv('zz_ef_pop_savings_week', 'D+=')}{cur} {L['month']}) — {L['savd']} {money('zz_ef_pop_deposits')}, "
        f"{L['savc']} {money('zz_ef_pop_cash')}",
        f"{tt('zz_ef_ms_tt_cb', L['cbab'])}: {L['metal']} #T {sv('zz_ef_cb_metal')}#! {gold} "
        f"({sv('zz_ef_v_f_hume', 'D+=')} {L['month']}), {L['cover']} {sv('zz_ef_cb_cover', '%0')}",
        f"{L['debt']}: {L['princ']} {money('zz_ef_debt_principal')}, {L['dcb']} {sv('zz_ef_debt_cb_gold')} {gold}, "
        f"{L['bdebt']} {money('zz_ef_bank_cb_debt')}",
        f"{tt('zz_ef_ms_tt_fx', L['fx'])}: {L['fxcb']} {sv('money_supply_state')} ({sv('zz_ef_v_d_cb', 'D+=')} {L['fxm']}), "
        f"{L['fxab']} {sv('money_supply_stockpile_by_other_country')}",
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

# The CB and abroad are one account (EF.48 item 6): flows with abroad (Z) are
# drawn in the CB's card; ext_expr/abr_expr still tell them apart.
ACC_ORDER = ["treasury", "buildings", "banks", "pops", "cb"]
TITLES = {
    "treasury": ("Казна", "Treasury"),
    "buildings": ("Касса предприятий", "Business cash"),
    "banks": ("Средства банков", "Bank funds"),
    "pops": ("Население", "Pops"),
    "cb": ("ЦБ и заграница", "The CB and abroad"),
    "abroad": ("Заграница", "Abroad"),
    "ext": ("Вне счетов", "Outside the accounts"),
}
# The account's change over the month; pops, the CB (in money) and abroad hold
# no stock -- money passes through them.
DELTA = {"treasury": "zz_ef_v_d_treasury", "buildings": "zz_ef_v_d_buildings", "banks": "zz_ef_v_d_pool"}

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
    (K, P, "маршруты поставок", "supply routes", gv("GetPortConnectionExpenses"), None),
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
    # --- banks ---
    (P, B, "взносы в пул — инвестиции зданий и сбережения богатых (ваниль)",
     "pool contributions — buildings' investment and the rich's saving (vanilla)", sv_("zz_ef_v_f_contrib"), None),
    (B, Z, "покупка облигаций других стран частными банками (E&F)", "foreign bonds bought by private banks (E&F)",
     svp("zz_ef_v_d_bonds"), None),
    (Z, B, "погашение облигаций других стран (E&F)", "foreign bonds run off (E&F)", svn("zz_ef_v_d_bonds"), None),
    # deposits: from the savings, not from the week's income -- banks' card only (window values)
    (N, B, "вклады населения из накоплений", "pops' deposits from their savings", sv_("zz_ef_v_w_dep_in"), B),
    (B, N, "снятие вкладов", "deposits withdrawn", sv_("zz_ef_v_w_dep_out"), B),
    (B, N, "проценты по вкладам", "interest on deposits", sv_("zz_ef_v_w_dep_int"), B),
    # consumer credit (EF.48 item 4): pool <-> pops through the dependents' surcharge
    (B, N, "потребительский кредит: выдано", "consumer credit: lent", sv_("zz_ef_v_w_cc_issue"), B),
    (N, B, "потребительский кредит: погашено", "consumer credit: repaid", sv_("zz_ef_v_w_cc_repay"), B),
    (N, B, "потребительский кредит: проценты", "consumer credit: interest", sv_("zz_ef_v_w_cc_int"), B),
    # --- central bank, in money (a transit account) ---
    (X, C, "выпуск: кредит банкам — новые деньги", "issue: credit to banks — new money", sv_("zz_ef_v_f_cb_borrow"), None),
    (C, B, "кредит банкам под ключевую ставку", "credit to banks at the key rate", sv_("zz_ef_v_f_cb_borrow"), None),
    (B, C, "погашение кредита ЦБ", "repayment of the CB's credit", sv_("zz_ef_v_f_cb_repay"), None),
    (C, X, "погашено — деньги изъяты", "repaid — money withdrawn", sv_("zz_ef_v_f_cb_repay"), None),
    (B, C, "проценты по кредиту ЦБ", "interest on the CB's credit", sv_("zz_ef_v_f_cb_interest"), None),
    (C, K, "прибыль ЦБ: проценты банков", "the CB's profit: banks' interest", sv_("zz_ef_v_f_cb_interest"), None),
    # --- abroad ---
    # trade centres: their cash change is the country's payments abroad (EF.48 item 1)
    (P, Z, "торговые центры: оплата импорта — убыль их кассы", "trade centres: paying for imports — their cash fell",
     svn("zz_ef_v_d_tc"), None),
    (Z, P, "торговые центры: выручка экспорта — прирост их кассы", "trade centres: export revenue — their cash grew",
     svp("zz_ef_v_d_tc"), None),
    # the pool's unexplained change (EF.48 item 2): foreign investment from the pool
    (B, Z, "за рубеж: иностранные инвестиции и прочее (необъяснённый остаток пула)",
     "abroad: foreign investment and other (the pool's unexplained change)", svn("zz_ef_v_f_pool_other"), None),
    (Z, B, "из-за рубежа: необъяснённый приход в пул", "from abroad: the pool's unexplained gain",
     svp("zz_ef_v_f_pool_other"), None),
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
              "(строительные товары). Банки держат в пуле взносы за несколько месяцев (12 при ставке 2%, 3 при 12%): "
              "ниже — занимают у ЦБ под ключевую ставку, выше — гасят долг.",
              "The investment pool. Private construction goes through the treasury: pool → treasury (transfer) → "
              "businesses (construction goods). Banks keep several months of contributions in the pool (12 at 2%, 3 "
              "at 12%): below it they borrow from the CB at the key rate, above it they repay."),
    "pops": ("Денег у населения в движке нет: остаток дохода движок превращает в достаток (число). Мод ловит "
             "эти деньги в накопления — по сохранению денег (мост GUI → скрипт): что пропало из казны и касс "
             "предприятий сверх известных переводов. Оплата заграницы (касса торговых центров) и необъяснённый "
             "остаток пула сюда не входят — это переводы за рубеж. Часть накоплений лежит во вкладах — это снова "
             "деньги движка (пул).",
             "Pops hold no money in the engine: it turns the income left over into wealth (a number). The mod "
             "catches this money into savings by money conservation (the GUI → script bridge): what vanished from "
             "the treasury and business cash beyond the known transfers. Payments abroad (the trade centres' cash) "
             "and the pool's unexplained change are not in it — they are transfers abroad. Part of the savings is "
             "in deposits — engine money again (the pool)."),
    "cb": ("ЦБ — расчётный агент страны: все платежи с заграницей идут через него. Кредит банкам — новые деньги, "
           "погашение их изымает, проценты уходят в казну. Запас счёта — резервы металла (и склад товара-валюты "
           "E&F в штуках): чистый отток за рубеж по курсу списывает металл, приток — добавляет (механизм Юма, "
           "только металлический стандарт с ЦБ). Металл и деньги убывают в одной доле, поэтому отток сам по себе "
           "курс не двигает; торговый баланс E&F в резервы больше не входит.",
           "The CB is the country's settlement agent: every payment with abroad goes through it. Credit to banks is "
           "new money, repayment withdraws it, interest goes to the treasury. The account's stock is the metal "
           "reserves (and E&F's currency-good stock, in counts): a net outflow abroad pays out metal at the "
           "currency's value, an inflow brings it in (Hume's mechanism, metal standards with a CB only). Metal and "
           "money fall by the same fraction, so an outflow alone does not move the value; E&F's trade balance is no "
           "longer in the reserves."),
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
    return C if a == Z else a


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
					on_finish = "[GetScriptedGui('zz_ef_money_hook_sg').Execute( GuiScope.SetRoot( Country.MakeScope ).AddScope( 'ext', MakeScopeValue( {ext} ) ).AddScope( 'abr', MakeScopeValue( {abr} ) ).End )]"
				}}
			}}
		}}
	}}
}}
"""


def write_hook():
    g = os.path.join(HOTFIX, "gui", "zz_ef_money_hook.gui")
    with open(g, "w", encoding="utf-8", newline="\n") as f:
        f.write(HOOK_GUI.format(ext=ext_expr(), abr=abr_expr()))
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
        fixed_resid = "Country.MakeScope.ScriptValue('zz_ef_other_treasury_budget')" if acc == K else None
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
                if dr == "in":
                    L.append(f"  ← #P +[{e}|D] {cur}#! {lab}")
                    if resid:
                        resid = f"Subtract_CFixedPoint({resid}, {e})"
                else:
                    L.append(f"  → #N −[{e}|D] {cur}#! {lab}")
                    if resid:
                        resid = f"Subtract_CFixedPoint({resid}, Negate_CFixedPoint({e}))"
            if other == X and resid:
                L.append(f"  ↔ [{fixed_resid or resid}|D+=] {cur} {other_lab}")
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
            L.append((f"Долг банков перед ЦБ {money('zz_ef_bank_cb_debt')}; цель пула {money('zz_ef_pool_target')} = "
                      f"взносы за месяц × {sv('zz_ef_credit_months', '1')} мес. при ставке {sv('zz_ef_money_rate', '%1')}; "
                      f"занимают и гасят 1.15% разрыва в неделю (~5% в месяц). Вклады идут к цели на 5% разрыва в неделю.")
                     if ru else
                     (f"Banks' debt to the CB {money('zz_ef_bank_cb_debt')}; pool target {money('zz_ef_pool_target')} = "
                      f"a month's contributions × {sv('zz_ef_credit_months', '1')} months at a rate of "
                      f"{sv('zz_ef_money_rate', '%1')}; they borrow and repay 1.15% of the gap a week (~5% a month). Deposits move 5% of their gap a week."))
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
            L.append((f"#b Кредит бизнесу (учёт): долг предприятий {money('zz_ef_bc_debt')}#! "
                      f"({sv('zz_ef_bc_debt_to_gdp', '%1')} ВВП). Частная стройка за неделю оплачена заёмными "
                      f"деньгами банков на {sv('zz_ef_bc_borrowed_share', '%0')} (кредит ЦБ и вклады к пулу): новый "
                      f"долг {money('zz_ef_v_f_bc_new')}; проценты {money('zz_ef_v_f_bc_int')} (ключевая + 3 п.п.), "
                      f"срок 5 лет; из взносов зданий в счёт долга {money('zz_ef_v_f_bc_paid')} "
                      f"({sv('zz_ef_bc_service_share', '%0')} взносов). Деньги не двигаются — только учёт.")
                     if ru else
                     (f"#b Business credit (accounting): businesses' debt {money('zz_ef_bc_debt')}#! "
                      f"({sv('zz_ef_bc_debt_to_gdp', '%1')} of GDP). This week's private construction was paid with "
                      f"the banks' borrowed money for {sv('zz_ef_bc_borrowed_share', '%0')} (CB credit and deposits "
                      f"to the pool): new debt {money('zz_ef_v_f_bc_new')}; interest {money('zz_ef_v_f_bc_int')} (key "
                      f"+ 3 pp), term 5 years; counted from the buildings' contributions {money('zz_ef_v_f_bc_paid')} "
                      f"({sv('zz_ef_bc_service_share', '%0')} of them). No money moves — accounting only."))
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
                      f"За неделю: выпало из денег движка {sv('zz_ef_v_f_inflow', 'D+=')}{cur}, проценты по вкладам "
                      f"{sv('zz_ef_v_f_dep_int', 'D+=')}{cur}; внесено {money('zz_ef_v_f_dep_in')}, снято "
                      f"{money('zz_ef_v_f_dep_out')}. Доля во вкладах — цель {sv('zz_ef_deposit_share', '%0')} "
                      f"(по ставке), ставка по вкладам {sv('zz_ef_deposit_rate', '%1')}.")
                     if ru else
                     (f"#b Savings: {money('zz_ef_pop_savings')}#! ({sv('zz_ef_pop_savings_week', 'D+=')}{cur} this "
                      f"week) — in deposits {money('zz_ef_pop_deposits')}, at hand {money('zz_ef_pop_cash')}. This "
                      f"week: dropped out of the engine's money {sv('zz_ef_v_f_inflow', 'D+=')}{cur}, deposit "
                      f"interest {sv('zz_ef_v_f_dep_int', 'D+=')}{cur}; deposited {money('zz_ef_v_f_dep_in')}, "
                      f"withdrawn {money('zz_ef_v_f_dep_out')}. Deposit share target "
                      f"{sv('zz_ef_deposit_share', '%0')} (by the rate), deposit rate {sv('zz_ef_deposit_rate', '%1')}."))
        d[f"zz_ef_ms_tt_{acc}"] = "\\n".join(L)
    d["zz_ef_ms_tt_fx"] = fx_card(lang)
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


def main():
    for lang in LANGS:
        d = build(lang)
        head = (f"l_{lang}:\n\n # GENERATED by tools/regen_ef_money_supply_loc.py -- do not edit by hand.\n"
                " # EF.39/EF.44/EF.48: E&F's Money Supply tooltip as M0/M1/M2, a card per account.\n")
        if lang not in ("english", "russian"):
            head += " # Not translated yet: English text.\n"
        lines = [head, "\n"]
        for key, v in d.items():
            assert '"' not in v, key
            lines.append(f' {key}:0 "{v}"\n')
        path = os.path.join(ROOT, lang, "replace", f"zz_ef_money_supply_replace_l_{lang}.yml")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path + ".tmp", "w", encoding="utf-8-sig", newline="\n") as f:
            f.write("".join(lines))
        os.replace(path + ".tmp", path)
    write_hook()
    print("ok", len(d), "keys x", len(LANGS), "+ hook gui")


if __name__ == "__main__":
    main()
