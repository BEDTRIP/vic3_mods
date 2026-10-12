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
    allc = {}
    mkt = {}
    bal = {}
    gap = {}
    msh = {}
    for ln in open(sys.argv[1], encoding='utf-8', errors='replace'):
        if ln.startswith('EFO|'):
            p = ln.rstrip('\n').split('|')
            d = kv(p[3:])
            try:
                brest[(p[2], p[1])] = float(d.get('b_rest', 0))
            except ValueError:
                pass
        elif ln.startswith('EFW|') and '|all|' in ln:
            p = ln.rstrip('\n').split('|')
            allc[p[2]] = kv(p[4:])
        elif ln.startswith('EFM|'):
            p = ln.rstrip('\n').split('|')
            d = kv(p[3:])
            mkt[(p[2], p[1])] = d.get('mkt', '?')
            try:
                msh[(p[2], p[1])] = float(d.get('msh_c', 'x'))
            except ValueError:
                pass
            if 'gap' in d:
                try:
                    gap[(d.get('mkt'), p[1])] = float(d['gap'])
                except ValueError:
                    pass
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
        sg = sum(gap.get((m, dt), 0) for dt in weekly[m] if (m, dt) in bal)
        print(f'{m:<6} {n:>5} {sa:>12.0f} {sb:>12.0f} {sa / sb if sb else 0:>6.2f} {r:>+6.2f}  gap {sg:>12.0f}  '
              f'{", ".join(mem)[:60]}')
    # per country: its b_rest against its market's balance / gap x its share of the market's consumption
    per = defaultdict(lambda: [0.0, 0.0, 0.0, 0])
    for (c, dt), v in brest.items():
        m = mkt.get((c, dt))
        sh = msh.get((c, dt))
        if m is None or sh is None or (m, dt) not in bal:
            continue
        a = per[c]
        a[0] += v
        a[1] += bal[(m, dt)] * sh
        a[2] += gap.get((m, dt), 0) * sh
        a[3] += 1
    print(f'{"country":<28} {"weeks":>5} {"b_rest":>12} {"bal x msh_c":>12} {"gap x msh_c":>12} {"ratio":>6}'
          f'  sol  lit  m2/gdp  pool/gdp')
    for c, a in sorted(per.items(), key=lambda kv: kv[1][0])[:30]:
        e = allc.get(c, {})

        def f(k):
            try:
                return float(e.get(k, 0))
            except ValueError:
                return 0.0
        g = f('gdp') or 1
        print(f'{c[:28]:<28} {a[3]:>5} {a[0]:>12.0f} {a[1]:>12.0f} {a[2]:>12.0f} {a[0] / a[1] if a[1] else 0:>6.2f}'
              f'  {f("sol"):>4.1f} {f("literacy"):>4.2f} {f("m2") / g:>6.2f} {f("pool") / g:>8.3f}')
    tot = [sum(a[i] for a in per.values()) for i in range(3)]
    print(f'all countries: b_rest {tot[0]:.0f}, bal x msh_c {tot[1]:.0f}, gap x msh_c {tot[2]:.0f}')


if __name__ == '__main__':
    main()
