"""A field of the fork's weekly EFR line by year and country (форк, R9б.4 — чеканка ЦБ без здания).

Usage:  py tools/ld_efr_sum.py <run>/eflog.txt [--field mint] [--top 10] [--countries "Великобритания,Франция"]

Per year: the weekly average of the field over the country's EFR lines, for the top countries by the field's total and
for the given ones, and the world's sum of the countries' averages. EFR -- the bridge's weekly line of the money model
(scripted_effects/ld_money_model.txt): ext, mint, mint_tr ...
"""
import sys
from collections import defaultdict


def year(date):
    try:
        return int(date.rsplit(',', 1)[1])
    except (ValueError, IndexError):
        return None


def main():
    a = sys.argv[1:]
    field = a[a.index('--field') + 1] if '--field' in a else 'mint'
    top = int(a[a.index('--top') + 1]) if '--top' in a else 10
    want = a[a.index('--countries') + 1].split(',') if '--countries' in a else []
    tot = defaultdict(lambda: defaultdict(float))
    cnt = defaultdict(lambda: defaultdict(int))
    for ln in open(a[0], encoding='utf-8', errors='replace'):
        if not ln.startswith('EFR|'):
            continue
        p = ln.rstrip('\n').split('|')
        y = year(p[1])
        if y is None:
            continue
        for x in p[3:]:
            k, _, v = x.partition(' ')
            if k == field:
                try:
                    tot[p[2]][y] += float(v)
                    cnt[p[2]][y] += 1
                except ValueError:
                    pass
                break
    years = sorted({y for c in tot for y in tot[c]})
    avg = {c: {y: tot[c][y] / cnt[c][y] for y in tot[c] if cnt[c][y]} for c in tot}
    order = sorted(avg, key=lambda c: -sum(avg[c].values()))
    show = order[:top] + [c for c in want if c in avg and c not in order[:top]]
    print(f'{field}: weekly average by year')
    print(f'{"country":28}' + ''.join(f'{y:>12}' for y in years))
    world = {y: sum(avg[c].get(y, 0) for c in avg) for y in years}
    print(f'{"WORLD":28}' + ''.join(f'{world[y]:12.0f}' for y in years))
    for c in show:
        print(f'{c[:28]:28}' + ''.join(f'{avg[c].get(y, 0):12.0f}' for y in years))


if __name__ == '__main__':
    main()
