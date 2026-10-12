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
        if not ln.startswith(('EFO|', 'EFR|', 'EFP|', 'EFJ|')):
            continue
        p = ln.rstrip('\n').split('|')
        if p[0] == 'EFJ':
            if len(p) > 4 and p[3] == 'lvl':
                d = fields(p[4:])
                rows[(p[2], p[1])]['lvl_pool'] += d.get('pool', 0) if isinstance(d.get('pool'), float) else 0
                rows[(p[2], p[1])]['lvl_tr'] += d.get('tr', 0) if isinstance(d.get('tr'), float) else 0
            continue
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
        elif p[3] == 'abr':
            for k, v in fields(p[4:]).items():
                if isinstance(v, float):
                    r['a_' + k] = v
        elif p[3] == 'inv':
            for k, v in fields(p[4:]).items():
                if isinstance(v, float):
                    r['i_' + k] = v
        elif p[3] == 'invdesc':
            r['desc'] = '|'.join(p[4:])[:300]
        elif p[3] == 'bld':
            d = fields(p[4:])
            r['n_bld'] += 1
            for k in ('rev', 'mat', 'wage', 'inc', 'texp', 'cash', 'maxc', 'trade', 'tax', 'gov', 'cg', 'wp'):
                if isinstance(d.get(k), float):
                    r['b_' + k] += d[k]
            r['b_full'] += 1 if isinstance(d.get('cash'), float) and isinstance(d.get('maxc'), float) and \
                d['maxc'] > 0 and d['cash'] >= d['maxc'] * 0.999 else 0
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
        if any(rows[k].get('a_d_abroad') is not None and 'a_abroad' in rows[k] for k in keys):
            ak = [k for k in keys if 'a_abroad' in rows[k]]
            acols = ('abr_rest', 'a_d_abroad', 'd_fxm', 'd_abr_rq', 'd_liab', 'a_fx_in', 'a_fx_out', 'a_cur_out',
                     'a_own_back', 'a_nr_xch', 'a_xch_abr', 'a_fxint', 'a_abr_rq', 'a_liab')
            print('abroad: date      ' + ' '.join(f'{k:>10}' for k in acols))
            prev = None
            tot = defaultdict(float)
            for k in ak:
                r = rows[k]
                if prev:
                    for a, b in (('d_fass', 'a_fassets'), ('d_fxm', 'a_fxm'), ('d_liab', 'a_liab'), ('d_blh', 'a_blh'),
                                 ('d_abr_rq', 'a_abr_rq')):
                        r[a] = r.get(b, 0) - prev.get(b, 0)
                prev = r
                for x in acols:
                    tot[x] += r.get(x, 0)
            for i, k in enumerate(ak):
                if i % 4 == 0:
                    r = rows[k]
                    print(f'{k[1]:<18} ' + ' '.join(f'{r.get(x, 0):>10.0f}' for x in acols))
            print('abroad sums: ' + ', '.join(f'{x} {tot[x]:.0f}' for x in acols if not x.startswith(('a_fxm', 'a_liab', 'a_par', 'a_abr_rq'))))
        if any('i_auto' in rows[k] for k in keys):
            ik = [k for k in keys if 'i_auto' in rows[k]]
            n = 0
            for i in range(1, len(ik)):
                a, b = rows[ik[i - 1]], rows[ik[i]]
                if b.get('lvl_pool') or b['i_auto'] != a['i_auto'] or b.get('i_privlv') != a.get('i_privlv'):
                    n += 1
                    if n <= 25:
                        print(f"inv {ik[i][1]:<18} auto {a['i_auto']:.0f}->{b['i_auto']:.0f} privlv {a.get('i_privlv', 0):.0f}->"
                              f"{b.get('i_privlv', 0):.0f} govlv {a.get('i_govlv', 0):.0f}->{b.get('i_govlv', 0):.0f} "
                              f"lvl_pool {b.get('lvl_pool', 0):.0f} lvl_tr {b.get('lvl_tr', 0):.0f} pool {b.get('i_pool', 0):.0f} "
                              f"chg {b.get('i_chg', 0):.0f}")
            print('last desc: ' + rows[ik[-1]].get('desc', '') if isinstance(rows[ik[-1]].get('desc'), str) else '')
        if any(rows[k].get('n_bld') for k in keys):
            bcols = ('b_rest', 'surplus', 'b_rev', 'b_mat', 'b_wage', 'b_inc', 'b_texp', 'b_wp', 'b_cash', 'b_maxc',
                     'b_trade', 'b_tax', 'b_gov', 'b_cg', 'b_full', 'n_bld')
            print('buildings: date ' + ' '.join(f'{k:>11}' for k in bcols))
            for i, k in enumerate(keys):
                if i % 4 == 0 and rows[k].get('n_bld'):
                    r = rows[k]
                    print(f'{k[1]:<18} ' + ' '.join(f'{r.get(x, 0):>11.0f}' for x in bcols))
            bk = [k for k in keys if rows[k].get('n_bld')]
            dc = [0] + [rows[bk[i]]['b_cash'] - rows[bk[i - 1]]['b_cash'] for i in range(1, len(bk))]
            for name, v in (('d_cash(sum bld)', dc),
                            ('rev-mat-wage', [rows[k]['b_rev'] - rows[k]['b_mat'] - rows[k]['b_wage'] for k in bk]),
                            ('inc', [rows[k]['b_inc'] for k in bk]), ('wp', [rows[k]['b_wp'] for k in bk])):
                y = [rows[k]['b_rest'] for k in bk]
                print(f'  {name}: mean {sum(v) / len(v):.0f}, corr with b_rest {corr(y[1:], v[1:]):+.2f}')
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
