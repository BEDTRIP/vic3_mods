"""Проверка ссылок `файл:N` в `docs/` форка по смыслу (ФК2): в строках N−2…N+2 файла есть хоть одно имя из той же
строки документа (слово с `_`, от 5 знаков). Ссылки без имён в строке не проверяются.

    python tools/ld_docs_anchor.py [--rev <ревизия>] [--list]

`--rev` — читать файлы мода из коммита (документы — из рабочей копии); `--list` — напечатать неподтверждённые.
Печатает: ссылок проверено, подтверждено, нет. Ничего не меняет.
"""
import argparse
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ld_gen  # noqa: E402

MENTION = re.compile(r"((?:common|gui|events)/[^\s`:,;()]+\.(?:txt|gui)|\b[\w.\-]+\.(?:txt|gui)):(\d+)")
WORD = re.compile(r"[A-Za-z][\w]*_[\w]+")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    allf = subprocess.run(["git", "-C", ld_gen.FORK, "ls-files", "common", "gui", "events"], capture_output=True,
                          text=True, encoding="utf-8").stdout.split("\n")
    byname = {}
    for p in allf:
        if p:
            byname.setdefault(os.path.basename(p), p)
            byname[p] = p
    cache = {}

    def lines(rel):
        if rel not in cache:
            if a.rev:
                r = subprocess.run(["git", "-C", ld_gen.FORK, "show", f"{a.rev}:{rel}"], capture_output=True)
                t = r.stdout.decode("utf-8", "replace") if r.returncode == 0 else ""
            else:
                p = os.path.join(ld_gen.FORK, rel)
                t = open(p, encoding="utf-8-sig", errors="replace").read() if os.path.exists(p) else ""
            cache[rel] = t.split("\n")
        return cache[rel]
    ok = bad = 0
    docs = os.path.join(ld_gen.FORK, "docs")
    for fn in sorted(os.listdir(docs)):
        if not fn.endswith(".md"):
            continue
        for i, line in enumerate(open(os.path.join(docs, fn), encoding="utf-8").read().split("\n"), 1):
            words = {w for w in WORD.findall(line) if len(w) >= 5 and not w.endswith(("_txt", "_gui"))}
            if not words:
                continue
            for m in MENTION.finditer(line):
                rel = byname.get(m.group(1)) or byname.get(os.path.basename(m.group(1)))
                if not rel:
                    continue
                n = int(m.group(2))
                L = lines(rel)
                win = "\n".join(L[max(0, n - 3):n + 2])
                if any(w in win for w in words):
                    ok += 1
                else:
                    bad += 1
                    if a.list:
                        print(f"{fn}:{i}  {rel}:{n}  | {L[n - 1].strip()[:80] if 0 < n <= len(L) else '<за концом>'}")
    print(f"ссылок проверено {ok + bad}, подтверждено {ok}, нет {bad}")


if __name__ == "__main__":
    main()
