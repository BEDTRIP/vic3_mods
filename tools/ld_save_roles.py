"""R1а, проверки до начала (7.10.2026): роли стран и торговля по текстовому сейву.

Usage:
    py tools/ld_save_roles.py [save] [--keys TAG] [--top N]
        save   -- имя в "save games" или полный путь (по умолчанию autosave.v3)
        --keys -- вывести ключи верхнего уровня записи страны TAG и первые записи менеджеров (разведка структуры)
        --top  -- сколько стран показать в таблицах (по умолчанию 40)

Печатает:
  Р17 -- страны по типу (country_type): число, сколько с казной / пулом / своим рынком / торговлей / зданиями кроме
         натуральных хозяйств; список децентрализованных с ненулевым чем-либо.
  Р2  -- торговля по странам: изменение кассы торговых центров нельзя взять из одного сейва, поэтому печатается
         касса торговых центров и торговля рынка (импорт / экспорт по маршрутам) -- для сверки двух сейвов подряд
         запускать на обоих.
"""
import os
import re
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

SAVES = os.path.expanduser(r'~\Documents\Paradox Interactive\Victoria 3\save games')
SUBSISTENCE = re.compile(r'building_subsistence_\w+')


def block(s, key, start=0):
    i = s.find('\n' + key + '={', start)
    if i < 0:
        return '', -1
    nxt = re.compile(r'\n[a-z_]+=\{').search(s, i + len(key) + 3)
    j = nxt.start() if nxt else len(s)
    return s[i:j], i


def records(seg):
    """Records N={ ... } of a manager block (one tab deep), as (id, body)."""
    for mm in re.finditer(r'\n\t(\d+)=\{\n', seg):
        end = seg.find('\n\t}\n', mm.start())
        yield mm.group(1), seg[mm.end():end]


def top_keys(rec, depth=2):
    tab = '\t' * depth
    return re.findall(r'\n' + tab + r'([a-z_0-9]+)=', '\n' + rec)


def num(rec, key, depth=None):
    pat = (r'\n' + '\t' * depth if depth else r'\n\t+') + key + r'=([-\d.]+)'
    mm = re.search(pat, '\n' + rec)
    return float(mm.group(1)) if mm else 0.0


def main():
    args = sys.argv[1:]
    keys_tag = None
    top = 40
    if '--keys' in args:
        i = args.index('--keys'); keys_tag = args[i + 1]; del args[i:i + 2]
    if '--top' in args:
        i = args.index('--top'); top = int(args[i + 1]); del args[i:i + 2]
    path = os.path.join(SAVES, args[0] if args else 'autosave.v3')
    if args and os.path.isabs(args[0]):
        path = args[0]
    s = open(path, 'rb').read().decode('utf-8', 'replace')
    date = re.search(r'game_date=([\d.]+)', s).group(1)
    managers = re.findall(r'\n([a-z_]+)=\{', s)
    print(f'Save {os.path.basename(path)}, date {date}')

    seg, _ = block(s, 'country_manager')
    countries = {}
    for mm in re.finditer(r'\n\t\t(\d+)=\{\n', seg):
        end = seg.find('\n\t\t}\n', mm.start())
        rec = seg[mm.end():end]
        d = re.search(r'\n\t\t\tdefinition="(\w+)"', '\n' + rec)
        if d:
            countries[mm.group(1)] = (d.group(1), rec)
    if not countries:
        # one level less deep
        for cid, rec in records(seg):
            d = re.search(r'\n\t\tdefinition="(\w+)"', '\n' + rec)
            if d:
                countries[cid] = (d.group(1), rec)

    if keys_tag:
        print('top-level managers:', ' '.join(managers))
        for cid, (tag, rec) in countries.items():
            if tag == keys_tag:
                print(f'country {tag} id {cid}, {len(rec)} chars; keys:')
                print(' '.join(dict.fromkeys(top_keys(rec, 3) or top_keys(rec, 2))))
                for k in ('budget', 'market', 'trade', 'gdp', 'country_type', 'money', 'investment_pool'):
                    mm = re.search(r'\n\t+' + k + r'=(\{[^{}]{0,400}|[^\n]*)', '\n' + rec)
                    print(f'  {k}: {mm.group(1)[:300]!r}' if mm else f'  {k}: -')
        for man in ('market_manager', 'trade_route_manager', 'building_manager', 'states', 'pops',
                    'market_goods_manager', 'trade_manager'):
            mseg, _ = block(s, man)
            if not mseg:
                print(f'\n{man}: none')
                continue
            print(f'\n{man}: {len(mseg)} chars; head:')
            print(mseg[:1500])
        return

    # states -> owner country, buildings by owner
    states_seg, _ = block(s, 'states')
    state_owner = {}
    for mm in re.finditer(r'\n\t\t(\d+)=\{\n', states_seg):
        end = states_seg.find('\n\t\t}\n', mm.start())
        rec = states_seg[mm.end():end]
        c = re.search(r'\n\t\t\tcountry=(\d+)', '\n' + rec)
        if c:
            state_owner[mm.group(1)] = c.group(1)
    bm, _ = block(s, 'building_manager')
    btypes = defaultdict(Counter)
    tc_cash = Counter()
    for mm in re.finditer(r'\n\t\t\d+=\{\n\t\t\tbuilding=(\w+)\n(.*?)\n\t\t\}', bm, re.S):
        body = mm.group(2)
        st = re.search(r'\n\t\t\tstate=(\d+)', '\n' + body)
        own = state_owner.get(st.group(1)) if st else None
        if own is None:
            continue
        btypes[own][mm.group(1)] += 1
        if mm.group(1) == 'building_trade_center':
            tc_cash[own] += num(body, 'cash_reserves', 3)

    # markets: owner country -> market id
    mk, _ = block(s, 'market_manager')
    market_owner = {}
    for mm in re.finditer(r'\n\t\t(\d+)=\{\n', mk):
        end = mk.find('\n\t\t}\n', mm.start())
        rec = mk[mm.end():end]
        o = re.search(r'\n\t\t\towner=(\d+)', '\n' + rec)
        if o:
            market_owner[o.group(1)] = mm.group(1)

    rows = []
    for cid, (tag, rec) in countries.items():
        ct = re.search(r'country_type="?(\w+)', rec)
        ct = ct.group(1) if ct else '?'
        g = re.search(r'\tgdp=\{.*?values=\{ ([^}]*)\}', rec, re.S)
        gdp = float(g.group(1).split()[-1]) if g else 0.0
        money = num(rec, 'money')
        pool = num(rec, 'investment_pool')
        nst = sum(1 for o in state_owner.values() if o == cid)
        bt = btypes.get(cid, Counter())
        non_sub = {k: v for k, v in bt.items() if not SUBSISTENCE.fullmatch(k)}
        rows.append(dict(cid=cid, tag=tag, type=ct, gdp=gdp, money=money, pool=pool, states=nst,
                         market=cid in market_owner, non_sub=non_sub, tc=tc_cash.get(cid, 0.0)))

    alive = [r for r in rows if r['states']]
    print(f'countries in the save: {len(rows)}, with states: {len(alive)}')
    by = defaultdict(list)
    for r in alive:
        by[r['type']].append(r)
    print('\nР17 -- by country_type (with states):')
    print(f'  {"type":<16}{"n":>5}{"money≠0":>9}{"pool>0":>8}{"market":>8}{"non-subs":>10}{"trade c.":>10}')
    for t, rs in sorted(by.items(), key=lambda kv: -len(kv[1])):
        print(f'  {t:<16}{len(rs):>5}{sum(1 for r in rs if abs(r["money"]) > 1):>9}'
              f'{sum(1 for r in rs if r["pool"] > 1):>8}{sum(1 for r in rs if r["market"]):>8}'
              f'{sum(1 for r in rs if r["non_sub"]):>10}'
              f'{sum(1 for r in rs if "building_trade_center" in r["non_sub"]):>10}')
    dec = by.get('decentralized', [])
    if dec:
        nb = Counter()
        for r in dec:
            nb.update(r['non_sub'])
        print(f'\n  decentralized: money {sum(r["money"] for r in dec):,.0f}, pool {sum(r["pool"] for r in dec):,.0f},'
              f' GDP {sum(r["gdp"] for r in dec):,.0f}; non-subsistence buildings: {dict(nb.most_common(15))}')

    alive.sort(key=lambda r: -r['gdp'])
    print(f'\nGDP ranks (country_type; 40th and 50th for the role threshold):')
    for i in (0, 9, 19, 29, 39, 49, 59, 79, 99):
        if i < len(alive):
            r = alive[i]
            print(f'  #{i + 1:<4}{r["tag"]:<5}{r["type"]:<14}GDP {r["gdp"]:>14,.0f}')
    print(f'\nР2 -- trade centres\' cash, top {top} by GDP:')
    for r in alive[:top]:
        print(f'  {r["tag"]:<5}{r["type"]:<14}GDP {r["gdp"]:>14,.0f}  treasury {r["money"]:>13,.0f}'
              f'  pool {r["pool"]:>12,.0f}  trade centres {r["non_sub"].get("building_trade_center", 0):>3}'
              f'  cash {r["tc"]:>12,.0f}  own market {"yes" if r["market"] else "no"}')


if __name__ == '__main__':
    main()
