"""What a company owns: levels by building type for the companies of a save (EF.49, этап 2).

Usage:  py tools/scan_company_buildings.py <save> [company_type_substring ...] [--cb]

--cb: only E&F bank companies (the 98 of zz_ef_cm_companies.txt + E&F's own) -- the ones that can hold
building_bank (the monopoly itself is not in the save's company records). Output per company: country, HQ, then building type -> levels (own levels, summed over
buildings), largest first. Parsing as in save_ownership.py.
"""
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import save_ownership as SO  # noqa: E402


def main():
    args = sys.argv[1:]
    cb = '--cb' in args
    args = [a for a in args if a != '--cb']
    d = SO.parse(args[0])
    subs = args[1:]
    banks = SO.bank_companies() if cb else None
    owned = collections.defaultdict(collections.Counter)
    for (kind, oid, bid), lv in d['own'].items():
        if kind != 'building':
            continue
        ctype = d['comp'].get(oid)
        if ctype is None:
            ob = d['bld'].get(oid)
            if ob and ob[0].startswith('building_regional_company_'):
                ctype = ob[0][len('building_regional_company_'):] + ' (regional)'
            else:
                continue
        b = d['bld'].get(bid)
        if not b:
            continue
        owned[(ctype, oid)][b[0]] += lv
    print(f"date {d['date']}")
    for (ctype, oid), c in sorted(owned.items(), key=lambda kv: -sum(kv[1].values())):
        base = ctype.split(' ')[0]
        if subs and not any(s.lower() in ctype.lower() for s in subs):
            continue
        if banks is not None and base not in banks:
            continue
        hq = d['bld'].get(oid)
        cty = d['tag'].get(hq[1], hq[1]) if hq else '?'
        print(f"{ctype} [{cty}] hq={oid}: " + ', '.join(f'{k} {v}' for k, v in c.most_common()))


if __name__ == '__main__':
    main()
