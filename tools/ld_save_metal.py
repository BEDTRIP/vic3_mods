"""Gold and silver made and used by buildings in a text save (форк, анализ после R4б).

Usage:  py tools/ld_save_metal.py <save> [<save> ...]

Sums the buildings' output_goods / input_goods (the week's amounts the game keeps on each building) by goods id over
the world; the ids of gold and silver are read off the save as the main output of building_gold_mine and
building_silver_mine. Prints per save: the date, gold and silver made a week (by building type), used a week by
buildings (by building type), and the levels of the mines.
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from save_ownership import section, SG  # noqa: E402

REC = re.compile(r'\n(\d+)=\{\n\tbuilding=(\w+)\n(.*?)\n\}', re.S)


def goods_block(body, key):
    m = re.search(r'\n\t' + key + r'=\{\n\t\tbehavior=\w+\n\t\tgoods=\{(.*?)\n\t\t\}', body, re.S)
    if not m:
        return {}
    return {int(g): float(v) for g, v in re.findall(r'\n\t\t\t(\d+)=\{\n\t\t\t\tvalue=(-?[\d.]+)', m.group(1))}


def main():
    for path in sys.argv[1:]:
        if not os.path.isabs(path):
            path = os.path.join(SG, path)
        s = open(path, 'rb').read().decode('utf-8', 'replace')
        date = re.search(r'\ndate=([\d.]+)', s).group(1)
        bm = section(s, 'building_manager')
        out = collections.defaultdict(collections.Counter)   # goods id -> type -> amount
        inp = collections.defaultdict(collections.Counter)
        levels = collections.Counter()
        first = {}
        for m in REC.finditer(bm):
            btype, body = m.group(2), m.group(3)
            if '\n\tstate=4294967295' in body:
                continue
            lv = re.search(r'\n\tlevels=(\d+)', body)
            if btype in ('building_gold_mine', 'building_silver_mine', 'building_gold_field'):
                levels[btype] += int(lv.group(1)) if lv else 0
            o = goods_block(body, 'output_goods')
            for g, v in o.items():
                out[g][btype] += v
            if btype in ('building_gold_mine', 'building_silver_mine') and o and btype not in first:
                first[btype] = max(o, key=o.get)
            for g, v in goods_block(body, 'input_goods').items():
                inp[g][btype] += v
        ids = {'gold': first.get('building_gold_mine'), 'silver': first.get('building_silver_mine')}
        print(f'== {os.path.basename(path)} date {date}; goods ids {ids}; mine levels {dict(levels)}')
        for name, g in ids.items():
            if g is None:
                continue
            made, used = out[g], inp[g]
            print(f'  {name}: made {sum(made.values()):.1f} / week -- ' + ', '.join(f'{k} {v:.1f}' for k, v in made.most_common(6)))
            print(f'  {name}: used by buildings {sum(used.values()):.1f} / week -- ' + ', '.join(f'{k} {v:.1f}' for k, v in used.most_common(8)))


if __name__ == '__main__':
    main()
