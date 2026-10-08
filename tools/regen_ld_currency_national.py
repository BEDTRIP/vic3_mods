"""Национальные валюты форка «E&F: Ledgerdemain» (R3а, пользователь 8.10): у страны без своей валюты (нет закона
валюты и валюты по культуре E&F — `var:zz_ef_cur` не задан) — название по наследию её основной культуры: у наследия
(как правило — языковая группа) историческое название денег (марка, франк, рубль, лян, рупия, песо…) + прилагательное
страны.

    python3 tools/regen_ld_currency_national.py [--check]

Порядок (пользователь 8.10): своё слово культуры (`CULTURE`: украинцы — гривна…), иначе языка (`LANGUAGE`), иначе
наследия (`HERITAGE`, слово для каждого из 110). Данные игры — `tools/data/vic3_heritages.json`,
`tools/data/vic3_cultures.json` (культуры 1.13 с наследием и языком; снимки с ПК). Слова — `NOUNS` (англ., рус.).

Пишет в форк:
- `common/scripted_effects/ld_currency_national.txt` — `zz_ef_cur_noun_set`: `var:zz_ef_cur_noun` = `flag:<слово>` по
  основной культуре: культура (`this = cu:X`), язык, наследие (`has_discrimination_trait`), первая подходящая группа; зовёт `zz_ef_cur_set`, когда своей валюты нет; лог `EFM|…|cur_nat`;
- `localization/{english,russian}/ld_currency_national_l_*.yml` — `zz_ef_cur_nat_<слово>` (англ.: «Bavarian mark»,
  рус.: «марка (Бавария)» — слово с прилагательным по роду не согласовать) и `zz_ef_cur_noun_<слово>`.
Ветки `currency_name` — `tools/regen_ld_currency_data.py` (берёт `NOUNS` отсюда). После правки английского —
`ld_loc_langs.py`. `--check` — только сравнить, код выхода 1 при расхождениях.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ld_gen  # noqa: E402
import ld_pdx  # noqa: E402

FORK = ld_gen.FORK
CHECK = ld_gen.CHECK
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "vic3_heritages.json")
CULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "vic3_cultures.json")
EFF = "common/scripted_effects/ld_currency_national.txt"
OLD = ("common/scripted_triggers/ld_currency_national_triggers.txt",)  # прежний вариант — по региону столицы
LOC = "localization/{0}/ld_currency_national_l_{0}.yml"

NOUNS = {
    "pound": ("pound", "фунт"), "franc": ("franc", "франк"), "guilder": ("guilder", "гульден"),
    "mark": ("mark", "марка"), "real": ("real", "реал"), "lira": ("lira", "лира"), "krona": ("krona", "крона"),
    "ruble": ("ruble", "рубль"), "zloty": ("zloty", "злотый"), "dinar": ("dinar", "динар"), "leu": ("leu", "лей"),
    "forint": ("forint", "форинт"), "drachma": ("drachma", "драхма"), "thaler": ("thaler", "талер"),
    "piastre": ("piastre", "пиастр"), "dirham": ("dirham", "дирхам"), "riyal": ("riyal", "риал"),
    "toman": ("toman", "туман"), "abazi": ("abazi", "абаз"), "dram": ("dram", "драм"), "tenge": ("tenge", "тенге"),
    "tugrik": ("tugrik", "тугрик"), "tangka": ("tangka", "танка"), "rupee": ("rupee", "рупия"),
    "kyat": ("kyat", "кьят"), "tical": ("tical", "тикаль"), "kip": ("kip", "кип"), "riel": ("riel", "риель"),
    "dong": ("dong", "донг"), "tael": ("tael", "лян"), "yen": ("yen", "иена"), "won": ("won", "вона"),
    "talari": ("talari", "талари"), "shilling": ("shilling", "шиллинг"), "cowrie": ("cowrie", "каури"),
    "dollar": ("dollar", "доллар"), "peso": ("peso", "песо"),
    "hryvnia": ("hryvnia", "гривна"), "koruna": ("koruna", "крона"), "litas": ("litas", "лит"), "lats": ("lats", "лат"),
    "kroon": ("kroon", "крона"), "manat": ("manat", "манат"), "markka": ("markka", "марка"), "lev": ("lev", "лев"),
    "lek": ("lek", "лек"), "taka": ("taka", "така"), "ringgit": ("ringgit", "ринггит"), "tolar": ("tolar", "толар"),
}
# сначала культура (у украинцев язык общий с русскими — гривну иначе не отличить), затем язык, затем наследие;
# испанский и английский языки здесь не стоят — у Мексики и США решает наследие (песо, доллар)
CULTURE = {
    "ukrainian": "hryvnia", "czech": "koruna", "slovak": "koruna", "lithuanian": "litas", "latvian": "lats",
    "estonian": "kroon", "azerbaijani": "manat",
}
LANGUAGE = {
    "finnic": "markka", "bulgarian": "lev", "albanian": "lek", "magadhan": "taka", "malay": "ringgit",
    "slovene": "tolar",
}
HERITAGE = {
    # Европа
    "british": "pound", "insular": "pound", "gallic": "franc", "netherlandish": "guilder", "germanic": "mark",
    "iberian": "real", "italic": "lira", "nordic": "krona", "sami": "krona", "baltic": "thaler", "east_slavic": "ruble",
    "west_slavic": "zloty", "south_slavic": "dinar", "romanian": "leu", "magyar": "forint", "greek": "drachma",
    "albanian": "piastre", "ashkenazi": "ruble", "sephardic": "piastre", "volga_uralic": "ruble", "tatar": "ruble",
    "siberian": "ruble", "circumpolar": "ruble", "promethean": "dollar",
    # Ближний Восток, Кавказ, Средняя Азия
    "anatolian": "piastre", "arab": "dirham", "syriac": "piastre", "kurdish": "piastre", "armenian": "dram",
    "georgian": "abazi", "caucasian": "abazi", "north_caucasian": "abazi", "persian": "toman", "iranian": "toman",
    "tajik": "tenge", "uzbek": "tenge", "turkmen": "tenge", "kipchak": "tenge", "uighur": "tenge", "afghan": "rupee",
    "hazaran": "rupee", "baluchi": "rupee", "mongolian": "tugrik", "tibetan": "tangka",
    # Южная и Юго-Восточная Азия
    "gangetic": "rupee", "rajasthani": "rupee", "gujarati": "rupee", "deccani": "rupee", "carnatic": "rupee",
    "southeast_indian": "rupee", "indusine": "rupee", "kashmiri": "rupee", "assamese": "rupee", "himalayan": "rupee",
    "burmese": "kyat", "tai": "tical", "khmu": "kip", "cambodian": "riel", "vietnamese": "dong",
    "insulindian": "guilder", "formosan": "tael",
    # Восточная Азия
    "han": "tael", "manchu": "tael", "miao": "tael", "yi": "tael", "zhuang": "tael", "japanese": "yen", "ainu": "yen",
    "korean": "won",
    # Африка
    "berber": "dirham", "afro_arab": "riyal", "somali": "riyal", "abyssinian": "talari", "eastern_highlands": "talari",
    "darfurian": "piastre", "kordofanian": "piastre", "nilotic": "piastre", "east_african": "shilling",
    "eastern_bantu": "shilling", "sahelian": "cowrie", "atlantic": "cowrie", "guinean": "cowrie", "central": "cowrie",
    "congolese": "cowrie", "southwest_bantu": "real", "southern_bantu": "pound", "khoisan": "pound",
    "african_settler": "pound", "african_diaspora": "dollar",
    # Америка и Океания
    "north_american_settler": "dollar", "eastern_woodlands_indian": "dollar", "plains_indian": "dollar",
    "plateau_indian": "dollar", "great_basin_indian": "dollar", "californian_indian": "dollar",
    "northwest_coast_indian": "dollar", "subarctic_indian": "dollar", "southwest_indian": "dollar",
    "caribbean": "dollar", "latin_american_settler": "peso", "mesoamerican": "peso", "andean": "peso",
    "guarani": "peso", "patagonian": "peso", "amazonian": "real", "australian": "pound", "oceanic_settler": "pound",
    "melanesian": "pound", "micronesian": "dollar", "polynesian": "dollar",
}

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


def groups():
    """[(уровень, слово, ключи)] по порядку проверки: культура, язык, наследие."""
    her = json.load(open(DATA, encoding="utf-8"))["heritages"]
    cul = json.load(open(CULT, encoding="utf-8"))["cultures"]
    langs = {c["language"] for c in cul.values() if c["language"]}
    names = [h[len("heritage_"):] for h in her]
    missing = [h for h in names if h not in HERITAGE]
    extra = [h for h in HERITAGE if h not in names] + [c for c in CULTURE if c not in cul] + \
        [l for l in LANGUAGE if "language_" + l not in langs]
    bad = [n for n in list(HERITAGE.values()) + list(CULTURE.values()) + list(LANGUAGE.values()) if n not in NOUNS]
    if missing or extra or bad:
        raise SystemExit(f"heritages without a word: {missing}; not in the game: {extra}; unknown words: {bad}")
    out = []
    for tier, table in (("culture", CULTURE), ("language", LANGUAGE), ("heritage", {h: HERITAGE[h] for h in names})):
        by = {}
        for k, n in table.items():
            by.setdefault(n, []).append(k)
        out += [(tier, n, ks) for n, ks in by.items()]
    return out


def nouns_used(gr):
    seen = []
    for _, n, _ in gr:
        if n not in seen:
            seen.append(n)
    return seen


def eff_text(gr):
    L = ["# GENERATED by tools/regen_ld_currency_national.py (vic3_mods) -- do not edit by hand.",
         "# R3а (the user, 8.10): a country without its own currency (no currency law, no E&F currency by culture --",
         "# zz_ef_cur_set) gets a national one: var:zz_ef_cur_noun = flag:<word>, the historical name of money of its primary",
         "# cultures: their own word, else their language's, else their heritage's; its name -- currency_name, «<adjective> <word>».",
         "zz_ef_cur_noun_set = {"]
    first = True
    for tier, n, ks in gr:
        if tier == "culture":
            cond = " ".join(f"this = cu:{k}" for k in ks)
        else:
            cond = " ".join(f"has_discrimination_trait = {tier}_{k}" for k in ks)
        # a culture's or language's own word -- only if all the primary cultures have it (Russia with Ukrainians as a
        # primary culture is not on the hryvnia); a heritage -- any primary culture, the first group
        cnt = "count = all " if tier != "heritage" else ""
        L.append(f"\t{'if' if first else 'else_if'} = {{ limit = {{ any_primary_culture = {{ {cnt}OR = {{ {cond} }} }} }} "
                 f"set_variable = {{ name = zz_ef_cur_noun value = flag:{n} }} }}")
        first = False
    L.append("\telse_if = { limit = { has_variable = zz_ef_cur_noun } remove_variable = zz_ef_cur_noun }")
    L.append("\tif = { limit = { zz_ef_logs_on = yes has_variable = zz_ef_cur_noun } debug_log = \"EFM|[TimeKeeper.GetCurrentDate.GetString]|"
             "[THIS.GetCountry.GetNameNoFormatting]|cur_nat|[THIS.GetCountry.GetCustom('currency_name')]\" }")
    L.append("}")
    return "\n".join(L) + "\n"


def loc_text(lang, gr):
    L = [f"l_{lang}:"]
    for n in nouns_used(gr):
        en, ru = NOUNS[n]
        if lang == "russian":
            L.append(f' zz_ef_cur_nat_{n}:0 "{ru} ([ROOT.GetCountry.GetNameNoFormatting])"')
            L.append(f' zz_ef_cur_noun_{n}:0 "{ru}"')
        else:
            L.append(f' zz_ef_cur_nat_{n}:0 "[ROOT.GetCountry.GetAdjectiveNoFormatting] {en}"')
            L.append(f' zz_ef_cur_noun_{n}:0 "{en}"')
    return "\n".join(L) + "\n"


def main():
    gr = groups()
    put(EFF, eff_text(gr))
    for lang in ("english", "russian"):
        put(LOC.format(lang), loc_text(lang, gr))
    for rel in OLD:
        if os.path.exists(os.path.join(FORK, rel)):
            _changed.append(rel + " (удалить)")
            if not CHECK:
                os.remove(os.path.join(FORK, rel))
    print("regen_ld_currency_national: " + ", ".join(f"{t[0]}:{n} {len(ks)}" for t, n, ks in gr))
    for x in _changed:
        print(f"  {'differs' if CHECK else 'written'}: {x}")
    if CHECK and _changed:
        sys.exit(1)


if __name__ == "__main__":
    main()
