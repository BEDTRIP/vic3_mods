"""The business cash's «прочее» against the engine's market balance (форк, R4б ночь: утечки).

Usage:  py tools/ld_mkt_check.py <run>/eflog.txt

EFO (b_rest, a week, the countries with logs) and EFM (the country's market by its owner's tag; for the owner the
market's balance, buy / sell orders): per market the run's sums of the logged members' b_rest and the balance, the
members seen, the correlation of the weekly sums.
"""
import sys
from collections import defaultdict


def kv(parts):
    d = {}
    for x in parts:
        k, _, v = x.partition(' ')
        d[k] = v
    return d


def corr(a, b):
    n = len(a)
    if n < 3:
        return float('nan')
    ma, mb = sum(a) / n, sum(b) / n
    sa = sum((x - ma) ** 2 for x in a) ** .5
    sb = sum((y - mb) ** 2 for y in b) ** .5
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / sa / sb if sa and sb else float('nan')


def main():
    brest = {}
    mkt = {}
    bal = {}
    for ln in open(sys.argv[1], encoding='utf-8', errors='replace'):
        if ln.startswith('EFO|'):
            p = ln.rstrip('\n').split('|')
            d = kv(p[3:])
            try:
                brest[(p[2], p[1])] = float(d.get('b_rest', 0))
            except ValueError:
                pass
        elif ln.startswith('EFM|'):
            p = ln.rstrip('\n').split('|')
            d = kv(p[3:])
            mkt[(p[2], p[1])] = d.get('mkt', '?')
            if 'bal' in d:
                try:
                    bal[(d.get('mkt'), p[1])] = float(d['bal'])
                except ValueError:
                    pass
    weekly = defaultdict(lambda: defaultdict(float))
    members = defaultdict(set)
    for (c, dt), v in brest.items():
        m = mkt.get((c, dt))
        if m is None:
            continue
        weekly[m][dt] += v
        members[m].add(c)
    rows = []
    for m, w in weekly.items():
        dts = [dt for dt in w if (m, dt) in bal]
        if not dts:
            continue
        a = [w[dt] for dt in dts]
        b = [bal[(m, dt)] for dt in dts]
        rows.append((sum(b), m, len(dts), sum(a), corr(a, b), sorted(members[m])))
    print(f'{"market":<6} {"weeks":>5} {"sum b_rest":>12} {"sum balance":>12} {"ratio":>6} {"corr":>6}  members logged')
    for sb, m, n, sa, r, mem in sorted(rows):
        print(f'{m:<6} {n:>5} {sa:>12.0f} {sb:>12.0f} {sa / sb if sb else 0:>6.2f} {r:>+6.2f}  {", ".join(mem)[:80]}')


if __name__ == '__main__':
    main()
