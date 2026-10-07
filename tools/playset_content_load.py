"""Набор модов плейсета лаунчера → content_load.json игры (для прогона на другом наборе, `run_vic3_sandbox.ps1 -Playset`).

Игра берёт моды из `Documents/…/Victoria 3/content_load.json` (лаунчер пишет его при «Играть»), а не из активного
плейсета (6.10). Скрипт читает `launcher-v2.sqlite` только на чтение: включённые моды плейсета по `position`, их
`dirPath`.

  python tools/playset_content_load.py --playset "Ledgerdemain" --out <файл>
  python tools/playset_content_load.py --list
  python tools/playset_content_load.py --playset vanilla --out <файл>   # без модов: база для сравнения
"""
import argparse
import json
import os
import sqlite3
import sys

DB = os.path.join(os.environ.get("USERPROFILE", ""), "Documents", "Paradox Interactive", "Victoria 3",
                  "launcher-v2.sqlite")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--playset")
    ap.add_argument("--out")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    if args.playset == "vanilla":
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump({"enabledMods": [], "disabledDLC": [], "enabledUGC": []}, f, separators=(",", ":"))
        print("vanilla: без модов")
        return 0
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    if args.list:
        for name, active in con.execute("select name, isActive from playsets order by name"):
            print(("* " if active else "  ") + name)
        return 0
    row = con.execute("select id from playsets where name = ?", (args.playset,)).fetchone()
    if not row:
        print(f"no playset {args.playset!r}; --list shows them", file=sys.stderr)
        return 1
    mods = con.execute("select m.displayName, m.dirPath from playsets_mods pm join mods m on m.id = pm.modId "
                       "where pm.playsetId = ? and pm.enabled = 1 order by pm.position", (row[0],)).fetchall()
    data = {"enabledMods": [{"path": p} for _, p in mods], "disabledDLC": [], "enabledUGC": []}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{args.playset}: " + ", ".join(n for n, _ in mods))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
