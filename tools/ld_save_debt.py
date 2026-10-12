"""Government debt of every country in a text save (форк, разбор R4б, В.R4б.14).

Usage:  py tools/ld_save_debt.py [save ...] [--top N]
        save -- names in "save games" or full paths (default autosave.v3)

Per save: the date and a table of the N largest countries by GDP (default 25) -- GDP, treasury, investment pool,
credit limit, debt (principal), debt / limit, debt / GDP, the last week's income and expenses (the engine's budget,
as save_money_check reads it); then the world: how many countries have debt, over half the limit, at the limit.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from save_money_check import SAVES, block  # noqa: E402

sys.stdout.reconfigure(encoding='utf-8')


def num(rec, key):
    g = re.search(r'\n\t\t' + key + r'=([-\d.]+)', rec)
    return float(g.group(1)) if g else 0.0


def gdp_of(rec):
    g = re.search(r'\tgdp=\{.*?values=\{ ([^}]*)\}', rec, re.S)
    return float(g.group(1).split()[-1]) if g else 0.0


def budget(rec, key):
    g = re.search(r'\n\t\t' + key + r'=\{ ([^}]*)\}', rec)
    return sum(float(x) for x in g.group(1).split()) if g else 0.0


def m(x):
    return f'{x / 1e6:8.2f}M'


def main():
    a = sys.argv[1:]
    top = 25
    if '--top' in a:
        i = a.index('--top')
        top = int(a[i + 1])
        del a[i:i + 2]
    for path in a or ['autosave.v3']:
        if not os.path.isabs(path):
            path = os.path.join(SAVES, path)
        s = open(path, 'rb').read().decode('utf-8', 'replace')
        date = re.search(r'game_date=([\d.]+)', s).group(1)
        seg, _ = block(s, 'country_manager')
        rows = []
        for mm in re.finditer(r'\n(\d+)=\{\n(?:\t[^\n]*\n){0,3}?\tdefinition="(\w+)"', seg):
            rec = seg[mm.start():seg.find('\n}\n', mm.start())]
            g = gdp_of(rec)
            if g <= 0:
                continue
            rows.append((mm.group(2), g, num(rec, 'money'), num(rec, 'investment_pool'), num(rec, 'credit'),
                         num(rec, 'principal'), budget(rec, 'weekly_income'), budget(rec, 'weekly_expenses')))
        rows.sort(key=lambda r: -r[1])
        print(f'== {os.path.basename(path)}  date {date}  countries {len(rows)}')
        print(f'{"tag":<5}{"gdp":>10}{"treasury":>10}{"pool":>10}{"credit":>10}{"debt":>10}{"debt/lim":>9}'
              f'{"debt/gdp":>9}{"inc/wk":>10}{"exp/wk":>10}')
        for t, g, tr, pool, cr, debt, inc, exp in rows[:top]:
            print(f'{t:<5}{m(g):>10}{m(tr):>10}{m(pool):>10}{m(cr):>10}{m(debt):>10}'
                  f'{(debt / cr if cr else 0):>9.2f}{(debt / g if g else 0):>9.2f}{inc:>10.0f}{exp:>10.0f}')
        with_debt = [r for r in rows if r[5] > 0]
        half = [r for r in rows if r[4] and r[5] / r[4] > 0.5]
        full = [r for r in rows if r[4] and r[5] / r[4] > 0.95]
        tot_g = sum(r[1] for r in rows)
        print(f'world: debt {m(sum(r[5] for r in rows))} = {sum(r[5] for r in rows) / tot_g:.2f} of GDP; with debt '
              f'{len(with_debt)} of {len(rows)}, over half the limit {len(half)}, at the limit {len(full)}; pool '
              f'{m(sum(r[3] for r in rows))}')


if __name__ == '__main__':
    main()
