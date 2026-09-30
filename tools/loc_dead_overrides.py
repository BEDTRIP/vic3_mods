"""Localization overrides that can never show.

Localization is first-come: the first file that defines a key wins, whatever
the mod order. A key in our mod OUTSIDE localization/<lang>/replace/ that
vanilla or an earlier mod already defines under a different path is dead.
Fix: move it to localization/<lang>/replace/. Written 2026-09-24.

EARLIER lists the mods that load before ours (check content_load.json);
OURS the folders to scan. Run: py tools/loc_dead_overrides.py
"""
import os, re, glob
W = r'C:\Games\Steam\steamapps\workshop\content\529340'
VAN = r'C:\Games\Steam\steamapps\common\Victoria 3\game'
EARLIER = {  # mods that load before our compatches (content_load.json order), plus vanilla
    'vanilla': VAN,
    'E&F': os.path.join(W, '3143591632'),
    'E&F RUS': os.path.join(W, '3520140574'),
    'PSC': r'C:\Users\Andrey\Projects\vic3\vic3_mods_out\PSC',
    'TGR': r'C:\Users\Andrey\Projects\vic3\vic3_mods_out\TheGreatRevision',
}
KEY = re.compile(r'^\s*([^\s:#][^:#\s]*)\s*:\s*\d*\s*"')

def keys_in(path, lang):
    out = {}
    base = os.path.join(path, 'localization')
    for p in glob.glob(os.path.join(base, '**', f'*_l_{lang}.yml'), recursive=True):
        if os.sep + 'replace' + os.sep in p:
            continue
        rel = os.path.relpath(p, base)
        for l in open(p, encoding='utf-8-sig', errors='replace'):
            m = KEY.match(l)
            if m:
                out.setdefault(m.group(1), rel)
    return out

OURS = {
    'hotfix': r'C:\Users\Andrey\Projects\vic3\vic3_mods\_ef\ef hotfix 1.13',
    'ef+psc': r'C:\Users\Andrey\Projects\vic3\vic3_mods\_ef\ef+psc done',
    'ef+tgr': r'C:\Users\Andrey\Projects\vic3\vic3_mods\_ef\ef+tgr done',
}
for lang in ('english', 'russian'):
    earlier = {}
    for name, path in EARLIER.items():
        for k, rel in keys_in(path, lang).items():
            earlier.setdefault(k, (name, rel))
    for oname, opath in OURS.items():
        base = os.path.join(opath, 'localization')
        for p in glob.glob(os.path.join(base, lang, '*.yml')):
            rel = os.path.relpath(p, base)
            dead = []
            for l in open(p, encoding='utf-8-sig', errors='replace'):
                m = KEY.match(l)
                if m and m.group(1) in earlier:
                    src = earlier[m.group(1)]
                    same_path = src[1] == rel
                    if not same_path:
                        dead.append((m.group(1), src[0], src[1]))
            if dead:
                print(f'[{lang}] {oname}: {rel} -- {len(dead)} keys defined earlier elsewhere')
                for d in dead[:6]:
                    print('     ', d)
