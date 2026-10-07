"""Сравнение логов двух прогонов по семействам (ФК2): база (CMF + ETF без форка, ваниль) против форка.

    python tools/ld_logdiff.py <база> <прогон> [--kinds debug,warning,game,error] [--top N] [--out <файл>]

Папки — как у `ld_logcats.py` (`runs/<id>` моста, `dbgparts/` и `errparts/` тоже читаются). Запись — строка с
`[ЧЧ:ММ:СС][файл.cpp:N]:`. Ключ — текст без времени и чисел, **имена в кавычках сохранены** (иначе «Unknown
trigger 'a'» и «… 'b'» сливаются); общее семейство (имена → '…') — для сводки. По каждому виду: записей и ключей
в базе и прогоне; семейства только прогона, выросшие (> 2× и +10), ушедшие; строки логов мода (`EF?|…`,
`common/…: EF`) — отдельной строкой, они нужны и в семейства не идут. Ничего не меняет.
"""
import argparse
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ld_logcats import HEAD, NUM, QUOTED, files  # noqa: E402

MODLOG = re.compile(r"(^|: )EF[A-Z]{1,2}\|")



def load(d, kind):
    keys, fams, ex, modlog, n = Counter(), Counter(), {}, 0, 0
    for p in files(d, kind):
        with open(p, encoding="utf-8", errors="replace") as f:
            for line in f:
                m = HEAD.match(line.rstrip("\n"))
                if not m:
                    continue
                n += 1
                msg = m.group(2)
                if MODLOG.search(msg):
                    modlog += 1
                    continue
                k = NUM.sub("N", msg)[:260]
                keys[k] += 1
                fams[NUM.sub("N", QUOTED.sub("'…'", msg))[:200]] += 1
                ex.setdefault(k, msg[:300])
    return n, modlog, keys, fams, ex


def fam_of(k):
    return QUOTED.sub("'…'", k)[:200]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("run")
    ap.add_argument("--kinds", default="debug,warning,game,error")
    ap.add_argument("--top", type=int, default=60)
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.out:
        sys.stdout = open(a.out, "w", encoding="utf-8")
    print(f"база: {a.base}\nпрогон: {a.run}")
    for kind in a.kinds.split(","):
        nA, mA, kA, fA, _ = load(a.base, kind)
        nB, mB, kB, fB, exB = load(a.run, kind)
        only = {k: c for k, c in kB.items() if k not in kA}
        grown = {k: (kA[k], c) for k, c in kB.items() if k in kA and c > 2 * kA[k] and c - kA[k] >= 10}
        gone = {k: c for k, c in kA.items() if k not in kB}
        print(f"\n# {kind}: база {nA} записей / {len(kA)} ключей; прогон {nB} записей / {len(kB)} ключей"
              f" (строк логов мода {mB}, в базе {mA})")
        print(f"только в прогоне: ключей {len(only)}, записей {sum(only.values())}; "
              f"выросло: {len(grown)}; ушло из базы: ключей {len(gone)}, записей {sum(gone.values())}")
        sf = Counter()
        for k, c in only.items():
            sf[fam_of(k)] += c
        print("## только в прогоне — по семействам")
        for f, c in sf.most_common(a.top):
            print(f"{c:8d}  {f}")
        print("## только в прогоне — ключи")
        for k, c in sorted(only.items(), key=lambda x: -x[1])[:a.top]:
            print(f"{c:8d}  {exB[k]}")
        if grown:
            print("## выросло (база → прогон)")
            for k, (x, y) in sorted(grown.items(), key=lambda x: -(x[1][1] - x[1][0]))[:a.top]:
                print(f"{x:8d} → {y:<8d} {exB[k]}")
        if gone:
            print("## ушло (есть в базе, нет в прогоне)")
            for k, c in sorted(gone.items(), key=lambda x: -x[1])[:a.top // 2]:
                print(f"{c:8d}  {k}")


if __name__ == "__main__":
    main()
