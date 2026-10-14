"""Construction by year from the fork's EFZ lines (форк, R9; docs/construction.md форка, «Логи»).

Usage:  py tools/ld_psc_sum.py <run>/eflog.txt [--countries "Великобритания,Великая Цин"] [--top 8]

Per year: the world's weekly average of the construction spending (total), its government part (gov), the points it
bought (pts), the construction goods made (prod), the rest not given out (rest, should stay >= 0), the construction
sectors' profit and levels, and the weeks with no spending at all among the countries that have sectors. Then the same
for the given countries and for the top countries by points in the last year. A country's week is one EFZ line (PSC
runs once a week per country, on a day of its own); a year's figure is the sum over countries of their weekly average.
"""
import sys
from collections import defaultdict

FIELDS = ('total', 'gov', 'pts', 'prod', 'rest', 'csec_profit', 'csec_lv')


def year(date):
    try:
        return int(date.rsplit(',', 1)[1])
    except (ValueError, IndexError):
        return None


def fields(parts):
    d = {}
    for p in parts:
        k, _, v = p.partition(' ')
        try:
            d[k] = float(v)
        except ValueError:
            pass
    return d


def main():
    a = sys.argv[1:]
    path = a[0]
    countries = a[a.index('--countries') + 1].split(',') if '--countries' in a else []
    top = int(a[a.index('--top') + 1]) if '--top' in a else 8
    # (year, country) -> field -> [sum, n]; idle weeks: sectors > 0 and total 0
    acc = defaultdict(lambda: defaultdict(lambda: [0.0, 0]))
    idle = defaultdict(lambda: [0, 0])
    negrest = defaultdict(int)
    for ln in open(path, encoding='utf-8', errors='replace'):
        if not ln.startswith('EFZ|'):
            continue
        p = ln.rstrip('\n').split('|')
        if len(p) < 4:
            continue
        y = year(p[1])
        if y is None:
            continue
        d = fields(p[3:])
        for k in FIELDS:
            if k in d:
                s = acc[(y, p[2])][k]
                s[0] += d[k]
                s[1] += 1
        if d.get('csec_lv', 0) > 0:
            idle[y][1] += 1
            if d.get('total', 0) <= 0:
                idle[y][0] += 1
        if d.get('rest', 0) < -1:
            negrest[y] += 1
    years = sorted({y for y, _ in acc})

    def avg(y, c, k):
        s = acc.get((y, c), {}).get(k)
        return s[0] / s[1] if s and s[1] else 0.0

    def world(y, k):
        return sum(avg(y, c, k) for (yy, c) in acc if yy == y)

    head = f"{'year':>5} " + ' '.join(f'{k:>11}' for k in FIELDS) + f" {'idle wk %':>9} {'rest<-1':>7}"
    print('WORLD (sum over countries of the weekly average)')
    print(head)
    for y in years:
        iw = idle[y]
        print(f'{y:>5} ' + ' '.join(f'{world(y, k):>11.0f}' for k in FIELDS)
              + f" {100 * iw[0] / iw[1] if iw[1] else 0:>9.1f} {negrest[y]:>7}")
    last = years[-1] if years else None
    if last is not None:
        best = sorted({c for (y, c) in acc if y == last}, key=lambda c: -avg(last, c, 'pts'))[:top]
        for c in countries + [c for c in best if c not in countries]:
            print(f'\n{c}')
            print(f"{'year':>5} " + ' '.join(f'{k:>11}' for k in FIELDS))
            for y in years:
                if (y, c) in acc:
                    print(f'{y:>5} ' + ' '.join(f'{avg(y, c, k):>11.0f}' for k in FIELDS))


if __name__ == '__main__':
    main()
