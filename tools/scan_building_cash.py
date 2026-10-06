"""The business cash (Σ cash_reserves of the buildings, the money model's M1 - M0) by building type, per country (В2, 7.10).

Usage:  py tools/scan_building_cash.py <save> [TAG ...] [--top N]

Per country: all cash, and the top building types by cash, with their levels and cash per level. Answers what the
"касса предприятий" holds: production, trade centres, the CB (building_bank), the Banks (building_zz_ef_bank),
government buildings, HQs. Parsing as in save_ownership.py / save_money_check.py.
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import save_ownership as SO  # noqa: E402


def main():
    args = sys.argv[1:]
    top = 15
    if '--top' in args:
        i = args.index('--top'); top = int(args[i + 1]); del args[i:i + 2]
    path, tags = args[0], set(args[1:])
    d = SO.parse(path)
    if not os.path.isabs(path):
        path = os.path.join(SO.SG, path)
    s = open(path, 'rb').read().decode('utf-8', 'replace')
    bm = SO.section(s, 'building_manager')
    cash = collections.defaultdict(lambda: collections.defaultdict(float))
    lvl = collections.defaultdict(lambda: collections.defaultdict(float))
    for m in re.finditer(r'\n(\d+)=\{\n\tbuilding=(\w+)\n(.*?)\n\}', bm, re.S):
        bid, bt, body = m.group(1), m.group(2), m.group(3)
        b = d['bld'].get(bid)
        if not b:
            continue
        tag = d['tag'].get(b[1], b[1])
        if tags and tag not in tags:
            continue
        cr = re.search(r'\n\tcash_reserves=([-\d.]+)', '\n' + body)
        lv = re.search(r'\n\tlevel=([\d.]+)', '\n' + body)
        if cr:
            cash[tag][bt] += float(cr.group(1))
        if lv:
            lvl[tag][bt] += float(lv.group(1))
    print(f"date {d['date']}")
    for tag in sorted(cash, key=lambda t: -sum(cash[t].values())):
        if not tags and sum(cash[tag].values()) < 5e6:
            continue
        tot = sum(cash[tag].values())
        print(f"\n{tag}: business cash {tot:,.0f}")
        print(f"  {'building type':44} {'cash':>13} {'share':>7} {'levels':>8} {'cash/level':>11}")
        for bt, v in sorted(cash[tag].items(), key=lambda kv: -kv[1])[:top]:
            l = lvl[tag].get(bt, 0)
            print(f"  {bt:44} {v:13,.0f} {v / tot:7.1%} {l:8,.0f} {v / l if l else 0:11,.0f}")


if __name__ == '__main__':
    main()
