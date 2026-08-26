# -*- coding: utf-8 -*-
"""Builds addon-LLWA out of its three pair compatches, and checks the result.

Rule the hard way round (section 8 of the working notes): the assembly is built
FROM the compatches, never by editing the previous assembly.

Three pairs make up this addon (LLWA.1-3 in the plan): TGR, VC, Kuromi's AI.
Unlike addon-VC's buy_packages, none of the three compatches here write the
same relative path as another -- `llwa+tgr done` writes
common/production_methods/zz_llwa_tgr_rails.txt, `llwa+vc done` writes
common/production_methods/zz_llwa_vc_rails.txt (different filename, same
folder, no collision), `llwa+kai done` writes three files under
common/ai_strategies/. So this build needs no addon-only merge file -- a
straight copy-and-verify is enough.

Usage:
    python3 build_addon_llwa.py --repo <path to vic3_mods> [--check]
"""
import argparse, os, shutil, filecmp, sys, re, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vic3lib import read, brace_balance

PAIRS = ['_llwa/llwa+tgr done',
         '_llwa/llwa+vc done',
         '_llwa/llwa+kai done']
ADDON = '__addon/addon llwa'

SKIP = {'.metadata', 'thumbnail.png'}
SKIP_SUFFIX = ('.md', '.xlsx')

# Repeated top-level keys the internal check would otherwise flag. Each one
# needs a reason here, not a silent exception (section 8). All eight are the
# SAME deliberate pattern inside `llwa+kai done`: file 1
# (03_political_strategies.txt) bare-restores current vanilla as a floor at
# LLWA's own file-overridden path; files 2/3 (filename-sorted after it,
# "z.../zz../zzz..." > "0...") explicitly INJECT:/REPLACE_OR_CREATE: on top
# of that floor -- the intended chain, not two compatches competing for the
# same record. See tools/regen_llwa_kai.py and _llwa/llwa+kai done/README.md.
_KAI_KEYS = ('common/ai_strategies', 'llwa+kai done: bare vanilla-restore floor in '
             '03_political_strategies.txt, then an explicit INJECT:/REPLACE_OR_CREATE: '
             'on top in a later-sorted file within the same compatch -- intentional '
             'layering, not competing owners. See regen_llwa_kai.py.')
DECLARED_DUPS = {
    ('common/ai_strategies', k): _KAI_KEYS[1]
    for k in (
        'ai_strategy_conservative_agenda',
        'ai_strategy_reactionary_agenda',
        'ai_strategy_progressive_agenda',
        'ai_strategy_egalitarian_agenda',
        'ai_strategy_nationalist_agenda',
        'ai_strategy_great_reforms',
        'ai_strategy_tanzimat_reforms',
        'ai_strategy_meiji_restoration',
    )
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

    # ---- target list ------------------------------------------------------------
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
        protect = set(target)
        stale = sorted(set(have) - protect)
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
        print('  %-16s %2d files, %d missing, %d different'
              % (pair.split('/')[-1], len(files), len(missing), len(differ)))
        for r in missing + differ:
            print('      ! ' + r)
        bad += len(missing) + len(differ)
    extra = sorted(set(walk(addon)) - set(target))
    print('  addon-only files: %d' % len(extra))
    for r in extra:
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

    goods = [r for r in files if r.startswith('common/goods/')]
    print('  goods files in the addon: %d (none of the three compatches add any -- '
          '128 ceiling unchanged)' % len(goods))

    print('\n%s' % ('ALL CHECKS PASS' if not bad else '%d PROBLEM(S)' % bad))
    return 1 if bad else 0


def _today():
    import datetime
    return datetime.date.today().isoformat()


if __name__ == '__main__':
    sys.exit(main())
