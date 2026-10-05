#!/usr/bin/env python3
"""
EF.30 / EF.45 -- localization of the key rate panel, button tooltips, concepts
and the EF.31 modifier, 11 languages (RU and EN written, the other 9 get EN).
Writes _ef/ef hotfix 1.13/localization/<lang>/zz_ef_cb_rate_panel_l_<lang>.yml
(UTF-8 with BOM). Moved from a scratch script into tools/ 2026-09-30.

Usage:
    py tools/regen_ef_cb_rate_loc.py
"""
import os

# relative to the repo, not the PC's main checkout: run from the bridge worktree it wrote there (5.10)
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_ef", "ef hotfix 1.13", "localization")
LANGS = ["english", "russian", "braz_por", "french", "german", "japanese",
         "korean", "polish", "simp_chinese", "spanish", "turkish"]

SV = "GetPlayer.MakeScope.ScriptValue"
NOTE = f"[{SV}('zz_ef_cb_rate_note_value')|2]"
RULE = f"[{SV}('zz_ef_cb_rate_rating_target')|%2]"
TARGET = f"[{SV}('zz_ef_cb_rate_target')|%2]"
CUR = "[GetPlayer.MakeScope.Var('base_rate_percentage').GetValue|%2]"
GAP = f"[{SV}('zz_ef_cb_rule_gap_pp')|2]"
STEP = f"[{SV}('zz_ef_cb_rate_next_step_pp')|+2]"
MONTHS = f"[{SV}('zz_ef_cb_rate_months_to_step')|0]"
BIAS = f"[{SV}('zz_ef_cb_rate_bias_pp')|+1]"
LETTER = "[GetPlayer.GetCustom('country_credit_rating_texture')]"
DEVAL = "[GetLawType('law_devaluation').GetName]"
REVAL = "[GetLawType('law_revaluation').GetName]"
FXC = "[GetStaticModifier('foreign_exchange_controls').GetName]"
KR = "[concept_base_rate_percentage]"
CB = "[concept_central_bank]"
CR = "[concept_country_rating]"
RR = "[concept_zz_ef_policy_rule_rate]"
DA = "[concept_zz_ef_discretionary_adjustment]"
MP = "[concept_monetary_policy]"
INF = "[concept_inflation_value]"
NEU = f"[{SV}('zz_ef_cb_rule_neutral_pp')|1]"
PIN = f"[{SV}('zz_ef_cb_rule_inflation_pp')|+1]"
PRI = f"[{SV}('zz_ef_cb_rule_risk_pp')|+1]"
PCO = f"[{SV}('zz_ef_cb_rule_cover_pp')|+1]"
# EF.43 + В4.3 (5.10): the currency (parity changes, suspended redemption) and debt / deficit parts of the premium
PFX = f"[{SV}('zz_ef_risk_fx_pp')|+1]"
PDB = f"[{SV}('zz_ef_risk_debt_pp')|+1]"
PMO = f"[{SV}('zz_ef_cb_rule_money_pp')|+1]"
COV = f"[{SV}('zz_ef_cb_cover')|%0]"
GRT = f"[{SV}('zz_ef_gov_rate_target')|%2]"
GPR = f"[{SV}('zz_ef_gov_rate_premium_pp')|+2]"
GCO = f"[{SV}('zz_ef_gov_rate_corr_pct')|+0]"

RU = {
    "concept_zz_ef_policy_rule_rate": "Ставка по правилу",
    "concept_zz_ef_policy_rule_rate_desc": (
        f"{RR} — ставка, которую {CB} рассчитывает сам, по денежной системе. Металлический стандарт — как Банк "
        "Англии XIX века, по резервам: 3% + поправка на покрытие (металл по паритету к M2, норма 40%: +1 п.п. за "
        "каждые 10 п.п. ниже нормы, до +5; −0.5 п.п. за 10 п.п. выше, до −2) + поправка на рост денег (+0.5 п.п. "
        f"за каждый п.п., на который M2 за год растёт быстрее ВВП, от −2 до +3). Фиатный — правило Тейлора: 2.5% + {INF} (цены потребительской корзины) + "
        f"0.5 × ({INF} − 2%) + та же поправка на рост денег. {CR} в ставку центробанка не входит: это премия, которую требуют с правительства. "
        "Коридор: металлический стандарт — 2–12%, фиатный или без денежной системы — 0.5–25%. "
        "Страна без центрального банка — 6.5%.\\n\\n"
        f"Фактическая {KR} идёт к ставке по правилу с {DA} правительства (до ±2 п.п.). Разница между "
        "ними показывает, насколько политика мягче или жёстче правила.\\n\\n"
        f"«Правило или усмотрение» — классический спор {MP}: правило делает ставку предсказуемой, "
        "усмотрение даёт свободу, но за неё платят доверием (Кидланд и Прескотт, 1977; правило Тейлора, 1993)."
    ),
    "concept_zz_ef_discretionary_adjustment": "Дискреционная поправка",
    "concept_zz_ef_discretionary_adjustment_desc": (
        f"{DA} — насколько правительство своим решением сдвинуло {KR} от {RR}: от −2 до +2 п.п., "
        "шагом 0.5 п.п., кнопками «−» и «+» в «Финансах». Центробанк ведёт ставку к правилу с этой "
        "поправкой и не отыгрывает её назад.\\n\\n"
        "Ниже правила — дешевле кредит, быстрее растёт инвестиционный пул, больше частной стройки; "
        "выше правила — наоборот, экономика остывает."
    ),
    "zz_ef_rate_box_rating": "Кредитный рейтинг",
    "zz_ef_rate_box_rating_value": f"{LETTER}\\n{NOTE}",
    "zz_ef_rate_box_rating_tt": (
        f"{CR}: #v {NOTE}#! (обычно 0–10, институт центробанка поднимает выше).\\n\\n"
        "До 10 баллов дают показатели экономики и государства (подробно — «Посмотреть кредитный рейтинг» выше), "
        "до +2.5 — институт центрального банка (0.5 за уровень). Взятые кредиты умножают рейтинг на 0.75, "
        "долгая война и большой госдолг снижают его ещё.\\n\\n"
        "Рейтинг — это премия, которую кредиторы требуют с правительства (его облигации и займы): #v 0.6 п.п.#! "
        f"за каждый балл ниже 10, до 6 п.п., плюс стабильность — всего сейчас {PRI} п.п. В {RR} он не входит."
    ),
    "zz_ef_rate_box_target": "Ставка по правилу",
    "zz_ef_rate_box_target_value": RULE,
    "zz_ef_rate_box_target_value_up": f"#N {RULE}#!",
    "zz_ef_rate_box_target_value_down": f"#P {RULE}#!",
    "zz_ef_rate_box_target_tt": (
        f"{RR}: #v {RULE}#!\\n"
        f"  базовая ставка: {NEU} п.п.\\n"
        f"  {INF} (фиат): {PIN} п.п.\\n"
        f"  покрытие металлом {COV} (норма 40%): {PCO} п.п.\\n"
        f"  рост M2 быстрее ВВП: {PMO} п.п.\\n"
        "В коридоре стандарта: металл 2–12%, фиат 0.5–25%. Страна без центробанка — 6.5%. "
        f"{DA} на неё не влияет.\\n\\n"
        f"Текущая {KR}: {CUR}. Правило минус ставка: #v {GAP} п.п.#! "
        "#N Красным#! — ставка ниже правила (политика мягче), #P зелёным#! — выше (жёстче).\\n\\n"
        f"Центробанк ведёт ставку к правилу с поправкой: к #v {TARGET}#!."
    ),
    "zz_ef_rate_box_step": "Динамика",
    "zz_ef_rate_box_step_value": f"{STEP} п.п.\\nчерез {MONTHS} мес.",
    "zz_ef_rate_box_step_tt": (
        f"Раз в квартал {CB} сдвигает {KR} к {RR} с {DA} (сейчас к #v {TARGET}#!): не больше чем на #v 0.5 п.п.#!, "
        "или на #v 1 п.п.#!, если до цели больше 5 п.п.\\n\\n"
        f"Следующий шаг: #v {STEP} п.п.#! через {MONTHS} мес."
    ),
    "zz_ef_rate_box_gov": "Ставка правительства",
    "zz_ef_rate_box_gov_value": f"{GRT}",
    "zz_ef_rate_box_gov_tt": (
        f"Под сколько занимает правительство: {KR} + премия за риск = #v {GRT}#!\\n\\n"
        f"Премия #v {GPR} п.п.#! — {PRI} п.п. по рейтингу и стабильности (как в {RR}; в них — "
        f"{PFX} п.п. за смену паритета и приостановку размена, затухает за 5 лет, и {PDB} п.п. за долг выше 25% ВВП и "
        f"хронический дефицит), с поправкой #v {GCO}%#! от статуса "
        "державы, компаний и технологий (не больше чем вдвое меньше или вдвое больше). Ниже ключевой ставка не бывает."
    ),
    "zz_ef_rate_box_policy": "Дискреционная поправка",
    "zz_ef_rate_box_policy_value": f"{BIAS} п.п.",
    "zz_ef_rate_box_policy_tt": (
        f"{DA}: #v {BIAS} п.п.#!\\n\\n"
        "Кнопки «−» и «+» под ставкой: каждое нажатие сразу сдвигает ставку на 0.5 п.п., и центробанк не "
        f"отыгрывает её назад. Всего не больше ±2 п.п. {RR} от поправки не меняется."
    ),
    "zz_ef_rate_tt_increase_desc": (
        "#b Повысить ключевую ставку#!\\n"
        f"{KR} сразу вырастет на 0.5 п.п.: {DA} станет на 0.5 п.п. выше, и центробанк не будет возвращать "
        f"ставку к правилу. Поправка сейчас: {BIAS} п.п. из допустимых ±2."
    ),
    "zz_ef_rate_tt_reduce_desc": (
        "#b Снизить ключевую ставку#!\\n"
        f"{KR} сразу снизится на 0.5 п.п.: {DA} станет на 0.5 п.п. ниже, и центробанк не будет возвращать "
        f"ставку к правилу. Поправка сейчас: {BIAS} п.п. из допустимых ±2."
    ),
    "zz_ef_rate_tt_effect_up": "Ключевая ставка: #P +0.5 п.п.#!, дискреционная поправка: +0.5 п.п.",
    "zz_ef_rate_tt_effect_down": "Ключевая ставка: #P −0.5 п.п.#!, дискреционная поправка: −0.5 п.п.",
    "zz_ef_rate_tt_conditions": "\\n\\n#b Условия и действие:#!\\n",
    "zz_ef_rate_tt_below_max": "Ключевая ставка ниже потолка коридора (12% при металле, 25% при фиате)",
    "zz_ef_rate_tt_above_min": "Ключевая ставка выше 0.5%",
    "zz_ef_rate_tt_bias_up": f"Дискреционная поправка ниже +2 п.п. (сейчас {BIAS})",
    "zz_ef_rate_tt_bias_down": f"Дискреционная поправка выше −2 п.п. (сейчас {BIAS})",
    "zz_ef_rate_tt_no_devaluation": f"Не действует закон «{DEVAL}»",
    "zz_ef_rate_tt_no_revaluation": f"Не действует закон «{REVAL}»",
    "zz_ef_rate_tt_no_fx_controls": f"Нет модификатора «{FXC}»",
    "zz_ef_rate_private_construction": "Ключевая ставка: частная стройка",
    "zz_ef_rate_private_construction_desc": (
        f"{KR} ниже 6.5% увеличивает долю очков строительства частного сектора, выше — уменьшает: "
        "5 п.п. доли за каждый процент ставки, не больше ±30."
    ),
    "zz_ef_business_cash": "Денежная масса: касса предприятий",
    "zz_ef_business_cash_desc": (
        "Устаревший: потолок кассы зданий теперь в базовых значениях страны. Снимается сам в начале месяца."
    ),
    "zz_ef_debt_service": "Погашение кредитов бизнеса",
    "zz_ef_debt_service_desc": (
        "Взносы зданий в инвестиционный пул не покрывают недельный платёж по банковскому кредиту бизнеса "
        "(1/260 долга + проценты): владельцы отдают в пул большую долю дохода вместо дивидендов. Растёт на 0.01 "
        "в неделю, пока не хватает, снижается, когда взносы покрывают платёж с запасом 20%."
    ),
}

EN = {
    "concept_zz_ef_policy_rule_rate": "Policy Rule Rate",
    "concept_zz_ef_policy_rule_rate_desc": (
        f"The {RR} is the rate the {CB} computes on its own from the money system. Metal standards, like the Bank "
        "of England in the 19th century, by its reserves: 3% + a cover term (metal at parity against M2, normal 40%: "
        "+1 pp per 10 pp under the norm, up to +5; −0.5 pp per 10 pp over it, down to −2) + a money growth term "
        "(+0.5 pp per pp M2 grows faster than GDP in a year, −2 to +3). Fiat, the Taylor rule: 2.5% + "
        f"{INF} (consumer prices) + 0.5 × ({INF} − 2%) + the same money growth term. The {CR} is not in the central bank's rate: it is the premium lenders ask "
        "of the government. "
        "Corridor: metal standards 2–12%, fiat or no monetary system 0.5–25%. "
        "A country without a central bank: 6.5%.\\n\\n"
        f"The actual {KR} moves towards the rule rate plus the government's {DA} (up to ±2 pp). The gap "
        "between them shows how much looser or tighter policy is than the rule.\\n\\n"
        f"Rules versus discretion is the classic debate of {MP}: a rule makes the rate predictable, "
        "discretion gives freedom and pays for it in credibility (Kydland and Prescott, 1977; the Taylor rule, 1993)."
    ),
    "concept_zz_ef_discretionary_adjustment": "Discretionary Adjustment",
    "concept_zz_ef_discretionary_adjustment_desc": (
        f"The {DA} is how far the government has moved the {KR} away from the {RR} by its own decision: "
        "from −2 to +2 pp in steps of 0.5 pp, with the − and + buttons in the Finance tab. The central bank "
        "steers the rate to the rule plus this adjustment and does not walk it back.\\n\\n"
        "Below the rule: cheaper credit, a faster growing investment pool, more private construction; "
        "above the rule: the reverse, the economy cools."
    ),
    "zz_ef_rate_box_rating": "Credit rating",
    "zz_ef_rate_box_rating_value": f"{LETTER}\\n{NOTE}",
    "zz_ef_rate_box_rating_tt": (
        f"{CR}: #v {NOTE}#! (normally 0–10, the central bank institution lifts it higher).\\n\\n"
        "Up to 10 points come from the economy and the state (details under \\\"View credit rating\\\" above), "
        "up to +2.5 from the central bank institution (0.5 per level). Taking loans multiplies the rating by 0.75, "
        "a long war and heavy debt lower it further.\\n\\n"
        "The rating is the premium lenders ask of the government (its bonds and loans): #v 0.6 pp#! for each "
        f"point below 10, up to 6 pp, plus stability — {PRI} pp now. It is not in the {RR}."
    ),
    "zz_ef_rate_box_target": "Policy rule rate",
    "zz_ef_rate_box_target_value": RULE,
    "zz_ef_rate_box_target_value_up": f"#N {RULE}#!",
    "zz_ef_rate_box_target_value_down": f"#P {RULE}#!",
    "zz_ef_rate_box_target_tt": (
        f"{RR}: #v {RULE}#!\\n"
        f"  base rate: {NEU} pp\\n"
        f"  {INF} (fiat): {PIN} pp\\n"
        f"  metal cover {COV} (normal 40%): {PCO} pp\\n"
        f"  M2 growing faster than GDP: {PMO} pp\\n"
        "Within the standard's corridor: metal 2–12%, fiat 0.5–25%. Without a central bank: 6.5%. "
        f"The {DA} does not change it.\\n\\n"
        f"Current {KR}: {CUR}. Rule minus rate: #v {GAP} pp#! "
        "#N Red#!: the rate is below the rule (looser policy), #P green#!: above it (tighter).\\n\\n"
        f"The central bank steers the rate to the rule plus the adjustment: to #v {TARGET}#!."
    ),
    "zz_ef_rate_box_step": "Trend",
    "zz_ef_rate_box_step_value": f"{STEP} pp\\nin {MONTHS} mo.",
    "zz_ef_rate_box_step_tt": (
        f"Every quarter the {CB} moves the {KR} towards the {RR} plus the {DA} (now to #v {TARGET}#!): by at most #v 0.5 pp#!, "
        "or #v 1 pp#! when that is more than 5 pp away.\\n\\n"
        f"Next step: #v {STEP} pp#! in {MONTHS} months."
    ),
    "zz_ef_rate_box_gov": "Government rate",
    "zz_ef_rate_box_gov_value": f"{GRT}",
    "zz_ef_rate_box_gov_tt": (
        f"What the government borrows at: the {KR} + the risk premium = #v {GRT}#!\\n\\n"
        f"Premium #v {GPR} pp#!: {PRI} pp from the rating and stability (as in the {RR}; of "
        f"them {PFX} pp for parity changes and suspended redemption, fading over 5 years, and {PDB} pp for debt over 25% "
        f"of GDP and a chronic deficit), scaled by #v {GCO}%#! for the "
        "country's rank, companies and technologies (at most halved or doubled). Never under the key rate."
    ),
    "zz_ef_rate_box_policy": "Discretionary adjustment",
    "zz_ef_rate_box_policy_value": f"{BIAS} pp",
    "zz_ef_rate_box_policy_tt": (
        f"{DA}: #v {BIAS} pp#!\\n\\n"
        "The − and + buttons under the rate: each press moves the rate by 0.5 pp at once, and the central bank "
        f"does not walk it back. At most ±2 pp in total. The {RR} does not change with the adjustment."
    ),
    "zz_ef_rate_tt_increase_desc": (
        "#b Raise the key rate#!\\n"
        f"The {KR} rises by 0.5 pp at once: the {DA} goes 0.5 pp up, and the central bank will not walk the rate "
        f"back to the rule. Adjustment now: {BIAS} pp of the allowed ±2."
    ),
    "zz_ef_rate_tt_reduce_desc": (
        "#b Cut the key rate#!\\n"
        f"The {KR} falls by 0.5 pp at once: the {DA} goes 0.5 pp down, and the central bank will not walk the rate "
        f"back to the rule. Adjustment now: {BIAS} pp of the allowed ±2."
    ),
    "zz_ef_rate_tt_effect_up": "Key rate: #P +0.5 pp#!, discretionary adjustment: +0.5 pp",
    "zz_ef_rate_tt_effect_down": "Key rate: #P −0.5 pp#!, discretionary adjustment: −0.5 pp",
    "zz_ef_rate_tt_conditions": "\\n\\n#b Requirements and effect:#!\\n",
    "zz_ef_rate_tt_below_max": "Key rate below the corridor ceiling (12% on metal, 25% on fiat)",
    "zz_ef_rate_tt_above_min": "Key rate above 0.5%",
    "zz_ef_rate_tt_bias_up": f"Discretionary adjustment below +2 pp (now {BIAS})",
    "zz_ef_rate_tt_bias_down": f"Discretionary adjustment above −2 pp (now {BIAS})",
    "zz_ef_rate_tt_no_devaluation": f"The {DEVAL} law is not in force",
    "zz_ef_rate_tt_no_revaluation": f"The {REVAL} law is not in force",
    "zz_ef_rate_tt_no_fx_controls": f"No {FXC} modifier",
    "zz_ef_rate_private_construction": "Key rate: private construction",
    "zz_ef_rate_private_construction_desc": (
        f"A {KR} below 6.5% raises the private sector's share of construction points, above it lowers it: "
        "5 pp of share per percent of rate, at most ±30."
    ),
    "zz_ef_business_cash": "Money supply: business cash",
    "zz_ef_business_cash_desc": (
        "Obsolete: the buildings' cash cap is in the country's base values now. Removed at the start of a month."
    ),
    "zz_ef_debt_service": "Business loan repayment",
    "zz_ef_debt_service_desc": (
        "The buildings' contributions to the investment pool do not cover the week's payment on the businesses' "
        "bank credit (1/260 of the debt + interest): owners put a larger share of their income into the pool "
        "instead of dividends. Grows by 0.01 a week while short, falls when the contributions cover the payment "
        "with 20% to spare."
    ),
}
assert set(RU) == set(EN)

FILES = "(gui/00_00_ef_cb_rate_panel.gui, common/scripted_guis/zz_ef_cb_rate_buttons.txt,\n # common/game_concepts/zz_ef_cb_rate_concepts.txt, common/static_modifiers/zz_ef_rate_private_construction.txt)\n # GENERATED by tools/regen_ef_cb_rate_loc.py -- do not edit by hand"
HEADER = {
    "russian": f" # EF.30: ключевая ставка — показатели центробанка, подсказки кнопок, понятия\n # {FILES}.\n\n",
}
for lang in LANGS:
    d = RU if lang == "russian" else EN
    head = HEADER.get(lang, f" # EF.30: key rate -- central bank boxes, button tooltips, concepts\n # {FILES}.\n"
                            + ("" if lang == "english" else " # Not translated yet: English text.\n") + "\n")
    lines = [f"l_{lang}:\n", "\n", head]
    for k, v in d.items():
        assert '"' not in v.replace('\\"', ''), k
        lines.append(f' {k}:0 "{v}"\n')
    path = os.path.join(ROOT, lang, f"zz_ef_cb_rate_panel_l_{lang}.yml")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write("".join(lines))
    os.replace(tmp, path)
print("ok", len(RU), "keys x", len(LANGS))
