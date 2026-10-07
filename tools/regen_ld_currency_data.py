"""Данные валют форка «E&F: Ledgerdemain» (R1б.2): переменная валюты страны и таблица 95 валют.

    python3 tools/regen_ld_currency_data.py [--check]

Источник — сам форк: законы `common/laws/01_ef_currency_type.txt` (95 законов `law_<cur>_currency`), история E&F
`common/history/global/99_ef_history_global_variable.txt` (у кого какая валюта, стандарт и паритет на 1836), названия и
символы `localization/<язык>/01_ef_currency_name_localization_l_<язык>.yml` (`<cur>`, `<cur>_texture`).

Пишет:
- в законах — `on_activate` каждого закона валюты: `var:zz_ef_cur` = `flag:<cur>`; у `law_no_market_liquidity` —
  `zz_ef_cur_set` (валюта по культуре);
- `common/scripted_effects/ld_currency_var.txt` — `zz_ef_cur_set`: закон валюты → флаг, нет закона — валюта по культуре
  E&F (`currency_identifiers_<cur>`), нет и её — переменной нет (общий символ);
- в `common/customizable_localization/00_ef_localization_ custom.txt` — тела `currency_name`, `currency_symbol`,
  `currency_symbol_generic` и `currency_symbol_<cur>` (топбар): чтение `var:zz_ef_cur` вместо проверок культуры (было
  5,3 с в профиле R0.7);
- `common/script_values/ld_currency_values.txt` — `zz_ef_fx_gold_<cur>`: единица валюты в резервах ЦБ в золоте по
  деньгам движка (стоимость E&F / паритет эмитента в золоте, `zz_ef_cur_par_update`); в
  `common/script_values/ld_fx_reserves_values.txt` (`zz_ef_fx_reserves_metal`) — `money_value_<cur>` → `zz_ef_fx_gold_<cur>`;
- `docs/currency-table.md` — таблица: ключ, название (англ., рус.), символ, ISO, страны и паритет на 1836.

ISO — справочник ниже (для исторических валют без кода — «—»). `--check` — только сравнить, код выхода 1 при расхождениях.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ld_gen  # noqa: E402
import ld_pdx  # noqa: E402

FORK = ld_gen.FORK
CHECK = ld_gen.CHECK
LAWS = "common/laws/01_ef_currency_type.txt"
HIST = "common/history/global/99_ef_history_global_variable.txt"
CUSTOM = "common/customizable_localization/00_ef_localization_ custom.txt"
VAR_FILE = "common/scripted_effects/ld_currency_var.txt"
TABLE = "docs/currency-table.md"
VALUES = "common/script_values/ld_currency_values.txt"
FX = "common/script_values/ld_fx_reserves_values.txt"
NAMES = "localization/{0}/01_ef_currency_name_localization_l_{0}.yml"

ISO = {
    "pound_sterling": "GBP", "franc_french_franc": "FRF", "franc_swiss_franc": "CHF", "franc_belgian_franc": "BEF",
    "franc_luxembourgish_franc": "LUF", "dollar_united_states_dollar": "USD", "dollar_canadian_dollar": "CAD",
    "dollar_australian_dollar": "AUD", "dollar_new_zealand_dollar": "NZD", "dollar_liberian_dollar": "LRD",
    "dollar_sierra_leonean_dollar": "SLL", "gulden_florin": "NLG", "gulden_hungarian_forint": "HUF",
    "gulden_indies_guilder": "—", "krone_danish_krone": "DKK", "krone_swedish_krona": "SEK", "krone_norwegian_krone": "NOK",
    "krone_icelandic_krona": "ISK", "krone_czech_koruna": "CSK", "krone_slovak_koruna": "SKK", "krone_estonian_kroon": "EEK",
    "leon_leu": "ROL", "leon_lev": "BGL", "lira": "ITL", "spe_peseta": "ESP", "spe_ruble": "RUB", "spe_yen": "JPY",
    "spe_yuan": "CNY", "spe_zloti": "PLZ", "spe_lithuanian_litas": "LTL", "spe_baht": "THB", "spe_korean_won": "KRW",
    "dinar_serbian_dinar": "RSD", "dinar_yugoslav_dinar": "YUD", "dinar_algerian_dinar": "DZD", "dinar_iraqi_dinar": "IQD",
    "dinar_libyan_dinar": "LYD", "dinar_moroccan_dirham": "MAD", "dinar_omanian_rial": "OMR", "dinar_saudi_riyal": "SAR",
    "dinar_tunisian_dinar": "TND", "dinar_qiran": "IRR", "eco_ethiopian_birr": "ETB", "eco_south_african_rand": "ZAR",
    "eco_nigerian_naira": "NGN", "eco_ghanaian_pound": "GHS", "eco_ariary": "MGA", "eco_west_african_eco": "XOF",
    "eco_central_african_eco": "XAF", "pound_egyptian_pound": "EGP", "peso_mexican_peso": "MXN", "peso": "—",
    "peso_argentine_peso": "ARS", "peso_chilean_peso": "CLP", "peso_colombian_peso": "COP", "peso_philippine_peso": "PHP",
    "peso_venezuelan_peso": "VEB", "peso_guatemalan_quetzal": "GTQ", "real_brazilian_real": "BRL", "rupee_indian_rupee": "INR",
    "lira_ottoman_lira": "TRL",
}


def read(rel):
    return ld_pdx.read(os.path.join(FORK, rel))


def currencies():
    src, _, _ = read(LAWS)
    return re.findall(r"^law_([a-z_]+)_currency = \{", src, re.M)


def history():
    """{cur: [(tag, standard, parity)]} -- the start's currency laws in E&F's history."""
    src, _, _ = read(HIST)
    out = {}
    for m in re.finditer(r"c:([A-Z0-9]{3}) \?= this\s*\}(.*?)(?=\n\t\tif = \{|\Z)", src, re.S):
        tag, body = m.group(1), m.group(2)
        cur = re.search(r"activate_law = law_type:law_([a-z_]+)_currency\b", body)
        if not cur:
            continue
        std = re.search(r"activate_law = law_type:law_([a-z]+)_standard\b", body)
        par = re.search(r"name = money_value_target_1\s*value = ([0-9.]+)", body)
        out.setdefault(cur.group(1), []).append((tag, std.group(1) if std else "", par.group(1) if par else ""))
    return out


def names(lang):
    src, _, _ = read(NAMES.format(lang))
    return dict(re.findall(r'^\s+([a-z_]+):\d*\s+"(.*)"', src, re.M))


_changed = []


def put_file(rel, text):
    dst = os.path.join(FORK, rel)
    old = ld_pdx.read(dst)[0] if os.path.exists(dst) else None
    if old is not None and old.replace("\r\n", "\n").lstrip("﻿") == text:
        return
    _changed.append(rel)
    if not CHECK:
        ld_pdx.write(dst, text, bom=rel.endswith(".txt"), eol="\n")


def laws_text(curs):
    src, bom, eol = read(LAWS)
    out = src
    for c in curs:
        pat = re.compile(r"(\nlaw_%s_currency = \{.*?\n    on_activate = \{)(.*?)(\n    \})" % re.escape(c), re.S)
        body = "\n        # R1б.2: the country's currency (zz_ef_cur, scripted_effects/ld_currency_var.txt)\n" \
               f"        set_variable = {{ name = zz_ef_cur value = flag:{c} }}"
        out, n = pat.subn(lambda m: m.group(1) + body + m.group(3), out, count=1)
        if n != 1:
            raise SystemExit(f"law_{c}_currency: no on_activate")
    pat = re.compile(r"(\nlaw_no_market_liquidity = \{.*?\n\tprogressiveness = 0\n)(.*?)(^\}\n)", re.S | re.M)
    body = "\t# R1б.2: no currency law -- the currency by culture (zz_ef_cur_set)\n\ton_activate = {\n\t\tzz_ef_cur_set = yes\n\t}\n"
    out, n = pat.subn(lambda m: m.group(1) + body + m.group(3), out, count=1)
    if n != 1:
        raise SystemExit("law_no_market_liquidity: not found")
    return src, out, bom, eol


def var_text(curs):
    L = ["﻿# GENERATED by tools/regen_ld_currency_data.py (vic3_mods) -- do not edit by hand.",
         "# R1б.2: the country's currency as data -- var:zz_ef_cur = flag:<cur> (the law, else E&F's currency by culture,",
         "# currency_identifiers_<cur>; none -- no var, the generic symbol). Set by the currency laws' on_activate, at the",
         "# country's first step and every January (zz_ef_money_model_step, zz_ef_money_model_monthly_step); read by",
         "# currency_name / currency_symbol (customizable localization). Table: docs/currency-table.md.",
         "zz_ef_cur_set = {"]
    first = True
    for c in curs:
        L.append(f"\t{'if' if first else 'else_if'} = {{ limit = {{ has_law = law_type:law_{c}_currency }} "
                 f"set_variable = {{ name = zz_ef_cur value = flag:{c} }} }}")
        first = False
    for c in curs:
        L.append(f"\telse_if = {{ limit = {{ currency_identifiers_{c} = 1 }} set_variable = {{ name = zz_ef_cur value = flag:{c} }} }}")
    L.append("\telse_if = { limit = { has_variable = zz_ef_cur } remove_variable = zz_ef_cur }")
    L.append("\tzz_ef_cur_par_update = yes")
    L.append("}")
    L += ["",
          "# R1б.1 (Д.1): the issuer's parity in gold, per currency (global_var:zz_ef_fxpar_<cur>), for the value of a currency",
          "# held in other CBs' reserves in the engine's money (zz_ef_fx_gold_<cur>, script_values/ld_currency_values.txt):",
          "# E&F's value of the currency (money_value_<cur>, gold per national unit) / this = gold per unit of the engine's",
          "# money. A CB on a metal standard with a currency law; monthly (zz_ef_money_model_monthly_step) and with zz_ef_cur_set.",
          "zz_ef_cur_par_update = {",
          "\tif = {",
          "\t\tlimit = { zz_ef_cb_metal_standard = yes has_variable = money_value_target_1 var:money_value_target_1 > 0 }"]
    first = True
    for c in curs:
        L.append(f"\t\t{'if' if first else 'else_if'} = {{ limit = {{ has_law = law_type:law_{c}_currency }} "
                 f"set_global_variable = {{ name = zz_ef_fxpar_{c} value = zz_ef_parity_gold }} }}")
        first = False
    L += ["\t}", "}"]
    return "\n".join(L) + "\n"


def values_text(curs):
    L = ["# GENERATED by tools/regen_ld_currency_data.py (vic3_mods) -- do not edit by hand.",
         "# R1б.1 (Д.1): a unit of a currency held in a CB's reserves (E&F's stockpiling_<cur>_state_1 -- our trims and the",
         "# deposits count it in the engine's money), in gold: E&F's value of the currency / its issuer's parity in gold",
         "# (global_var:zz_ef_fxpar_<cur>, scripted_effects/ld_currency_var.txt) -- about 1 (the value's band, +-2%) for a",
         "# metal standard; a fiat currency -- E&F's value as it is. Read by zz_ef_fx_reserves_metal (ld_fx_reserves_values.txt).",
         "# The issuer's parity in gold: a silver standard's parity is in silver.",
         "zz_ef_parity_gold = {", "\tvalue = var:money_value_target_1",
         "\tif = { limit = { has_law = law_type:law_silver_standard } multiply = silver_to_gold_rate }", "}"]
    for c in curs:
        L += [f"zz_ef_fx_gold_{c} = {{", f"\tvalue = money_value_{c}",
              f"\tif = {{ limit = {{ has_global_variable = zz_ef_fxpar_{c} global_var:zz_ef_fxpar_{c} > 0 }} divide = global_var:zz_ef_fxpar_{c} }}",
              "}"]
    return "\n".join(L) + "\n"


def fx_text(curs):
    src, bom, eol = read(FX)
    out = src
    for c in curs:
        out = out.replace(f"multiply = money_value_{c} min = 0", f"multiply = zz_ef_fx_gold_{c} min = 0")
    return src, out, bom, eol


def custom_text(curs):
    def one(key, suffix):
        L = [f"{key} = {{", "\ttype = country", "\tlog_loc_errors = no", "",
             "\t# R1б.2: the country's currency from var:zz_ef_cur (scripted_effects/ld_currency_var.txt); was 95 checks of",
             "\t# E&F's currency by culture per call", "\t#generic", "\ttext = {",
             "\t\ttrigger = { NOT = { has_variable = zz_ef_cur } }", f"\t\tlocalization_key = spe_uni{suffix}", "\t}"]
        for c in curs:
            L += [f"\t#{c}", "\ttext = {", f"\t\ttrigger = {{ var:zz_ef_cur ?= flag:{c} }}",
                  f"\t\tlocalization_key = {c}{suffix}", "\t}"]
        L.append("}")
        return "\n".join(L)
    # the top bar's symbol (currency_symbol_top_bar: 96 textboxes, one per definition, every frame)
    T = ["currency_symbol_generic = {", "\ttype = country", "\tlog_loc_errors = no", "",
         "\t# R1б.2: no var:zz_ef_cur -- the generic symbol", "\ttext = {",
         "\t\ttrigger = { NOT = { has_variable = zz_ef_cur } }", "\t\tlocalization_key = spe_uni_texture", "\t}", "}"]
    for c in curs:
        T += [f"currency_symbol_{c} = {{", "\ttype = country", "\tlog_loc_errors = no", "", "\ttext = {",
              f"\t\ttrigger = {{ var:zz_ef_cur ?= flag:{c} }}", f"\t\tlocalization_key = {c}_texture", "\t}", "}"]
    return one("currency_name", "") + "\n" + one("currency_symbol", "_texture") + "\n" + "\n".join(T) + "\n"


def table_text(curs, hist, en, ru):
    L = ["# Таблица валют", "",
         "Сгенерирована `../vic3_mods/tools/regen_ld_currency_data.py` из законов, истории и локализации форка — руками не",
         "править. Переменная валюты страны — `var:zz_ef_cur` (`flag:<ключ>`), `docs/currencies.md`. Паритет — металл на",
         "национальную единицу из истории E&F на 1.1.1836 (курс между валютами и подписи; в деньгах движка не участвует, Д.1).",
         "", "| ключ | название | по-русски | символ | ISO | страны 1836: стандарт, паритет |", "| --- | --- | --- | --- | --- | --- |"]
    for c in curs:
        h = "; ".join(f"{t}: {s or '—'}, {p or '—'}" for t, s, p in hist.get(c, [])) or "—"
        L.append(f"| `{c}` | {en.get(c, '—')} | {ru.get(c, '—')} | `{c}_texture` | {ISO.get(c, '—')} | {h} |")
    return "\n".join(L) + "\n"


def main():
    curs = currencies()
    if len(curs) != 95:
        raise SystemExit(f"{len(curs)} currency laws, expected 95")
    src, laws, bom, eol = laws_text(curs)
    if src != laws:
        _changed.append(LAWS)
        if not CHECK:
            ld_pdx.write(os.path.join(FORK, LAWS), laws, bom=bom, eol=eol)
    put_file(VAR_FILE, var_text(curs).lstrip("﻿"))
    put_file(VALUES, values_text(curs))
    src, fx, bom, eol = fx_text(curs)
    if src != fx:
        _changed.append(FX)
        if not CHECK:
            ld_pdx.write(os.path.join(FORK, FX), fx, bom=bom, eol=eol)
    ld_gen.emit(CUSTOM, custom_text(curs))
    put_file(TABLE, table_text(curs, history(), names("english"), names("russian")))
    ld_gen.report("regen_ld_currency_data")
    for x in _changed:
        print(f"  {'differs' if CHECK else 'written'}: {x}")
    if CHECK and (_changed or ld_gen._stats["changed"]):
        sys.exit(1)


if __name__ == "__main__":
    main()
