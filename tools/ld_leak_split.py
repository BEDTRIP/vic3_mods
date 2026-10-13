"""Who lost the money of the line «движок: оплачено сверх продаж рынка» (форк, R4б, шаг 2; Д.R4б.33).

Usage:  py tools/ld_leak_split.py <run>/eflog.txt [--from 1837] [--to 1839] [--tags FRA,GBR,NET,BAV,...]

Per country that owns its market (EFM tag = mkt) and writes the bridge line (EFR leak), week by week: the line against
the market's gap by goods groups (EFM: gap_fin -- the mod's financial goods, the pops' needs; gap_psc -- PSC's
construction goods, the construction sector's inputs and the pops' housing; gap_metal -- gold and silver, the pops' hoard
and the banks' orders; the rest -- vanilla goods). Least squares leak ~ a_fin x fin + a_psc x psc + a_metal x metal
+ a_van x van (no constant): which groups lose money one to one (a ~ 1) and which do not (a ~ 0). The split: each
group's part of the line (a x its sum) -- the pops' part = fin + metal, the buildings' part = psc (принято ночью,
проверить: the households' share of construction goods and the banks' share of metal are not in the log), vanilla --
apart. Per country and over all of them, and the spread of the weekly pops' share (weeks with |leak| > 1000).
Через мост: py_tool("ld_leak_split", ["runs/<id>/eflog.txt", "--from", "1837", "--to", "1839"]).
"""
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
G = ['fin', 'psc', 'metal', 'van']


def fields(parts):
    d = {}
    for x in parts:
        k, _, v = x.rpartition(' ')
        try:
            d[k] = float(v)
        except ValueError:
            d[k] = v
    return d


def year(dt):
    return int(dt.rsplit(',', 1)[1])


def solve(rows):
    """Least squares without a constant: rows of (y, [x...]); Gauss on the normal equations."""
    n = len(G)
    a = [[0.0] * (n + 1) for _ in range(n)]
    for y, x in rows:
        for i in range(n):
            for j in range(n):
                a[i][j] += x[i] * x[j]
            a[i][n] += x[i] * y
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(a[r][i]))
        a[i], a[p] = a[p], a[i]
        if abs(a[i][i]) < 1e-9:
            continue
        for r in range(n):
            if r != i:
                f = a[r][i] / a[i][i]
                for c in range(i, n + 1):
                    a[r][c] -= f * a[i][c]
    return [a[i][n] / a[i][i] if abs(a[i][i]) > 1e-9 else 0.0 for i in range(n)]


def main():
    a = sys.argv[1:]
    path = a[0]
    y0 = int(a[a.index('--from') + 1]) if '--from' in a else 0
    y1 = int(a[a.index('--to') + 1]) if '--to' in a else 9999
    tags = set(a[a.index('--tags') + 1].split(',')) if '--tags' in a else None
    leak = {}                          # (name, date) -> the line
    mkt = {}                           # (name, date) -> EFM groups
    tag_of = {}
    for ln in open(path, encoding='utf-8', errors='replace'):
        if len(ln) < 6 or ln[0] != 'E' or ln[3] != '|':
            continue
        p = ln.rstrip('\n').split('|')
        if len(p) < 5 or not (y0 <= year(p[1]) <= y1):
            continue
        if p[0] == 'EFR':
            d = fields(p[3:])
            if 'leak' in d:
                leak[(p[2], p[1])] = d['leak']
        elif p[0] == 'EFM' and p[3].startswith('tag '):
            d = fields(p[3:])
            if d.get('tag') != d.get('mkt') or 'gap_psc' not in d:
                continue
            tag_of[p[2]] = d['tag']
            fin, psc, met = d.get('gap_fin', 0), d.get('gap_psc', 0), d.get('gap_metal', 0)
            mkt[(p[2], p[1])] = [fin, psc, met, d.get('gap', 0) - fin - psc - met]
    by = defaultdict(list)
    for k, x in mkt.items():
        if k in leak and (tags is None or tag_of.get(k[0]) in tags):
            by[k[0]].append((leak[k], x))
    allrows = []
    print(f"{'страна':24} {'нед':>4} {'статья':>11} " + ' '.join(f'{"a_" + g:>7}' for g in G)
          + ' ' + ' '.join(f'{g:>10}' for g in G) + f" {'население':>9} {'разброс':>8}")
    for c in sorted(by, key=lambda c: -sum(abs(y) for y, _ in by[c])):
        rows = by[c]
        allrows += rows
        co = solve(rows)
        part = [co[i] * sum(x[i] for _, x in rows) for i in range(len(G))]
        tot = sum(y for y, _ in rows)
        mod = part[0] + part[1] + part[2]
        pop = (part[0] + part[2]) / mod if abs(mod) > 1 else float('nan')
        wk = [(co[0] * x[0] + co[2] * x[2]) / (co[0] * x[0] + co[1] * x[1] + co[2] * x[2])
              for y, x in rows if abs(y) > 1000 and abs(co[0] * x[0] + co[1] * x[1] + co[2] * x[2]) > 1]
        wk.sort()
        spread = (wk[int(len(wk) * 0.9)] - wk[int(len(wk) * 0.1)]) if len(wk) >= 10 else float('nan')
        print(f'{c[:24]:24} {len(rows):4} {tot:11.0f} ' + ' '.join(f'{v:7.2f}' for v in co)
              + ' ' + ' '.join(f'{v:10.0f}' for v in part) + f' {pop:9.2f} {spread:8.2f}')
    co = solve(allrows)
    part = [co[i] * sum(x[i] for _, x in allrows) for i in range(len(G))]
    mod = part[0] + part[1] + part[2]
    print(f"{'ВСЕ':24} {len(allrows):4} {sum(y for y, _ in allrows):11.0f} " + ' '.join(f'{v:7.2f}' for v in co)
          + ' ' + ' '.join(f'{v:10.0f}' for v in part) + f' {(part[0] + part[2]) / mod if abs(mod) > 1 else 0:9.2f}')


if __name__ == '__main__':
    main()
