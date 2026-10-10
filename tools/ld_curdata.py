"""Список валют форка — один источник для генераторов и анализаторов.

Валюта — ключ `flag:<cur>` переменной `var:zz_ef_cur` страны (R8в, шаг 5); список — `tools/data/ld_currencies.txt`
(ключи 95 законов валют E&F, законы — в архиве форка `_archive/ef_currency_laws/`). Порядок — порядок файла законов (по
алфавиту); по нему идут цепочки `if / else_if` всех генераторов.

    import ld_curdata
    ld_curdata.currencies()   # ['dinar', 'dinar_algerian_dinar', ...]
    ld_curdata.by_length()    # длинные ключи раньше — для регулярного выражения по именам
"""
import os

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "ld_currencies.txt")


def currencies():
    out = [ln.strip() for ln in open(DATA, encoding="utf-8") if ln.strip() and not ln.startswith("#")]
    assert len(out) >= 90, len(out)
    return out


def by_length():
    return sorted(set(currencies()), key=len, reverse=True)
