"""Would the line «engine: paid beyond the market's sales» be steadier with the exact budget lines with abroad? (аудит)

Usage:  py tools/ld_extchk.py <run>/eflog.txt

EFP extx (scripted_effects/ld_probe_ext.txt): each line the GUI bridge sums into ext as the trend it reads (<k>_t) and
as the GUI's exact weekly number (<k>_x). The line = d_m2 - ext - ...; with the exact numbers: leak + sum_in (t - x) -
sum_out (t - x). Prints sum |leak| as logged and with the exact lines, per line pair the sum |t - x|.
"""
import sys
from collections import defaultdict

IN = ('pi', 'ti', 'bi', 'ri', 'ai', 'mi')
OUT = ('px', 'tx', 'bx', 'ax')


def fields(parts):
    d = {}
    for x in parts:
        k, _, v = x.partition(' ')
        try:
            d[k] = abs(float(v))
        except ValueError:
            pass
    return d


def main():
    leak, ex = {}, {}
    for ln in open(sys.argv[1], encoding='utf-8', errors='replace'):
        if ln.startswith('EFR|'):
            p = ln.rstrip('\n').split('|')
            for x in p[3:]:
                if x.startswith('leak '):
                    leak[(p[2], p[1])] = float(x[5:])
        elif ln.startswith('EFP|') and '|extx|' in ln:
            p = ln.rstrip('\n').split('|')
            ex[(p[2], p[1])] = fields(p[4:])
    a0 = a1 = 0.0
    diff = defaultdict(float)
    n = 0
    for k, v in leak.items():
        d = ex.get(k)
        if d is None:
            continue
        n += 1
        alt = v + sum(d.get(x + '_t', 0) - d.get(x + '_x', 0) for x in IN) - sum(d.get(x + '_t', 0) - d.get(x + '_x', 0) for x in OUT)
        a0 += abs(v)
        a1 += abs(alt)
        for x in IN + OUT:
            diff[x] += abs(d.get(x + '_t', 0) - d.get(x + '_x', 0))
    print(f'weeks {n}: sum|leak| as logged {a0 / 1e6:.2f}M, with the exact lines {a1 / 1e6:.2f}M')
    for x, v in sorted(diff.items(), key=lambda kv: -kv[1]):
        print(f'  {x}: sum|trend - exact| {v / 1e6:.3f}M')


if __name__ == '__main__':
    main()
