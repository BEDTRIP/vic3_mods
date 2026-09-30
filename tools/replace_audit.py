"""Audit: our REPLACE:/TRY_REPLACE: bodies that omit top-level fields of the record they replace.

If REPLACE: replaces the whole record (decided 2026-09-24), every omitted field is
lost. Source of "the record": the last non-REPLACE definition of the key in the
same category dir, across vanilla + vic3_mods_out (any mod).
"""
import os, re, glob, collections
REPO = r"C:/Users/Andrey/Projects/vic3/vic3_mods"
OUT = r"C:/Users/Andrey/Projects/vic3/vic3_mods_out"
VAN = r"C:/Games/Steam/steamapps/common/Victoria 3/game"

# МП.7 (2026-09-25): omissions checked by hand and kept on purpose. Key =
# (category, record); value = (the omitted fields, why). A row matches only if
# the omitted set is exactly this -- a new omission shows up again.
DECLARED = {
    ('static_modifiers', 'speculative_bubble_modifier'): (['state_construction_mult'],
        'EF.29: the bubble does not cut construction'),
    ('static_modifiers', 'no_money_production'): (['state_sell_orders_local_currency_add'],
        "hotfix: E&F's flat 2500 currency per state removed at the source"),
    ('buildings', 'building_construction_sector'): (['has_max_level'],
        "PSC's own body (no level cap); greys+psc states has_max_level = no explicitly"),
    ('buildings', 'building_ef_private_construction'): (['required_construction'],
        'E&F building disabled under PSC (potential = always no)'),
    ('building_groups', 'bg_construction'): (['is_government_funded', 'lens', 'urbanization'],
        "PSC's own body, verbatim: construction is private under PSC"),
}
for _pm in ('pm_wooden_buildings', 'pm_iron_frame_buildings', 'pm_steel_frame_buildings', 'pm_arc_welded_buildings'):
    DECLARED[('production_methods', _pm)] = (None,
        "PSC's model: construction comes from goods through the regulator, not country_construction_add; "
        "VC's state_modifiers layer is restored in greys+vc")
# T&R branch rows (_tr/, and megapack variants carrying T&R) are left listed:
# that branch is unsupported since 05.09 and not triaged.

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
declared = []
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
        dec = DECLARED.get((c, key))
        if miss and dec and (dec[0] is None or dec[0] == miss):
            declared.append((rp.split('/common/')[0], c, key, dec[1]))
            continue
        if miss:
            rows.append((rp.split('/common/')[0], c, key, miss, o[1]))
print(len(declared), 'omissions declared on purpose (DECLARED, МП.7)')
agg = collections.Counter(r[0] for r in rows)
print(len(rows), 'REPLACE entries missing fields of the original')
for mod, n in agg.most_common(): print(f'  {n:4} {mod}')
print()
for r in rows[:400]:
    print(f"{r[0]} | {r[1]} | {r[2]} | missing {r[3]} | orig {r[4]}")
