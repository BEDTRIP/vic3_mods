"""Which budget number explains the treasury's change? (форк, аудит учёта, EFJ bud_chk)

Usage:  py tools/ld_budchk.py <run>/eflog.txt [--top 10]

The receiver of the GUI bridge logs, the same moment: the GUI's weekly income, expenses, balance, one-off (temporary)
income and expenses, the income / expense trends, and the script's total_income, total_expenses, net_total_income,
the treasury (gold) and the debt (principal). For consecutive lines of a country 7 days apart: the change of the
treasury net of debt against each candidate, of the earlier line (lag 1) and of the later (lag 0). The smallest sum
of |change - candidate| names the number the model should take.
"""
import sys
from collections import defaultdict
from datetime import date

MONTHS = {'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
          'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12}


def day(s):
    m, rest = s.split(' ', 1)
    d, y = rest.split(',')
    return date(int(y), MONTHS[m], int(d))


CANDS = {
    'script ti - te': lambda d: d['ti'] - d['te'],
    'script nti': lambda d: d['nti'],
    'gui wbal': lambda d: d['wbal'],
    'gui winc - wexp': lambda d: d['winc'] - d['wexp'],
    'gui trend tinc - texp': lambda d: d['tinc'] - d['texp'],
    'script ti - te + tmp': lambda d: d['ti'] - d['te'] + d['tmpi'] - d['tmpx'],
    'gui wbal + tmp': lambda d: d['wbal'] + d['tmpi'] - d['tmpx'],
}


def main():
    rows = defaultdict(list)
    for ln in open(sys.argv[1], encoding='utf-8', errors='replace'):
        if '|bud_chk|' not in ln or not ln.startswith('EFJ|'):
            continue
        p = ln.rstrip('\n').split('|')
        d = {}
        for x in p[4:]:
            k, _, v = x.partition(' ')
            try:
                d[k] = float(v)
            except ValueError:
                pass
        try:
            rows[p[2]].append((day(p[1]), d))
        except (ValueError, KeyError):
            pass
    tot = defaultdict(float)
    per = defaultdict(lambda: defaultdict(float))
    tmp = defaultdict(float)
    n = 0
    for c, r in rows.items():
        for (d0, a), (d1, b) in zip(r, r[1:]):
            if (d1 - d0).days != 7 or not all(k in a and k in b for k in ('gold', 'principal', 'ti', 'te', 'nti', 'wbal')):
                continue
            ch = (b['gold'] - b['principal']) - (a['gold'] - a['principal'])
            n += 1
            for name, f in CANDS.items():
                for lag, src in (('lag1', a), ('lag0', b)):
                    try:
                        v = abs(ch - f(src))
                    except KeyError:
                        continue
                    tot[(name, lag)] += v
                    per[c][(name, lag)] += v
            tmp[c] += abs(b.get('tmpi', 0)) + abs(b.get('tmpx', 0))
    print(f'pairs {n}, countries {len(rows)}')
    print('candidate                      sum|d(treasury - debt) - candidate|')
    for (name, lag), v in sorted(tot.items(), key=lambda kv: kv[1]):
        print(f'  {name:26} {lag}  {v / 1e6:10.2f}M')
    best = min(tot, key=tot.get) if tot else None
    top = int(sys.argv[sys.argv.index('--top') + 1]) if '--top' in sys.argv else 10
    print(f'countries by the residual of the best ({best}); one-off lines summed')
    for c, d in sorted(per.items(), key=lambda kv: -kv[1].get(best, 0))[:top]:
        print(f'  {c[:30]:30} best {d.get(best, 0) / 1e6:8.2f}M  script ti-te lag1 {d.get(("script ti - te", "lag1"), 0) / 1e6:8.2f}M'
              f'  one-off {tmp[c] / 1e6:8.2f}M')


if __name__ == '__main__':
    main()
