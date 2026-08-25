# -*- coding: utf-8 -*-
"""Writes .metadata/metadata.json for the three addon-1 pair compatches and for
the addon itself.  Kept as one script so the dependency ids and the tested_with
block cannot drift apart between four files.

metadata.json must be written WITHOUT a BOM: the launcher parses it as strict
JSON and dies on \xEF\xBB\xBF before the '{'.
"""
import json, os, sys

DATE = '2026-08-25'
GAME = '1.13.*'

MODS = {
    'cmf':  ('com.github.Victoria-3-Modding-Co-op.Community-Mod-Framework', 'Community Mod Framework', '1.63.0'),
    'etf':  ('com.github.Victoria-3-Modding-Co-op.Expanded-Topbar-Framework', 'Expanded Topbar Framework', '1.19.0'),
    'gob':  ('3384997867', '[1.13] Gates of the Bosphorus', '4.0.8'),
    'moh':  ('top.sleepingbed.moh', 'Mandate of Heaven', '1.4.6.1'),
    'morg': ('2889925770', '[1.13] Morgenroete - Dawn of Flavor', '2.8.3e Mitsopoulos'),
    'tgr':  ('3215078236', 'The Great Revision', "2.0 (1.13.10, 12.08.2026)"),
    'tr':   ('tech.res', '[1.13] Tech & Res', "1.6'"),
    'kai':  ('kai.kuromi', "Kuromi's AI", '7.5'),
    'mega': ('3638078714', 'MegaComPatch TGR + PSC + E&F + MR + T&R + PBE', '1.13.11-3'),
}
# Hail, Columbia! ships an EMPTY id in its metadata.json, so it cannot appear in
# relationships at all -- it is named in the README and in tested_with instead.
HC_NAME, HC_VER = 'Hail, Columbia! - United States Flavor Pack', '8.6-Roosevelt'


def dep(k, ver='*'):
    i, n, _ = MODS[k]
    return {'rel_type': 'dependency', 'id': i, 'display_name': n,
            'resource_type': 'mod', 'version': ver}


def tested(keys):
    out = []
    for k in keys:
        i, n, v = MODS[k]
        out.append({'id': i, 'display_name': n, 'version': v, 'date': DATE})
    out.append({'id': '', 'display_name': HC_NAME, 'version': HC_VER, 'date': DATE})
    return out


def meta(name, mid, short, deps, tests, tags):
    return {
        'name': name,
        'id': mid,
        'version': '1.13.11-2',
        'supported_game_version': GAME,
        'short_description': short,
        'picture': 'thumbnail.png',
        'tags': tags,
        'relationships': [dep(k) for k in deps],
        'game_custom_data': {'multiplayer_synchronized': True, 'tested_with': tested(tests)},
    }


FIX = ['Fixes', 'Utilities', '1.13']

FILES = {
    '_HC+GoB+MoH/hc+morg done': meta(
        'ComPatch HC + GoB + MoH + Morgenroete',
        'asm.compatch.hcgobmoh.morgenroete',
        'Compatibility patch for Hail, Columbia! + Gates of the Bosphorus + Mandate of Heaven '
        'with Morgenroete. Load after all four.',
        ['cmf', 'gob', 'moh', 'morg'], ['cmf', 'gob', 'moh', 'morg'], FIX),
    '_HC+GoB+MoH/hc+tgr done': meta(
        'ComPatch HC + GoB + MoH + The Great Revision',
        'asm.compatch.hcgobmoh.tgr',
        'Compatibility patch for Hail, Columbia! + Gates of the Bosphorus + Mandate of Heaven '
        'with The Great Revision. Load after all four.',
        ['cmf', 'gob', 'moh', 'tgr'], ['cmf', 'gob', 'moh', 'tgr'], FIX),
    '_HC+GoB+MoH/hc+tr+kai done': meta(
        'ComPatch HC + GoB + MoH + Tech & Res + Kuromi AI',
        'asm.compatch.hcgobmoh.trkai',
        'Compatibility patch for Hail, Columbia! + Gates of the Bosphorus + Mandate of Heaven '
        'with Tech & Res and Kuromi\'s AI. Load after all five.',
        ['cmf', 'gob', 'moh', 'tr', 'kai'], ['cmf', 'gob', 'moh', 'tr', 'kai'], FIX),
    '__addon/addon1 hc+gob+moh': meta(
        'Addon 1: HC + GoB + MoH x MegaComPatch',
        'asm.addon1.hcgobmoh',
        'Compatibility addon that puts Hail, Columbia! + Gates of the Bosphorus + Mandate of '
        'Heaven on top of the MegaComPatch set. Merge of my three ComPatches for this block. '
        'Load last, after all of them.',
        ['cmf', 'etf', 'mega', 'gob', 'moh', 'morg', 'tgr', 'tr', 'kai'],
        ['cmf', 'etf', 'mega', 'gob', 'moh', 'morg', 'tgr', 'tr', 'kai'],
        ['Fixes', 'Utilities', 'Expansion', 'Historical', 'Gameplay', '1.13']),
}


def main(out):
    for folder, data in FILES.items():
        path = os.path.join(out, folder, '.metadata', 'metadata.json')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        text = json.dumps(data, indent=2, ensure_ascii=False)
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text + '\n')
        os.replace(tmp, path)
        b = open(path, 'rb').read()
        assert b[:3] != b'\xEF\xBB\xBF', 'BOM in ' + path
        json.loads(b.decode('utf-8'))
        print('ok  ' + folder + '/.metadata/metadata.json')


if __name__ == '__main__':
    main(sys.argv[1])
