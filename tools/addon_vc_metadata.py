# -*- coding: utf-8 -*-
"""Writes .metadata/metadata.json for addon-VC.

The four pair compatches (tgr+vc, ef+vc, morg+vc, kai+vc) already have their own
metadata.json, written by their own regen_vc_*.py generators; this script only
writes the assembly's.

metadata.json must be written WITHOUT a BOM: the launcher parses it as strict
JSON and dies on \xEF\xBB\xBF before the '{'.

Usage:
    python3 addon_vc_metadata.py <repo>
"""
import json, os, sys

DATE = '2026-08-26'
GAME = '1.13.*'

MODS = {
    'cmf': ('com.github.Victoria-3-Modding-Co-op.Community-Mod-Framework', 'Community Mod Framework', '1.63.0'),
    'etf': ('com.github.Victoria-3-Modding-Co-op.Expanded-Topbar-Framework', 'Expanded Topbar Framework', '1.19.0'),
    'tgr': ('3215078236', 'The Great Revision', '2.0'),
    'kai': ('kai.kuromi', "Kuromi's AI", '7.5'),
    'ef': ('3143591632', 'Economic and Financial Mod (E&F) - V4', 'mod declares no version'),
    'morg': ('2889925770', '[1.13] Morgenroete - Dawn of Flavor', '2.8.3e Mitsopoulos'),
    'mega': ('3640735868', 'MegaComPatch TGR + PSC + KAI + E&F + MR + PBE', '1.13.11-2'),
}
# Victorian Century ships an EMPTY id, version and supported_game_version in its
# own metadata.json, so it cannot appear in relationships at all -- it is named
# in the short_description and in tested_with instead (same shape as
# Hail, Columbia! in addon1_metadata.py).
VC_NAME, VC_VER = 'Victorian Century', 'unpacked 2026-08-25, mod declares no version'


def dep(k, ver='*'):
    i, n, _ = MODS[k]
    return {'rel_type': 'dependency', 'id': i, 'display_name': n,
            'resource_type': 'mod', 'version': ver}


def tested(keys):
    out = []
    for k in keys:
        i, n, v = MODS[k]
        out.append({'id': i, 'display_name': n, 'version': v, 'date': DATE})
    out.append({'id': '', 'display_name': VC_NAME, 'version': VC_VER, 'date': DATE})
    return out


DEPS = ['cmf', 'etf', 'mega', 'tgr', 'ef', 'morg', 'kai']

DATA = {
    'name': 'Addon: Victorian Century x MegaComPatch',
    'id': 'asm.addon.vc',
    'version': '1.13.11-1',
    'supported_game_version': GAME,
    'short_description': (
        'Compatibility addon that puts Victorian Century on top of the MegaComPatch set '
        '(The Great Revision, Private Sector Construction, Kuromi\'s AI, E&F, Morgenroete, '
        'Power Blocs Expanded). Merge of my four ComPatches for this block -- The Great '
        'Revision, E&F, Morgenroete and Kuromi\'s AI -- plus one internal merge file the '
        'assembly itself needs (see README). Private Sector Construction and Power Blocs '
        'Expanded need no patch against Victorian Century, confirmed VC.5/VC.6. Load last, '
        'after all of them, and before Hail, Columbia! if you use it.'
    ),
    'picture': 'thumbnail.png',
    'tags': ['Fixes', 'Utilities', 'Expansion', 'Historical', 'Gameplay', '1.13'],
    'relationships': [dep(k) for k in DEPS],
    'game_custom_data': {'multiplayer_synchronized': True, 'tested_with': tested(DEPS)},
}


def main(repo):
    path = os.path.join(repo, '__addon', 'addon vc', '.metadata', 'metadata.json')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    text = json.dumps(DATA, indent=2, ensure_ascii=False)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text + '\n')
    os.replace(tmp, path)
    b = open(path, 'rb').read()
    assert b[:3] != b'\xEF\xBB\xBF', 'BOM in ' + path
    json.loads(b.decode('utf-8'))
    print('ok  __addon/addon vc/.metadata/metadata.json')


if __name__ == '__main__':
    main(sys.argv[1])
