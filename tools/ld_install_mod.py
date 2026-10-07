"""Положить папку репозитория модом в Documents/…/Victoria 3/mod/<имя> (оптимизация: моды для замеров).

    python tools/ld_install_mod.py <папка в репо> "<имя мода>"

Папка мода заменяется целиком (только если её нет или в ней лежит .metadata/metadata.json с тем же id).
Для форка — ld_sync_live.py; это — для служебных модов вроде tools/ld_profiler_view.
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODS = os.path.join(os.environ.get("USERPROFILE", ""), "Documents", "Paradox Interactive", "Victoria 3", "mod")


def mod_id(d):
    p = os.path.join(d, ".metadata", "metadata.json")
    return json.load(open(p, encoding="utf-8-sig"))["id"] if os.path.exists(p) else None


def main():
    src = os.path.join(HERE, "..", sys.argv[1])
    dst = os.path.join(MODS, sys.argv[2])
    if os.path.exists(dst) and mod_id(dst) != mod_id(src):
        print(f"{dst}: другой мод, не трогаю")
        return 1
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print(f"{dst}: {sum(len(f) for _, _, f in os.walk(dst))} файлов")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
