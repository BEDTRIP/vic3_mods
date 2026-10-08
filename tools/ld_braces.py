"""Баланс фигурных скобок в файлах скрипта форка: перед коммитом и прогоном (8.10: лишняя `}` в ld_money_model.txt
сломала весь файл — модель не запустилась, r1008_133626).

    python tools/ld_braces.py [файл ...]        без файлов — изменённые в рабочем дереве форка и в последнем коммите

Комментарии `#` и строки в кавычках не считаются. Печатает файлы с ненулевым итогом или уходом в минус (строку);
код выхода 1, если такие есть. Ничего не меняет.
"""
import os
import re
import subprocess
import sys

FORK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Economic-and-Financial-Ledgerdemain-Mod")


def check(path):
    s = open(path, encoding="utf-8-sig", errors="replace").read()
    s = re.sub(r'"[^"\n]*"', '""', s)
    s = re.sub(r"#[^\n]*", "", s)
    depth, neg = 0, None
    for i, line in enumerate(s.split("\n"), 1):
        for ch in line:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth < 0 and neg is None:
                    neg = i
    return depth, neg


def changed():
    out = subprocess.run(["git", "-C", FORK, "diff", "--name-only", "HEAD~1"], capture_output=True, text=True).stdout
    out += subprocess.run(["git", "-C", FORK, "ls-files", "-o", "--exclude-standard"], capture_output=True, text=True).stdout
    return sorted({os.path.join(FORK, f) for f in out.split() if f.endswith((".txt", ".gui")) and not f.startswith("_archive")})


def main():
    files = sys.argv[1:] or changed()
    bad = 0
    for f in files:
        if not os.path.isfile(f):
            continue
        depth, neg = check(f)
        if depth or neg:
            bad += 1
            print(f"{os.path.relpath(f, FORK)}: итог {depth:+d}" + (f", минус со строки {neg}" if neg else ""))
    print(f"файлов {len(files)}, с ошибкой {bad}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
