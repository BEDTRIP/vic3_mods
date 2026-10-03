"""Construction goods flows per country from text saves (СТР.3 / Д.7-Д.8, ночь Г).

Usage:  py tools/save_construction_goods.py <save> [--top N] [--json out.json]

PSC's four construction goods (wood / iron / steel / arc-welded construction, local goods): who makes
them and who uses them, per country and for the world, in units a week.
  sectors   output of building_construction_sector (levels too)
  subsist   output of the subsistence buildings (СТР.3: wood_construction from natural economies)
  regul     input of building_construction_regulator -> construction points = regul / 10
  urban     input of building_urban_center (СТР.3: ЖКХ)
  pops      sectors + subsist - regul - urban: what households bought (СТР.3), ~ (unsold goods count here too)
  price     regulators' goods_cost / units bought -- average price paid for construction goods
  hh%       (pops + urban) / (sectors + subsist): households + ЖКХ share of all construction goods (Д.5: 25-35%)
Goods ids are read off the save: the outputs of construction sectors by production method.
"""
import re, sys, json, collections, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import save_ownership as so

PM_GOOD = {'pm_wooden_buildings': 'wood', 'pm_iron_frame_buildings': 'iron', 'pm_steel_frame_buildings': 'steel',
           'pm_arc_welded_buildings': 'arc'}
SUBSIST = ('building_subsistence_farm', 'building_subsistence_rice_farm', 'building_subsistence_pasture',
           'building_subsistence_orchard', 'building_subsistence_fishing_village')


def goods(body, kind):
    g = re.search(kind + r'=\{\n\t\tbehavior=\w+\n\t\tgoods=\{(.*?)\n\t\t\}\n\t\}', body, re.S)
    return {int(a): float(b) for a, b in re.findall(r'(\d+)=\{\n\t+value=([\d.]+)', g.group(1))} if g else {}


def main():
    args = sys.argv[1:]
    top = 15; out = None
    if '--top' in args:
        i = args.index('--top'); top = int(args[i + 1]); del args[i:i + 2]
    if '--json' in args:
        i = args.index('--json'); out = args[i + 1]; del args[i:i + 2]
    p = args[0]
    if not os.path.isabs(p):
        p = os.path.join(so.SG, p)
    s = open(p, 'rb').read().decode('utf-8', 'replace')
    date = re.search(r'\ndate=([\d.]+)', s).group(1)
    tag = {m.group(1): m.group(2) for m in
           re.finditer(r'\n(\d+)=\{\n(?:\t[^\n]*\n){0,3}?\tdefinition="(\w+)"', so.section(s, 'country_manager'))}
    st = {m.group(1): m.group(2) for m in
          re.finditer(r'\n(\d+)=\{\n\tcapital=\d+\n\n?\tcountry=(\d+)', so.section(s, 'states'))}
    recs = []
    for m in re.finditer(r'\n(\d+)=\{\n\tbuilding=(\w+)\n(.*?)\n\}', so.section(s, 'building_manager'), re.S):
        bt = m.group(2)
        if bt not in ('building_construction_sector', 'building_construction_regulator', 'building_urban_center') + SUBSIST:
            continue
        body = m.group(3)
        if '\n\tdead=yes' in body:  # removed building: the record and its last values stay in the save
            continue
        stt =re.search(r'\n\tstate=(\d+)', body)
        lv = re.search(r'\n\tlevels=(\d+)', '\n' + body)
        pms = re.search(r'production_methods=\{([^}]*)\}', body)
        gc = re.search(r'\n\tgoods_cost=([\d.]+)', body)
        recs.append(dict(bt=bt, cty=tag.get(st.get(stt.group(1) if stt else ''), '?'), lv=int(lv.group(1)) if lv else 0,
                         pms=pms.group(1) if pms else '', out=goods(body, 'output_goods'), inp=goods(body, 'input_goods'),
                         cost=float(gc.group(1)) if gc else 0))
    # construction goods ids: per method, the outputs all its sectors share, minus what every sector
    # makes whatever its method (E&F's liquidity product); PSC defines the four in a row
    by_pm = collections.defaultdict(list)
    for r in recs:
        if r['bt'] == 'building_construction_sector':
            for pm, g in PM_GOOD.items():
                if pm in r['pms']:
                    by_pm[g].append(set(r['out']))
    common_all = set.intersection(*[x for v in by_pm.values() for x in v]) if by_pm else set()
    ids = {}
    for g, sets in by_pm.items():
        c = set.intersection(*sets) - (common_all if len(by_pm) > 1 else set())
        if len(c) == 1:
            ids[g] = c.pop()
    if 'wood' in ids:  # methods nobody runs yet: PSC_goods.txt order wood, iron, steel, arc
        for k, g in enumerate(('wood', 'iron', 'steel', 'arc')):
            ids.setdefault(g, ids['wood'] + k)
    CG = set(ids.values())
    T = collections.defaultdict(lambda: collections.Counter())
    for r in recs:
        c = r['cty']
        for k in (c, 'WORLD'):
            t = T[k]
            if r['bt'] == 'building_construction_sector':
                t['sect_lv'] += r['lv']
                t['sectors'] += sum(v for i, v in r['out'].items() if i in CG)
            elif r['bt'] == 'building_construction_regulator':
                u = sum(v for i, v in r['inp'].items() if i in CG)
                t['regul'] += u
                t['regul_cost'] += r['cost'] if u else 0
            elif r['bt'] == 'building_urban_center':
                t['urban'] += sum(v for i, v in r['inp'].items() if i in CG)
                t['uc_lv'] += r['lv']
            else:
                t['subsist'] += sum(v for i, v in r['out'].items() if i in CG)
    res = {'date': date, 'ids': ids, 'countries': {}}
    print(f"{date}  construction goods ids {ids}")
    print('country  sect_lv  sectors  subsist    regul   points    urban     pops  price   hh%  uc_lv')
    order = sorted(T, key=lambda c: -T[c]['regul'])
    for c in order[:top + 1]:
        t = T[c]
        pops = t['sectors'] + t['subsist'] - t['regul'] - t['urban']
        supply = t['sectors'] + t['subsist']
        price = t['regul_cost'] / t['regul'] if t['regul'] else 0
        hh = 100 * (pops + t['urban']) / supply if supply else 0
        print(f"{c:7} {t['sect_lv']:8.0f} {t['sectors']:8.0f} {t['subsist']:8.0f} {t['regul']:8.0f} {t['regul'] / 10:8.0f} "
              f"{t['urban']:8.0f} {pops:8.0f} {price:6.0f} {hh:5.1f} {t['uc_lv']:6.0f}")
    for c, t in T.items():
        res['countries'][c] = dict(t, pops=t['sectors'] + t['subsist'] - t['regul'] - t['urban'])
    if out:
        json.dump(res, open(out, 'w'), indent=1)


if __name__ == '__main__':
    main()
