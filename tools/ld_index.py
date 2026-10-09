"""Индекс форка «E&F: Ledgerdemain» (ФК2): верхнеуровневые определения, их размер и число ссылок на них.

Для разведки и уборки: какие эффекты / значения / триггеры / GUI-типы определены где, сколько строк занимают и
упоминаются ли где-нибудь ещё (скрипт, GUI, локализация, события). Ссылка = вхождение имени как слова в любом файле
мода, кроме самого определения (имя внутри своего тела — рекурсия — тоже не считается).

    python tools/ld_index.py [--fork <путь>] [--out <папка>]

Пишет `<out>/index.tsv` (файл, строка, папка, ключ, строк, ссылок) и `<out>/files.tsv` (файл, строк, записей,
записей без ссылок). refs = -1 — точка входа движка (история, on_actions), -2 — ссылок по имени нет, но имя подходит
под шаблон с параметром (`stockpiling_$currency$_c_var_1`). Ничего в форке не меняет.
"""
import argparse
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ld_pdx  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FORK = os.path.normpath(os.path.join(HERE, "..", "..", "Economic-and-Financial-Ledgerdemain-Mod"))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "_tmp_analysis", "ld_index"))
WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
# имя, собранное из параметра эффекта: `stockpiling_$currency$_c_var_1` — ссылка на любое подходящее имя
PARAM = re.compile(r"[A-Za-z0-9_]*(?:\$[A-Za-z_]+\$[A-Za-z0-9_]*)+")
TEXT_EXT = (".txt", ".gui", ".yml", ".gfx", ".asset", ".shader", ".fxh")
GUI_TYPE = re.compile(r"^\s*(?:type|template)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=", re.M)


# комментарий — `#` вне строки в кавычках: в GUI `"#T [..ScriptValue('x')..]"` — форматирование текста, не комментарий
COMMENT = re.compile(r'"[^"\n]*"|#[^\n]*')


def strip_comments(t):
    return COMMENT.sub(lambda m: m.group(0) if m.group(0).startswith('"') else "", t)


def walk(root):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in (".git", "docs", "_archive", "понятия", "история")]  # _archive/ — мёртвое, игра не читает
        for f in fn:
            if f.endswith(TEXT_EXT):
                yield os.path.join(dp, f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fork", default=FORK)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    words = Counter()
    pats = set()
    texts = {}
    for p in walk(a.fork):
        t, _, _ = ld_pdx.read(p)
        rel = os.path.relpath(p, a.fork).replace("\\", "/")
        texts[rel] = t
        # комментарии не считаются ссылками
        clean = strip_comments(t) if not rel.endswith(".yml") else t
        words.update(WORD.findall(clean))
        for m in PARAM.finditer(clean):
            pats.add(m.group(0))

    # шаблоны с хотя бы одной буквенной частью вне параметров; `$X$` целиком — не шаблон
    rx = [re.compile("^" + re.sub(r"\\\$[A-Za-z_]+\\\$", "[A-Za-z0-9_]+", re.escape(p)) + "$")
          for p in pats if re.sub(r"\$[A-Za-z_]+\$", "", p).strip("_")]
    big = re.compile("|".join("(?:%s)" % r.pattern for r in rx)) if rx else None
    rows, files = [], []
    for rel, t in sorted(texts.items()):
        top = rel.split("/")[0]
        defs = []
        if rel.startswith(("common/", "events/")) and rel.endswith(".txt"):
            ents, _ = ld_pdx.parse(t)
            for e in ents:
                if rel.startswith("common/history") or rel.startswith("common/on_actions"):
                    kind = rel.split("/")[1]
                else:
                    kind = rel.split("/")[1] if top == "common" else "events"
                body = ld_pdx.norm(e.body(t)) if e.is_block else ""
                inner = len([w for w in WORD.findall(body) if w == e.key])
                defs.append((t.count("\n", 0, e.start) + 1, kind, e.key, t.count("\n", e.start, e.end) + 1, inner))
        elif rel.endswith(".gui"):
            for m in GUI_TYPE.finditer(t):
                defs.append((t.count("\n", 0, m.start()) + 1, "gui_type", m.group(1), 0, 0))
        else:
            continue
        own = Counter(k for _, _, k, _, _ in defs)
        dead = 0
        for line, kind, key, size, inner in defs:
            refs = words[key] - own[key] - inner
            if kind in ("history", "on_actions"):
                refs = -1          # точки входа движка, ссылок не ждём
            elif refs == 0 and big and big.match(key):
                refs = -2          # подходит под имя, собранное из параметра, — не мёртвое наверняка
            if refs == 0:
                dead += 1
            rows.append((rel, line, kind, key, size, refs))
        files.append((rel, t.count("\n") + 1, len(defs), dead))

    with open(os.path.join(a.out, "index.tsv"), "w", encoding="utf-8") as f:
        f.write("file\tline\tkind\tkey\tlines\trefs\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")
    with open(os.path.join(a.out, "files.tsv"), "w", encoding="utf-8") as f:
        f.write("file\tlines\tdefs\tunreferenced\n")
        for r in files:
            f.write("\t".join(map(str, r)) + "\n")
    tot_dead = sum(1 for r in rows if r[5] == 0)
    print(f"{len(files)} файлов, {len(rows)} определений, без ссылок {tot_dead} -> {a.out}")


if __name__ == "__main__":
    main()
