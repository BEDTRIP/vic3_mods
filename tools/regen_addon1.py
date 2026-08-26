# -*- coding: utf-8 -*-
"""Generator for Addon 1: HC + GoB + MoH  x  megapack.

Builds three pair compatches under _HC+GoB+MoH/ :

    hc+morg done      HC+GoB+MoH  x  Morgenroete
    hc+tgr done       HC+GoB+MoH  x  The Great Revision
    hc+kai done       HC+GoB+MoH  x  Kuromi's AI

Load order these are written for (see the addon README):

    ... megapack -> Hail Columbia -> Gates of the Bosphorus -> Mandate of Heaven
        -> THIS

so every file here is the last word on the entries it touches.

Nothing below is transcribed by hand from a foreign mod: each merged body is cut
out of the mods themselves at run time, and every place we rely on a particular
line existing is an assert.  When a foreign mod moves that line the run stops
with a readable message -- which is the only warning we get, because none of
these conflicts produce a single line in error.log.

Usage:
    python3 regen_addon1.py --root <vic3_mods_out> --out <vic3_mods>
    python3 regen_addon1.py --root ... --out ... --check   # compare only, exit 1 on drift
"""
import argparse, os, sys, re, subprocess, tempfile, filecmp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vic3lib import read, write, entry, sub, sub_span, sub_names, replace_sub, brace_balance
import tgr_default_strategy as tgrds

NOTES = []          # human-readable log of what this run merged


def note(s):
    NOTES.append(s)


def need(cond, msg):
    if not cond:
        raise SystemExit('SOURCE DRIFT: ' + msg)


def banner(*lines):
    out = []
    for l in lines:
        out.append(('### ' + l).rstrip())
    return '\n'.join(out) + '\n\n'


# =============================================================================
#  paths
# =============================================================================
class P(object):
    def __init__(self, root):
        self.van  = os.path.join(root, '.vanillaVIC3')
        self.tgr  = os.path.join(root, 'TheGreatRevision')
        self.kai  = os.path.join(root, 'TechRes+Kuromi', 'kai')
        self.morg = os.path.join(root, 'Morgenrote')
        self.hc   = os.path.join(root, 'for addon', 'hailcolumbia')
        self.gob  = os.path.join(root, 'for addon', 'gatesofbosphorus')
        self.moh  = os.path.join(root, 'for addon', 'mandateofheaven')


# =============================================================================
#  compatch 1:  HC+GoB+MoH  x  Morgenroete
# =============================================================================
def build_morg(p):
    files = {}

    # -- gaudi static modifier ------------------------------------------------
    # GoB ships common/static_modifiers/zz_gbbf_placeholder_modifiers.txt so that
    # its Byzantium journal entry can say has_modifier = gaudi_..._level_4 even
    # when Morgenroete is absent.  The stub is a bare key with nothing but an
    # icon in it, GoB loads after Morgenroete, and a bare body replaces the whole
    # entry -- so with both mods on, Gaudi's level 4 capital expansion silently
    # becomes a modifier that modifies nothing.
    mr_gaudi = entry(read(os.path.join(p.morg, 'common/static_modifiers/mr_arts_gaudi_modifiers.txt')),
                     'gaudi_capital_expansion_level_4_modifier')[0]
    need('state_infrastructure_add' in mr_gaudi,
         'Morgenroete gaudi_capital_expansion_level_4_modifier no longer carries state modifiers')
    gob_gaudi = entry(read(os.path.join(p.gob, 'common/static_modifiers/zz_gbbf_placeholder_modifiers.txt')),
                      'gaudi_capital_expansion_level_4_modifier')[1]
    need('state_infrastructure_add' not in gob_gaudi,
         'GoB placeholder gaudi modifier is no longer a placeholder -- re-read it before regenerating')
    files['common/static_modifiers/zz_hcm_gaudi_modifier.txt'] = banner(
        'ComPatch HC+GoB+MoH x Morgenroete -- Gaudi capital expansion, level 4',
        '',
        'Gates of the Bosphorus carries a stub of this modifier in',
        'common/static_modifiers/zz_gbbf_placeholder_modifiers.txt with nothing in it',
        'but an icon.  The stub exists so that the Byzantium journal entry',
        '(1-20_grefm_byzantium.txt, has_modifier = gaudi_capital_expansion_level_4_modifier',
        'under a morgenrote_is_active gate) still resolves when Morgenroete is not',
        'installed -- reasonable on its own.  But GoB loads after Morgenroete, and a',
        'bare body replaces the entry outright, so with both mods installed Gaudi\'s',
        'level 4 modifier loses all eight of its state modifiers and becomes an icon.',
        'Silent: the modifier still exists, so nothing is logged.',
        '',
        'Below is Morgenroete\'s body, re-issued last.  GoB keeps its guard (the key',
        'exists either way) and Morgenroete keeps its numbers.',
        '',
        '!! MAINTENANCE !! body copied from Morgenroete',
        'common/static_modifiers/mr_arts_gaudi_modifiers.txt -- re-run this generator',
        'after a Morgenroete update.') + mr_gaudi + '\n'
    note('gaudi_capital_expansion_level_4_modifier: restored Morgenroete body over GoB placeholder')

    # -- Olympic games decision ----------------------------------------------
    # Morgenroete hides the vanilla one-shot decision because it ships a whole
    # Olympics system (Vikelas: journal entry, scripted GUI, traits, PMs).  GoB
    # reworks the same decision into a Greek one and loads later, so with both
    # mods the player gets both Olympics at once.  Decision: Morgenroete's wins.
    mr_dec = read(os.path.join(p.morg, 'common/decisions/vanilla_decisions.txt'))
    decl, body = entry(mr_dec, 'revive_olympic_games_decision', prefix='TRY_REPLACE:')
    need('always = no' in sub(body, 'is_shown'),
         'Morgenroete no longer hides revive_olympic_games_decision -- the fork below is stale')
    gob_dec = entry(read(os.path.join(p.gob, 'common/decisions/1-00_grefm_greece_decisions.txt')),
                    'revive_olympic_games_decision', prefix='REPLACE:')[1]
    need('cu:greek' in gob_dec, 'GoB no longer reworks revive_olympic_games_decision')
    files['common/decisions/zz_hcm_olympic_games.txt'] = banner(
        'ComPatch HC+GoB+MoH x Morgenroete -- the vanilla Olympics decision',
        '',
        'Two authors take the vanilla revive_olympic_games_decision in opposite',
        'directions.  Morgenroete hides it (is_shown = always no) because it replaces',
        'it with a full mechanic -- je_vikelas_olympics, scripted GUI, character',
        'traits, production methods.  Gates of the Bosphorus rewrites the same',
        'decision into a Greek one: Attica plus organized_sports, two modifiers.',
        '',
        'GoB loads after Morgenroete, so as shipped the player gets Morgenroete\'s',
        'Olympics system AND a second, unrelated Olympics decision.  Not a bug in',
        'either mod, and nothing is logged -- it just reads as duplicated content.',
        '',
        'We re-issue Morgenroete\'s suppression last.  Greece loses one flavour',
        'decision; Morgenroete\'s Olympics remain the only ones in the game.',
        '',
        '!! MAINTENANCE !! if Morgenroete ever drops its Olympics system this file',
        'has to go, or the Olympics disappear entirely.') \
        + 'REPLACE:revive_olympic_games_decision = {' + body + '}\n'
    note('revive_olympic_games_decision: Morgenroete suppression re-issued over GoB Greek rework')

    # -- character templates --------------------------------------------------
    files['common/character_templates/zz_hcm_characters.txt'] = _morg_characters(p)

    # -- achievement groups ---------------------------------------------------
    files['common/achievement_groups.txt'] = _achievement_groups(p)

    return files


def _morg_characters(p):
    """Walter Chrysler and Mark Twain: HC's body, Morgenroete's role."""
    hc_exec = read(os.path.join(p.hc, 'common/character_templates/usfp_characters_executives.txt'))
    hc_usa  = read(os.path.join(p.hc, 'common/character_templates/country_usa.txt'))
    mr_eng  = read(os.path.join(p.morg, 'common/character_templates/mr_science_tesla_engineers_politician.txt'))
    mr_wri  = read(os.path.join(p.morg, 'common/character_templates/mr_arts_manzoni_writers.txt'))

    out = [banner(
        'ComPatch HC+GoB+MoH x Morgenroete -- two shared characters',
        '',
        'Morgenroete and Hail, Columbia! both define Walter Chrysler and Mark Twain,',
        'under the same template keys, for different jobs:',
        '',
        '  Chrysler  MR: role = character_role_tesla_engineer, engineer traits, an',
        '                on_created that registers him with MR\'s engineer system',
        '            HC: executive_usage for company_basic_motors, 1915-1940',
        '  Twain     MR: role = character_role_manzoni_writer, writer traits + genre,',
        '                on_created registering him with MR\'s writer system',
        '            HC: is_agitator + agitator_usage, Missouri, 1865-1910',
        '',
        'HC loads later and both its bodies are bare, so each replaces the whole entry',
        'and Morgenroete\'s two characters quietly stop existing as far as its own',
        'mechanics are concerned -- the templates are still there, they just no longer',
        'carry the role or run the on_created that hooks them up.  No log line.',
        '',
        'Merged below: HC\'s body is the base (it is the last full body and the more',
        'specific one -- these are American characters in an American flavour mod),',
        'plus Morgenroete\'s role, its two mechanic-bearing traits and its on_created.',
        'MR\'s purely descriptive traits (ambitious, erudite/reckless duplicates) are',
        'not carried over: HC already gives each character a full trait list and the',
        'union would run to seven traits.',
        '',
        '!! MAINTENANCE !! both bodies are cut out of the mods at generation time.',
        'Re-run after either mod updates.  If a future game version rejects `role`',
        'next to executive_usage / agitator_usage this is the file to look at -- the',
        'combination exists in neither vanilla nor either mod.')]

    # ---- Chrysler -----------------------------------------------------------
    hc_b = entry(hc_exec, 'ecchi_usa_chrysler_character_template')[1]
    mr_b = entry(mr_eng,  'ecchi_usa_chrysler_character_template')[1]
    need('executive_usage' in hc_b, 'HC Chrysler no longer has executive_usage')
    need('role = character_role_tesla_engineer' in mr_b, 'MR Chrysler no longer a tesla engineer')
    mr_created = sub(mr_b, 'on_created')
    need(mr_created and 'mr_make_character_engineer_effect' in mr_created,
         'MR Chrysler on_created no longer calls mr_make_character_engineer_effect')
    need(sub(hc_b, 'on_created') is None, 'HC Chrysler grew an on_created -- merge it by hand')
    b = _add_line_after(hc_b, r'dna\s*=', '\trole = character_role_tesla_engineer')
    b = _add_line_after(b, r'role\s*=\s*character_role_tesla_engineer', '\thistorical = yes')
    b = _add_traits(b, ['engineer', 'tesla_mechanical_engineer'])
    b = b.rstrip('\n \t') + '\n\t# Morgenroete: registers him with the Tesla engineer system.\n\ton_created = ' \
        + mr_created + '\n'
    out.append('ecchi_usa_chrysler_character_template = {' + b + '}\n')
    note('ecchi_usa_chrysler_character_template: HC executive body + MR tesla-engineer role/on_created')

    # ---- Mark Twain ---------------------------------------------------------
    hc_b = entry(hc_usa, 'usa_mark_twain_character_template')[1]
    mr_b = entry(mr_wri, 'usa_mark_twain_character_template', prefix='TRY_REPLACE:')[1]
    need('agitator_usage' in hc_b, 'HC Twain no longer has agitator_usage')
    need('role = character_role_manzoni_writer' in mr_b, 'MR Twain no longer a manzoni writer')
    mr_dna = re.search(r'(?m)^\tdna\s*=\s*(\S+)', mr_b)
    need(mr_dna is not None, 'MR Twain no longer carries a dna')
    mr_created = sub(mr_b, 'on_created')
    need(mr_created and 'mr_make_character_writer_effect' in mr_created,
         'MR Twain on_created no longer calls mr_make_character_writer_effect')
    hc_created = sub(hc_b, 'on_created')
    need(hc_created is not None, 'HC Twain lost its on_created')
    b = _add_line_after(hc_b, r'first_name\s*=', '\tdna = ' + mr_dna.group(1))
    b = _add_line_after(b, r'dna\s*=', '\trole = character_role_manzoni_writer')
    b = _add_traits(b, ['manzoni_writer_fiction', 'manzoni_genre_adventure'])
    # HC's ideology ladder is the newer one (has_law_or_variant, extra branches),
    # so it stays; Morgenroete's three registration lines go in front of it.
    reg = ['\t\tset_variable = mr_no_headgear_var',
           '\t\tmr_make_character_writer_effect = yes',
           '\t\tset_global_variable = mr_twain_created_global_var']
    for line in reg:
        need(line.strip() in re.sub(r'[ \t]+', ' ', mr_created).replace(' =', ' ='),
             'MR Twain on_created no longer contains ' + line.strip())
    new_created = '{\n\t\t# Morgenroete: registers him with the Manzoni writer system.\n' \
                  + '\n'.join(reg) + '\n' + hc_created[1:]
    b = replace_sub(b, 'on_created', new_created)
    out.append('usa_mark_twain_character_template = {' + b + '}\n')
    note('usa_mark_twain_character_template: HC agitator body + MR writer role/dna/on_created')

    return '\n'.join(out)


def _indent_of(body):
    """The indent string this body uses for its own top-level lines."""
    m = re.search(r'(?m)^([ \t]+)[A-Za-z_]', body)
    return m.group(1) if m else '\t'


def _add_line_after(body, pattern, line):
    """Insert `line` (given with a leading TAB) after the first depth-0 line
    matching `pattern`, re-indented to whatever the body already uses."""
    ind = _indent_of(body)
    m = re.search(r'(?m)^[ \t]*' + pattern + r'.*$', body)
    need(m is not None, 'anchor line /%s/ not found' % pattern)
    return body[:m.end()] + '\n' + ind + line.lstrip('\t') + body[m.end():]


def _add_traits(body, extra):
    ind = _indent_of(body)
    m = re.search(r'(?m)^[ \t]*traits\s*=\s*\{([^}]*)\}', body)
    need(m is not None, 'traits block not found or not flat')
    have = m.group(1).split()
    merged = have + [t for t in extra if t not in have]
    return body[:m.start()] + ind + 'traits = { ' + ' '.join(merged) + ' }' + body[m.end():]


def _achievement_groups(p):
    """common/achievement_groups.txt -- Morgenroete's groups plus MoH's entries.

    Three mods ship this file at the vanilla path.  It has no top-level keys (it
    is a list of anonymous `group = {}` blocks), so the only way to touch it is a
    path override, and the last mod wins the whole file.  Mandate of Heaven is
    last, so Morgenroete's twelve achievement groups vanish from the achievements
    screen and one vanilla achievement loses its group as well.
    """
    van  = read(os.path.join(p.van,  'common/achievement_groups.txt'))
    mr   = read(os.path.join(p.morg, 'common/achievement_groups.txt'))
    moh  = read(os.path.join(p.moh,  'common/achievement_groups.txt'))

    # Morgenroete = vanilla + its own groups appended, verbatim.
    need(mr.startswith(van.rstrip('\n')) or van.rstrip('\n') in mr,
         'Morgenroete achievement_groups.txt is no longer vanilla + appended groups')
    mr_extra = mr[mr.index(van.rstrip('\n')) + len(van.rstrip('\n')):]
    need('lepsius_achievement_group' in mr_extra,
         'Morgenroete achievement groups not found in the appended tail')

    # MoH = an older vanilla with its own achievements slotted into the existing
    # groups.  It drops achievement_exactly_100, which current vanilla has.
    need('achievement_wuxu_reform' in moh, 'MoH no longer adds its achievements here')
    need('achievement_exactly_100' not in moh and 'achievement_exactly_100' in van,
         'MoH/vanilla no longer disagree about achievement_exactly_100 -- re-check this merge')
    merged = moh.rstrip('\n')
    # put the vanilla achievement MoH dropped back where vanilla has it
    anchor = _line_before(van, 'achievement_exactly_100')
    need(anchor is not None, 'cannot locate achievement_exactly_100 context in vanilla')
    need(anchor in merged, 'vanilla anchor %r missing from MoH file' % anchor)
    merged = merged.replace(anchor, anchor + '\n\t\t"achievement_exactly_100"', 1)

    note('achievement_groups.txt: MoH base + 12 Morgenroete groups + achievement_exactly_100 restored')
    return banner(
        'ComPatch HC+GoB+MoH x Morgenroete -- the achievements screen',
        '',
        'This file has no top-level keys: it is a list of anonymous `group = {}`',
        'blocks, so INJECT: has nothing to attach to and the only tool is a path',
        'override.  Vanilla, Morgenroete and Mandate of Heaven all ship it, MoH loads',
        'last, and its copy wins entirely.  Two things are lost:',
        '',
        '  * Morgenroete\'s twelve achievement groups (lepsius, verrier, elgar, gaudi,',
        '    curtiss, dubois, andersson, agassiz, mendelejew, panum, douglas, vikelas)',
        '    -- roughly sixty achievements stop being grouped and drop off the screen;',
        '  * achievement_exactly_100, which current vanilla lists and MoH\'s copy does',
        '    not.  MoH\'s file is built on a slightly older vanilla.',
        '',
        'Neither shows up in any log -- achievements simply are not there.',
        '',
        'Merged below: MoH\'s file (it has MoH\'s own achievements slotted into the',
        'vanilla groups), with achievement_exactly_100 put back and Morgenroete\'s',
        'groups appended unchanged.',
        '',
        '!! MAINTENANCE !! all three copies are read at generation time.  A new',
        'vanilla achievement lands here only if MoH picks it up; check this file',
        'against vanilla after a game patch.') + merged + '\n' + mr_extra.lstrip('\n') + '\n'


def _line_before(text, needle):
    lines = text.split('\n')
    for i, l in enumerate(lines):
        if needle in l:
            return lines[i - 1] if i else None
    return None


def merge3(base, ours, theirs, label, resolve=None):
    """Three-way text merge (git merge-file).  `resolve` may inspect each
    conflict and return the text to use; without it a conflict is fatal."""
    with tempfile.TemporaryDirectory() as d:
        fb, fo, ft = (os.path.join(d, n) for n in ('base', 'ours', 'theirs'))
        for path, txt in ((fb, base), (fo, ours), (ft, theirs)):
            open(path, 'w', encoding='utf-8', newline='\n').write(txt)
        r = subprocess.run(['git', 'merge-file', '-p', '--diff3',
                            '-L', 'ours', '-L', 'base', '-L', 'theirs', fo, fb, ft],
                           capture_output=True, text=True)
        out = r.stdout
    if '<<<<<<<' not in out:
        return out
    if resolve is None:
        raise SystemExit('MERGE CONFLICT in %s -- resolve it in the generator:\n%s'
                         % (label, out[:2000]))
    return _resolve_conflicts(out, resolve, label)


def _resolve_conflicts(text, resolve, label):
    lines, out, i, n = text.split('\n'), [], 0, 0
    while i < len(lines):
        if lines[i].startswith('<<<<<<<'):
            j = i
            while not lines[j].startswith('>>>>>>>'):
                j += 1
            blk = lines[i:j + 1]
            a, b = blk.index('||||||| base'), blk.index('=======')
            n += 1
            take = resolve(blk[1:a], blk[a + 1:b], blk[b + 1:-1], n)
            if take is None:
                raise SystemExit('MERGE CONFLICT %d in %s left unresolved:\n%s'
                                 % (n, label, '\n'.join(blk)[:2000]))
            out.extend(take)
            i = j + 1
        else:
            out.append(lines[i])
            i += 1
    return '\n'.join(out)


def _ws(lines):
    return re.sub(r'\s+', ' ', ' '.join(lines)).strip()


# =============================================================================
#  compatch 2:  HC+GoB+MoH  x  The Great Revision
# =============================================================================
def build_tgr(p):
    files = {}
    van_lo = read(os.path.join(p.van, 'common/interest_groups/00_landowners.txt'))
    van_rf = read(os.path.join(p.van, 'common/interest_groups/00_rural_folk.txt'))
    tgr_lo = read(os.path.join(p.tgr, 'common/interest_groups/TGR_POLITICS_landowners.txt'))
    tgr_rf = read(os.path.join(p.tgr, 'common/interest_groups/TGR_POLITICS_rural_folk.txt'))
    hc_lo  = read(os.path.join(p.hc,  'common/interest_groups/00_landowners.txt'))
    hc_rf  = read(os.path.join(p.hc,  'common/interest_groups/00_rural_folk.txt'))
    moh_rf = read(os.path.join(p.moh, 'common/interest_groups/moh_rural_folk.txt'))

    files['common/interest_groups/zz_hct_ig_landowners.txt'] = _ig_landowners(van_lo, tgr_lo, hc_lo)
    files['common/interest_groups/zz_hct_ig_rural_folk.txt'] = _ig_rural_folk(van_rf, tgr_rf, hc_rf, moh_rf)
    files['common/ideologies/zz_hct_jacksonian_democrat.txt'] = _jacksonian(p)
    files['common/history/countries/chi - china.txt'] = _history_china(p)
    files['common/history/countries/tur - ottoman empire.txt'] = _history_ottoman(p)
    return files


IG_HEAD = (
    'Both interest groups below are re-issued as one complete REPLACE: body.',
    'That is deliberate and it is the expensive option: REPLACE: swaps the whole',
    'entry, so a partial body would drop everything it does not name.  Proved in',
    'game 21.08.2026 -- REPLACE:building_bank = { ownership_type = self } made the',
    'central bank disappear, and 285 production methods restated with only',
    'building_modifiers lost their unlocking_laws.',
)


def _ig_landowners_body(van, tgr, hc):
    """HC+TGR merge of ig_landowners, before any optional-mod layer (e.g.
    Victorian Century's rework -- see the standalone hc+vc compatch under
    _HC+GoB+MoH/hc+vc done, which imports this function via `regen_addon1`
    and layers VC's on_enable/pop_potential/pop_weight rework on top). The
    scope-safety fix is a real bug independent of any optional mod (TGR's own
    source already carries it), so it applies here regardless."""
    v = entry(van, 'ig_landowners')[1]
    t = entry(tgr, 'ig_landowners', prefix='REPLACE_OR_CREATE:')[1]
    h = entry(hc,  'ig_landowners')[1]
    vw, tw, hw = sub(v, 'pop_weight'), sub(t, 'pop_weight'), sub(h, 'pop_weight')
    need('0.030' in tw, 'TGR no longer raises the LEADER_POPULARITY multiplier in ig_landowners')
    need('0.0025' in hw, 'HC ig_landowners no longer carries the vanilla LEADER_POPULARITY multiplier')
    merged = merge3(vw, tw, hw, 'ig_landowners/pop_weight', resolve=_ig_resolve)
    need('0.030' in merged and 'USFP' in merged,
         'ig_landowners/pop_weight merge lost either TGR\'s multiplier or HC\'s planters rule')
    return replace_sub(h, 'pop_weight', _safe_scope(merged, 'ig_landowners/pop_weight'))


def _ig_landowners(van, tgr, hc):
    body = _ig_landowners_body(van, tgr, hc)
    note('ig_landowners: HC+TGR body merged (three-way against vanilla); scope:interest_group '
         'restored to the safe ?= form throughout, including one occurrence TGR itself had '
         'already silently downgraded')
    return banner(
        'ComPatch HC+GoB+MoH x The Great Revision -- ig_landowners',
        '',
        'TGR reworks this interest group from TGR_POLITICS_landowners.txt with',
        'REPLACE_OR_CREATE:.  Hail, Columbia! ships',
        'common/interest_groups/00_landowners.txt -- the vanilla path, a bare body --',
        'and loads last of the two, so TGR\'s version is gone entirely.  Silent; the',
        'interest group still exists, it just has vanilla\'s content back.',
        '',
        'What TGR actually changes here is one line: in pop_weight, the LEADER_POPULARITY',
        'multiplier goes from 0.0025 to 0.030, i.e. a popular leader pulls twelve times',
        'as hard.  Everything else in TGR\'s 772-line body is vanilla.',
        '',
        'What HC changes: usfp_country_is_american in on_enable, and a pop_weight rule',
        'that zeroes Southern planters outside slave states during the Civil War.',
        '',
        'Merged below: HC\'s body with TGR\'s multiplier folded into pop_weight.',
        '',
        'TGR\'s own `scope:interest_group ?= {` -> `= {` downgrade in the',
        'LEADER_POPULARITY block is not carried: vanilla and HC use the safe-scope',
        'form, and the strict form is the one that can go wrong.  Restored to `?=`.',
        '',
        'VARIANTS: safe in every megapack composition -- the merged body names no TGR',
        'entity, only numbers and vanilla trait/ideology keys.  Victorian Century',
        'reworks this same interest group too -- if VC is part of the composition,',
        'load the standalone HC+GoB+MoH x TGR x VC compatch',
        '(_HC+GoB+MoH/hc+vc done) after this addon; it REPLACEs this same path,',
        'layering VC\'s on_enable/pop_potential/pop_weight rework on top of the exact',
        'body below.',
        *IG_HEAD) + 'REPLACE:ig_landowners = {' + body + '}\n'


def _ig_resolve(ours, base, theirs, n):
    """Conflict policy for the interest-group pop_weight merges.

    Hail, Columbia! and vanilla differ in trailing whitespace in a dozen places,
    which turns into spurious conflicts.  Anything that is whitespace-identical
    on one side is resolved to the side that actually changed something.
    """
    if _ws(theirs) == _ws(base):
        return ours
    if _ws(ours) == _ws(base):
        return theirs
    if _ws(ours) == _ws(theirs):
        return ours
    return None


def _safe_scope(text, label):
    """Restore `scope:interest_group ?= {` wherever a source silently dropped
    the `?`."""
    fixed = text.replace('scope:interest_group = {', 'scope:interest_group ?= {')
    need('scope:interest_group = {' not in fixed,
         '%s: still found an unsafe scope:interest_group = { form after the '
         'safety fix -- re-read the merged pop_weight' % label)
    return fixed


def _ig_rural_folk_body(van, tgr, hc, moh):
    """HC+TGR+MoH merge of ig_rural_folk, before any optional-mod layer (e.g.
    Victorian Century's rework -- see the standalone hc+vc compatch under
    _HC+GoB+MoH/hc+vc done, which imports this function via `regen_addon1`
    and layers VC's on_enable/pop_potential/pop_weight rework on top)."""
    v = entry(van, 'ig_rural_folk')[1]
    t = entry(tgr, 'ig_rural_folk', prefix='REPLACE_OR_CREATE:')[1]
    h = entry(hc,  'ig_rural_folk')[1]
    m = entry(moh, 'ig_rural_folk', prefix='INJECT:')[1]

    tw = sub(t, 'pop_weight')
    need('value = 250' in tw and 'value = 150' in tw,
         'TGR no longer rebalances POP_FARMERS/POP_PEASANTS in ig_rural_folk')
    merged = merge3(sub(v, 'pop_weight'), tw, sub(h, 'pop_weight'),
                    'ig_rural_folk/pop_weight', resolve=_ig_resolve)
    need('value = 250' in merged and '0.030' in merged,
         'ig_rural_folk/pop_weight merge lost TGR\'s numbers')
    body = replace_sub(h, 'pop_weight', _safe_scope(merged, 'ig_rural_folk/pop_weight'))

    # Mandate of Heaven INJECTs this entry, but almost all of what it injects is a
    # restatement of a PRE-1.13 vanilla body.  Keep only the parts that are its own.
    kept, dropped = [], []
    for nm in sub_names(m):
        mb, vb = sub(m, nm), sub(v, nm)
        new_ids = _ids(mb) - (_ids(vb) if vb else set())
        if vb is None:
            dropped.append((nm, 'not a 1.13 field'))
        elif not new_ids or new_ids <= {'has_law'}:
            # has_law is the pre-1.13 spelling of has_law_or_variant
            dropped.append((nm, 'restates vanilla' if not new_ids else 'pre-1.13 has_law'))
        else:
            kept.append(nm)
    need(sorted(kept) == ['character_ideologies', 'on_enable'],
         'Mandate of Heaven now contributes %s to ig_rural_folk -- re-read moh_rural_folk.txt'
         % sorted(kept))

    ideo = sub(m, 'character_ideologies').strip('{} \n\t')
    need('ideology_moh_kmt' in ideo, 'MoH no longer adds ideology_moh_kmt')
    body = replace_sub(body, 'character_ideologies',
                       _open_block(sub(body, 'character_ideologies')).rstrip()
                       + '\n\t\t# Mandate of Heaven\n\t\t' + ideo.strip() + '\n\t}')
    nong = sub(m, 'on_enable').strip()
    inner = nong[1:-1].strip('\n')
    need('set_interest_group_name = ig_farmers' in inner, 'MoH Nongmin rename block moved')
    body = replace_sub(body, 'on_enable',
                       _open_block(sub(body, 'on_enable')).rstrip()
                       + '\n\n\t\t# Mandate of Heaven: Nongmin.\n' + inner + '\n\t}')

    note('ig_rural_folk: HC body + TGR farmers/peasants/leader numbers + MoH kmt ideology and Nongmin rename '
         '(dropped as stale pre-1.13 copies: %s); scope:interest_group restored to the safe ?= form '
         'throughout, including one occurrence TGR itself had already silently downgraded'
         % ', '.join(n for n, _ in dropped))
    return body


def _ig_rural_folk(van, tgr, hc, moh):
    body = _ig_rural_folk_body(van, tgr, hc, moh)
    return banner(
        'ComPatch HC+GoB+MoH x The Great Revision -- ig_rural_folk',
        '',
        'Three mods write this entry:',
        '',
        '  TGR   REPLACE_OR_CREATE: from TGR_POLITICS_rural_folk.txt.  Its real change',
        '        is three numbers in pop_weight: POP_FARMERS 200 -> 250, POP_PEASANTS',
        '        200 -> 150, LEADER_POPULARITY 0.0025 -> 0.030.',
        '  HC    a bare body at the vanilla path 00_rural_folk.txt -- so all of TGR is',
        '        gone.  HC\'s own changes: usfp_country_is_american in on_enable and an',
        '        aristocrat/American-culture rule in pop_potential.',
        '  MoH   INJECT: from moh_rural_folk.txt, 316 lines.',
        '',
        'The MoH file needs saying out loud: of its fifteen sub-blocks, exactly two are',
        'its own -- ideology_moh_kmt in character_ideologies, and the on_enable block',
        'that renames the IG to Nongmin for Chinese cultures.  The other thirteen are a',
        'copy of a PRE-1.13 vanilla body: has_law where 1.13 has has_law_or_variant,',
        '`scope:interest_group = {` where 1.13 has `?= {`, an EMPTY',
        'on_character_ig_membership where vanilla has the Zanzibar religion rule, a',
        'priority_cultures missing vanilla\'s ZAN rule, and commander_leader_chance,',
        'which 1.13 renamed to commander_leader_weight.  Whatever the engine does with',
        'a sub-block INJECT:ed on top of one that already exists, that copy can only',
        'take things away.  Same class as the stale ai_strategies file in LLWA.',
        '',
        'Merged below: HC\'s body (current vanilla plus HC\'s two edits), TGR\'s three',
        'numbers merged into pop_weight three-way against vanilla, and MoH\'s two real',
        'additions appended.  Nothing from MoH\'s stale copy is carried.',
        '',
        'TGR\'s own `scope:interest_group ?= {` -> `= {` downgrade is not carried,',
        'for the same reason as in ig_landowners -- restored to `?=` throughout.',
        '',
        'VARIANTS: safe in every composition -- ideology_moh_kmt and the Nongmin rename',
        'come from Mandate of Heaven, which is part of this addon\'s own block; the TGR',
        'contribution is numbers only.  Victorian Century reworks this same interest',
        'group too -- if VC is part of the composition, load the standalone',
        'HC+GoB+MoH x TGR x VC compatch (_HC+GoB+MoH/hc+vc done) after this addon;',
        'it REPLACEs this same path, layering VC\'s on_enable/pop_potential/pop_weight',
        'rework on top of the exact body below.',
        *IG_HEAD) + 'REPLACE:ig_rural_folk = {' + body + '}\n'


def _open_block(block):
    """Drop the final closing brace of a `{ ... }` text, keeping everything else."""
    i = block.rindex('}')
    return block[:i]


def _ids(t):
    return set(re.findall(r'[A-Za-z_][A-Za-z_0-9:]*', re.sub(r'#[^\n]*', '', t or '')))


def _jacksonian_tgr_body(p):
    """HC+TGR merge of ideology_jacksonian_democrat, before any optional-mod
    layer (e.g. Victorian Century's law stances -- see the standalone hc+vc
    compatch under _HC+GoB+MoH/hc+vc done, which imports this function via
    `regen_addon1` and folds VC's laws on top)."""
    hc  = read(os.path.join(p.hc,  'common/ideologies/usfp_ideology_overrides.txt'))
    tgr = read(os.path.join(p.tgr, 'common/ideologies/TGR_POLITICS_character_ideologies.txt'))
    h = entry(hc,  'ideology_jacksonian_democrat', prefix='REPLACE_OR_CREATE:')[1]
    t = entry(tgr, 'ideology_jacksonian_democrat', prefix='INJECT:')[1]

    tgr_add = [nm for nm in sub_names(t)]
    need(tgr_add == ['lawgroup_election_system', 'lawgroup_legislative_process'],
         'TGR now injects %s into ideology_jacksonian_democrat' % tgr_add)
    for nm in tgr_add:
        need(sub(h, nm) is None, 'HC now defines %s itself -- decide which stance wins' % nm)

    tgr_lines = ['\n\t# The Great Revision\n\t%s = %s' % (nm, sub(t, nm)) for nm in tgr_add]
    tail = '\n'.join(tgr_lines)
    body = _open_block('{' + h + '}')[1:].rstrip() + '\n' + tail + '\n}'
    note('ideology_jacksonian_democrat: HC body + TGR two law-group stances appended')
    return body


def _jacksonian(p):
    body = _jacksonian_tgr_body(p)
    return banner(
        'ComPatch HC+GoB+MoH x The Great Revision -- ideology_jacksonian_democrat',
        '',
        'TGR INJECT:s two law stances into this ideology -- lawgroup_election_system and',
        'lawgroup_legislative_process, five laws each.  Hail, Columbia! then rewrites the',
        'whole ideology with REPLACE_OR_CREATE: and names neither, so both stances are',
        'dropped: REPLACE swaps the entry, it does not patch the sub-blocks a mod',
        'happens to list.  A Jacksonian leader ends up with no opinion at all on either',
        'law group, which reads as "neutral" everywhere and is logged nowhere.',
        '',
        'Merged below: HC\'s body with TGR\'s two stance blocks appended.  They do not',
        'overlap -- HC names governance_principles, distribution_of_power, bureaucracy,',
        'colonization and land_reform; TGR falls outside that list.',
        '',
        'VARIANTS: needs TGR -- the appended blocks are its balance, not vanilla\'s.',
        'Victorian Century adds its own law stances to this same ideology too -- if VC',
        'is part of the composition, load the standalone HC+GoB+MoH x TGR x VC compatch',
        '(_HC+GoB+MoH/hc+vc done) after this addon; it REPLACE_OR_CREATE:s this same',
        'entry, folding VC\'s laws into HC\'s pre-existing groups and appending VC\'s six',
        'new stance blocks on top of the exact body below.') \
        + 'REPLACE_OR_CREATE:ideology_jacksonian_democrat = {' + body[:-1] + '}\n'


def _history_merge(p, relpath, winner_dir, winner_name, tgr_anchor, hdr_lines):
    """Country history file that a mod of this addon overrides at the vanilla path,
    dropping TGR's addition to the same country."""
    tgr = read(os.path.join(p.tgr, relpath))
    win = read(os.path.join(winner_dir, relpath))
    m = re.search(r'(?ms)^(\t*)add_company = company_type:%s\b.*?\n\1\}\n' % re.escape(tgr_anchor), tgr)
    need(m is not None, 'TGR no longer adds %s in %s' % (tgr_anchor, relpath))
    block = m.group(0).rstrip('\n')
    need(tgr_anchor not in win, '%s already adds %s -- the merge below is stale' % (winner_name, tgr_anchor))
    # Append inside the country's effect block.  A country history file is
    # COUNTRIES = { c:XXX = { ... } }, so the last two closing braces close the
    # country and the container; we insert before the first of them, keeping the
    # original indentation of the tail so the diff against a future version of the
    # foreign file stays readable.
    w = win.rstrip('\n')
    i = w.rindex('}')
    j = w[:i].rindex('}')
    line_start = w.rfind('\n', 0, j) + 1
    out = w[:line_start].rstrip('\n') + '\n\n' + block + '\n' + w[line_start:] + '\n'
    note('%s: %s body + TGR %s' % (relpath, winner_name, tgr_anchor))
    return banner(*hdr_lines) + out


def _history_china(p):
    return _history_merge(
        p, 'common/history/countries/chi - china.txt', p.moh, 'Mandate of Heaven',
        'company_ong_lung_sheng_tea_company',
        ('ComPatch HC+GoB+MoH x The Great Revision -- China at 1836',
         '',
         'Both TGR and Mandate of Heaven ship common/history/countries/chi - china.txt.',
         'Same relative path, so the later mod wins the file outright and nothing else',
         'is read.  MoH is later, and what it wins is a full rewrite of Chinese setup --',
         'laws, journal entries, variables, the Ewo Hong company, a land amendment.',
         'TGR\'s single addition to the same country, the Ong Lung Sheng tea company,',
         'goes with the file.  A company that never gets founded produces no error.',
         '',
         'Merged below: MoH\'s file with TGR\'s add_company block appended inside the',
         'country effect.  MoH\'s history is otherwise untouched.',
         '',
         'VARIANTS: needs TGR (the company type is TGR\'s).  In a composition without',
         'TGR, ship Mandate of Heaven\'s file unchanged -- that is, drop this one.',
         'Victorian Century ships this same path too, REPLACE by path overlap same as',
         'TGR and MoH -- checked line by line 26.08.2026 and found to add nothing worth',
         'carrying against MoH\'s choices here (MoH\'s land-reform and bureaucracy law',
         'picks leave VC\'s own additions\' prerequisites unmet, and MoH\'s own journal',
         'chain already covers the same ground as VC\'s).  See',
         '_HC+GoB+MoH/hc+vc done/README.md for the full write-up.  Nothing in this file',
         'changes whether or not VC is part of the composition.'))


def _history_ottoman(p):
    relpath = 'common/history/countries/tur - ottoman empire.txt'
    return _history_merge(
        p, relpath, p.gob, 'Gates of the Bosphorus',
        'company_imperial_arsenal',
        ('ComPatch HC+GoB+MoH x The Great Revision -- the Ottomans at 1836',
         '',
         'Same shape as the China file: TGR and Gates of the Bosphorus both ship',
         'common/history/countries/tur - ottoman empire.txt, GoB is later and takes the',
         'whole file, and TGR\'s addition -- the Imperial Arsenal company -- disappears',
         'with it.  Silent.',
         '',
         'Merged below: GoB\'s file with TGR\'s add_company block appended.',
         '',
         'VARIANTS: needs TGR for the company; without it, drop just that append.',
         'Victorian Century reworks this same file too -- if VC is part of the',
         'composition, load the standalone HC+GoB+MoH x TGR x VC compatch',
         '(_HC+GoB+MoH/hc+vc done) after this addon; it REPLACEs this same path,',
         'layering VC\'s law_madrasa activation and two amendments (verified-safe',
         'additions, not a competing rework -- see that compatch\'s README) on top of',
         'the exact body below.'))


# =============================================================================
#  compatch 3:  HC+GoB+MoH  x  Kuromi's AI
# =============================================================================
#  Tech & Res left the set on 25.08.2026.  Three files this section used to build
#  -- the four slavery laws, the Greener Grass decree and the warlord China
#  journal entry -- were merges of a T&R body with an HC or MoH one and have no
#  meaning without it; they are in
#  _HC+GoB+MoH/hc+kai done/_to_delete/tr_removed_2026-08-25/ together with T&R's
#  re-issued ai_strategy_default injection.  What is left is the pair that never
#  depended on T&R: Kuromi's AI against Mandate of Heaven.
def build_kai(p):
    files = {}
    strat, tgr_reinject = _ai_default(p)
    files['common/ai_strategies/zz_hctr_ai_strategy_default.txt'] = strat
    files['common/ai_strategies/zz_hctr_tgr_default_strategy.txt'] = tgr_reinject
    return files


def canon_indent(text):
    """Re-indent a script body from its own braces, one tab per level, and drop
    trailing whitespace.

    Used before the three-way merge of ai_strategy_default.  Mandate of Heaven
    re-indented a dozen passages it did not otherwise change; without this every
    one of them shows up as a conflict against KAI and buries the handful of real
    ones.  The merged file is ours, so canonical indentation costs nothing.
    """
    out, d = [], 0
    for line in text.split('\n'):
        st = line.strip()
        code = st.split('#')[0]
        lead = 0
        for ch in code:
            if ch == '}':
                lead += 1
            elif ch == '{':
                break
        out.append(('\t' * max(0, d - lead) + st) if st else '')
        d += code.count('{') - code.count('}')
    return '\n'.join(out)


def _ai_default(p):
    """ai_strategy_default: the largest single loss in this addon.

    Chain as loaded: vanilla -> TGR (three INJECTs) -> KAI (a bare body at the
    vanilla path 00_default_strategy.txt, which already erases TGR's three) ->
    Mandate of Heaven (REPLACE:, 9075 lines built on vanilla).  MoH is last and
    REPLACE swaps the entry, so KAI's rework goes with it.  This is the file that
    decides how every AI country behaves, and losing it is invisible: no error,
    the AI just plays vanilla.
    """
    van = read(os.path.join(p.van, 'common/ai_strategies/00_default_strategy.txt'))
    kai = read(os.path.join(p.kai, 'common/ai_strategies/00_default_strategy.txt'))
    moh = read(os.path.join(p.moh, 'common/ai_strategies/moh_default_strategy.txt'))

    v = entry(van, 'ai_strategy_default')[1]
    k = entry(kai, 'ai_strategy_default')[1]
    m = entry(moh, 'ai_strategy_default', prefix='REPLACE:')[1]
    need('KAI' in k, 'KAI\'s 00_default_strategy.txt no longer marks its own changes')

    stats = {'conflicts': 0}

    def resolve(ours, base, theirs, n):
        # ours = KAI, theirs = MoH.  Every conflict seen so far is one of:
        #   * MoH re-indented a block KAI rewrote  (MoH == base, ignoring space)
        #   * both arrived at the same text        (ours == theirs)
        # Anything else is a real disagreement between an AI mod and a China mod
        # about the same lines, and a human has to look at it.
        stats['conflicts'] += 1
        if _ws(theirs) == _ws(base) or _ws(ours) == _ws(theirs):
            return ours
        if _ws(ours) == _ws(base):
            return theirs
        return None

    merged = merge3(canon_indent(v), canon_indent(k), canon_indent(m),
                    'ai_strategy_default', resolve=resolve)
    need('KAI' in merged, 'ai_strategy_default merge lost KAI\'s changes')
    need('naval_power_projection' in merged, 'ai_strategy_default merge lost KAI max_active_stances')
    body = merged
    note('ai_strategy_default: three-way merge of KAI and MoH over vanilla '
         '(%d conflicts, all whitespace or agreement)' % stats['conflicts'])

    strat = banner(
        'ComPatch HC+GoB+MoH x Kuromi AI -- ai_strategy_default',
        '',
        'This entry is the base every AI country loads before its own strategy, and',
        'three mods in this set write it:',
        '',
        '  TGR   three INJECT: files (diplomatic_play_support, institution_scores,',
        '        wanted_construction_output, combat_unit_group_weights,',
        '        conscript_battalion_ratio);',
        '  KAI   a bare body at the vanilla path common/ai_strategies/00_default_strategy.txt',
        '        -- 42 changed passages, and it already erases TGR\'s three injections',
        '        before this addon is in the picture.  The megapack puts those back;',
        '        this file drops them again along with everything else, so they are',
        '        re-issued here too, in zz_hctr_tgr_default_strategy.txt;',
        '  MoH   REPLACE:, 9075 lines, built on vanilla.',
        '',
        'MoH loads last, so KAI disappears under it.  An AI mod being',
        'switched off by a flavour mod is not something either author could see: there',
        'is no error, the AI simply plays vanilla again.',
        '',
        'Below is a three-way merge of KAI and MoH against vanilla as the common base,',
        'so each keeps the passages it actually changed.  The one injection still',
        'written against this entry is restored in its own file, which sorts after',
        'this one inside the mod and therefore lands on the merged body rather than',
        'under it: TGR\'s, in zz_hctr_tgr_default_strategy.txt.',
        '',
        'Tech & Res used to be a fourth author here and its 1360-line injection was',
        're-issued in a file of its own.  T&R left the set on 25.08.2026 and that',
        'file went with it.',
        '',
        '!! MAINTENANCE !! this file is generated, never edited.  The merge is redone',
        'from the three sources on every run and the generator stops if KAI and MoH',
        'start disagreeing about the same lines -- at the moment they never do; every',
        'conflict git reports is either MoH re-indenting a passage KAI rewrote, or the',
        'two arriving at the same text.') \
        + 'REPLACE:ai_strategy_default = {' + body + '}\n'

    tgr_src = tgrds.read_sources(tgr_dir=p.tgr, van_dir=p.van)
    tgr_notes = []
    tgr_block = tgrds.build_body(body, tgr_src, tgr_notes)
    for n in tgr_notes:
        note('ai_strategy_default / ' + n)
    tgr_reinject = banner(
        'ComPatch HC+GoB+MoH x The Great Revision -- TGR\'s default AI strategy, re-issued',
        '',
        'The Great Revision writes ai_strategy_default with three INJECT: files.  They',
        'are already gone before this addon loads -- Kuromi\'s AI ships a bare body at',
        'the vanilla path and a bare body eats every earlier injection -- and the',
        'megapack puts them back.  Then Mandate of Heaven REPLACE:s the entry and',
        'zz_hctr_ai_strategy_default.txt above re-issues the merged body, and both of',
        'those drop the megapack\'s copy again.  So it is re-issued here, on top of the',
        'merged body, in a file that sorts after it.',
        '',
        'This is not a verbatim copy of TGR\'s three files: two of the five sub-blocks',
        'they touch are also written by KAI, and only one of those is merged.  What is',
        'restored, what is merged and what is deliberately left to KAI is spelled out',
        'in tools/tgr_default_strategy.py and in conflicts_tgr_vs_kai_report.md next to',
        'the TGR + T&R + KAI compatch (marked outdate 25.08.2026).  The same block, built against KAI\'s own body',
        'instead of this merged one, is what the megapack ships.',
        '',
        '!! MAINTENANCE !! generated, never edited.  The bodies are cut out of TGR and',
        'out of the merged body on every run, and the run stops if either side moves a',
        'line the merge depends on.',
        '',
        'VARIANTS: needs The Great Revision.  It also sits on the merged body from',
        'zz_hctr_ai_strategy_default.txt, so it goes wherever that file goes.') \
        + tgr_block

    return strat, tgr_reinject


# =============================================================================
#  driver
# =============================================================================
COMPATCHES = [
    ('hc+morg done',   build_morg),
    ('hc+tgr done',    build_tgr),
    ('hc+kai done',     build_kai),
]
PAIR_DIR = '_HC+GoB+MoH'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', required=True, help='path to vic3_mods_out (the foreign mods)')
    ap.add_argument('--out',  required=True, help='path to vic3_mods (this repository)')
    ap.add_argument('--check', action='store_true',
                    help='compare against what is on disk, write nothing, exit 1 on a difference')
    args = ap.parse_args(argv)

    p = P(args.root)
    p.out = args.out
    for probe in (p.van, p.tgr, p.kai, p.morg, p.hc, p.gob, p.moh):
        if not os.path.isdir(probe):
            raise SystemExit('missing source mod: ' + probe)

    diffs, written = [], 0
    for folder, build in COMPATCHES:
        base = os.path.join(args.out, PAIR_DIR, folder)
        for rel, text in build(p).items():
            bal = brace_balance(text)
            if bal:
                raise SystemExit('brace balance %+d in %s/%s' % (bal, folder, rel))
            path = os.path.join(base, rel)
            if args.check:
                if not os.path.exists(path):
                    diffs.append('missing: %s/%s' % (folder, rel))
                elif read(path) != text:
                    diffs.append('differs: %s/%s' % (folder, rel))
            else:
                write(path, text)
                written += 1

    print('--- what this run merged ---')
    for n in NOTES:
        print('  * ' + n)
    if args.check:
        for d in diffs:
            print('  ! ' + d)
        print('%d file(s) out of date' % len(diffs))
        return 1 if diffs else 0
    print('%d file(s) written under %s' % (written, os.path.join(args.out, PAIR_DIR)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
