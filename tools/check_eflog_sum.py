"""Sum a field of one eflog record type over countries at its last date (этап 2).

Usage:  py tools/check_eflog_sum.py <eflog.txt> <record> <field> [<field> ...]

eflog lines are RECORD|date|country|key value|key value|... (tools/parse_eflog.py). For the record type (e.g.
EFX) takes the last date it appears with, and sums each field over the countries logged with that date.
Example: check_eflog_sum.py runs/<id>/eflog.txt EFX gdp m2
"""
import collections
import sys


def main():
    path, rec, fields = sys.argv[1], sys.argv[2], sys.argv[3:]
    last = {}
    for ln in open(path, encoding='utf-8', errors='replace'):
        p = ln.rstrip('\n').split('|')
        if len(p) < 4 or p[0] != rec:
            continue
        last.setdefault(p[1], {})[p[2]] = p[3:]
    if not last:
        print('no records'); return
    dates = list(last)
    date = dates[-1]
    # a month's records are spread over its days: take every country's last record within the last 31 entries
    pool = {}
    for d in dates[-31:]:
        pool.update(last[d])
    tot = collections.Counter()
    for kv in pool.values():
        for item in kv:
            k, _, v = item.partition(' ')
            if k in fields:
                try:
                    tot[k] += float(v)
                except ValueError:
                    pass
    print(f'{rec} last date {date}, countries {len(pool)}')
    for f in fields:
        print(f'{f} {tot[f]:.0f}')


if __name__ == '__main__':
    main()
