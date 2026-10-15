"""Устаревшие полные тела мода: записи с полным телом без полей, которые есть у ванили — обёртка над `v3 audit stale`.

    py tools/stale_bodies.py <папка мода> [строк на вывод]

То же напрямую: `v3 audit stale <мод> --set tools/blocks.json`. Ванилью служит первая папка `load_order` из
blocks.json. Не считаются defines, on_actions и history. Пропущенное поле — либо новое в игре (вернуть, см. TGR.3 /
`regen_tgr_113_fix.py`), либо переделка автора (оставить).
"""
import sys

from v3run import BLOCKS, v3

if len(sys.argv) < 2:
    sys.exit(__doc__)
limit = sys.argv[2] if len(sys.argv) > 2 else 200
sys.exit(v3("audit", "stale", sys.argv[1], "--set", BLOCKS, "--limit", limit))
