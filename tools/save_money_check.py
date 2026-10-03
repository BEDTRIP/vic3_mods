"""UI.9 step 3 (3.10.2026): money accounts of a country straight from a text save -- to check the in-game
money tooltips against the engine's own numbers, independently of the mod's GUI.

Usage:
    py tools/save_money_check.py [save] [TAG ...]
        save -- a name in "save games" or a full path (default autosave.v3)
        TAG  -- country tags (default: the player and the five biggest by GDP)

Prints per country, for the save's date:
  ENGINE (as stored, the tooltips' "дв" marks): treasury (money), the buildings' cash (sum of cash_reserves over the
  country's states; of it trade centres), the investment pool, credit limit and debt, GDP, and the budget of the
  last week as the engine stored it (budget.weekly_income / weekly_expenses -- exact week, not the smoothed trends
  the budget panel and the tooltips show);
  MODEL (the mod's variables, "мод"/"расч"): pops' savings, deposits and cash at hand, consumer credit, business
  credit, banks' debt to the CB, the CB's metal (gold_state_1 / silver_state_1 over the country's states) and parity,
  and what the model recorded at its last weekly step (zz_ef_prev_*) -- a difference against ENGINE is what
  changed after that step.

Budget index -> line: matched 3.10 against the budget panel of the same save (Britain 1839.7); entries with "?" are
not confirmed -- the raw value is printed anyway.
Variables are stored x 1e5; negative ones as unsigned 64-bit (read as value - 2^64 / 1e5).
"""
import os
import re
import sys

SAVES = os.path.expanduser(r'~\Documents\Paradox Interactive\Victoria 3\save games')

INCOME = {0: "дополнительный доход", 1: "подоходные налоги", 2: "подушные налоги", 3: "потребительские налоги",
          4: "налоги на дивиденды", 5: "дипломатические пакты", 6: "бюджет блока? (не подтверждено)",
          7: "трансфер инвестиционного пула", 8: "денежное производство", 9: "? (не подтверждено)",
          10: "государственные дивиденды", 11: "договоры? (не подтверждено)",
          12: "сеть снабжения? (не подтверждено)", 13: "пошлины (tolls)", 14: "пиратство? (не подтверждено)",
          15: "сборы с рынка? (не подтверждено)"}
EXPENSE = {0: "дополнительные расходы", 1: "? (не подтверждено)", 2: "товары для правительственных сооружений",
           3: "государственные зарплаты", 4: "? (не подтверждено)", 5: "товары для вооружённых сил",
           6: "зарплаты военных", 7: "строительные товары", 8: "субсидии", 9: "субвенции", 10: "? (не подтверждено)",
           11: "дипломатические пакты", 12: "? (не подтверждено)", 13: "? (не подтверждено)",
           14: "убытки государственных предприятий", 15: "социальные выплаты? (не подтверждено)",
           16: "налоговые потери? (не подтверждено)", 17: "? (не подтверждено)", 18: "? (не подтверждено)",
           19: "содержание кораблей снабжения", 20: "содержание военных кораблей", 21: "маршруты поставок"}

VAR_RE = re.compile(r'flag=(\w+)\n(?:\t+tick=\d+\n)?\t+data=\{\n\t+type=\w+\n(?:\t+identity=(-?\d+))?')


def var_value(raw):
    if not raw:
        return 0.0
    v = int(raw)
    if v > 2 ** 63:
        v -= 2 ** 64
    return v / 1e5


def block(s, key, start=0):
    i = s.find('\n' + key + '={', start)
    if i < 0:
        return '', -1
    # records inside are N={ ... } at column 0 too, so the block ends at the next top-level key
    nxt = re.compile(r'\n[a-z_]+=\{').search(s, i + len(key) + 3)
    j = nxt.start() if nxt else len(s)
    return s[i:j], i


def m(x):
    return f'{x / 1e6:10.3f}M' if abs(x) >= 1e5 else f'{x:11,.0f}'


def main():
    args = sys.argv[1:]
    path = os.path.join(SAVES, 'autosave.v3')
    if args and not re.fullmatch(r'[A-Z][A-Z0-9]{2}', args[0]):
        path = args.pop(0)
        if not os.path.isabs(path):
            path = os.path.join(SAVES, path)
    s = open(path, 'rb').read().decode('utf-8', 'replace')
    date = re.search(r'game_date=([\d.]+)', s).group(1)
    player = re.search(r'\bplayer_country_name="?([^"\n]*)', s)

    seg, _ = block(s, 'country_manager')
    countries = {}
    for mm in re.finditer(r'\n(\d+)=\{\n(?:\t[^\n]*\n){0,3}?\tdefinition="(\w+)"', seg):
        rec = seg[mm.start():seg.find('\n}\n', mm.start())]
        countries[mm.group(1)] = (mm.group(2), rec)

    states_seg, _ = block(s, 'states')
    state_owner, state_vars = {}, {}
    for mm in re.finditer(r'\n(\d+)=\{\n', states_seg):
        end = states_seg.find('\n}\n', mm.start())
        rec = states_seg[mm.start():end]
        c = re.search(r'\n\tcountry=(\d+)', rec)
        if c:
            state_owner[mm.group(1)] = c.group(1)
            v = {k: var_value(x) for k, x in VAR_RE.findall(rec)}
            if v.get('gold_state_1') or v.get('silver_state_1'):
                state_vars[mm.group(1)] = v

    bm, _ = block(s, 'building_manager')
    cash, tc = {}, {}
    for mm in re.finditer(r'\n\d+=\{\n\tbuilding=(\w+)\n(.*?)\n\}', bm, re.S):
        body = mm.group(2)
        st = re.search(r'\n\tstate=(\d+)', '\n' + body)
        cr = re.search(r'\n\tcash_reserves=([-\d.]+)', '\n' + body)
        if not st or not cr:
            continue
        own = state_owner.get(st.group(1))
        if own is None:
            continue
        cash[own] = cash.get(own, 0) + float(cr.group(1))
        if mm.group(1) == 'building_trade_center':
            tc[own] = tc.get(own, 0) + float(cr.group(1))

    def gdp_of(rec):
        g = re.search(r'\tgdp=\{.*?values=\{ ([^}]*)\}', rec, re.S)
        return float(g.group(1).split()[-1]) if g else 0.0

    tags = args
    if not tags:
        tags = [t for _, (t, rec) in sorted(countries.items(), key=lambda kv: -gdp_of(kv[1][1]))[:5]]
    by_tag = {t: (cid, rec) for cid, (t, rec) in countries.items()}

    print(f'Save {os.path.basename(path)}, date {date}' + (f', player {player.group(1)}' if player else ''))
    for tag in tags:
        if tag not in by_tag:
            print(f'\n{tag}: not in the save')
            continue
        cid, rec = by_tag[tag]
        v = {k: var_value(x) for k, x in VAR_RE.findall(rec)}
        num = lambda key: float(re.search(r'\n\t\t' + key + r'=([-\d.]+)', rec).group(1)) \
            if re.search(r'\n\t\t' + key + r'=([-\d.]+)', rec) else 0.0
        print(f'\n===== {tag} ({date}) =====')
        print('ENGINE (дв, as stored)')
        print(f'  казна (money)                  {m(num("money"))}')
        print(f'  касса предприятий (Σ cash)     {m(cash.get(cid, 0))}   из них торговые центры {m(tc.get(cid, 0))}')
        print(f'  инвестиционный пул             {m(num("investment_pool"))}')
        print(f'  кредитный лимит / долг         {m(num("credit"))} / {m(num("principal"))}')
        print(f'  ВВП (год)                      {m(gdp_of(rec))}')
        for name, table in (('weekly_income', INCOME), ('weekly_expenses', EXPENSE)):
            arr = re.search(r'\t' + name + r'=\{ ([^}]*)\}', rec)
            if not arr:
                continue
            vals = [float(x) for x in arr.group(1).split()]
            print(f'  бюджет за неделю, {"доходы" if name == "weekly_income" else "расходы"}: всего {m(sum(vals))}')
            for i, x in enumerate(vals):
                if x:
                    print(f'      [{i:2}] {m(x)}  {table.get(i, "?")}')
        print('MODEL (мод / расч, variables)')
        sav, dep = v.get('zz_ef_pop_savings', 0), v.get('zz_ef_pop_deposits', 0)
        print(f'  накопления населения           {m(sav)}   вклады {m(dep)}   на руках {m(sav - dep)}')
        print(f'  потребкредит (долг)            {m(v.get("zz_ef_cc_debt", 0))}')
        print(f'  кредит бизнесу (долг)          {m(v.get("zz_ef_bc_debt", 0))}')
        print(f'  долг банков перед ЦБ           {m(v.get("zz_ef_bank_cb_debt", 0))}')
        gold = sum(sv.get('gold_state_1', 0) for st, sv in state_vars.items() if state_owner.get(st) == cid)
        silver = sum(sv.get('silver_state_1', 0) for st, sv in state_vars.items() if state_owner.get(st) == cid)
        parity = v.get('money_value_target_1', 0)
        print(f'  металл в областях страны       золото {m(gold)}   серебро {m(silver)}   паритет {parity:.4f} металла за ед.')
        if parity:
            # E&F keeps the standard as variables law_<standard> = 1 (gold for bimetallism, as the model)
            metal = silver if v.get('law_silver_standard') == 1 else gold
            std = next((k[4:] for k in ('law_gold_standard', 'law_silver_standard', 'law_bimetallism_standard',
                                        'law_gold_exchange_standard', 'law_fiat_standard') if v.get(k) == 1), '?')
            print(f'  стандарт (переменная E&F)      {std}')
            print(f'  металл по паритету (≈ резервы ЦБ в деньгах) {m(metal / parity)}   (подсказка: «Резервы ЦБ»)')
        print('  последний шаг модели (zz_ef_prev_*), против движка выше:')
        for key, lab, eng in (('treasury', 'казна', num('money')), ('buildings', 'касса предприятий', cash.get(cid, 0)),
                              ('pool', 'пул', num('investment_pool'))):
            pv = v.get('zz_ef_prev_' + key)
            if pv is not None:
                print(f'      {lab:<20} модель {m(pv)}   движок сейчас {m(eng)}   разница {m(eng - pv)}')


if __name__ == '__main__':
    main()
