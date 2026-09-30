#!/usr/bin/env python3
"""
EF.39 / EF.44 -- the "Money Supply" tooltip as M0 / M1 / M2 with a monthly
ledger per account (hover an account: where its money came from and went to
over the last month).

E&F's tooltip is 12 localization keys MONEY_SUPPLY_DESC_* (one per monetary
standard, AI and player variants), all the same text except the data context
(Country / GetPlayer). They listed E&F's five counters; the hotfix changed the
composition (script_values/zz_ef_money_model_values.txt: treasury in, the
government_loan counter out, building cash from the credit limit), so the text
is rewritten. Each account line is a nested tooltip
(#tooltippable;tooltip:[X.GetTooltipTag],key ...#!), the nested keys read the
country through Country.* (the tag passes it).

Writes _ef/ef hotfix 1.13/localization/<lang>/replace/
zz_ef_money_supply_replace_l_<lang>.yml (UTF-8 with BOM): RU and EN written,
the other 9 languages get EN.

Usage:
    py tools/regen_ef_money_supply_loc.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, r"..\_ef\ef hotfix 1.13\localization"))
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


def nested(lang):
    cur, sv, money, delta, tt = ctx("Country")

    def row(label, name):
        return f"  {label}: {sv(name, 'D+=')}{cur}"

    if lang == "russian":
        return {
            "zz_ef_ms_tt_savings": "\\n".join([
                f"#b Сбережения населения за месяц: {delta('zz_ef_v_d_savings')}#!",
                row("приток — спрос на валюту, доля страны в рынке", "zz_ef_v_f_inflow"),
                row("→ казна: налоги (оценка)", "zz_ef_f_taxes_neg"),
                row("→ предприятия: траты на товары", "zz_ef_f_goods_neg"),
                row("↔ банки: вклады (минус) / изъятия (плюс)", "zz_ef_f_deposits_neg"),
                row("поправка: срез выше 2 ВВП", "zz_ef_f_cap_neg"),
                row("прочее", "zz_ef_other_savings"),
                "",
                "Наличные у населения. Приток — спрос рынка на валюту (E&F), делится между странами рынка по доле "
                "ВВП. Траты на товары и налоги ≈ ВВП − взносы в пул; из большого запаса тратят целиком, из малого — "
                "почти ничего. Доля налогов в тратах — оценка: доход бюджета без чеканки / траты населения.",
                "",
                f"Траты населения в месяц (оценка): {money('zz_ef_v_f_outlays')} = ВВП / 12 {money('zz_ef_gdp_month')} "
                f"− взносы в пул {money('zz_ef_pool_contrib_month_gdp')}. Из сбережений потрачено "
                f"{money('zz_ef_v_f_outflow')}.",
            ]),
            "zz_ef_ms_tt_banks": "\\n".join([
                f"#b Средства банков за месяц: {delta('zz_ef_v_d_pool')}#!",
                row("← население: вклады / изъятия", "zz_ef_v_f_deposits"),
                row("новый кредит банков (+) / сжатие (−)", "zz_ef_v_f_credit"),
                row("← население и здания: взносы в пул (ваниль)", "zz_ef_v_f_contrib"),
                row("→ предприятия: частная стройка", "zz_ef_f_construction_neg"),
                row("прочее", "zz_ef_other_pool"),
                "",
                f"Вклады {money('zz_ef_deposits')} ({sv('zz_ef_v_d_deposits', 'D+=')}{cur}), кредит банков "
                f"{money('zz_ef_bank_credit')}. Банки тянут средства к вкладам × множитель: сейчас "
                f"×{sv('zz_ef_pool_to_deposits', '2')}, цель ×{sv('zz_ef_credit_multiplier', '2')} при ставке "
                f"{sv('zz_ef_money_rate', '%1')} (×3 при 2%, ×1.2 при 12%). Прочее — госстройка из пула, проценты "
                "по облигациям.",
            ]),
            "zz_ef_ms_tt_treasury": "\\n".join([
                f"#b Казна за месяц: {delta('zz_ef_v_d_treasury')}#!",
                row("налоги и прочие доходы бюджета (оценка)", "zz_ef_v_f_taxes_all"),
                row("чеканка — новые деньги", "zz_ef_v_f_minting"),
                row("прочее: расходы, пошлины, пакты, займы", "zz_ef_other_treasury"),
                "",
                "Деньги государства — часть M0. Полный бюджет — «Деньги» в верхней панели. Чеканка — единственная "
                "статья бюджета, которая создаёт деньги; займы создают деньги вместе с долгом.",
            ]),
            "zz_ef_ms_tt_buildings": "\\n".join([
                f"#b Касса предприятий за месяц: {delta('zz_ef_v_d_buildings')}#!",
                row("← население: траты на товары", "zz_ef_v_f_goods"),
                row("← банки: частная стройка", "zz_ef_v_f_construction"),
                row("прочее: зарплаты, дивиденды, закупки, экспорт", "zz_ef_other_buildings"),
                "",
                "Денежные резервы зданий. Движок отдаёт их только внутри кредитного лимита страны: лимит − база − "
                "доля ВВП (константы COUNTRY_MIN_CREDIT_*). Зарплат и дивидендов по отдельности скрипту не видно — "
                "они в «прочем».",
            ]),
            "zz_ef_ms_tt_cb": "\\n".join([
                f"#b Резервы центрального банка за месяц: {delta('zz_ef_v_d_cb')}#!",
                row("по расчёту E&F (выпуск, выкуп, девальвация)", "money_supply_state_monthly"),
                "",
                "Валюта, которую держит центральный банк, вне обращения.",
            ]),
        }
    return {
        "zz_ef_ms_tt_savings": "\\n".join([
            f"#b Pop savings this month: {delta('zz_ef_v_d_savings')}#!",
            row("inflow — currency demand, the country's share of its market", "zz_ef_v_f_inflow"),
            row("→ treasury: taxes (estimate)", "zz_ef_f_taxes_neg"),
            row("→ businesses: spending on goods", "zz_ef_f_goods_neg"),
            row("↔ banks: deposits (minus) / withdrawals (plus)", "zz_ef_f_deposits_neg"),
            row("correction: cut above 2 × GDP", "zz_ef_f_cap_neg"),
            row("other", "zz_ef_other_savings"),
            "",
            "Cash held by pops. Inflow is the market's demand for the currency (E&F), split among the market's "
            "countries by GDP share. Spending on goods and taxes ≈ GDP − pool contributions; a large stock is "
            "spent from fully, a small one hardly at all. The taxes' share of spending is an estimate: budget "
            "income without minting / pops' outlays.",
            "",
            f"Pops' outlays per month (estimate): {money('zz_ef_v_f_outlays')} = GDP / 12 {money('zz_ef_gdp_month')} "
            f"− pool contributions {money('zz_ef_pool_contrib_month_gdp')}. Spent from savings: "
            f"{money('zz_ef_v_f_outflow')}.",
        ]),
        "zz_ef_ms_tt_banks": "\\n".join([
            f"#b Bank funds this month: {delta('zz_ef_v_d_pool')}#!",
            row("← pops: deposits / withdrawals", "zz_ef_v_f_deposits"),
            row("new bank credit (+) / contraction (−)", "zz_ef_v_f_credit"),
            row("← pops and buildings: pool contributions (vanilla)", "zz_ef_v_f_contrib"),
            row("→ businesses: private construction", "zz_ef_f_construction_neg"),
            row("other", "zz_ef_other_pool"),
            "",
            f"Deposits {money('zz_ef_deposits')} ({sv('zz_ef_v_d_deposits', 'D+=')}{cur}), bank credit "
            f"{money('zz_ef_bank_credit')}. Banks steer their funds to deposits × multiplier: now "
            f"×{sv('zz_ef_pool_to_deposits', '2')}, target ×{sv('zz_ef_credit_multiplier', '2')} at a rate of "
            f"{sv('zz_ef_money_rate', '%1')} (×3 at 2%, ×1.2 at 12%). Other: government construction from the "
            "pool, interest on bonds.",
        ]),
        "zz_ef_ms_tt_treasury": "\\n".join([
            f"#b Treasury this month: {delta('zz_ef_v_d_treasury')}#!",
            row("taxes and other budget income (estimate)", "zz_ef_v_f_taxes_all"),
            row("minting — new money", "zz_ef_v_f_minting"),
            row("other: expenses, tariffs, pacts, loans", "zz_ef_other_treasury"),
            "",
            "State money, part of M0. The full budget: Money in the top bar. Minting is the only budget item "
            "that creates money; loans create money together with debt.",
        ]),
        "zz_ef_ms_tt_buildings": "\\n".join([
            f"#b Business cash this month: {delta('zz_ef_v_d_buildings')}#!",
            row("← pops: spending on goods", "zz_ef_v_f_goods"),
            row("← banks: private construction", "zz_ef_v_f_construction"),
            row("other: wages, dividends, purchases, exports", "zz_ef_other_buildings"),
            "",
            "Buildings' cash reserves. The engine gives them only inside the country's credit limit: limit − base − "
            "GDP share (COUNTRY_MIN_CREDIT_* defines). Wages and dividends are not visible to scripts one by one — "
            "they are in other.",
        ]),
        "zz_ef_ms_tt_cb": "\\n".join([
            f"#b Central bank reserves this month: {delta('zz_ef_v_d_cb')}#!",
            row("by E&F's reckoning (issue, buyback, devaluation)", "money_supply_state_monthly"),
            "",
            "Currency held by the central bank, out of circulation.",
        ]),
    }


def build(lang):
    src = "russian" if lang == "russian" else "english"
    d = {}
    for k in KEYS_COUNTRY:
        d[k] = main_text(src, "Country")
    for k in KEYS_PLAYER:
        d[k] = main_text(src, "GetPlayer")
    d.update(nested(src))
    return d


def main():
    for lang in LANGS:
        d = build(lang)
        head = (f"l_{lang}:\n\n # GENERATED by tools/regen_ef_money_supply_loc.py -- do not edit by hand.\n"
                " # EF.39/EF.44: E&F's Money Supply tooltip as M0/M1/M2 with a monthly ledger per account.\n")
        if lang not in ("english", "russian"):
            head += " # Not translated yet: English text.\n"
        lines = [head, "\n"]
        for k, v in d.items():
            assert '"' not in v, k
            lines.append(f' {k}:0 "{v}"\n')
        path = os.path.join(ROOT, lang, "replace", f"zz_ef_money_supply_replace_l_{lang}.yml")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path + ".tmp", "w", encoding="utf-8-sig", newline="\n") as f:
            f.write("".join(lines))
        os.replace(path + ".tmp", path)
    print("ok", len(d), "keys x", len(LANGS))


if __name__ == "__main__":
    main()
