"""Матрица пересечений блоков набора — обёртка над `v3 matrix` / `v3 conflicts` (пакет vic3tools).

    py tools/pair_matrix.py [--blocks blocks.json] [--pair "A,B"] [--limit N] [--rebuild]

То же напрямую: `v3 matrix --groups tools/blocks.json`, `v3 conflicts A B --groups tools/blocks.json`. Считает ключи
записей и пути файлов, которые определяют ОБА блока; аддитивные папки (on_actions, history…) не считаются. Чего не
видит — нового содержимого одного мода, о котором другой не знает: для этого `content_holes.py`.
"""
import argparse
import sys

from v3run import BLOCKS, v3

ap = argparse.ArgumentParser()
ap.add_argument("--blocks", default=BLOCKS)
ap.add_argument("--pair", help='один блок против другого: "A,B"')
ap.add_argument("--limit", type=int, default=25)
ap.add_argument("--rebuild", action="store_true")
a = ap.parse_args()
extra = ["--rebuild"] if a.rebuild else []
if a.pair:
    x, y = [s.strip() for s in a.pair.split(",", 1)]
    sys.exit(v3("conflicts", x, y, "--groups", a.blocks, "--limit", a.limit, *extra))
sys.exit(v3("matrix", "--groups", a.blocks, *extra))
