"""Символ валюты форка «E&F: Ledgerdemain» (R8а.7, Д.R8а.8): две буквы страны + знак слова — `CH ₣`, `GB £`, `RU ₽`.

    python3 tools/regen_ld_currency_symbol.py [--check]

Две буквы — ISO 3166-1 у страны, которая соответствует нынешней (`ISO`), иначе две буквы тега с разводом совпадений
(пары букв тега, затем первая буква тега или названия с буквой названия, затем первая буква тега с любой, затем любая
свободная пара, по кругу; сначала все страны с историей на 1836, потом остальные; ISO и выбранные раньше — заняты). Теги — снимок `tools/data/vic3_country_tags.json` (ваниль 1.13:
`common/country_definitions` с английскими названиями, `history_1836` — теги файлов `common/history/countries`).
Знак — по слову валюты (`var:zz_ef_cur_noun`, слова — `regen_ld_currency_national.py`): `SIGN`; нет знака — первые
буквы слова. Валюта закона со своим знаком, отличным от знака слова (турецкая лира ₺, филиппинское песо ₱), — `CUR_SIGN`.
Без денежной системы — `¤` (Д.R8а.2: своей валюты нет).

Движок (проба r1009_032419): `Country.GetTagName` — тег, `Localize(Concatenate('zz_ef_iso2_', тег))` — текст ключа; в тексте
custom loc `ROOT.GetCountry` — страна, у которой спрошен символ.

Пишет в форк:
- `localization/{english,russian}/ld_currency_symbol_l_*.yml` — `zz_ef_iso2_<тег>` (две буквы), `zz_ef_sym_<слово>`,
  `zz_ef_sym_cur_<валюта>`, `zz_ef_sym_none`, `zz_ef_sym_generic`: «[две буквы страны] <знак>»;
- в `common/customizable_localization/00_ef_localization_ custom.txt` — тело `currency_symbol`.
После правки английского — `ld_loc_langs.py`. `--check` — только сравнить, код выхода 1 при расхождениях.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ld_gen  # noqa: E402
from regen_ld_currency_national import groups as _national_groups, nouns_used as _national_nouns, LAW_NOUN  # noqa: E402

FORK = ld_gen.FORK
CHECK = ld_gen.CHECK
TAGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "vic3_country_tags.json")
CUSTOM = "common/customizable_localization/00_ef_localization_ custom.txt"
LOC = "localization/{0}/ld_currency_symbol_l_{0}.yml"

# тег ванили → ISO 3166-1 alpha-2 (страна, которая соответствует нынешней; у каждого кода — один тег)
ISO = {
    "AFG": "AF", "ALB": "AL", "ALD": "DZ", "ARG": "AR", "ARM": "AM", "AST": "AU", "AUS": "AT", "AZB": "AZ",
    "BAH": "BS", "BEL": "BE", "BEN": "BJ", "BHN": "BH", "BHU": "BT", "BOL": "BO", "BOS": "BA", "BRD": "BI",
    "BRU": "BN", "BRZ": "BR", "BST": "LS", "BUL": "BG", "BUR": "MM", "BYE": "BY", "CAM": "KH", "CAN": "CA",
    "CEY": "LK", "CHI": "CN", "CHL": "CL", "CLM": "CO", "CNG": "CG", "COS": "CR", "CRO": "HR", "CUB": "CU",
    "CYP": "CY", "CZH": "CZ", "DAI": "VN", "DEN": "DK", "DOM": "DO", "ECU": "EC", "EGY": "EG", "ELS": "SV",
    "EOT": "JO", "EST": "EE", "ETH": "ET", "FIN": "FI", "FJI": "FJ", "FRA": "FR", "GAM": "GM", "GBR": "GB",
    "GEO": "GE", "GER": "DE", "GLC": "GH", "GRE": "GR", "GRN": "GL", "GUA": "GT", "HAI": "HT", "HND": "IN",
    "HON": "HN", "HUN": "HU", "ICL": "IS", "IDN": "ID", "IRE": "IE", "IRQ": "IQ", "ISR": "IL", "ITA": "IT",
    "JAM": "JM", "JAP": "JP", "KAZ": "KZ", "KOR": "KR", "KYR": "KG", "LAO": "LA", "LAT": "LV", "LBY": "LY",
    "LEB": "LB", "LIB": "LR", "LIT": "LT", "LUX": "LU", "MAD": "MG", "MAL": "ML", "MEX": "MX", "MGL": "MN",
    "MLD": "MV", "MLT": "MT", "MOL": "MD", "MON": "ME", "MOR": "MA", "NEP": "NP", "NET": "NL", "NIC": "NI",
    "NOR": "NO", "NRU": "NR", "NZL": "NZ", "OMA": "OM", "PAK": "PK", "PAL": "PS", "PAP": "VA", "PCO": "PR",
    "PER": "IR", "PEU": "PE", "PHI": "PH", "PNM": "PA", "POL": "PL", "POR": "PT", "PRG": "PY", "ROM": "RO",
    "RUS": "RU", "RWD": "RW", "SAF": "ZA", "SAH": "EH", "SER": "RS", "SIA": "TH", "SIL": "SL", "SLO": "SI",
    "SLV": "SK", "SPA": "ES", "SUD": "SD", "SWE": "SE", "SWI": "CH", "SWZ": "SZ", "SYR": "SY", "TJI": "TJ",
    "TNG": "TO", "TRC": "TM", "TUN": "TN", "TUR": "TR", "UKR": "UA", "URU": "UY", "USA": "US", "UZB": "UZ",
    "VNT": "VU", "VNZ": "VE", "YEM": "YE", "ZAN": "TZ", "ZIM": "ZW",
}
# слово → знак (нет здесь — первые буквы слова: SIGN.get(n) or n[:1].upper())
SIGN = {
    "pound": "£", "franc": "₣", "guilder": "ƒ", "gulden": "ƒ", "florin": "ƒ", "mark": "ℳ", "real": "R$", "lira": "₤",
    "krona": "kr", "krone": "kr", "kroon": "kr", "ruble": "₽", "zloty": "zł", "forint": "Ft", "drachma": "₯",
    "tenge": "₸", "tugrik": "₮", "rupee": "₹", "rupiah": "Rp", "baht": "฿", "tical": "฿", "kip": "₭", "dong": "₫",
    "yuan": "¥", "yen": "¥", "won": "₩", "birr": "Br", "naira": "₦", "ariary": "Ar", "dollar": "$", "peso": "$",
    "colon": "₡", "cordoba": "C$", "sol": "S/", "peseta": "₧", "hryvnia": "₴", "koruna": "Kč", "litas": "Lt",
    "lats": "Ls", "manat": "₼", "markka": "mk", "lev": "лв", "ringgit": "RM", "taka": "Tk",
}
# валюта закона E&F со своим знаком (у слова — другой)
CUR_SIGN = {"lira_ottoman_lira": "₺", "peso_philippine_peso": "₱"}
NONE_SIGN = "¤"
ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def codes():
    data = json.load(open(TAGS, encoding="utf-8"))
    if len(set(ISO.values())) != len(ISO):
        raise SystemExit("ISO: один код у двух тегов")
    start = set(data["history_1836"])
    used = set(ISO.values())
    out = dict(ISO)
    # the countries with a history (on the map in 1836) first, then the rest; in each -- rounds: every tag its own
    # letters first, then letters of its name, then any
    order = sorted(data["tags"], key=lambda x: (x not in start, x))

    def rounds(t):
        name = "".join(ch for ch in data["tags"][t].upper() if "A" <= ch <= "Z")
        yield [t[0] + t[1], t[0] + t[2], t[1] + t[2], t[1] + t[0], t[2] + t[0], t[2] + t[1]]
        yield [t[0] + ch for ch in name[1:]] + [name[:1] + ch for ch in name[1:]]
        yield [t[0] + ch for ch in ABC]
        yield [x + y for x in ABC for y in ABC]
    gens = {t: list(rounds(t)) for t in order}
    for group in ([t for t in order if t in start], [t for t in order if t not in start]):
        for r in range(4):
            for t in group:
                if t in out:
                    continue
                pick = next((c for c in gens[t][r] if len(c) == 2 and c.isalpha() and c not in used), None)
                if pick:
                    out[t] = pick
                    used.add(pick)
    for t in order:
        out.setdefault(t, t[:2])
    return out


def sign_of(n):
    return SIGN.get(n) or n[:1].upper()


def loc_text(lang, iso, nouns):
    pre = "[Localize(Concatenate('zz_ef_iso2_', ROOT.GetCountry.GetTagName))] "
    L = [f"﻿l_{lang}:"]
    L += [f' zz_ef_iso2_{t}:0 "{c}"' for t, c in sorted(iso.items())]
    L.append(f' zz_ef_sym_none:0 "{pre}{NONE_SIGN}"')
    L.append(f' zz_ef_sym_generic:0 "{pre}{NONE_SIGN}"')
    L += [f' zz_ef_sym_{n}:0 "{pre}{sign_of(n)}"' for n in nouns]
    L += [f' zz_ef_sym_cur_{c}:0 "{pre}{s}"' for c, s in sorted(CUR_SIGN.items())]
    return "\n".join(L) + "\n"


def custom_text(nouns):
    L = ["currency_symbol = {", "\ttype = country", "\tlog_loc_errors = no", "",
         "\t# «<two letters of the country> <the sign of its currency's word>» (Д.R8а.8, tools/regen_ld_currency_symbol.py)",
         "\t#no monetary system", "\ttext = {", "\t\ttrigger = { has_law = law_type:law_no_monetary_system }",
         "\t\tlocalization_key = zz_ef_sym_none", "\t}"]
    for c in sorted(CUR_SIGN):
        L += [f"\t#{c}", "\ttext = {", f"\t\ttrigger = {{ var:zz_ef_cur ?= flag:{c} }}",
              f"\t\tlocalization_key = zz_ef_sym_cur_{c}", "\t}"]
    for n in nouns:
        L += [f"\t#{n}", "\ttext = {", f"\t\ttrigger = {{ var:zz_ef_cur_noun ?= flag:{n} }}",
              f"\t\tlocalization_key = zz_ef_sym_{n}", "\t}"]
    L += ["\t#generic", "\ttext = {", "\t\tlocalization_key = zz_ef_sym_generic", "\t}", "}"]
    return "\n".join(L) + "\n"


def put(rel, text):
    path = os.path.join(FORK, rel)
    old = open(path, encoding="utf-8").read() if os.path.exists(path) else None
    if old == text:
        ld_gen._stats["same"].append(rel)
        return
    ld_gen._stats["changed"].append(rel)
    if not CHECK:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)


def main():
    iso = codes()
    nouns = sorted(set(_national_nouns(_national_groups())) | set(LAW_NOUN.values()))
    for lang in ("english", "russian"):
        put(LOC.format(lang), loc_text(lang, iso, nouns))
    ld_gen.emit(CUSTOM, custom_text(nouns))
    ld_gen.report("regen_ld_currency_symbol")
    if CHECK and ld_gen._stats["changed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
