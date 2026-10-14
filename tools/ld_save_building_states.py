"""Where a building stands: its levels by state region and owner, from text saves (R9б.9 — Сонора).

Usage:  py tools/ld_save_building_states.py <save> [<save> ...] [--building building_silver_mine] [--region STATE_X]

For each save: every live record of the building type -- the state's region, the country that holds the state, the
building's levels (summed over its ownership records) and who owns them (country / building type of the owner), and
the state's modifiers whose name has the building's stem (E&F's caps: silver_mine_max_level). --region keeps one
region. Save format -- save_ownership.py.
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import save_ownership as SO  # noqa: E402


def opt(args, name, default):
    if name in args:
        i = args.index(name); v = args[i + 1]; del args[i:i + 2]; return v
    return default


def states(s):
    sec = SO.section(s, 'states')
    out = {}
    heads = list(re.finditer(r'\n(\d+)=\{\n\tcapital=\d+\n\n?\tcountry=(\d+)', sec))
    for i, m in enumerate(heads):
        body = sec[m.end():heads[i + 1].start() if i + 1 < len(heads) else len(sec)]
        reg = re.search(r'\n\tregion="(\w+)"', body)
        mods = re.findall(r'modifier="?(\w+)"?', body)
        out[m.group(1)] = (reg.group(1) if reg else '?', m.group(2), mods)
    return out


def main():
    args = sys.argv[1:]
    btype = opt(args, '--building', 'building_silver_mine')
    region = opt(args, '--region', None)
    stem = btype.replace('building_', '')
    for path in args:
        if not os.path.isabs(path):
            path = os.path.join(SO.SG, path)
        s = open(path, 'rb').read().decode('utf-8', 'replace')
        date = re.search(r'\ndate=([\d.]+)', s).group(1)
        tag = {}
        for m in re.finditer(r'\n(\d+)=\{\n(?:\t[^\n]*\n){0,3}?\tdefinition="(\w+)"', SO.section(s, 'country_manager')):
            tag[m.group(1)] = m.group(2)
        st = states(s)
        bld, owner_type = {}, {}
        for m in re.finditer(r'\n(\d+)=\{\n\tbuilding=(\w+)\n(?:\t[^\n]*\n)*?\tstate=(\d+)', SO.section(s, 'building_manager')):
            if m.group(3) == '4294967295':
                continue
            owner_type[m.group(1)] = (m.group(2), m.group(3))
            if m.group(2) == btype:
                bld[m.group(1)] = m.group(3)
        lv = collections.Counter()
        who = collections.defaultdict(list)
        for m in re.finditer(r'\n\d+=\{\n\tlevels=(\d+)\n\tidentity=\{\n\t\t(building|country)=(\d+)\n\t\}\n\tbuilding=(\d+)\n',
                             SO.section(s, 'building_ownership_manager')):
            b = m.group(4)
            if b not in bld:
                continue
            lv[b] += int(m.group(1))
            if m.group(2) == 'country':
                who[b].append(f"{tag.get(m.group(3), m.group(3))} {m.group(1)}")
            else:
                ot = owner_type.get(m.group(3), ('?', None))
                cty = st.get(ot[1], ('?', '?', []))[1]
                who[b].append(f"{ot[0].replace('building_', '')}@{tag.get(cty, cty)} {m.group(1)}")
        print(f'{os.path.basename(path)} ({date}): {btype}, {len(bld)} buildings, {sum(lv.values())} levels')
        rows = []
        for b, sid in bld.items():
            reg, cty, mods = st.get(sid, ('?', '?', []))
            if region and reg != region:
                continue
            cap = [x for x in mods if stem in x]
            rows.append((reg, tag.get(cty, cty), lv[b], ', '.join(who[b]), ' '.join(cap) or '-'))
        for r in sorted(rows):
            print(f'  {r[0]:28} {r[1]:5} {r[2]:4}  owners: {r[3]}  caps: {r[4]}')


if __name__ == '__main__':
    main()
