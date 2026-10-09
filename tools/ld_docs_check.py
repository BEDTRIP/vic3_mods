"""Проверка документации форка «E&F: Ledgerdemain» (`docs/`, ФК2).

1. Каждый файл `common/` и `events/` форка упомянут в `docs/` — путём целиком или маской (`common/laws/01_ef_*.txt`,
   `PSC_*`, `<cur>`/`<lang>` — любое имя).
2. Каждый путь в обратных кавычках в `docs/` (начинается с `common/`, `gui/`, `events/`, `localization/`) существует
   (маски — совпадают хотя бы с одним файлом), строка `путь:N` — не дальше конца файла.
3. Каждая вики-ссылка `[[Имя]]` / `[[Имя|подпись]]` в `docs/`, `понятия/`, `ваниль/`, `план.md`, `решения.md` ведёт
   на заметку `понятия/Имя.md` (или другой `.md` форка с таким именем); заметка понятия без входящих ссылок — тоже
   ошибка.
4. Заметка понятия (`понятия/`, кроме `_*` и заметок с тегом `обзор`) — разделы «## Подсказка», «## Рабочее»,
   «### Целевое значение», «### Что в коде» по порядку; подсказка не пустая, без кода в обратных кавычках и номеров
   решений — она уйдёт в игру.

    python tools/ld_docs_check.py [--fork <путь>]

Код выхода 1 — есть непокрытые файлы, битые ссылки или заметки не по формату. Ничего не меняет.
"""
import argparse
import fnmatch
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FORK = os.path.normpath(os.path.join(HERE, "..", "..", "Economic-and-Financial-Ledgerdemain-Mod"))
ROOTS = ("common/", "gui/", "events/", "localization/")
REF = re.compile(r"`((?:common|gui|events|localization)/[^`\n:]+?)(?::(\d+)[^`]*)?`")


def files(fork, top):
    for dp, dn, fn in os.walk(os.path.join(fork, top)):
        for f in fn:
            yield os.path.relpath(os.path.join(dp, f), fork).replace(os.sep, "/")


def pattern(p):
    p = re.sub(r"<[^>]+>", "*", p)
    return p.rstrip("/") + ("/**" if p.endswith("/") else "")


def match(pat, rel):
    if pat.endswith("/**"):
        pat = pat[:-3]
    return fnmatch.fnmatchcase(rel, pat) or any(
        fnmatch.fnmatchcase(rel[:i], pat) for i in range(len(rel)) if rel[i] == "/")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fork", default=FORK)
    a = ap.parse_args()
    docs = os.path.join(a.fork, "docs")
    refs = []
    for f in sorted(os.listdir(docs)):
        if f.endswith(".md"):
            text = open(os.path.join(docs, f), encoding="utf-8").read()
            for m in REF.finditer(text):
                refs.append((f, m.group(1), int(m.group(2)) if m.group(2) else None))
    all_files = [r for t in ROOTS for r in files(a.fork, t)]
    bad = []
    pats = set()
    for doc, p, line in refs:
        pat = pattern(p)
        pats.add(pat)
        hit = [r for r in all_files if match(pat, r)]
        if not hit:
            bad.append(f"{doc}: нет файла `{p}`")
        elif line and "*" not in pat:
            with open(os.path.join(a.fork, hit[0]), "rb") as fh:
                n = fh.read().count(b"\n") + 1
            if line > n:
                bad.append(f"{doc}: `{p}:{line}` — в файле {n} строк")
    need = [r for t in ("common/", "events/") for r in files(a.fork, t)]
    uncovered = [r for r in need if not any(match(p, r) for p in pats)]
    print(f"ссылок {len(refs)}, битых {len(bad)}; файлов common/events {len(need)}, не упомянуто {len(uncovered)}")
    for x in bad:
        print("  битая:", x)
    for x in uncovered:
        print("  не упомянут:", x)
    wbad, orphans = wiki(a.fork)
    for x in wbad:
        print("  битая вики-ссылка:", x)
    for x in orphans:
        print("  понятие без ссылок на него:", x)
    fbad = notes_format(a.fork)
    for x in fbad:
        print("  формат заметки:", x)
    sys.exit(1 if bad or uncovered or wbad or orphans or fbad else 0)


HEADS = ("## Подсказка", "## Рабочее", "### Целевое значение", "### Что в коде")


def notes_format(fork):
    """Заметки понятий: разделы по порядку; подсказка без кода и номеров решений."""
    d = os.path.join(fork, "понятия")
    bad, n = [], 0
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if not f.endswith(".md") or f.startswith("_"):
            continue
        text = open(os.path.join(d, f), encoding="utf-8").read()
        if re.search(r"^tags:.*\bобзор\b", text, re.M):
            continue
        n += 1
        lines = text.split("\n")
        pos = [lines.index(h) if h in lines else -1 for h in HEADS]
        if -1 in pos or pos != sorted(pos):
            bad.append(f"{f}: нужны разделы {' → '.join(HEADS)}")
            continue
        tip = "\n".join(lines[pos[0] + 1:pos[1]])
        if not tip.strip():
            bad.append(f"{f}: пустая подсказка")
        elif "`" in tip or re.search(r"Д\.(?:R|П|Г|\d)", tip):
            bad.append(f"{f}: в подсказке код или номер решения")
    print(f"формат заметок понятий: проверено {n}, не по формату {len(bad)}")
    return bad


WIKI = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")


def wiki(fork):
    """Вики-ссылки документации форка: (битые, понятия без входящих ссылок)."""
    names = set()
    for dp, dn, fn in os.walk(fork):
        dn[:] = [d for d in dn if d not in (".git", "common", "gui", "events", "localization", "gfx", "_archive")]
        names.update(f[:-3] for f in fn if f.endswith(".md"))
    srcs = [os.path.join(fork, "план.md"), os.path.join(fork, "решения.md")]
    for d in ("docs", "понятия", "ваниль"):
        dd = os.path.join(fork, d)
        if os.path.isdir(dd):
            srcs += [os.path.join(dd, f) for f in sorted(os.listdir(dd)) if f.endswith(".md")]
    bad, seen = [], set()
    for src in srcs:
        if not os.path.exists(src):
            continue
        rel = os.path.relpath(src, fork)
        own = os.path.basename(src)[:-3]
        for m in WIKI.finditer(open(src, encoding="utf-8").read()):
            n = m.group(1).strip()
            if n not in names:
                bad.append(f"{rel}: [[{n}]]")
            elif n != own:
                seen.add(n)
    notes = os.path.join(fork, "понятия")
    orphans = []
    if os.path.isdir(notes):
        orphans = [f[:-3] for f in sorted(os.listdir(notes))
                   if f.endswith(".md") and f[:-3] not in seen and not f.startswith("_")]
    print(f"вики-ссылки: битых {len(bad)}, понятий без входящих ссылок {len(orphans)}")
    return bad, orphans


if __name__ == "__main__":
    main()
