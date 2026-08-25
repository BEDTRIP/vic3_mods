# -*- coding: utf-8 -*-
"""Generator for Addon 1: HC + GoB + MoH  x  megapack.

Builds three pair compatches under _HC+GoB+MoH/ :

    hc+morg done      HC+GoB+MoH  x  Morgenroete
    hc+tgr done       HC+GoB+MoH  x  The Great Revision
    hc+tr+kai done    HC+GoB+MoH  x  Tech&Res + Kuromi AI

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
        self.tr   = os.path.join(root, 'TechRes+Kuromi', 't&r')
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


def _ig_landowners(van, tgr, hc):
    v = entry(van, 'ig_landowners')[1]
    t = entry(tgr, 'ig_landowners', prefix='REPLACE_OR_CREATE:')[1]
    h = entry(hc,  'ig_landowners')[1]
    vw, tw, hw = sub(v, 'pop_weight'), sub(t, 'pop_weight'), sub(h, 'pop_weight')
    need('0.030' in tw, 'TGR no longer raises the LEADER_POPULARITY multiplier in ig_landowners')
    need('0.0025' in hw, 'HC ig_landowners no longer carries the vanilla LEADER_POPULARITY multiplier')
    merged = merge3(vw, tw, hw, 'ig_landowners/pop_weight', resolve=_ig_resolve)
    need('0.030' in merged and 'USFP' in merged,
         'ig_landowners/pop_weight merge lost either TGR\'s multiplier or HC\'s planters rule')
    body = replace_sub(h, 'pop_weight', merged)
    note('ig_landowners: HC body + TGR LEADER_POPULARITY 0.0025 -> 0.030')
    return banner(
        'ComPatch HC+GoB+MoH x The Great Revision -- ig_landowners',
        '',
        'TGR reworks this interest group from TGR_POLITICS_landowners.txt with',
        'REPLACE_OR_CREATE:.  Hail, Columbia! ships common/interest_groups/00_landowners.txt',
        '-- the vanilla path, a bare body -- and loads later, so TGR\'s version is gone',
        'entirely.  Silent; the interest group still exists, it just has vanilla\'s',
        'numbers back.',
        '',
        'What TGR actually changes here is one line: in pop_weight, the LEADER_POPULARITY',
        'multiplier goes from 0.0025 to 0.030, i.e. a popular leader pulls twelve times',
        'as hard.  Everything else in TGR\'s 772-line body is vanilla.',
        '',
        'What HC changes: usfp_country_is_american in on_enable, and a pop_weight rule',
        'that zeroes Southern planters outside slave states during the Civil War.',
        '',
        'Merged below: HC\'s body with TGR\'s multiplier merged into pop_weight',
        '(three-way against vanilla, so a future edit by either author conflicts',
        'loudly instead of being dropped).',
        '',
        'TGR\'s `scope:interest_group ?= {` -> `= {` change is NOT carried: vanilla and',
        'HC both use the safe-scope form, TGR\'s looks incidental, and the strict form',
        'is the one that can go wrong.',
        '',
        'VARIANTS: safe in every megapack composition -- the merged body names no TGR',
        'entity, only a number.',
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


def _ig_rural_folk(van, tgr, hc, moh):
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
    body = replace_sub(h, 'pop_weight', merged)

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
         '(dropped as stale pre-1.13 copies: %s)' % ', '.join(n for n, _ in dropped))
    return banner(
        'ComPatch HC+GoB+MoH x The Great Revision -- ig_rural_folk',
        '',
        'Three mods write this entry and each of the last two erases part of the one',
        'before it:',
        '',
        '  TGR   REPLACE_OR_CREATE: from TGR_POLITICS_rural_folk.txt.  Its real change',
        '        is three numbers in pop_weight: POP_FARMERS 200 -> 250, POP_PEASANTS',
        '        200 -> 150, LEADER_POPULARITY 0.0025 -> 0.030.',
        '  HC    a bare body at the vanilla path 00_rural_folk.txt -- so all of TGR is',
        '        gone.  HC\'s own changes: usfp_country_is_american in on_enable and an',
        '        aristocrat rule in pop_potential that exempts American cultures.',
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
        'VARIANTS: safe in every composition -- ideology_moh_kmt and the Nongmin rename',
        'come from Mandate of Heaven, which is part of this addon\'s own block; the TGR',
        'contribution is numbers only.',
        *IG_HEAD) + 'REPLACE:ig_rural_folk = {' + body + '}\n'


def _open_block(block):
    """Drop the final closing brace of a `{ ... }` text, keeping everything else."""
    i = block.rindex('}')
    return block[:i]


def _ids(t):
    return set(re.findall(r'[A-Za-z_][A-Za-z_0-9:]*', re.sub(r'#[^\n]*', '', t or '')))


def _jacksonian(p):
    hc  = read(os.path.join(p.hc,  'common/ideologies/usfp_ideology_overrides.txt'))
    tgr = read(os.path.join(p.tgr, 'common/ideologies/TGR_POLITICS_character_ideologies.txt'))
    h = entry(hc,  'ideology_jacksonian_democrat', prefix='REPLACE_OR_CREATE:')[1]
    t = entry(tgr, 'ideology_jacksonian_democrat', prefix='INJECT:')[1]
    add = [nm for nm in sub_names(t)]
    need(add == ['lawgroup_election_system', 'lawgroup_legislative_process'],
         'TGR now injects %s into ideology_jacksonian_democrat' % add)
    for nm in add:
        need(sub(h, nm) is None, 'HC now defines %s itself -- decide which stance wins' % nm)
    tail = '\n'.join('\n\t# The Great Revision\n\t%s = %s' % (nm, sub(t, nm)) for nm in add)
    body = _open_block('{' + h + '}')[1:].rstrip() + '\n' + tail + '\n}'
    note('ideology_jacksonian_democrat: HC body + TGR lawgroup_election_system / lawgroup_legislative_process')
    return banner(
        'ComPatch HC+GoB+MoH x The Great Revision -- ideology_jacksonian_democrat',
        '',
        'TGR INJECT:s two law stances into this ideology -- lawgroup_election_system and',
        'lawgroup_legislative_process, five laws each.  Hail, Columbia! then rewrites',
        'the whole ideology with REPLACE_OR_CREATE: and names neither, so both stances',
        'are dropped: REPLACE swaps the entry, it does not patch the sub-blocks a mod',
        'happens to list.  A Jacksonian leader ends up with no opinion at all on',
        'election systems or legislative process, which reads as "neutral" everywhere',
        'and is logged nowhere.',
        '',
        'Merged below: HC\'s body, unchanged, with TGR\'s two stance blocks appended.',
        'They do not overlap -- HC names governance_principles, distribution_of_power,',
        'bureaucracy, colonization and land_reform.',
        '',
        'VARIANTS: needs TGR.  Drop this file from a composition without it -- the two',
        'appended blocks are TGR\'s balance, not vanilla\'s.') \
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
         'country effect.  MoH\'s history is untouched.',
         '',
         'VARIANTS: needs TGR (the company type is TGR\'s).  In a composition without',
         'TGR, ship Mandate of Heaven\'s file unchanged -- that is, drop this one.'))


def _history_ottoman(p):
    return _history_merge(
        p, 'common/history/countries/tur - ottoman empire.txt', p.gob, 'Gates of the Bosphorus',
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
         'VARIANTS: needs TGR.  Without it, ship GoB\'s file unchanged.'))


# =============================================================================
#  compatch 3:  HC+GoB+MoH  x  Tech & Res + Kuromi AI
# =============================================================================
SLAVERY_LAWS = ['law_slave_trade', 'law_debt_slavery', 'law_legacy_slavery', 'law_colonial_slavery']


def build_trkai(p):
    files = {}
    files['common/laws/zz_hctr_slavery.txt'] = _slavery(p)
    files['common/decrees/zz_hctr_greener_grass.txt'] = _greener_grass(p)
    files['common/journal_entries/zz_hctr_warlord_china.txt'] = _warlord_china(p)
    strat, tgr_reinject, reinject = _ai_default(p)
    files['common/ai_strategies/zz_hctr_ai_strategy_default.txt'] = strat
    files['common/ai_strategies/zz_hctr_tgr_default_strategy.txt'] = tgr_reinject
    files['common/ai_strategies/zzz_hctr_tr_default_strategy.txt'] = reinject
    return files


def _slavery(p):
    van = read(os.path.join(p.van, 'common/laws/02_slavery.txt'))
    tr  = read(os.path.join(p.tr,  'common/laws/ztr_un_updated_slavery.txt'))
    hc  = read(os.path.join(p.hc,  'common/laws/usfp_law_slavery_overrides.txt'))
    out = [banner(
        'ComPatch HC+GoB+MoH x Tech & Res -- the four slavery laws',
        '',
        'Tech & Res REPLACE:s all four out of ztr_un_updated_slavery.txt; Hail, Columbia!',
        'REPLACE:s the same four out of usfp_law_slavery_overrides.txt and loads later.',
        'REPLACE swaps the whole entry, so as shipped T&R\'s slavery rework is simply',
        'not in the game.  Nothing is logged: the laws exist, they are just vanilla',
        'again with HC\'s additions on top.',
        '',
        'The good news, and the reason this file is short: the two authors barely touch',
        'the same thing.',
        '',
        '  T&R  rewrites on_activate (and the modifier on legacy slavery), and adds a',
        '       can_enact gate tied to its UN human-rights vote plus BPM compatibility.',
        '  HC   adds a can_enact gate for the American gag rule and Corwin amendment,',
        '       and one ai_will_do on the slave trade.',
        '',
        'can_enact is the only block both write, and a can_enact block is a conjunction:',
        'the two sets of conditions are about different things and simply AND together.',
        'Everything else is taken from whichever author changed it.',
        '',
        'VARIANTS: needs Tech & Res (ztr_is_un_member, global_var:ztr_un_hr_slavery,',
        'BPM_is_active_trigger).  Drop this file from a composition without T&R -- HC\'s',
        'own bodies are correct on their own.',
        '',
        '!! MAINTENANCE !! all three bodies are cut out at generation time and the',
        'generator refuses to run if the two authors start overlapping anywhere but',
        'can_enact.')]
    for law in SLAVERY_LAWS:
        v = entry(van, law)[1]
        t = entry(tr,  law, prefix='REPLACE:')[1]
        h = entry(hc,  law, prefix='REPLACE:')[1]
        body, took = h, []
        for nm in sub_names(t):
            vb, tb, hb = sub(v, nm), sub(t, nm), sub(h, nm)
            if vb is not None and _ws2(tb) == _ws2(vb):
                continue                       # T&R did not change this one
            if nm == 'can_enact':
                continue                       # handled below
            need(hb is None or _ws2(hb) == _ws2(vb) if vb is not None else hb is None,
                 '%s/%s: T&R and HC now both rewrite it -- merge it by hand' % (law, nm))
            body = (replace_sub(body, nm, tb) if hb is not None
                    else _append_sub(body, nm, tb))
            took.append(nm)
        tc, hcc = sub(t, 'can_enact'), sub(h, 'can_enact')
        if tc is not None:
            if hcc is None:
                body = _append_sub(body, 'can_enact', tc)
                took.append('can_enact (T&R only)')
            else:
                merged, n = _merge_statements(
                    hcc, tc, '# Tech & Res: UN human rights vote, and BPM.')
                need(n, '%s/can_enact: T&R adds nothing HC does not already say' % law)
                body = replace_sub(body, 'can_enact', merged)
                took.append('can_enact (HC + %d from T&R)' % n)
        need(took, '%s: nothing merged -- T&R no longer changes this law' % law)
        note('%s: HC body + T&R %s' % (law, ', '.join(took)))
        out.append('REPLACE:%s = {%s}\n' % (law, body))
    return '\n'.join(out)


def _statements(block_body):
    """Split the inside of a `{ ... }` into its depth-0 statements, comments
    attached to whatever follows them."""
    out, cur, d = [], [], 0
    for line in block_body.split('\n'):
        code = line.split('#')[0]
        if not cur and not line.strip():
            continue
        cur.append(line)
        d += code.count('{') - code.count('}')
        if d == 0 and line.strip() and not line.strip().startswith('#'):
            out.append('\n'.join(cur))
            cur = []
    if cur and '\n'.join(cur).strip():
        out.append('\n'.join(cur))
    return out


def _merge_statements(base_block, add_block, comment):
    """Append the statements of add_block to base_block, skipping any that base
    already says verbatim.  Both arguments include their braces."""
    have = [_ws2(x) for x in _statements(_open_block(base_block)[1:])]
    extra = [x for x in _statements(_open_block(add_block)[1:]) if _ws2(x) not in have]
    if not extra:
        return base_block, 0
    return (_open_block(base_block).rstrip() + '\n\t\t' + comment + '\n'
            + '\n'.join(extra).rstrip() + '\n\t}'), len(extra)


def _ws2(t):
    return re.sub(r'\s+', ' ', re.sub(r'#[^\n]*', '', t or '')).strip()


def _append_sub(body, name, block):
    return _open_block('{' + body + '}')[1:].rstrip() + '\n\t%s = %s\n' % (name, block)


def _greener_grass(p):
    hc = read(os.path.join(p.hc, 'common/decrees/usfp_decrees_overwrite.txt'))
    tr = read(os.path.join(p.tr, 'common/decrees/ztr_decree.txt'))
    h = entry(hc, 'decree_greener_grass_campaign', prefix='REPLACE:')[1]
    t = entry(tr, 'decree_greener_grass_campaign', prefix='INJECT:')[1]
    add = sub_names(t)
    need(add == ['country_trigger'], 'T&R now injects %s into the greener grass decree' % add)
    need(sub(h, 'country_trigger') is None,
         'HC now sets country_trigger itself on the greener grass decree')
    body = _append_sub(h, 'country_trigger', sub(t, 'country_trigger'))
    note('decree_greener_grass_campaign: HC body + T&R country_trigger')
    return banner(
        'ComPatch HC+GoB+MoH x Tech & Res -- the Greener Grass decree',
        '',
        'T&R INJECT:s a country_trigger onto this decree -- it stops being available',
        'once modern_urban_planning is researched.  Hail, Columbia! REPLACE:s the whole',
        'decree (to stop it stacking with the Homestead Act) and does not carry that',
        'trigger, so with HC later in the order the decree stays available forever.',
        'Silent.',
        '',
        'Merged below: HC\'s body with T&R\'s country_trigger appended.',
        '',
        'VARIANTS: needs Tech & Res.  Note that Grey\'s soft_pop also REPLACE:s this',
        'decree and loads after this addon -- when that block joins the set, this file',
        'stops being the last word and the same merge has to move into addon 3.') \
        + 'REPLACE:decree_greener_grass_campaign = {' + body + '}\n'


def _warlord_china(p):
    van = read(os.path.join(p.van, 'common/journal_entries/00_warlord_china.txt'))
    tr  = read(os.path.join(p.tr,  'common/journal_entries/ztr_vanilla_je.txt'))
    moh = read(os.path.join(p.moh, 'common/journal_entries/moh_warlord_china.txt'))
    v = entry(van, 'je_warlord_china')[1]
    t = entry(tr,  'je_warlord_china', prefix='REPLACE:')[1]
    m = entry(moh, 'je_warlord_china', prefix='REPLACE:')[1]

    # T&R's two changes: the journal entry can also finish by outliving 1940, and
    # completing it after 1940 fires a different event.
    tcomp = sub(t, 'complete')
    need(re.search(r'year\s*>\s*1940', tcomp), 'T&R no longer adds the 1940 escape to je_warlord_china')
    need(_ws2(sub(m, 'on_complete')) == _ws2(sub(v, 'on_complete')),
         'MoH now rewrites on_complete too -- merge it by hand')
    body = replace_sub(m, 'on_complete', sub(t, 'on_complete'))

    mcomp = _open_block(sub(m, 'complete'))[1:].strip('\n')
    body = replace_sub(body, 'complete',
                       '{\n\t\tOR = {\n\t\t\tAND = {\n'
                       + re.sub(r'(?m)^', '\t\t', mcomp) + '\n\t\t\t}\n'
                       + '\t\t\t# Tech & Res: after 1940 the warlord era ends either way.\n'
                       + '\t\t\tyear > 1940\n\t\t}\n\t}')
    note('je_warlord_china: MoH body + T&R 1940 escape in complete and the branching on_complete')
    return banner(
        'ComPatch HC+GoB+MoH x Tech & Res -- je_warlord_china',
        '',
        'Both mods REPLACE: this journal entry and Mandate of Heaven is later, so T&R\'s',
        'version is gone.  T&R adds exactly two things:',
        '',
        '  * complete also succeeds on year > 1940, so the entry cannot hang forever;',
        '  * on_complete branches -- warlord_china_events.200 up to 1940, and',
        '    the_future_of_china.201 after it.',
        '',
        'MoH rewrites complete around its own Chinese content (Wuxu reform, autocracy,',
        'Guofan, self-strengthening, treaty ports) and leaves on_complete at vanilla.',
        '',
        'Merged below: MoH\'s body, with its complete conditions wrapped in an AND and',
        'T&R\'s 1940 escape put beside them, and T&R\'s on_complete taken as is.',
        '',
        'VARIANTS: needs Tech & Res (the_future_of_china.201 is T&R\'s event).') \
        + 'REPLACE:je_warlord_china = {' + body + '}\n'


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
    T&R (a 1360-line INJECT) -> Mandate of Heaven (REPLACE:, 9075 lines built on
    vanilla).  MoH is last and REPLACE swaps the entry, so both KAI's rework and
    T&R's injection go.  This is the file that decides how every AI country
    behaves, and losing it is invisible: no error, the AI just plays vanilla.
    """
    van = read(os.path.join(p.van, 'common/ai_strategies/00_default_strategy.txt'))
    kai = read(os.path.join(p.kai, 'common/ai_strategies/00_default_strategy.txt'))
    moh = read(os.path.join(p.moh, 'common/ai_strategies/moh_default_strategy.txt'))
    trf = read(os.path.join(p.tr,  'common/ai_strategies/ztr_default_strategy.txt'))

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
        'ComPatch HC+GoB+MoH x Tech & Res + Kuromi AI -- ai_strategy_default',
        '',
        'This entry is the base every AI country loads before its own strategy, and',
        'four mods in this set write it:',
        '',
        '  TGR   three INJECT: files (diplomatic_play_support, institution_scores,',
        '        wanted_construction_output, combat_unit_group_weights,',
        '        conscript_battalion_ratio);',
        '  KAI   a bare body at the vanilla path common/ai_strategies/00_default_strategy.txt',
        '        -- 42 changed passages, and it already erases TGR\'s three injections',
        '        before this addon is in the picture.  The megapack puts those back;',
        '        this file drops them again along with everything else, so they are',
        '        re-issued here too, in zz_hctr_tgr_default_strategy.txt;',
        '  T&R   a 1360-line INJECT: (institution_scores, aggression,',
        '        building_group_weights, subsidies, goods_stances);',
        '  MoH   REPLACE:, 9075 lines, built on vanilla.',
        '',
        'MoH loads last, so KAI and T&R both disappear under it.  An AI mod being',
        'switched off by a flavour mod is not something either author could see: there',
        'is no error, the AI simply plays vanilla again.',
        '',
        'Below is a three-way merge of KAI and MoH against vanilla as the common base,',
        'so each keeps the passages it actually changed.  The two injections that were',
        'written against this entry are restored in their own files, which sort after',
        'this one inside the mod and therefore land on the merged body rather than',
        'under it: TGR\'s in zz_hctr_tgr_default_strategy.txt, T&R\'s in',
        'zzz_hctr_tr_default_strategy.txt -- in that order, the order their authors',
        'load in.',
        '',
        '!! MAINTENANCE !! this file is generated, never edited.  The merge is redone',
        'from the three sources on every run and the generator stops if KAI and MoH',
        'start disagreeing about the same lines -- at the moment they never do; every',
        'conflict git reports is either MoH re-indenting a passage KAI rewrote, or the',
        'two arriving at the same text.') \
        + 'REPLACE:ai_strategy_default = {' + body + '}\n'

    tgr_src = tgrds.read_sources(tgr_dir=p.tgr, van_dir=p.van, tr_dir=p.tr)
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
        'merged body, in a file that sorts after it and before T&R\'s.',
        '',
        'This is not a verbatim copy of TGR\'s three files: two of the five sub-blocks',
        'they touch are also written by KAI, and only one of those is merged.  What is',
        'restored, what is merged and what is deliberately left to KAI is spelled out',
        'in tools/tgr_default_strategy.py and in conflicts_tgr_vs_kai_report.md next to',
        'the TGR + T&R + KAI compatch.  The same block, built against KAI\'s own body',
        'instead of this merged one, is what the megapack ships.',
        '',
        '!! MAINTENANCE !! generated, never edited.  The bodies are cut out of TGR and',
        'out of the merged body on every run, and the run stops if either side moves a',
        'line the merge depends on.',
        '',
        'VARIANTS: needs The Great Revision.  It also sits on the merged body from',
        'zz_hctr_ai_strategy_default.txt, so it goes wherever that file goes.') \
        + tgr_block

    tr_entry = entry(trf, 'ai_strategy_default', prefix='INJECT:')[0]
    need(len(tr_entry.split('\n')) > 1000, 'T&R default strategy injection shrank unexpectedly')
    note('ai_strategy_default: T&R INJECT: re-issued after MoH (%d lines)'
         % len(tr_entry.split('\n')))
    reinject = banner(
        'ComPatch HC+GoB+MoH x Tech & Res -- T&R\'s default AI strategy, re-issued',
        '',
        'Mandate of Heaven REPLACE:s ai_strategy_default, which drops Tech & Res\'s',
        'INJECT: along with everything else.  This file is that injection again,',
        'copied verbatim from T&R common/ai_strategies/ztr_default_strategy.txt, under a',
        'name that sorts after zz_hctr_ai_strategy_default.txt so it lands on the merged',
        'body rather than under it.',
        '',
        'Copied, not rewritten, on purpose: it is 1360 lines of T&R\'s balance and the',
        'only sane way to keep it current is to take it from the mod each time this',
        'generator runs.  Do not edit here.',
        '',
        'VARIANTS: needs Tech & Res.') + tr_entry + '\n'
    return strat, tgr_reinject, reinject


# =============================================================================
#  driver
# =============================================================================
COMPATCHES = [
    ('hc+morg done',   build_morg),
    ('hc+tgr done',    build_tgr),
    ('hc+tr+kai done', build_trkai),
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
    for probe in (p.van, p.tgr, p.tr, p.kai, p.morg, p.hc, p.gob, p.moh):
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
