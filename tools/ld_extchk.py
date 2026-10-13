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
    leak, ex, tro = {}, {}, {}
    for ln in open(sys.argv[1], encoding='utf-8', errors='replace'):
        if ln.startswith('EFR|'):
            p = ln.rstrip('\n').split('|')
            for x in p[3:]:
                if x.startswith('leak '):
                    leak[(p[2], p[1])] = float(x[5:])
                elif x.startswith('tr_other '):
                    tro[(p[2], p[1])] = float(x[9:])
        elif ln.startswith('EFP|') and '|extx|' in ln:
            p = ln.rstrip('\n').split('|')
            ex[(p[2], p[1])] = fields(p[4:])
    a0 = a1 = s0 = s1 = 0.0
    per = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
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
        s0 += v
        s1 += alt
        r = per[k[0]]
        r[0] += v
        r[1] += alt
        r[2] += d.get('ai_t', 0) - d.get('ax_t', 0)
        r[3] += d.get('ai_x', 0) - d.get('ax_x', 0)
        for x in IN + OUT:
            diff[x] += abs(d.get(x + '_t', 0) - d.get(x + '_x', 0))
    print(f'weeks {n}: sum|leak| as logged {a0 / 1e6:.2f}M, with the exact lines {a1 / 1e6:.2f}M')
    print(f'sum leak as logged {s0 / 1e6:.2f}M, with the exact lines {s1 / 1e6:.2f}M')
    print('countries: sum leak logged / exact; additional income - expenses: trend / temporary (exact)')
    for c, r in sorted(per.items(), key=lambda kv: -abs(kv[1][2] - kv[1][3]))[:10]:
        print(f'  {c[:28]:28} {r[0] / 1e6:8.2f}M {r[1] / 1e6:8.2f}M   {r[2] / 1e6:8.2f}M {r[3] / 1e6:8.2f}M')
    # do the one-off lines hold the script's writes to the treasury (already in the treasury's «прочее», tr_other)?
    big = [(k, d) for k, d in ex.items() if abs(d.get('ai_x', 0)) + abs(d.get('ax_x', 0)) > 20000]
    same = sum(1 for k, d in big if abs(tro.get(k, 0)) > 0.5 * (abs(d.get('ai_x', 0) - d.get('ax_x', 0))))
    print(f'weeks with one-off lines > 20K: {len(big)}; of them with a treasury «прочее» at least half as big: {same}')
    for k, d in sorted(big, key=lambda kd: -(abs(kd[1].get('ai_x', 0)) + abs(kd[1].get('ax_x', 0))))[:8]:
        print(f'  {k[1]:18} {k[0][:22]:22} one-off in {d.get("ai_x", 0):10.0f} out {d.get("ax_x", 0):10.0f}  '
              f'trend in {d.get("ai_t", 0):10.0f} out {d.get("ax_t", 0):10.0f}  tr_other {tro.get(k, 0):10.0f}')
    for x, v in sorted(diff.items(), key=lambda kv: -kv[1]):
        print(f'  {x}: sum|trend - exact| {v / 1e6:.3f}M')


if __name__ == '__main__':
    main()
