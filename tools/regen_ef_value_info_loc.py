#!/usr/bin/env python3
"""
M.1 / UI.9 step 2 (the user, 4.10): the currency tooltip's E&F lines that contradict our model.

The currency tooltip (E&F's MONEY_VALUE_<standard>) is MONEY_VALUE_INFO_* + our MONEY_SUPPLY_DESC_*
(regen_ef_money_supply_loc.py) + NATIONAL_CAPACITY_DESC_* + metal prices + the modifier. In the
first and the third E&F showed three different "covers" side by side (В2.10: "share of gold
reserves 193M/359M (53.8%)", "metal cover limit 98.1M/52.8M £", ours "cover of M2 21%") and the
national capacity x 2.5 with the gold pledged abroad. Since M.1 / M.2 (4.10) there is one measure:
the reserves = the CB's metal + foreign currency in its reserves (in the standard's metal), the
cover = the reserves at parity / M2, the value = the parity while the cover is 25%+ (+-2% by the
cover), under 25% parity x cover / 40%.

Rewritten (metal standards, AI and player variants -- 6 + 6 keys):
  MONEY_VALUE_INFO_*      the value with inflation (E&F's first line, kept), the value, the parity,
                          the cover and the rule;
  NATIONAL_CAPACITY_DESC_* the reserves: metal, currency, total; the gold pledged abroad shown as
                          NOT a reserve.
Fiat, gold exchange and subjects keep E&F's text.

M.11 (4.10): INFLATION_BALANCE / _player -- E&F's breakdown under the inflation's title (consumer
goods, energy, "currency value change +7.93% (capped)", monetary policy) is the old formula and
does not add up to the title, which is ours (the consumer basket's price index, inflation_value
replaced). The breakdown goes; the title, our index and the money's growth stay. Our own breakdown --
UI.5, stage 6.

Writes _ef/ef hotfix 1.13/localization/<lang>/replace/zz_ef_value_info_replace_l_<lang>.yml
(RU and EN; the other languages get EN).

Usage:
    py tools/regen_ef_value_info_loc.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, r"..\_ef\ef hotfix 1.13\localization"))
LANGS = ["english", "russian", "braz_por", "french", "german", "japanese",
         "korean", "polish", "simp_chinese", "spanish", "turkish"]

# (key suffix of MONEY_VALUE_INFO_ / NATIONAL_CAPACITY_DESC_, data context, metal icon)
STANDARDS = [
    ("silver_standard", "Country", "@silver!"), ("bimetallism_standard", "Country", "@gold!"),
    ("gold_standard", "Country", "@gold!"),
    ("silver_Player", "GetPlayer", "@silver!"), ("bimetallism_Player", "GetPlayer", "@gold!"),
    ("gold_Player", "GetPlayer", "@gold!"),
]

# 4.10 (the user: "the tooltip is for the money supply and the rate"): the rate in two lines -- the value
# against the parity (bimetallism: also in silver), the cover and its rule in one line; the reserves block
# (NATIONAL_CAPACITY_DESC) is empty -- the CB's reserves are told once, on their line in the money supply.
TEXT = {
    "russian": {
        "info": ("#b Курс:#! #T 1 {sym}#! = #T [{c}.MakeScope.ScriptValue('money_value_0')|4]#! {m}{alt} — паритет "
                 "[{c}.MakeScope.ScriptValue('zz_ef_cb_valuation')|4] {m}; сила к эталону [{c}.MakeScope.ScriptValue('zz_ef_currency_strength')|2]\\n"
                 "Покрытие #T [{c}.MakeScope.ScriptValue('zz_ef_cb_cover')|%0]#! (норма 40%): от 25% — размен на металл, курс у паритета ±2%; "
                 "ниже — размен приостановлен, курс = паритет × покрытие / 40%\\n"
                 "С инфляцией: 1 {sym} = [{c}.MakeScope.ScriptValue('money_value_rapported_inflation')] {m} "
                 "([{c}.MakeScope.ScriptValue('inflation_value')|%|=-] @inflation!)\\n$TOOLTIP_DELIMITER$"),
        "alt": " = [{c}.MakeScope.ScriptValue('zz_ef_value_in_silver')|2] @silver!",
        "cap": "",
    },
    "english": {
        "info": ("#b Rate:#! #T 1 {sym}#! = #T [{c}.MakeScope.ScriptValue('money_value_0')|4]#! {m}{alt} — parity "
                 "[{c}.MakeScope.ScriptValue('zz_ef_cb_valuation')|4] {m}; strength against the reference [{c}.MakeScope.ScriptValue('zz_ef_currency_strength')|2]\\n"
                 "Cover #T [{c}.MakeScope.ScriptValue('zz_ef_cb_cover')|%0]#! (norm 40%): from 25% notes are redeemed in metal, the value "
                 "stays at the parity ±2%; under it redemption is suspended, value = parity × cover / 40%\\n"
                 "With inflation: 1 {sym} = [{c}.MakeScope.ScriptValue('money_value_rapported_inflation')] {m} "
                 "([{c}.MakeScope.ScriptValue('inflation_value')|%|=-] @inflation!)\\n$TOOLTIP_DELIMITER$"),
        "alt": " = [{c}.MakeScope.ScriptValue('zz_ef_value_in_silver')|2] @silver!",
        "cap": "",
    },
}


INFL = {
    "russian": ("Текущее: #n [{c}.MakeScope.ScriptValue('inflation_value')|%|=-]#! — рост цен потребительской корзины за год "
                "(индекс [{c}.MakeScope.ScriptValue('zz_ef_price_index')|1], 100 = цены 1836); для сравнения: рост M2 "
                "[{c}.MakeScope.ScriptValue('zz_ef_circ_growth_year')|%1=+], ВВП [{c}.MakeScope.ScriptValue('zz_ef_gdp_growth_year')|%1=+] за год.\\n"
                "Разложение E&F (товары, энергия, «изменение стоимости валюты») скрыто: оно считалось старой формулой и не "
                "складывалось в итог.\\n$TOOLTIP_DELIMITER$"),
    "english": ("Current: #n [{c}.MakeScope.ScriptValue('inflation_value')|%|=-]#! — the consumer basket's price growth over a year "
                "(index [{c}.MakeScope.ScriptValue('zz_ef_price_index')|1], 100 = 1836 prices); compare: M2 growth "
                "[{c}.MakeScope.ScriptValue('zz_ef_circ_growth_year')|%1=+], GDP [{c}.MakeScope.ScriptValue('zz_ef_gdp_growth_year')|%1=+] a year.\\n"
                "E&F's breakdown (goods, energy, \"currency value change\") is hidden: it was the old formula and did not add up "
                "to the total.\\n$TOOLTIP_DELIMITER$"),
}


def text_for(lang):
    t = TEXT["russian" if lang == "russian" else "english"]
    lines = [f"l_{lang}:"]
    for suffix, c, m in STANDARDS:
        sym = f"[{c}.GetCustom('currency_symbol')]"
        alt = t["alt"].format(c=c) if suffix.startswith("bimetallism") else ""
        lines.append(f' MONEY_VALUE_INFO_{suffix}:0 "{t["info"].format(c=c, m=m, sym=sym, alt=alt)}"')
        lines.append(f' NATIONAL_CAPACITY_DESC_{suffix}:0 "{t["cap"]}"')
    infl = INFL["russian" if lang == "russian" else "english"]
    lines.append(f' INFLATION_BALANCE:0 "{infl.format(c="Country")}"')
    lines.append(f' INFLATION_BALANCE_player:0 "{infl.format(c="GetPlayer")}"')
    return "\n".join(lines) + "\n"


def main():
    for lang in LANGS:
        d = os.path.join(ROOT, lang, "replace")
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, f"zz_ef_value_info_replace_l_{lang}.yml")
        with open(p, "w", encoding="utf-8-sig", newline="\n") as f:
            f.write(text_for(lang))
        print("ok", p)


if __name__ == "__main__":
    main()
