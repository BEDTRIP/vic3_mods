#!/usr/bin/env python3
"""
EF.39 / EF.44 -- the "Money Supply" tooltip as M0 / M1 / M2, with a card per
account: hover an account for every transfer of the last month, from and to
each of the other accounts.

E&F's tooltip is 12 localization keys MONEY_SUPPLY_DESC_* (one per monetary
standard, AI and player variants), all the same text except the data context
(Country / GetPlayer). They listed E&F's five counters; the hotfix changed the
composition (script_values/zz_ef_money_model_values.txt: treasury in, the
government_loan counter out, building cash from the credit limit), so the text
is rewritten. Each account line is a nested tooltip
(#tooltippable;tooltip:[X.GetTooltipTag],key ...#!) with the account's card;
the nested keys read the country through Country.* (the tag passes it).

Card (user's layout, 2026-09-30): the change over the month, then one block
per other account and one "outside the accounts", each transfer on its own
signed line: "← +in  what" / "→ −out  what". Amounts are from the last monthly
step, so all lines add up to the change ("other" closes the gap).
The main tooltip ends with a reconciliation block: the engine's raw weekly
budget numbers, to be compared with the Money panel before the flows are
rebuilt (decided 2026-09-30: savings from flows, a sixth account "abroad").

Writes
  _ef/ef hotfix 1.13/localization/<lang>/replace/zz_ef_money_supply_replace_l_<lang>.yml
    (UTF-8 with BOM; RU and EN written, the other 9 languages get EN);
  _ef/ef hotfix 1.13/common/script_values/zz_ef_money_ledger_values.txt
    (one script value per card line).

Usage:
    py tools/regen_ef_money_supply_loc.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
HOTFIX = os.path.normpath(os.path.join(HERE, r"..\_ef\ef hotfix 1.13"))
ROOT = os.path.join(HOTFIX, "localization")
VALUES_OUT = os.path.join(HOTFIX, "common", "script_values", "zz_ef_money_ledger_values.txt")
LANGS = ["english", "russian", "braz_por", "french", "german", "japanese",
         "korean", "polish", "simp_chinese", "spanish", "turkish"]

KEYS_COUNTRY = ["MONEY_SUPPLY_DESC_fiat_standard", "MONEY_SUPPLY_DESC_silver_standard",
                "MONEY_SUPPLY_DESC_bimetallism_standard", "MONEY_SUPPLY_DESC_gold_standard",
                "MONEY_SUPPLY_DESC_MONEY_VALUE_gold_exchange_standard", "MONEY_SUPPLY_DESC_MONEY_VALUE_subject"]
KEYS_PLAYER = ["MONEY_SUPPLY_DESC_fiat_Player", "MONEY_SUPPLY_DESC_silver_Player",
               "MONEY_SUPPLY_DESC_bimetallism_Player", "MONEY_SUPPLY_DESC_gold_Player",
               "MONEY_SUPPLY_DESC_MONEY_VALUE_gold_exchange_standard_Player",
               "MONEY_SUPPLY_DESC_MONEY_VALUE_subject_player"]


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
                 mult="к вкладам, цель", mm="Денежный мультипликатор M2 / M0", other="В собственности других стран",
                 debt="Госдолг (не деньги)", princ="долг бюджета", dcb="перед центральным банком",
                 hint="Наведите на счёт — все переводы за месяц.")
    else:
        L = dict(title="Money Supply", total="Total", own="Owned in the country (M2)", month="this month",
                 m0="M0 — cash and state money", cb="Central bank reserves", tr="Treasury",
                 sav="Pop savings", m1="M1 = M0 + business cash", bld="Business cash",
                 m2="M2 = M1 + bank funds", bank="Bank funds", dep="deposits", cred="bank credit",
                 mult="of deposits, target", mm="Money multiplier M2 / M0", other="Owned by other countries",
                 debt="Government debt (not money)", princ="budget debt", dcb="to the central bank",
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
        f" - {L['other']}: #T {money('money_supply_stockpile_by_other_country')}#!",
        f"{L['debt']}: {L['princ']} {money('zz_ef_debt_principal')}, {L['dcb']} {sv('zz_ef_debt_cb_gold')} {gold}",
        f"#italic {L['hint']}#!",
        "",
    ]
    raw = [
        ("fixed_income", "постоянные доходы", "fixed income"),
        ("total_income", "все доходы", "total income"),
        ("income", "income (движок)", "income (engine)"),
        ("minting_week", "чеканка", "minting"),
        ("fixed_expenses", "постоянные расходы", "fixed expenses"),
        ("total_expenses", "все расходы", "total expenses"),
        ("military", "армия", "military"),
        ("transfers_out", "переводы по договорам", "treaty transfers"),
        ("tax_waste", "недобранные налоги", "tax waste"),
        ("pool_gross", "пул: приход", "pool: gross income"),
        ("pool_net", "пул: чистый", "pool: net income"),
    ]
    lines.append("#b Сверка — сырые числа движка, в неделю:#!" if ru else "#b Reconciliation — engine raw numbers, weekly:#!")
    lines.append(", ".join(f"{r[1] if ru else r[2]} {sv('zz_ef_raw_' + r[0])}" for r in raw))
    lines.append((f"экспорт {sv('zz_ef_raw_export_gold')} {gold}, импорт {sv('zz_ef_raw_import_gold')} {gold}, "
                  f"ВВП в год {sv('zz_ef_raw_gdp')}") if ru else
                 (f"exports {sv('zz_ef_raw_export_gold')} {gold}, imports {sv('zz_ef_raw_import_gold')} {gold}, "
                  f"GDP per year {sv('zz_ef_raw_gdp')}"))
    return "\\n".join(lines) + "\\n$TOOLTIP_DELIMITER$"


# ---------------------------------------------------------------------------
# Account cards.
# A line: (dir, ru, en, source); dir "in" (money comes to this account) or
# "out". Sources: ("var", x) var:zz_ef_<x>; ("sv", x) script value x;
# ("pos"/"neg", "var"|"sv", x) the positive / negative part of a signed one.
# Every line is shown non-negative, with its sign from dir.
# ---------------------------------------------------------------------------

ACC_ORDER = ["savings", "treasury", "buildings", "banks", "cb"]
TITLES = {
    "savings": ("Сбережения населения", "Pop savings"),
    "treasury": ("Казна", "Treasury"),
    "buildings": ("Касса предприятий", "Business cash"),
    "banks": ("Средства банков", "Bank funds"),
    "cb": ("Резервы центрального банка", "Central bank reserves"),
    "ext": ("Вне счетов", "Outside the accounts"),
}
DELTA = {"savings": "d_savings", "treasury": "d_treasury", "buildings": "d_buildings",
         "banks": "d_pool", "cb": "d_cb"}

OTHER_POS = ("прочее — не видно скрипту", "other — not visible to scripts")

LINES = {
    "savings": {
        "treasury": [("out", "налоги (оценка)", "taxes (estimate)", ("var", "f_taxes"))],
        "buildings": [("out", "покупки товаров", "purchases of goods", ("var", "f_goods"))],
        "banks": [("in", "изъятия вкладов", "deposit withdrawals", ("neg", "var", "f_deposits")),
                  ("out", "вклады", "deposits", ("pos", "var", "f_deposits"))],
        "cb": [("in", "спрос рынка на валюту — доля страны", "market demand for the currency — the country's share",
                ("var", "f_inflow"))],
        "ext": [("out", "срез выше 2 ВВП", "cut above 2 × GDP", ("var", "f_cap")),
                ("in", *OTHER_POS, ("pos", "sv", "zz_ef_other_savings")),
                ("out", *OTHER_POS, ("neg", "sv", "zz_ef_other_savings"))],
    },
    "treasury": {
        "savings": [("in", "налоги из сбережений (оценка)", "taxes from savings (estimate)", ("var", "f_taxes"))],
        "buildings": [],
        "banks": [],
        "cb": [],
        "ext": [("in", "чеканка — новые деньги", "minting — new money", ("var", "f_minting")),
                ("in", "прочие доходы бюджета", "other budget income", ("sv", "zz_ef_lg_taxes_rest")),
                ("in", *OTHER_POS, ("pos", "sv", "zz_ef_other_treasury")),
                ("out", "расходы бюджета и прочее", "budget expenses and other", ("neg", "sv", "zz_ef_other_treasury"))],
    },
    "buildings": {
        "savings": [("in", "покупки населения", "pops' purchases", ("var", "f_goods"))],
        "treasury": [],
        "banks": [("in", "стройка из пула", "construction from the pool", ("var", "f_construction"))],
        "cb": [],
        "ext": [("in", *OTHER_POS, ("pos", "sv", "zz_ef_other_buildings")),
                ("out", "зарплаты, дивиденды, закупки, импорт и прочее", "wages, dividends, purchases, imports and other",
                 ("neg", "sv", "zz_ef_other_buildings"))],
    },
    "banks": {
        "savings": [("in", "вклады", "deposits", ("pos", "var", "f_deposits")),
                    ("out", "изъятия вкладов", "deposit withdrawals", ("neg", "var", "f_deposits"))],
        "treasury": [],
        "buildings": [("out", "стройка — частная и через казну", "construction — private and via the treasury",
                       ("var", "f_construction"))],
        "cb": [],
        "ext": [("in", "новый кредит банков", "new bank credit", ("pos", "var", "f_credit")),
                ("in", "взносы в пул — население и здания (ваниль)", "pool contributions — pops and buildings (vanilla)",
                 ("var", "f_contrib")),
                ("out", "сжатие кредита", "credit contraction", ("neg", "var", "f_credit")),
                ("in", *OTHER_POS, ("pos", "sv", "zz_ef_other_pool")),
                ("out", *OTHER_POS, ("neg", "sv", "zz_ef_other_pool"))],
    },
    "cb": {
        "savings": [("out", "в обращение: спрос рынка — доля страны", "into circulation: market demand — the country's share",
                     ("sv", "zz_ef_cb_demand_own"))],
        "treasury": [],
        "buildings": [],
        "banks": [],
        "ext": [("in", "выпуск: продажи товара-валюты на рынке", "issue: sales of the currency good on the market",
                 ("sv", "zz_ef_cb_issue_month")),
                ("out", "в обращение: другим странам рынка", "into circulation: other countries of the market",
                 ("sv", "zz_ef_cb_demand_others")),
                ("in", "девальвация", "devaluation", ("sv", "zz_ef_cb_devaluation_month")),
                ("out", "ревальвация", "revaluation", ("sv", "zz_ef_cb_revaluation_month")),
                ("in", *OTHER_POS, ("pos", "sv", "zz_ef_other_cb")),
                ("out", *OTHER_POS, ("neg", "sv", "zz_ef_other_cb"))],
    },
}

NOTES = {
    "savings": ("Наличные у населения — модель: денег у групп населения в движке нет. Налоги и покупки — оценка "
                "(ВВП / 12 − взносы в пул; доля налогов — доход бюджета без чеканки).",
                "Cash held by pops — a model: pops hold no money in the engine. Taxes and purchases are an estimate "
                "(GDP / 12 − pool contributions; the taxes' share — budget income without minting)."),
    "treasury": ("Деньги государства — часть M0. Полный бюджет — «Деньги» в верхней панели.",
                 "State money, part of M0. The full budget: Money in the top bar."),
    "buildings": ("Денежные резервы зданий: кредитный лимит − база − доля ВВП (COUNTRY_MIN_CREDIT_*).",
                  "Buildings' cash reserves: credit limit − base − GDP share (COUNTRY_MIN_CREDIT_*)."),
    "banks": ("Банки тянут средства к вкладам × множитель (×3 при 2%, ×1.2 при 12%).",
              "Banks steer their funds to deposits × multiplier (×3 at 2%, ×1.2 at 12%)."),
    "cb": ("Валюта, которую держит центральный банк, вне обращения. Выпуск и спрос — рынок товара-валюты за месяц "
           "(E&F, у хозяина рынка).",
           "Currency held by the central bank, out of circulation. Issue and demand: the currency good's market "
           "this month (E&F, market owner)."),
}


def src_body(src):
    """Body of a script value reading one source, non-negative."""
    if src[0] == "var":
        v = f"zz_ef_{src[1]}"
        return f"\tvalue = 0\n\tif = {{\n\t\tlimit = {{ has_variable = {v} }}\n\t\tvalue = var:{v}\n\t}}\n\tmin = 0\n"
    if src[0] == "sv":
        return f"\tvalue = {src[1]}\n\tmin = 0\n"
    sign, kind, name = src
    flip = "\tmultiply = -1\n" if sign == "neg" else ""
    if kind == "var":
        v = f"zz_ef_{name}"
        return (f"\tvalue = 0\n\tif = {{\n\t\tlimit = {{ has_variable = {v} }}\n\t\tvalue = var:{v}\n\t}}\n"
                f"{flip}\tmin = 0\n")
    return f"\tvalue = {name}\n{flip}\tmin = 0\n"


def ledger_values():
    out = ["# GENERATED by tools/regen_ef_money_supply_loc.py -- do not edit by hand.",
           "# EF.39/EF.44: one script value per line of the account cards in the Money",
           "# Supply tooltip, from the monthly ledger of scripted_effects/",
           "# zz_ef_money_model.txt. COUNTRY scope.",
           "",
           "# Budget income without minting that did not come from pops' savings.",
           "zz_ef_lg_taxes_rest = {\n\tvalue = zz_ef_v_f_taxes_all\n\tif = {\n\t\tlimit = { has_variable = zz_ef_f_taxes }\n"
           "\t\tsubtract = var:zz_ef_f_taxes\n\t}\n\tmin = 0\n}",
           ""]
    for acc in ACC_ORDER:
        for other, lines in LINES[acc].items():
            for i, (_, _, _, src) in enumerate(lines, 1):
                out.append(f"zz_ef_lg_{acc}_{other}_{i} = {{\n{src_body(src)}}}")
        out.append("")
    return "\n".join(out) + "\n"


def nested(lang):
    cur, sv, money, delta, tt = ctx("Country")
    ru = lang == "russian"
    k = 0 if ru else 1
    none = "  нет переводов, видимых скрипту" if ru else "  no transfers visible to scripts"
    d = {}
    for acc in ACC_ORDER:
        L = [f"#b {TITLES[acc][k]} {'за месяц' if ru else 'this month'}: {delta('zz_ef_v_' + DELTA[acc])}#!"]
        n = 0
        for other in [a for a in ACC_ORDER if a != acc] + ["ext"]:
            n += 1
            L.append(f"{n} {TITLES[other][k]}")
            lines = LINES[acc][other]
            if not lines:
                L.append(none)
            for i, (dr, lr, le, _) in enumerate(lines, 1):
                v = money(f"zz_ef_lg_{acc}_{other}_{i}")
                lab = lr if ru else le
                L.append(f"  ← #P +{v}#! {lab}" if dr == "in" else f"  → #N −{v}#! {lab}")
        L += ["", NOTES[acc][k]]
        if acc == "savings":
            L.append((f"Траты населения в месяц: {money('zz_ef_v_f_outlays')} = ВВП / 12 {money('zz_ef_gdp_month')} "
                      f"− взносы в пул {money('zz_ef_pool_contrib_month_gdp')}; из сбережений потрачено "
                      f"{money('zz_ef_v_f_outflow')}.") if ru else
                     (f"Pops' outlays per month: {money('zz_ef_v_f_outlays')} = GDP / 12 {money('zz_ef_gdp_month')} "
                      f"− pool contributions {money('zz_ef_pool_contrib_month_gdp')}; spent from savings "
                      f"{money('zz_ef_v_f_outflow')}."))
        if acc == "banks":
            L.append((f"Вклады {money('zz_ef_deposits')}, кредит банков {money('zz_ef_bank_credit')}: сейчас "
                      f"×{sv('zz_ef_pool_to_deposits', '2')}, цель ×{sv('zz_ef_credit_multiplier', '2')} при ставке "
                      f"{sv('zz_ef_money_rate', '%1')}.") if ru else
                     (f"Deposits {money('zz_ef_deposits')}, bank credit {money('zz_ef_bank_credit')}: now "
                      f"×{sv('zz_ef_pool_to_deposits', '2')}, target ×{sv('zz_ef_credit_multiplier', '2')} at a rate "
                      f"of {sv('zz_ef_money_rate', '%1')}."))
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
    with open(VALUES_OUT + ".tmp", "w", encoding="utf-8", newline="\n") as f:
        f.write(ledger_values())
    os.replace(VALUES_OUT + ".tmp", VALUES_OUT)
    for lang in LANGS:
        d = build(lang)
        head = (f"l_{lang}:\n\n # GENERATED by tools/regen_ef_money_supply_loc.py -- do not edit by hand.\n"
                " # EF.39/EF.44: E&F's Money Supply tooltip as M0/M1/M2, a card per account.\n")
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
    print("ok", len(d), "keys x", len(LANGS), "+", os.path.basename(VALUES_OUT))


if __name__ == "__main__":
    main()
