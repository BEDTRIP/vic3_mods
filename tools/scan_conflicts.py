"""Пересечения двух модов — обёртка над `v3 conflicts` (пакет vic3tools).

    py tools/scan_conflicts.py --a <мод A> --b <мод B> [--out отчёт.md]

То же напрямую: `v3 conflicts <A> <B> --mods <A> <B>`. Ключи записей, пути файлов, ключи локализации, GUI-типы и id
событий (верхние ключи events/), которые определяют оба мода.
"""
import argparse
import contextlib
import io
import sys

from v3run import v3

ap = argparse.ArgumentParser()
ap.add_argument("--a", required=True)
ap.add_argument("--b", required=True)
ap.add_argument("--limit", type=int, default=250)
ap.add_argument("--out", help="записать вывод в файл")
a = ap.parse_args()
args = ("conflicts", a.a, a.b, "--mods", a.a, a.b, "--limit", a.limit)
if not a.out:
    sys.exit(v3(*args))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    code = v3(*args)
open(a.out, "w", encoding="utf-8").write(buf.getvalue())
print(buf.getvalue().split("\n", 1)[0])
print("->", a.out)
sys.exit(code)
