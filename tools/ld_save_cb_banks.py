"""Страны с ЦБ (здание building_bank) и их здания «Банк» (building_zz_ef_bank) по сейву (R4а, шаг 3).

Usage:  py tools/ld_save_cb_banks.py <save.v3>   (имя внутри 'save games' тоже годится)

Для каждой страны с building_bank: уровни ЦБ и уровни «Банков»; в конце — сколько стран с ЦБ без «Банков».
Через мост: py_tool("ld_save_cb_banks", ["docs/save games/autosave.v3"]).
"""
import collections
import re
import sys

import save_ownership as so

sys.stdout.reconfigure(encoding="utf-8")


def main():
    path = sys.argv[1]
    import os
    if not os.path.isabs(path):
        path = os.path.join(so.SG, path)
    s = open(path, 'rb').read().decode('utf-8', 'replace')
    d = so.parse(path)
    lv = collections.defaultdict(collections.Counter)
    for m in re.finditer(r'\n(\d+)=\{\n\tbuilding=(building_bank|building_zz_ef_bank)\n(?:\t[^\n]*\n)*?\tstate=(\d+)\n'
                         r'(?:\t[^\n]*\n)*?\tlevels=(\d+)', so.section(s, 'building_manager')):
        b = d['bld'].get(m.group(1))
        if not b:
            continue
        lv[d['tag'].get(b[1], b[1])][m.group(2)] += int(m.group(4))
    cb = sorted(c for c in lv if lv[c]['building_bank'] > 0)
    print(f"{d['date']}: стран с ЦБ {len(cb)}, из них без «Банков» "
          f"{sum(1 for c in cb if lv[c]['building_zz_ef_bank'] == 0)}")
    for c in cb:
        print(f"  {c:6} ЦБ {lv[c]['building_bank']:3}  «Банк» {lv[c]['building_zz_ef_bank']:3}")


if __name__ == '__main__':
    main()
