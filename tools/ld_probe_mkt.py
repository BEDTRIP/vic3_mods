"""Reads the market probe of a sandbox run (форк, R4б, В.R4б.28; scripted_effects/ld_probe_mkt.txt).

Usage:  py tools/ld_probe_mkt.py <run>/eflog.txt

EFP|bld lines (France, Britain, every 4th week): per building what it paid for its inputs (mat), the value of its
consumption (cv), its input availability (av). If a buyer pays for the whole order, mat / cv grows as av falls (the
value counts what it got) or mat ≈ cv / av; prints mat / cv by availability band, by building type, and the sums.
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
    bands = defaultdict(lambda: [0, 0.0, 0.0, 0.0])      # (country, band) -> n, mat, cv, cv/av
    types = defaultdict(lambda: [0, 0.0, 0.0, 0.0])
    mkt = defaultdict(lambda: [0, 0.0, 0.0])
    for ln in open(sys.argv[1], encoding='utf-8', errors='replace'):
        if not ln.startswith('EFP|'):
            continue
        p = ln.rstrip('\n').split('|')
        if len(p) < 5:
            continue
        d = fields(p[4:])
        if p[3] == 'mkt':
            m = mkt[p[2]]
            m[0] += 1
            m[1] += d.get('bal', 0)
            m[2] += d.get('gap', 0)
            continue
        if p[3] != 'bld':
            continue
        mat, cv, av = d.get('mat', 0), d.get('cv', 0), d.get('av', 1)
        if not isinstance(mat, float) or not isinstance(cv, float) or (mat == 0 and cv == 0):
            continue
        if not isinstance(av, float):
            av = 1.0
        band = 1.0 if av >= 0.999 else round(int(av * 10) / 10, 1)
        for key, tab in (((p[2], band), bands), ((p[2], d.get('t', '?'), 'short' if av < 0.999 else 'full'), types)):
            r = tab[key]
            r[0] += 1
            r[1] += mat
            r[2] += cv
            r[3] += cv / av if av > 0.01 else cv
    print('market lines: country -> n, sum bal, sum gap')
    for c, m in mkt.items():
        print(f'  {c}: {m[0]}  {m[1]:.0f}  {m[2]:.0f}')
    print('\nby availability: country, band -> n, mat, cv, mat/cv, mat/(cv/av)')
    for (c, b), r in sorted(bands.items()):
        print(f'  {c:16} {b:4}  n {r[0]:6}  mat {r[1]:14.0f}  cv {r[2]:14.0f}  mat/cv {r[1] / r[2] if r[2] else 0:6.3f}'
              f'  mat/(cv/av) {r[1] / r[3] if r[3] else 0:6.3f}')
    print('\nbuilding types with shortages (the 25 largest by mat): country, type -> n, mat, cv, mat/cv')
    rows = [(k, r) for k, r in types.items() if k[2] == 'short']
    for (c, t, _), r in sorted(rows, key=lambda kv: -kv[1][1])[:25]:
        full = types.get((c, t, 'full'))
        fr = f'  без нехватки mat/cv {full[1] / full[2]:.3f}' if full and full[2] else ''
        print(f'  {c:16} {t[:40]:40} n {r[0]:5}  mat {r[1]:12.0f}  mat/cv {r[1] / r[2] if r[2] else 0:6.3f}{fr}')


if __name__ == '__main__':
    main()
