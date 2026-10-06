"""ФК1: сверка переноса хотфикса — итоговое определение каждого ключа common/ в форке то же, что было с хотфиксом.

Собирает оба набора по правилам загрузки и сравнивает итог по каждому (папка, ключ):
  база — ваниль, CMF, ETF, PSC, E&F, хотфикс (порядок плейсета «база хотфикс»);
  форк — ваниль, CMF, ETF, форк.
Правила (`Правила работы с модами Victoria 3.md`): файл по тому же пути у позднего мода заменяет ранний; файлы папки
грузятся по имени (ASCII, по всем модам сразу); голый повтор ключа переопределяет, кроме scripted_effects /
scripted_triggers / script_values (там действует первое); on_actions складываются; REPLACE / REPLACE_OR_CREATE заменяют,
INJECT вливается (`ld_port_hotfix.inject_merge`). Сравнение — по токенам без комментариев и пробелов.

  python tools/ld_verify_port.py [--fork <папка>] [--limit N]

Вывод — `_tmp_analysis/ld_verify_report.md`; код выхода 1, если есть расхождения.
"""
import argparse
import os
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ld_pdx  # noqa: E402
import re  # noqa: E402
from ld_port_hotfix import (ADDITIVE, FIRST_WINS, FORK, GUI_TYPE, HF, INJECTS, OUT, REPLACES, ROOT,  # noqa: E402
                            SKIP_DIRS, TR, gui_block_end, inject_merge, ld_name)

REPORT = ROOT / "_tmp_analysis" / "ld_verify_report.md"
BASE_MODS = [OUT / ".vanillaVIC3", OUT / "_cmf", OUT / "_etf", OUT / "PSC", OUT / "E&F", TR, HF]
LOC_FULL = re.compile(r'^\s*([\w.\-]+):\d*\s*"(.*)"\s*(?:#.*)?$')


def vfs(mods):
    """{папка: [(имя файла, путь)]} по правилу «поздний мод заменяет файл по тому же пути»."""
    files = {}
    for m in mods:
        for p in (m / "common").rglob("*.txt"):
            r = p.relative_to(m).as_posix()
            if not any(r.startswith(s + "/") for s in SKIP_DIRS):
                files[r] = p
    by = defaultdict(list)
    for r, p in files.items():
        by[r.rsplit("/", 1)[0]].append((r.rsplit("/", 1)[1], p))
    return by


def resolve(mods, folders):
    """{(папка, ключ): текст записи `ключ = …`} — итог после загрузки."""
    by = vfs(mods)
    state = {}
    for folder in folders:
        for _, p in sorted(by.get(folder, []), key=lambda x: x[0]):
            text = ld_pdx.read(p)[0]
            for e in ld_pdx.parse(text)[0]:
                k = (folder, e.key)
                body = text[e.start:e.end]
                if e.directive:
                    body = body.split(":", 1)[1]                  # `ключ = …` без директивы
                has = k in state
                if not e.directive:
                    if has and folder in FIRST_WINS:
                        continue
                    if has and folder in ADDITIVE and e.is_block:
                        state[k] = merge(state[k], body)
                        continue
                    state[k] = body
                elif e.directive in REPLACES:
                    if has or e.directive == "REPLACE_OR_CREATE":
                        state[k] = body
                elif e.directive in INJECTS:
                    if has and e.is_block:
                        state[k] = merge(state[k], body)
                    elif not has and e.directive == "INJECT_OR_CREATE":
                        state[k] = body
                else:
                    state[k] = body
    return state


def files_vfs(mods, sub, exts):
    files = {}
    for m in mods:
        if (m / sub).exists():
            for p in (m / sub).rglob("*"):
                if p.is_file() and p.suffix in exts:
                    files[p.relative_to(m).as_posix()] = p
    return files


def resolve_gui(mods, path_map):
    """{тип: текст} — тип регистрирует первый файл по имени (ASCII, по всем модам)."""
    files = files_vfs(mods, "gui", (".gui",))
    out = {}
    for r, p in sorted(files.items(), key=lambda x: (x[0].rsplit("/", 1)[1], x[0])):
        text = ld_pdx.read(p)[0]
        for m in GUI_TYPE.finditer(text):
            if m.group(1) not in out:
                end = gui_block_end(text, m.end())
                t = text[m.start():end]
                for old, new in path_map.items():
                    t = t.replace(old, new)
                out[m.group(1)] = t
    return out


def resolve_loc(mods, keys=None):
    """{(язык, ключ): значение} — файлы replace/ раньше всех, дальше первый файл по имени."""
    files = files_vfs(mods, "localization", (".yml",))
    out = {}
    order = sorted(files.items(), key=lambda x: ("/replace/" not in x[0], x[0].rsplit("/", 1)[1], x[0]))
    for r, p in order:
        lang = r.split("/")[1]
        for line in ld_pdx.read(p)[0].split("\n"):
            m = LOC_FULL.match(line)
            if m and (keys is None or m.group(1) in keys) and (lang, m.group(1)) not in out:
                out[(lang, m.group(1))] = m.group(2)
    return out


def compare(a, b):
    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))
    diff = sorted(k for k in set(a) & set(b) if ld_pdx.norm(a[k]) != ld_pdx.norm(b[k]))
    return only_a, only_b, diff


def merge(cur, inj):
    ce = ld_pdx.parse(cur)[0]
    ie = ld_pdx.parse(inj)[0]
    if not ce or not ie or not ce[0].is_block:
        return cur
    return inject_merge(cur, ce[0], inj, ie[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fork", default=str(FORK))
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args()
    fork = Path(args.fork)
    fork_mods = [OUT / ".vanillaVIC3", OUT / "_cmf", OUT / "_etf", fork]

    folders = set()
    for m in (OUT / "PSC", OUT / "E&F", HF, fork):
        for p in (m / "common").rglob("*.txt"):
            f = p.relative_to(m).as_posix().rsplit("/", 1)[0]
            if not any(f == s or f.startswith(s + "/") for s in SKIP_DIRS):
                folders.add(f)
    folders = sorted(folders)

    a = resolve(BASE_MODS, folders)
    b = resolve(fork_mods, folders)
    # GUI: пути переименованных файлов хотфикса в базе — как в форке
    path_map = {}
    for p in (HF / "gui").rglob("*"):
        r = p.relative_to(HF).as_posix()
        if p.is_file() and not any((m / r).exists() for m in BASE_MODS[:5]):
            path_map[r] = r.rsplit("/", 1)[0] + "/" + ld_name(p.name)
    ga, gb = resolve_gui(BASE_MODS, path_map), resolve_gui(fork_mods, {})
    for k in set(ga) | set(gb):
        a[("gui", k)] = ga.get(k)
        b[("gui", k)] = gb.get(k)
    # локализация: ключи, которые определяют E&F, PSC, перевод, хотфикс или форк
    ours = set()
    for m in (OUT / "PSC", OUT / "E&F", TR, HF, fork):
        for p in (m / "localization").rglob("*.yml"):
            for line in ld_pdx.read(p)[0].split("\n"):
                mm = LOC_FULL.match(line)
                if mm:
                    ours.add(mm.group(1))
    la, lb = resolve_loc(BASE_MODS, ours), resolve_loc(fork_mods, ours)
    for k in set(la) | set(lb):
        a[("loc " + k[0], k[1])] = la.get(k)
        b[("loc " + k[0], k[1])] = lb.get(k)
    a = {k: v for k, v in a.items() if v is not None}
    for k, v in a.items():
        for old, new in path_map.items():
            v = v.replace(old, new)
        a[k] = v
    b = {k: v for k, v in b.items() if v is not None}
    only_a, only_b, diff = compare(a, b)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as o:
        o.write("# Сверка переноса хотфикса (ФК1) — `ld_verify_port.py`\n\n")
        o.write(f"ключей: база {len(a)}, форк {len(b)}; только в базе {len(only_a)}, только в форке {len(only_b)}, "
                f"разное определение {len(diff)}\n")
        for title, keys in (("только в базе", only_a), ("только в форке", only_b)):
            o.write(f"\n## {title} ({len(keys)})\n\n")
            for f, k in keys:
                o.write(f"- {f} | {k}\n")
        o.write(f"\n## разное определение ({len(diff)})\n")
        for f, k in diff:
            ta, tb = ld_pdx.norm(a[(f, k)]), ld_pdx.norm(b[(f, k)])
            i = next((j for j in range(min(len(ta), len(tb))) if ta[j] != tb[j]), min(len(ta), len(tb)))
            o.write(f"\n### {f} | {k}\n\nбаза: `…{ta[max(0, i - 80):i + 160]}`\n\nфорк: `…{tb[max(0, i - 80):i + 160]}`\n")
    print(f"keys: base {len(a)}, fork {len(b)}; only base {len(only_a)}, only fork {len(only_b)}, different {len(diff)}")
    for f, k in (only_a + only_b + diff)[:args.limit]:
        print("  ", f, "|", k)
    print(REPORT)
    return 1 if (only_a or only_b or diff) else 0


if __name__ == "__main__":
    raise SystemExit(main())
