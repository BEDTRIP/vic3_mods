"""Наши REPLACE: / TRY_REPLACE:, в теле которых нет полей заменяемой записи — обёртка над `v3 audit replace`.

    py tools/replace_audit.py [папка компача …]

REPLACE: заменяет запись целиком (решено 24.09.2026) — каждое пропущенное поле теряется. Без аргументов проверяет все
наши папки из `load_order` blocks.json (что лежит в этом репо), каждую против набора blocks.json. Намеренные пропуски —
`tools/replace_declared.toml` (МП.7). То же напрямую: `v3 audit replace <мод> --set tools/blocks.json --declared
tools/replace_declared.toml`.
"""
import json
import os
import sys

from v3run import BLOCKS, HERE, v3

REPO = os.path.dirname(HERE)
cfg = json.load(open(BLOCKS, encoding="utf-8-sig"))
base = os.path.dirname(BLOCKS)
ours = sys.argv[1:] or [p for p in cfg["load_order"]
                        if os.path.abspath(os.path.join(base, p)).startswith(REPO + os.sep)]
worst = 0
for p in ours:
    full = p if os.path.isabs(p) else os.path.join(base, p)
    if not os.path.isdir(full):
        print(f"нет папки: {p}")
        continue
    worst = max(worst, v3("audit", "replace", full, "--set", BLOCKS, "--declared",
                          os.path.join(HERE, "replace_declared.toml"), "--limit", 400))
sys.exit(worst)
