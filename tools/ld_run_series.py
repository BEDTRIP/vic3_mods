"""Monthly series of a sandbox run for the analysis page (форк, анализ после R4б).

Usage:  py tools/ld_run_series.py <run>/eflog.txt <out.json> [--until 1847.12]

From the weekly log lines (eflog.txt, written by the fork with zz_ef_logs_on), one point per month (the month's last
line), into <out.json>, one series per line ("key": [[t, v], ...]) so read_text can page it:
  metal.*      EFV WORLD: metal of CBs / banks / pops (gold, silver), bought / sold on the market that week, total in
               gold units (total_ge), silver price in gold (s2g)
  other.*      EFJ WORLD: «прочее» -- the week's change summed (cum: running total), its treasury part
  oth_c.<TAG>  EFJ by country: «прочее» stock (other) for the countries with the largest |other| at the end
  item.*       EFJ by country, summed over the world each month: lvl_pool, lvl_tr, bk_woff (classified lines, stocks)
  money.<TAG>.* EFW: m0, m2, m3, gdp, cbm (CB metal), rate, infl for the logged countries (player and GDP > 20 M)
  flow.*       EFG WORLD: in, out, nocl (not cleared), trade_m, wexp, wimp
  bud.<TAG>.*  EFW|budget: income, expenses (all, fixed), army, debt, credit, pool and its transfer to construction
  acc.<TAG|WORLD>.* EFW|acc: every account of the money tooltip, gdp, exp, imp, surplus, other (monthly)
  lvl          EFJ|lvl: the steps that classified levels bought / sold, with the change of the government's levels
  metal.prod_* / cons_* / buyo_* / sello_* / price_*: the world's markets this week (goods)
  xch.<exchange>.* EFD|xch_month: each exchange's month -- turnover, deals, foreign share, fee, capitalization at the
               market and the base, overheat, members, assets, the year's turnover, its fund (Д.R4б.11)
t is the year as a fraction (1836.5 = July 1836).
"""
import json
import re
import sys
from collections import defaultdict

MON = {'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
       'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12,
       'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8,
       'September': 9, 'October': 10, 'November': 11, 'December': 12}
DATE = re.compile(r'(\w+) (\d+), (\d{4})')


def tdate(s):
    m = DATE.match(s)
    if not m or m.group(1) not in MON:
        return None, None
    y, mo = int(m.group(3)), MON[m.group(1)]
    return y + (mo - 1) / 12, (y, mo)


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
    a = sys.argv[1:]
    path, out = a[0], a[1]
    until = float(a[a.index('--until') + 1]) if '--until' in a else 9999
    uy, um = int(until), round((until - int(until)) * 100) or 12
    lim = (uy, um)
    month = defaultdict(dict)        # key -> {(y,m): (t, v)}
    oth_last = {}                    # country -> other (last)
    oth_month = defaultdict(dict)    # country -> {(y,m): (t,v)}
    item_cty = defaultdict(dict)     # item -> {country: value} (stock, last)
    item_month = defaultdict(dict)   # item -> {(y,m): (t, world sum)}
    cum = 0.0
    lvl = []                         # EFJ|lvl: [t, country, pool multiple, treasury multiple, d_govlv]
    for ln in open(path, encoding='utf-8', errors='replace'):
        if len(ln) < 6 or ln[0] != 'E' or ln[3] != '|':
            continue
        p = ln.rstrip('\n').split('|')
        if len(p) < 4:
            continue
        t, ym = tdate(p[1])
        if t is None or ym > lim:
            continue
        pre, who = p[0], p[2]
        if pre == 'EFV' and who == 'WORLD':
            d = fields(p[3:])
            for k in ('cb_g', 'bank_g', 'pop_g', 'buy_g', 'sell_g', 'cb_s', 'bank_s', 'pop_s', 'buy_s', 'sell_s',
                      'total_ge', 's2g', 'rest_ge', 'prod_g', 'cons_g', 'buyo_g', 'sello_g', 'prod_s', 'cons_s',
                      'buyo_s', 'sello_s', 'price_g', 'price_s'):
                if k in d:
                    month['metal.' + k][ym] = (round(t, 3), d[k])
        elif pre == 'EFJ' and who == 'WORLD' and p[3].startswith('other '):
            d = fields(p[3:])
            cum += d.get('other', 0)
            month['other.cum'][ym] = (round(t, 3), round(cum))
            month['other.week'][ym] = (round(t, 3), d.get('other', 0))
            month['other.tr_week'][ym] = (round(t, 3), d.get('other_tr', 0))
        elif pre == 'EFJ' and p[3] == 'lvl':
            d = fields(p[4:])
            lvl.append([round(t, 3), who, d.get('pool', 0), d.get('tr', 0), d.get('d_govlv', 0)])
        elif pre == 'EFW' and len(p) > 4 and p[3] == 'budget':
            d = fields(p[4:])
            for k, v in d.items():
                month[f'bud.{who}.{k}'][ym] = (round(t, 3), v)
        elif pre == 'EFW' and len(p) > 4 and p[3] == 'acc':
            d = fields(p[4:])
            for k, v in d.items():
                month[f'acc.{who}.{k}'][ym] = (round(t, 3), v)
        elif pre == 'EFD' and len(p) > 4 and p[3] == 'xch_month':
            d = fields(p[4:])
            for k, v in d.items():
                month[f'xch.{who}.{k}'][ym] = (round(t, 3), v)
        elif pre == 'EFJ' and p[3].startswith('other '):
            d = fields(p[3:])
            oth_last[who] = d.get('other', 0)
            oth_month[who][ym] = (round(t, 3), d.get('other', 0))
            for k in ('lvl_pool', 'lvl_tr', 'bk_woff', 'heir_debt', 'heir_tr', 'other_pool', 'other_tr'):
                if k in d:
                    item_cty[k][who] = d[k]
                    item_month[k][ym] = (round(t, 3), round(sum(item_cty[k].values())))
        elif pre == 'EFW':
            d = fields(p[3:])
            for k in ('m0', 'm2', 'm3', 'gdp', 'cbm', 'rate', 'infl', 'circ'):
                if k in d:
                    month[f'money.{who}.{k}'][ym] = (round(t, 3), d[k])
        elif pre == 'EFG' and who == 'WORLD':
            d = fields(p[3:])
            for k in ('in', 'out', 'nocl', 'trade_m', 'wexp', 'wimp'):
                if k in d:
                    month['flow.' + k][ym] = (round(t, 3), d[k])
    res = {k: [v for _, v in sorted(m.items())] for k, m in month.items()}
    for k, m in item_month.items():
        res['item.' + k] = [v for _, v in sorted(m.items())]
    res['lvl'] = lvl
    top = sorted(oth_last, key=lambda c: -abs(oth_last[c]))[:10]
    for c in top:
        res['oth_c.' + c] = [v for _, v in sorted(oth_month[c].items())]
    with open(out, 'w', encoding='utf-8') as f:
        f.write('{\n')
        f.write(',\n'.join(f'{json.dumps(k, ensure_ascii=False)}: {json.dumps(v)}' for k, v in sorted(res.items())))
        f.write('\n}\n')
    print(f'{len(res)} series -> {out}; top other: ' + ', '.join(f'{c} {oth_last[c]:.0f}' for c in top))


if __name__ == '__main__':
    main()
