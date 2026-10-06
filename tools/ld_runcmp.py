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


BLOB = re.compile(r"tooltip:[^\s!»]*|dw_\d+,[A-Za-z0-9+/=]+|[A-Za-z0-9+/]{24,}={0,2}")


def family(line):
    s = TS.sub("", line)
    s = BLOB.sub("<blob>", s)
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


MONTHS = {"января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6, "июля": 7, "августа": 8,
          "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12, "january": 1, "february": 2, "march": 3,
          "april": 4, "may": 5, "june": 6, "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
          "december": 12}


def ddate(s):
    """Дата лога: `1836.1.13` или локализованная `января 13, 1836` / `January 13, 1836`."""
    s = s.strip()
    m = re.match(r"(\d+)\.(\d+)\.(\d+)$", s)
    if m:
        return tuple(int(x) for x in m.groups())
    m = re.match(r"([^\W\d_]+)\s+(\d+),\s*(\d+)$", s)
    if m and m.group(1).lower() in MONTHS:
        return (int(m.group(3)), MONTHS[m.group(1).lower()], int(m.group(2)))
    return None


def week_clock(run):
    """Стенные часы недельного шага: метки [ЧЧ:ММ:СС] строк EFW одной страны (самой частой) в dbgparts/debug*.log.
    Возвращает (страна, [(дата, секунды от первой строки)])."""
    rx = re.compile(r"^\[(\d\d):(\d\d):(\d\d)\].*?EFW\|([^|]+)\|([^|]+)\|")
    rows = []
    files = sorted(glob.glob(os.path.join(run, "dbgparts", "*"))) + sorted(glob.glob(os.path.join(run, "debug*.log")))
    seen = set()
    for p in files:
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                for l in f:
                    m = rx.match(l)
                    if m and (m.group(4), m.group(5)) not in seen:
                        seen.add((m.group(4), m.group(5)))
                        d = ddate(m.group(4))
                        if d:
                            rows.append((m.group(5), d, int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))))
        except OSError:
            pass
    if not rows:
        return None, []
    who = Counter(r[0] for r in rows).most_common(1)[0][0]
    pts = sorted((d, s) for c, d, s in rows if c == who)
    out, base, prev, add = [], pts[0][1], pts[0][1], 0
    for d, s in pts:
        if s < prev:  # через полночь
            add += 86400
        prev = s
        out.append((d, s + add - base))
    return who, out


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
            if t0 and (re.match(r"new autosaves: [1-9]", m.group(2)) or m.group(2).startswith("closing the game")):
                t1 = t
                if m.group(2).startswith("new autosaves"):
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
    ap.add_argument("--top-b", type=int, default=0, help="сколько самых частых семейств B напечатать")
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
    print("\n### Все семейства B (топ по числу строк)")
    for k, v in eb.most_common(a.top_b):
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
    print(f"\n## Время до автосейва / конца (run.log, точность ~1 мин)\nA: {ta} с\nB: {tb} с")
    print("\n## Часы недельного шага (EFW одной страны: секунды от первой недели)")
    for name, r in (("A", a.a), ("B", a.b)):
        who, pts = week_clock(r)
        if not pts:
            print(f"{name}: нет строк EFW с метками")
            continue
        weeks = len(pts) - 1
        tot = pts[-1][1]
        steps = [pts[i + 1][1] - pts[i][1] for i in range(weeks)]
        print(f"{name}: {who}, недель {weeks}, {pts[0][0]} → {pts[-1][0]}, {tot} с, {tot / max(weeks, 1):.1f} с/нед, "
              f"макс. неделя {max(steps) if steps else 0} с")
        print("   по неделям:", " ".join(str(x) for x in steps))


if __name__ == "__main__":
    main()
