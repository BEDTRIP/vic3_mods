"""Живая копия форка «E&F: Ledgerdemain» = рабочее дерево форка (локальный режим; из облака — `sync_fork` моста).

Копирует новые и изменённые файлы форка в `Documents/…/Victoria 3/mod/E&F Ledgerdemain`, файлы, которых в форке
больше нет, переносит в `_to_delete/<дата>/` живой копии (правило проекта). `.git` и `_to_delete` не трогает.
Пока игра идёт — отказывается (в -debug_mode игра перечитывает файлы на лету).

  python tools/ld_sync_live.py [--fork <папка>] [--dry]
"""
import argparse
import datetime
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORK = ROOT / "Economic-and-Financial-Ledgerdemain-Mod"
LIVE = Path(os.environ.get("USERPROFILE", "")) / "Documents" / "Paradox Interactive" / "Victoria 3" / "mod" / "E&F Ledgerdemain"
# документация и история форка — агенту и пользователю, не игре: docs/, понятия/, ваниль/, история/, _archive/, план,
# решения, схема, CLAUDE.md, настройки Claude и Obsidian
SKIP = (".git", "_to_delete", "docs", "_archive", "понятия", "ваниль", "история", ".claude", ".obsidian",
        "CLAUDE.md", "план.md", "решения.md", "схема.md")


def game_running():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq victoria3.exe"], capture_output=True, text=True).stdout
    return "victoria3.exe" in out.lower()


def sync(src, dst, dry=False):
    copied, moved = [], []
    for f in src.rglob("*"):
        rel = f.relative_to(src)
        if f.is_file() and rel.parts[0] not in SKIP:
            t = dst / rel
            if not t.exists() or t.read_bytes() != f.read_bytes():
                if not dry:
                    t.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, t)
                copied.append(rel.as_posix())
    bin_ = dst / "_to_delete" / f"{datetime.date.today():%Y-%m-%d}"
    for t in list(dst.rglob("*")):
        rel = t.relative_to(dst)
        if t.is_file() and rel.parts[0] not in SKIP and not (src / rel).exists():
            if not dry:
                (bin_ / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.move(t, bin_ / rel)
            moved.append(rel.as_posix())
    return copied, moved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fork", default=str(FORK))
    ap.add_argument("--live", default=str(LIVE))
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    if not args.dry and game_running():
        raise SystemExit("the game is running: the live copy is not synced during a run")
    copied, moved = sync(Path(args.fork), Path(args.live), args.dry)
    print(f"copied {len(copied)}, moved to _to_delete {len(moved)}")
    for r in (copied + moved)[:40]:
        print("  ", r)


if __name__ == "__main__":
    main()
