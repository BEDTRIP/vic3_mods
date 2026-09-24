"""Audit: our REPLACE:/TRY_REPLACE: bodies that omit top-level fields of the record they replace.

If REPLACE: replaces the whole record (decided 2026-09-24), every omitted field is
lost. Source of "the record": the last non-REPLACE definition of the key in the
same category dir, across vanilla + vic3_mods_out (any mod).
"""
import os, re, glob, collections
REPO = r"C:/Users/Andrey/Projects/vic3/vic3_mods"
OUT = r"C:/Users/Andrey/Projects/vic3/vic3_mods_out"
VAN = r"C:/Games/Steam/steamapps/common/Victoria 3/game"

def strip(t):
    return '\n'.join(l.split('#')[0] for l in t.splitlines())

def entries(text):
    """yield (prefix, key, body) for top-level entries"""
    i, n = 0, len(text)
    for m in re.finditer(r'(?m)^[ \t]*((?:[A-Z_]+:)?)([A-Za-z_0-9.:\-]+)\s*=\s*\{', text):
        pass
    depth = 0; pos = 0
    pat = re.compile(r'((?:[A-Z_]+:)?)([A-Za-z_0-9.\-]+)\s*=\s*\{')
    while pos < n:
        c = text[pos]
        if depth == 0:
            m = pat.match(text, pos)
            if m:
                j = m.end() - 1; d = 0
                for k in range(j, n):
                    if text[k] == '{': d += 1
                    elif text[k] == '}':
                        d -= 1
                        if d == 0: break
                yield m.group(1), m.group(2), text[j + 1:k]
                pos = k + 1; continue
        if c == '{': depth += 1
        elif c == '}': depth = max(0, depth - 1)
        pos += 1

def fields(body):
    out = set(); d = 0; pos = 0
    pat = re.compile(r'([A-Za-z_0-9.:\-@$]+)\s*(=|\?=|<|>)')
    while pos < len(body):
        c = body[pos]
        if d == 0:
            m = pat.match(body, pos)
            if m and (pos == 0 or not (body[pos-1].isalnum() or body[pos-1] in '_:.')):
                out.add(m.group(1)); pos = m.end(); continue
        if c == '{': d += 1
        elif c == '}': d -= 1
        pos += 1
    return out

def cat_of(path):
    p = path.replace('\\', '/')
    i = p.find('/common/')
    if i < 0: return None
    rest = p[i + 8:]
    return os.path.dirname(rest)

# originals
orig = {}
for base in [VAN] + [os.path.join(OUT, d) for d in os.listdir(OUT)]:
    for f in glob.glob(os.path.join(base, '**', 'common', '**', '*.txt'), recursive=True):
        c = cat_of(f)
        if not c: continue
        try: t = strip(open(f, encoding='utf-8-sig', errors='replace').read())
        except Exception: continue
        for pre, key, body in entries(t):
            if 'REPLACE' in pre or 'INJECT' in pre: continue
            orig[(c, key)] = (fields(body), os.path.relpath(f, OUT if f.startswith(OUT) else VAN))

rows = []
for f in glob.glob(os.path.join(REPO, '**', 'common', '**', '*.txt'), recursive=True):
    rp = os.path.relpath(f, REPO).replace('\\', '/')
    if any(s in rp for s in ('_to_delete', 'deprecated/', '/out', ' out/', 'архив')): continue
    c = cat_of(f)
    t = strip(open(f, encoding='utf-8-sig', errors='replace').read())
    for pre, key, body in entries(t):
        if pre not in ('REPLACE:', 'TRY_REPLACE:'): continue
        o = orig.get((c, key))
        if not o: continue
        miss = sorted(o[0] - fields(body))
        if miss:
            rows.append((rp.split('/common/')[0], c, key, miss, o[1]))
agg = collections.Counter(r[0] for r in rows)
print(len(rows), 'REPLACE entries missing fields of the original')
for mod, n in agg.most_common(): print(f'  {n:4} {mod}')
print()
for r in rows[:400]:
    print(f"{r[0]} | {r[1]} | {r[2]} | missing {r[3]} | orig {r[4]}")
