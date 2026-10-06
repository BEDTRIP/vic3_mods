"""Отличия файлов форка от ванили (ФК2, шаг 4): копии ванильных GUI в `gui/ef_dev_and_custom_windows/maj/`.

    python tools/ld_vanilla_diff.py <путь в форке> [<путь в ванили>] [--hunks N]

Путь в ванили по умолчанию — `gui/<имя файла>` (если нет — ищется по имени во всей `game/gui`). Ваниль —
`../vic3_mods_out/.vanillaVIC3/game` (на ПК; в облаке её нет — запуск через `py_tool` моста). Сравнение без учёта
пробелов и концов строк; печатает число строк, отличий, строки форка с признаками E&F (`GetScriptedGui`, `GetCustom`,
`ScriptValue`, `ef`, `EF`, `zz_ef`, `currency`) среди отличий и первые N кусков diff. Ничего не меняет.
"""
import argparse
import difflib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ld_gen  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
VAN = os.path.normpath(os.path.join(HERE, "..", "..", "vic3_mods_out", ".vanillaVIC3"))
EF = re.compile(r"GetScriptedGui|GetCustom|ScriptValue|zz_ef|\bef_|_ef_|EF_|currency|E&F", re.I)


def read(p):
    with open(p, encoding="utf-8-sig", errors="replace") as f:
        return [re.sub(r"\s+", " ", l).strip() for l in f.read().splitlines()]


def find_vanilla(name):
    for root in (os.path.join(VAN, "game", "gui"), os.path.join(VAN, "gui")):
        for dp, _, fn in os.walk(root):
            if name in fn:
                return os.path.join(dp, name)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fork")
    ap.add_argument("vanilla", nargs="?")
    ap.add_argument("--hunks", type=int, default=6)
    a = ap.parse_args()
    fp = os.path.join(ld_gen.FORK, a.fork)
    vp = os.path.join(VAN, a.vanilla) if a.vanilla else find_vanilla(os.path.basename(a.fork))
    if not vp or not os.path.exists(vp):
        sys.exit(f"нет ванильного файла для {a.fork} (ваниль: {VAN})")
    f, v = read(fp), read(vp)
    sm = difflib.SequenceMatcher(None, v, f, autojunk=False)
    ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
    added = [l for t, i1, i2, j1, j2 in ops for l in f[j1:j2]]
    removed = [l for t, i1, i2, j1, j2 in ops for l in v[i1:i2]]
    ef = [l for l in added if EF.search(l)]
    print(f"{a.fork} vs {os.path.relpath(vp, VAN)}: строк форк {len(f)}, ваниль {len(v)}, кусков {len(ops)}, "
          f"строк только в форке {len(added)}, только в ванили {len(removed)}, из них с признаками E&F {len(ef)}")
    for l in ef[:15]:
        print("  EF:", l[:200])
    for t, i1, i2, j1, j2 in ops[:a.hunks]:
        print(f"--- {t} ваниль {i1 + 1}-{i2} / форк {j1 + 1}-{j2}")
        for l in v[i1:i2][:6]:
            print("  -", l[:160])
        for l in f[j1:j2][:6]:
            print("  +", l[:160])


if __name__ == "__main__":
    main()
