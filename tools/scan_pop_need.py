"""Expected weekly demand of the population for one need, from the pops of a save (Д2.2, этап 2).

Usage:  py tools/scan_pop_need.py <save> [--need popneed_currency] [--packages FILE] [--per 10000]

For every pop: size = workforce + dependents, wealth -> the need's value in the wealth tier's buy package
(default: the hotfix's zz_ef_currency_need_packages.txt), demand = value x size / per. Summed by the owner country
of the pop's state (location is a state id). The engine's own scaling of buy packages is the unknown checked here:
compare with the market's real consumption (tools/scan_goods_io.py).
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import save_ownership as SO  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PKG = os.path.join(HERE, '..', '_ef', 'ef hotfix 1.13', 'common', 'buy_packages', 'zz_ef_currency_need_packages.txt')


def opt(args, name, default, cast=str):
    if name in args:
        i = args.index(name); v = cast(args[i + 1]); del args[i:i + 2]; return v
    return default


def main():
    args = sys.argv[1:]
    need = opt(args, '--need', 'popneed_currency')
    pkg = opt(args, '--packages', DEFAULT_PKG)
    per = opt(args, '--per', 10000.0, float)
    path = args[0]
    table = {}
    for m in re.finditer(r'wealth_(\d+)\s*=\s*\{[^{}]*?\bgoods\s*=\s*\{[^{}]*?\b' + need + r'\s*=\s*([\d.]+)',
                         open(pkg, encoding='utf-8-sig').read()):
        table[int(m.group(1))] = float(m.group(2))
    print(f'packages {pkg}: {len(table)} tiers, wealth 10 -> {table.get(10)}')
    d = SO.parse(path)
    if not os.path.isabs(path):
        path = os.path.join(SO.SG, path)
    s = open(path, 'rb').read().decode('utf-8', 'replace')
    st_country = {}
    for m in re.finditer(r'\n(\d+)=\{\n\tcapital=\d+\n\n?\tcountry=(\d+)', SO.section(s, 'states')):
        st_country[m.group(1)] = m.group(2)
    a = s.find('\npops={')
    e = s.find('\n}\n', s.find('\tdatabase={', a))
    dem = collections.Counter(); size = collections.Counter()
    for m in re.finditer(r'\n\d+=\{\n\ttype=\w+\n(.*?)\n\}', s[a:e], re.S):
        b = m.group(1)
        wf = re.search(r'\tworkforce=(\d+)', b); dp = re.search(r'\tdependents=(\d+)', b)
        n = (int(wf.group(1)) if wf else 0) + (int(dp.group(1)) if dp else 0)
        w = re.search(r'\twealth=(\d+)', b); loc = re.search(r'\tlocation=(\d+)', b)
        if not (n and w and loc):
            continue
        tag = d['tag'].get(st_country.get(loc.group(1)), '?')
        dem[tag] += table.get(int(w.group(1)), 0) * n / per
        size[tag] += n
    print(f"date {d['date']}  need {need}, per {per:.0f} people")
    for tag, v in dem.most_common(10):
        print(f'{tag:7} demand {v:10.0f}  people {size[tag]:12.0f}')
    print(f"ALL     demand {sum(dem.values()):10.0f}  people {sum(size.values()):12.0f}")


if __name__ == '__main__':
    main()
