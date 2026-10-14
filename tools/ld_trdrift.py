"""The treasury part of «прочее» drifting: which line moves with it over a run (форк, R5, закрытие).

Usage:  py tools/ld_trdrift.py <run>/eflog.txt [--top 15]

Per log country: the run's sum of the treasury part's weekly «прочее» (EFJ other, d_other_tr) and the run's sum of every
numeric field of the same weeks' EFF treasury card and EFR line. Over the countries: the fields whose sums track the
drift -- least |drift - s x field| summed over the countries (s = +1 / -1), and the ratio drift / field. A small weekly
bias with no single week standing out shows here, not in ld_restexplain (week by week).
Через мост: py_tool("ld_trdrift", ["runs/<id>/eflog.txt"]).
"""
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")


def fields(parts, prefix=''):
    d = {}
    for x in parts:
        k, _, v = x.rpartition(' ')
        try:
            d[prefix + k.lstrip('-')] = float(v) * (-1 if k.startswith('-') else 1)
        except ValueError:
            pass
    return d


def main():
    a = sys.argv[1:]
    top = int(a[a.index('--top') + 1]) if '--top' in a else 15
    drift = defaultdict(float)
    weeks = defaultdict(set)
    cand = defaultdict(lambda: defaultdict(float))
    rows = defaultdict(dict)
    for ln in open(a[0], encoding='utf-8', errors='replace'):
        if not ln.startswith(('EFJ|', 'EFF|', 'EFR|')):
            continue
        p = ln.rstrip('\n').split('|')
        if len(p) < 4:
            continue
        k = (p[2], p[1])
        if p[0] == 'EFJ' and p[3].startswith('other '):
            v = fields(p[3:]).get('d_other_tr')
            if v is not None:
                drift[p[2]] += v
                weeks[p[2]].add(p[1])
        elif p[0] == 'EFF' and len(p) > 4 and p[3] == 'treasury':
            rows[k].update(fields(p[4:], 'tr.'))
        elif p[0] == 'EFR':
            rows[k].update(fields(p[3:], 'r.'))
    for (c, dt), f in rows.items():
        if dt in weeks.get(c, ()):
            for n, x in f.items():
                cand[c][n] += x
    cs = [c for c in drift if c in cand]
    base = sum(abs(drift[c]) for c in cs)
    print(f'стран {len(cs)}, сумма дрейфа {sum(drift[c] for c in cs) / 1e6:.2f} млн, сумма модулей {base / 1e6:.2f} млн')
    names = set(n for c in cs for n in cand[c])
    score = []
    for n in names:
        for s in (1, -1):
            sc = sum(abs(drift[c] - s * cand[c].get(n, 0)) for c in cs)
            tot = sum(cand[c].get(n, 0) for c in cs)
            score.append((sc, n, s, tot))
    score.sort()
    for sc, n, s, tot in score[:top]:
        print(f'  дрейф {"−" if s > 0 else "+"} {n:40} -> {sc / 1e6:8.2f} млн ({sc / base if base else 0:.2f}); сумма поля {tot / 1e6:9.2f} млн')
    print('по странам (дрейф, млн):', ', '.join(f'{c[:14]} {drift[c] / 1e6:.2f}' for c in sorted(cs, key=lambda c: -abs(drift[c]))[:8]))


if __name__ == '__main__':
    main()
