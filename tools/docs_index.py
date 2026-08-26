"""
docs_index.py -- сводка по всем README набора без их чтения целиком.

Каждый README компача и сборки несёт машиночитаемую шапку:

    <!-- meta
    пара: LLWA × E&F
    статус: done
    ...
    -->

Скрипт собирает эти шапки в одну таблицу. Смысл -- чтобы вопрос «что у нас
вообще есть и в каком состоянии» стоил один прогон, а не тридцать пять чтений.

    python3 tools/docs_index.py                # таблица
    python3 tools/docs_index.py --missing      # только папки без README или без шапки
    python3 tools/docs_index.py --field статус # сгруппировать по одному полю
"""
from __future__ import annotations

import argparse
import os
import re

FIELDS = ["пара", "статус", "версии", "позиция", "файлов", "генератор", "зависит от"]
META_RE = re.compile(r"<!--\s*meta\s*(.*?)-->", re.S)
SKIP_DIRS = {"tools", "__translations", "сводки по модам", "_архив", "stuff", ".git"}


def read_meta(path: str) -> dict | None:
    try:
        txt = open(path, encoding="utf-8-sig", errors="ignore").read(4000)
    except OSError:
        return None
    m = META_RE.search(txt)
    if not m:
        return None
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta


def walk(root: str):
    for top in sorted(os.listdir(root)):
        p = os.path.join(root, top)
        if not os.path.isdir(p) or top in SKIP_DIRS:
            continue
        for sub in sorted(os.listdir(p)):
            sp = os.path.join(p, sub)
            if not os.path.isdir(sp):
                continue
            items = set(os.listdir(sp))
            is_mod = bool(items & {"common", "localization", ".metadata", "metadata.json"})
            if not is_mod and "README.md" not in items:
                continue
            yield f"{top}/{sub}", sp, ("README.md" in items)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--missing", action="store_true")
    ap.add_argument("--field", default=None)
    args = ap.parse_args()
    rows, missing = [], []
    for name, path, has_readme in walk(args.root):
        if not has_readme:
            missing.append((name, "нет README"))
            continue
        meta = read_meta(os.path.join(path, "README.md"))
        if meta is None:
            missing.append((name, "нет шапки meta"))
            continue
        rows.append((name, meta))
    if args.missing:
        for n, why in missing:
            print(f"{why:16} {n}")
        print(f"\nвсего без шапки: {len(missing)}, с шапкой: {len(rows)}")
        return
    if args.field:
        groups: dict[str, list] = {}
        for n, m in rows:
            groups.setdefault(m.get(args.field, "—"), []).append(n)
        for k in sorted(groups):
            print(f"{k} ({len(groups[k])})")
            for n in groups[k]:
                print("    ", n)
        return
    w = max((len(n) for n, _ in rows), default=10)
    print(f"{'папка'.ljust(w)}  {'статус':10} {'файлов':>6}  пара / сборка")
    for n, m in rows:
        print(f"{n.ljust(w)}  {m.get('статус','—'):10} {m.get('файлов','—'):>6}  {m.get('пара', m.get('сборка','—'))}")
    print(f"\nс шапкой: {len(rows)}, без шапки: {len(missing)} (см. --missing)")


if __name__ == "__main__":
    main()
