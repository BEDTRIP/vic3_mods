# -*- coding: utf-8 -*-
"""Writes .metadata/metadata.json for addon-Grey's.

The twelve compatches folded into this addon (PSC, PBE, E&F, Morgenroete, TGR,
KAI, addon-LLWA, megapack, and the four internal fixes) already have their own
metadata.json, written by their own regen_greys_*.py generators; this script
only writes the assembly's.

metadata.json must be written WITHOUT a BOM: the launcher parses it as strict
JSON and dies on \xEF\xBB\xBF before the '{'.

Usage:
    python3 addon_greys_metadata.py <repo>
"""
import json, os, sys

DATE = '2026-08-27'
GAME = '1.13.*'

MODS = {
    # The eight Grey's pack mods themselves -- none declare a version; grey_diplo
    # ships an empty id in its own metadata.json, found instead via the "Grey's
    # Essential Recommendations" Steam Workshop collection page (see the plan,
    # GR.14/GR.11 write-ups).
    'soft_econ':   ('3345217364', "Grey's Soft Econ Adjustments", 'mod declares no version'),
    'soft_pop':    ('3336914177', "Grey's Soft Pop Adjustments", 'mod declares no version'),
    'usu':         ('3371689443', "Grey's Urban Synergy Unleashed", 'mod declares no version'),
    'cinosphere':  ('3108195724', "Grey's Deeper Sinosphere", 'mod declares no version'),
    'food':        ('3330261506', "Grey's Food Industries Rework", 'mod declares no version'),
    'ranch':       ('3394847149', "Grey's Ranch Production Rework", 'mod declares no version'),
    'diplo':       ('3646757534', "Grey's Diplomatic Interaction Suite", 'mod declares no version'),
    'subject':     ('3276243851', "Grey's Subject Interaction Suite", 'mod declares no version'),
    # External mods the twelve core compatches depend on.
    'psc':   ('3420714166', '[1.13] Private Sector Construction', '1.3.7'),
    'ef':    ('3143591632', 'Economic and Financial Mod (E&F) - V4', 'mod declares no version'),
    'efhf':  ('3786286962', 'E&F Hotfix', '4.1.7.4'),
    'pbe':   ('3623185901', '[1.13] Power Blocs Expanded', 'mod declares no version'),
    'tgr':   ('3215078236', 'The Great Revision', '2.0'),
    'morg':  ('2889925770', '[1.13] Morgenroete - Dawn of Flavor', '2.8.3e Mitsopoulos'),
    'llwa':  ('3790590434', 'Addon: LLWA x MegaComPatch', '1.13.11.3'),
    'mega':  ('3640735868', 'MegaComPatch TGR + PSC + KAI + E&F + MR + PBE', '1.13.11.2'),
    # KAI's own metadata.json declares this non-Steam id, not a Workshop number
    # -- same convention as addon1_metadata.py / addon_vc_metadata.py.
    'kai':   ('kai.kuromi', "Kuromi's AI", '7.5'),
}

DEPS = ['soft_econ', 'soft_pop', 'usu', 'cinosphere', 'food', 'ranch', 'diplo', 'subject',
        'psc', 'ef', 'efhf', 'pbe', 'tgr', 'morg', 'llwa', 'mega', 'kai']


def dep(k, ver='*'):
    i, n, _ = MODS[k]
    return {'rel_type': 'dependency', 'id': i, 'display_name': n,
            'resource_type': 'mod', 'version': ver}


def tested(keys):
    out = []
    for k in keys:
        i, n, v = MODS[k]
        out.append({'id': i, 'display_name': n, 'version': v, 'date': DATE})
    return out


DATA = {
    'name': "Addon: Grey's x MegaComPatch",
    'id': 'asm.addon.greys',
    'version': '1.13.11-1',
    'supported_game_version': GAME,
    'short_description': (
        "Compatibility addon that puts the Grey's pack (Soft Econ, Soft Pop, Urban Synergy "
        "Unleashed, Deeper Sinosphere, Food Industries Rework, Ranch Production Rework, "
        "Diplomatic Interaction Suite, Subject Interaction Suite) on top of the MegaComPatch "
        "set (The Great Revision, Private Sector Construction, Kuromi's AI, E&F, Morgenroete, "
        "Power Blocs Expanded) and addon-LLWA. Merge of eight ComPatches for this block -- "
        "PSC, PBE, E&F+Hotfix, Morgenroete, TGR, KAI, addon-LLWA, megapack no-t&r -- plus four "
        "internal fixes for bugs within the Grey's pack itself (a CMF registry flag, two "
        "cross-file field losses, a typo'd prefix), plus one internal merge file the assembly "
        "itself needs (two buildings E&F and TGR both touch, see README). Does NOT carry "
        "Victorian Century or Hail, Columbia!+GoB+MoH content: those two branches are "
        "alternatives to each other upstream of this addon, so their Grey's compatches "
        "(ComPatch Grey's + VC, ComPatch Grey's + addon-VC, ComPatch Grey's + HC+GoB+MoH) each "
        "ship separately -- load the one matching your branch right after this addon. Load "
        "this addon last, after the whole Grey's pack."
    ),
    'picture': 'thumbnail.png',
    'tags': ['Fixes', 'Utilities', 'Expansion', 'Historical', 'Gameplay', '1.13'],
    'relationships': [dep(k) for k in DEPS],
    'game_custom_data': {'multiplayer_synchronized': True, 'tested_with': tested(DEPS)},
}


def main(repo):
    path = os.path.join(repo, '__addon', 'addon greys', '.metadata', 'metadata.json')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    text = json.dumps(DATA, indent=2, ensure_ascii=False)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text + '\n')
    os.replace(tmp, path)
    b = open(path, 'rb').read()
    assert b[:3] != b'\xEF\xBB\xBF', 'BOM in ' + path
    json.loads(b.decode('utf-8'))
    print('ok  __addon/addon greys/.metadata/metadata.json')


if __name__ == '__main__':
    main(sys.argv[1])
