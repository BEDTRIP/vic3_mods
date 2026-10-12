"""Short yearly summary of a sandbox run of the fork (форк, разбор прогонов; R4б).

Usage:  py tools/ld_run_summary.py <run>/eflog.txt [--until 1847.12] [--top 6]

One pass over the log lines (eflog.txt, written with zz_ef_logs_on); prints, short enough for the bridge (py_tool
gives back the last 20 000 characters):
  checks   lines, last date, EFQ lines, bank sums (EFJ|bank_sum: the largest |diff| / |map_diff|), bank failures (EFK)
  world    at each year's last month (EFW|WORLD|acc): M0, M2, M3, pool, treasury, deposits, loans, banks' capital,
           pops' cash and savings; «прочее» (EFJ WORLD other, running total)
  metal    a week's average a year (EFV WORLD): gold / silver mined, consumed, bought / sold by the world's markets
           (orders), bought / sold onto the accounts (buy_ / sell_), held by pops
  levels   EFJ|lvl a year: steps classified as levels bought, multiples of the pool and the treasury, the change of
           the government's levels; the world's lvl_pool / lvl_tr stocks at the year's end
  budget   the largest countries by GDP at the end, a year's average a week (EFW|budget, EFW|acc): income, expenses,
           fixed expenses, army, debt, credit, pool to construction, M2, GDP; PSC (EFZ): points, construction spending
  exchanges the last EFD|xch_month line of each exchange, by the year's turnover
"""
import re
import sys
from collections import defaultdict

MON = {'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
       'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12,
       'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8,
       'September': 9, 'October': 10, 'November': 11, 'December': 12}
DATE = re.compile(r'(\w+) (\d+), (\d{4})')


def ym(s):
    m = DATE.match(s)
    if not m or m.group(1) not in MON:
        return None
    return int(m.group(3)), MON[m.group(1)]


def fields(parts):
    d = {}
    for x in parts:
        k, _, v = x.partition(' ')
        try:
            d[k] = float(v)
        except ValueError:
            pass
    return d


def fmt(v):
    a = abs(v)
    if a >= 1e9:
        return f'{v / 1e9:.2f}B'
    if a >= 1e6:
        return f'{v / 1e6:.2f}M'
    if a >= 1e4:
        return f'{v / 1e3:.0f}k'
    if a >= 100:
        return f'{v:.0f}'
    return f'{v:.3g}'


def main():
    a = sys.argv[1:]
    path = a[0]
    until = float(a[a.index('--until') + 1]) if '--until' in a else 9999
    top = int(a[a.index('--top') + 1]) if '--top' in a else 6
    lim = (int(until), round((until - int(until)) * 100) or 12)
    n = 0
    last = None
    efq = 0
    diff = mdiff = 0.0
    fails = 0
    world = {}                                   # year -> acc fields (last month)
    other = 0.0
    other_y = {}
    metal = defaultdict(lambda: defaultdict(list))   # year -> key -> weekly values
    lvl = defaultdict(lambda: [0, 0.0, 0.0, 0.0])   # year -> steps, pool, tr, d_govlv
    items = {}                                   # (item, country) -> stock
    items_y = defaultdict(dict)
    bud = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))   # country -> year -> key -> values
    gdp_last = {}
    xch = {}
    for ln in open(path, encoding='utf-8', errors='replace'):
        if len(ln) < 6 or ln[0] != 'E' or ln[3] != '|':
            continue
        p = ln.rstrip('\n').split('|')
        if len(p) < 4:
            continue
        d8 = ym(p[1])
        if d8 is None or d8 > lim:
            continue
        n += 1
        last = p[1]
        y = d8[0]
        pre, who, k3 = p[0], p[2], p[3]
        if pre == 'EFQ':
            efq += 1
        elif pre == 'EFK' and k3 == 'bank_fail':
            fails += 1
        elif pre == 'EFJ' and k3 == 'bank_sum':
            d = fields(p[4:])
            diff = max(diff, abs(d.get('diff', 0)))
            mdiff = max(mdiff, abs(d.get('map_diff', 0)))
        elif pre == 'EFW' and len(p) > 4 and k3 == 'acc':
            d = fields(p[4:])
            if who == 'WORLD':
                world[y] = d
            else:
                for k in ('m2', 'gdp'):
                    if k in d:
                        bud[who][y][k].append(d[k])
                if 'gdp' in d:
                    gdp_last[who] = d['gdp']
        elif pre == 'EFW' and len(p) > 4 and k3 == 'budget':
            d = fields(p[4:])
            for k, v in d.items():
                bud[who][y][k].append(v)
        elif pre == 'EFZ':
            d = fields(p[3:])
            for k in ('pts', 'total', 'csec_lv'):
                if k in d:
                    bud[who][y]['psc_' + k].append(d[k])
        elif pre == 'EFV' and who == 'WORLD':
            d = fields(p[3:])
            for k, v in d.items():
                metal[y][k].append(v)
        elif pre == 'EFJ' and k3 == 'lvl':
            d = fields(p[4:])
            r = lvl[y]
            r[0] += 1
            r[1] += d.get('pool', 0)
            r[2] += d.get('tr', 0)
            r[3] += d.get('d_govlv', 0)
        elif pre == 'EFJ' and who == 'WORLD' and k3.startswith('other '):
            other += fields(p[3:]).get('other', 0)
            other_y[y] = other
        elif pre == 'EFJ' and k3.startswith('other '):
            d = fields(p[3:])
            for k in ('lvl_pool', 'lvl_tr'):
                if k in d:
                    items[(k, who)] = d[k]
                    items_y[y][k] = sum(v for (kk, _), v in items.items() if kk == k)
        elif pre == 'EFD' and len(p) > 4 and k3 == 'xch_month':
            xch[who] = (p[1], fields(p[4:]))
    out = [f'== checks: {n} lines to {last}; EFQ {efq}; bank sums max |diff| {diff:.2f}, |map_diff| {mdiff:.2f}; '
           f'bank failures {fails}']
    out.append('== world at each year\'s end (EFW|WORLD|acc) and «прочее» running total')
    keys = ('m0', 'm2', 'm3', 'pool', 'treasury', 'deposits', 'loans', 'bkcap', 'cash', 'savings', 'gdp')
    out.append('year ' + ' '.join(f'{k:>8}' for k in keys) + '    other')
    for y in sorted(world):
        d = world[y]
        out.append(f'{y} ' + ' '.join(f'{fmt(d.get(k, 0)):>8}' for k in keys) + f' {fmt(other_y.get(y, 0)):>8}')
    out.append('== metal, a week\'s average a year (EFV WORLD; goods: prod/cons/buyo/sello -- markets; buy/sell -- '
               'onto / off the accounts, units)')
    mk = ('prod_g', 'cons_g', 'buyo_g', 'sello_g', 'buy_g', 'sell_g', 'pop_g', 'prod_s', 'cons_s', 'buyo_s', 'sello_s',
          'buy_s', 'sell_s', 'pop_s')
    out.append('year ' + ' '.join(f'{k:>8}' for k in mk))
    for y in sorted(metal):
        out.append(f'{y} ' + ' '.join(f'{fmt(sum(metal[y][k]) / len(metal[y][k]) if metal[y][k] else 0):>8}' for k in mk))
    out.append('== levels bought (EFJ|lvl a year: steps, pool multiples, treasury multiples, d_govlv) and stocks')
    for y in sorted(set(lvl) | set(items_y)):
        r = lvl.get(y, [0, 0, 0, 0])
        it = items_y.get(y, {})
        out.append(f'{y} steps {r[0]} pool {r[1]:.0f} tr {r[2]:.0f} d_govlv {r[3]:.0f} | lvl_pool {fmt(it.get("lvl_pool", 0))} '
                   f'lvl_tr {fmt(it.get("lvl_tr", 0))}')
    big = sorted(gdp_last, key=lambda c: -gdp_last[c])[:top]
    bk = ('inc', 'exp', 'fix_exp', 'mil', 'debt', 'credit', 'pool_constr', 'm2', 'gdp', 'psc_pts', 'psc_total',
          'psc_csec_lv')
    for c in big:
        out.append(f'== budget {c}, a year\'s average (a week)')
        out.append('year ' + ' '.join(f'{k:>8}' for k in bk))
        for y in sorted(bud[c]):
            dd = bud[c][y]
            out.append(f'{y} ' + ' '.join(f'{fmt(sum(dd[k]) / len(dd[k]) if dd[k] else 0):>8}' for k in bk))
    out.append('== exchanges, the last month (EFD|xch_month), by the year\'s turnover')
    xk = ('to_g', 'year_to_g', 'deals', 'foreign', 'fee_g', 'cap_g', 'cap_base_g', 'heat', 'members', 'assets', 'fund_g',
          'nav', 'has')
    out.append(f'{"exchange":<24} ' + ' '.join(f'{k:>9}' for k in xk))
    for c, (dt, d) in sorted(xch.items(), key=lambda kv: -kv[1][1].get('year_to_g', kv[1][1].get('to_g', 0) * 12)):
        if d.get('members', 0) == 0 and d.get('to_g', 0) == 0:
            continue
        out.append(f'{c[:24]:<24} ' + ' '.join(f'{fmt(d.get(k, 0)):>9}' for k in xk))
    print('\n'.join(out))


if __name__ == '__main__':
    main()
