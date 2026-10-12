"""Checks the debug log parts of a sandbox run for gaps (форк, R4б: «строки лога не теряются»).

Usage:  py tools/ld_logparts_check.py <run>

For each saved part (dbgparts/*.log, oldest first, then debug.log): its first and last clock time and game date of
the EF lines, its line count; then the EFW|<country>|acc lines a month in eflog.txt, the months under 80 % of the
median -- where the lines were lost.
"""
import re
import sys
from collections import Counter
from pathlib import Path

CLOCK = re.compile(r'^\[(\d\d:\d\d:\d\d)\]')
EF = re.compile(r': (EF[A-Z])\|([^|]+)\|')


def main():
    run = Path(sys.argv[1])
    parts = sorted((run / 'dbgparts').glob('*.log'), key=lambda p: p.name) + [run / 'debug.log']
    for p in parts:
        if not p.exists():
            continue
        first = last = fd = ld = None
        n = 0
        with open(p, encoding='utf-8', errors='replace') as f:
            for ln in f:
                n += 1
                m = CLOCK.match(ln)
                if m:
                    first = first or m.group(1)
                    last = m.group(1)
                e = EF.search(ln)
                if e:
                    fd = fd or e.group(2)
                    ld = e.group(2)
        print(f'{p.name:<24} lines {n:>6} clock {first}-{last} dates {fd} .. {ld}')
    cnt = Counter()
    for ln in open(run / 'eflog.txt', encoding='utf-8', errors='replace'):
        if ln.startswith('EFW|'):
            p = ln.split('|')
            if len(p) > 3 and p[3] == 'acc' and p[2] != 'WORLD':
                d = p[1].split()
                cnt[(d[-1], d[0])] += 1
    med = sorted(cnt.values())[len(cnt) // 2] if cnt else 0
    print(f'EFW acc country lines a month: median {med}')
    for k, v in cnt.items():
        if v < 0.8 * med:
            print(f'  low: {k[1]} {k[0]}: {v}')


if __name__ == '__main__':
    main()
