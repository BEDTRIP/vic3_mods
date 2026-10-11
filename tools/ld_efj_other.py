"""«Прочее» денег по странам из недельного лога EFJ: где копится и чем — скачками или дрейфом (R8в).

Usage:  py tools/ld_efj_other.py <run>/eflog.txt [--top N] [--jump J]

По последней строке EFJ каждой страны: «прочее» (other), его части пула и казны, выкуп уровней пула и казны; по всем
неделям — сумма недельных изменений «прочего» (d_other) скачками (|d_other| >= J, по умолчанию 20 000) и дрейфом
(остальное), число скачков и три крупнейших (дата, величина). Строки — по |other|, мир — итог.
Через мост: py_tool("ld_efj_other", ["runs/<id>/eflog.txt"]).
"""
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")


def main():
    a = sys.argv[1:]
    path = a[0]
    top = int(a[a.index('--top') + 1]) if '--top' in a else 25
    jump = float(a[a.index('--jump') + 1]) if '--jump' in a else 20000
    last = {}
    jumps = defaultdict(list)
    drift = defaultdict(float)
    for ln in open(path, encoding='utf-8', errors='replace'):
        p = ln.rstrip('\n').split('|')
        if len(p) < 5 or p[0] != 'EFJ' or not p[3].startswith('other '):
            continue
        d = {}
        for x in p[3:]:
            k, _, v = x.partition(' ')
            try:
                d[k] = float(v)
            except ValueError:
                pass
        last[p[2]] = d
        do = d.get('d_other', 0)
        if abs(do) >= jump:
            jumps[p[2]].append((do, p[1]))
        else:
            drift[p[2]] += do
    keys = ['other', 'other_pool', 'other_tr', 'lvl_pool', 'lvl_tr']
    w = defaultdict(float)
    print(f"{'страна':24} " + ' '.join(f'{k:>11}' for k in keys) + f" {'скачки':>11} {'n':>3} {'дрейф':>11}  крупнейшие")
    rows = sorted(last, key=lambda c: -abs(last[c].get('other', 0)))
    for c in rows:
        d = last[c]
        js = sum(x for x, _ in jumps[c])
        for k in keys:
            w[k] += d.get(k, 0)
        w['jumps'] += js; w['n'] += len(jumps[c]); w['drift'] += drift[c]
        if rows.index(c) < top:
            big = sorted(jumps[c], key=lambda x: abs(x[0]))[-3:][::-1]
            print(f'{c[:24]:24} ' + ' '.join(f'{d.get(k, 0):11.0f}' for k in keys)
                  + f' {js:11.0f} {len(jumps[c]):3} {drift[c]:11.0f}  ' + '; '.join(f'{x:.0f} {t}' for x, t in big))
    print(f"{'МИР (' + str(len(last)) + ')':24} " + ' '.join(f'{w[k]:11.0f}' for k in keys)
          + f" {w['jumps']:11.0f} {int(w['n']):3} {w['drift']:11.0f}")


if __name__ == '__main__':
    main()
