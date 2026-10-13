"""The pool's multiples left as «прочее» (форк, R4б, Д.R4б.30): who got the money.

Usage:  py tools/ld_pmult_check.py <run>/eflog.txt [--min 50000]

EFJ|lvl lines with pmult < 0 and nothing classified (pool 0, priv 0, tr 0): the pool fell by a multiple of the level's
price, the country's levels did not grow. Per such step: the change of the levels (government, companies, private),
of the foreign-owned GDP here (d_fown) and ours abroad (d_aown); and the other countries whose «прочее» rose that week or
the next (EFJ other line, d_other >= half the step) -- the seller candidates. At the end: the steps' sum and how many
had d_fown < 0 (bought from foreign owners) or a candidate abroad.
"""
import sys
from collections import defaultdict


def fields(parts):
    d = {}
    for x in parts:
        k, _, v = x.partition(' ')
        try:
            d[k] = float(v)
        except ValueError:
            d[k] = v.strip()
    return d


def main():
    path = sys.argv[1]
    mn = 50000.0
    if '--min' in sys.argv:
        mn = float(sys.argv[sys.argv.index('--min') + 1])
    steps = []
    dother = defaultdict(dict)            # date -> country -> d_other
    dates = []
    for ln in open(path, encoding='utf-8', errors='replace'):
        if not ln.startswith('EFJ|'):
            continue
        p = ln.rstrip('\n').split('|')
        if len(p) < 4:
            continue
        date, cty = p[1], p[2]
        if p[3] == 'lvl':
            d = fields(p[4:])
            if d.get('pmult', 0) < 0 and d.get('pool', 0) == 0 and d.get('priv', 0) == 0 and d.get('tr', 0) == 0:
                steps.append((date, cty, d))
        elif p[3].startswith('other ') and cty != 'WORLD':
            d = fields(p[3:])
            if isinstance(d.get('d_other'), float):
                dother[date][cty] = d['d_other']
                if not dates or dates[-1] != date:
                    if date not in dates:
                        dates.append(date)
    dates.sort()
    nxt = {a: b for a, b in zip(dates, dates[1:])}
    tot = 0.0
    n_fown = n_cand = 0
    sum_fown = sum_cand = 0.0
    for date, cty, d in steps:
        pm = d['pmult']
        if -pm < mn:
            continue
        tot += pm
        cands = []
        for dd in (date, nxt.get(date)):
            if not dd:
                continue
            for c, v in dother.get(dd, {}).items():
                if c != cty and v >= -pm * 0.5 and v <= -pm * 1.5:
                    cands.append(f'{c} {v:.0f} ({dd})')
        fo = d.get('d_fown', 0)
        if isinstance(fo, float) and fo < 0:
            n_fown += 1
            sum_fown += pm
        if cands:
            n_cand += 1
            sum_cand += pm
        print(f'{date} {cty:28} pmult {pm:10.0f} d_gov {d.get("d_govlv", 0)} d_comp {d.get("d_complv", 0)} '
              f'd_priv {d.get("d_privlv", 0)} fown {d.get("fown", 0)} d_fown {fo} aown {d.get("aown", 0)} '
              f'd_aown {d.get("d_aown", 0)} | sellers? {"; ".join(cands[:4]) or "-"}')
    print(f'steps {sum(1 for s in steps if -s[2]["pmult"] >= mn)}, sum {tot:.0f}; with d_fown < 0: {n_fown} '
          f'({sum_fown:.0f}); with a candidate abroad: {n_cand} ({sum_cand:.0f})')


if __name__ == '__main__':
    main()
