"""Reads the gap probe of a sandbox run (форк, R4б, ночь закрытия, шаг 1; scripted_effects/ld_probe_gap.txt).

Usage:  py tools/ld_probe_gap.py <run>/eflog.txt [--weeks N]

Per probed country (FRA, JAP) and week: the line «engine: the market gap» (EFP gmkt leak) against the market's gap
(all goods and by groups: financial, PSC, metal, vanilla), the pops' income less expenses by strata (EFP gpop) and the
buildings' money (EFP gbld: revenue, materials, wages, income, total expenses, cash and its weekly change). Prints the
weekly rows (every 4th), the sums over the run, the regression of the line on the candidates and the buildings' groups
with the largest sums.
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
            d[k] = v
    return d


def ols(y, xs):
    """Least squares y ~ b0 + sum bi xi; returns (coefs, r2)."""
    n, k = len(y), len(xs) + 1
    if n <= k:
        return None, float('nan')
    X = [[1.0] + [x[i] for x in xs] for i in range(n)]
    A = [[sum(X[r][i] * X[r][j] for r in range(n)) for j in range(k)] for i in range(k)]
    b = [sum(X[r][i] * y[r] for r in range(n)) for i in range(k)]
    # Gauss-Jordan
    for i in range(k):
        p = max(range(i, k), key=lambda r: abs(A[r][i]))
        if abs(A[p][i]) < 1e-12:
            return None, float('nan')
        A[i], A[p] = A[p], A[i]
        b[i], b[p] = b[p], b[i]
        for r in range(k):
            if r != i:
                f = A[r][i] / A[i][i]
                for c in range(i, k):
                    A[r][c] -= f * A[i][c]
                b[r] -= f * b[i]
    coef = [b[i] / A[i][i] for i in range(k)]
    my = sum(y) / n
    fit = [sum(coef[j] * X[r][j] for j in range(k)) for r in range(n)]
    ss = sum((y[r] - my) ** 2 for r in range(n))
    sr = sum((y[r] - fit[r]) ** 2 for r in range(n))
    return coef, (1 - sr / ss) if ss else float('nan')


def main():
    args = sys.argv[1:]
    path = args[0]
    wk = defaultdict(lambda: defaultdict(float))      # (tag, date) -> key -> value
    bgrp = defaultdict(lambda: defaultdict(float))    # (tag, building name) -> key -> sum over weeks
    dates = defaultdict(list)
    for ln in open(path, encoding='utf-8', errors='replace'):
        if not ln.startswith('EFP|'):
            continue
        p = ln.rstrip('\n').split('|')
        if len(p) < 5 or p[3] not in ('gmkt', 'gpop', 'gbld'):
            continue
        date, tag, kind = p[1], p[2], p[3]
        d = fields(p[4:])
        r = wk[(tag, date)]
        if kind == 'gmkt':
            if 'seen' not in r:
                dates[tag].append(date)
            r['seen'] = 1
            for k in ('leak', 'gap', 'gap_fin', 'gap_psc', 'gap_metal', 'buy', 'sell', 'bal', 'bcash', 'savings', 'gdpw'):
                v = d.get(k)
                if isinstance(v, float):
                    r[k] = v
            r['gap_van'] = r['gap'] - r['gap_fin'] - r['gap_psc'] - r['gap_metal']
        elif kind == 'gpop':
            st = d.get('st', '?')
            inc, exp = d.get('inc', 0.0), d.get('exp', 0.0)
            if not isinstance(inc, float) or not isinstance(exp, float):
                continue
            r['pop_inc'] += inc
            r['pop_exp'] += exp
            r['pop_net_' + st] += inc - exp
            r['pop_net'] += inc - exp
            w = d.get('wexp')
            if isinstance(w, float):
                r['pop_wexp'] += w
        else:
            name = d.get('t', '?')
            for k in ('rev', 'mat', 'wage', 'inc', 'texp', 'cash', 'gov', 'wp'):
                v = d.get(k)
                if isinstance(v, float):
                    r['b_' + k] += v
                    bgrp[(tag, name)][k] += v
            bgrp[(tag, name)]['n'] += 1
            sub = 'subsist' in str(name).lower() or 'натурал' in str(name).lower()
            if sub:
                for k in ('rev', 'mat', 'wage', 'cash'):
                    v = d.get(k)
                    if isinstance(v, float):
                        r['bs_' + k] += v
    for tag in sorted(dates):
        ds = dates[tag]
        rows = [wk[(tag, x)] for x in ds]
        for i, r in enumerate(rows):
            r['d_bcash'] = r['b_cash'] - rows[i - 1]['b_cash'] if i else 0.0
            r['b_net'] = r['b_rev'] - r['b_mat'] - r['b_wage']
        print(f'=== {tag}: {len(ds)} weeks {ds[0]} .. {ds[-1]}')
        keys = ['leak', 'gap', 'gap_fin', 'gap_psc', 'gap_metal', 'gap_van', 'pop_inc', 'pop_exp', 'pop_net',
                'pop_net_lower', 'pop_net_middle', 'pop_net_upper', 'b_rev', 'b_mat', 'b_wage', 'b_net', 'b_wp',
                'd_bcash', 'bs_rev', 'bs_wage', 'gdpw']
        print('date        ' + ' '.join(f'{k[:9]:>10}' for k in keys))
        for i, (x, r) in enumerate(zip(ds, rows)):
            if i % 4 == 0:
                print(f'{x:11} ' + ' '.join(f'{r[k]:10.0f}' for k in keys))
        sk = rows[1:]
        print('sum (from week 2):')
        for k in keys:
            print(f'  {k:16} {sum(r[k] for r in sk):14.0f}   per week {sum(r[k] for r in sk) / max(1, len(sk)):12.0f}')
        y = [r['leak'] for r in sk]
        for label, cand in (('gap', ['gap']), ('gap groups', ['gap_fin', 'gap_psc', 'gap_metal', 'gap_van']),
                            ('pop_net', ['pop_net']), ('pop by strata', ['pop_net_lower', 'pop_net_middle', 'pop_net_upper']),
                            ('b_net', ['b_net']), ('pop_net + gap', ['pop_net', 'gap']),
                            ('pop_net + gap groups', ['pop_net', 'gap_fin', 'gap_psc', 'gap_metal', 'gap_van'])):
            coef, r2 = ols(y, [[r[k] for r in sk] for k in cand])
            if coef:
                print(f'  leak ~ {label:22} r2 {r2:5.2f}  b0 {coef[0]:10.0f}  ' +
                      '  '.join(f'{k} {c:6.3f}' for k, c in zip(cand, coef[1:])))
        print('buildings by name (sum over weeks, top 15 by |rev - mat - wage|):')
        grp = [(n, v) for (t, n), v in bgrp.items() if t == tag]
        grp.sort(key=lambda nv: -abs(nv[1]['rev'] - nv[1]['mat'] - nv[1]['wage']))
        for n, v in grp[:15]:
            print(f'  {str(n)[:34]:34} rev {v["rev"]:12.0f} mat {v["mat"]:12.0f} wage {v["wage"]:12.0f} '
                  f'wp {v["wp"]:12.0f} rows {v["n"]:6.0f}')


if __name__ == '__main__':
    main()
