"""Проверка документации форка «E&F: Ledgerdemain» (`docs/`, ФК2).

1. Каждый файл `common/` и `events/` форка упомянут в `docs/` — путём целиком или маской (`common/laws/01_ef_*.txt`,
   `PSC_*`, `<cur>`/`<lang>` — любое имя).
2. Каждый путь в обратных кавычках в `docs/` (начинается с `common/`, `gui/`, `events/`, `localization/`) существует
   (маски — совпадают хотя бы с одним файлом), строка `путь:N` — не дальше конца файла.

    python tools/ld_docs_check.py [--fork <путь>]

Код выхода 1 — есть непокрытые файлы или битые ссылки. Ничего не меняет.
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
    sys.exit(1 if bad or uncovered else 0)


if __name__ == "__main__":
    main()
