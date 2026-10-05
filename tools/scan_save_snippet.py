"""Print pieces of a save around a regex, for reading its structure (этап 2).

Usage:  py tools/scan_save_snippet.py <save> <regex> [--after N] [--before N] [--max K] [--from TEXT]

--from TEXT: start searching at the first occurrence of TEXT (e.g. "\\nmarket_manager={").
Prints up to K matches (default 3), each with N chars after (default 1500) and before (default 200).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import save_ownership as SO  # noqa: E402


def opt(args, name, default, cast):
    if name in args:
        i = args.index(name); v = cast(args[i + 1]); del args[i:i + 2]; return v
    return default


def main():
    args = sys.argv[1:]
    after = opt(args, '--after', 1500, int)
    before = opt(args, '--before', 200, int)
    k = opt(args, '--max', 3, int)
    start = opt(args, '--from', None, str)
    path, pat = args[0], args[1]
    if not os.path.isabs(path):
        path = os.path.join(SO.SG, path)
    s = open(path, 'rb').read().decode('utf-8', 'replace')
    pos = 0
    if start:
        pos = s.find(start.encode().decode('unicode_escape'))
        print(f'--from at {pos}')
        if pos < 0:
            return
    n = 0
    for m in re.compile(pat).finditer(s, pos):
        print(f'=== match at {m.start()}')
        print(s[max(0, m.start() - before):m.start() + after])
        n += 1
        if n >= k:
            break
    if not n:
        print('no match')


if __name__ == '__main__':
    main()
