# -*- coding: utf-8 -*-
"""Generator for the TGR x KAI half of common/ai_strategies.

Writes one file:

    _tgr/tgr+kai done/common/ai_strategies/zz_kai_tgr_ai_default_strategy.txt

Tech & Res left the main set on 25.08.2026 and the old three-way TGR + T&R + KAI
compatch was split: its TGR x T&R half is now _tr/tgr+tr done, its KAI x T&R half
is _tr/kai+tr done, and what is left of the TGR x KAI pair is this one entry.
Of the 37 keys the two mods share it is the only one that needs a file -- see
conflicts_tgr_vs_kai_report.md next to the output for the other 36.

Kuromi's AI ships its default strategy as a bare body at the vanilla path, which
erases The Great Revision's three INJECT: files into the same entry.  Nothing in
error.log says so; the AI just stops using TGR's institutions, TGR's naval unit
weights, TGR's conscription ratio and TGR's diplomatic-play scenarios.  The merge
itself, and the two places where the two authors genuinely collide, are
documented in tgr_default_strategy.py and in conflicts_tgr_vs_kai_report.md.

Usage:
    python3 regen_tgr_kai_ai_default.py --root <vic3_mods_out> --out <vic3_mods>
    python3 regen_tgr_kai_ai_default.py --root ... --out ... --check
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vic3lib import read, write, entry, brace_balance
import tgr_default_strategy as tgrds

REL = '_tgr/tgr+kai done/common/ai_strategies/zz_kai_tgr_ai_default_strategy.txt'

HEADER = """\
### ComPatch: The Great Revision + Kuromi AI -- ai_strategy_default
###
### Load order (see README): CMF -> TGR -> KAI -> this patch.
###
### ai_strategy_default is the entry every AI country loads before its own
### strategy.  The Great Revision writes it with three INJECT: files
### (TGR_ADJUSTMENTS / TGR_POLITICS / TGR_TRADE_default_strategy.txt).  Kuromi's
### AI then ships its own body at the vanilla path
### common/ai_strategies/00_default_strategy.txt with no prefix at all -- and a
### bare body in a later mod eats every INJECT: that came before it.  All three
### of TGR's files disappear the moment KAI is installed.
###
### There is no error for this.  An injection that lands under a bare body is not
### a missing key, it is simply not applied: the AI never invests in TGR's twelve
### institutions, never weighs the three naval unit groups TGR added, keeps
### vanilla's conscription ratio, and takes no side in any of TGR's own wars.
###
### What this file re-issues, and what it deliberately does not:
###
###   institution_scores          TGR's block re-issued whole: its twelve own
###                               institutions plus its 10 -> 500 on vanilla's
###                               police / health_system / home_affairs.  Until
###                               25.08.2026 those three were NOT restored,
###                               because Tech & Res re-stated all seven vanilla
###                               institutions at 10 in an injection that loaded
###                               after this patch, so in the authors' own order
###                               TGR's 500s were already gone and putting them
###                               back would have decided the TGR x T&R pair
###                               rather than this one.  T&R has left the set.
###   combat_unit_group_weights   TGR's three naval groups (light / capital /
###                               support ship), restored.  The rest of TGR's
###                               block is byte-identical to vanilla.
###   conscript_battalion_ratio   TGR's block, verbatim: it opens with
###                               `value = 0.5`, so re-issuing it is exact.
###                               National militia 2.5 -> 4.5.
###   diplomatic_play_support     merged.  TGR opens its version with `value = 0`
###                               and ships its own scenario list (German
###                               unification, five Italian-unification blocks,
###                               foreign civil wars, Alsace-Lorraine, the
###                               American-Mexican war, French North Africa, Al
###                               Rif); KAI keeps vanilla's list and edits 36
###                               lines inside it.  Below is KAI's list minus its
###                               German Leadership War block -- TGR ships its own
###                               version of that same scenario and the two would
###                               add up -- with TGR's scenarios appended.
###   wanted_construction_output  NOT re-issued.  Both authors rewrote the whole
###                               formula from the same ancestor and both open
###                               with `value = 0`, so whoever is last owns it.
###                               KAI is the later mod and this is an AI mod's
###                               own subject; TGR's caps and its investment-pool
###                               term are left out on purpose.
###   icon                        TGR injects it identical to vanilla.  Skipped.
###
### !! MAINTENANCE !! generated by tools/regen_tgr_kai_ai_default.py, never edited
### by hand.  The bodies are cut out of TGR and KAI on every run, and the run
### stops if either author moves a line this merge depends on -- which is the only
### warning available, since none of this produces a line in error.log.
###
### VARIANTS: needs both The Great Revision and Kuromi's AI.

"""


def build(root):
    src = tgrds.read_sources(
        tgr_dir=os.path.join(root, 'TheGreatRevision'),
        van_dir=os.path.join(root, '.vanillaVIC3'))
    kai = read(os.path.join(root, 'TechRes+Kuromi', 'kai',
                            'common/ai_strategies/00_default_strategy.txt'))
    base = entry(kai, 'ai_strategy_default')[1]
    if 'KAI' not in base:
        raise SystemExit("SOURCE DRIFT: KAI's 00_default_strategy.txt no longer marks "
                         "its own changes")
    notes = []
    text = HEADER + tgrds.build_body(base, src, notes)
    return text, notes


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', required=True, help='path to vic3_mods_out (the foreign mods)')
    ap.add_argument('--out', required=True, help='path to vic3_mods (this repository)')
    ap.add_argument('--check', action='store_true',
                    help='compare against what is on disk, write nothing, exit 1 on a difference')
    args = ap.parse_args(argv)

    text, notes = build(args.root)
    bal = brace_balance(text)
    if bal:
        raise SystemExit('brace balance %+d in %s' % (bal, REL))

    print('--- what this run merged ---')
    for n in notes:
        print('  * ' + n)

    path = os.path.join(args.out, REL)
    if args.check:
        if not os.path.exists(path):
            print('  ! missing: ' + REL)
            return 1
        if read(path) != text:
            print('  ! differs: ' + REL)
            return 1
        print('0 file(s) out of date')
        return 0

    write(path, text)
    print('written %s' % path)
    return 0


if __name__ == '__main__':
    sys.exit(main())
