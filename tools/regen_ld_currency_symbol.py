"""Код и знак валюты форка «E&F: Ledgerdemain» (Д.R8в.20, заменяет Д.R8а.8): код — две буквы страны + первая буква
слова валюты, как в ISO 4217 (`GBP`, `CHF`, `USD`, `RUR`); в окнах — знак у выбранных кодов (`GBP` → £, `USD` → $),
у остальных — код.

    python3 tools/regen_ld_currency_symbol.py [--check]

Две буквы — ISO 3166-1 у страны, которая соответствует нынешней (`ISO`), иначе две буквы тега с разводом совпадений
(пары букв тега, затем первая буква тега или названия с буквой названия, затем первая буква тега с любой, затем любая
свободная пара, по кругу; сначала все страны с историей на 1836, потом остальные; ISO и выбранные раньше — заняты). Теги — снимок `tools/data/vic3_country_tags.json` (ваниль 1.13:
`common/country_definitions` с английскими названиями, `history_1836` — теги файлов `common/history/countries`).
Буква — первая буква слова валюты (`var:zz_ef_cur_noun`, слова — `regen_ld_currency_national.py`). Член валютного союза
(Д.R8в.5) — буквы главы союза (`var:zz_ef_mu_head`). Знак — `CODE_SIGN` (один знак — один код). Без денежной системы —
`¤` (Д.R8а.2: своей валюты нет).

Движок (проба r1009_032419): `Country.GetTagName` — тег, `Localize(Concatenate('zz_ef_iso2_', тег))` — текст ключа; в тексте
custom loc `ROOT.GetCountry` — страна, у которой спрошен код или знак.

Пишет в форк:
- `localization/{english,russian}/ld_currency_symbol_l_*.yml` — `zz_ef_iso2_<тег>` (две буквы), `zz_ef_iso2_self`,
  `zz_ef_code_<слово>` (код), `zz_ef_sym_code_<код>` (знак), `zz_ef_sym_code` (код вместо знака), `zz_ef_sym_none`;
- в `common/customizable_localization/00_ef_localization_ custom.txt` — тела `zz_ef_cur_iso2` (две буквы: свои или
  главы союза), `currency_code`, `currency_symbol`.
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
# код → (слово, знак): только эти коды показываются знаком, остальные — кодом
CODE_SIGN = {
    "GBP": ("pound", "£"), "USD": ("dollar", "$"), "FRF": ("franc", "₣"), "RUR": ("ruble", "₽"), "JPY": ("yen", "¥"),
    "INR": ("rupee", "₹"), "DEM": ("mark", "ℳ"), "TRL": ("lira", "₺"), "KRW": ("won", "₩"), "PHP": ("peso", "₱"),
    "UAH": ("hryvnia", "₴"), "THB": ("baht", "฿"), "VND": ("dong", "₫"), "ESP": ("peseta", "₧"),
    "GRD": ("drachma", "₯"),
}
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


def letter_of(n):
    return n[:1].upper()


def sign_codes(iso):
    """{код: (тег, слово, знак)} для CODE_SIGN; код без тега с этими буквами или не того слова -- ошибка таблицы."""
    by_two = {c: tg for tg, c in iso.items()}
    out = {}
    for code, (n, sign) in sorted(CODE_SIGN.items()):
        tg = by_two.get(code[:2])
        if not tg or letter_of(n) != code[2]:
            raise SystemExit(f"CODE_SIGN: {code} -- нет тега с буквами {code[:2]} или слово {n} не на {code[2]}")
        out[code] = (tg, n, sign)
    return out


def loc_text(lang, iso, nouns, signs):
    two = "[ROOT.GetCountry.GetCustom('zz_ef_cur_iso2')]"
    L = [f"\ufeffl_{lang}:"]
    L += [f' zz_ef_iso2_{t}:0 "{c}"' for t, c in sorted(iso.items())]
    L.append(' zz_ef_iso2_self:0 "[Localize(Concatenate(\'zz_ef_iso2_\', ROOT.GetCountry.GetTagName))]"')
    L += [f' zz_ef_code_{n}:0 "{two}{letter_of(n)}"' for n in nouns]
    L.append(f' zz_ef_sym_none:0 "{NONE_SIGN}"')
    L.append(' zz_ef_sym_code:0 "[ROOT.GetCountry.GetCustom(\'currency_code\')]"')
    L += [f' zz_ef_sym_code_{c}:0 "{s}"' for c, (_, _, s) in signs.items()]
    return "\n".join(L) + "\n"


def custom_text(iso, nouns, signs):
    L = ["zz_ef_cur_iso2 = {", "\ttype = country", "\tlog_loc_errors = no", "",
         "\t# the two letters of the currency's code: the country's own, a currency union's follower -- its head's",
         "\t# (Д.R8в.20, tools/regen_ld_currency_symbol.py)",
         "\ttext = {", "\t\ttrigger = { NOT = { zz_ef_mu_follower = yes } }",
         "\t\tlocalization_key = zz_ef_iso2_self", "\t}"]
    for tg in sorted(iso):
        L += ["\ttext = {", f"\t\ttrigger = {{ var:zz_ef_mu_head ?= c:{tg} }}",
              f"\t\tlocalization_key = zz_ef_iso2_{tg}", "\t}"]
    L += ["\ttext = {", "\t\tlocalization_key = zz_ef_iso2_self", "\t}", "}", ""]
    L += ["currency_code = {", "\ttype = country", "\tlog_loc_errors = no", "",
          "\t# «<two letters of the country> <the first letter of its currency's word>» (Д.R8в.20)",
          "\t#no monetary system", "\ttext = {", "\t\ttrigger = { has_law = law_type:law_no_monetary_system }",
          "\t\tlocalization_key = zz_ef_sym_none", "\t}"]
    for n in nouns:
        L += [f"\t#{n}", "\ttext = {", f"\t\ttrigger = {{ var:zz_ef_cur_noun ?= flag:{n} }}",
              f"\t\tlocalization_key = zz_ef_code_{n}", "\t}"]
    L += ["\t#generic", "\ttext = {", "\t\tlocalization_key = zz_ef_sym_none", "\t}", "}", ""]
    L += ["currency_symbol = {", "\ttype = country", "\tlog_loc_errors = no", "",
          "\t# the sign of the codes that have one, else the code (Д.R8в.20)",
          "\t#no monetary system", "\ttext = {", "\t\ttrigger = { has_law = law_type:law_no_monetary_system }",
          "\t\tlocalization_key = zz_ef_sym_none", "\t}"]
    for c, (tg, n, _) in signs.items():
        L += [f"\t#{c}", "\ttext = {", "\t\ttrigger = {", f"\t\t\tvar:zz_ef_cur_noun ?= flag:{n}",
              "\t\t\tOR = {", f"\t\t\t\tAND = {{ NOT = {{ zz_ef_mu_follower = yes }} c:{tg} ?= this }}",
              f"\t\t\t\tvar:zz_ef_mu_head ?= c:{tg}", "\t\t\t}", "\t\t}",
              f"\t\tlocalization_key = zz_ef_sym_code_{c}", "\t}"]
    L += ["\t#the code", "\ttext = {", "\t\tlocalization_key = zz_ef_sym_code", "\t}", "}"]
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
    signs = sign_codes(iso)
    for lang in ("english", "russian"):
        put(LOC.format(lang), loc_text(lang, iso, nouns, signs))
    ld_gen.emit(CUSTOM, custom_text(iso, nouns, signs))
    ld_gen.report("regen_ld_currency_symbol")
    if CHECK and ld_gen._stats["changed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
