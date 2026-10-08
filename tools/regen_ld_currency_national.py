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
- `localization/{english,russian}/ld_currency_national_l_*.yml` — `zz_ef_cur_nat_<слово>` для всех слов (национальных и
  `LAW_NOUN` — валют законов E&F): «<прилагательное эмитента> <слово>» (англ. «British pound», рус. «Британский фунт»:
  основа прилагательного игры + окончание по роду слова), и `zz_ef_cur_noun_<слово>`.
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

# слово: (англ., рус., род по-русски: m / f / n — окончание прилагательного страны «ий» / «ая» / «ое»; у прилагательного
# страны в русской локализации игры — только основа: «Австрийск»)
NOUNS = {
    "pound": ("pound", "фунт", "m"), "franc": ("franc", "франк", "m"), "guilder": ("guilder", "гульден", "m"),
    "gulden": ("gulden", "гульден", "m"), "florin": ("florin", "флорин", "m"),
    "mark": ("mark", "марка", "f"), "real": ("real", "реал", "m"), "lira": ("lira", "лира", "f"),
    "krona": ("krona", "крона", "f"), "krone": ("krone", "крона", "f"),
    "ruble": ("ruble", "рубль", "m"), "zloty": ("zloty", "злотый", "m"), "dinar": ("dinar", "динар", "m"),
    "leu": ("leu", "лей", "m"), "forint": ("forint", "форинт", "m"), "drachma": ("drachma", "драхма", "f"),
    "thaler": ("thaler", "талер", "m"), "piastre": ("piastre", "пиастр", "m"), "dirham": ("dirham", "дирхам", "m"),
    "riyal": ("riyal", "риал", "m"), "qiran": ("qiran", "киран", "m"), "toman": ("toman", "туман", "m"),
    "abazi": ("abazi", "абаз", "m"), "dram": ("dram", "драм", "m"), "tenge": ("tenge", "тенге", "m"),
    "tugrik": ("tugrik", "тугрик", "m"), "tangka": ("tangka", "танка", "f"), "rupee": ("rupee", "рупия", "f"),
    "rupiah": ("rupiah", "рупия", "f"), "kyat": ("kyat", "кьят", "m"), "tical": ("tical", "тикаль", "m"),
    "baht": ("baht", "бат", "m"), "kip": ("kip", "кип", "m"), "riel": ("riel", "риель", "m"),
    "dong": ("dong", "донг", "m"), "tael": ("tael", "лян", "m"), "yuan": ("yuan", "юань", "m"),
    "yen": ("yen", "иена", "f"), "won": ("won", "вона", "f"), "talari": ("talari", "талари", "m"),
    "birr": ("birr", "быр", "m"), "shilling": ("shilling", "шиллинг", "m"), "cowrie": ("cowrie", "каури", "f"),
    "rand": ("rand", "ранд", "m"), "naira": ("naira", "найра", "f"), "ariary": ("ariary", "ариари", "m"),
    "ouguiya": ("ouguiya", "угия", "f"), "eco": ("eco", "эко", "m"),
    "dollar": ("dollar", "доллар", "m"), "peso": ("peso", "песо", "n"), "colon": ("colon", "колон", "m"),
    "quetzal": ("quetzal", "кетсаль", "m"), "lempira": ("lempira", "лемпира", "f"),
    "cordoba": ("cordoba", "кордоба", "f"), "sol": ("sol", "соль", "m"), "peseta": ("peseta", "песета", "f"),
    "ducat": ("ducat", "дукат", "m"), "scudo": ("scudo", "скудо", "m"),
    "hryvnia": ("hryvnia", "гривна", "f"), "koruna": ("koruna", "крона", "f"), "litas": ("litas", "лит", "m"),
    "lats": ("lats", "лат", "m"), "kroon": ("kroon", "крона", "f"), "manat": ("manat", "манат", "m"),
    "markka": ("markka", "марка", "f"), "lev": ("lev", "лев", "m"), "lek": ("lek", "лек", "m"),
    "taka": ("taka", "така", "f"), "ringgit": ("ringgit", "ринггит", "m"), "tolar": ("tolar", "толар", "m"),
}
RU_END = {"m": "ий", "f": "ая", "n": "ое"}
# валюта закона E&F (var:zz_ef_cur = flag:<ключ>) → слово; название — «<прилагательное эмитента> <слово>» (пользователь
# 8.10: «русский рубль, британский фунт» — для всех). spe_uni (условная «уни») — без слова, название E&F.
LAW_NOUN = {
    "dinar": "dinar", "dinar_algerian_dinar": "dinar", "dinar_iraqi_dinar": "dinar", "dinar_libyan_dinar": "dinar",
    "dinar_moroccan_dirham": "dirham", "dinar_omanian_rial": "riyal", "dinar_qiran": "qiran",
    "dinar_saudi_riyal": "riyal", "dinar_serbian_dinar": "dinar", "dinar_tunisian_dinar": "dinar",
    "dinar_yugoslav_dinar": "dinar",
    "dollar_australian_dollar": "dollar", "dollar_canadian_dollar": "dollar", "dollar_caribbean_dollar": "dollar",
    "dollar_confederate_states_dollar": "dollar", "dollar_liberian_dollar": "dollar",
    "dollar_new_zealand_dollar": "dollar", "dollar_sierra_leonean_dollar": "dollar",
    "dollar_united_states_dollar": "dollar",
    "eco_ariary": "ariary", "eco_central_african_eco": "eco", "eco_east_african_eco": "eco",
    "eco_ethiopian_birr": "birr", "eco_ghanaian_pound": "pound", "eco_nigerian_naira": "naira",
    "eco_south_african_rand": "rand", "eco_tuareg_ouguiya": "ouguiya", "eco_west_african_eco": "eco",
    "franc_belgian_franc": "franc", "franc_french_franc": "franc", "franc_luxembourgish_franc": "franc",
    "franc_swiss_franc": "franc",
    "gulden": "gulden", "gulden_bavarian_gulden": "gulden", "gulden_florin": "florin",
    "gulden_hungarian_forint": "forint", "gulden_indies_guilder": "guilder", "gulden_south_german_gulden": "gulden",
    "krone_czech_koruna": "koruna", "krone_danish_krone": "krone", "krone_estonian_kroon": "kroon",
    "krone_icelandic_krona": "krona", "krone_norwegian_krone": "krone", "krone_slovak_koruna": "koruna",
    "krone_swedish_krona": "krona",
    "leon_leu": "leu", "leon_lev": "lev",
    "lira": "lira", "lira_ducato": "ducat", "lira_ottoman_lira": "lira", "lira_scudo_pontificio": "scudo",
    "lira_scudo_sardo": "scudo", "lira_toscane_lira": "lira",
    "mark": "mark", "mark_finnish_markka": "markka",
    "peso": "peso", "peso_argentine_peso": "peso", "peso_bolivien_peso": "peso", "peso_chilean_peso": "peso",
    "peso_colombian_peso": "peso", "peso_costa_rican_colon": "colon", "peso_cuban_peso": "peso",
    "peso_ecuadorian_peso": "peso", "peso_el_salvador_colon": "colon", "peso_guatemalan_quetzal": "quetzal",
    "peso_honduran_lempira": "lempira", "peso_mexican_peso": "peso", "peso_nicaraguan_cordoba": "cordoba",
    "peso_paraguayan_peso": "peso", "peso_philippine_peso": "peso", "peso_sol_de_oro": "sol",
    "peso_uruguayan_peso": "peso", "peso_venezuelan_peso": "peso",
    "pound_egyptian_pound": "pound", "pound_irish_pound": "pound", "pound_sterling": "pound",
    "real": "real", "real_brazilian_real": "real",
    "rupee_indian_rupee": "rupee", "rupee_indonesian_rupiah": "rupiah",
    "spe_baht": "baht", "spe_dong": "dong", "spe_drachma": "drachma", "spe_korean_won": "won",
    "spe_latvian_lats": "lats", "spe_lithuanian_litas": "litas", "spe_peseta": "peseta", "spe_ruble": "ruble",
    "spe_yen": "yen", "spe_yuan": "yuan", "spe_zloti": "zloty",
    "thaler_hannoveraner_thaler": "thaler", "thaler_prussian_thaler": "thaler", "thaler_saxon_thaler": "thaler",
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

# прилагательное эмитента валюты (var:zz_ef_cur_issuer — zz_ef_cur_name_set, ld_currency_var.txt)
ISSUER_ADJ = "ROOT.GetCountry.MakeScope.Var('zz_ef_cur_issuer').GetCountry.GetAdjectiveNoFormatting"

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
    bad = [n for n in list(HERITAGE.values()) + list(LAW_NOUN.values()) + list(CULTURE.values()) + list(LANGUAGE.values()) if n not in NOUNS]
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
    """Слова по порядку: национальные (по группам), затем слова законов E&F."""
    seen = []
    for n in [n for _, n, _ in gr] + list(LAW_NOUN.values()):
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
    L.append("}")
    return "\n".join(L) + "\n"


def loc_text(lang, gr):
    L = [f"l_{lang}:"]
    for n in nouns_used(gr):
        en, ru, g = NOUNS[n]
        if lang == "russian":
            L.append(f' zz_ef_cur_nat_{n}:0 "[{ISSUER_ADJ}]{RU_END[g]} {ru}"')
            L.append(f' zz_ef_cur_noun_{n}:0 "{ru}"')
        else:
            L.append(f' zz_ef_cur_nat_{n}:0 "[{ISSUER_ADJ}] {en}"')
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
