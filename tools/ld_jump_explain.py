"""Weekly jumps of a country's «прочее» and the accounts that moved that week (форк, R4б, Д.R4б.32).

Usage:  py tools/ld_jump_explain.py <run>/eflog.txt [--jump 300000] [--top 40]

For every week where a country's «прочее» (EFJ other, d_other) moved by at least --jump: the change of the pool and of
the banks' book that week, and the book's parts from the same week's lines -- pops' deposits (EFJ dep), the banks'
capital (EFJ capital), non-residents' deposits in the register (EFR nr_dep) and the part posted into the pool at the
step (EFR f_nr_dep), the loans (EFR cc_debt, bc_debt), the foreign bonds (EFB pbonds); the treasury's part (d_other_tr)
and the explained lines (lvl_pool, lvl_tr, bk_woff, heir_*). With the book's parts in the EFJ line (b_*) -- their
changes, the biggest three. The next week's d_other beside it shows a swing (-x then +x) -- a timing error, not a
loss. «дн» -- days since the country's previous EFJ line (a line is written only for a big week or a log country:
more than 7 -- the changes span several weeks).
Через мост: py_tool("ld_jump_explain", ["runs/<id>/eflog.txt"]).
"""
import sys
from collections import defaultdict
from datetime import date

MONTHS = {'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
          'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12}
BOOK = ['b_nr', 'b_nrp', 'b_fd', 'b_cbd', 'b_gov', 'b_cc', 'b_bc', 'b_bonds', 'b_inv', 'b_priv']


def day(s):
    m, rest = s.split(' ', 1)
    d, y = rest.split(',')
    return date(int(y), MONTHS[m], int(d))


sys.stdout.reconfigure(encoding="utf-8")


def fields(parts):
    d = {}
    for x in parts:
        k, _, v = x.rpartition(' ')
        try:
            d[k] = float(v)
        except ValueError:
            pass
    return d


def main():
    a = sys.argv[1:]
    path = a[0]
    jump = float(a[a.index('--jump') + 1]) if '--jump' in a else 300000
    top = int(a[a.index('--top') + 1]) if '--top' in a else 40
    wk = defaultdict(list)            # country -> [(date, EFJ other fields)]
    efr = {}                          # (country, date) -> EFR fields
    efb = {}                          # (country, date) -> EFB fields
    for ln in open(path, encoding='utf-8', errors='replace'):
        if len(ln) < 6 or ln[0] != 'E' or ln[3] != '|':
            continue
        p = ln.rstrip('\n').split('|')
        if len(p) < 4:
            continue
        pre, dt, who = p[0], p[1], p[2]
        if pre == 'EFJ' and who != 'WORLD' and p[3].startswith('other '):
            wk[who].append((dt, fields(p[3:])))
        elif pre == 'EFR':
            efr[(who, dt)] = fields(p[3:])
        elif pre == 'EFB':
            efb[(who, dt)] = fields(p[3:])
    rows = []
    for c, ws in wk.items():
        for i, (dt, d) in enumerate(ws):
            do = d.get('d_other', 0)
            if abs(do) < jump or i == 0:
                continue
            pd = ws[i - 1][1]
            nxt = ws[i + 1][1].get('d_other', 0) if i + 1 < len(ws) else 0
            r, rp = efr.get((c, dt), {}), efr.get((c, ws[i - 1][0]), {})
            b, bp = efb.get((c, dt), {}), efb.get((c, ws[i - 1][0]), {})

            def dd(k, cur=d, prev=pd):
                return cur.get(k, 0) - prev.get(k, 0)
            rows.append((abs(do), c, dt, do, nxt, dd('pool'), dd('book'), dd('dep'), dd('capital'),
                         dd('nr_dep', r, rp), r.get('f_nr_dep', 0), dd('cc_debt', r, rp) + dd('bc_debt', r, rp),
                         dd('pbonds', b, bp), d.get('d_other_tr', 0),
                         dd('lvl_pool') + dd('lvl_tr') + dd('bk_woff') + dd('heir_debt') + dd('heir_tr'),
                         (day(dt) - day(ws[i - 1][0])).days,
                         sorted(((k[2:], dd(k)) for k in BOOK if k in d), key=lambda kv: -abs(kv[1]))[:3]))
    rows.sort(reverse=True)
    hdr = ['страна', 'дата', 'd_other', 'след.', 'd_pool', 'd_book', 'd_dep', 'd_cap', 'd_nr_dep', 'f_nr_dep',
           'd_loans', 'd_pbonds', 'd_oth_tr', 'd_статьи', 'дн']
    print(f'{hdr[0]:24} {hdr[1]:18} ' + ' '.join(f'{h:>10}' for h in hdr[2:]) + '  книга')
    for x in rows[:top]:
        print(f'{x[1][:24]:24} {x[2][:18]:18} ' + ' '.join(f'{v:10.0f}' for v in x[3:-1]) + '  '
              + ' '.join(f'{k} {v:.0f}' for k, v in x[-1] if abs(v) >= 1))
    print(f'скачков >= {jump:.0f}: {len(rows)}')


if __name__ == '__main__':
    main()
