"""Ключи локализации наших модов, которые никогда не покажутся — обёртка над `v3 audit loc-dead`.

Локализация — «первый определивший побеждает»: ключ нашего файла вне `localization/<язык>/replace/`, который раньше
определяет ваниль или мод выше по списку под другим путём, мёртв. Исправление — перенести в `replace/`.

EARLIER — моды, которые грузятся раньше наших компачей (порядок content_load.json); OURS — что проверять.
    py tools/loc_dead_overrides.py
"""
import os
import sys

from v3run import v3

W = r'C:\Games\Steam\steamapps\workshop\content\529340'
EARLIER = [  # без ванили: её `v3` ставит первой сам
    os.path.join(W, '3143591632'),  # E&F
    os.path.join(W, '3520140574'),  # E&F RUS
    r'C:\Users\Andrey\Projects\vic3\vic3_mods_out\PSC',
    r'C:\Users\Andrey\Projects\vic3\vic3_mods_out\TheGreatRevision',
]
OURS = [
    r'C:\Users\Andrey\Projects\vic3\vic3_mods\_ef\ef hotfix 1.13',  # ef+psc внутри хотфикса с 02.10 (STR.6)
    r'C:\Users\Andrey\Projects\vic3\vic3_mods\_ef\ef+tgr done',
]
worst = 0
for ours in OURS:
    worst = max(worst, v3("audit", "loc-dead", ours, "--mods", *EARLIER, ours))
sys.exit(worst)
