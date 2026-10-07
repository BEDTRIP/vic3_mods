"""Пересчёт номеров строк в `docs/` форка после правки файлов (ФК2): `файл:N` → новая строка того же места.

    python tools/ld_docs_lines.py <ревизия-база> [--dry]

База — коммит, на котором номера в документах были верны. Для каждого файла `common/`, `gui/`, `events/`,
изменённого от базы до рабочей копии, по ханкам `git diff -U0` строится отображение «старая строка → новая»
(строка внутри удалённого куска → начало куска в новом файле). В строке документа после упоминания такого файла
(путь или имя) пересчитываются номера `:N`, перечни `N,M`, диапазоны `N-M` / `N…M` / `N..M` — до следующего
упоминания другого файла. Ссылки без имени файла в строке (`:N` в продолжении абзаца) печатаются для ручной
проверки. `--dry` — только напечатать замены.
"""
import argparse
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ld_gen  # noqa: E402

HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", re.M)


def git(*a):
    return subprocess.run(["git", "-C", ld_gen.FORK, *a], capture_output=True, text=True, encoding="utf-8").stdout


def mapping(base, rel):
    hunks = []
    for m in HUNK.finditer(git("diff", "-U0", base, "--", rel)):
        os_, oc, ns, nc = int(m.group(1)), int(m.group(2) or 1), int(m.group(3)), int(m.group(4) or 1)
        hunks.append((os_, oc, ns, nc))

    def f(n):
        off = 0
        for os_, oc, ns, nc in hunks:
            if oc == 0:  # вставка после строки os_
                if n > os_:
                    off = ns + nc - 1 - os_
                continue
            if n < os_:
                break
            if n < os_ + oc:  # строка удалена или заменена
                return ns if nc else max(ns, 1)
            off = (ns + nc) - (os_ + oc)
        return n + off
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    changed = [p for p in git("diff", "--name-only", a.base, "--", "common", "gui", "events").split("\n") if p]
    maps = {p: mapping(a.base, p) for p in changed}
    names = {}
    for p in changed:
        names[p] = p
        names.setdefault(os.path.basename(p), p)
    mention = re.compile(r"((?:common|gui|events)/[^\s`:,;()]+\.(?:txt|gui)|\b[\w.\-]+\.(?:txt|gui))")
    num = re.compile(r"(:|(?<=\d)(?:,\s?|-|–|…|\.\.)|^)(\d+)")
    docs = os.path.join(ld_gen.FORK, "docs")
    total = 0
    for fn in sorted(os.listdir(docs)):
        if not fn.endswith(".md"):
            continue
        p = os.path.join(docs, fn)
        lines = open(p, encoding="utf-8").read().split("\n")
        ch = 0
        for i, line in enumerate(lines):
            ms = list(mention.finditer(line))
            if not ms:
                continue
            out, pos = [], 0
            for k, m in enumerate(ms):
                end = ms[k + 1].start() if k + 1 < len(ms) else len(line)
                rel = names.get(m.group(1)) or names.get(os.path.basename(m.group(1)))
                out.append(line[pos:m.end()])
                seg = line[m.end():end]
                if rel:
                    f = maps[rel]
                    # номера идут сразу за именем: `:N`, затем перечни/диапазоны
                    mm = re.match(r"(:\d+(?:(?:,\s?|-|–|…|\.\.|/)\d+)*)", seg)
                    head, rest = (mm.group(1), seg[mm.end():]) if mm else ("", seg)
                    if head:
                        head = re.sub(r"(:|,\s?|-|–|…|\.\.|/)(\d+)", lambda x: x.group(1) + str(f(int(x.group(2)))), head)
                    # дальнейшие ` :N` в том же сегменте
                    rest = re.sub(r"((?:^|[\s(;])[:])(\d+)", lambda x: x.group(1) + str(f(int(x.group(2)))), rest)
                    seg = head + rest
                out.append(seg)
                pos = end
            out.append(line[pos:])
            new = "".join(out)
            if new != line:
                ch += 1
                if a.dry:
                    print(f"{fn}:{i + 1}\n  - {line[:300]}\n  + {new[:300]}")
                lines[i] = new
        if ch:
            total += ch
            print(f"{fn}: строк изменено {ch}")
            if not a.dry:
                open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    print("всего", total)


if __name__ == "__main__":
    main()
