# -*- coding: utf-8 -*-
"""Builds the one addon-only merge file addon-VC needs: common/buy_packages.

Three of the four pair compatches that make up addon-VC touch the same 99
wealth_N records: _vc/tgr+vc done (REPLACE_OR_CREATE, full body, all 99),
_vc/ef+vc done (INJECT: popneed_currency / popneed_financial_products, all 99)
and _vc/morg+vc done (TRY_INJECT: popneed_entertainment, wealth_10 up, 90
records). Copied into the addon as three separate files they sort
zz_vc_ef_buy_packages.txt < zz_vc_morg_buy_packages.txt <
zz_vc_tgr_buy_packages.txt, so TGR's file -- a full REPLACE_OR_CREATE that
names none of E&F's or Morgenroete's fields -- would load LAST inside the one
addon mod and silently wipe both of their restorations again. That is exactly
the bug all three compatches individually exist to fix against Victorian
Century; assembling them naively would just reintroduce it one level up.

Section 8 of "Правила работы с модами Victoria 3" calls this the typical
assembly conflict ("two compatches REPLACE: the same record, each for its own
line") and prescribes one zzzz_addon_<...>.txt file, loaded last, carrying the
merged body. This script generates exactly that file: TGR's body (already the
right REPLACE_OR_CREATE prefix and the record every wealth tier needs) with
E&F's and Morgenroete's injected fields appended into the same `goods` block,
so all three restorations survive together regardless of file name order.

It is generated fresh from the three pair compatches every run -- never
hand-copied and never hand-edited. Re-run it after regen_vc_tgr.py,
regen_vc_ef.py or regen_vc_morg.py changes their output.

Usage:
    python3 regen_addon_vc.py --repo <path to vic3_mods> [--check]
"""
import argparse, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vic3lib import read, write, sub, _depth0_iter, brace_balance

TGR_SRC = '_vc/tgr+vc done/common/buy_packages/zz_vc_tgr_buy_packages.txt'
EF_SRC = '_vc/ef+vc done/common/buy_packages/zz_vc_ef_buy_packages.txt'
MORG_SRC = '_vc/morg+vc done/common/buy_packages/zz_vc_morg_buy_packages.txt'
OUT = '__addon/addon vc/common/buy_packages/zzzz_addon_vc_buy_packages.txt'


def top_entries(text):
    """key -> (name_start, open_brace, close_brace, inner_text_between_braces)"""
    return {nm: (a, o, c, text[o + 1:c]) for nm, a, o, c in _depth0_iter(text)}


def prefix_of(text, name_start):
    line_start = text.rfind('\n', 0, name_start) + 1
    return text[line_start:name_start].strip()


def goods_scalars(inner):
    """Flat {field: value} of the numeric fields inside this entry's `goods` sub-block."""
    g = sub(inner, 'goods')
    if g is None:
        return {}
    return dict(re.findall(r'([a-zA-Z_]\w*)\s*=\s*([\d.]+)', g[1:-1]))


def insert_into_goods(decl_text, additions):
    """Insert `additions` (field, value, source-comment) as new lines just before
    the closing brace of this declaration's `goods` sub-block, matching its own
    tab indentation -- so the merged file reads like one author wrote it."""
    if not additions:
        return decl_text
    m = re.search(r'goods\s*=\s*\{', decl_text)
    if not m:
        raise KeyError('no goods sub-block in %r' % decl_text[:80])
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
    if close is None:
        raise ValueError('unbalanced goods sub-block')
    line_start = decl_text.rfind('\n', 0, close) + 1
    indent_of_close = decl_text[line_start:close]
    field_indent = indent_of_close + '\t'
    lines = ''.join('%s%s = %s\t# %s\n' % (field_indent, f, v, c) for f, v, c in additions)
    return decl_text[:line_start] + lines + decl_text[line_start:]


def build(repo):
    tgr_text = read(os.path.join(repo, TGR_SRC))
    ef_text = read(os.path.join(repo, EF_SRC))
    morg_text = read(os.path.join(repo, MORG_SRC))

    tgr = top_entries(tgr_text)
    ef = top_entries(ef_text)
    morg = top_entries(morg_text)

    tgr_prefixes = {prefix_of(tgr_text, v[0]) for v in tgr.values()}
    ef_prefixes = {prefix_of(ef_text, v[0]) for v in ef.values()}
    morg_prefixes = {prefix_of(morg_text, v[0]) for v in morg.values()}
    assert tgr_prefixes == {'REPLACE_OR_CREATE:'}, \
        'tgr+vc buy_packages changed prefix (%s) -- re-check the merge logic' % tgr_prefixes
    assert ef_prefixes == {'INJECT:'}, \
        'ef+vc buy_packages changed prefix (%s) -- re-check the merge logic' % ef_prefixes
    assert morg_prefixes == {'TRY_INJECT:'}, \
        'morg+vc buy_packages changed prefix (%s) -- re-check the merge logic' % morg_prefixes

    wealth_keys = sorted((k for k in tgr if k.startswith('wealth_')),
                          key=lambda k: int(k.split('_')[1]))
    assert wealth_keys == ['wealth_%d' % i for i in range(1, 100)], \
        'tgr+vc no longer covers exactly wealth_1..wealth_99 -- re-check (%d keys found)' % len(wealth_keys)
    assert set(ef) <= set(tgr), 'ef+vc has a wealth_ record tgr+vc does not: %s' % (set(ef) - set(tgr))
    assert set(morg) <= set(tgr), 'morg+vc has a wealth_ record tgr+vc does not: %s' % (set(morg) - set(tgr))

    chunks, ef_used, morg_used = [], 0, 0
    for key in wealth_keys:
        name_start, open_b, close_b, inner = tgr[key]
        line_start = tgr_text.rfind('\n', 0, name_start) + 1
        decl = tgr_text[line_start:close_b + 1]
        tgr_goods = goods_scalars(inner)

        additions = []
        if key in ef:
            ef_goods = goods_scalars(ef[key][3])
            overlap = set(ef_goods) & set(tgr_goods)
            assert not overlap, 'wealth field collision tgr/ef on %s: %s' % (key, overlap)
            additions += [(f, v, 'E&F') for f, v in sorted(ef_goods.items())]
            ef_used += 1
        if key in morg:
            morg_goods = goods_scalars(morg[key][3])
            already = set(tgr_goods) | {f for f, v, c in additions}
            overlap = set(morg_goods) & already
            assert not overlap, 'wealth field collision on %s: %s' % (key, overlap)
            additions += [(f, v, 'Morgenrote') for f, v in sorted(morg_goods.items())]
            morg_used += 1

        chunks.append(insert_into_goods(decl, additions))

    header = (
        "# addon-VC only -- this file is in NONE of the three pair compatches.\n"
        "#\n"
        "# Why it exists: _vc/tgr+vc done, _vc/ef+vc done and _vc/morg+vc done each\n"
        "# restore something Victorian Century's REPLACE_OR_CREATE:wealth_N wiped --\n"
        "# TGR's consumption multipliers (full body, all 99 records), E&F's\n"
        "# popneed_currency / popneed_financial_products (INJECT, all 99) and\n"
        "# Morgenroete's popneed_entertainment (TRY_INJECT, wealth_10 up, 90 records).\n"
        "# Copied into the addon as three separate files they sort\n"
        "# zz_vc_ef_buy_packages.txt < zz_vc_morg_buy_packages.txt <\n"
        "# zz_vc_tgr_buy_packages.txt, so TGR's file -- a full REPLACE_OR_CREATE naming\n"
        "# none of E&F's or Morgenroete's fields -- would load LAST inside this one\n"
        "# addon mod and silently wipe both of their restorations again. Section 8 of\n"
        "# the working rules calls this the typical assembly conflict and prescribes\n"
        "# one merged file that loads last instead. This is that file: TGR's body plus\n"
        "# E&F's and Morgenroete's fields appended into the same `goods` block, all\n"
        "# three surviving together regardless of file name order.\n"
        "#\n"
        "# !! MAINTENANCE !! Generated by tools/regen_addon_vc.py from\n"
        "# _vc/tgr+vc done, _vc/ef+vc done and _vc/morg+vc done -- never hand-edit,\n"
        "# the next run overwrites this file. Re-run after any of those three\n"
        "# compatches changes. The generator asserts each source's prefix and field\n"
        "# set stay what they were when this was written; a failed assert means one\n"
        "# of the three pairs changed shape and the merge needs a fresh look, not a\n"
        "# silent re-run.\n"
        "\n"
    )
    text = header + '\n\n'.join(chunks) + '\n'
    assert brace_balance(text) == 0, 'generated file has unbalanced braces'
    return text, len(wealth_keys), ef_used, morg_used


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True)
    ap.add_argument('--check', action='store_true', help='verify only, change nothing')
    a = ap.parse_args(argv)

    text, n, ef_used, morg_used = build(a.repo)
    out_path = os.path.join(a.repo, OUT)

    if a.check:
        old = read(out_path) if os.path.exists(out_path) else None
        same = (old == text)
        print('%s: %s (%d wealth_N records, E&F fields on %d, Morgenrote fields on %d)'
              % (OUT, 'SAME' if same else 'DRIFT', n, ef_used, morg_used))
        return 0 if same else 1

    write(out_path, text)
    print('wrote %s: %d wealth_N records (E&F fields on %d, Morgenrote fields on %d)'
          % (OUT, n, ef_used, morg_used))
    return 0


if __name__ == '__main__':
    sys.exit(main())
