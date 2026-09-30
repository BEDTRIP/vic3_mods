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

EF.48 (2026-09-30, evening revision): everything in the ENGINE'S money.
Money = treasury (M0) + businesses' cash (M1) + the pool (M2) -- exact engine
numbers. Pops, the central bank (in money) and abroad hold no stock: money
passes through them (pops' income goes to taxes and purchases, the rest
becomes wealth, i.e. leaves the money). E&F's central-bank "reserves" and
currency-good flows are counts of a good, shown in a separate card. Each
transfer is ONE entry (FLOWS: from, to, label, value) and shows in both cards
with opposite signs. Values come from the budget through GUI data functions
(GetTrendValue(Country.Get...Trend), week x 4.333) -- exact per budget line,
costing nothing unless the tooltip is open -- and from the model's script
values (monthly step). "Other" = the account's change minus everything listed,
computed in the GUI; pops close with "purchases and wealth growth".

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
        L = dict(title="Денежная масса", sub="деньги движка", total="Всего (M2)", month="за месяц",
                 m0="M0 — деньги государства", tr="Казна", m1="M1 = M0 + деньги предприятий",
                 bld="Касса предприятий", m2="M2 = M1 + деньги банков", bank="Средства банков",
                 nostock="Счета без запаса (деньги проходят насквозь)", pops="Население", cb="Центральный банк",
                 abroad="Заграница", debt="Долг (не деньги)", princ="бюджета", dcb="перед ЦБ (E&F)",
                 bdebt="банков перед ЦБ", fx="Товар-валюта E&F (штуки, не деньги)", fxcb="склад ЦБ",
                 fxab="у других стран", hint="Наведите на счёт — все переводы за месяц.")
    else:
        L = dict(title="Money Supply", sub="the engine's money", total="Total (M2)", month="this month",
                 m0="M0 — state money", tr="Treasury", m1="M1 = M0 + business money", bld="Business cash",
                 m2="M2 = M1 + bank money", bank="Bank funds", nostock="Accounts without a stock (money passes through)",
                 pops="Pops", cb="Central bank", abroad="Abroad", debt="Debt (not money)", princ="budget",
                 dcb="to the CB (E&F)", bdebt="banks to the CB", fx="E&F currency good (counts, not money)",
                 fxcb="CB stock", fxab="held by other countries", hint="Hover an account for all its transfers this month.")
    lines = [
        f"{L['title']} ({L['sub']}):",
        f"{L['total']}: #p {money('money_supply')}#! ({delta('zz_ef_v_d_m2')} {L['month']})",
        f" {L['m0']}: #T {money('zz_ef_m0')}#!",
        f"  -> {tt('zz_ef_ms_tt_treasury', L['tr'])}: #T {money('zz_ef_treasury')}#! ({delta('zz_ef_v_d_treasury')})",
        f" {L['m1']}: #T {money('zz_ef_m1')}#!",
        f"  -> {tt('zz_ef_ms_tt_buildings', L['bld'])}: #T {money('zz_ef_building_cash')}#! ({delta('zz_ef_v_d_buildings')})",
        f" {L['m2']}: #T {money('money_supply')}#!",
        f"  -> {tt('zz_ef_ms_tt_banks', L['bank'])}: #T {money('zz_ef_pool')}#! ({delta('zz_ef_v_d_pool')})",
        f" {L['nostock']}: {tt('zz_ef_ms_tt_pops', L['pops'])}, {tt('zz_ef_ms_tt_cb', L['cb'])}, "
        f"{tt('zz_ef_ms_tt_abroad', L['abroad'])}",
        f"{L['debt']}: {L['princ']} {money('zz_ef_debt_principal')}, {L['dcb']} {sv('zz_ef_debt_cb_gold')} {gold}, "
        f"{L['bdebt']} {money('zz_ef_bank_cb_debt')}",
        f"{tt('zz_ef_ms_tt_fx', L['fx'])}: {L['fxcb']} {sv('money_supply_state')} ({sv('zz_ef_v_d_cb', 'D+=')}), "
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
    lines.append(", ".join(f"{r[1] if ru else r[2]} {sv('zz_ef_raw_' + r[0])}" for r in raw)
                 + (f"; ВВП в год {sv('zz_ef_raw_gdp')}" if ru else f"; GDP per year {sv('zz_ef_raw_gdp')}"))
    return "\\n".join(lines) + "\\n$TOOLTIP_DELIMITER$"


# ---------------------------------------------------------------------------
# Accounts and flows, all in the engine's money.
# ---------------------------------------------------------------------------

ACC_ORDER = ["treasury", "buildings", "banks", "pops", "cb", "abroad"]
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
    # the pool's transfer to the budget for construction; GetInvestmentFundTrend is the pool's STOCK
    (B, K, "[concept_budget_investment_income]: на стройку", "[concept_budget_investment_income]: for construction",
     gt("GetInvestmentIncomeTrend"), None),
    (X, K, "[concept_budget_minting] — новые деньги движка", "[concept_budget_minting] — new engine money",
     gt("GetMintingTrend"), None),
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
    # --- pops: a transit account ---
    (P, N, "зарплаты и дивиденды (оценка: ВВП / 12 − госвыплаты)", "wages and dividends (estimate: GDP / 12 − state pay)",
     ("expr", "WAGES"), None),
    (N, P, "покупки товаров и прирост достатка — остаток дохода",
     "purchases of goods and wealth growth — the rest of the income", ("closing",), None),
    # --- banks ---
    (P, B, "взносы в пул — инвестиции зданий и сбережения богатых (ваниль)",
     "pool contributions — buildings' investment and the rich's saving (vanilla)", sv_("zz_ef_v_f_contrib"), None),
    (B, Z, "покупка облигаций других стран частными банками (E&F)", "foreign bonds bought by private banks (E&F)",
     svp("zz_ef_v_d_bonds"), None),
    (Z, B, "погашение облигаций других стран (E&F)", "foreign bonds run off (E&F)", svn("zz_ef_v_d_bonds"), None),
    # --- central bank, in money (a transit account) ---
    (X, C, "выпуск: кредит банкам — новые деньги", "issue: credit to banks — new money", sv_("zz_ef_v_f_cb_borrow"), None),
    (C, B, "кредит банкам под ключевую ставку", "credit to banks at the key rate", sv_("zz_ef_v_f_cb_borrow"), None),
    (B, C, "погашение кредита ЦБ", "repayment of the CB's credit", sv_("zz_ef_v_f_cb_repay"), None),
    (C, X, "погашено — деньги изъяты", "repaid — money withdrawn", sv_("zz_ef_v_f_cb_repay"), None),
    (B, C, "проценты по кредиту ЦБ", "interest on the CB's credit", sv_("zz_ef_v_f_cb_interest"), None),
    (C, K, "прибыль ЦБ: проценты банков", "the CB's profit: banks' interest", sv_("zz_ef_v_f_cb_interest"), None),
    # --- abroad ---
    (Z, P, "торговля: экспорт сверх импорта (E&F)", "trade: exports over imports (E&F)", svp("zz_ef_trade_month"), None),
    (P, Z, "торговля: импорт сверх экспорта (E&F)", "trade: imports over exports (E&F)", svn("zz_ef_trade_month"), None),
]

NOTES = {
    "treasury": ("Статьи бюджета — точно, неделя × 4.33; изменение казны — за месяц.",
                 "Budget lines are exact, week × 4.33; the treasury's change is over the month."),
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
    "pops": ("Денег у населения в движке нет: доход уходит на налоги и покупки, остаток становится достатком "
             "(числом, а не деньгами) — поэтому движок деньги не сохраняет.",
             "Pops hold no money in the engine: income goes to taxes and purchases, the rest becomes wealth (a "
             "number, not money) — that is why the engine does not conserve money."),
    "cb": ("В деньгах движка у ЦБ запаса нет: кредит банкам — новые деньги, погашение их изымает, проценты уходят "
           "в казну. Склад товара-валюты E&F — отдельно, в штуках.",
           "In the engine's money the CB holds no stock: credit to banks is new money, repayment withdraws it, "
           "interest goes to the treasury. E&F's currency-good stock is separate, in counts."),
    "abroad": ("Запаса у счёта нет — только переводы.", "The account holds no stock — only transfers."),
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
    if kind in ("sv", "svp"):
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
    EXPRS["closing"] = closing_expr()
    ru = lang == "russian"
    k = 0 if ru else 1
    none = "  нет переводов" if ru else "  no transfers"
    other_lab = "прочее" if ru else "other"
    d = {}
    for acc in ACC_ORDER:
        flows = card_flows(acc)
        head = TITLES[acc][k] + (" за месяц" if ru else " this month")
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
                bin_, bout = ("Country.MakeScope.ScriptValue('zz_ef_total_income_month')",
                              "Country.MakeScope.ScriptValue('zz_ef_total_expenses_month')")
                for o, dr, f in flows:
                    if f[4][0] in ("gt", "gv"):
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
                      f"взносы за месяц × {sv('zz_ef_credit_months', '1')} мес. при ставке {sv('zz_ef_money_rate', '%1')}.")
                     if ru else
                     (f"Banks' debt to the CB {money('zz_ef_bank_cb_debt')}; pool target {money('zz_ef_pool_target')} = "
                      f"a month's contributions × {sv('zz_ef_credit_months', '1')} months at a rate of "
                      f"{sv('zz_ef_money_rate', '%1')}."))
        if acc == N:
            L.append((f"Доход населения ≈ ВВП / 12 = {money('zz_ef_gdp_month')}.") if ru else
                     (f"Pops' income ≈ GDP / 12 = {money('zz_ef_gdp_month')}."))
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
    print("ok", len(d), "keys x", len(LANGS))


if __name__ == "__main__":
    main()
