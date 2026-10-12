"""Reads the leak probe of a sandbox run (форк, R4б, ночь: утечки; scripted_effects/ld_probe_leak.txt).

Usage:  py tools/ld_probe_leak.py <run>/eflog.txt

Per probed country and week: the card residuals (EFO b_rest, EFR leak) against the candidates -- the pops' income less
their expenses (sum over EFP|pop lines: inc - exp, inc - wexp), the market's buy / sell orders and balance, the
buildings' weekly profit and cash (EFP|mkt). Prints the weekly rows (every 4th), the sums and the correlations of the
residuals with each candidate and its weekly change.
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


def corr(a, b):
    n = len(a)
    if n < 3:
        return float('nan')
    ma, mb = sum(a) / n, sum(b) / n
    sa = sum((x - ma) ** 2 for x in a) ** .5
    sb = sum((y - mb) ** 2 for y in b) ** .5
    if not sa or not sb:
        return float('nan')
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / sa / sb


def main():
    rows = defaultdict(lambda: defaultdict(float))     # (country, date) -> key -> value
    order = []
    tags = {}
    for ln in open(sys.argv[1], encoding='utf-8', errors='replace'):
        if not ln.startswith(('EFO|', 'EFR|', 'EFP|')):
            continue
        p = ln.rstrip('\n').split('|')
        key = (p[2], p[1])
        r = rows[key]
        if p[0] == 'EFO':
            d = fields(p[3:])
            r['b_rest'] = d.get('b_rest', 0)
            r['abr_rest'] = d.get('abr_rest', 0)
            r['seen'] = 1
            order.append(key)
        elif p[0] == 'EFR':
            r['leak'] = fields(p[3:]).get('leak', 0)
        elif p[3] == 'mkt':
            d = fields(p[4:])
            tags[p[2]] = d.get('tag', '?')
            for k in ('buy', 'sell', 'bal', 'bprofit', 'bcash', 'gdpw'):
                if isinstance(d.get(k), float):
                    r[k] = d[k]
            r['probe'] = 1
        elif p[3] == 'pop':
            d = fields(p[4:])
            inc, exp, wexp = d.get('inc', 0), d.get('exp', 0), d.get('wexp', 0)
            r['n_pop'] += 1
            r['size'] += d.get('size', 0) if isinstance(d.get('size'), float) else 0
            r['inc'] += inc
            r['exp'] += exp
            r['wexp'] += wexp
            r['surplus'] += inc - exp
            r['surplus_w'] += inc - wexp
    by = defaultdict(list)
    for key in order:
        if rows[key].get('probe'):
            by[key[0]].append(key)
    for c, keys in by.items():
        print(f'== {c} (tag {tags.get(c)}), {len(keys)} weeks')
        cols = ('b_rest', 'leak', 'abr_rest', 'surplus', 'surplus_w', 'inc', 'exp', 'wexp', 'buy', 'sell', 'bal',
                'bprofit', 'bcash', 'gdpw', 'n_pop')
        print('date               ' + ' '.join(f'{k:>11}' for k in cols))
        for i, k in enumerate(keys):
            if i % 4 == 0:
                r = rows[k]
                print(f'{k[1]:<18} ' + ' '.join(f'{r.get(x, 0):>11.0f}' for x in cols))
        tot = {x: sum(rows[k].get(x, 0) for k in keys) for x in ('b_rest', 'leak', 'abr_rest', 'surplus', 'surplus_w', 'bal', 'bprofit')}
        print('sums: ' + ', '.join(f'{x} {v:.0f}' for x, v in tot.items()))
        sell_buy = [rows[k].get('sell', 0) - rows[k].get('buy', 0) for k in keys]
        dcash = [0] + [rows[keys[i]].get('bcash', 0) - rows[keys[i - 1]].get('bcash', 0) for i in range(1, len(keys))]
        cands = {'surplus': [rows[k].get('surplus', 0) for k in keys],
                 'surplus_w': [rows[k].get('surplus_w', 0) for k in keys],
                 'bal': [rows[k].get('bal', 0) for k in keys],
                 'sell-buy': sell_buy,
                 'bprofit': [rows[k].get('bprofit', 0) for k in keys],
                 'd_bcash': dcash}
        for res in ('b_rest', 'leak'):
            y = [rows[k].get(res, 0) for k in keys]
            print(f'corr {res}: ' + ', '.join(f'{n} {corr(y[1:], v[1:]):+.2f}' for n, v in cands.items()))
            print(f'  mean {res} {sum(y) / len(y):.0f}; means: ' + ', '.join(f'{n} {sum(v) / len(v):.0f}' for n, v in cands.items()))


if __name__ == '__main__':
    main()
