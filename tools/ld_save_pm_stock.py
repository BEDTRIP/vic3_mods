"""R1а.2 (Д.1): do the buildings' "stock" methods follow their private ownership share? From a text save.

Usage:  python tools/ld_save_pm_stock.py <save> [--top N]

E&F's rule (private_ownership_production_stocks, now the hook zz_ef_pm_stock_building on one building): a building
of the 48 listed types runs pm_private_ownership_majority_<g>_stock when its private ownership share is over 0.5,
pm_no_private_ownership_<g>_stock otherwise (g = manufacture / agricultural / mining / railroad). The share: the
levels owned by anyone but a country (companies, manors, financial districts, the building itself) over all its
levels (building_ownership_manager; privatization records skipped). Prints per group: buildings checked, matching,
mismatched both ways, and the countries with most mismatches. Reads only; the save format -- save_ownership.py.
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import save_ownership as so  # noqa: E402

GROUPS = ('manufacture', 'agricultural', 'mining', 'railroad')


def main():
    args = sys.argv[1:]
    top = 10
    if '--top' in args:
        i = args.index('--top'); top = int(args[i + 1]); del args[i:i + 2]
    path = args[0]
    if not os.path.isabs(path):
        path = os.path.join(so.SG, path)
    s = open(path, 'rb').read().decode('utf-8', 'replace')
    date = re.search(r'\ndate=([\d.]+)', s).group(1)
    tag = {}
    for m in re.finditer(r'\n(\d+)=\{\n(?:\t[^\n]*\n){0,3}?\tdefinition="(\w+)"', so.section(s, 'country_manager')):
        tag[m.group(1)] = m.group(2)
    st_country = {m.group(1): m.group(2) for m in
                  re.finditer(r'\n(\d+)=\{\n\tcapital=\d+\n\n?\tcountry=(\d+)', so.section(s, 'states'))}
    bm = so.section(s, 'building_manager')
    pms = {}
    for m in re.finditer(r'\n(\d+)=\{\n\tbuilding=(\w+)\n(.*?)\n\}', bm, re.S):
        body = m.group(3)
        st = re.search(r'\n\tstate=(\d+)', '\n' + body)
        if not st or st.group(1) == '4294967295':
            continue
        pm = re.search(r'\tproduction_methods=\{([^}]*)\}', body)
        if not pm:
            continue
        names = re.findall(r'"(\w+)"', pm.group(1))
        stock = [n for n in names if n.endswith('_stock') and 'private_ownership' in n]
        if stock:
            pms[m.group(1)] = (m.group(2), st_country.get(st.group(1)), stock[0])
    gov = collections.Counter()
    tot = collections.Counter()
    for m in re.finditer(r'\n\d+=\{\n\tlevels=(\d+)\n\tidentity=\{\n\t\t(building|country)=(\d+)\n\t\}\n\tbuilding=(\d+)\n(\tprivatization=yes\n)?',
                         so.section(s, 'building_ownership_manager')):
        if m.group(5):
            continue
        lv = int(m.group(1))
        tot[m.group(4)] += lv
        if m.group(2) == 'country':
            gov[m.group(4)] += lv
    res = {g: collections.Counter() for g in GROUPS}
    bad = collections.Counter()
    for bid, (bt, cty, pm) in pms.items():
        if not tot[bid]:
            continue
        g = next((x for x in GROUPS if f'_{x}_stock' in pm), None)
        if not g:
            continue
        share = 1 - gov[bid] / tot[bid]
        majority = pm.startswith('pm_private_ownership_majority_')
        r = res[g]
        r['checked'] += 1
        if majority == (share > 0.5):
            r['ok'] += 1
        elif majority:
            r['majority_but_<=0.5'] += 1
            bad[tag.get(cty, cty)] += 1
        else:
            r['no_but_>0.5'] += 1
            bad[tag.get(cty, cty)] += 1
    print(f'{date}: buildings with a stock method {len(pms)}')
    for g in GROUPS:
        r = res[g]
        print(f"  {g:12} checked {r['checked']:6d}  ok {r['ok']:6d}  majority<=0.5 {r['majority_but_<=0.5']:5d}  "
              f"no>0.5 {r['no_but_>0.5']:5d}")
    if bad:
        print('  mismatches by country: ' + ', '.join(f'{c} {n}' for c, n in bad.most_common(top)))


if __name__ == '__main__':
    main()
