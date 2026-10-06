"""Ошибки прогона по местам в коде (ФК2, шаг 4): что чинить, где и сколько раз сработало.

    python tools/ld_errsites.py <прогон> [--out <файл>] [--top N] [--all]

Прогон — папка с `error.log` / `error.N.log` / `errparts/` (`runs/<id>` моста). Запись лога — строка с
`[ЧЧ:ММ:СС][файл.cpp:N]:` и строки-продолжения без метки. Место — путь мода с номером строки из текста записи
(`'common/…:N'`, `Script location: …:N`, `file: "…" near line: N`, `at …:N`, `gui/…:N -`). Ключ — место + сообщение
(числа → N, место вырезано). По умолчанию — только места в файлах мода (`common/`, `gui/`, `events/`,
`localization/`); `--all` — и записи без места. Печатает: число записей и мест; по файлам — сколько записей; список
мест по убыванию. Ничего не меняет.
"""
import argparse
import glob
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ld_gen  # noqa: E402

HEAD = re.compile(r"^\[\d\d:\d\d:\d\d\]\[[^\]]*\]:\s?")
LOC = re.compile(r"((?:common|gui|events|localization)/[^'\"\n:]+?\.(?:txt|gui|yml))(?:['\"]?\s*(?:near line:|:)\s*(\d+))?")
NUM = re.compile(r"\b\d+(\.\d+)?\b")


_maps = {}


def real_lines(rel, n):
    """Строка error.log → настоящие строки файла форка. В эффектах и значениях движок считает строки определения
    без пустых и комментарных (находка ФК2, 7.10): отсчёт сбрасывается на каждом определении верхнего уровня."""
    if rel not in _maps:
        p = os.path.join(ld_gen.FORK, rel)
        rep = {}
        if os.path.exists(p):
            c = 0
            with open(p, encoding="utf-8-sig", errors="replace") as f:
                for i, l in enumerate(f.read().split("\n"), 1):
                    if re.match(r"[A-Za-z_][\w:.\-]*\s*=", l):
                        c = 0
                    if re.match(r"^[ \t]*(#.*)?$", l):
                        c += 1
                    else:
                        rep.setdefault(i - c, []).append(i)
        _maps[rel] = rep
    return _maps[rel].get(n, [])


def entries(run):
    files = sorted(glob.glob(os.path.join(run, "errparts", "*"))) or \
        sorted(glob.glob(os.path.join(run, "error*.log")), key=lambda p: (-len(p), p), reverse=True)
    cur = None
    for p in files:
        with open(p, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.rstrip("\n")
                if HEAD.match(line):
                    if cur is not None:
                        yield cur
                    cur = HEAD.sub("", line)
                elif cur is not None:
                    cur += "\n" + line
    if cur is not None:
        yield cur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--out")
    ap.add_argument("--top", type=int, default=400)
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    if a.out:
        sys.stdout = open(a.out, "w", encoding="utf-8")
    sites = Counter()
    per_file = Counter()
    total = located = 0
    for e in entries(a.run):
        total += 1
        locs = [(m.group(1), m.group(2) or "?") for m in LOC.finditer(e)]
        msg = LOC.sub("<loc>", e.split("\n")[0])
        msg = NUM.sub("N", msg)[:240]
        if locs:
            located += 1
            f, n = locs[0]
            sites[(f"{f}:{n}", msg)] += 1
            per_file[f] += 1
        elif a.all:
            sites[("-", msg)] += 1
    print(f"записей {total}, с местом в моде {located}, мест {len(sites)}, файлов {len(per_file)}")
    print("\n## По файлам")
    for f, n in per_file.most_common():
        print(f"{n:7d}  {f}")
    print("\n## Места")
    for (loc, msg), n in sites.most_common(a.top):
        extra = ""
        if loc != "-" and "/script" in loc and loc.rsplit(":", 1)[1].isdigit():
            f, ln = loc.rsplit(":", 1)
            real = real_lines(f, int(ln))
            if real and real != [int(ln)]:
                extra = f"  (строки в файле: {','.join(map(str, real[:3]))})"
        print(f"{n:7d}  {loc}  {msg}{extra}")


if __name__ == "__main__":
    main()
