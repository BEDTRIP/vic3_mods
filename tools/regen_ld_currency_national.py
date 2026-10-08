"""Национальные валюты форка «E&F: Ledgerdemain» (R3а, пользователь 8.10): у страны без своей валюты (нет закона
валюты и валюты по культуре E&F — `var:zz_ef_cur` не задан) — название по стратегическому региону её столицы: слово
державы, которая исторически больше всего влияет на регион (песо, фунт, марка, франк, рубль, иена, лира…), +
прилагательное страны.

    python3 tools/regen_ld_currency_national.py [--check]

Данные игры — `tools/data/vic3_strategic_regions.json` (регионы 1.13 и их штаты; снимок с ПК). Таблица «слово →
регионы» — `NOUNS` ниже; крупный регион делится списком штатов (`SPLIT`: Британские острова — фунт, Нидерланды —
гульден, остальное «Западной Европы» — франк; Иберия — песета, остальное «Южной Европы» — лира).

Пишет в форк:
- `common/scripted_triggers/ld_currency_national_triggers.txt` — `zz_ef_cur_area_<слово>` (штат: его регион);
- `common/scripted_effects/ld_currency_national.txt` — `zz_ef_cur_noun_set`: `var:zz_ef_cur_noun` = `flag:<слово>` по
  штату столицы (зовёт `zz_ef_cur_set`, когда своей валюты нет);
- `localization/{english,russian}/ld_currency_national_l_*.yml` — `zz_ef_cur_nat_<слово>` (англ.: «Bavarian mark»,
  рус.: «марка (Бавария)» — слово с прилагательным по роду не согласовать) и `zz_ef_cur_noun_<слово>`.
Ветки `currency_name` — `tools/regen_ld_currency_data.py`. После правки английского — `ld_loc_langs.py`.
`--check` — только сравнить, код выхода 1 при расхождениях.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ld_gen  # noqa: E402
import ld_pdx  # noqa: E402

FORK = ld_gen.FORK
CHECK = ld_gen.CHECK
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "vic3_strategic_regions.json")
TRIG = "common/scripted_triggers/ld_currency_national_triggers.txt"
EFF = "common/scripted_effects/ld_currency_national.txt"
LOC = "localization/{0}/ld_currency_national_l_{0}.yml"

# слово: (англ., рус., регионы)
NOUNS = {
    "pound": ("pound", "фунт", ["region_oceania", "region_west_africa", "region_southern_africa"]),
    "franc": ("franc", "франк", ["region_equatorial_africa", "region_north_africa"]),
    "guilder": ("guilder", "гульден", ["region_indonesia"]),
    "mark": ("mark", "марка", ["region_central_europe"]),
    "peseta": ("peseta", "песета", []),
    "lira": ("lira", "лира", []),
    "krona": ("krona", "крона", ["region_northern_europe"]),
    "ruble": ("ruble", "рубль", ["region_russia", "region_siberia", "region_central_asia", "region_eastern_europe"]),
    "piastre": ("piastre", "пиастр", ["region_balkans", "region_near_east", "region_arabia", "region_nile_basin"]),
    "toman": ("toman", "туман", ["region_greater_persia"]),
    "rupee": ("rupee", "рупия", ["region_north_india", "region_south_india", "region_himalayas", "region_east_africa"]),
    "tical": ("tical", "тикаль", ["region_indochina"]),
    "tael": ("tael", "лян", ["region_north_china", "region_south_china"]),
    "yen": ("yen", "иена", ["region_northeast_asia"]),
    "dollar": ("dollar", "доллар", ["region_atlantic_coast", "region_great_plains", "region_pacific_coast", "region_canada"]),
    "peso": ("peso", "песо", ["region_central_america", "region_gran_colombia", "region_andes", "region_la_plata"]),
    "real": ("real", "реал", ["region_brazil"]),
}
# регион, который делится по державам: (регион, {слово: штаты}, слово для остальных штатов)
SPLIT = [
    ("region_western_europe", {
        "pound": "WALES MIDLANDS EAST_ANGLIA WEST_COUNTRY HOME_COUNTIES YORKSHIRE LANCASHIRE HIGHLANDS LOWLANDS ULSTER "
                 "LEINSTER CONNAUGHT MUNSTER",
        "guilder": "HOLLAND GELRE FRIESLAND",
    }, "franc"),
    ("region_southern_europe", {
        "peseta": "CATALONIA OLD_CASTILE BALEARIC_ISLANDS ARAGON BASQUE_COUNTRY GALICIA ASTURIAS BEIRA LOWER_ANDALUSIA "
                  "ALENTEJO EXTREMADURA NEW_CASTILE UPPER_ANDALUSIA VALENCIA ESTREMADURA CAPE_VERDE CANARY_ISLANDS "
                  "AZORES MADEIRA MURCIA LEON ENTRE_DOURO_E_MINHO",
    }, "lira"),
]

_changed = []


def put(rel, text, bom=True):
    dst = os.path.join(FORK, rel)
    old = ld_pdx.read(dst)[0] if os.path.exists(dst) else None
    if old is not None and old.replace("\r\n", "\n").lstrip("﻿") == text:
        return
    _changed.append(rel)
    if not CHECK:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        ld_pdx.write(dst, text, bom=bom, eol="\n")


def areas():
    data = json.load(open(DATA, encoding="utf-8"))
    reg = data["regions"]
    out = {n: [] for n in NOUNS}
    for n, (_, _, regions) in NOUNS.items():
        for r in regions:
            out[n] += reg[r]
    covered = {r for _, _, rs in NOUNS.values() for r in rs}
    for r, parts, rest in SPLIT:
        taken = set()
        for n, sts in parts.items():
            sts = ["STATE_" + s for s in sts.split()]
            out[n] += [s for s in sts if s in reg[r]]
            taken |= set(sts)
        out[rest] += [s for s in reg[r] if s not in taken]
        covered.add(r)
    missing = sorted(set(reg) - covered)
    if missing:
        raise SystemExit(f"regions without a currency word: {missing}")
    return {n: sorted(set(s)) for n, s in out.items()}, data


def trig_text(ar):
    L = ["# GENERATED by tools/regen_ld_currency_national.py (vic3_mods) -- do not edit by hand.",
         "# R3а (the user, 8.10): the national currency's word by the strategic region of the country's capital (state scope).",
         ""]
    for n, sts in ar.items():
        L.append(f"zz_ef_cur_area_{n} = {{")
        L.append("\tOR = {")
        for i in range(0, len(sts), 6):
            L.append("\t\t" + " ".join(f"state_region = s:{s}" for s in sts[i:i + 6]))
        L += ["\t}", "}"]
    return "\n".join(L) + "\n"


def eff_text(ar):
    L = ["# GENERATED by tools/regen_ld_currency_national.py (vic3_mods) -- do not edit by hand.",
         "# R3а (the user, 8.10): a country without its own currency (no currency law, no E&F currency by culture --",
         "# zz_ef_cur_set) gets a national one: var:zz_ef_cur_noun = flag:<word> by the region of its capital; its name --",
         "# currency_name (customizable localization), «<adjective> <word>».",
         "zz_ef_cur_noun_set = {"]
    first = True
    for n in ar:
        L.append(f"\t{'if' if first else 'else_if'} = {{ limit = {{ capital ?= {{ zz_ef_cur_area_{n} = yes }} }} "
                 f"set_variable = {{ name = zz_ef_cur_noun value = flag:{n} }} }}")
        first = False
    L.append("\telse_if = { limit = { has_variable = zz_ef_cur_noun } remove_variable = zz_ef_cur_noun }")
    L.append("\tif = { limit = { zz_ef_logs_on = yes has_variable = zz_ef_cur_noun } debug_log = \"EFM|[TimeKeeper.GetCurrentDate.GetString]|"
             "[THIS.GetCountry.GetNameNoFormatting]|cur_nat|[THIS.GetCountry.GetCustom('currency_name')]\" }")
    L.append("}")
    return "\n".join(L) + "\n"


def loc_text(lang):
    L = [f"l_{lang}:"]
    for n, (en, ru, _) in NOUNS.items():
        if lang == "russian":
            L.append(f' zz_ef_cur_nat_{n}:0 "{ru} ([ROOT.GetCountry.GetNameNoFormatting])"')
            L.append(f' zz_ef_cur_noun_{n}:0 "{ru}"')
        else:
            L.append(f' zz_ef_cur_nat_{n}:0 "[ROOT.GetCountry.GetAdjectiveNoFormatting] {en}"')
            L.append(f' zz_ef_cur_noun_{n}:0 "{en}"')
    return "\n".join(L) + "\n"


def main():
    ar, data = areas()
    put(TRIG, trig_text(ar))
    put(EFF, eff_text(ar))
    for lang in ("english", "russian"):
        put(LOC.format(lang), loc_text(lang))
    # countries of the 1.13 map by their capital's word (report only)
    st2n = {s: n for n, sts in ar.items() for s in sts}
    cnt = {}
    for t, c in data["capitals"].items():
        cnt[st2n.get(c, "?")] = cnt.get(st2n.get(c, "?"), 0) + 1
    print("regen_ld_currency_national: " + ", ".join(f"{n} {v}" for n, v in sorted(cnt.items(), key=lambda x: -x[1])))
    for x in _changed:
        print(f"  {'differs' if CHECK else 'written'}: {x}")
    if CHECK and _changed:
        sys.exit(1)


if __name__ == "__main__":
    main()
