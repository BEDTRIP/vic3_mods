"""Reads the market probe of a sandbox run (форк, R4б, В.R4б.28).

Usage:  py tools/ld_probe_mkt.py <run>/eflog.txt

EFW|all (every country, monthly): its market's owner (mkt), the line «engine: the market gap» summed since the start
(leak_cum), and for a market's owner its market's gap summed over the same steps (gap_cum). Per market from the first
February line to the last: the line summed over every member against the market's gap -- does the gap (vanilla goods
and the mod's) take the money one to one when all of the market's countries are counted.
"""
import sys
from collections import defaultdict


def fields(parts):
    d = {}
    for x in parts:
        k, _, v = x.partition(' ')
        try:
            d[k] = float(v)
        except ValueError:
            d[k] = v.strip()
    return d


def main():
    first, last, mkt_of = {}, {}, {}
    for ln in open(sys.argv[1], encoding='utf-8', errors='replace'):
        if not ln.startswith('EFW|') or '|all|' not in ln:
            continue
        p = ln.rstrip('\n').split('|')
        d = fields(p[4:])
        if 'leak_cum' not in d:
            continue
        c = p[2]
        if c not in first and not p[1].startswith('января'):
            first[c] = d
        if c in first:
            last[c] = d
            mkt_of[c] = d.get('mkt', '?')
    st = defaultdict(float)
    n = defaultdict(int)
    for c, d in last.items():
        st[mkt_of[c]] += d.get('leak_cum', 0) - first[c].get('leak_cum', 0)
        n[mkt_of[c]] += 1
    gap = {}
    for c, d in last.items():
        tag = d.get('tag')
        if tag and isinstance(d.get('gap_cum'), float):
            gap[tag] = d['gap_cum'] - (first[c].get('gap_cum', 0) if isinstance(first[c].get('gap_cum'), float) else 0)
    rows = sorted(((m, st[m], gap.get(m, 0), n[m]) for m in st), key=lambda r: r[2])
    print('market: countries, the line summed over them, the market gap, line / gap (millions)')
    ts = tg = 0
    for m, s, g, k in rows[:25]:
        print(f'  {m:5} {k:4}  {s / 1e6:9.2f}  {g / 1e6:9.2f}  {s / g if g else 0:6.2f}')
    for m, s, g, k in rows:
        ts += s
        tg += g
    print(f'world: the line {ts / 1e6:.2f}, the gap {tg / 1e6:.2f}, ratio {ts / tg if tg else 0:.2f}')


if __name__ == '__main__':
    main()
