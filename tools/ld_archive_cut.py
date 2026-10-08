"""Перенос верхнеуровневых записей форка в `_archive/<механизм>/` (правила `CLAUDE.md` форка, «Мёртвое»).

    python tools/ld_archive_cut.py <механизм> --re '<регулярка ключа>' [--re …] [--keys <файл со списком>]
                                   [--files <glob под common/>] [--dry]

Ключ записи (`ld_pdx.parse`) целиком подходит под одну из регулярок или есть в списке → запись (с комментариями
вплотную над ней) вырезается из живого файла и дописывается в `_archive/<механизм>/<тот же путь>` (в начале файла
архива — откуда). Затем — оставшиеся упоминания вырезанных имён в живых файлах (`common`, `events`, `gui`,
`localization`): их снимать отдельно и записывать в README механизма. `--dry` — только список.
"""
import argparse
import glob
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ld_pdx  # noqa: E402

FORK = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                                     "Economic-and-Financial-Ledgerdemain-Mod"))
LIVE = ("common", "events", "gui", "localization")
WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mech")
    ap.add_argument("--re", action="append", default=[])
    ap.add_argument("--keys")
    ap.add_argument("--files", default="**/*.txt")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    pats = [re.compile(p) for p in a.re]
    keys = set(open(a.keys, encoding="utf-8").read().split()) if a.keys else set()
    cut = {}
    lines = Counter()
    for path in sorted(glob.glob(os.path.join(FORK, "common", a.files), recursive=True)):
        rel = os.path.relpath(path, FORK).replace("\\", "/")
        text, bom, eol = ld_pdx.read(path)
        ents, _ = ld_pdx.parse(text)
        hit = [e for e in ents if e.key in keys or any(p.fullmatch(e.key) for p in pats)]
        if not hit:
            continue
        pieces, out, pos = [], [], 0
        for e in hit:
            s, t = e.lead, e.end
            while t < len(text) and text[t] in " \t":
                t += 1
            if t < len(text) and text[t] == "\n":
                t += 1
            pieces.append(text[s:t])
            out.append(text[pos:s])
            pos = t
            cut[e.key] = rel
            lines[rel] += text[s:t].count("\n")
        out.append(text[pos:])
        if not a.dry:
            ld_pdx.write(path, "".join(out), bom=bom, eol=eol)
            dst = os.path.join(FORK, "_archive", a.mech, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            old = open(dst, encoding="utf-8-sig").read() if os.path.exists(dst) else f"# From {rel}.\n\n"
            ld_pdx.write(dst, old.rstrip("\n") + "\n\n" + "".join(pieces), bom=bom, eol=eol)
    print(f"записей {len(cut)}, строк {sum(lines.values())}")
    for rel, n in sorted(lines.items()):
        print(f"  {rel}: {n} строк")
    left = defaultdict(Counter)
    for top in LIVE:
        for path in glob.glob(os.path.join(FORK, top, "**", "*"), recursive=True):
            if not os.path.isfile(path) or not path.endswith((".txt", ".gui", ".yml")):
                continue
            rel = os.path.relpath(path, FORK).replace("\\", "/")
            text = open(path, encoding="utf-8-sig", errors="replace").read()
            if a.dry:
                text = "\n".join(l for l in text.split("\n"))
            for w in WORD.findall(text):
                if w in cut:
                    left[w][rel] += 1
    if a.dry:
        print("(--dry: упоминания считаются вместе с самими записями)")
    print(f"упоминаний вырезанных имён в живых файлах: {sum(sum(c.values()) for c in left.values())} ({len(left)} имён)")
    byfile = Counter()
    for w, c in left.items():
        for f, n in c.items():
            byfile[f] += n
    for f, n in byfile.most_common():
        names = sorted(w for w in left if f in left[w])
        print(f"  {f}: {n} — " + ", ".join(names[:8]) + (" …" if len(names) > 8 else ""))


if __name__ == "__main__":
    main()
