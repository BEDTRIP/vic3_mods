"""A country's script variables and variable maps from a save, read as numbers.

Usage:  py tools/save_vars.py <save> <TAG> [regex] [--raw REGEX] [--global]

<save>   a file in "save games" or a full path (text saves, as in -debug_mode)
<TAG>    country tag (GBR); its variables and maps whose name matches [regex] (default: all)
--raw    also print the country block's own lines matching REGEX (budget, debt: "principal|money|credit")
--global the global variables matching [regex] instead of a country's

Values: type=value identity / 100000; a country key or value -- its tag; maps -- one line per key.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import save_ownership as SO  # noqa: E402

DIV = 100000


def opt(args, name, default):
    if name in args:
        i = args.index(name); v = args[i + 1]; del args[i:i + 2]; return v
    return default


def block(s, start):
    """The text of the brace block opening at s[start] == '{'."""
    d = 0
    for i in range(start, len(s)):
        c = s[i]
        if c == '{':
            d += 1
        elif c == '}':
            d -= 1
            if d == 0:
                return s[start:i + 1]
    return s[start:]


def val(kind, ident, tags):
    if kind == 'value':
        return '%.5g' % (int(ident or 0) / DIV)
    if kind == 'ctry':
        return tags.get(ident, 'ctry:' + str(ident))
    if kind == 'boolean':
        return 'yes' if ident else 'no'
    return '%s:%s' % (kind, ident)


def dump_vars(text, pat, tags):
    v = re.search(r'\bvariables=\{', text)
    if not v:
        print('  (no variables)'); return
    vb = block(text, v.end() - 1)
    for m in re.finditer(r'flag=(\w+)\s+(?:tick=\d+\s+)?data=\{\s*type=(\w+)\s*(?:identity=(-?\d+))?', vb):
        if pat.search(m.group(1)):
            print('  %s = %s' % (m.group(1), val(m.group(2), m.group(3), tags)))
    for m in re.finditer(r'name="(\w+)"\s*list=\{', vb):
        if not pat.search(m.group(1)):
            continue
        lb = block(vb, m.end() - 1)
        rows = re.findall(r'key=\{\s*type=(\w+)\s*(?:identity=(-?\d+))?\s*\}\s*value=\{\s*type=(\w+)\s*(?:identity=(-?\d+))?', lb)
        print('  map %s (%d):' % (m.group(1), len(rows)))
        for kk, ki, vk, vi in rows:
            print('    %s = %s' % (val(kk, ki, tags), val(vk, vi, tags)))


def main():
    args = sys.argv[1:]
    raw = opt(args, '--raw', None)
    glob = '--global' in args
    if glob:
        args.remove('--global')
    path, tag = args[0], args[1]
    pat = re.compile(args[2] if len(args) > 2 else '.')
    if not os.path.isabs(path):
        path = os.path.join(SO.SG, path)
    s = open(path, 'rb').read().decode('utf-8', 'replace')
    print('date', re.search(r'\ndate=([\d.]+)', s).group(1))
    cm = SO.section(s, 'country_manager')
    heads = list(re.finditer(r'\n(\d+)=\{\n(?:\t[^\n]*\n){0,3}?\tdefinition="(\w+)"', cm))
    tags = {m.group(1): m.group(2) for m in heads}
    if glob:
        g = s.find('\nvariables={')
        if g < 0:
            print('no global variables'); return
        dump_vars('variables=' + block(s, g + len('\nvariables=')), pat, tags)
        return
    for i, m in enumerate(heads):
        if m.group(2) != tag:
            continue
        end = heads[i + 1].start() if i + 1 < len(heads) else len(cm)
        text = cm[m.start():end]
        print('country %s id %s' % (tag, m.group(1)))
        if raw:
            r = re.compile(raw)
            for line in text.split('\n'):
                if line.startswith('\t') and not line.startswith('\t\t\t') and r.search(line):
                    print('  raw:', line.strip()[:200])
        dump_vars(text, pat, tags)


if __name__ == '__main__':
    main()
