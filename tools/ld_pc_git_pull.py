"""`git pull --ff-only` в рабочих копиях репо на ПК (vic3_mods и форк) — по просьбе пользователя, из облака через мост
(`py_tool ld_pc_git_pull`), чтобы документы подтянулись, например, в Syncthing.

    py tools/ld_pc_git_pull.py [--root <папка с репо>]

Корень по умолчанию — папка, где лежат `vic3_mods` и `Economic-and-Financial-Ledgerdemain-Mod` (рядом с `_bridge`, если
скрипт запущен из worktree моста, или рядом с самим репо). Только перемотка вперёд: локальные правки не прячет, ничего
не сбрасывает и не сливает — если git отказывает, печатает почему. Код выхода 1 — хотя бы один репо не подтянут.
"""
import argparse
import subprocess
import sys
from pathlib import Path

REPOS = (("vic3_mods", "main"), ("Economic-and-Financial-Ledgerdemain-Mod", "master"))


def default_root():
    here = Path(__file__).resolve().parents[1]          # tools/.. — repo or the bridge's worktree
    for cand in (here.parent, here.parent.parent):      # Projects/vic3 (main checkout) or Projects/vic3 above _bridge/wt
        if (cand / "vic3_mods" / ".git").exists():
            return cand
    return here.parent


def git(repo, *args):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout + p.stderr).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    a = ap.parse_args()
    root = Path(a.root) if a.root else default_root()
    failed = 0
    for name, want in REPOS:
        repo = root / name
        print(f"== {repo}")
        if not (repo / ".git").exists():
            print("  нет репо"); failed += 1; continue
        _, branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD")
        _, dirty = git(repo, "status", "--porcelain")
        _, before = git(repo, "log", "-1", "--format=%h %s")
        print(f"  ветка {branch} (ожидается {want}); было: {before}")
        if dirty:
            print(f"  локальные изменения ({len(dirty.splitlines())}):")
            for line in dirty.splitlines()[:20]:
                print("   ", line)
        if branch != want:
            print(f"  не та ветка — не трогаю"); failed += 1; continue
        code, out = git(repo, "pull", "--ff-only", "origin", want)
        print("  " + out.replace("\n", "\n  ")[-3000:])
        _, after = git(repo, "log", "-1", "--format=%h %s")
        print(f"  стало: {after}")
        if code:
            failed += 1
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
