"""One good's flows through buildings in a save, by country: input (bought by buildings) and output (Д2.2, этап 2).

Usage:  py tools/scan_goods_io.py <save> <good_index> [--top N]

good_index is the save's numeric goods id (liquidity_currency was 69 in 1.13 with the set, run r1005_172152).
Per country: units bought by buildings as input, units made, and the top input building types. What the
population buys = the market's buy orders minus the buildings' input (the market side is not read here).
Parsing as in save_ownership.py.
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import save_ownership as SO  # noqa: E402


def main():
    args = sys.argv[1:]
    top = 25
    if '--top' in args:
        i = args.index('--top'); top = int(args[i + 1]); del args[i:i + 2]
    path, gid = args[0], args[1]
    d = SO.parse(path)
    if not os.path.isabs(path):
        path = os.path.join(SO.SG, path)
    s = open(path, 'rb').read().decode('utf-8', 'replace')
    bm = SO.section(s, 'building_manager')
    rin = collections.Counter(); rout = collections.Counter()
    by_type = collections.defaultdict(collections.Counter)
    pat_in = re.compile(r'input_goods=\{.*?goods=\{(.*?)\n\t\}', re.S)
    for m in re.finditer(r'\n(\d+)=\{\n\tbuilding=(\w+)\n(.*?)\n\}', bm, re.S):
        bid, bt, body = m.group(1), m.group(2), m.group(3)
        b = d['bld'].get(bid)
        if not b:
            continue
        tag = d['tag'].get(b[1], b[1])
        for kind, ctr in (('input_goods', rin), ('output_goods', rout)):
            k = body.find(kind + '={')
            if k < 0:
                continue
            g = re.search(r'\b' + gid + r'=\{\s*value=(-?[\d.]+)', body[k:k + 3000])
            if g:
                v = float(g.group(1))
                ctr[tag] += v
                if kind == 'input_goods':
                    by_type[tag][bt] += v
    print(f"date {d['date']}  good {gid}")
    print('country      input     output   top input building types')
    for tag, v in rin.most_common(top):
        tops = ', '.join(f'{k} {x:.0f}' for k, x in by_type[tag].most_common(4))
        print(f'{tag:7} {v:10.0f} {rout[tag]:10.0f}   {tops}')
    print(f"ALL     {sum(rin.values()):10.0f} {sum(rout.values()):10.0f}")


if __name__ == '__main__':
    main()
