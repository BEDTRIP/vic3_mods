"""Stale full bodies: a mod's records re-issued with a full body (REPLACE:/REPLACE_OR_CREATE:/bare)
that lack top-level fields vanilla has -- usually a body written before the current game version.

Usage:  py tools/stale_bodies.py <mod root> [max rows per category]
        e.g. py tools/stale_bodies.py "../vic3_mods_out/TheGreatRevision" 40

Noise to ignore: defines (merged per key), on_actions and history (additive). The rest needs a
human: a missing field is either the game's new content (restore, see TGR.3 /
tools/regen_tgr_113_fix.py) or the mod's own redesign (leave). Written for TGR.3, 2026-09-25."""
import os, re, glob, collections, sys
OUT = r'C:\Users\Andrey\Projects\vic3\vic3_mods_out'
VAN = os.path.join(OUT, '.vanillaVIC3', 'common')
TGR = os.path.join(os.path.abspath(sys.argv[1]), 'common')

def records(path):
    t = open(path, encoding='utf-8-sig', errors='replace').read()
    t = re.sub(r'#[^\n]*', '', t)
    out = []
    for m in re.finditer(r'(?m)^([A-Z_]+:)?([A-Za-z0-9_.\-]+)\s*=\s*\{', t):
        i = t.index('{', m.start()); d = 0
        for j in range(i, len(t)):
            if t[j] == '{': d += 1
            elif t[j] == '}':
                d -= 1
                if d == 0: break
        out.append((m.group(1) or '', m.group(2), t[i + 1:j]))
    return out

def top_fields(body):
    names, d, i = [], 0, 0
    for m in re.finditer(r'([A-Za-z0-9_]+)\s*=|\{|\}', body):
        s = m.group(0)
        if s == '{': d += 1
        elif s == '}': d -= 1
        elif d == 0: names.append(m.group(1))
    return set(names)

van = {}
for f in glob.glob(os.path.join(VAN, '**', '*.txt'), recursive=True):
    cat = os.path.relpath(os.path.dirname(f), VAN).replace('\\', '/')
    for pre, k, b in records(f):
        van[(cat, k)] = top_fields(b)
res = collections.defaultdict(list)
for f in glob.glob(os.path.join(TGR, '**', '*.txt'), recursive=True):
    cat = os.path.relpath(os.path.dirname(f), TGR).replace('\\', '/')
    for pre, k, b in records(f):
        if pre.startswith('INJECT') or pre.startswith('TRY_INJECT'): continue
        v = van.get((cat, k))
        if v is None: continue
        miss = sorted(v - top_fields(b))
        if miss: res[cat].append((k, miss, os.path.basename(f)))
for cat, items in sorted(res.items()):
    print(f'== {cat}: {len(items)}')
    for k, miss, f in items[:int(sys.argv[2]) if len(sys.argv) > 2 else 8]:
        print(f'   {k:45} {miss}  ({f})')
