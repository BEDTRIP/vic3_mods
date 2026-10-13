"""The mod's goods on the markets: buy against sell orders (форк, R4б, Д.R4б.27; the EFM modg line).

Usage:  py tools/ld_modg.py <run>/eflog.txt [--from 1837.1]

Per good: the sell orders over the buy orders, summed over the logged markets' owners and weeks (from --from), and the
same for the 8 largest markets by the good's buy orders; plus the EFM gap by groups (fin, psc, metal) over the same
weeks. Sell / buy < 1 -- the orders exceed the supply (the needs' weights to lower by about that factor).
"""
import sys
from collections import defaultdict

MONTHS = {'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
          'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12}


def ym(date):
    try:
        m, rest = date.split(' ', 1)
        y = int(rest.split(',')[1])
        return y + (MONTHS[m] - 1) / 100
    except (ValueError, KeyError, IndexError):
        return None


def main():
    path = sys.argv[1]
    frm = float(sys.argv[sys.argv.index('--from') + 1]) if '--from' in sys.argv else 0
    tot = defaultdict(lambda: [0.0, 0.0])
    bym = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0]))
    gaps = defaultdict(float)
    weeks = set()
    for ln in open(path, encoding='utf-8', errors='replace'):
        if not ln.startswith('EFM|'):
            continue
        p = ln.rstrip('\n').split('|')
        if len(p) < 5:
            continue
        t = ym(p[1])
        if t is None or t < frm:
            continue
        if p[3] == 'modg':
            weeks.add(p[1])
            for x in p[5:]:
                k, _, v = x.partition(' ')
                b, _, s = v.partition('/')
                try:
                    b, s = float(b), float(s)
                except ValueError:
                    continue
                tot[k][0] += b
                tot[k][1] += s
                bym[k][p[2]][0] += b
                bym[k][p[2]][1] += s
        elif p[3].startswith('tag '):
            for x in p[3:]:
                k, _, v = x.partition(' ')
                if k in ('gap', 'gap_fin', 'gap_psc', 'gap_metal'):
                    try:
                        gaps[k] += float(v)
                    except ValueError:
                        pass
    print(f'weeks {len(weeks)} (from {frm})')
    print('good      buy orders   sell orders   sell/buy   largest markets: sell/buy (buy)')
    for k, (b, s) in tot.items():
        top = sorted(bym[k].items(), key=lambda kv: -kv[1][0])[:8]
        tops = '; '.join(f'{m} {v[1] / v[0] if v[0] else 0:.2f} ({v[0]:.0f})' for m, v in top)
        print(f'{k:7} {b:13.0f} {s:13.0f} {s / b if b else 0:9.2f}   {tops}')
    print('gap over the same weeks (logged markets): ' + ', '.join(f'{k} {v / 1e6:.2f}M' for k, v in gaps.items()))


if __name__ == '__main__':
    main()
