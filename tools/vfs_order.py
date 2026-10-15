"""Кто выигрывает ключ и в каком порядке — обёртка над `v3 winner` (пакет vic3tools).

    py tools/vfs_order.py [--blocks blocks.json] common/buildings building_railway [ещё ключи]

То же напрямую: `v3 winner --set tools/blocks.json common/buildings building_railway`. Порядок — `load_order` из
blocks.json; у каждого определения — директива, файл:строка и что оно делает в цепочке.
"""
import argparse
import sys

from v3run import BLOCKS, v3

ap = argparse.ArgumentParser()
ap.add_argument("--blocks", default=BLOCKS)
ap.add_argument("category")
ap.add_argument("keys", nargs="+")
a = ap.parse_args()
sys.exit(v3("winner", "--set", a.blocks, a.category, *a.keys))
