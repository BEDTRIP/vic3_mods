"""Сравнение двух прогонов песочницы (ФК2): ошибки, eflog, время.

    python tools/ld_runcmp.py <прогон A> <прогон B> [--weeks N] [--top N] [--fork-only]

Прогон — папка с `error.log` (+ `error.N.log`, `errparts/`), `eflog.txt`, `run.log` (`runs/<id>` моста или
`_tmp_analysis/fk0_runs/<имя>`). Пишет в stdout:
1. ошибки: число строк и семейств (строка без времени, чисел и кавычек) в A и B, новые и ушедшие семейства (топ по числу);
   `--fork-only` — только семейства, где упомянут файл мода (`common/`, `gui/`, `events/`, `localization/`);
2. eflog: число строк по префиксу (`EFW`, `EFX` …), последняя дата; первые N недель (по дате) — сколько строк совпало
   байт в байт, первые расхождения;
3. время: от «advancing: True» до первого автосейва / конца (`run.log`).
Ничего не меняет.
"""
import argparse
import glob
import os
import re
import sys
from collections import Counter
from datetime import datetime

TS = re.compile(r"^\[\d\d:\d\d:\d\d\]")
NUM = re.compile(r"\d+(\.\d+)?")
QUOTED = re.compile(r"'[^']*'|\"[^\"]*\"")
MODFILE = re.compile(r"(common|gui|events|localization)[/\\]")


def error_lines(run):
    files = sorted(glob.glob(os.path.join(run, "error*.log")), key=lambda p: (len(p), p))
    parts = sorted(glob.glob(os.path.join(run, "errparts", "*")))
    seen = []
    for p in parts + files:
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                seen.extend(f.read().splitlines())
        except OSError:
            pass
    return seen


def family(line):
    s = TS.sub("", line)
    s = re.sub(r"^\[[^\]]*\]:?\s*", "", s)  # [file.cpp:123]:
    s = QUOTED.sub("'…'", s) if "Unknown" not in s and "unknown" not in s else s
    return NUM.sub("N", s).strip()


def errors(run, fork_only):
    c = Counter()
    lines = error_lines(run)
    for l in lines:
        if not l.strip():
            continue
        if fork_only and not MODFILE.search(l):
            continue
        c[family(l)] += 1
    return len(lines), c


def eflog(run):
    p = os.path.join(run, "eflog.txt")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8", errors="replace") as f:
        return [l.rstrip("\n") for l in f if l.startswith("EF")]


def ddate(s):
    try:
        y, m, d = (int(x) for x in s.split("."))
        return (y, m, d)
    except ValueError:
        return None


def timing(run):
    p = os.path.join(run, "run.log")
    if not os.path.exists(p):
        return None
    t0 = t1 = None
    with open(p, encoding="utf-8", errors="replace") as f:
        for l in f:
            m = re.match(r"\[(\d\d:\d\d:\d\d)\]\s*(.*)", l)
            if not m:
                continue
            t = datetime.strptime(m.group(1), "%H:%M:%S")
            if t0 is None and m.group(2).startswith("advancing: True"):
                t0 = t
            if t0 and ("autosave" in m.group(2).lower() or m.group(2).startswith("closing the game")):
                t1 = t
                if "autosave" in m.group(2).lower():
                    break
    if t0 and t1:
        s = (t1 - t0).total_seconds()
        return s + 86400 if s < 0 else s
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--weeks", type=int, default=4)
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--fork-only", action="store_true")
    a = ap.parse_args()
    for r in (a.a, a.b):
        if not os.path.isdir(r):
            sys.exit(f"нет папки {r}")
        print(f"{r}: {', '.join(sorted(os.listdir(r))[:40])}")

    na, ea = errors(a.a, a.fork_only)
    nb, eb = errors(a.b, a.fork_only)
    print(f"\n## Ошибки{' (файлы мода)' if a.fork_only else ''}\nA: строк {na}, семейств {len(ea)}\nB: строк {nb}, семейств {len(eb)}")
    new = Counter({k: v for k, v in eb.items() if k not in ea})
    gone = Counter({k: v for k, v in ea.items() if k not in eb})
    print(f"новых семейств в B: {len(new)} (строк {sum(new.values())}); ушло: {len(gone)} (строк {sum(gone.values())})")
    print("\n### Новые в B (топ)")
    for k, v in new.most_common(a.top):
        print(f"{v:6d}  {k[:300]}")
    print("\n### Ушли из A (топ)")
    for k, v in gone.most_common(a.top):
        print(f"{v:6d}  {k[:300]}")

    la, lb = eflog(a.a), eflog(a.b)
    print("\n## eflog")
    for name, L in (("A", la), ("B", lb)):
        c = Counter(l.split("|", 1)[0] for l in L)
        last = max((ddate(l.split("|")[1]) for l in L if l.count("|") > 1 and ddate(l.split("|")[1])), default=None)
        print(f"{name}: строк {len(L)}, по префиксам {dict(sorted(c.items()))}, последняя дата {last}")
    dates = sorted({ddate(l.split("|")[1]) for l in la if l.count("|") > 1 and ddate(l.split("|")[1])})
    if dates:
        y, m, d = dates[0]
        lim = (y, m, d + 7 * a.weeks) if d + 7 * a.weeks <= 28 else (y, m + (d + 7 * a.weeks) // 28, (d + 7 * a.weeks) % 28)
        early = lambda L: [l for l in L if l.count("|") > 1 and ddate(l.split("|")[1]) and ddate(l.split("|")[1]) < lim]
        ea_, eb_ = early(la), early(lb)
        sb = Counter(eb_)
        same = sum(min(v, sb[k]) for k, v in Counter(ea_).items())
        print(f"первые ~{a.weeks} нед. (до {lim}): A {len(ea_)} строк, B {len(eb_)}, совпало байт в байт {same}")
        sa = set(ea_)
        diff = [l for l in eb_ if l not in sa][:8]
        for l in diff:
            print("  B≠:", l[:400])

    ta, tb = timing(a.a), timing(a.b)
    print(f"\n## Время до автосейва / конца\nA: {ta} с\nB: {tb} с")


if __name__ == "__main__":
    main()
