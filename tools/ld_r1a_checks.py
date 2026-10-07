"""R1а, проверки до начала (7.10.2026): разбор eflog.txt прогона.

Usage:
    py tools/ld_r1a_checks.py <run>/eflog.txt [--top N]

Р8  -- мост: на страну число недельных шагов (EFW, постановка в очередь моста) и приёмников (EFR); пропуски.
Р10 -- бюджетный тик: строки зонда EFD|дата|страна|was|now (диагностика R1а) -- в какие дни у стран меняется казна;
       если все страны меняются в один день недели -- тик общий.
Р2  -- торговля: за каждую неделю приёмника d_tc (изменение кассы торговых центров) против trade / tfin (торговля
       рынка по базовым ценам с масштабом) -- суммы и корреляция по странам.
"""
import re
import sys
from collections import Counter, defaultdict
from datetime import date

sys.stdout.reconfigure(encoding='utf-8')


MON = {"января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6, "июля": 7, "августа": 8,
       "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12, "January": 1, "February": 2, "March": 3, "April": 4,
       "May": 5, "June": 6, "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}


def d(s):
    """The game writes dates with month names of the user's language: 'января 8, 1836'."""
    mm = re.match(r'(\w+) (\d+), (\d+)', s.strip())
    if mm:
        return date(int(mm.group(3)), MON[mm.group(1)], int(mm.group(2)))
    y, m, dd = (int(x) for x in s.split('.')[:3])
    return date(y, m, dd)


def parse(path):
    rows = defaultdict(list)
    for line in open(path, encoding='utf-8', errors='replace'):
        i = line.find('EF')
        if i < 0:
            continue
        parts = line[i:].rstrip('\n').split('|')
        if len(parts) < 3 or parts[0] not in ('EFW', 'EFR', 'EFD'):
            continue
        kv = {}
        for p in parts[3:]:
            k, _, v = p.partition(' ')
            try:
                kv[k] = float(v.replace(',', ''))
            except ValueError:
                kv[k] = v
        rows[parts[0]].append((parts[1], parts[2], kv))
    return rows


def corr(a, b):
    n = len(a)
    if n < 3:
        return float('nan')
    ma, mb = sum(a) / n, sum(b) / n
    va = sum((x - ma) ** 2 for x in a) ** 0.5
    vb = sum((x - mb) ** 2 for x in b) ** 0.5
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (va * vb) if va and vb else float('nan')


def main():
    args = sys.argv[1:]
    top = 15
    if '--top' in args:
        i = args.index('--top'); top = int(args[i + 1]); del args[i:i + 2]
    rows = parse(args[0])
    efw, efr, eft = rows['EFW'], rows['EFR'], rows['EFD']
    dates = sorted({d(x[0]) for x in efw + efr + eft})
    print(f'lines: EFW {len(efw)}, EFR {len(efr)}, EFD {len(eft)}; dates {dates[0] if dates else "-"} .. {dates[-1] if dates else "-"}')

    # Р8
    w, r = Counter(c for _, c, _ in efw), Counter(c for _, c, _ in efr)
    # both lines are written for the player and GDP > 20M (EFR also for some more) -- compare where both are
    miss = {c: w[c] - r.get(c, 0) for c in w if c in r or w[c] > 2}
    print('\nР8 -- steps (EFW) vs receivers (EFR):')
    print(f'  countries with steps {len(w)}, with receivers {len(r)}; steps {sum(w.values())}, receivers {sum(r.values())}')
    lost = sorted(((v, c) for c, v in miss.items() if v > 1), reverse=True)
    print(f'  countries missing >1 receiver: {len(lost)}' + (': ' + ', '.join(f'{c} {v}' for v, c in lost[:20]) if lost else ''))
    # receivers per date (the bridge's rhythm)
    per_day = Counter(d(x[0]) for x in efr)
    if per_day:
        span = (max(per_day) - min(per_day)).days + 1
        print(f'  receivers on {len(per_day)} of {span} days; per week ~{sum(per_day.values()) / span * 7:.0f}')

    # Р10
    if eft:
        print('\nР10 -- treasury changes (EFD) by weekday of the game calendar:')
        wd = defaultdict(Counter)
        for dt, c, kv in eft:
            wd[c][d(dt).toordinal() % 7] += 1
        main_day = Counter()
        for c, cnt in wd.items():
            main_day[cnt.most_common(1)[0][0]] += 1
        print(f'  countries {len(wd)}; their most frequent day (ordinal mod 7): {dict(main_day)}')
        allday = Counter(d(dt).toordinal() % 7 for dt, _, _ in eft)
        print(f'  all changes by day: {dict(sorted(allday.items()))}')
        days = sorted({d(dt) for dt, _, _ in eft})
        for dd in days[:30]:
            n = sum(1 for dt, _, _ in eft if d(dt) == dd)
            print(f'    {dd} (mod7 {dd.toordinal() % 7}): {n} countries')

    # Р2
    print(f'\nР2 -- trade: d_tc (trade centres\' cash change) vs trade (market trade, base prices) and tfin, top {top}:')
    by = defaultdict(list)
    for dt, c, kv in efr:
        if isinstance(kv.get('d_tc'), float) and isinstance(kv.get('trade'), float):
            by[c].append((kv['d_tc'], kv['trade'], kv.get('tfin', 0.0) if isinstance(kv.get('tfin'), float) else 0.0,
                          kv.get('ext_net', 0.0) if isinstance(kv.get('ext_net'), float) else 0.0))
    big = sorted(by, key=lambda c: -sum(abs(x[1]) for x in by[c]))[:top]
    print(f'  {"country":<22}{"weeks":>6}{"Σd_tc":>13}{"Σtrade":>13}{"Σtfin":>13}{"Σext_net":>13}{"corr(dtc,trade)":>17}')
    for c in big:
        xs = by[c]
        print(f'  {c[:21]:<22}{len(xs):>6}{sum(x[0] for x in xs):>13,.0f}{sum(x[1] for x in xs):>13,.0f}'
              f'{sum(x[2] for x in xs):>13,.0f}{sum(x[3] for x in xs):>13,.0f}{corr([x[0] for x in xs], [x[1] for x in xs]):>17.2f}')


if __name__ == '__main__':
    main()
