"""Список валют форка — один источник для генераторов и анализаторов.

Валюта — ключ закона `law_<cur>_currency` в `common/laws/01_ef_currency_type.txt` форка (95 законов). Порядок —
порядок файла (по алфавиту); по нему идут цепочки `if / else_if` всех генераторов.

    import ld_curdata
    ld_curdata.currencies()   # ['dinar', 'dinar_algerian_dinar', ...]
    ld_curdata.laws()         # [(cur, тело закона)] — для разбора can_enact, on_activate
    ld_curdata.by_length()    # длинные ключи раньше — для регулярного выражения по именам
"""
import os
import re

FORK = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                                     "Economic-and-Financial-Ledgerdemain-Mod"))
LAWS = os.path.join(FORK, "common", "laws", "01_ef_currency_type.txt")


def laws():
    """[(cur, тело закона)] в порядке файла."""
    text = open(LAWS, encoding="utf-8-sig").read()
    out = re.findall(r"^law_([a-z_]+)_currency = \{(.*?)^\}", text, re.M | re.S)
    assert len(out) >= 90, len(out)
    return out


def currencies():
    return [c for c, _ in laws()]


def by_length():
    return sorted(set(currencies()), key=len, reverse=True)
