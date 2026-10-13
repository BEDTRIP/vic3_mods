"""Do the engine's flow numbers and the measured changes of the accounts belong to the same week? (форк, аудит учёта)

Usage:  py tools/ld_lagcheck.py <run>/eflog.txt [--top 12]

From the weekly EFW line of each logged country: the treasury's change (d_treasury) against the budget the step read
(budget), and the pool's change (d_pool) against the pops' contribution less the transfer to construction (contrib -
transfer). For pairs of consecutive steps 7 days apart: the sum of |change - flow| with the flow of the same step (lag
0) and of the step before (lag 1). Lag 1 clearly smaller -- the model reconciles numbers of different weeks.
The GUI bridge (EFR ext, the budget's lines outside the accounts): the step uses the latest numbers it got -- if they
are a week old, the leak computed with the next step's ext (leak + ext - ext_next) is smaller than the leak as logged.
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


def fields(parts):
    d = {}
    for x in parts:
        k, _, v = x.partition(' ')
        try:
            d[k] = float(v)
        except ValueError:
            pass
    return d


PAIRS = (('treasury', 'd_treasury', lambda d: d.get('budget', 0.0)),
         ('pool', 'd_pool', lambda d: d.get('contrib', 0.0) - d.get('transfer', 0.0)))


def main():
    rows = defaultdict(list)
    efr = defaultdict(list)
    for ln in open(sys.argv[1], encoding='utf-8', errors='replace'):
        if ln.startswith('EFR|'):
            p = ln.rstrip('\n').split('|')
            try:
                efr[p[2]].append((day(p[1]), fields(p[3:])))
            except (ValueError, KeyError):
                pass
            continue
        if not ln.startswith('EFW|') or '|m0 ' not in ln:
            continue
        p = ln.rstrip('\n').split('|')
        try:
            rows[p[2]].append((day(p[1]), fields(p[3:])))
        except (ValueError, KeyError):
            continue
    tot = {k: [0.0, 0.0, 0] for k, _, _ in PAIRS}
    per = []
    for c, r in rows.items():
        acc = {k: [0.0, 0.0, 0] for k, _, _ in PAIRS}
        for (d0, a), (d1, b), (d2, cur) in zip(r, r[1:], r[2:]):
            if (d2 - d1).days != 7 or (d1 - d0).days != 7:
                continue
            for k, ch, fl in PAIRS:
                if ch not in cur:
                    continue
                acc[k][0] += abs(cur[ch] - fl(cur))
                acc[k][1] += abs(cur[ch] - fl(b))
                acc[k][2] += 1
        for k in acc:
            for i in range(3):
                tot[k][i] += acc[k][i]
        per.append((c, acc))
    for k, (l0, l1, n) in tot.items():
        print(f'{k:9} weeks {n:6}  sum|change - flow| lag 0 {l0 / 1e6:10.2f}M   lag 1 {l1 / 1e6:10.2f}M   ratio {l1 / l0 if l0 else 0:5.2f}')
    a0 = a1 = 0.0
    n = 0
    bridge = []
    for c, r in efr.items():
        b0 = b1 = 0.0
        for (d0, a), (d1, b) in zip(r, r[1:]):
            if (d1 - d0).days != 7 or 'leak' not in a or 'ext' not in a or 'ext' not in b:
                continue
            b0 += abs(a['leak'])
            b1 += abs(a['leak'] + a['ext'] - b['ext'])
            n += 1
        a0 += b0
        a1 += b1
        bridge.append((c, b0, b1))
    print(f'bridge    weeks {n:6}  sum|leak| as logged {a0 / 1e6:10.2f}M   with next ext {a1 / 1e6:10.2f}M   ratio {a1 / a0 if a0 else 0:5.2f}')
    for c, b0, b1 in sorted(bridge, key=lambda x: -x[1])[:8]:
        print(f'   {c[:30]:30} |leak| {b0 / 1e6:8.2f}M  with next ext {b1 / 1e6:8.2f}M  ratio {b1 / b0 if b0 else 0:5.2f}')
    top = int(sys.argv[sys.argv.index('--top') + 1]) if '--top' in sys.argv else 12
    for k, _, _ in PAIRS:
        print(f'-- {k}: countries by lag 0 residual')
        for c, acc in sorted(per, key=lambda x: -x[1][k][0])[:top]:
            l0, l1, n = acc[k]
            print(f'   {c[:30]:30} n {n:4}  lag0 {l0 / 1e6:8.2f}M  lag1 {l1 / 1e6:8.2f}M  ratio {l1 / l0 if l0 else 0:5.2f}')


if __name__ == '__main__':
    main()
