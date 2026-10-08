"""Технологии стартовых денежных законов — в истории стран (R3а (а), R3б.5).

Движок на загрузке проверяет условия законов («not permitted to retain law») по технологиям из истории стран, а не по
выданным скриптом истории позже, поэтому технологии законов старта стоят в `history/countries/`.

Читает форк:
- `common/history/buildings/00_ef_building.txt` — ЦБ истории: страны (`c:TAG ?= this`) в условиях блоков с
  `initialize_historic_macro_facilities_bc` → `banking`, `currency_standards`, `central_banking`, `metalique_standard`;
- `common/history/global/99_ef_history_global_variable.txt` — страны, которым история ставит металлический стандарт
  (`law_gold_standard` / `law_silver_standard` / `law_bimetallism_standard`) и закон валюты, без ЦБ истории →
  `banking`, `currency_standards`, `metalique_standard`.

Пишет (через ld_gen, по ключам записей): `common/history/countries/ld_start_technologies.txt` (`COUNTRIES`).

    python3 tools/regen_ld_start_technologies.py [--check]
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ld_gen  # noqa: E402

BUILD = os.path.join(ld_gen.FORK, "common", "history", "buildings", "00_ef_building.txt")
HIST = os.path.join(ld_gen.FORK, "common", "history", "global", "99_ef_history_global_variable.txt")
OUT = "common/history/countries/ld_start_technologies.txt"
CB_TECH = ("banking", "currency_standards", "central_banking", "metalique_standard")
STD_TECH = ("banking", "currency_standards", "metalique_standard")


def uncomment(text):
    return "\n".join(line.split("#", 1)[0] for line in text.split("\n"))


def blocks(text, key):
    """Тела блоков `key = { … }` по порядку."""
    out = []
    for m in re.finditer(r"\b" + key + r"\s*=\s*\{", text):
        i, d = m.end(), 1
        while d:
            d += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        out.append(text[m.end():i - 1])
    return out


def cb_tags():
    text = uncomment(open(BUILD, encoding="utf-8-sig").read())
    tags = set()
    for body in blocks(text, "if"):
        lim = blocks(body, "limit")
        if lim and "initialize_historic_macro_facilities_bc" in body and "if = {" not in body.split("limit", 1)[0]:
            tags |= set(re.findall(r"c:([A-Z0-9]{3}) ?\?= this", lim[0]))
    assert len(tags) >= 30, sorted(tags)
    return tags


def standard_tags():
    text = uncomment(open(HIST, encoding="utf-8-sig").read())
    tags = set()
    for body in blocks(text, "if"):
        lim = blocks(body, "limit")
        if not lim:
            continue
        own = body[body.index(lim[0]) + len(lim[0]):]
        if (re.search(r"activate_law = law_type:law_(gold|silver|bimetallism)_standard\b", own)
                and re.search(r"activate_law = law_type:law_\w+_currency\b", own)):
            tags |= set(re.findall(r"c:([A-Z0-9]{3}) ?\?= this", lim[0]))
    return tags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.parse_args()
    cb = cb_tags()
    std = standard_tags() - cb
    out = ["COUNTRIES = {\n"]
    for tag in sorted(cb | std):
        out.append(f"\tc:{tag} ?= {{\n")
        out += [f"\t\tadd_technology_researched = {t}\n" for t in (CB_TECH if tag in cb else STD_TECH)]
        out.append("\t}\n")
    out.append("}\n")
    ld_gen.emit(OUT, "".join(out))
    ld_gen.report("regen_ld_start_technologies")


if __name__ == "__main__":
    main()
