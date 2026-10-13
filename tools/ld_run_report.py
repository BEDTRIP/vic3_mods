"""The run report of the fork: one HTML page, the same for every sandbox run (форк, разбор прогонов; навык run-report).

Usage:
    py tools/ld_run_report.py <run> <out.html> [--until 1847.12] [--data <out.json>] [--base <data.json>] [--title T]
    py tools/ld_run_report.py --from-data <data.json> <out.html> [--base <data.json>]

<run> -- the run's folder (runs/<id>: eflog.txt, error*.log or errparts/). The first form reads the run and writes the
page (and, with --data, the run's data for later -- a base to compare with or the page built elsewhere); the second
builds the page from saved data (the bridge: the data is made on the PC with --data and read back in parts, the page is
built here). --base -- another run's data: a table «этот прогон / база» by year.

What it reads (the fork's logs with zz_ef_logs_on): EFW|WORLD|acc, EFW|<country>|acc / budget / all, EFV|WORLD and
EFV|<owner>|mkt, EFJ WORLD other, EFJ|lvl, EFJ|bank_sum, EFK|bank_fail, EFQ, EFZ, EFD|<exchange>|xch_month; the error
logs: «Script location:» lines by file. The page: checks, a short summary with thresholds, money, «прочее» and the
levels bought, metal (world, holders, markets, the pops' hoard against its target), the pool by country, budget and
debt (a chosen country), people, construction, exchanges, banks; each section with a fixed explanation of what it shows.
"""
import glob
import json
import os
import re
import sys
from collections import defaultdict

MON = {'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
       'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12,
       'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8,
       'September': 9, 'October': 10, 'November': 11, 'December': 12}
DATE = re.compile(r'(\w+) (\d+), (\d{4})')
GOLD_U, SILVER_U = 100, 775          # account units a good of gold / silver
TOP = 12                             # countries with monthly series (by GDP at the end)
# the unexplained remainders a week (EFO, EFR): key -> what account
REST_KEYS = {'b_rest': 'касса предприятий', 'pool_rest': 'банки и пул', 'abr_rest': 'заграница', 'tr_rest': 'казна',
             'cbm_rest': 'ЦБ', 'pop_rest': 'наличные населения', 'dep_rest': 'вклады населения'}
# the engine's market gap -- a line of the business cash's card (Д.R4б.21), not a remainder: EFR leak
# words that name a form of state, not the country: not a stem to join a revolution's country by
GENERIC = {'респу', 'корол', 'импер', 'восст', 'радик', 'народ', 'социа', 'федер', 'конфе', 'княже', 'герцо', 'султа',
           'ханст', 'держа', 'госуд', 'компа', 'терри', 'колон', 'прови', 'союзн', 'объед', 'соеди', 'демок', 'совет',
           'комму', 'рабоч', 'вольн', 'свобо', 'север', 'южная', 'южный', 'запад', 'восто', 'верхн', 'нижня',
           'вели', 'велик', 'новая', 'новый', 'транс', 'либер', 'консе', 'крест', 'аболи', 'рабов', 'рабол', 'нацио',
           'фунда', 'мятеж', 'анарх', 'монар', 'респу', 'теокр', 'клери', 'реакц', 'прогр', 'мусул'}
# the keys that are shares or indices: joined by GDP weights, not summed
RATIO_KEYS = {'price', 'cover', 'popm_share', 'popm_target', 'radical', 'loyalist', 'sol', 'legit', 'literacy', 'cb'}
ALL_KEYS = ('gdp', 'm2', 'price', 'pool', 'pool_constr', 'treasury', 'debt', 'credit', 'inc', 'exp', 'savings',
            'deposits', 'loans', 'bkcap', 'popm', 'popm_share', 'popm_target', 'popm_cb', 'popm_bank', 'radical',
            'loyalist', 'sol', 'legit', 'govlv', 'privlv', 'cover', 'bonds_abroad', 'cbm', 'trm', 'bankm')


def day(s):
    """The game date as a day number (the world's week takes the countries' lines of the days before it)."""
    m = DATE.match(s)
    if not m or m.group(1) not in MON:
        return 0
    return int(m.group(3)) * 372 + MON[m.group(1)] * 31 + int(m.group(2))


def ym(s):
    m = DATE.match(s)
    if not m or m.group(1) not in MON:
        return None
    return int(m.group(3)), MON[m.group(1)]


def fields(parts):
    d = {}
    for x in parts:
        k, _, v = x.partition(' ')
        try:
            d[k] = float(v)
        except ValueError:
            pass
    return d


def r4(v):
    if v is None or v == 0:
        return v
    from math import floor, log10
    return round(v, -int(floor(log10(abs(v)))) + 3)


def errors(run):
    files = sorted(glob.glob(os.path.join(run, 'errparts', '*'))) or sorted(glob.glob(os.path.join(run, 'error*.log')))
    # the script errors of the running game also land in game.log (r1013_011039: 32 of the fork's, none in error.log)
    files += sorted(glob.glob(os.path.join(run, 'game*.log')))
    cnt = defaultdict(int)
    seen = set()
    for p in files:
        try:
            txt = open(p, encoding='utf-8', errors='replace').read()
        except OSError:
            continue
        for blk in txt.split('\n['):
            m = re.search(r'Script location: (common/[^\s:]+):(\d+)', blk)
            if not m:
                continue
            key = blk[:400]
            if key in seen:
                continue
            seen.add(key)
            cnt[m.group(1)] += 1
    return sorted(cnt.items(), key=lambda kv: -kv[1])


def read_run(run, until):
    lim = (int(until), round((until - int(until)) * 100) or 12)
    last = defaultdict(dict)                      # key -> {month: stock}
    avg = defaultdict(lambda: defaultdict(list))  # key -> month -> values
    summ = defaultdict(lambda: defaultdict(float))
    cty = defaultdict(lambda: defaultdict(dict))  # country -> key -> {month: value}
    cavg = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    xch = defaultdict(lambda: defaultdict(dict))
    xlast = {}
    allc = defaultdict(dict)                      # country -> last EFW|all fields
    first_seen, last_seen, gdp0 = {}, {}, {}
    tags = {}                                     # country name -> its tag (EFW|all 'tag')
    mkt_of = {}                                   # (country, date) -> its market's owner tag (EFM)
    mkt_gap = defaultdict(float)                  # market owner tag -> the run's market gap (EFM bal)
    mkt_grp = defaultdict(lambda: defaultdict(float))  # market owner tag -> goods group -> the run's gap (EFM gap_*)
    lk_first, lk_last = {}, {}                    # country -> (market, leak_cum, gap_cum): first after January, last
    gap_wk = {}                                   # (country, date) -> the week's line «engine: the market gap» (EFR leak)
    gap_cty = defaultdict(float)                  # country -> the line over the run
    cwk = []                                      # (day, country, its «прочее» of the week) -- for the world's weeks
    xtot = defaultdict(float)                     # exchange -> the run's turnover
    fills = defaultdict(lambda: defaultdict(list))  # month -> metal -> [(fill, buy orders)]
    bsub = defaultdict(float)                     # date -> the world's bank subjects that week
    leak = {}                                     # country -> its «прочее»: first, last, parts, biggest week
    rest_cty = {}                                 # remainder kind -> country -> sum over the run
    rest_week = defaultdict(list)                 # remainder kind -> the biggest weeks
    week_top = defaultdict(list)                  # date -> the 3 countries with the biggest «прочее» of the week
    world_week = []                               # (date, the world's «прочее» of the week)
    chk = dict(lines=0, efq=0, diff=0.0, mdiff=0.0, mdiff_at='', fails=[], last='')
    other = other_tr = 0.0
    mo0 = None
    items = {}
    path = os.path.join(run, 'eflog.txt')
    for ln in open(path, encoding='utf-8', errors='replace'):
        if len(ln) < 6 or ln[0] != 'E' or ln[3] != '|':
            continue
        p = ln.rstrip('\n').split('|')
        if len(p) < 4:
            continue
        mo = ym(p[1])
        if mo is None or mo > lim:
            continue
        chk['lines'] += 1
        chk['last'] = p[1]
        if chk['lines'] == 1:
            mo0 = mo                              # the first month: the start's setup, not a remainder
        pre, who, k3 = p[0], p[2], p[3]
        summ['o.lines'][mo] += 1
        if pre == 'EFI' and who == 'WORLD':
            d = fields(p[3:])
            last['o.claims'][mo] = d.get('n_m', 0) + d.get('n_b', 0) + d.get('n_f', 0)
        elif pre == 'EFG' and who == 'WORLD':
            avg['o.clearing'][mo].append(fields(p[3:]).get('n', 0))
        elif pre == 'EFD' and who == 'WORLD':
            d = fields(p[3:])
            for k in ('orders', 'deals', 'assets'):
                if k in d:
                    last['o.' + k][mo] = d[k]
        elif pre == 'EFJ' and k3 == 'bank_subj':
            bsub[p[1]] += fields(p[4:]).get('n', 0)
        elif pre == 'EFU':
            summ['o.funds_l'][mo] += 1
        elif pre == 'EFV' and k3 == 'mkt':
            summ['o.markets'][mo] += 1
        if pre == 'EFW' and k3 == 'all':
            summ['o.countries'][mo] += 1
        if pre == 'EFR' and 'leak ' in ln:
            v = fields(p[3:]).get('leak', 0)
            summ['r.eng_gap'][mo] += v
            if mo != mo0:
                gap_wk[(who, p[1])] = v
                gap_cty[who] += v
        if pre == 'EFO':
            # the unexplained remainder of each account a week: the change less every known item (business cash,
            # banks, abroad, treasury, CB, the pops' cash and deposits)
            d = fields(p[3:])
            for k in REST_KEYS:
                if k in d and d[k]:
                    v = d[k]
                    summ['r.' + k][mo] += v
                    if mo == mo0:
                        continue
                    rc = rest_cty.setdefault(k, defaultdict(float))
                    rc[who] += v
                    top = rest_week[k]
                    top.append((abs(v), p[1], who, v))
                    if len(top) > 40:
                        top.sort(reverse=True)
                        del top[10:]
        if pre == 'EFM':
            # the engine's market gap (the owner's line: Σ goods (sold - bought by the orders) x price) and each logged
            # country's market -- against the business cash's remainder
            d = fields(p[3:])
            mk = next((x[4:].strip() for x in p[3:] if x.startswith('mkt ')), '?')
            mkt_of[(who, p[1])] = mk
            if 'bal' in d:
                summ['r.mkt_gap'][mo] += d['bal']
                mkt_gap[mk] += d['bal']
                for g in ('fin', 'psc', 'metal'):
                    v = d.get('gap_' + g)
                    if isinstance(v, float):
                        summ['r.gap_' + g][mo] += v
                        mkt_grp[mk][g] += v
        if pre == 'EFQ':
            chk['efq'] += 1
            d = fields(p[3:])
            summ['r.efq_g'][mo] += d.get('oth_g', 0)
            summ['r.efq_s'][mo] += d.get('oth_s', 0)
        elif pre == 'EFK' and k3 == 'bank_fail':
            chk['fails'].append(p[1:])
        elif pre == 'EFJ' and k3 == 'bank_sum':
            d = fields(p[4:])
            chk['diff'] = max(chk['diff'], abs(d.get('diff', 0)))
            if abs(d.get('map_diff', 0)) > chk['mdiff']:
                chk['mdiff'] = abs(d.get('map_diff', 0))
                chk['mdiff_at'] = f'{p[1]}, {who}'
        elif pre == 'EFW' and len(p) > 4 and k3 == 'acc':
            d = fields(p[4:])
            if who == 'WORLD':
                for k, v in d.items():
                    last['w.' + k][mo] = v
        elif pre == 'EFW' and len(p) > 4 and k3 == 'budget':
            for k, v in fields(p[4:]).items():
                cavg[who][k][mo].append(v)
        elif pre == 'EFW' and len(p) > 4 and k3 == 'all':
            d = fields(p[4:])
            allc[who] = dict(d, _date=p[1])
            if isinstance(d.get('leak_cum'), float):
                # the line «engine: the market gap» of every country (not only the logged ones) and its market's gap,
                # summed since the start; January is the start's setup
                mk = next((x[4:].strip() for x in p[4:] if x.startswith('mkt ')), '?')
                rec = (mk, d['leak_cum'],
                       d['gap_cum'] if isinstance(d.get('gap_cum'), float) else None)
                if who not in lk_first and mo != mo0:
                    lk_first[who] = rec
                if who in lk_first:
                    lk_last[who] = rec
            for x in p[4:6]:
                if x.startswith('tag '):
                    tags[who] = x[4:].strip()
            if who not in first_seen:
                first_seen[who] = mo
                gdp0[who] = d.get('gdp', 0)
            last_seen[who] = mo
            for k in ALL_KEYS:
                if k in d:
                    cty[who][k][mo] = d[k]
            for k in ('pool', 'm2', 'gdp', 'debt', 'credit', 'popm', 'savings', 'treasury', 'bkcap', 'loans',
                      'deposits', 'popm_cb', 'popm_bank', 'bonds_abroad', 'cbm', 'trm', 'bankm'):
                if k in d:
                    summ['a.' + k][mo] += d[k]
            if 'popm_target' in d and 'savings' in d:
                summ['a.target_money'][mo] += d['popm_target'] * (d['savings'] + d.get('popm', 0))
        elif pre == 'EFZ':
            d = fields(p[3:])
            for k in ('pts', 'total', 'csec_lv'):
                if k in d:
                    cavg[who]['psc_' + k][mo].append(d[k])
        elif pre == 'EFV' and who == 'WORLD':
            for k, v in fields(p[3:]).items():
                avg['m.' + k][mo].append(v)
                if k in ('buy_g', 'sell_g', 'buy_s', 'sell_s'):
                    last['m.last_' + k][mo] = v
        elif pre == 'EFV' and len(p) > 4 and k3 == 'mkt':
            d = fields(p[4:])
            for m in ('g', 's'):
                if d.get('buyo_' + m, 0) > 0:
                    fills[mo][m].append((d.get('fill_' + m, 1), d['buyo_' + m]))
        elif pre == 'EFJ' and k3 == 'lvl':
            d = fields(p[4:])
            summ['l.steps'][mo] += 1
            summ['l.pool'][mo] += d.get('pool', 0)
            summ['l.tr'][mo] += d.get('tr', 0)
            summ['l.d_govlv'][mo] += d.get('d_govlv', 0)
        elif pre == 'EFJ' and who == 'WORLD' and k3.startswith('other '):
            d = fields(p[3:])
            other += d.get('other', 0)
            other_tr += d.get('other_tr', 0)
            world_week.append((p[1], d.get('other', 0), day(p[1])))
            last['w.other'][mo] = other
            last['w.other_tr'][mo] = other_tr
        elif pre == 'EFJ' and k3.startswith('other '):
            d = fields(p[3:])
            # leaks: «прочее» of the country -- at its first line, at its last, its biggest week; the week's biggest
            lk = leak.setdefault(who, {'first': d.get('other', 0), 'first_at': p[1], 'jump': 0, 'jump_at': ''})
            lk['last'] = d.get('other', 0)
            lk['last_at'] = p[1]
            for k in ('other_pool', 'other_tr', 'lvl_pool', 'lvl_tr', 'bk_woff', 'heir_debt'):
                if k in d:
                    lk[k] = d[k]
            dw = d.get('d_other', 0)
            if abs(dw) > abs(lk['jump']):
                lk['jump'], lk['jump_at'] = dw, p[1]
            if dw:
                cwk.append((day(p[1]), who, dw))
            for k in ('lvl_pool', 'lvl_tr'):
                if k in d:
                    items[(k, who)] = d[k]
                    last['l.' + k][mo] = sum(v for (kk, _), v in items.items() if kk == k)
        elif pre == 'EFD' and len(p) > 4 and k3 == 'xch_month':
            d = fields(p[4:])
            for k in ('to_g', 'heat', 'cap_g', 'members'):
                if k in d:
                    xch[who][k][mo] = d[k]
            xtot[who] += d.get('to_g', 0)
            xlast[who] = dict(d, _date=p[1])
    # the world's week (the world pass) takes the countries' lines since the last world line: the countries step on
    # their own days of the week
    cwk.sort()
    i = 0
    prev = -1
    for dt, _, dd in sorted(world_week, key=lambda x: x[2]):
        while i < len(cwk) and cwk[i][0] <= dd:
            if cwk[i][0] > prev:
                week_top[dt].append((abs(cwk[i][2]), cwk[i][1], cwk[i][2]))
            i += 1
        week_top[dt] = sorted(week_top[dt], reverse=True)[:3]
        prev = dd
    # the engine's market gap by market against the line of its logged members (the EFM line comes after EFO / EFR)
    mkt_line = defaultdict(float)
    for key, v in gap_wk.items():
        if key in mkt_of:
            mkt_line[mkt_of[key]] += v
    # every country of the market (EFW|all leak_cum) against the owner's gap (gap_cum), when the log has them
    mkt_all, mkt_n, mkt_gcum = defaultdict(float), defaultdict(int), {}
    for c, (mk, lc, gc) in lk_last.items():
        f = lk_first[c]
        mkt_all[mk] += lc - f[1]
        mkt_n[mk] += 1
        if gc is not None and tags.get(c) == mk:
            mkt_gcum[mk] = gc - (f[2] or 0)
    if mkt_gcum:
        mkt_rows = [(m, mkt_n[m], round(mkt_all[m]), round(g), {k: round(v) for k, v in mkt_grp[m].items()})
                    for m, g in sorted(mkt_gcum.items(), key=lambda kv: kv[1])[:20]]
        mkt_world = (round(sum(mkt_all.values())), round(sum(mkt_gcum.values())))
    else:
        mkt_rows = [(m, 0, round(mkt_line.get(m, 0)), round(g), {k: round(v) for k, v in mkt_grp[m].items()})
                    for m, g in sorted(mkt_gap.items(), key=lambda kv: kv[1])[:15]]
        mkt_world = None
    for dt, n in bsub.items():
        avg['o.banks'][ym(dt)].append(n)
    months = sorted({m for s in last.values() for m in s} | {m for s in avg.values() for m in s}
                    | {m for s in summ.values() for m in s})
    idx = {m: i for i, m in enumerate(months)}

    def ser(dm):
        v = [None] * len(months)
        for m, x in dm.items():
            if m in idx:
                v[idx[m]] = r4(x)
        return v
    S = {'t': [round(y + (m - 1) / 12, 3) for y, m in months]}
    for k, dm in last.items():
        S[k] = ser(dm)
    for k, dm in avg.items():
        S[k] = ser({m: sum(x) / len(x) for m, x in dm.items()})
    for k, dm in summ.items():
        S[k] = ser(dm)
    for metal, u in (('g', GOLD_U), ('s', SILVER_U)):
        for side in ('buy', 'sell'):
            dm = last.get(f'm.last_{side}_{metal}', {})
            ms = sorted(dm)
            wk = {}
            for i in range(1, len(ms)):
                y0, m0 = ms[i - 1]
                y1, m1 = ms[i]
                wk[ms[i]] = (dm[ms[i]] - dm[ms[i - 1]]) / (((y1 - y0) * 12 + (m1 - m0)) * 52 / 12) / u
            S[f'm.{side}w_{metal}'] = ser(wk)
        # markets: the share of the world's buy orders met (weighted fill), the markets with a shortage
        S[f'k.fill_{metal}'] = ser({m: sum(f * b for f, b in fills[m][metal]) / sum(b for _, b in fills[m][metal])
                                    for m in fills if fills[m][metal]})
        S[f'k.short_{metal}'] = ser({m: sum(1 for f, _ in fills[m][metal] if f < 0.99) for m in fills if fills[m][metal]})
    # months whose country lines were lost (the debug log's parts are copied while the game writes; a month with under 80 %
    # of the usual lines): the world's sums of them are not shown, the months are listed in the checks
    oc = [x for x in S.get('o.countries') or [] if x]
    lost = []
    if oc:
        med = sorted(oc)[len(oc) // 2]
        g = S.get('a.gdp') or []

        def gdp_dip(i):
            # the big countries' lines lost: the month's world GDP under 90 % of both neighbours'
            if i <= 0 or i + 1 >= len(g) or not g[i] or not g[i - 1] or not g[i + 1]:
                return False
            return g[i] < 0.9 * min(g[i - 1], g[i + 1])
        for i, x in enumerate(S['o.countries']):
            if x is not None and (x < 0.8 * med or gdp_dip(i)):
                lost.append(S['t'][i])
                for k in list(S):
                    if k.startswith('a.') or k in ('o.countries', 'o.markets'):
                        S[k][i] = None
    chk['lost'] = [f'{int(x)}.{round((x - int(x)) * 12) + 1:02d}' for x in lost]
    # revolutions: a country that appears during the run (a civil war's rebels, a republic after a revolution) is joined
    # to the country of the start -- by its tag first (a country renamed keeps it: France -> the French Republic), else by
    # the same stem of its name (the rebels get a new tag) -- so that the statistics of Britain and its radicals stay one
    # line
    t0 = months[0] if months else None
    new = [c for c, m in first_seen.items() if t0 and m > (t0[0], t0[1] + 2 if t0[1] <= 10 else 12)]
    gone = [c for c, m in last_seen.items() if months and m < months[-1]]
    start = [c for c in gdp0 if c not in new]
    joined = {}
    def stems(name):
        return {w.lower()[:5] for w in re.findall(r'[А-Яа-яЁёA-Za-z]{5,}', name)} - GENERIC

    def months_apart(a, b):
        return abs((a[0] - b[0]) * 12 + a[1] - b[1])
    for c in new:
        same = [p for p in start if tags.get(c) and tags.get(p) == tags.get(c)]
        if same:
            joined[c] = same[0]
            continue
        best, best_score = None, 0
        for p in start:
            shared = sum(1 for st in stems(c) if st in p.lower())
            if not shared:
                continue
            # a start country gone the month the new one comes -- the same country renamed (a republic, a company)
            renamed = p in gone and months_apart(last_seen[p], first_seen[c]) <= 2
            score = shared + (3 if renamed else 0) + gdp0.get(p, 0) * 1e-12
            if score > best_score:
                best, best_score = p, score
        if best:
            joined[c] = best
    for c, parent in joined.items():
        for k in set(cty[c]) | set(cty[parent]):
            a, b = cty[parent].get(k, {}), cty[c].get(k, {})
            ga, gb = cty[parent].get('gdp', {}), cty[c].get('gdp', {})
            for m, v in b.items():
                if k in RATIO_KEYS:
                    wa, wb = ga.get(m, 0), gb.get(m, 0)
                    if m in a and wa + wb > 0:
                        a[m] = (a[m] * wa + v * wb) / (wa + wb)
                    elif m not in a:
                        a[m] = v
                else:
                    a[m] = a.get(m, 0) + v
            cty[parent][k] = a
        for k, dm in cavg[c].items():
            for m, vs in dm.items():
                pv = cavg[parent][k][m]
                if pv and vs:
                    tot = sum(pv) / len(pv) + sum(vs) / len(vs)
                    cavg[parent][k][m] = [tot]
                elif vs:
                    cavg[parent][k][m] = list(vs)
        for k, v in allc.get(c, {}).items():
            if isinstance(v, float) and k not in RATIO_KEYS and last_seen.get(c) == last_seen.get(parent):
                allc[parent][k] = allc[parent].get(k, 0) + v
    # «прочее» of a renamed country (the same tag) continues its own running total: the new name's line is the
    # country's, the old one's -- its past (France and the French Republic were both shown, the total twice)
    for c, parent in joined.items():
        renamed = parent in gone and months_apart(last_seen[parent], first_seen[c]) <= 2
        if renamed and tags.get(c) and tags.get(c) == tags.get(parent) and c in leak:
            a, b = leak.setdefault(parent, dict(leak[c])), leak.pop(c)
            for k, v in b.items():
                if k not in ('first', 'first_at', 'jump', 'jump_at'):
                    a[k] = v
            if abs(b.get('jump', 0)) > abs(a.get('jump', 0)):
                a['jump'], a['jump_at'] = b['jump'], b['jump_at']
    for c in joined:
        cty.pop(c, None)
        cavg.pop(c, None)
        gdp0.pop(c, None)
        if c in allc and joined[c] in allc:
            allc.pop(c)
    # the countries with monthly series: the largest by GDP at the start (the reference -- Britain -- among them, even
    # if a revolution takes it apart) and at the end
    gdp_end = {c: d.get('gdp', 0) for c, d in allc.items()}
    big = sorted(gdp0, key=lambda c: -gdp0[c])[:6]
    for c in sorted(gdp_end, key=lambda c: -gdp_end[c]):
        if len(big) >= TOP:
            break
        if c not in big:
            big.append(c)
    C = {}
    for c in big:
        C[c] = {k: ser(dm) for k, dm in cty[c].items()}
        for k, dm in cavg[c].items():
            C[c][k] = ser({m: sum(x) / len(x) for m, x in dm.items()})
    # the exchanges by the run's turnover: one that died in a revolution stays in the charts
    xs = sorted(xlast, key=lambda c: -xtot[c])
    X = {c: {k: ser(dm) for k, dm in xch[c].items()} for c in xs[:8]}
    for c in xs:
        xlast[c]['_total'] = xtot[c]
    # the speed: real seconds a game month, a quarter at a time (ld_speed: the real time [HH:MM:SS] of the debug lines
    # with a game date); the user's pauses at the PC count too
    S['spd'] = []
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from datetime import date
        import ld_speed
        pts = sorted(ld_speed.points(run))
        g_lim = date(lim[0], lim[1], 28).toordinal()
        pts = [x for x in pts if x[0] <= g_lim and x[0] >= date(1836, 2, 1).toordinal()]
        by_q = defaultdict(list)
        for g, sec in pts:
            d = date.fromordinal(g)
            by_q[(d.year, (d.month - 1) // 3)].append((g, sec))
        for (y, q), qp in sorted(by_q.items()):
            sl = ld_speed.slope(qp)
            if sl is not None and sl > 0:
                S['spd'].append([round(y + q / 4 + 0.125, 3), round(sl, 2)])
    except Exception as e:  # no debug logs here (the data built elsewhere) -- no speed
        S['spd_err'] = str(e)[:200]
    return dict(run=os.path.basename(os.path.normpath(run)), until=until, chk=chk, S=S, C=C, X=X, big=big,
                end={c: dict(allc[c], _gdp0=gdp0.get(c, 0)) for c in sorted(allc, key=lambda c: -gdp_end[c])},
                xend={c: xlast[c] for c in xs}, new=new, gone=gone, joined=joined, err=errors(run),
                leak=dict(sorted(leak.items(), key=lambda kv: -abs(kv[1].get('last', 0)))[:25]),
                rest={k: dict(sorted(v.items(), key=lambda kv: -abs(kv[1]))[:12]) for k, v in rest_cty.items()},
                rest_top={k: [(dt, c, round(v)) for _, dt, c, v in sorted(w, reverse=True)[:10]] for k, w in rest_week.items()},
                mkt=mkt_rows, mkt_world=mkt_world,
                gap=dict(sorted(gap_cty.items(), key=lambda kv: kv[1])[:12]),
                wjumps=[(dt, v, [(c, round(dw)) for _, c, dw in week_top.get(dt, [])])
                        for dt, v, _ in sorted(world_week, key=lambda x: -abs(x[1]))[:15]])


# ---------------------------------------------------------------------------------------------------------------------
def last_of(v):
    for x in reversed(v or []):
        if x is not None:
            return x
    return None


def first_of(v):
    for x in v or []:
        if x is not None:
            return x
    return None


def yearly(t, v, f='last'):
    out = {}
    for x, y in zip(t, v or []):
        if y is None:
            continue
        out.setdefault(int(x), []).append(y)
    return {y: (vs[-1] if f == 'last' else sum(vs) / len(vs) if f == 'avg' else sum(vs)) for y, vs in out.items()}


def summary(D):
    """The short summary: (state, title, text) -- state ok / warn / bad by fixed thresholds."""
    S, t = D['S'], D['S']['t']
    out = []
    m2 = last_of(S.get('w.m2'))
    oth = last_of(S.get('w.other'))
    if m2:
        sh = (oth or 0) / m2
        st = 'ok' if abs(sh) < 0.01 else 'warn' if abs(sh) < 0.03 else 'bad'
        out.append((st, '«Прочее» мира', f'{fmt(oth)} к концу — {sh * 100:.1f} % M2 (норма — меньше 1 %).'))
    for m, name, u in (('g', 'золото', GOLD_U), ('s', 'серебро', SILVER_U)):
        prod = S.get(f'm.prod_{m}')
        buy = S.get(f'm.last_buy_{m}')
        sell = S.get(f'm.last_sell_{m}')
        if prod and buy:
            mined = sum(x for x in prod if x) * 52 / 12
            got = ((last_of(buy) or 0) - (first_of(buy) or 0) - (last_of(sell) or 0) + (first_of(sell) or 0)) / u
            r = got / mined if mined else 0
            st = 'ok' if 0.8 <= r <= 1.15 else 'warn' if 0.6 <= r <= 1.4 else 'bad'
            out.append((st, f'Металл на счетах — {name}', f'пришло на счета {fmt(got)} товара, добыто {fmt(mined)} — '
                        f'{r:.2f} от добычи (норма — около 1).'))
    pm, sv, tg = last_of(S.get('a.popm')), last_of(S.get('a.savings')), last_of(S.get('a.target_money'))
    if pm and sv:
        sh = pm / (sv + pm)
        tsh = tg / (sv + pm) if tg else None
        st = 'ok' if tsh is not None and abs(sh - tsh) < 0.05 else 'warn'
        out.append((st, 'Кубышка населения', f'металл — {sh * 100:.0f} % всего, что держит население' +
                    (f', цель — {tsh * 100:.0f} %.' if tsh is not None else '.')))
    pool = last_of(S.get('a.pool')) or last_of(S.get('w.pool'))
    if pool and m2:
        sh = pool / m2
        out.append(('ok' if sh < 0.25 else 'warn' if sh < 0.5 else 'bad', 'Пул',
                    f'{fmt(pool)} — {sh * 100:.0f} % M2 (пул, который не тратится, копится).'))
    # the banks' capital from the end of the first year (the first months -- the start's setup)
    ky = yearly(t, S.get('w.bkcap'))
    k0, k1 = (ky[min(ky)], last_of(S.get('w.bkcap'))) if ky else (None, None)
    if k0 and k1:
        g = k1 / k0
        out.append(('ok' if g < 5 else 'warn', 'Капитал банков', f'{fmt(k0)} в конце первого года → {fmt(k1)}, ×{g:.1f}.'))
    debt, gdp = last_of(S.get('a.debt')), last_of(S.get('a.gdp'))
    if gdp:
        hi = [c for c, d in D['end'].items() if d.get('credit') and d.get('debt', 0) / d['credit'] > 0.5]
        bonds = last_of(S.get('a.bonds_abroad'))
        out.append(('ok' if len(hi) < 10 else 'warn', 'Госдолг',
                    f'мира {fmt(debt or 0)} — {100 * (debt or 0) / gdp:.0f} % ВВП' +
                    (f': долг движка {fmt(debt - bonds)}, облигации у держателей {fmt(bonds)} ({100 * bonds / debt:.0f} %)'
                     if bonds and debt else '') +
                    f'; больше половины предела у {len(hi)} стран.'))
    sp = S.get('spd') or []
    if sp:
        a0 = sum(v for _, v in sp[:4]) / len(sp[:4])
        a1 = sum(v for _, v in sp[-4:]) / len(sp[-4:])
        out.append(('ok' if a1 < 25 else 'warn', 'Скорость', f'{a0:.1f} с на игровой месяц в первый год, {a1:.1f} — в '
                    f'последний.'))
    fe = sum(n for f, n in D['err'] if os.path.basename(f).startswith('ld_'))
    out.append(('ok' if fe == 0 else 'bad', 'Ошибки по файлам форка', f'{fe} (файлы ld_*), всего с местом в скрипте — '
                f'{sum(n for _, n in D["err"])}.'))
    big_new = [c for c in D['new'] if D['end'].get(c, {}).get('gdp', 0) > 5e6]
    if big_new:
        out.append(('warn', 'Новые крупные страны', ', '.join(big_new) + ' (революции, распады, объединения).'))
    return out


def fmt(v):
    if v is None:
        return '—'
    a = abs(v)
    s = (f'{v / 1e9:.2f} млрд' if a >= 1e9 else f'{v / 1e6:.2f} млн' if a >= 1e6 else f'{v / 1e3:.0f} тыс.'
         if a >= 1e4 else f'{v:.0f}' if a >= 100 else f'{v:.2f}')
    return s.replace('.', ',')


OPS = [('o.countries', 'страны с моделью'), ('o.claims', 'записи требований'), ('o.banks', 'субъекты-банки'),
       ('o.orders', 'заявки бирж'), ('o.deals', 'сделки бирж'), ('o.assets', 'активы в стаканах'),
       ('o.clearing', 'страны в клиринге'), ('o.markets', 'рынки'), ('o.lines', 'строк лога')]


def ops_year(S):
    out = {}
    t = S['t']
    for k, name in OPS:
        out[k] = yearly(t, S.get(k), 'avg')
    return out


def ops_index(S):
    res = []
    for k, name in OPS:
        y = yearly(S['t'], S.get(k), 'avg')
        ys = sorted(y)
        if len(ys) < 2 or not y[ys[0]]:
            continue
        res.append([name, [[yy + 0.5, round(y[yy] / y[ys[0]], 3)] for yy in ys]])
    return res


def holders(S, t, m, scale):
    # the state's metal: the CB's reserves and the treasury's hoard (cb_* is both; tr_* -- the hoard, logged since R4б)
    def ser(k):
        return [[x, round(y * scale, 1)] for x, y in zip(t, S.get(k) or []) if y is not None]
    out = [['население', ser(f'm.pop_{m}')], ['банки', ser(f'm.bank_{m}')]]
    if S.get(f'm.tr_{m}'):
        cb = [[x, round((a - (b or 0)) * scale, 1)] for x, a, b in zip(t, S.get(f'm.cb_{m}') or [], S[f'm.tr_{m}']) if a is not None]
        out += [['ЦБ', cb], ['кубышка казны', ser(f'm.tr_{m}')]]
    else:
        out += [['ЦБ и кубышка казны (вместе в этом прогоне)', ser(f'm.cb_{m}')]]
    return out


def charts(D):
    S, C, X = D['S'], D['C'], D['X']
    t = S['t']

    def s(k, scale=1, nd=3, src=None):
        v = (src or S).get(k) or []
        return [[x, round(y * scale, nd)] for x, y in zip(t, v) if y is not None]

    def diff(k1, k2, scale=1, nd=3, src=None):
        a, b = (src or S).get(k1) or [], (src or S).get(k2) or []
        return [[x, round((y - (z or 0)) * scale, nd)] for x, y, z in zip(t, a, b + [None] * (len(a) - len(b))) if y is not None]

    def cum(v, scale=1, nd=3):
        # from the second month: the first is the start's setup (the CB's metal recount), not a leak
        out, acc = [], 0.0
        for x, y in zip(t, v or []):
            if y is None or x < t[0] + 0.08:
                continue
            acc += y
            out.append([x, round(acc * scale, nd)])
        return out

    def sm(k, n=3, nd=1):
        p = s(k, 1, 6)
        return [[p[i][0], round(sum(x[1] for x in p[max(0, i - n + 1):i + 1]) / len(p[max(0, i - n + 1):i + 1]), nd)]
                for i in range(len(p))]
    M = 1e-6
    big = D['big']
    ch = {
        'money': ('Денежная масса мира, млн', 'млн', [['M0', s('w.m0', M)], ['M2', s('w.m2', M)], ['M3', s('w.m3', M)]]),
        'acc': ('Счета мира, млн', 'млн', [['пул', s('w.pool', M)], ['кредиты банков', s('w.loans', M)],
                                          ['вклады', s('w.deposits', M)], ['капитал банков', s('w.bkcap', M)],
                                          ['казна', s('w.treasury', M)]]),
        'price': ('Индекс цен крупных стран', '', [[c, s('price', 1, 1, C[c])] for c in big[:8]]),
        'other': ('«Прочее» мира нарастающим итогом, млн', 'млн', [['всего', s('w.other', M)],
                                                                  ['в т. ч. казна', s('w.other_tr', M)]]),
        'rests': ('Необъяснённые остатки счетов мира нарастающим итогом, млн (должны быть около 0)', 'млн',
                  [[name, cum(S.get('r.' + k), M)] for k, name in REST_KEYS.items() if S.get('r.' + k)] +
                  [['«прочее» (пул + казна)', s('w.other', M)]]),
        'gap': ('Движок: разрыв рынка — статья кассы предприятий (страны с логами) и разрыв рынков движка, нарастающим итогом, млн',
                'млн', [['статья «движок: разрыв рынка»', cum(S.get('r.eng_gap'), M)]] +
                ([['разрыв рынков движка (рынки стран с логами)', cum(S.get('r.mkt_gap'), M)]] if S.get('r.mkt_gap') else []) +
                [[name, cum(S.get('r.gap_' + g), M)] for g, name in (('fin', 'в т. ч. финансовые товары'),
                                                                     ('psc', 'в т. ч. стройматериалы PSC'),
                                                                     ('metal', 'в т. ч. металл')) if S.get('r.gap_' + g)]),
        'mrest': ('Остаток металла мира: счета − старт − куплено + продано (должен быть 0), тыс. товара', 'тыс.',
                  [['золото', s('m.rest_g', 1e-5, 2)], ['серебро', s('m.rest_s', 1 / 775e3, 2)]]),
        'lvlst': ('Вынесено из «прочего» как выкуп уровней, млн', 'млн', [['пул', s('l.lvl_pool', M)],
                                                                         ['казна', s('l.lvl_tr', M)]]),
        'gold': ('Золото в неделю, товар', 'товар/нед', [['добыто', s('m.prod_g', 1, 1)],
                                                         ['пришло на счета (3 мес.)', sm('m.buyw_g')],
                                                         ['заказы рынков', s('m.buyo_g', 1, 1)],
                                                         ['продажи рынков', s('m.sello_g', 1, 1)],
                                                         ['ушло со счетов (3 мес.)', sm('m.sellw_g')]]),
        'silver': ('Серебро в неделю, товар', 'товар/нед', [['добыто', s('m.prod_s', 1, 0)],
                                                            ['пришло на счета (3 мес.)', sm('m.buyw_s', 3, 0)],
                                                            ['заказы рынков', s('m.buyo_s', 1, 0)],
                                                            ['продажи рынков', s('m.sello_s', 1, 0)],
                                                            ['ушло со счетов (3 мес.)', sm('m.sellw_s', 3, 0)]]),
        'mgold': ('Золото на счетах, тыс. товара', 'тыс.', holders(S, t, 'g', 1e-5)),
        'msilver': ('Серебро на счетах, тыс. товара', 'тыс.', holders(S, t, 's', 1 / 775e3)),
        'fill': ('Доля заказов металла, которую рынки исполнили', '', [['золото', s('k.fill_g', 1, 3)],
                                                                      ['серебро', s('k.fill_s', 1, 3)]]),
        'smetal': ('Металл мира по держателям, млн (в деньгах стран)', 'млн', [['ЦБ', s('a.cbm', M)], ['кубышки казны', s('a.trm', M)],
                                                                           ['банки', s('a.bankm', M)], ['население', s('a.popm', M)]]),
        'hoard': ('Кубышка населения мира: металл и цель, млн', 'млн', [['металл населения', s('a.popm', M)],
                                                                        ['цель', s('a.target_money', M)],
                                                                        ['сдано в ЦБ за месяц', s('a.popm_cb', M * 4.3)],
                                                                        ['сдано в банки за месяц', s('a.popm_bank', M * 4.3)]]),
        'pool': ('Пул мира и пул крупных стран, млн', 'млн', [['мир', s('a.pool', M)]] +
                 [[c, s('pool', M, 3, C[c])] for c in big[:6]]),
        'debt': ('Госдолг мира, млн', 'млн', [['долг движка (без облигаций)', diff('a.debt', 'a.bonds_abroad', M)],
                                              ['облигации у держателей', s('a.bonds_abroad', M)],
                                              ['весь долг', s('a.debt', M)], ['предел кредита', s('a.credit', M)]]),
        'soc': ('Доля радикалов', '', [[c, s('radical', 1, 3, C[c])] for c in big[:8]]),
        'sol': ('Средний уровень жизни', '', [[c, s('sol', 1, 1, C[c])] for c in big[:8]]),
        'psc': ('Очки стройки в неделю', 'очков', [[c, s('psc_pts', 1, 1, C[c])] for c in big[:8]]),
        'xto': ('Оборот бирж за месяц, тыс. в золоте', 'тыс.', [[c, s('to_g', 1e-3, 1, X[c])] for c in list(X)[:8]]),
        'xheat': ('Перегрев бирж', '×', [[c, s('heat', 1, 3, X[c])] for c in list(X)[:6]]),
        'xmem': ('Участники бирж (страны, торгующие на бирже)', 'стран', [[c, s('members', 1, 0, X[c])] for c in list(X)[:8]]),
        'ops': ('Нагрузка механик по годам: во сколько раз больше, чем в первый год', '×', ops_index(S)),
        'spd': ('Скорость: секунд реального времени на игровой месяц, по кварталам', 'с', [['прогон', S.get('spd') or []]]),
        'bk': ('Банки мира, млн', 'млн', [['капитал', s('w.bkcap', M)], ['кредиты', s('w.loans', M)],
                                         ['вклады', s('w.deposits', M)]]),
    }
    B = {}
    for c in big:
        cc = C[c]
        B[c] = dict(budget=[['доходы', s('inc', 1e-3, 1, cc)], ['расходы', s('exp', 1e-3, 1, cc)],
                            ['фикс. расходы', s('fix_exp', 1e-3, 1, cc)], ['армия', s('mil', 1e-3, 1, cc)],
                            ['пул на стройку', s('pool_constr', 1e-3, 1, cc)]],
                    debt=[['долг движка (без облигаций)', diff('debt', 'bonds_abroad', M, 2, cc)],
                          ['облигации у держателей', s('bonds_abroad', M, 2, cc)], ['весь долг', s('debt', M, 2, cc)],
                          ['предел кредита', s('credit', M, 2, cc)], ['казна', s('treasury', M, 2, cc)]],
                    metal=[['металл ЦБ', s('cbm', M, 2, cc)], ['кубышка казны', s('trm', M, 2, cc)],
                           ['металл банков', s('bankm', M, 2, cc)], ['металл населения', s('popm', M, 2, cc)]],
                    hoard=[['доля металла', s('popm_share', 1, 3, cc)], ['цель', s('popm_target', 1, 3, cc)],
                           ['радикалы', s('radical', 1, 3, cc)], ['лоялисты', s('loyalist', 1, 3, cc)]])
    return {k: dict(title=v[0], unit=v[1], series=v[2]) for k, v in ch.items()}, B


SECTIONS = [
    ('Деньги', 'Денежная масса и счета мира — сумма по всем странам. M0 — наличные, M2 — с вкладами. Ровный рост с '
     'экономикой — норма; провалы — революции и исчезнувшие страны. Индекс цен: 100 — базовые цены игры; первые годы '
     'цены сходятся к равновесию.', ['money', 'acc', 'price']),
    ('«Прочее» и выкуп уровней', '«Прочее» — движение денег, которое сверка не объяснила проводками; естественный '
     'прирост — ноль. Выкуп уровней — недельные изменения пула, кратные цене уровня (25 000), которые сверка вынесла '
     'из «прочего»: если они не совпадают с изменением уровней государства, это не выкуп.', ['other', 'lvlst']),
    ('Утечки', 'Где течёт. Металл: остаток мира — счета минус старт, плюс проданное, минус купленное; 0 — металл не '
     'появляется и не исчезает. Деньги: «прочее» по странам (только страны, которые пишут строку сверки: игрок, крупные и '
     'любая страна с большим «прочим» недели) — сколько к концу, сколько сразу при первой строке (рождение страны, '
     'революция), самая большая неделя; ниже — недели с самым большим «прочим» мира и чьё оно. Остатки счетов — '
     'изменение каждого счёта подсказки денег минус все известные статьи за неделю: касса предприятий, банки и пул, '
     'заграница, казна, ЦБ, наличные и вклады населения (только страны, которые пишут эти строки: игрок и крупные); любой '
     'устойчивый рост — утечка, её счёт и страна — в таблицах. Деньги, которые движок теряет в частном секторе (разрыв '
     'рынка, неистраченный доход населения), — статья кассы предприятий, не утечка: её график и таблица — рядом с '
     'разрывом рынков движка.', ['rests', 'mrest', 'gap']),
    ('Металл', 'Металл на счетах должен расти вровень с добычей: на счета записывается только то, что рынок продал '
     '(заказы × доля исполнения). «Пришло на счета» выше «добыто» долго — металл берётся из ниоткуда. Доля исполнения '
     '1 — рынки продали весь заказ, ниже — нехватка.', ['gold', 'silver', 'mgold', 'msilver', 'fill']),
    ('Кубышка населения', 'Население держит в металле целевую долю всего, чем владеет: больше при радикалах, меньше '
     'при лоялистах. Сверх цели сдаёт излишек в ЦБ (металлический стандарт) или в банки вкладом. Металл населения '
     'должен держаться около цели, а не расти без конца. Ниже — металл по держателям в деньгах стран: ЦБ, кубышки '
     'казны, банки, население (с прогонов, где кубышка казны пишется отдельно).', ['hoard', 'smetal']),
    ('Пул', 'Инвестиционный пул — деньги частного сектора на стройку. Если пул растёт, а стройка нет, деньги лежат без '
     'дела. Таблица внизу — крупнейшие пулы к концу прогона.', ['pool']),
    ('Бюджет и долг', 'Бюджет недели по движку и долг выбранной страны; ниже — кубышка населения той же страны и её '
     'радикалы. Долг мира — сумма по всем странам. Облигации у держателей — часть долга, которую держат банки, '
     'население, казны и ЦБ других стран облигациями (реестр требований); остальное — долг движка без облигаций.', ['debt']),
    ('Люди', 'Радикалы и уровень жизни крупных стран. Рост радикалов и падение уровня жизни ведут к революциям; '
     'новые страны в списке «Проверки» — признак революций и распадов.', ['soc', 'sol']),
    ('Стройка', 'Очки стройки в неделю (PSC), среднее за месяц.', ['psc']),
    ('Биржи', 'Биржи выбраны по обороту за весь прогон: биржа, исчезнувшая в революции, остаётся на графиках. Оборот '
     'за месяц в золоте, участники — страны, торгующие на бирже, перегрев — рыночная цена требований к их стоимости '
     'без спроса (1 — равно, ниже — дешевле).', ['xto', 'xmem', 'xheat']),
    ('Банки', 'Капитал, кредиты и вклады банков мира; таблица банкротств — внизу.', ['bk']),
    ('Нагрузка механик', 'Сколько работы делает каждая механика за год, во сколько раз больше первого года: страны с '
     'моделью, записи в словаре требований, субъекты-банки, заявки, сделки и активы бирж, страны в клиринге, рынки, '
     'строки лога. Это не время, а объём работы: если скорость падает вместе с ростом одной из линий, её механика и '
     'дорожает. Числа по годам — таблица ниже.', ['ops']),
    ('Скорость', 'Секунды реального времени на игровой месяц (по строкам debug.log с реальным временем и игровой датой). '
     'Рост со временем — игра дорожает: больше стран, зданий, требований. Паузы пользователя за ПК тоже попадают сюда. '
     'Что именно ест время по механикам, показывает только профилировщик (навык vic3-sandbox, «Профилировщик») — '
     'отдельным прогоном.', ['spd']),
]

CSS = """:root{--bg:#fcfcfb;--fg:#0b0b0b;--mut:#52514e;--rule:#e2e1dc;--grid:#ecebe6;--chip:#f1f0ec;
--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--s5:#e87ba4;--s6:#008300;--s7:#6250d6;--s8:#e34948;--ok:#1a7f4b;--warn:#a16207;--bad:#c2410c;
--disp:"PT Serif",Georgia,serif;--body:"PT Sans","Segoe UI",sans-serif;--mono:"PT Mono",ui-monospace,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#1a1a19;--fg:#f0efec;--mut:#c3c2b7;--rule:#34332f;--grid:#2a2a27;--chip:#262624;
--s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--s5:#d55181;--s6:#2f9e2f;--s7:#9085e9;--s8:#e66767;--ok:#3fbf7f;--warn:#e0b341;--bad:#f0844f;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#1a1a19;--fg:#f0efec;--mut:#c3c2b7;--rule:#34332f;--grid:#2a2a27;--chip:#262624;
--s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--s5:#d55181;--s6:#2f9e2f;--s7:#9085e9;--s8:#e66767;--ok:#3fbf7f;--warn:#e0b341;--bad:#f0844f;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font:16px/1.55 var(--body);margin:0}
main{max-width:900px;margin:0 auto;padding-inline:16px;padding-block:32px 64px}
h1{font:700 2rem/1.15 var(--disp);margin:0 0 .3rem;text-wrap:balance}h2{font:700 1.25rem var(--disp);margin:2.6rem 0 .4rem}
h3{font:700 1rem var(--disp);margin:1.4rem 0 .2rem}p{max-width:68ch}.sub{color:var(--mut);margin:0}
.chart{position:relative;margin:.4rem 0 0}.chart svg{width:100%;height:auto;display:block;overflow:visible}
.ct{font:700 .92rem var(--body);margin:1.2rem 0 0}.ax{fill:var(--mut);font:11px var(--mono)}.gl{stroke:var(--grid)}.zl{stroke:var(--mut)}
.cut{stroke:var(--mut);stroke-dasharray:3 4}.ln{fill:none;stroke-width:2;stroke-linejoin:round}
.leg{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:.86rem;color:var(--mut);margin:.3rem 0 0}
.leg i{display:inline-block;width:14px;height:3px;border-radius:2px;vertical-align:middle;margin-right:6px}
.tip{position:absolute;pointer-events:none;background:var(--bg);border:1px solid var(--rule);border-radius:4px;padding:6px 8px;font:12px/1.4 var(--mono);color:var(--fg);box-shadow:0 2px 8px rgba(0,0,0,.12);white-space:nowrap;z-index:2}
.find{border-left:3px solid var(--mut);padding:.1rem 0 .1rem 12px;margin:.7rem 0}.find b{font-family:var(--disp)}
.f-ok{border-left-color:var(--ok)}.f-warn{border-left-color:var(--warn)}.f-bad{border-left-color:var(--bad)}
table{border-collapse:collapse;font-size:.88rem;width:100%}th,td{padding:5px 8px;border-bottom:1px solid var(--rule);text-align:left;vertical-align:top}
th{font-size:.72rem;text-transform:uppercase;letter-spacing:.06em;color:var(--mut)}td.n{font-family:var(--mono);text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.tw{overflow-x:auto}.sel{display:flex;flex-wrap:wrap;gap:6px;margin:.6rem 0}
.sel button{font:13px var(--body);color:var(--fg);background:var(--chip);border:1px solid var(--rule);border-radius:999px;padding:4px 12px;cursor:pointer}
.sel button[aria-pressed="true"]{background:var(--fg);color:var(--bg);border-color:var(--fg)}.sel button:focus-visible{outline:2px solid var(--s1);outline-offset:2px}
code{font:.88em var(--mono)}"""

JS = r"""
const X0=Math.floor(DATA.t0), X1=Math.ceil(DATA.t1);
const cols=['--s1','--s2','--s3','--s4','--s5','--s6','--s7','--s8'];
function fx(v){const a=Math.abs(v);if(a<1e-9)return '0';return (a>=100?v.toFixed(0):a>=10?v.toFixed(1):a>=1?v.toFixed(2):v.toFixed(3)).replace('.',',')}
function fm(v){if(v==null)return '—';const a=Math.abs(v);return (a>=1e9?(v/1e9).toFixed(2)+' млрд':a>=1e6?(v/1e6).toFixed(2)+' млн':a>=1e4?(v/1e3).toFixed(0)+' тыс.':a>=100?v.toFixed(0):v.toFixed(2)).replace('.',',')}
function nice(lo,hi){const span=hi-lo||1;const step=Math.pow(10,Math.floor(Math.log10(span/4)));const m=[1,2,2.5,5,10].find(k=>span/(k*step)<=6)*step;return {lo:Math.floor(lo/m)*m,hi:Math.ceil(hi/m)*m,step:m}}
function draw(id,cfg){const el=document.getElementById('c_'+id);if(!el)return;
 const ser=cfg.series.filter(s=>s[1].length);const W=860,H=270,L=60,R=12,T=12,B=28;
 let lo=Infinity,hi=-Infinity;ser.forEach(s=>s[1].forEach(p=>{lo=Math.min(lo,p[1]);hi=Math.max(hi,p[1])}));
 if(!isFinite(lo)){el.innerHTML='<p class="sub">нет данных в этом прогоне</p>';return}
 if(cfg.unit!=='×'&&cfg.unit!==''){if(lo>0)lo=0;if(hi<0)hi=0}const n=nice(lo,hi);
 const X=t=>L+(t-X0)/(X1-X0)*(W-L-R),Y=v=>T+(n.hi-v)/(n.hi-n.lo)*(H-T-B);
 let s=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${cfg.title}">`;
 for(let v=n.lo;v<=n.hi+1e-9;v+=n.step)s+=`<line x1="${L}" x2="${W-R}" y1="${Y(v)}" y2="${Y(v)}" class="${Math.abs(v)<1e-9?'zl':'gl'}"/><text x="${L-6}" y="${Y(v)+4}" class="ax" text-anchor="end">${fx(v)}</text>`;
 const st=X1-X0>8?2:1;for(let y=X0;y<=X1;y+=st)s+=`<text x="${X(y)}" y="${H-8}" class="ax" text-anchor="middle">${y}</text>`;
 if(cfg.unit==='×')s+=`<line x1="${L}" x2="${W-R}" y1="${Y(1)}" y2="${Y(1)}" class="cut"/>`;
 ser.forEach(sr=>{const c=`var(${cols[cfg.series.indexOf(sr)%8]})`;const pts=sr[1];let st=1;for(let i=1;i<pts.length;i++)st=Math.min(st,pts[i][0]-pts[i-1][0]);sr.step=st;
  let d='',prev=null;pts.forEach(p=>{d+=(prev!==null&&p[0]-prev<st*2.5?' L':' M')+X(p[0]).toFixed(1)+','+Y(p[1]).toFixed(1);prev=p[0]});s+=`<path class="ln" stroke="${c}" d="${d}"/>`;
  if(pts.length<60)pts.forEach(p=>{s+=`<circle cx="${X(p[0]).toFixed(1)}" cy="${Y(p[1]).toFixed(1)}" r="3.5" fill="${c}" stroke="var(--bg)" stroke-width="1.5"/>`})});
 s+=`<line class="xl cut" y1="${T}" y2="${H-B}" x1="-10" x2="-10" style="stroke-dasharray:none;opacity:.5"/></svg>`;
 el.innerHTML=s+'<div class="leg">'+ser.map(x=>`<span><i style="background:var(${cols[cfg.series.indexOf(x)%8]})"></i>${x[0]}</span>`).join('')+'</div>';
 const svg=el.querySelector('svg'),tip=document.createElement('div');tip.className='tip';tip.hidden=true;el.appendChild(tip);
 svg.addEventListener('mousemove',e=>{const r=svg.getBoundingClientRect();const t=X0+((e.clientX-r.left)/r.width*W-L)/(W-L-R)*(X1-X0);if(t<X0||t>X1){tip.hidden=true;return}
  const xl=svg.querySelector('.xl');const rows=ser.map(sr=>{const p=sr[1].reduce((a,b)=>Math.abs(b[0]-t)<Math.abs(a[0]-t)?b:a);if(Math.abs(p[0]-t)>Math.max(0.1,(sr.step||0)*0.6))return'';return `<span style="color:var(${cols[cfg.series.indexOf(sr)%8]})">■</span> ${sr[0]}: ${fx(p[1])}`}).filter(Boolean);
  xl.setAttribute('x1',X(t));xl.setAttribute('x2',X(t));if(!rows.length){tip.hidden=true;return}
  const yr=Math.floor(t),mo=Math.floor((t-yr)*12)+1;tip.innerHTML=`${String(mo).padStart(2,'0')}.${yr}`+(cfg.unit?` · ${cfg.unit}`:'')+'<br>'+rows.join('<br>');tip.hidden=false;
  tip.style.left=Math.max(0,Math.min(e.clientX-r.left+12,r.width-tip.offsetWidth-4))+'px';tip.style.top='8px'});
 svg.addEventListener('mouseleave',()=>{tip.hidden=true})}
Object.keys(DATA.ch).forEach(k=>draw(k,DATA.ch[k]));
const bsel=document.getElementById('bsel');
function showB(c){[...bsel.children].forEach(b=>b.setAttribute('aria-pressed',b.textContent===c));const b=DATA.B[c];
 draw('cb',{title:'Бюджет '+c,unit:'тыс.',series:b.budget});draw('cd',{title:'Долг '+c,unit:'млн',series:b.debt});draw('ch',{title:'Кубышка '+c,unit:'',series:b.hoard});if(b.metal)draw('cm',{title:'Металл '+c,unit:'млн',series:b.metal})}
Object.keys(DATA.B).forEach(c=>{const b=document.createElement('button');b.type='button';b.textContent=c;b.addEventListener('click',()=>showB(c));bsel.appendChild(b)});
if(Object.keys(DATA.B).length)showB(Object.keys(DATA.B)[0]);
"""


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def render(D, out, base=None, title=None):
    ch, B = charts(D)
    S = D['S']
    t = S['t']
    chk = D['chk']
    title = title or f'Прогон {D["run"]}'
    h = [f'<title>{esc(title)}</title>',
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=PT+Serif:wght@400;700&family=PT+Sans:wght@400;700&family=PT+Mono&display=swap">',
         f'<style>{CSS}</style><main>', f'<h1>{esc(title)}</h1>',
         f'<p class="sub">Отчёт по логам модели прогона <code>{esc(D["run"])}</code>: {esc(chk["lines"])} строк, до '
         f'{esc(chk["last"])}. Страница одинакова для всех прогонов (<code>tools/ld_run_report.py</code>); пояснения в '
         f'начале разделов — что показано и какая норма.</p>', '<h2>Коротко</h2>']
    for st, name, text in summary(D):
        h.append(f'<div class="find f-{st}"><b>{esc(name)}.</b> {esc(text)}</div>')
    h.append('<h2>Проверки</h2><div class="tw"><table><thead><tr><th>Что</th><th>Итог</th></tr></thead><tbody>')
    rows = [('Строк лога', f'{chk["lines"]}, последняя дата {chk["last"]}'),
            ('Расхождение металла ЦБ (EFQ)', f'{chk["efq"]} строк'),
            ('Суммы банков = счета страны', f'max |diff| {chk["diff"]:.2f}'),
            ('Карты требований банков', f'max |map_diff| {chk["mdiff"]:.2f}' + (f' ({chk["mdiff_at"]})' if chk['mdiff_at'] else '')),
            ('Банкротства банков', str(len(chk['fails']))),
            ('Новые страны за прогон', ', '.join(D['new'][:20]) or '—'),
            ('Исчезли за прогон', ', '.join(D['gone'][:20]) or '—'),
            ('Месяцы с потерянными строками лога (их суммы по странам не показаны)', ', '.join(chk.get('lost') or []) or '—'),
            ('Объединено (революции: статистика новой страны — к стартовой)',
             '; '.join(f'{a} → {b}' for a, b in (D.get('joined') or {}).items()) or '—')]
    for a, b in rows:
        h.append(f'<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>')
    h.append('</tbody></table></div><h3>Ошибки скрипта по файлам</h3>')
    if D['err']:
        h.append('<div class="tw"><table><thead><tr><th>Файл</th><th class="n">Ошибок</th></tr></thead><tbody>')
        for f, n in D['err'][:15]:
            h.append(f'<tr><td><code>{esc(f)}</code></td><td class="n">{n}</td></tr>')
        h.append('</tbody></table></div>')
    else:
        h.append('<p class="sub">ошибок с местом в скрипте нет</p>')
    for name, intro, ids in SECTIONS:
        h.append(f'<h2>{esc(name)}</h2><p>{esc(intro)}</p>')
        if name == 'Бюджет и долг':
            h.append('<div class="sel" id="bsel" role="group" aria-label="Страна"></div>'
                     '<div class="ct">Бюджет недели, тыс.</div><div class="chart" id="c_cb"></div>'
                     '<div class="ct">Долг движка и облигации, весь долг, предел кредита и казна, млн</div><div class="chart" id="c_cd"></div>'
                     '<div class="ct">Металл страны по держателям, млн (в деньгах страны)</div><div class="chart" id="c_cm"></div>'
                     '<div class="ct">Кубышка населения: доля металла, цель, радикалы, лоялисты</div><div class="chart" id="c_ch"></div>')
        for i in ids:
            h.append(f'<div class="ct">{esc(ch[i]["title"])}</div><div class="chart" id="c_{i}"></div>')
        if name == 'Утечки':
            h.append('<p class="sub">Первый месяц игры не считается — ни в графиках, ни в таблицах остатков: в нём стартовая '
                     'настройка счетов (металл ЦБ — 40 % M2), это не утечка.</p>')
            h.append('<h3>«Прочее» по странам</h3><div class="tw"><table><thead><tr><th>Страна</th><th class="n">К концу</th>'
                     '<th class="n">При первой строке</th><th>Первая строка</th><th class="n">Пул</th><th class="n">Казна</th>'
                     '<th class="n">Самая большая неделя</th><th>Когда</th></tr></thead><tbody>')
            for c, d in (D.get('leak') or {}).items():
                h.append(f'<tr><td>{esc(c)}</td><td class="n">{fmt(d.get("last"))}</td><td class="n">{fmt(d.get("first"))}</td>'
                         f'<td>{esc(d.get("first_at", ""))}</td><td class="n">{fmt(d.get("other_pool"))}</td>'
                         f'<td class="n">{fmt(d.get("other_tr"))}</td><td class="n">{fmt(d.get("jump"))}</td>'
                         f'<td>{esc(d.get("jump_at", ""))}</td></tr>')
            h.append('</tbody></table></div>')
            for k, name in REST_KEYS.items():
                rc = (D.get('rest') or {}).get(k)
                if not rc:
                    continue
                h.append(f'<h3>Остаток «{esc(name)}»: страны за весь прогон и самые большие недели</h3><div class="tw"><table>'
                         '<thead><tr><th>Страна</th><th class="n">Сумма остатков</th></tr></thead><tbody>')
                for c, v in list(rc.items())[:8]:
                    h.append(f'<tr><td>{esc(c)}</td><td class="n">{fmt(v)}</td></tr>')
                h.append('</tbody></table></div><div class="tw"><table><thead><tr><th>Неделя</th><th>Страна</th>'
                         '<th class="n">Остаток</th></tr></thead><tbody>')
                for dt, c, v in (D.get('rest_top') or {}).get(k, [])[:6]:
                    h.append(f'<tr><td>{esc(dt)}</td><td>{esc(c)}</td><td class="n">{fmt(v)}</td></tr>')
                h.append('</tbody></table></div>')
            if D.get('gap'):
                h.append('<h3>Статья «движок: разрыв рынка» по странам за прогон</h3><div class="tw"><table><thead><tr>'
                         '<th>Страна</th><th class="n">Статья</th></tr></thead><tbody>')
                for c, v in D['gap'].items():
                    h.append(f'<tr><td>{esc(c)}</td><td class="n">{fmt(v)}</td></tr>')
                h.append('</tbody></table></div>')
            if D.get('mkt'):
                allm = D.get('mkt_world') is not None
                h.append('<h3>Статья «движок: разрыв рынка» против разрыва рынка движка</h3><p class="sub">Разрыв рынка — Σ по товарам '
                         '(продано − заказано) × цена; по группам товаров мода — финансовые (облигации, акции, валюты), '
                         'стройматериалы PSC, металл, остальное — ванильные. Статья — '
                         + ('все страны рынка (с февраля 1836). ' if allm else 'только страны с логами (ВВП больше 20 млн). ')
                         + 'Доля около 1 — разрыв уничтожает деньги один к одному, около 0 — не уничтожает.</p>'
                         '<div class="tw"><table><thead><tr><th>Рынок</th><th class="n">Стран</th><th class="n">Статья стран рынка</th>'
                         '<th class="n">Разрыв рынка</th><th class="n">Доля</th><th class="n">Финансовые</th>'
                         '<th class="n">PSC</th><th class="n">Металл</th></tr></thead><tbody>')
                for row in D['mkt']:
                    m, n, b, g, gr = row if len(row) == 5 else (row[0], 0, row[1], row[2], {})
                    h.append(f'<tr><td>{esc(m)}</td><td class="n">{n or "—"}</td><td class="n">{fmt(b)}</td><td class="n">{fmt(g)}</td>'
                             f'<td class="n">{b / g if g else 0:.2f}</td><td class="n">{fmt(gr.get("fin", 0))}</td>'
                             f'<td class="n">{fmt(gr.get("psc", 0))}</td><td class="n">{fmt(gr.get("metal", 0))}</td></tr>')
                if allm:
                    b, g = D['mkt_world']
                    h.append(f'<tr><td><b>мир</b></td><td></td><td class="n">{fmt(b)}</td><td class="n">{fmt(g)}</td>'
                             f'<td class="n">{b / g if g else 0:.2f}</td><td></td><td></td><td></td></tr>')
                h.append('</tbody></table></div>')
            h.append('<h3>Недели с самым большим «прочим» мира</h3><div class="tw"><table><thead><tr>'
                     '<th>Неделя</th><th class="n">«Прочее» мира</th><th>Чьё (страна: за неделю)</th></tr></thead><tbody>')
            for dt, v, top in D.get('wjumps') or []:
                who = '; '.join(f'{c}: {fmt(x)}' for c, x in top) or '—'
                h.append(f'<tr><td>{esc(dt)}</td><td class="n">{fmt(v)}</td><td>{esc(who)}</td></tr>')
            h.append('</tbody></table></div>')
        if name == 'Пул':
            h.append('<h3>Крупнейшие пулы к концу</h3><div class="tw"><table><thead><tr><th>Страна</th><th class="n">Пул</th>'
                     '<th class="n">ВВП</th><th class="n">Пул / ВВП</th><th class="n">На стройку / нед</th></tr></thead><tbody>')
            for c, d in sorted(D['end'].items(), key=lambda kv: -kv[1].get('pool', 0))[:15]:
                h.append(f'<tr><td>{esc(c)}</td><td class="n">{fmt(d.get("pool"))}</td><td class="n">{fmt(d.get("gdp"))}</td>'
                         f'<td class="n">{(d.get("pool", 0) / d["gdp"] if d.get("gdp") else 0):.2f}</td>'
                         f'<td class="n">{fmt(d.get("pool_constr"))}</td></tr>')
            h.append('</tbody></table></div>')
        if name == 'Бюджет и долг':
            h.append('<h3>Долг к концу: страны больше половины предела</h3><div class="tw"><table><thead><tr><th>Страна</th>'
                     '<th class="n">Весь долг</th><th class="n">Долг движка</th><th class="n">Облигации</th><th class="n">Предел</th><th class="n">Долг / ВВП</th><th class="n">Доходы / нед</th>'
                     '<th class="n">Расходы / нед</th></tr></thead><tbody>')
            hi = [(c, d) for c, d in D['end'].items() if d.get('credit') and d.get('debt', 0) / d['credit'] > 0.5]
            for c, d in sorted(hi, key=lambda kv: -kv[1].get('debt', 0))[:20]:
                h.append(f'<tr><td>{esc(c)}</td><td class="n">{fmt(d.get("debt"))}</td><td class="n">{fmt(d.get("debt", 0) - d.get("bonds_abroad", 0))}</td><td class="n">{fmt(d.get("bonds_abroad"))}</td><td class="n">{fmt(d.get("credit"))}</td>'
                         f'<td class="n">{(d.get("debt", 0) / d["gdp"] if d.get("gdp") else 0):.2f}</td>'
                         f'<td class="n">{fmt(d.get("inc"))}</td><td class="n">{fmt(d.get("exp"))}</td></tr>')
            if not hi:
                h.append('<tr><td colspan="8">нет</td></tr>')
            h.append('</tbody></table></div>')
        if name == 'Нагрузка механик':
            oy = ops_year(S)
            yrs = sorted({y for v in oy.values() for y in v})
            h.append('<div class="tw"><table><thead><tr><th>Год</th>' + ''.join(f'<th class="n">{esc(n)}</th>' for _, n in OPS)
                     + '</tr></thead><tbody>')
            for y in yrs:
                h.append(f'<tr><td>{y}</td>' + ''.join(f'<td class="n">{fmt(oy[k].get(y))}</td>' for k, _ in OPS) + '</tr>')
            h.append('</tbody></table></div><p class="sub">Среднее за месяц; строки лога — за месяц.</p>')
        if name == 'Биржи':
            h.append('<h3>Биржи по обороту за весь прогон (в золоте; остальное — последний месяц биржи)</h3><div class="tw"><table><thead><tr><th>Биржа</th>'
                     '<th class="n">Оборот за прогон</th><th class="n">За последний год</th><th>Последний месяц</th>'
                     '<th class="n">Капитализация</th><th class="n">Перегрев</th>'
                     '<th class="n">Участники</th><th class="n">Из-за границы</th><th class="n">Купили ЦБ / банки / население / казна</th>'
                     '<th class="n">Продали ЦБ / банки / население / казна</th></tr></thead><tbody>')
            for c, d in list(D['xend'].items())[:15]:
                bs = ' / '.join(fmt(d.get(f'b_{k}_g', 0)) for k in ('cb', 'bk', 'pp', 'tr'))
                ss = ' / '.join(fmt(d.get(f's_{k}_g', 0)) for k in ('cb', 'bk', 'pp', 'tr'))
                h.append(f'<tr><td>{esc(c)}</td><td class="n">{fmt(d.get("_total"))}</td><td class="n">{fmt(d.get("year_to_g"))}</td>'
                         f'<td>{esc(d.get("_date", ""))}</td><td class="n">{fmt(d.get("cap_g"))}</td>'
                         f'<td class="n">{d.get("heat", 0):.2f}</td><td class="n">{d.get("members", 0):.0f}</td>'
                         f'<td class="n">{100 * d.get("foreign", 0):.0f} %</td><td class="n">{bs}</td><td class="n">{ss}</td></tr>')
            h.append('</tbody></table></div>')
        if name == 'Банки':
            h.append('<h3>Банкротства</h3><div class="tw"><table><thead><tr><th>Дата</th><th>Страна</th><th>Банк</th>'
                     '<th>Подробно</th></tr></thead><tbody>')
            for f in chk['fails'][:30]:
                h.append(f'<tr><td>{esc(f[0])}</td><td>{esc(f[1])}</td><td>{esc(f[3] if len(f) > 3 else "")}</td>'
                         f'<td><code>{esc(" · ".join(f[4:]))}</code></td></tr>')
            if not chk['fails']:
                h.append('<tr><td colspan="4">нет</td></tr>')
            h.append('</tbody></table></div>')
    # by year: this run (and the base)
    h.append('<h2>По годам</h2><p>Конец каждого года. С базой — второе число в ячейке.</p><div class="tw"><table><thead><tr><th>Год</th>')
    cols = [('M2', 'w.m2', 'last'), ('«Прочее»', 'w.other', 'last'), ('Пул', 'a.pool', 'last'),
            ('Металл населения', 'a.popm', 'last'), ('Капитал банков', 'w.bkcap', 'last'), ('Весь долг мира', 'a.debt', 'last'),
            ('из него облигации', 'a.bonds_abroad', 'last')]
    ys = {k: yearly(t, S.get(k), f) for _, k, f in cols}
    yb = {k: yearly(base['S']['t'], base['S'].get(k), f) for _, k, f in cols} if base else {}
    def spd_year(SS):
        out = {}
        for x, v in SS.get('spd') or []:
            out.setdefault(int(x), []).append(v)
        return {y: sum(v) / len(v) for y, v in out.items()}
    cols.append(('Секунд / мес.', 'spd', 'avg'))
    ys['spd'] = spd_year(S)
    if base:
        yb['spd'] = spd_year(base['S'])
    h.append(''.join(f'<th class="n">{esc(a)}</th>' for a, _, _ in cols) + '</tr></thead><tbody>')
    for y in sorted({y for v in ys.values() for y in v}):
        cells = []
        for _, k, _ in cols:
            v = fmt(ys[k].get(y))
            if base:
                v += f' / {fmt(yb.get(k, {}).get(y))}'
            cells.append(f'<td class="n">{v}</td>')
        h.append(f'<tr><td>{y}</td>{"".join(cells)}</tr>')
    h.append('</tbody></table></div></main>')
    data = dict(ch=ch, B=B, t0=t[0] if t else 1836, t1=t[-1] if t else 1848)
    h.append('<script>const DATA=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';' + JS + '</script>')
    open(out, 'w', encoding='utf-8').write('\n'.join(h))
    return out


def save_data(D, path):
    # JSON lines, one series a line ({"p": [key, ...], "v": value}): the bridge reads the file in parts
    with open(path, 'w', encoding='utf-8') as f:
        for k, v in D.items():
            if k in ('S', 'C', 'X', 'end', 'xend'):
                for k2, v2 in v.items():
                    if k in ('C', 'X'):
                        for k3, v3 in v2.items():
                            f.write(json.dumps({'p': [k, k2, k3], 'v': v3}, ensure_ascii=False, separators=(',', ':')) + '\n')
                    else:
                        f.write(json.dumps({'p': [k, k2], 'v': v2}, ensure_ascii=False, separators=(',', ':')) + '\n')
            else:
                f.write(json.dumps({'p': [k], 'v': v}, ensure_ascii=False, separators=(',', ':')) + '\n')


def load_data(path):
    D = {'S': {}, 'C': {}, 'X': {}, 'end': {}, 'xend': {}}
    for ln in open(path, encoding='utf-8'):
        ln = ln.strip()
        if not ln:
            continue
        r = json.loads(ln)
        p = r['p']
        if len(p) == 1:
            D[p[0]] = r['v']
        elif len(p) == 2:
            D[p[0]][p[1]] = r['v']
        else:
            D[p[0]].setdefault(p[1], {})[p[2]] = r['v']
    return D


def main():
    a = sys.argv[1:]

    def opt(name, conv=str, default=None):
        if name in a:
            i = a.index(name)
            v = conv(a[i + 1])
            del a[i:i + 2]
            return v
        return default
    until = opt('--until', float, 9999)
    data_out = opt('--data')
    base = opt('--base')
    title = opt('--title')
    src = opt('--from-data')
    if src:
        D = load_data(src)
        out = a[0]
    else:
        run, out = a[0], a[1]
        D = read_run(run, until)
        if data_out:
            save_data(D, data_out)
    B = load_data(base) if base else None
    render(D, out, B, title)
    print(f'{out}: {D["chk"]["lines"]} lines to {D["chk"]["last"]}; countries {len(D["end"])}, errors '
          f'{sum(n for _, n in D["err"])}')


if __name__ == '__main__':
    main()
