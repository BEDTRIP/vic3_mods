"""Who owns the levels: production levels by owner class per country, from text saves (СТР.5, ночь Г).

Usage:  py tools/save_ownership.py <save1> [<save2> ...] [--json out.json] [--top N]

For each save: levels of production buildings (no owner buildings, army, ports, urban centers, government)
by owner class — gov (country), company (ordinary HQ / regional HQ), bank (E&F bank companies: the 98
INJECT'ed in zz_ef_cm_companies.txt + E&F's own banks), manor (aristocrats), findist (capitalists outside
companies), f_pop / f_comp / f_gov (owner from another country: aristocrats or capitalists / company / state), other. With two saves or more, also the gross
additions between consecutive saves: per (owner, building) record the positive change in levels, summed by
class — this is "who builds" (privatization from the state shows up as a gain for the buyer).
Populace share = (manor + findist + f_pop) / all private additions (Д.1/Д.2 target: >= 20%).
Save format notes — архив «блок Г, стройка — ход работы 2.10».
"""
import os, re, sys, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
HOTFIX = os.path.join(HERE, '..', '_ef', 'ef hotfix 1.13', 'common', 'company_types')
SG = os.path.expanduser(r'~\Documents\Paradox Interactive\Victoria 3\save games')

NONPROD = {'building_manor_house', 'building_financial_district', 'building_barrack', 'building_conscription_center',
           'building_construction_regulator', 'building_trade_center', 'building_government_administration',
           'building_port', 'building_river_port', 'building_university', 'building_urban_center', 'building_bank',
           'building_zz_ef_cm_central_bank', 'usu_building_public_green', 'building_army_logistics_center'}
NONPROD_PREFIX = ('LLWA_building_', 'building_naval_', 'building_financial_centre', 'building_company_',
                  'building_regional_company_')
OWNER_TYPES = {'building_manor_house': 'manor', 'building_financial_district': 'findist'}


def bank_companies():
    names = set()
    for fn in os.listdir(HOTFIX):
        s = open(os.path.join(HOTFIX, fn), encoding='utf-8-sig', errors='replace').read()
        for m in re.finditer(r'^(?:INJECT:|REPLACE:)?(\w+)\s*=\s*\{(.*?)^\}', s, re.S | re.M):
            body = m.group(2)
            bt = re.search(r'building_types\s*=\s*\{(.*?)\}', body, re.S)
            if bt and 'building_bank' in bt.group(1):  # commented "#building_bank" too: E&F's own banks
                names.add(m.group(1))
    return names


TOP = ['country_manager', 'states', 'interest_groups', 'building_manager', 'building_ownership_manager',
       'decree_manager', 'companies', 'company_charters']


def section(s, key):
    # records sit at column 0 and countries carry column-0 counters too: cut at the next known top-level block
    a = s.find('\n' + key + '={\n')
    ends = [e for e in (s.find('\n' + k + '={\n', a + 2) for k in TOP if k != key) if e > a]
    return s[a:min(ends) if ends else len(s)]


def parse(path):
    if not os.path.isabs(path):
        path = os.path.join(SG, path)
    s = open(path, 'rb').read().decode('utf-8', 'replace')
    date = re.search(r'\ndate=([\d.]+)', s).group(1)
    tag = {}
    for m in re.finditer(r'\n(\d+)=\{\n(?:\t[^\n]*\n){0,3}?\tdefinition="(\w+)"', section(s, 'country_manager')):
        tag[m.group(1)] = m.group(2)
    st_country = {m.group(1): m.group(2) for m in
                  re.finditer(r'\n(\d+)=\{\n\tcapital=\d+\n\n?\tcountry=(\d+)', section(s, 'states'))}
    bld = {}
    for m in re.finditer(r'\n(\d+)=\{\n\tbuilding=(\w+)\n(?:\t[^\n]*\n)*?\tstate=(\d+)', section(s, 'building_manager')):
        bld[m.group(1)] = (m.group(2), st_country.get(m.group(3)))
    comp = {}
    for m in re.finditer(r'\n(\d+)=\{\n\tcountry=\d+\n\tbuilding=(\d+)\n\tcompany_type=(\w+)', section(s, 'companies')):
        comp[m.group(2)] = m.group(3)
    own = {}
    for m in re.finditer(r'\n\d+=\{\n\tlevels=(\d+)\n\tidentity=\{\n\t\t(building|country)=(\d+)\n\t\}\n\tbuilding=(\d+)\n(\tprivatization=yes\n)?',
                         section(s, 'building_ownership_manager')):
        if m.group(5):
            continue
        own[(m.group(2), m.group(3), m.group(4))] = int(m.group(1))
    return dict(date=date, tag=tag, bld=bld, comp=comp, own=own)


def classify(d, kind, oid, bid, banks):
    b = d['bld'].get(bid)
    if not b or b[0] in NONPROD or b[0].startswith(NONPROD_PREFIX):
        return None, None
    cty = d['tag'].get(b[1], b[1])
    if kind == 'country':
        return cty, ('gov' if d['tag'].get(oid) == cty else 'f_gov')
    ob = d['bld'].get(oid)
    if not ob:
        return cty, 'other'
    if ob[0] in OWNER_TYPES:
        cl = OWNER_TYPES[ob[0]]
    elif oid in d['comp']:  # company HQ: building_company_<type>, E&F central banks building_zz_ef_cm_central_bank
        cl = 'bank' if d['comp'][oid] in banks else 'company'
    elif ob[0].startswith('building_regional_company_'):  # regional office of a company
        cl = 'bank' if ob[0][len('building_regional_company_'):] in banks else 'company'
    elif oid == bid:
        cl = 'self'
    else:
        cl = 'other'
    if d['tag'].get(ob[1], ob[1]) != cty:
        cl = 'f_pop' if cl in ('manor', 'findist') else 'f_comp'
    return cty, cl


CLASSES = ['gov', 'company', 'bank', 'manor', 'findist', 'f_pop', 'f_comp', 'f_gov', 'self', 'other']
POP = ('manor', 'findist', 'f_pop')


def main():
    args = [a for a in sys.argv[1:]]
    out = None; top = 15
    if '--json' in args:
        i = args.index('--json'); out = args[i + 1]; del args[i:i + 2]
    if '--top' in args:
        i = args.index('--top'); top = int(args[i + 1]); del args[i:i + 2]
    banks = bank_companies()
    saves = [parse(p) for p in args]
    res = {'banks_known': len(banks), 'saves': [], 'adds': []}
    for d in saves:
        tot = collections.defaultdict(lambda: collections.Counter())
        for (k, o, b), lv in d['own'].items():
            c, cl = classify(d, k, o, b, banks)
            if c:
                tot[c][cl] += lv
                tot['WORLD'][cl] += lv
        res['saves'].append({'date': d['date'], 'levels': {c: dict(v) for c, v in tot.items()}})
    for a, b in zip(saves, saves[1:]):
        add = collections.defaultdict(lambda: collections.Counter())
        for key, lv in b['own'].items():
            d0 = a['own'].get(key, 0)
            if lv > d0:
                c, cl = classify(b, *key, banks)
                if c:
                    add[c][cl] += lv - d0
                    add['WORLD'][cl] += lv - d0
        res['adds'].append({'from': a['date'], 'to': b['date'], 'adds': {c: dict(v) for c, v in add.items()}})
    if len(saves) > 1:
        cum = collections.defaultdict(lambda: collections.Counter())
        for x in res['adds']:
            for c, v in x['adds'].items():
                cum[c].update(v)
        res['adds_total'] = {c: dict(v) for c, v in cum.items()}
        print(f"gross additions {saves[0]['date']} -> {saves[-1]['date']} (levels; pop% = (manor+findist+f_pop) / all private)")
        print('country ' + ' '.join(f'{c:>7}' for c in CLASSES) + '   pop%')
        last = res['saves'][-1]['levels']
        order = sorted(cum, key=lambda c: -sum(last.get(c, {}).values()))
        for c in order[:top + 1]:
            v = cum[c]
            priv = sum(v[x] for x in CLASSES if x not in ('gov', 'f_gov'))
            pop = sum(v[x] for x in POP)
            print(f'{c:7} ' + ' '.join(f'{v[x]:7d}' for x in CLASSES) + f'  {100 * pop / priv if priv else 0:5.1f}')
    d = res['saves'][-1]
    print(f"\nlevels at {d['date']}")
    print('country ' + ' '.join(f'{c:>7}' for c in CLASSES))
    order = sorted(d['levels'], key=lambda c: -sum(d['levels'][c].values()))
    for c in order[:top + 1]:
        v = d['levels'][c]
        print(f'{c:7} ' + ' '.join(f'{v.get(x, 0):7d}' for x in CLASSES))
    if out:
        json.dump(res, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
