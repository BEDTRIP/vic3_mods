"""Which logged flow explains a card's remainder? (форк, аудит учёта)

Usage:  py tools/ld_restexplain.py <run>/eflog.txt <rest> [--lag 0|1] [--top 12]

<rest> -- a key of the weekly EFO line (b_rest, pool_rest, abr_rest, ...), or efj:<key> -- of the reconciliation's EFJ
other line (efj:d_other_tr -- the treasury part's «прочее» of the week). Candidates -- every numeric field of the
same country's EFR line (of the same week, or of the week before with --lag 1) and of its EFF card lines (named
<card>.<key>). For each candidate and sign s = +1 / -1: sum over countries and weeks of |rest - s x field| against
sum |rest|. The best few name the flow the card misses (or counts twice).
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


def fields(parts, prefix=''):
    d = {}
    for x in parts:
        k, _, v = x.rpartition(' ')
        try:
            d[prefix + k.lstrip('-')] = float(v) * (-1 if k.startswith('-') else 1)
        except ValueError:
            pass
    return d


def main():
    key = sys.argv[2]
    lag = int(sys.argv[sys.argv.index('--lag') + 1]) if '--lag' in sys.argv else 0
    top = int(sys.argv[sys.argv.index('--top') + 1]) if '--top' in sys.argv else 12
    rest = {}
    cand = defaultdict(dict)
    for ln in open(sys.argv[1], encoding='utf-8', errors='replace'):
        if not ln.startswith(('EFO|', 'EFR|', 'EFF|', 'EFJ|')):
            continue
        p = ln.rstrip('\n').split('|')
        try:
            k = (p[2], day(p[1]))
        except (ValueError, KeyError, IndexError):
            continue
        if p[0] == 'EFJ':
            if key.startswith('efj:') and len(p) > 3 and p[3].startswith('other '):
                v = fields(p[3:]).get(key[4:])
                if v is not None:
                    rest[k] = v
        elif p[0] == 'EFO':
            v = fields(p[3:]).get(key)
            if v is not None:
                rest[k] = v
        elif p[0] == 'EFR':
            cand[k].update(fields(p[3:]))
        elif len(p) > 4:
            cand[k].update(fields(p[4:], p[3] + '.'))
    base = 0.0
    score = defaultdict(float)
    n = 0
    for (c, d), v in rest.items():
        src = cand.get((c, d)) if lag == 0 else next((cand[(c, x)] for x in [d.fromordinal(d.toordinal() - i) for i in range(7, 0, -1)]
                                                      if (c, x) in cand), None)
        if not src:
            continue
        base += abs(v)
        n += 1
        for f, x in src.items():
            score[(f, 1)] += abs(v - x)
            score[(f, -1)] += abs(v + x)
    print(f'{key}: weeks {n}, sum|rest| {base / 1e6:.2f}M (lag {lag})')
    for (f, s), sc in sorted(score.items(), key=lambda kv: kv[1])[:top]:
        print(f'  rest {"-" if s > 0 else "+"} {f:34} -> {sc / 1e6:10.2f}M  ({sc / base if base else 0:.2f})')


if __name__ == '__main__':
    main()
