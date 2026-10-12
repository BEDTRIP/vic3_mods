"""Monthly data of a sandbox run of the fork for the analysis page (форк, разбор прогонов; R4б).

Usage:  py tools/ld_run_pagedata.py <run>/eflog.txt <out.jsonl> [--until 1847.12] [--top 10] [--also "A,B"]

One pass over eflog.txt; one month = the month's last value of a stock, the average of a week's flow. Writes JSON
lines, one series per line ({"k": key, "v": [values by month]}, the first line {"k": "t", "v": [months as 1836.0,
1836.083, ...]}), so read_text can page it:
  w.<key>      EFW|WORLD|acc stocks; w.other -- «прочее» running total (EFJ WORLD other), w.other_tr -- its treasury part
  m.<key>      EFV WORLD: metal a week (prod/cons/buyo/sello -- markets, goods; buy/sell -- onto / off the accounts,
               units, running totals turned into a week's amount: buyw_/sellw_), prices, stocks by holder
  l.<key>      EFJ|lvl a month: steps, pool / treasury multiples, d_govlv; l.lvl_pool / l.lvl_tr -- the world's stocks
  c.<country>.<key>  the largest countries by GDP at the end (+ --also): EFW|budget, EFW|acc (m2, gdp, price, cover,
               infl, treasury, bkcap, pool, other), EFZ (pts, total, csec_lv)
  x.<exchange>.<key>  EFD|xch_month of the exchanges with the largest year's turnover: to_g, cap_g, heat, members, foreign
  fail         EFK|bank_fail lines (date, country, the rest)
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
GOLD_U, SILVER_U = 100, 775       # account units a good of gold / silver


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


def r4(v):
    if v is None:
        return None
    if v == 0:
        return 0
    from math import floor, log10
    return round(v, -int(floor(log10(abs(v)))) + 3)


def main():
    a = sys.argv[1:]
    path, out = a[0], a[1]
    until = float(a[a.index('--until') + 1]) if '--until' in a else 9999
    top = int(a[a.index('--top') + 1]) if '--top' in a else 10
    also = [x for x in (a[a.index('--also') + 1].split(',') if '--also' in a else []) if x]
    lim = (int(until), round((until - int(until)) * 100) or 12)
    last = defaultdict(dict)                  # key -> {month: value} (stock: last)
    avg = defaultdict(lambda: defaultdict(list))   # key -> month -> values (flow: average)
    summ = defaultdict(lambda: defaultdict(float))  # key -> month -> sum
    other = 0.0
    other_tr = 0.0
    items = {}
    gdp = {}
    cty = defaultdict(lambda: defaultdict(dict))     # country -> key -> {month: last}
    cty_avg = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    xch = defaultdict(lambda: defaultdict(dict))
    xyear = {}
    fails = []
    for ln in open(path, encoding='utf-8', errors='replace'):
        if len(ln) < 6 or ln[0] != 'E' or ln[3] != '|':
            continue
        p = ln.rstrip('\n').split('|')
        if len(p) < 4:
            continue
        mo = ym(p[1])
        if mo is None or mo > lim:
            continue
        pre, who, k3 = p[0], p[2], p[3]
        if pre == 'EFW' and len(p) > 4 and k3 == 'acc':
            d = fields(p[4:])
            if who == 'WORLD':
                for k, v in d.items():
                    last['w.' + k][mo] = v
            else:
                for k, v in d.items():
                    cty[who][k][mo] = v
                if 'gdp' in d:
                    gdp[who] = d['gdp']
        elif pre == 'EFW' and len(p) > 4 and k3 == 'budget':
            for k, v in fields(p[4:]).items():
                cty_avg[who][k][mo].append(v)
        elif pre == 'EFZ':
            d = fields(p[3:])
            for k in ('pts', 'total', 'csec_lv', 'csec_profit'):
                if k in d:
                    cty_avg[who]['psc_' + k][mo].append(d[k])
        elif pre == 'EFV' and who == 'WORLD':
            d = fields(p[3:])
            for k, v in d.items():
                avg['m.' + k][mo].append(v)
                if k in ('buy_g', 'sell_g', 'buy_s', 'sell_s'):
                    last['m.last_' + k][mo] = v
        elif pre == 'EFJ' and k3 == 'lvl':
            d = fields(p[4:])
            summ['l.steps'][mo] += 1
            summ['l.pool'][mo] += d.get('pool', 0)
            summ['l.tr'][mo] += d.get('tr', 0)
            summ['l.d_govlv'][mo] += d.get('d_govlv', 0)
        elif pre == 'EFJ' and who == 'WORLD' and k3.startswith('other '):
            d = fields(p[3:])
            other += d.get('other', 0)
            other_tr += d.get('other_tr', 0)
            last['w.other'][mo] = other
            last['w.other_tr'][mo] = other_tr
            summ['w.other_month'][mo] += d.get('other', 0)
        elif pre == 'EFJ' and k3.startswith('other '):
            d = fields(p[3:])
            for k in ('lvl_pool', 'lvl_tr'):
                if k in d:
                    items[(k, who)] = d[k]
                    last['l.' + k][mo] = sum(v for (kk, _), v in items.items() if kk == k)
        elif pre == 'EFD' and len(p) > 4 and k3 == 'xch_month':
            d = fields(p[4:])
            for k in ('to_g', 'cap_g', 'cap_base_g', 'heat', 'members', 'foreign', 'fee_g', 'assets', 'deals'):
                if k in d:
                    xch[who][k][mo] = d[k]
            xyear[who] = d.get('year_to_g', 0) or d.get('to_g', 0) * 12
        elif pre == 'EFK' and k3 == 'bank_fail':
            fails.append(p[1:])
    months = sorted({m for s in list(last.values()) + [dict.fromkeys(v) for v in avg.values()] for m in s})
    idx = {m: i for i, m in enumerate(months)}
    rows = [{'k': 't', 'v': [round(y + (m - 1) / 12, 3) for y, m in months]}]

    def series(dm):
        v = [None] * len(months)
        for m, x in dm.items():
            if m in idx:
                v[idx[m]] = r4(x)
        return v
    for k in sorted(last):
        rows.append({'k': k, 'v': series(last[k])})
    for k in sorted(avg):
        rows.append({'k': k, 'v': series({m: sum(x) / len(x) for m, x in avg[k].items()})})
    for k in sorted(summ):
        rows.append({'k': k, 'v': series(summ[k])})
    # running totals of metal bought / sold onto the accounts -> a week's amount in goods
    for metal, u in (('g', GOLD_U), ('s', SILVER_U)):
        for side in ('buy', 'sell'):
            dm = last.get(f'm.last_{side}_{metal}', {})
            ms = sorted(dm)
            wk = {}
            for i in range(1, len(ms)):
                y0, m0 = ms[i - 1]
                y1, m1 = ms[i]
                weeks = ((y1 - y0) * 12 + (m1 - m0)) * 52 / 12
                wk[ms[i]] = (dm[ms[i]] - dm[ms[i - 1]]) / weeks / u
            rows.append({'k': f'm.{side}w_{metal}', 'v': series(wk)})
    big = sorted(gdp, key=lambda c: -gdp[c])[:top]
    for c in also:
        if c not in big and c in gdp:
            big.append(c)
    rows.append({'k': 'countries', 'v': big})
    for c in big:
        for k in ('m2', 'gdp', 'price', 'cover', 'infl', 'treasury', 'bkcap', 'pool', 'other', 'loans', 'deposits',
                  'surplus', 'm0'):
            if k in cty[c]:
                rows.append({'k': f'c.{c}.{k}', 'v': series(cty[c][k])})
        for k, dm in cty_avg[c].items():
            rows.append({'k': f'c.{c}.{k}', 'v': series({m: sum(x) / len(x) for m, x in dm.items()})})
    xs = sorted(xyear, key=lambda c: -xyear[c])[:top]
    rows.append({'k': 'exchanges', 'v': xs})
    for c in xs:
        for k, dm in xch[c].items():
            rows.append({'k': f'x.{c}.{k}', 'v': series(dm)})
    rows.append({'k': 'fail', 'v': fails})
    with open(out, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, separators=(',', ':')) + '\n')
    print(f'{len(rows)} series, {len(months)} months -> {out}; countries {", ".join(big)}')


if __name__ == '__main__':
    main()
