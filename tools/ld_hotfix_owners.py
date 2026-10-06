"""ФК1, шаг анализа: чьё каждое определение хотфикса E&F.

Для каждого верхнеуровневого определения в common/ хотфикса (с директивой REPLACE_OR_CREATE / REPLACE / INJECT /
TRY_INJECT / INJECT_OR_CREATE или без неё) ищет, кто ещё определяет тот же ключ в той же папке: E&F, PSC, ваниль,
CMF, ETF. Итог — куда это определение переедет в форке.

  python tools/ld_hotfix_owners.py [--out <файл.md>]

Классы:
  ef        — ключ определён в E&F: правка вносится в тело E&F (тот же файл, то же место)
  psc       — ключ PSC (и не E&F): правка в файл PSC внутри форка
  vanilla   — ключ ванили / CMF / ETF: остаётся переопределением (директива) в файле ld_*
  new       — ключ нигде больше не определён: новый, переезжает как есть (файл ld_*)
  multi     — ключ определён и в E&F, и в PSC: разбирать руками
"""
import argparse
import os
import re
from collections import Counter, defaultdict

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "vic3_mods_out")
HOTFIX = os.path.join(ROOT, "vic3_mods", "_ef", "ef hotfix 1.13")
SOURCES = {
    "ef": os.path.join(OUT, "E&F"),
    "psc": os.path.join(OUT, "PSC"),
    "vanilla": os.path.join(OUT, ".vanillaVIC3"),
    "cmf": os.path.join(OUT, "_cmf"),
    "etf": os.path.join(OUT, "_etf"),
}
CLASSES = ("ef", "psc", "vanilla", "new", "multi")
DIRECTIVES = ("REPLACE_OR_CREATE", "REPLACE", "INJECT", "TRY_INJECT", "INJECT_OR_CREATE", "TRY_REPLACE", "CREATE")
# Папки, где верхний уровень — не база объектов с ключами.
SKIP_DIRS = {"common/history", "common/defines"}

TOKEN = re.compile(r'#[^\n]*|"(?:[^"\\\n]|\\.)*"|[{}=]|[^\s{}=#"]+')


def split_directive(key):
    if ":" in key and key.split(":", 1)[0] in DIRECTIVES:
        d, key = key.split(":", 1)
        return d, key
    return None, key


def top_level(path):
    """[(директива, ключ, строка)] для определений верхнего уровня файла (блоки и скаляры)."""
    try:
        text = open(path, encoding="utf-8-sig", errors="replace").read()
    except OSError:
        return []
    out, depth = [], 0
    toks = [(m.group(0), m.start()) for m in TOKEN.finditer(text) if not m.group(0).startswith("#")]
    for i, (t, pos) in enumerate(toks):
        if t == "{":
            depth += 1
        elif t == "}":
            depth = max(0, depth - 1)
        elif depth == 0 and t == "=" and i > 0 and i + 1 < len(toks):
            key, kpos = toks[i - 1]
            if key in "{}=":
                continue
            d, key = split_directive(key)
            out.append((d, key, text.count("\n", 0, kpos) + 1))
    return out


def scan(root):
    """{папка: {ключ: [(файл, строка, директива)]}} по common/ мода."""
    idx = defaultdict(lambda: defaultdict(list))
    for d, _, files in os.walk(os.path.join(root, "common")):
        rel_dir = os.path.relpath(d, root).replace("\\", "/")
        if any(rel_dir == s or rel_dir.startswith(s + "/") for s in SKIP_DIRS):
            continue
        for f in sorted(files):
            if f.endswith(".txt"):
                p = os.path.join(d, f)
                for dr, key, line in top_level(p):
                    idx[rel_dir][key].append((os.path.relpath(p, root).replace("\\", "/"), line, dr))
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "_tmp_analysis", "ld_hotfix_owners.md"))
    args = ap.parse_args()

    src = {k: scan(v) for k, v in SOURCES.items()}
    hf = scan(HOTFIX)

    rows, cls_count, dir_count = [], Counter(), Counter()
    by_dir = defaultdict(Counter)
    for folder in sorted(hf):
        for key, defs in sorted(hf[folder].items()):
            owners = [k for k in SOURCES if key in src[k].get(folder, {})]
            if "ef" in owners and "psc" in owners:
                cls = "multi"
            elif "ef" in owners:
                cls = "ef"
            elif "psc" in owners:
                cls = "psc"
            elif owners:
                cls = "vanilla"
            else:
                cls = "new"
            where = "; ".join(f"{k}:{src[k][folder][key][0][0]}" for k in owners)
            for f, line, dr in defs:
                cls_count[cls] += 1
                dir_count[dr or "-"] += 1
                by_dir[folder][cls] += 1
                rows.append((cls, folder, key, dr or "-", f"{f}:{line}", where))

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as o:
        o.write("# Хотфикс E&F → форк: чьё каждое определение (ФК1)\n\n")
        o.write("Сгенерировано `tools/ld_hotfix_owners.py`; классы — в его докстринге.\n\n")
        o.write("| класс | определений |\n| --- | --- |\n")
        for c in CLASSES:
            o.write(f"| {c} | {cls_count[c]} |\n")
        o.write("\n| директива | определений |\n| --- | --- |\n")
        for d, n in dir_count.most_common():
            o.write(f"| {d} | {n} |\n")
        o.write("\n## По папкам\n\n| папка | " + " | ".join(CLASSES) + " |\n| --- |" + " --- |" * len(CLASSES) + "\n")
        for folder in sorted(by_dir):
            o.write(f"| {folder} | " + " | ".join(str(by_dir[folder][c]) for c in CLASSES) + " |\n")
        o.write("\n## Все определения\n\n| класс | папка | ключ | директива | хотфикс | владельцы |\n")
        o.write("| --- | --- | --- | --- | --- | --- |\n")
        for r in sorted(rows):
            o.write("| " + " | ".join(r) + " |\n")
    print("classes:", {c: cls_count[c] for c in CLASSES})
    print("directives:", dict(dir_count))
    print(args.out)


if __name__ == "__main__":
    main()
