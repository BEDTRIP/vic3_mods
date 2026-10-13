"""Are two card remainders one movement booked in two cards? (форк, аудит учёта)

Usage:  py tools/ld_restpair.py <run>/eflog.txt [A B]   (default: b_rest pool_rest)

From the weekly EFO line: per country the sums of A, B and A + B over the run, and the share of weeks where A and B
have opposite signs with |A + B| < 20 % of max(|A|, |B|) (one movement in two cards). Prints the countries with the
largest |A| + |B|.
"""
import sys
from collections import defaultdict


def main():
    a, b = (sys.argv[2], sys.argv[3]) if len(sys.argv) > 3 else ('b_rest', 'pool_rest')
    s = defaultdict(lambda: [0.0, 0.0, 0.0, 0, 0])
    for ln in open(sys.argv[1], encoding='utf-8', errors='replace'):
        if not ln.startswith('EFO|'):
            continue
        p = ln.rstrip('\n').split('|')
        d = {}
        for x in p[3:]:
            k, _, v = x.partition(' ')
            try:
                d[k] = float(v)
            except ValueError:
                pass
        x, y = d.get(a, 0.0), d.get(b, 0.0)
        r = s[p[2]]
        r[0] += x
        r[1] += y
        r[2] += abs(x) + abs(y)
        if abs(x) > 1000 or abs(y) > 1000:
            r[4] += 1
            if x * y < 0 and abs(x + y) < 0.2 * max(abs(x), abs(y)):
                r[3] += 1
    tot = [sum(r[i] for r in s.values()) for i in range(5)]
    print(f'world: {a} {tot[0] / 1e6:.2f}M  {b} {tot[1] / 1e6:.2f}M  sum {(tot[0] + tot[1]) / 1e6:.2f}M  '
          f'mirror weeks {tot[3]} of {tot[4]} weeks with either > 1000')
    for c, r in sorted(s.items(), key=lambda kv: -kv[1][2])[:15]:
        print(f'  {c[:32]:32} {a} {r[0] / 1e6:8.2f}M  {b} {r[1] / 1e6:8.2f}M  sum {(r[0] + r[1]) / 1e6:8.2f}M  '
              f'mirror {r[3]:4} / {r[4]:4}')


if __name__ == '__main__':
    main()
