"""Reads the market probe of a sandbox run (форк, R4б, В.R4б.28; scripted_effects/ld_probe_mkt.txt).

Usage:  py tools/ld_probe_mkt.py <run>/eflog.txt

EFP|bld lines (France, Britain, every 4th week): per building what it paid for its inputs (mat) and its input
availability (av: 1 -- every input bought, lower -- a shortage). The value of what it got is not readable from script
(GetTotalConsumptionValue wants the interface), so the test is in time: the same building (country, name, line order)
from a sample with av = 1 to the next one with av < 1. If it pays for what it got, mat falls with av (mat ratio ≈ the
share of the inputs it got); if it pays for the whole order, mat stays (ratio ≈ 1 whatever av). Prints the ratio by
the drop of av, and the reverse step (a shortage ends) as the control.
"""
import sys
from collections import defaultdict
from statistics import median


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
    series = defaultdict(list)          # (country, name, k-th building of that name in the sample) -> [(date, mat, av)]
    mkt = defaultdict(lambda: [0, 0.0])
    seen = defaultdict(int)
    last_date = None
    for ln in open(sys.argv[1], encoding='utf-8', errors='replace'):
        if not ln.startswith('EFP|'):
            continue
        p = ln.rstrip('\n').split('|')
        if len(p) < 5:
            continue
        if p[1] != last_date:
            seen.clear()
            last_date = p[1]
        d = fields(p[4:])
        if p[3] == 'mkt':
            mkt[p[2]][0] += 1
            mkt[p[2]][1] += d.get('bal', 0)
            continue
        if p[3] != 'bld':
            continue
        mat, av = d.get('mat'), d.get('av')
        if not isinstance(mat, float) or not isinstance(av, float):
            continue
        key = (p[2], d.get('t', '?'))
        seen[key] += 1
        series[key + (seen[key],)].append((p[1], mat, av))
    print('market lines: country -> samples, sum of the balance')
    for c, m in mkt.items():
        print(f'  {c}: {m[0]}  {m[1]:.0f}')
    into = defaultdict(list)            # av band after the drop -> mat ratios (full -> shortage)
    out = defaultdict(list)             # shortage -> full
    same = []                           # full -> full (the control: prices and size change alone)
    for s in series.values():
        for (d0, m0, a0), (d1, m1, a1) in zip(s, s[1:]):
            if m0 < 100 or m1 < 0:
                continue
            r = m1 / m0
            if a0 >= 0.999 and a1 >= 0.999:
                same.append(r)
            elif a0 >= 0.999 and a1 < 0.999:
                into[round(int(a1 * 10) / 10, 1)].append(r)
            elif a0 < 0.999 and a1 >= 0.999:
                out[round(int(a0 * 10) / 10, 1)].append(r)
    print(f'\ncontrol, av 1 -> 1: n {len(same)}, median mat ratio {median(same) if same else 0:.3f}')
    print('a shortage begins, av 1 -> band: n, median mat ratio (paid for what it got ≈ av, for the order ≈ 1)')
    for b in sorted(into):
        print(f'  av {b:3}: n {len(into[b]):5}  median {median(into[b]):.3f}')
    print('a shortage ends, band -> av 1: n, median mat ratio (paid for what it got ≈ 1 / av, for the order ≈ 1)')
    for b in sorted(out):
        print(f'  av {b:3}: n {len(out[b]):5}  median {median(out[b]):.3f}')


if __name__ == '__main__':
    main()
