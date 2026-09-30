#!/usr/bin/env python3
"""
EF.39 / EF.44 -- the "Money Supply" tooltip as M0 / M1 / M2, with a card per
account: hover an account for what came in from and went out to each of the
other accounts over the last month.

E&F's tooltip is 12 localization keys MONEY_SUPPLY_DESC_* (one per monetary
standard, AI and player variants), all the same text except the data context
(Country / GetPlayer). They listed E&F's five counters; the hotfix changed the
composition (script_values/zz_ef_money_model_values.txt: treasury in, the
government_loan counter out, building cash from the credit limit), so the text
is rewritten. Each account line is a nested tooltip
(#tooltippable;tooltip:[X.GetTooltipTag],key ...#!) with the account's card;
the nested keys read the country through Country.* (the tag passes it).

Card (user's layout, 2026-09-30): the change over the month, then rows 1-4 =
the other four accounts, row 5 = outside the accounts (new money, vanilla's
pool contributions, "other" the engine does not give scripts), each row
"-> : +in" and "<- : -out". Amounts are from the last monthly step, so the
rows add up to the change exactly ("other" closes the gap).

Writes
  _ef/ef hotfix 1.13/localization/<lang>/replace/zz_ef_money_supply_replace_l_<lang>.yml
    (UTF-8 with BOM; RU and EN written, the other 9 languages get EN);
  _ef/ef hotfix 1.13/common/script_values/zz_ef_money_ledger_values.txt
    (the card cells).

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
    if lang == "russian":
        L = dict(title="Денежная масса", total="Всего", own="В собственности страны (M2)", month="за месяц",
                 m0="M0 — наличные и деньги государства", cb="Резервы центрального банка", tr="Казна",
                 sav="Сбережения населения", m1="M1 = M0 + касса предприятий", bld="Касса предприятий",
                 m2="M2 = M1 + средства банков", bank="Средства банков", dep="вклады", cred="кредит банков",
                 mult="к вкладам, цель", mm="Денежный мультипликатор M2 / M0", other="В собственности других стран",
                 debt="Госдолг (не деньги)", princ="долг бюджета", dcb="перед центральным банком",
                 hint="Наведите на счёт — переводы за месяц.")
    else:
        L = dict(title="Money Supply", total="Total", own="Owned in the country (M2)", month="this month",
                 m0="M0 — cash and state money", cb="Central bank reserves", tr="Treasury",
                 sav="Pop savings", m1="M1 = M0 + business cash", bld="Business cash",
                 m2="M2 = M1 + bank funds", bank="Bank funds", dep="deposits", cred="bank credit",
                 mult="of deposits, target", mm="Money multiplier M2 / M0", other="Owned by other countries",
                 debt="Government debt (not money)", princ="budget debt", dcb="to the central bank",
                 hint="Hover an account for its transfers this month.")
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
    ]
    return "\\n".join(lines) + "\\n$TOOLTIP_DELIMITER$"


# ---------------------------------------------------------------------------
# Account cards.
# Sources: ("var", x) a non-negative ledger variable var:zz_ef_<x>;
# ("sv", x) a non-negative script value x;
# ("pos"/"neg", "var"|"sv", x) the positive / negative part of a signed one.
# A cell is the sum of its sources; [] is a flow the model does not see.
# ---------------------------------------------------------------------------

ACC_ORDER = ["savings", "treasury", "buildings", "banks", "cb"]
TITLES = {
    "savings": ("Сбережения населения", "Pop savings"),
    "treasury": ("Казна", "Treasury"),
    "buildings": ("Касса предприятий", "Business cash"),
    "banks": ("Средства банков", "Bank funds"),
    "cb": ("Резервы центрального банка", "Central bank reserves"),
}
DELTA = {"savings": "d_savings", "treasury": "d_treasury", "buildings": "d_buildings",
         "banks": "d_pool", "cb": "d_cb"}

# CELLS[acc][other] = (in: sources, out: sources); other "ext" = outside.
CELLS = {
    "savings": {
        "treasury": ([], [("var", "f_taxes")]),
        "buildings": ([], [("var", "f_goods")]),
        "banks": ([("neg", "var", "f_deposits")], [("pos", "var", "f_deposits")]),
        "cb": ([], []),
        "ext": ([("var", "f_inflow"), ("pos", "sv", "zz_ef_other_savings")],
                [("var", "f_cap"), ("neg", "sv", "zz_ef_other_savings")]),
    },
    "treasury": {
        "savings": ([("var", "f_taxes")], []),
        "buildings": ([], []),
        "banks": ([], []),
        "cb": ([], []),
        "ext": ([("var", "f_minting"), ("sv", "zz_ef_lg_taxes_rest"), ("pos", "sv", "zz_ef_other_treasury")],
                [("neg", "sv", "zz_ef_other_treasury")]),
    },
    "buildings": {
        "savings": ([("var", "f_goods")], []),
        "treasury": ([], []),
        "banks": ([("var", "f_construction")], []),
        "cb": ([], []),
        "ext": ([("pos", "sv", "zz_ef_other_buildings")], [("neg", "sv", "zz_ef_other_buildings")]),
    },
    "banks": {
        "savings": ([("pos", "var", "f_deposits")], [("neg", "var", "f_deposits")]),
        "treasury": ([], []),
        "buildings": ([], [("var", "f_construction")]),
        "cb": ([], []),
        "ext": ([("pos", "var", "f_credit"), ("var", "f_contrib"), ("pos", "sv", "zz_ef_other_pool")],
                [("neg", "var", "f_credit"), ("neg", "sv", "zz_ef_other_pool")]),
    },
    "cb": {
        "savings": ([], []),
        "treasury": ([], []),
        "buildings": ([], []),
        "banks": ([], []),
        "ext": ([("pos", "var", "d_cb")], [("neg", "var", "d_cb")]),
    },
}

EXT = {
    "savings": ("вне счетов: спрос на валюту / срез выше 2 ВВП, прочее",
                "outside: currency demand / cut above 2 × GDP, other"),
    "treasury": ("вне счетов: чеканка, прочие доходы бюджета / расходы бюджета",
                 "outside: minting, other budget income / budget expenses"),
    "buildings": ("вне счетов: зарплаты, дивиденды, закупки, экспорт",
                  "outside: wages, dividends, purchases, exports"),
    "banks": ("вне счетов: новый кредит банков, взносы в пул (ваниль) / сжатие кредита, прочее",
              "outside: new bank credit, pool contributions (vanilla) / credit contraction, other"),
    "cb": ("вне счетов: выпуск и выкуп по расчёту E&F", "outside: issue and buyback by E&F's reckoning"),
}

NOTES = {
    "savings": ("Наличные у населения. Налоги и траты на товары — оценка: ВВП / 12 − взносы в пул, доля налогов — "
                "доход бюджета без чеканки. Зарплаты и дивиденды скрипту не видны — они в «прочем» у предприятий.",
                "Cash held by pops. Taxes and spending on goods are an estimate: GDP / 12 − pool contributions, the "
                "taxes' share — budget income without minting. Wages and dividends are not visible to scripts — they "
                "are in businesses' other."),
    "treasury": ("Деньги государства — часть M0. Полный бюджет — «Деньги» в верхней панели.",
                 "State money, part of M0. The full budget: Money in the top bar."),
    "buildings": ("Денежные резервы зданий: кредитный лимит − база − доля ВВП (COUNTRY_MIN_CREDIT_*).",
                  "Buildings' cash reserves: credit limit − base − GDP share (COUNTRY_MIN_CREDIT_*)."),
    "banks": ("Стройка — частная и через казну (перевод из пула в бюджет). Банки тянут средства к вкладам × "
              "множитель (×3 при 2%, ×1.2 при 12%).",
              "Construction: private and via the treasury (transfer from the pool to the budget). Banks steer "
              "their funds to deposits × multiplier (×3 at 2%, ×1.2 at 12%)."),
    "cb": ("Валюта, которую держит центральный банк, вне обращения.",
           "Currency held by the central bank, out of circulation."),
}


def src_read(src):
    """Lines of a script value adding one source (non-negative)."""
    if src[0] == "var":
        v = f"zz_ef_{src[1]}"
        return f"\tif = {{\n\t\tlimit = {{ has_variable = {v} }}\n\t\tadd = {{\n\t\t\tvalue = var:{v}\n\t\t\tmin = 0\n\t\t}}\n\t}}\n"
    if src[0] == "sv":
        return f"\tadd = {{\n\t\tvalue = {src[1]}\n\t\tmin = 0\n\t}}\n"
    sign, kind, name = src
    flip = "\t\t\tmultiply = -1\n" if sign == "neg" else ""
    if kind == "var":
        v = f"zz_ef_{name}"
        return (f"\tif = {{\n\t\tlimit = {{ has_variable = {v} }}\n\t\tadd = {{\n\t\t\tvalue = var:{v}\n"
                f"{flip}\t\t\tmin = 0\n\t\t}}\n\t}}\n")
    return f"\tadd = {{\n\t\tvalue = {name}\n{flip.replace(chr(9) * 3, chr(9) * 2)}\t\tmin = 0\n\t}}\n"


def ledger_values():
    out = ["# GENERATED by tools/regen_ef_money_supply_loc.py -- do not edit by hand.",
           "# EF.39/EF.44: cells of the account cards in the Money Supply tooltip, from the",
           "# monthly ledger of scripted_effects/zz_ef_money_model.txt. COUNTRY scope.",
           "",
           "# Budget income without minting that did not come from pops' savings.",
           "zz_ef_lg_taxes_rest = {\n\tvalue = zz_ef_v_f_taxes_all\n\tif = {\n\t\tlimit = { has_variable = zz_ef_f_taxes }\n"
           "\t\tsubtract = var:zz_ef_f_taxes\n\t}\n\tmin = 0\n}",
           ""]
    for acc in ACC_ORDER:
        for other, (cin, cout) in CELLS[acc].items():
            for side, srcs in (("in", cin), ("out", cout)):
                body = "\tvalue = 0\n" + "".join(src_read(s) for s in srcs)
                out.append(f"zz_ef_lg_{acc}_{other}_{side} = {{\n{body}}}")
        out.append("")
    return "\n".join(out) + "\n"


def nested(lang):
    cur, sv, money, delta, tt = ctx("Country")
    ru = lang == "russian"
    k = 0 if ru else 1
    d = {}
    for acc in ACC_ORDER:
        L = [f"#b {TITLES[acc][k]} {'за месяц' if ru else 'this month'}: {delta('zz_ef_v_' + DELTA[acc])}#!"]
        n = 0
        for other in [a for a in ACC_ORDER if a != acc] + ["ext"]:
            n += 1
            name = TITLES[other][k] if other != "ext" else EXT[acc][k]
            L.append(f"{n} {name}")
            L.append(f"  -> : #P +{money(f'zz_ef_lg_{acc}_{other}_in')}#!")
            L.append(f"  <- : #N −{money(f'zz_ef_lg_{acc}_{other}_out')}#!")
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
