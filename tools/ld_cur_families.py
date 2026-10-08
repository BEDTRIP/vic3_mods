"""Имена «по одной на валюту» в живых файлах форка (R3а, пользователь 8.10: одна переменная на всех + переменная
валюты, шильдики для всех тегов): каждое имя, в котором стоит ключ одной из валют E&F (`law_<cur>_currency`), сводится к
шаблону с `<cur>`; по шаблону — сколько валют, сколько упоминаний, в каких файлах и каким образом (задаётся /
читается скриптом / GUI и локализация / определение ключа).

    python tools/ld_cur_families.py [--top N] [--out <файл>] [--grep <шаблон>]

Ничего не меняет.
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ld_curdata  # noqa: E402

FORK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Economic-and-Financial-Ledgerdemain-Mod")
DIRS = ("common", "gui", "events", "localization/english")


def currencies():
    return ld_curdata.by_length()


def kind(line, name):
    l = line.split("#")[0]
    if re.search(r"(set_variable|set_global_variable|change_variable|change_global_variable|set_local_variable)\s*=\s*\{?\s*(name\s*=\s*)?" + re.escape(name) + r"\b", l):
        return "set"
    if re.search(r"(add_to_\w*list|value\s*=\s*flag:)\s*.*" + re.escape(name), l):
        return "list"
    if re.match(r"\s*" + re.escape(name) + r"\s*[:=]", l):
        return "def"
    return "read"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=80)
    ap.add_argument("--out")
    ap.add_argument("--grep")
    a = ap.parse_args()
    curs = currencies()
    cur_re = re.compile(r"(?<![a-z])(" + "|".join(curs) + r")(?![a-z])")
    word = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    fam = collections.defaultdict(lambda: {"curs": set(), "n": 0, "files": collections.Counter(), "kinds": collections.Counter()})
    for d in DIRS:
        for root, _, fs in os.walk(os.path.join(FORK, d)):
            for f in fs:
                if not f.endswith((".txt", ".gui", ".yml")):
                    continue
                p = os.path.join(root, f)
                rel = os.path.relpath(p, FORK)
                gui = f.endswith((".gui", ".yml"))
                for line in open(p, encoding="utf-8-sig", errors="replace"):
                    if line.lstrip().startswith("#"):
                        continue
                    for w in set(word.findall(line)):
                        m = cur_re.search(w)
                        if not m or w.startswith("law_") and w.endswith("_currency"):
                            continue
                        key = w[:m.start()] + "<cur>" + w[m.end():]
                        e = fam[key]
                        e["curs"].add(m.group(1))
                        e["n"] += 1
                        e["files"][rel] += 1
                        e["kinds"]["gui" if gui else kind(line, w)] += 1
    rows = sorted(fam.items(), key=lambda kv: -kv[1]["n"])
    if a.grep:
        rows = [r for r in rows if re.search(a.grep, r[0])]
    out = [f"валют {len(curs)}, шаблонов {len(rows)}, упоминаний {sum(e['n'] for _, e in rows)}"]
    for k, e in rows[:a.top]:
        kinds = ", ".join(f"{x} {v}" for x, v in e["kinds"].most_common())
        files = ", ".join(f"{os.path.basename(x)} {v}" for x, v in e["files"].most_common(3))
        out.append(f"{e['n']:7}  {len(e['curs']):3} вал.  {k}  [{kinds}]  {files}")
    text = "\n".join(out)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text + "\n")
    print(text)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
