# -*- coding: utf-8 -*-
"""The Great Revision's three INJECT:s into ai_strategy_default, re-issued.

Kuromi's AI ships its whole default strategy as a bare body at the vanilla path
common/ai_strategies/00_default_strategy.txt.  A bare body in a later mod eats
every INJECT: that came before it, so all three of TGR's injection files vanish
the moment KAI is installed -- silently, because a missing injection is not an
error, the AI simply plays without it.

This module rebuilds those injections on top of whatever body actually wins
further down the chain (KAI's own body in the megapack; the KAI+MoH merge in
addon 1), and it is deliberately not a verbatim re-issue.  Sub-block by
sub-block:

    institution_scores          KAI leaves it at vanilla.  TGR adds twelve
                                institutions of its own -- pure loss, restored.
                                TGR also raises vanilla's police / health /
                                home_affairs from 10 to 500, and those three are
                                NOT restored here: Tech & Res re-states all seven
                                vanilla institutions at 10 in an injection that
                                loads after this file, so in the authors' own
                                order TGR's 500s are already gone.  Restoring
                                them would decide the TGR x T&R pair, not this
                                one.

    combat_unit_group_weights   KAI leaves it at vanilla.  TGR's restated entries
                                are byte-identical to vanilla except for three
                                new naval groups -- only those three are issued.

    conscript_battalion_ratio   KAI leaves it at vanilla.  TGR re-states the whole
                                block (it opens with `value = 0.5`, which resets
                                the accumulation, so a verbatim re-issue is exact)
                                to change one number, 2.5 -> 4.5.

    diplomatic_play_support     both authors claim it.  TGR opens its injection
                                with `value = 0`, which zeroes vanilla's scenario
                                list, and ships its own: German unification, five
                                Italian-unification blocks, foreign civil wars,
                                Alsace-Lorraine, the American-Mexican war, French
                                North Africa, Al Rif.  KAI keeps vanilla's list
                                and edits 36 lines inside it.  Merged here, by
                                the owner's decision: the winning body, minus its
                                German Leadership War block (TGR ships its own
                                version of that same scenario and the two would
                                add up), plus TGR's scenarios appended.

    wanted_construction_output  both authors rewrote the formula from the same
                                ancestor and both open with `value = 0`, so
                                whoever is issued last owns it outright.  Left to
                                KAI, by the owner's decision and by load order:
                                KAI is the later mod and this is an AI mod's core
                                competence.  Not issued here at all.

    icon                        TGR injects it, identical to vanilla.  Skipped.

Why an injection and not a REPLACE:.  Sub-blocks merge into the entry, and inside
one sub-block the game evaluates script-value statements in order: `value = X`
resets what came before, named entries (institution_*, combat_unit_group_*)
override the same name, anonymous `add = { }` blocks accumulate.  TGR's own files
are written for exactly that model -- every block TGR wants to own opens with a
`value =` reset, and in institution_scores TGR comments out the four vanilla
institutions it does not change and keeps only the three it does.  That is why a
re-issue reproduces "TGR without KAI" and why the merged diplomatic_play_support
below has to restate the winning body rather than only append to it.
"""
import os
import re

from vic3lib import read, entry, sub, sub_span, sub_names

GERMAN_MARK = '### German Leadership War'
AFTER_GERMAN_MARK = '### Schleswig War'

# TGR's file names, and which sub-block we take from each.
TGR_FILES = {
    'adjustments': 'common/ai_strategies/TGR_ADJUSTMENTS_default_strategy.txt',
    'politics': 'common/ai_strategies/TGR_POLITICS_default_strategy.txt',
    'trade': 'common/ai_strategies/TGR_TRADE_default_strategy.txt',
}


def _need(cond, msg):
    if not cond:
        raise SystemExit('SOURCE DRIFT: ' + msg)


def _ws(text):
    return re.sub(r'\s+', ' ', text or '').strip()


def _statement(body, name):
    """The whole `name = { ... }` statement at depth 0 of body, from the start of
    its own line so the foreign mod's indentation survives into our file."""
    span = sub_span(body, name)
    _need(span is not None, 'sub-block %s is gone' % name)
    start = body.rfind('\n', 0, span[0]) + 1
    return body[start:span[1]]


def _inner(block):
    return block[block.index('{') + 1:block.rindex('}')]


def _drop_leading_value_reset(inner):
    """Remove TGR's opening `value = 0` from an injected sub-block body."""
    lines = inner.split('\n')
    for i, line in enumerate(lines):
        if line.split('#')[0].strip() == 'value = 0':
            del lines[i]
            return '\n'.join(lines)
    _need(False, 'TGR diplomatic_play_support no longer opens with value = 0 -- '
                 'it no longer claims the whole block, and this merge is wrong')


def _cut_german_block(block):
    """Drop the German Leadership War scenario from the winning body."""
    a = block.find(GERMAN_MARK)
    b = block.find(AFTER_GERMAN_MARK)
    _need(a >= 0, 'winning diplomatic_play_support has no %r comment' % GERMAN_MARK)
    _need(b > a, 'winning diplomatic_play_support has no %r after it' % AFTER_GERMAN_MARK)
    a = block.rfind('\n', 0, a) + 1
    b = block.rfind('\n', 0, b) + 1
    return block[:a] + block[b:]


def _append_inside(block, extra):
    """Insert extra just before the closing brace of block, keeping that brace's
    own indentation."""
    close = block.rindex('}')
    line_start = block.rfind('\n', 0, close) + 1
    return (block[:line_start].rstrip('\n') + '\n\n'
            + extra.strip('\n') + '\n' + block[line_start:])


def read_sources(tgr_dir, van_dir, tr_dir):
    """Everything this module reads out of the foreign mods, in one place."""
    src = {}
    for name, rel in TGR_FILES.items():
        src[name] = entry(read(os.path.join(tgr_dir, rel)),
                          'ai_strategy_default', prefix='INJECT:')[1]
    src['vanilla'] = entry(read(os.path.join(van_dir, 'common/ai_strategies/00_default_strategy.txt')),
                           'ai_strategy_default')[1]
    src['t&r'] = entry(read(os.path.join(tr_dir, 'common/ai_strategies/ztr_default_strategy.txt')),
                       'ai_strategy_default', prefix='INJECT:')[1]
    return src


def build_body(base_body, src, notes=None):
    """Return the text of INJECT:ai_strategy_default = { ... } for a given winner.

    base_body is the body of the entry as it stands just before our file loads:
    KAI's bare body in the megapack, the KAI+MoH merge in addon 1.
    """
    say = notes.append if notes is not None else (lambda _s: None)
    van = src['vanilla']

    # ---- diplomatic_play_support: winning body minus its German block + TGR's list
    base_dps = sub(base_body, 'diplomatic_play_support')
    tgr_dps = sub(src['adjustments'], 'diplomatic_play_support')
    _need(base_dps and tgr_dps, 'diplomatic_play_support missing on one side')
    _need('TGR LINE START: DIPLOMATIC PLAY SUPPORT' in tgr_dps,
          'TGR stopped marking its diplomatic_play_support changes')
    merged_dps = _append_inside(_cut_german_block(base_dps),
                                _drop_leading_value_reset(_inner(tgr_dps)))
    say('diplomatic_play_support: winning body minus German Leadership War '
        '(TGR ships its own) + TGR\'s %d scenario lines'
        % len(_inner(tgr_dps).strip().split('\n')))

    # ---- institution_scores: TGR's own institutions only
    van_inst = sub(van, 'institution_scores')
    tgr_inst = sub(src['politics'], 'institution_scores')
    base_inst = sub(base_body, 'institution_scores')
    tr_inst = sub(src['t&r'], 'institution_scores')
    _need(_ws(base_inst) == _ws(van_inst),
          'the winning body no longer leaves institution_scores at vanilla -- '
          'somebody else now edits it and this merge has to be re-thought')
    van_names = set(sub_names(_inner(van_inst)))
    tgr_names = sub_names(_inner(tgr_inst))
    new_inst = [n for n in tgr_names if n not in van_names]
    shared = [n for n in tgr_names if n in van_names]
    _need(sorted(shared) == ['institution_health_system', 'institution_home_affairs',
                             'institution_police'],
          'TGR now re-states a different set of vanilla institutions: %s' % sorted(shared))
    for n in shared:
        _need(sub(_inner(tr_inst), n) is not None,
              'Tech & Res no longer re-states %s, so TGR\'s value for it is no longer '
              'overwritten downstream and the omission here is now a real loss' % n)
    _need(len(new_inst) == 12, 'TGR now adds %d institutions, not 12' % len(new_inst))
    say('institution_scores: TGR\'s %d institutions restored (its 500s for police / '
        'health / home affairs left to T&R, which re-states them at 10 later)'
        % len(new_inst))
    inst_body = '\n'.join(_statement(_inner(tgr_inst), n) for n in new_inst)

    # ---- combat_unit_group_weights: TGR's three naval groups
    van_cug = sub(van, 'combat_unit_group_weights')
    tgr_cug = sub(src['trade'], 'combat_unit_group_weights')
    base_cug = sub(base_body, 'combat_unit_group_weights')
    _need(_ws(base_cug) == _ws(van_cug),
          'the winning body no longer leaves combat_unit_group_weights at vanilla')
    van_cug_names = set(sub_names(_inner(van_cug)))
    tgr_cug_names = sub_names(_inner(tgr_cug))
    new_cug = [n for n in tgr_cug_names if n not in van_cug_names]
    for n in tgr_cug_names:
        if n in van_cug_names:
            _need(_ws(sub(_inner(tgr_cug), n)) == _ws(sub(_inner(van_cug), n)),
                  'TGR now changes vanilla\'s %s as well, not just adding new groups' % n)
    _need(len(new_cug) == 3, 'TGR now adds %d combat unit groups, not 3' % len(new_cug))
    say('combat_unit_group_weights: TGR\'s %d naval groups restored' % len(new_cug))
    cug_body = '\n'.join(_statement(_inner(tgr_cug), n) for n in new_cug)

    # ---- conscript_battalion_ratio: verbatim, it resets itself
    van_cbr = sub(van, 'conscript_battalion_ratio')
    base_cbr = sub(base_body, 'conscript_battalion_ratio')
    _need(_ws(base_cbr) == _ws(van_cbr),
          'the winning body no longer leaves conscript_battalion_ratio at vanilla')
    tgr_cbr = _statement(src['trade'], 'conscript_battalion_ratio')
    _need('value = 0.5' in tgr_cbr,
          'TGR\'s conscript_battalion_ratio no longer opens with a value reset, so '
          're-issuing it verbatim would stack on top of the winning body')
    say('conscript_battalion_ratio: TGR\'s block re-issued verbatim (national militia 2.5 -> 4.5)')

    # ---- wanted_construction_output: not ours to move
    base_wco = sub(base_body, 'wanted_construction_output')
    _need(_ws(base_wco) != _ws(sub(van, 'wanted_construction_output')),
          'the winning body now leaves wanted_construction_output at vanilla -- KAI '
          'stopped rewriting it, so TGR\'s version is a pure loss again and should be '
          'restored here')
    say('wanted_construction_output: left to KAI on purpose (both authors rewrote it '
        'whole; the later mod owns it)')

    return ('INJECT:ai_strategy_default = {\n'
            + '\t' + 'diplomatic_play_support = ' + merged_dps + '\n\n'
            + '\tinstitution_scores = {\n' + inst_body + '\n\t}\n\n'
            + '\tcombat_unit_group_weights = {\n' + cug_body + '\n\t}\n\n'
            + tgr_cbr + '\n'
            + '}\n')
