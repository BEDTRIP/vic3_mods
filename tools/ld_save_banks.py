"""Who owns the levels of the "Bank" building (building_zz_ef_bank) by country, from a text save (форк, R4б, Д.R4б.1).

Usage:  py tools/ld_save_banks.py <save> [--top N] [--json out.json]

For each country (owner of the building's state): levels of building_zz_ef_bank by owner — gov (the country itself),
every company separately (its company type; bank companies — company types that list building_zz_ef_bank), manor
(aristocrats), findist (capitalists outside companies), foreign (any owner from another country), self, other.
Prints per country: total levels, gov, companies (n and levels), private (manor + findist + self + other + foreign),
and the list of companies. A subject-bank of the fork (Д.R4б.1) = every company with levels, "госбанки" = gov,
"частные банкиры" = the rest.
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from save_ownership import parse, SG  # noqa: E402

BANK = 'building_zz_ef_bank'
OWNER_TYPES = {'building_manor_house': 'manor', 'building_financial_district': 'findist'}


def owner_class(d, kind, oid, bid, cty):
    if kind == 'country':
        return ('gov' if d['tag'].get(oid) == cty else 'foreign'), None
    ob = d['bld'].get(oid)
    if not ob:
        return 'other', None
    octy = d['tag'].get(ob[1], ob[1])
    if oid in d['comp']:
        cl, name = 'company', d['comp'][oid]
    elif ob[0].startswith('building_regional_company_'):
        cl, name = 'company', ob[0][len('building_regional_company_'):]
    elif ob[0] in OWNER_TYPES:
        cl, name = OWNER_TYPES[ob[0]], None
    elif oid == bid:
        cl, name = 'self', None
    else:
        cl, name = 'other', ob[0]
    if octy != cty:
        return 'foreign', name
    return cl, name


def main():
    args = sys.argv[1:]
    top, out = 25, None
    if '--top' in args:
        i = args.index('--top'); top = int(args[i + 1]); del args[i:i + 2]
    if '--json' in args:
        i = args.index('--json'); out = args[i + 1]; del args[i:i + 2]
    path = args[0] if args else 'autosave.v3'
    d = parse(path if os.path.isabs(path) else os.path.join(SG, path))
    cls = collections.defaultdict(collections.Counter)
    comps = collections.defaultdict(collections.Counter)
    for (kind, oid, bid), lv in d['own'].items():
        b = d['bld'].get(bid)
        if not b or b[0] != BANK:
            continue
        cty = d['tag'].get(b[1], b[1])
        cl, name = owner_class(d, kind, oid, bid, cty)
        cls[cty][cl] += lv
        if cl == 'company':
            comps[cty][name] += lv
    rows = []
    for c, v in cls.items():
        tot = sum(v.values())
        rows.append(dict(country=c, total=tot, gov=v['gov'], companies=dict(comps[c]),
                         private=tot - v['gov'] - v['company'], classes=dict(v)))
    rows.sort(key=lambda r: -r['total'])
    print(f"date {d['date']}; countries with banks {len(rows)}; levels {sum(r['total'] for r in rows)}; "
          f"companies with bank levels {sum(len(r['companies']) for r in rows)}")
    ncomp = collections.Counter(len(r['companies']) for r in rows)
    print('countries by number of bank-owning companies: ' + ', '.join(f'{k}: {ncomp[k]}' for k in sorted(ncomp)))
    print(f"{'country':7} {'total':>6} {'gov':>5} {'comp':>5} {'priv':>5}  companies")
    for r in rows[:top]:
        cs = ', '.join(f'{k} {v}' for k, v in sorted(r['companies'].items(), key=lambda x: -x[1]))
        print(f"{r['country']:7} {r['total']:6d} {r['gov']:5d} {sum(r['companies'].values()):5d} {r['private']:5d}  {cs}")
    if out:
        json.dump(dict(date=d['date'], rows=rows), open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
