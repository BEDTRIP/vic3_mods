#!/usr/bin/env python3
"""
EF.39 / EF.44 / EF.48 -- the "Money Supply" tooltip as M0 / M1 / M2, with a
card per account: every transfer of the month from and to each other account.

E&F's tooltip is 12 localization keys MONEY_SUPPLY_DESC_* (one per monetary
standard, AI and player variants), all the same text except the data context
(Country / GetPlayer). The hotfix changed the composition of the money supply
(script_values/zz_ef_money_model_values.txt), so the text is rewritten. Each
account line is a nested tooltip (#tooltippable;tooltip:[X.GetTooltipTag],key
...#!) with the account's card; the nested keys read Country.* (the tag passes
the country).

EF.48 (2026-09-30): six accounts -- pops' savings, treasury, businesses,
banks, central bank, abroad -- and "outside the accounts" (new money, the
unseen). Each transfer is ONE entry (FLOWS: from, to, label, value) and shows
in both cards with opposite signs. Values come from
  - the budget through GUI data functions (GetTrendValue(Country.Get...Trend),
    weekly x 4.333 = a month): exact per budget line, costs nothing unless the
    tooltip is open;
  - the model's script values (monthly step).
"Other" of a card = the account's change over the month minus everything
listed, computed in the GUI, so the lines always add up to the change.
Steps 2-3 (2026-09-30): pops' savings from flows -- the savings card shows
the budget's taxes and state pay exactly, wages and dividends as GDP / 12 minus
state pay, deposits, pool contributions, deposit interest, and purchases as
its closing line (the rest of the pops' income, so the card adds up); bank
credit is borrowed from the central bank (borrowing, repayment, interest, the
CB's profit to the treasury).

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

WEEKS = "'(CFixedPoint)4.333'"
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
        L = dict(title="Денежная масса", total="Всего", own="В собственности страны (M2)", month="за месяц",
                 m0="M0 — наличные и деньги государства", cb="Резервы центрального банка", tr="Казна",
                 sav="Сбережения населения", m1="M1 = M0 + касса предприятий", bld="Касса предприятий",
                 m2="M2 = M1 + средства банков", bank="Средства банков", dep="вклады", cred="кредит банков",
                 mult="к вкладам, цель", mm="Денежный мультипликатор M2 / M0", other="Заграница",
                 other2="валюта у других стран", debt="Госдолг (не деньги)", princ="долг бюджета",
                 dcb="перед центральным банком", bdebt="долг банков перед ЦБ",
                 hint="Наведите на счёт — все переводы за месяц.")
    else:
        L = dict(title="Money Supply", total="Total", own="Owned in the country (M2)", month="this month",
                 m0="M0 — cash and state money", cb="Central bank reserves", tr="Treasury",
                 sav="Pop savings", m1="M1 = M0 + business cash", bld="Business cash",
                 m2="M2 = M1 + bank funds", bank="Bank funds", dep="deposits", cred="bank credit",
                 mult="of deposits, target", mm="Money multiplier M2 / M0", other="Abroad",
                 other2="currency held by other countries", debt="Government debt (not money)",
                 princ="budget debt", dcb="to the central bank", bdebt="banks' debt to the CB",
                 hint="Hover an account for all its transfers this month.")
    lines = [
        f"{L['title']}:",
        f"{L['total']} #v {L['title']}#!: #p {sv('total_money_supply')}#! {cur}",
        f" - {L['own']}: #T {money('money_supply')}#! ({delta('zz_ef_v_d_m2')} {L['month']})",
        f"   {L['m0']}: #T {money('zz_ef_m0')}#!",
        f"    -> {tt('zz_ef_ms_tt_cb', L['cb'])}: #T {money('money_supply_state')}#! ({delta('zz_ef_v_d_cb')})",
        f"    -> {tt('zz_ef_ms_tt_treasury', L['tr'])}: #T {money('zz_ef_treasury')}#! ({delta('zz_ef_v_d_treasury')})",
        f"    -> {tt('zz_ef_ms_tt_savings', L['sav'])}: #T {money('zz_ef_savings')}#! ({delta('zz_ef_v_d_savings')})",
        f"   {L['m1']}: #T {money('zz_ef_m1')}#!",
        f"    -> {tt('zz_ef_ms_tt_buildings', L['bld'])}: #T {money('zz_ef_building_cash')}#! ({delta('zz_ef_v_d_buildings')})",
        f"   {L['m2']}: #T {money('money_supply')}#!",
        f"    -> {tt('zz_ef_ms_tt_banks', L['bank'])}: #T {money('zz_ef_pool')}#! ({delta('zz_ef_v_d_pool')})",
        f"       {L['dep']} {money('zz_ef_deposits')}, {L['cred']} {money('zz_ef_bank_credit')}: "
        f"×{sv('zz_ef_pool_to_deposits', '2')} {L['mult']} ×{sv('zz_ef_credit_multiplier', '2')}",
        f"   {L['mm']}: ×{sv('zz_ef_m2_to_m0', '2')}",
        f" - {tt('zz_ef_ms_tt_abroad', L['other'])}: {L['other2']} #T {money('money_supply_stockpile_by_other_country')}#!",
        f"{L['debt']}: {L['princ']} {money('zz_ef_debt_principal')}, {L['dcb']} {sv('zz_ef_debt_cb_gold')} {gold}; "
        f"{L['bdebt']} {money('zz_ef_bank_cb_debt')}",
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
    lines.append(", ".join(f"{r[1] if ru else r[2]} {sv('zz_ef_raw_' + r[0])}" for r in raw)
                 + (f"; ВВП в год {sv('zz_ef_raw_gdp')}" if ru else f"; GDP per year {sv('zz_ef_raw_gdp')}"))
    return "\\n".join(lines) + "\\n$TOOLTIP_DELIMITER$"


# ---------------------------------------------------------------------------
# Accounts and flows.
# ---------------------------------------------------------------------------

ACC_ORDER = ["savings", "treasury", "buildings", "banks", "cb", "abroad"]
TITLES = {
    "savings": ("Сбережения населения", "Pop savings"),
    "treasury": ("Казна", "Treasury"),
    "buildings": ("Касса предприятий", "Business cash"),
    "banks": ("Средства банков", "Bank funds"),
    "cb": ("Резервы центрального банка", "Central bank reserves"),
    "abroad": ("Заграница", "Abroad"),
    "ext": ("Вне счетов", "Outside the accounts"),
}
# The account's change over the month (script value); abroad holds no stock.
DELTA = {"savings": "zz_ef_v_d_savings", "treasury": "zz_ef_v_d_treasury", "buildings": "zz_ef_v_d_buildings",
         "banks": "zz_ef_v_d_pool", "cb": "zz_ef_v_d_cb"}

N, K, P, B, C, Z, X = "savings", "treasury", "buildings", "banks", "cb", "abroad", "ext"


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
    # --- budget, exact (GUI), week x 4.333 ---
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
    (C, K, "[concept_budget_minting]", "[concept_budget_minting]", gt("GetMintingTrend"), None),
    (X, C, "выпуск для казны: чеканка", "issued for the treasury: minting", gt("GetMintingTrend"), None),
    # the pool's transfer to the budget for construction ("investment pool
    # transfer"); GetInvestmentFundTrend is the pool's STOCK, not a flow
    # (2026-09-30: it showed 335M = 77.3M x 4.333)
    (B, K, "[concept_budget_investment_income]: на стройку", "[concept_budget_investment_income]: for construction",
     gt("GetInvestmentIncomeTrend"), None),
    (K, X, "[concept_budget_interest] — держателям долга", "[concept_budget_interest] — to the debt holders",
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
    # --- model, monthly step ---
    (P, N, "зарплаты и дивиденды (оценка: ВВП / 12 − госвыплаты)", "wages and dividends (estimate: GDP / 12 − state pay)",
     ("expr", "WAGES"), None),
    (N, P, "покупки товаров — остаток дохода", "purchases of goods — the rest of the income", ("closing",), None),
    (N, B, "вклады", "deposits", svp("zz_ef_v_f_deposits"), None),
    (B, N, "изъятия вкладов", "deposit withdrawals", svn("zz_ef_v_f_deposits"), None),
    (N, B, "взносы в пул — сбережения богатых (ваниль)", "pool contributions — the rich's saving (vanilla)",
     sv_("zz_ef_v_f_contrib"), None),
    (B, N, "проценты по вкладам", "interest on deposits", sv_("zz_ef_v_f_dep_interest"), None),
    (C, P, "в обращение: спрос на товар-валюту — здания и население страны (E&F)",
     "into circulation: demand for the currency good — the country's buildings and pops (E&F)",
     sv_("zz_ef_cb_demand_own"), None),
    (C, Z, "в обращение: другим странам рынка (E&F)", "into circulation: other countries of the market (E&F)",
     sv_("zz_ef_cb_demand_others"), None),
    (X, C, "выпуск: продажи товара-валюты на рынке (E&F)", "issue: sales of the currency good (E&F)",
     sv_("zz_ef_cb_issue_month"), None),
    (X, C, "девальвация (E&F)", "devaluation (E&F)", sv_("zz_ef_cb_devaluation_month"), None),
    (C, X, "ревальвация (E&F)", "revaluation (E&F)", sv_("zz_ef_cb_revaluation_month"), None),
    (X, C, "выпуск: кредит банкам", "issue: credit to banks", sv_("zz_ef_v_f_cb_borrow"), None),
    (C, B, "кредит банкам под ключевую ставку", "credit to banks at the key rate", sv_("zz_ef_v_f_cb_borrow"), None),
    (B, C, "погашение кредита ЦБ", "repayment of the CB's credit", sv_("zz_ef_v_f_cb_repay"), None),
    (C, X, "погашено — изъято из обращения", "repaid — withdrawn from circulation", sv_("zz_ef_v_f_cb_repay"), None),
    (B, C, "проценты по кредиту ЦБ", "interest on the CB's credit", sv_("zz_ef_v_f_cb_interest"), None),
    (C, K, "прибыль ЦБ: проценты банков", "the CB's profit: banks' interest", sv_("zz_ef_v_f_cb_interest"), None),
    (Z, P, "торговля: экспорт сверх импорта (E&F)", "trade: exports over imports (E&F)", svp("zz_ef_trade_month"), None),
    (P, Z, "торговля: импорт сверх экспорта (E&F)", "trade: imports over exports (E&F)", svn("zz_ef_trade_month"), None),
]

NOTES = {
    "savings": ("Наличные у населения — модель: денег у групп населения в движке нет. Население держит на руках "
                "4 месяца дохода (кембриджская доля денег) и каждый месяц сдвигается к этому запасу на 5%; всё "
                "остальное от дохода уходит в покупки.",
                "Cash held by pops — a model: pops hold no money in the engine. Pops keep 4 months of income in hand "
                "(the Cambridge k) and move 5% of the way there each month; the rest of the income goes to purchases."),
    "treasury": ("Статьи бюджета — точно, неделя × 4.33; изменение казны — за месяц. Государство держит деньги "
                 "вне обращения — часть M0.",
                 "Budget lines are exact, week × 4.33; the treasury's change is over the month. State money, out of "
                 "circulation — part of M0."),
    "buildings": ("Денежные резервы зданий: кредитный лимит − база − доля ВВП (COUNTRY_MIN_CREDIT_*). Зарплаты и "
                  "дивиденды населению скрипту не видны — они в «прочем».",
                  "Buildings' cash reserves: credit limit − base − GDP share (COUNTRY_MIN_CREDIT_*). Wages and "
                  "dividends to pops are not visible to scripts — they are in other."),
    "banks": ("Частная стройка идёт через казну: пул → казна (трансфер) → предприятия (строительные товары). "
              "Банки держат средства около вкладов × множитель (×3 при 2%, ×1.2 при 12%): ниже — занимают у ЦБ под "
              "ключевую ставку, выше — гасят долг. По вкладам платят ключевую − 1.5 п.п. (не меньше 0.5%).",
              "Private construction goes through the treasury: pool → treasury (transfer) → businesses "
              "(construction goods). Banks keep their funds near deposits × multiplier (×3 at 2%, ×1.2 at 12%): "
              "below it they borrow from the CB at the key rate, above it they repay. Deposits earn the key rate − "
              "1.5 pp (at least 0.5%)."),
    "cb": ("Валюта, которую держит центральный банк, вне обращения. Выпуск и спрос — рынок товара-валюты (E&F, у "
           "хозяина рынка); чеканку и кредит банкам ЦБ выпускает, погашенный кредит изымает; проценты банков — "
           "прибыль ЦБ, уходит в казну.",
           "Currency held by the central bank, out of circulation. Issue and demand: the currency good's market "
           "(E&F, market owner); the CB issues minting and credit to banks, withdraws repaid credit; banks' "
           "interest is the CB's profit, remitted to the treasury."),
    "abroad": ("Запаса у счёта нет — только переводы. Проценты иностранным держателям госдолга — шаг 3.",
               "The account holds no stock — only transfers. Interest to foreign holders of government debt: step 3."),
}


STATE_PAY = ["GetGovernmentWagesExpenseTrend", "GetMilitaryWagesExpenseTrend", "GetWelfarePaymentsTrend"]
EXPRS = {}


def wages_expr():
    e = "Country.MakeScope.ScriptValue('zz_ef_gdp_month')"
    for fn in STATE_PAY:
        e = f"Subtract_CFixedPoint({e}, Abs_CFixedPoint(Multiply_CFixedPoint(GetTrendValue(Country.{fn}), {WEEKS})))"
    return f"Max_CFixedPoint({e}, {ZERO})"


def expr(v):
    """GUI expression (CFixedPoint, non-negative, a month) for a flow value."""
    if v[0] == "expr":
        return wages_expr()
    if v[0] == "closing":
        return EXPRS["closing"]
    kind, name = v
    if kind == "gt":
        return f"Abs_CFixedPoint(Multiply_CFixedPoint(GetTrendValue(Country.{name}), {WEEKS}))"
    if kind == "gv":
        return f"Abs_CFixedPoint(Multiply_CFixedPoint(Country.{name}, {WEEKS}))"
    s = f"Country.MakeScope.ScriptValue('{name}')"
    if kind == "sv":
        return f"Max_CFixedPoint({s}, {ZERO})"
    if kind == "svp":
        return f"Max_CFixedPoint({s}, {ZERO})"
    return f"Max_CFixedPoint(Negate_CFixedPoint({s}), {ZERO})"


def card_flows(acc):
    """Flows shown in acc's card, as (other, dir, flow)."""
    out = []
    for f in FLOWS:
        frm, to, _, _, _, only = f
        if only and only != acc:
            continue
        if to == acc:
            out.append((frm, "in", f))
        elif frm == acc:
            out.append((to, "out", f))
    return out


def closing_expr():
    """Pops' purchases: all other flows of the savings card minus its change."""
    e = f"Country.MakeScope.ScriptValue('{DELTA[N]}')"
    ins, outs = [], []
    for other, dr, f in card_flows(N):
        if f[4][0] == "closing":
            continue
        (ins if dr == "in" else outs).append(expr(f[4]))
    # purchases = in - out - change
    acc = ins[0]
    for x in ins[1:]:
        acc = f"Subtract_CFixedPoint({acc}, Negate_CFixedPoint({x}))"
    for x in outs:
        acc = f"Subtract_CFixedPoint({acc}, {x})"
    return f"Subtract_CFixedPoint({acc}, {e})"


def nested(lang):
    cur, sv, money, delta, tt = ctx("Country")
    EXPRS["closing"] = closing_expr()
    ru = lang == "russian"
    k = 0 if ru else 1
    none = "  нет переводов" if ru else "  no transfers"
    other_lab = "прочее — не видно скрипту" if ru else "other — not visible to scripts"
    d = {}
    for acc in ACC_ORDER:
        flows = card_flows(acc)
        head = TITLES[acc][k] + (" за месяц" if ru else " this month")
        L = [f"#b {head}: {delta(DELTA[acc])}#!" if acc in DELTA else f"#b {head}#!"]
        # residual: change - in + out
        resid = f"Country.MakeScope.ScriptValue('{DELTA[acc]}')" if acc in DELTA and acc != N else None
        # the treasury lists the whole budget: its other is budget-free (script)
        fixed_resid = "Country.MakeScope.ScriptValue('zz_ef_other_treasury_budget')" if acc == K else None
        n = 0
        for other in [a for a in ACC_ORDER if a != acc] + [X]:
            n += 1
            L.append(f"{n} {TITLES[other][k]}")
            rows = [(dr, f) for o, dr, f in flows if o == other]
            if not rows and not (other == X and resid):
                L.append(none)
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
                bin_, bout = "Country.MakeScope.ScriptValue('zz_ef_total_income_month')",                     "Country.MakeScope.ScriptValue('zz_ef_total_expenses_month')"
                for o, dr, f in flows:
                    if f[4][0] in ("gt", "gv"):
                        if dr == "in":
                            bin_ = f"Subtract_CFixedPoint({bin_}, {expr(f[4])})"
                        else:
                            bout = f"Subtract_CFixedPoint({bout}, {expr(f[4])})"
                L.append(("  проверка: доходы бюджета вне строк " if ru else "  check: budget income not in any line ")
                         + f"[{bin_}|D+=] {cur}" + (", расходы вне строк " if ru else ", expenses not in any line ")
                         + f"[{bout}|D+=] {cur}")
        L += ["", NOTES[acc][k]]
        if acc == "savings":
            L.append((f"Доход населения ≈ ВВП / 12 = {money('zz_ef_gdp_month')}; целевой запас на руках "
                      f"{money('zz_ef_cash_target')}, сдвиг к нему за месяц {delta('zz_ef_v_f_cash')}.") if ru else
                     (f"Pops' income ≈ GDP / 12 = {money('zz_ef_gdp_month')}; target cash in hand "
                      f"{money('zz_ef_cash_target')}, this month's move to it {delta('zz_ef_v_f_cash')}."))
        if acc == "banks":
            L.append((f"Долг банков перед ЦБ {money('zz_ef_bank_cb_debt')}, ставка по вкладам "
                      f"{sv('zz_ef_deposit_rate', '%1')}.") if ru else
                     (f"Banks' debt to the CB {money('zz_ef_bank_cb_debt')}, deposit rate "
                      f"{sv('zz_ef_deposit_rate', '%1')}."))
            L.append((f"Вклады {money('zz_ef_deposits')}, кредит банков {money('zz_ef_bank_credit')}: сейчас "
                      f"×{sv('zz_ef_pool_to_deposits', '2')}, цель ×{sv('zz_ef_credit_multiplier', '2')} при ставке "
                      f"{sv('zz_ef_money_rate', '%1')}.") if ru else
                     (f"Deposits {money('zz_ef_deposits')}, bank credit {money('zz_ef_bank_credit')}: now "
                      f"×{sv('zz_ef_pool_to_deposits', '2')}, target ×{sv('zz_ef_credit_multiplier', '2')} at a rate "
                      f"of {sv('zz_ef_money_rate', '%1')}."))
        if acc == "abroad":
            L.append((f"Валюта страны у других стран: {money('money_supply_stockpile_by_other_country')}.") if ru else
                     (f"The country's currency held by other countries: {money('money_supply_stockpile_by_other_country')}."))
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
    print("ok", len(d), "keys x", len(LANGS))


if __name__ == "__main__":
    main()
