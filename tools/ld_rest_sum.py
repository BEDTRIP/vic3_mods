"""Sums the card remainders of a run by country up to a date (форк, R4б ночь: утечки).

Usage:  py tools/ld_rest_sum.py <run>/eflog.txt [--until 1836.12] [--top 8]

EFO (b_rest, pool_rest, abr_rest, tr_rest, cbm_rest) and EFR (leak): the world's sums and the countries with the largest
|sum| of each remainder.
"""
import sys
from collections import defaultdict

MON = {'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
       'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12}
KEYS = ('b_rest', 'leak', 'abr_rest', 'pool_rest', 'tr_rest', 'cbm_rest')


def main():
    a = sys.argv[1:]
    until = float(a[a.index('--until') + 1]) if '--until' in a else 9999
    top = int(a[a.index('--top') + 1]) if '--top' in a else 8
    lim = (int(until), round((until - int(until)) * 100) or 12)
    tot = defaultdict(lambda: defaultdict(float))
    first = None
    for ln in open(a[0], encoding='utf-8', errors='replace'):
        if not ln.startswith(('EFO|', 'EFR|')):
            continue
        p = ln.rstrip('\n').split('|')
        d = p[1].replace(',', '').split()
        if len(d) < 3 or d[0] not in MON:
            continue
        mo = (int(d[2]), MON[d[0]])
        if mo > lim:
            continue
        if first is None:
            first = mo
        if mo == first:
            continue          # the first month: the start's setting
        for x in p[3:]:
            k, _, v = x.partition(' ')
            if k in KEYS:
                try:
                    tot[k][p[2]] += float(v)
                except ValueError:
                    pass
    for k in KEYS:
        c = tot.get(k)
        if not c:
            continue
        w = sum(c.values())
        big = sorted(c.items(), key=lambda kv: -abs(kv[1]))[:top]
        print(f'{k}: world {w / 1e6:+.2f}M; ' + ', '.join(f'{n} {v / 1e6:+.2f}' for n, v in big))


if __name__ == '__main__':
    main()
