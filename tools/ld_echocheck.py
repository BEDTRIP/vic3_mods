"""Is the business cash's remainder the echo of last week's treasury «прочее»? (форк, аудит учёта)

Usage:  py tools/ld_echocheck.py <run>/eflog.txt [--top 10]

The GUI bridge reads the budget's lines outside the accounts from the trends (GetTrendValue) -- last week's numbers.
A one-off write to the treasury (an event, E&F's add_treasury) lands in the treasury's «прочее» (EFR tr_other) the week
it happens and comes back a week later through the bridge (EFR ext): the line «engine: paid beyond the market's sales»
jumps by it and the business cash's remainder (EFO b_rest) takes it back. Per country: sum |b_rest| against
sum |b_rest - tr_other of the previous week|, and the share of |b_rest| > 20 000 weeks the echo explains within 20 %.
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


def main():
    tr = defaultdict(dict)
    br = defaultdict(dict)
    for ln in open(sys.argv[1], encoding='utf-8', errors='replace'):
        if ln.startswith('EFR|'):
            p = ln.rstrip('\n').split('|')
            try:
                tr[p[2]][day(p[1])] = fields(p[3:]).get('tr_other', 0.0)
            except (ValueError, KeyError):
                pass
        elif ln.startswith('EFO|'):
            p = ln.rstrip('\n').split('|')
            try:
                br[p[2]][day(p[1])] = fields(p[3:]).get('b_rest', 0.0)
            except (ValueError, KeyError):
                pass
    rows = []
    T = [0.0, 0.0, 0, 0]
    for c, b in br.items():
        s0 = s1 = 0.0
        big = hit = 0
        for d, v in b.items():
            prev = [x for x in tr[c] if 0 < (d - x).days <= 7]
            t = tr[c][prev[0]] if prev else 0.0
            s0 += abs(v)
            s1 += abs(v - t)
            if abs(v) > 20000:
                big += 1
                if abs(v - t) < 0.2 * abs(v):
                    hit += 1
        rows.append((c, s0, s1, big, hit))
        for i, x in enumerate((s0, s1, big, hit)):
            T[i] += x
    print(f'world: sum|b_rest| {T[0] / 1e6:.2f}M, less last week tr_other {T[1] / 1e6:.2f}M; '
          f'weeks |b_rest| > 20K: {T[2]}, echo within 20 %: {T[3]}')
    top = int(sys.argv[sys.argv.index('--top') + 1]) if '--top' in sys.argv else 10
    for c, s0, s1, big, hit in sorted(rows, key=lambda r: -r[1])[:top]:
        print(f'  {c[:30]:30} |b_rest| {s0 / 1e6:8.2f}M  less echo {s1 / 1e6:8.2f}M  big {big:4} echo {hit:4}')


if __name__ == '__main__':
    main()
