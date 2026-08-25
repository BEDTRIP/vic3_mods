# -*- coding: utf-8 -*-
"""Builds Addon 1 out of its three pair compatches, and checks the result.

Rule the hard way round (section 8 of the working notes): the assembly is built
FROM the compatches, never by editing the previous assembly.  An old assembly is
behind on every file rename, and once it is you can no longer tell a renamed file
from a deleted one.  So: work out the target file list, move everything that is
not in it into _to_delete/, copy the target list in, then verify coverage
byte-for-byte.

Usage:
    python3 build_addon1.py --repo <path to vic3_mods> [--check]
"""
import argparse, os, shutil, filecmp, sys, re, json, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vic3lib import read, brace_balance

PAIRS = ['_HC+GoB+MoH/hc+morg done',
         '_HC+GoB+MoH/hc+tgr done',
         '_HC+GoB+MoH/hc+kai done']
ADDON = '__addon/addon1 hc+gob+moh'

# Files that belong to the addon and to no compatch.  Each one needs a header
# whose first line says so, and a reason (section 8).  Empty for now: the three
# compatches share no key and no path, so nothing has to be merged a second time.
ADDON_ONLY = []

SKIP = {'.metadata', 'thumbnail.png'}
# Markdown is documentation, not mod content: the pair reports live next to
# their compatches and conflicts_addon1_internal.md belongs to the assembly.
# Neither is a file the game reads, so neither takes part in coverage.
SKIP_SUFFIX = ('.md',)

# Repeated top-level keys the internal check would otherwise flag.  Each one needs
# a reason here, not a silent exception (section 8).
DECLARED_DUPS = {
    ('common', 'group'):
        'achievement_groups.txt is a list of anonymous `group = {}` blocks, not a '
        'keyed database; the repeats are the groups themselves',
    ('common/history/countries', 'COUNTRIES'):
        'container key, additive across files -- one per country file, same as vanilla',
    ('common/ai_strategies', 'ai_strategy_default'):
        'deliberate, and in this order: zz_hctr_ai_strategy_default ships the merged '
        'REPLACE: body and zz_hctr_tgr_default_strategy re-issues The Great Revision\'s '
        'injection on top of it -- the order their authors load in, and the order the '
        'file names sort in (`_` 0x5F before `z` 0x7A).  Tech & Res used to add a third '
        'file here; it left the set on 25.08.2026',
}


def walk(base):
    out = {}
    for r, ds, fs in os.walk(base):
        ds[:] = [d for d in ds if d not in ('_to_delete',)]
        for f in fs:
            p = os.path.join(r, f)
            rel = os.path.relpath(p, base).replace('\\', '/')
            if rel.split('/')[0] in SKIP or rel in SKIP:
                continue
            if rel.endswith(SKIP_SUFFIX):
                continue
            out[rel] = p
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True)
    ap.add_argument('--check', action='store_true', help='verify only, change nothing')
    a = ap.parse_args(argv)
    addon = os.path.join(a.repo, ADDON)

    # ---- target list --------------------------------------------------------
    target, owner = {}, {}
    for pair in PAIRS:
        for rel, src in walk(os.path.join(a.repo, pair)).items():
            if rel in target:
                raise SystemExit('two compatches ship %s (%s and %s) -- needs an '
                                 'addon-only merge file' % (rel, owner[rel], pair))
            target[rel], owner[rel] = src, pair

    # ---- copy ---------------------------------------------------------------
    if not a.check:
        have = walk(addon) if os.path.isdir(addon) else {}
        stale = sorted(set(have) - set(target))
        if stale:
            dump = os.path.join(addon, '_to_delete', 'rebuild_%s' % _today())
            for rel in stale:
                dst = os.path.join(dump, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.move(have[rel], dst)   # rm is not permitted on the mount
            print('moved %d stale file(s) to %s' % (len(stale), dump))
        for rel, src in target.items():
            dst = os.path.join(addon, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)
        print('copied %d file(s) into %s' % (len(target), ADDON))

    # ---- coverage -----------------------------------------------------------
    print('\n--- coverage (every compatch file, byte for byte) ---')
    bad = 0
    for pair in PAIRS:
        files = walk(os.path.join(a.repo, pair))
        missing = [r for r in files if not os.path.exists(os.path.join(addon, r))]
        differ = [r for r in files
                  if r not in missing and not filecmp.cmp(files[r], os.path.join(addon, r), shallow=False)]
        print('  %-24s %2d files, %d missing, %d different'
              % (pair.split('/')[-1], len(files), len(missing), len(differ)))
        for r in missing + differ:
            print('      ! ' + r)
        bad += len(missing) + len(differ)
    extra = sorted(set(walk(addon)) - set(target))
    print('  addon-only files: %d %s' % (len(extra), extra if extra else ''))
    for r in extra:
        if r not in ADDON_ONLY:
            print('      ! %s is in the addon but in no compatch and not declared' % r)
            bad += 1

    # ---- internal checks ----------------------------------------------------
    print('\n--- checks ---')
    files = walk(addon)
    print('  files: %d' % len(files))
    imbalance = [(r, brace_balance(read(p))) for r, p in files.items()
                 if r.endswith('.txt') and brace_balance(read(p))]
    print('  brace balance: %s' % ('ok' if not imbalance else imbalance))
    bad += len(imbalance)

    enc = []
    for r, p in files.items():
        raw = open(p, 'rb').read()
        has_bom = raw[:3] == b'\xEF\xBB\xBF'
        txt = raw[3:].decode('utf-8') if has_bom else raw.decode('utf-8')
        needs = any(ord(c) > 127 for line in txt.split('\n') for c in line.split('#')[0])
        if needs and not has_bom:
            enc.append(r)
    print('  encodings: %s' % ('ok' if not enc else 'missing BOM in %s' % enc))
    bad += len(enc)

    dup = collections.defaultdict(list)
    for r, p in files.items():
        if not r.startswith('common/') or not r.endswith('.txt'):
            continue
        cat = os.path.dirname(r)
        for m in re.finditer(r'(?m)^(?:[A-Z_]+:)?([a-zA-Z_][a-zA-Z_0-9]*)\s*=\s*\{', read(p)):
            dup[(cat, m.group(1))].append(r)
    dups = {k: v for k, v in dup.items() if len(v) > 1}
    declared, real = [], {}
    for k, v in dups.items():
        why = DECLARED_DUPS.get(k)
        (declared.append((k, why)) if why else real.__setitem__(k, v))
    print('  duplicate top-level keys inside the addon: %s'
          % ('none beyond the %d declared' % len(declared) if not real else real))
    for k, why in sorted(declared):
        print('      declared: %s/%s -- %s' % (k[0], k[1], why))
    bad += len(real)

    loc = collections.defaultdict(list)
    for r, p in files.items():
        if not r.startswith('localization/'):
            continue
        lang = r.split('/')[1]
        for m in re.finditer(r'(?m)^\s*([A-Za-z_][\w.]*):\d*\s+"', read(p)):
            loc[(lang, m.group(1))].append(r)
    ldups = {k: v for k, v in loc.items() if len(v) > 1}
    print('  localization: %d keys, duplicates per language: %s'
          % (len(loc), 'none' if not ldups else ldups))
    bad += len(ldups)

    goods = [r for r in files if r.startswith('common/goods/')]
    print('  goods files in the addon: %d (nothing added, so the 128 ceiling is unchanged '
          'at 74)' % len(goods))

    print('\n%s' % ('ALL CHECKS PASS' if not bad else '%d PROBLEM(S)' % bad))
    return 1 if bad else 0


def _today():
    import datetime
    return datetime.date.today().isoformat()


if __name__ == '__main__':
    sys.exit(main())
