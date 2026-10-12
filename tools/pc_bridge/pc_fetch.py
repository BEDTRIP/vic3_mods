"""Copy a text file from the PC to here through the bridge (read_text in parts).

Usage:  python3 tools/pc_bridge/pc_fetch.py <path on the bridge> <local file> [--step 40]

<path on the bridge> -- as read_text takes it (runs/<id>/..., docs/logs/...). For files made of short lines (JSON lines,
logs): read_text gives back a page of numbered lines; a page at a time until it is empty. Prints the lines copied.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    a = sys.argv[1:]
    step = int(a[a.index('--step') + 1]) if '--step' in a else 40
    remote, local = a[0], a[1]
    n = off = 0
    with open(local, 'w', encoding='utf-8') as out:
        while True:
            r = subprocess.run([sys.executable, os.path.join(HERE, 'pc_call.py'), 'call', 'read_text',
                                json.dumps({'path': remote, 'offset': off, 'limit': step})],
                               capture_output=True, text=True, encoding='utf-8').stdout
            rows = re.findall(r'^\s*(\d+)\t(.*)$', r, re.M)
            if not rows:
                break
            for _, line in rows:
                out.write(line + '\n')
                n += 1
            off = int(rows[-1][0])
            if len(rows) < step:
                break
    print(f'{n} lines -> {local}')


if __name__ == '__main__':
    main()
