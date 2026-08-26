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
    'kai':  ('kai.kuromi', "Kuromi's AI", '7.5'),
    'mega': ('3640735868', 'MegaComPatch TGR + PSC + KAI + E&F + MR + PBE', '1.13.11-2'),
}
# Hail, Columbia! and Victorian Century both ship an EMPTY id in their
# metadata.json, so neither can appear in relationships at all -- each is named
# in the README and in tested_with instead.
HC_NAME, HC_VER = 'Hail, Columbia! - United States Flavor Pack', '8.6-Roosevelt'
VC_NAME, VC_VER = 'Victorian Century', 'unpacked 2026-08-25, mod declares no version'


def dep(k, ver='*'):
    i, n, _ = MODS[k]
    return {'rel_type': 'dependency', 'id': i, 'display_name': n,
            'resource_type': 'mod', 'version': ver}


def tested(keys, vc=False):
    out = []
    for k in keys:
        i, n, v = MODS[k]
        out.append({'id': i, 'display_name': n, 'version': v, 'date': DATE})
    out.append({'id': '', 'display_name': HC_NAME, 'version': HC_VER, 'date': DATE})
    if vc:
        out.append({'id': '', 'display_name': VC_NAME, 'version': VC_VER, 'date': DATE})
    return out


def meta(name, mid, short, deps, tests, tags, vc=False):
    return {
        'name': name,
        'id': mid,
        'version': '1.13.11-3',
        'supported_game_version': GAME,
        'short_description': short,
        'picture': 'thumbnail.png',
        'tags': tags,
        'relationships': [dep(k) for k in deps],
        'game_custom_data': {'multiplayer_synchronized': True, 'tested_with': tested(tests, vc=vc)},
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
        'with The Great Revision. Load after all four. ideology_jacksonian_democrat also carries '
        'Victorian Century\'s law stances (built from the tgr+vc compatch), and this pair also '
        'carries Victorian Century\'s rework of ig_landowners/ig_rural_folk plus VC additions to '
        'chi - china.txt, tur - ottoman empire.txt and usa - usa.txt, so Victorian Century is a '
        'dependency too -- load it, and the tgr+vc compatch, before this one.',
        ['cmf', 'gob', 'moh', 'tgr'], ['cmf', 'gob', 'moh', 'tgr'], FIX, vc=True),
    '_HC+GoB+MoH/hc+kai done': meta(
        'ComPatch HC + GoB + MoH + Kuromi AI',
        'asm.compatch.hcgobmoh.kai',
        'Compatibility patch for Hail, Columbia! + Gates of the Bosphorus + Mandate of Heaven '
        'with Kuromi\'s AI. Load after all five. Also re-issues The Great Revision\'s '
        'injections into ai_strategy_default, so The Great Revision is a dependency too.',
        ['cmf', 'gob', 'moh', 'kai', 'tgr'], ['cmf', 'gob', 'moh', 'kai', 'tgr'], FIX),
    '_HC+GoB+MoH/hc+vc done': meta(
        'ComPatch HC + GoB + MoH + Victorian Century',
        'asm.compatch.hcgobmoh.vc',
        'Compatibility patch for Hail, Columbia! + Gates of the Bosphorus + Mandate of Heaven '
        'with Victorian Century. Load after all four. Five more shared items -- ig_landowners, '
        'ig_rural_folk, chi - china.txt, tur - ottoman empire.txt, usa - usa.txt -- are carried '
        'by the hc+tgr compatch instead (same REPLACE path), so The Great Revision and that '
        'compatch are dependencies too.',
        ['cmf', 'gob', 'moh', 'tgr'], ['cmf', 'gob', 'moh', 'tgr'], FIX, vc=True),
    '__addon/addon1 hc+gob+moh': meta(
        'Addon 1: HC + GoB + MoH x MegaComPatch',
        'asm.addon1.hcgobmoh',
        'Compatibility addon that puts Hail, Columbia! + Gates of the Bosphorus + Mandate of '
        'Heaven on top of the MegaComPatch set. Merge of my four ComPatches for this block. '
        'Also carries Victorian Century\'s law stances for ideology_jacksonian_democrat and its '
        'own character/DNA/flag/opium/law content, so Victorian Century is a dependency too. '
        'Load last, after all of them.',
        ['cmf', 'etf', 'mega', 'gob', 'moh', 'morg', 'tgr', 'kai'],
        ['cmf', 'etf', 'mega', 'gob', 'moh', 'morg', 'tgr', 'kai'],
        ['Fixes', 'Utilities', 'Expansion', 'Historical', 'Gameplay', '1.13'], vc=True),
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
