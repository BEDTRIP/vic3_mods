# -*- coding: utf-8 -*-
"""Builds the one addon-only merge file addon-Grey's needs: five buildings.

Two of the twelve compatches that make up addon-Grey's touch overlapping
building records: `_greys/greys+ef done`'s zz_greys_ef_buildings_inject.txt
carries TRY_INJECT: on five buildings (building_food_industry,
building_livestock_ranch, building_port, building_power_plant,
building_trade_center), each adding one or two of E&F's own
production-method groups so the building enters E&F's stock/liquidity
economy. `_greys/greys+tgr done`'s zz_greys_tgr_food_industry.txt and
zz_greys_tgr_trade_center.txt are full REPLACE_OR_CREATE: bodies for two of
those same five (TGR's building_group and has_max_level restores
respectively), each naming its own production_method_groups list that does
not include E&F's groups.

Copied into the addon as separate files they sort
zz_greys_ef_buildings_inject.txt < zz_greys_tgr_food_industry.txt /
zz_greys_tgr_trade_center.txt, so TGR's REPLACE_OR_CREATE: -- which names none
of E&F's fields -- would load LAST and silently wipe E&F's injection again on
those two buildings. That is exactly the bug the two individual compatches
each exist to fix against their own target; assembling them naively
reintroduces it one level up, the same class of collision documented for
addon-VC's buy_packages (see tools/regen_addon_vc.py) -- section 8 of the
working rules calls this the typical assembly conflict and prescribes one
zzzz_addon_<...>.txt file, loaded last, carrying the merged body.

This script generates exactly that, for all five buildings so the whole
source file can be excluded from the plain copy without losing anything:
TGR's body (already the right REPLACE_OR_CREATE: prefix and every other field
each pair already restores) with E&F's groups appended into the same list,
for the two buildings TGR also touches; E&F's own TRY_INJECT: unchanged,
verbatim, for the three it does not (no other compatch names these three, so
there is nothing to merge them WITH -- see build_addon_greys.py's duplicate-
key check, which finds no collision on them).

Generated fresh from the two source compatches every run -- never hand-copied,
never hand-edited. Re-run after regen_greys_ef.py or regen_greys_tgr.py
changes their output.

Usage:
    python3 regen_addon_greys.py --repo <path to vic3_mods> [--check]
"""
import argparse, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vic3lib as V

EF_SRC = '_greys/greys+ef done/common/buildings/zz_greys_ef_buildings_inject.txt'
TGR_FOOD_SRC = '_greys/greys+tgr done/common/buildings/zz_greys_tgr_food_industry.txt'
TGR_TRADE_SRC = '_greys/greys+tgr done/common/buildings/zz_greys_tgr_trade_center.txt'
OUT = '__addon/addon greys/common/buildings/zzzz_addon_greys_buildings.txt'

# Buildings where E&F's TRY_INJECT: collides with a TGR REPLACE_OR_CREATE: --
# (key, tgr source file, human label for the TGR restore, expected E&F groups)
MERGED_BUILDINGS = [
    ('building_food_industry', TGR_FOOD_SRC, 'TGR (building_group restore)',
     ['pmg_market_liquidity', 'pmg_private_ownership_manufacture_stock']),
    ('building_trade_center', TGR_TRADE_SRC, 'TGR (has_max_level restore)',
     ['pmg_market_liquidity', 'pmg_private_ownership_manufacture_stock']),
]

# Buildings where E&F's TRY_INJECT: is the only compatch touching the record
# -- nothing to merge it with, carried over verbatim so the whole ef source
# file can still be excluded from the plain per-compatch copy as one unit.
EF_ONLY_BUILDINGS = ['building_livestock_ranch', 'building_port', 'building_power_plant']


def pmg_list(body):
    """Bare group names inside a production_method_groups sub-block, in order."""
    block = V.sub(body, 'production_method_groups')
    assert block, 'no production_method_groups sub-block found'
    inner = block[1:-1]
    return [ln.strip() for ln in inner.split('\n') if ln.strip() and not ln.strip().startswith('#')]


def insert_groups(decl_text, extra_names):
    """Append `extra_names` as new lines just before the closing brace of this
    declaration's production_method_groups sub-block, matching its own tab
    indentation -- so the merged file reads like one author wrote it."""
    m = re.search(r'production_method_groups\s*=\s*\{', decl_text)
    assert m, 'no production_method_groups sub-block in declaration'
    i = decl_text.index('{', m.start())
    depth, close = 0, None
    for j in range(i, len(decl_text)):
        if decl_text[j] == '{':
            depth += 1
        elif decl_text[j] == '}':
            depth -= 1
            if depth == 0:
                close = j
                break
    assert close is not None, 'unbalanced production_method_groups sub-block'
    line_start = decl_text.rfind('\n', 0, close) + 1
    indent_of_close = decl_text[line_start:close]
    item_indent = indent_of_close + '\t'
    lines = ''.join('%s%s\t# E&F\n' % (item_indent, name) for name in extra_names)
    return decl_text[:line_start] + lines + decl_text[line_start:]


def build(repo):
    ef_text = V.read(os.path.join(repo, EF_SRC))

    chunks = []
    for key, tgr_src, label, expect_groups in MERGED_BUILDINGS:
        ef_decl, ef_body = V.entry(ef_text, key, 'TRY_INJECT:')
        ef_groups = pmg_list(ef_body)
        assert ef_groups == expect_groups, \
            '%s: E&F injection groups changed shape (%s) -- re-check the merge' % (key, ef_groups)

        tgr_text = V.read(os.path.join(repo, tgr_src))
        tgr_decl, tgr_body = V.entry(tgr_text, key, 'REPLACE_OR_CREATE:')
        tgr_groups = pmg_list(tgr_body)
        overlap = set(ef_groups) & set(tgr_groups)
        assert not overlap, '%s: E&F group already present in TGR body: %s' % (key, overlap)

        merged = insert_groups(tgr_decl, ef_groups)
        assert V.brace_balance(merged) == 0, '%s: merge produced unbalanced braces' % key
        chunks.append('# %s -- %s, plus E&F\'s production_method_groups folded in\n%s'
                       % (key, label, merged))

    for key in EF_ONLY_BUILDINGS:
        ef_decl, ef_body = V.entry(ef_text, key, 'TRY_INJECT:')
        assert V.brace_balance(ef_decl) == 0, '%s: source declaration has unbalanced braces' % key
        chunks.append('# %s -- E&F only, no other compatch touches this record, carried over verbatim\n%s'
                       % (key, ef_decl))

    header = (
        "# addon-Grey's only -- this file is in NEITHER of the two compatches it merges.\n"
        "#\n"
        "# Why it exists: _greys/greys+ef done's zz_greys_ef_buildings_inject.txt\n"
        "# TRY_INJECT:s E&F's production_method_groups onto five buildings. Two of\n"
        "# them -- building_food_industry, building_trade_center -- are also\n"
        "# REPLACE_OR_CREATE:d whole by _greys/greys+tgr done's\n"
        "# zz_greys_tgr_food_industry.txt / zz_greys_tgr_trade_center.txt, which name\n"
        "# their own production_method_groups list without E&F's entries. Copied into\n"
        "# the addon as separate files they sort zz_greys_ef_buildings_inject.txt <\n"
        "# zz_greys_tgr_food_industry.txt / zz_greys_tgr_trade_center.txt, so TGR's\n"
        "# full body -- naming none of E&F's fields -- would load LAST inside this one\n"
        "# addon mod and silently wipe E&F's injection again on those two buildings.\n"
        "# Section 8 of the working rules calls this the typical assembly conflict and\n"
        "# prescribes one merged file that loads last instead. This is that file: for\n"
        "# the two contested buildings, TGR's body (with every other field it already\n"
        "# restores) plus E&F's groups appended into the same list; for the other\n"
        "# three (building_livestock_ranch, building_port, building_power_plant, which\n"
        "# no other compatch touches) E&F's own TRY_INJECT: carried over verbatim, so\n"
        "# the whole zz_greys_ef_buildings_inject.txt source file can be excluded from\n"
        "# the plain per-compatch copy as one unit without losing anything.\n"
        "#\n"
        "# !! MAINTENANCE !! Generated by tools/regen_addon_greys.py from\n"
        "# _greys/greys+ef done and _greys/greys+tgr done -- never hand-edit, the next\n"
        "# run overwrites this file. Re-run after either of those two compatches\n"
        "# changes. The generator asserts E&F's group lists and prefixes stay what they\n"
        "# were when this was written, and that TGR's body does not already name\n"
        "# either group; a failed assert means one of the two pairs changed shape and\n"
        "# the merge needs a fresh look, not a silent re-run.\n"
        "\n"
    )
    text = header + '\n\n'.join(chunks) + '\n'
    assert V.brace_balance(text) == 0, 'generated file has unbalanced braces'
    return text, len(MERGED_BUILDINGS), len(EF_ONLY_BUILDINGS)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True)
    ap.add_argument('--check', action='store_true', help='verify only, change nothing')
    a = ap.parse_args(argv)

    text, n_merged, n_ef_only = build(a.repo)
    out_path = os.path.join(a.repo, OUT)

    if a.check:
        old = V.read(out_path) if os.path.exists(out_path) else None
        same = (old == text)
        print('%s: %s (%d merged, %d E&F-only carried over)' % (OUT, 'SAME' if same else 'DRIFT', n_merged, n_ef_only))
        return 0 if same else 1

    V.write(out_path, text)
    print('wrote %s: %d merged, %d E&F-only carried over' % (OUT, n_merged, n_ef_only))
    return 0


if __name__ == '__main__':
    sys.exit(main())
