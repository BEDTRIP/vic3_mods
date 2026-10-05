"""Buildings of one type in a save, by country: levels, weekly sales / costs / profit, owners (Д2.4, этап 2).

Usage:  py tools/scan_building_type.py <save> <building_type> [TAG ...] [--top N]

Per country: levels (sum over buildings), goods_sales, goods_cost, profit_after_reserves (the save's weekly
figures), and the owned levels by owner kind (fd = financial district, company, country, other). Parsing as in
save_ownership.py.
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import save_ownership as SO  # noqa: E402


def num(body, key):
    m = re.search(r'\n\t' + key + r'=(-?[\d.]+)', body)
    return float(m.group(1)) if m else 0.0


def main():
    args = sys.argv[1:]
    top = 30
    if '--top' in args:
        i = args.index('--top'); top = int(args[i + 1]); del args[i:i + 2]
    path, btype, tags = args[0], args[1], set(args[2:])
    d = SO.parse(path)
    if not os.path.isabs(path):
        path = os.path.join(SO.SG, path)
    s = open(path, 'rb').read().decode('utf-8', 'replace')
    bm = SO.section(s, 'building_manager')
    rows = collections.defaultdict(lambda: collections.Counter())
    for bid, (bt, cid) in d['bld'].items():
        if bt != btype:
            continue
        r = re.search(r'\n' + bid + r'=\{\n(.*?)\n\}', bm, re.S)
        if not r:
            continue
        body = '\n' + r.group(1)
        tag = d['tag'].get(cid, cid)
        c = rows[tag]
        c['n'] += 1
        c['levels'] += num(body, 'levels')
        c['sales'] += num(body, 'goods_sales')
        c['cost'] += num(body, 'goods_cost')
        c['profit'] += num(body, 'profit_after_reserves')
        c['gov_div'] += num(body, 'government_dividends')
    for (kind, oid, bid), lv in d['own'].items():
        b = d['bld'].get(bid)
        if not b or b[0] != btype:
            continue
        tag = d['tag'].get(b[1], b[1])
        if kind == 'country':
            rows[tag]['own_country'] += lv
        else:
            ob = d['bld'].get(oid)
            k = 'own_fd' if ob and ob[0] == 'building_financial_district' else (
                'own_company' if oid in d['comp'] or (ob and ob[0].startswith('building_regional_company_')) else 'own_other')
            rows[tag][k] += lv
    print(f"date {d['date']}  {btype}")
    print('country   n  levels      sales       cost     profit   gov_div  own: fd/company/country/other')
    total = collections.Counter()
    for tag, c in sorted(rows.items(), key=lambda kv: -kv[1]['sales'])[:top] if not tags else \
            [(t, rows[t]) for t in tags if t in rows]:
        total.update(c)
        print(f"{tag:7} {c['n']:3.0f} {c['levels']:7.0f} {c['sales']:10.0f} {c['cost']:10.0f} {c['profit']:10.0f} "
              f"{c['gov_div']:9.0f}  {c['own_fd']:.0f}/{c['own_company']:.0f}/{c['own_country']:.0f}/{c['own_other']:.0f}")
    allc = collections.Counter()
    for c in rows.values():
        allc.update(c)
    print(f"ALL     {allc['n']:3.0f} {allc['levels']:7.0f} {allc['sales']:10.0f} {allc['cost']:10.0f} {allc['profit']:10.0f} "
          f"{allc['gov_div']:9.0f}  {allc['own_fd']:.0f}/{allc['own_company']:.0f}/{allc['own_country']:.0f}/{allc['own_other']:.0f}")


if __name__ == '__main__':
    main()
