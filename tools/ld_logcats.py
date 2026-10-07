"""Сводка логов игры по семействам (ФК2): debug / warning / game / error — что пишется и сколько раз.

    python tools/ld_logcats.py <папка логов> [--kinds debug,warning] [--top N] [--out <файл>]

Папка — `logs` игры или `runs/<id>` моста (`dbgparts/`, `errparts/` тоже читаются). Запись — строка с
`[ЧЧ:ММ:СС][файл.cpp:N]:`; семейство — текст без времени, чисел и содержимого кавычек (имя в кавычках
оставлено для «Unknown …»: там важно, что именно; имена «set but never used» — отдельным списком). По каждому виду: записей, семейств,
по источнику (`файл.cpp`), топ семейств с одним примером. Ничего не меняет.
"""
import argparse
import glob
import os
import re
import sys
from collections import Counter

HEAD = re.compile(r"^\[\d\d:\d\d:\d\d\]\[([^\]]*)\]:\s?(.*)")
NUM = re.compile(r"\d+(\.\d+)?")
QUOTED = re.compile(r"'[^']*'|\"[^\"]*\"")


def family(msg):
    keep = "nknown" in msg
    s = msg if keep else QUOTED.sub("'…'", msg)
    return NUM.sub("N", s)[:220]


def files(d, kind):
    sub = {"debug": "dbgparts", "error": "errparts"}.get(kind)
    parts = sorted(glob.glob(os.path.join(d, sub, "*"))) if sub else []
    return parts or sorted(glob.glob(os.path.join(d, f"{kind}*.log")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--kinds", default="debug,warning,game,error")
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.out:
        sys.stdout = open(a.out, "w", encoding="utf-8")
    for kind in a.kinds.split(","):
        fam, src, ex, unused = Counter(), Counter(), {}, Counter()
        n = 0
        fl = files(a.dir, kind)
        for p in fl:
            with open(p, encoding="utf-8", errors="replace") as f:
                for line in f:
                    m = HEAD.match(line.rstrip("\n"))
                    if not m:
                        continue
                    n += 1
                    k = family(m.group(2))
                    fam[k] += 1
                    src[m.group(1).split(":")[0]] += 1
                    ex.setdefault(k, m.group(2)[:300])
                    u = re.match(r"(\w+) '([^']+)' is (?:set|used) but is never (?:used|set)", m.group(2))
                    if u:
                        unused[(u.group(1), u.group(2), "set" if "is set" in m.group(2) else "used")] += 1
        print(f"\n# {kind}: файлов {len(fl)}, записей {n}, семейств {len(fam)}")
        print("## по источнику")
        for s, c in src.most_common(15):
            print(f"{c:8d}  {s}")
        print("## семейства")
        for k, c in fam.most_common(a.top):
            print(f"{c:8d}  {k}")
            if ex[k] != k:
                print(f"          пример: {ex[k]}")
        if unused:
            print(f"## never used / never set: имён {len(unused)}")
            for (t, nm, how), c in sorted(unused.items()):
                print(f"  {t} {how}-but-never {nm}")


if __name__ == "__main__":
    main()
