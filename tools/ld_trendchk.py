"""Would the business cash card's remainder go with the exact weekly budget lines instead of the trends? (форк, аудит)

Usage:  py tools/ld_trendchk.py <run>/eflog.txt [--top 10]

EFP trend (scripted_effects/ld_probe_trend.txt): each budget line of the card as the trend it reads (<k>_t) and as the
GUI's exact number (<k>_x). The card's remainder (EFO b_rest) = the cash's change - the lines in + the lines out; with
the exact numbers it becomes b_rest + sum_in (t - x) - sum_out (t - x). Variants: the military goods as one line or army
+ navy, the construction goods all or the government's. Prints sum |b_rest| and its sum over the run per variant.
"""
import sys
from collections import defaultdict

IN = ('gg', 'mg', 'cg', 'sub', 'sv')
OUT = ('tar', 'div')


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
    rest, tr = {}, {}
    for ln in open(sys.argv[1], encoding='utf-8', errors='replace'):
        if ln.startswith('EFO|'):
            p = ln.rstrip('\n').split('|')
            for x in p[3:]:
                if x.startswith('b_rest '):
                    rest[(p[2], p[1])] = float(x[7:])
        elif ln.startswith('EFP|') and '|trend|' in ln:
            p = ln.rstrip('\n').split('|')
            tr[(p[2], p[1])] = fields(p[4:])

    def exact(d, k, var):
        if k == 'mg' and var.get('mil') == 'army+navy':
            return d.get('ag_x', 0) + d.get('ng_x', 0)
        if k == 'cg' and var.get('cons') == 'gov':
            return d.get('gcg_x', 0)
        return d.get(k + '_x', 0)
    variants = {'trends (as now)': None, 'exact': {}, 'exact, army+navy': {'mil': 'army+navy'},
                'exact, gov construction': {'cons': 'gov'}, 'exact, army+navy, gov construction': {'mil': 'army+navy', 'cons': 'gov'}}
    res = {}
    per = defaultdict(lambda: defaultdict(float))
    for name, var in variants.items():
        sa = ss = 0.0
        for key, r in rest.items():
            d = tr.get(key)
            if d is None:
                continue
            v = r
            if var is not None:
                v += sum(d.get(k + '_t', 0) - exact(d, k, var) for k in IN)
                v -= sum(d.get(k + '_t', 0) - exact(d, k, var) for k in OUT)
            sa += abs(v)
            ss += v
            per[key[0]][name] += v
        res[name] = (sa, ss)
    n = sum(1 for k in rest if k in tr)
    print(f'weeks {n}')
    for name, (sa, ss) in res.items():
        print(f'  {name:38} sum|b_rest| {sa / 1e6:9.2f}M   sum b_rest {ss / 1e6:9.2f}M')
    top = int(sys.argv[sys.argv.index('--top') + 1]) if '--top' in sys.argv else 10
    print('countries: sum b_rest, trends / exact')
    for c, d in sorted(per.items(), key=lambda kv: -abs(kv[1]['trends (as now)']))[:top]:
        print(f'  {c[:30]:30} {d["trends (as now)"] / 1e6:8.2f}M  {d["exact"] / 1e6:8.2f}M')


if __name__ == '__main__':
    main()
