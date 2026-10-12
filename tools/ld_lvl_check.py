"""Are the pool's «levels bought» real (форк, R4б ночь, шаг 6)? EFJ|<country>|other lines: the engine pool's unexplained
change of the step u = d_pool - contrib + transfer; if the engine buys levels at multiples of 25 000, the |u| > 20 000
weeks cluster near the multiples (rest = u - nearest multiple), else rest is spread evenly over ±12 500.

Usage:  py tools/ld_lvl_check.py <run>/eflog.txt
"""
import sys
from collections import Counter

U = 25000


def fields(parts):
    d = {}
    for x in parts:
        k, _, v = x.partition(' ')
        try:
            d[k] = float(v)
        except ValueError:
            pass
    return d


def main():
    hist = Counter()
    big = Counter()
    n = 0
    for ln in open(sys.argv[1], encoding='utf-8', errors='replace'):
        if not ln.startswith('EFJ|'):
            continue
        p = ln.rstrip('\n').split('|')
        if len(p) < 4 or not p[3].startswith('other ') or p[2] == 'WORLD':
            continue
        d = fields(p[3:])
        if 'd_pool' not in d or d.get('weeks', 1) != 1:
            continue
        u = d['d_pool'] - d.get('contrib', 0) + d.get('transfer', 0)
        if abs(u) < 20000:
            continue
        n += 1
        rest = u - round(u / U) * U
        b = int((rest + 12500) // 2500)
        (big if abs(u) >= 100000 else hist)[b] += 1
    print(f'weeks with |u| >= 20 000: {n}')
    for name, h in (('20k..100k', hist), ('>=100k', big)):
        print(f'{name}: rest bins of 2 500 from -12 500: ' + ' '.join(str(h.get(i, 0)) for i in range(10)))


if __name__ == '__main__':
    main()
