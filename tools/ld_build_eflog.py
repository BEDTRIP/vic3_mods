"""Rebuild <run>/eflog.txt from the run's debug parts (as Close-And-Collect of tools/vic3_ui_lib.ps1 does).

Usage:  py tools/ld_build_eflog.py <run>

For a run whose collection was cut (the script stopped while writing eflog.txt): the parts <run>/dbgparts/*.log
(oldest first, by name) and <run>/debug.log, each part once (by its content), the mod's log lines (': EF?|') with the
prefix cut, into <run>/eflog.txt.
"""
import glob
import hashlib
import os
import re
import sys

LINE = re.compile(r'^.*?: (EF[A-Z]\|)')


def main():
    run = sys.argv[1]
    parts = sorted(glob.glob(os.path.join(run, 'dbgparts', '*.log')), key=os.path.basename)
    if os.path.exists(os.path.join(run, 'debug.log')):
        parts.append(os.path.join(run, 'debug.log'))
    seen = set()
    n = 0
    with open(os.path.join(run, 'eflog.txt'), 'w', encoding='utf-8') as out:
        for p in parts:
            h = hashlib.md5(open(p, 'rb').read()).hexdigest()
            if h in seen:
                continue
            seen.add(h)
            for ln in open(p, encoding='utf-8', errors='replace'):
                m = LINE.match(ln)
                if m and ': EF' in ln:
                    out.write(ln[m.start(1):])
                    n += 1
    print(f'{len(seen)} parts, {n} lines -> {os.path.join(run, "eflog.txt")}')


if __name__ == '__main__':
    main()
