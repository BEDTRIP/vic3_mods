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
        self.vc   = os.path.join(root, 'VC')


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
    vc_lo  = read(os.path.join(p.vc,  'common/interest_groups/joi_landowners.txt'))
    vc_rf  = read(os.path.join(p.vc,  'common/interest_groups/joi_rural_folk.txt'))

    files['common/interest_groups/zz_hct_ig_landowners.txt'] = _ig_landowners(van_lo, tgr_lo, hc_lo, vc_lo)
    files['common/interest_groups/zz_hct_ig_rural_folk.txt'] = _ig_rural_folk(van_rf, tgr_rf, hc_rf, moh_rf, vc_rf)
    files['common/ideologies/zz_hct_jacksonian_democrat.txt'] = _jacksonian(p)
    files['common/history/countries/chi - china.txt'] = _history_china(p)
    files['common/history/countries/tur - ottoman empire.txt'] = _history_ottoman(p)
    files['common/history/countries/usa - usa.txt'] = _history_usa(p)
    return files


IG_HEAD = (
    'Both interest groups below are re-issued as one complete REPLACE: body.',
    'That is deliberate and it is the expensive option: REPLACE: swaps the whole',
    'entry, so a partial body would drop everything it does not name.  Proved in',
    'game 21.08.2026 -- REPLACE:building_bank = { ownership_type = self } made the',
    'central bank disappear, and 285 production methods restated with only',
    'building_modifiers lost their unlocking_laws.',
)


def _ig_landowners(van, tgr, hc, vc):
    v = entry(van, 'ig_landowners')[1]
    t = entry(tgr, 'ig_landowners', prefix='REPLACE_OR_CREATE:')[1]
    h = entry(hc,  'ig_landowners')[1]
    vc_body = entry(vc, 'ig_landowners', prefix='REPLACE_OR_CREATE:')[1]
    vw, tw, hw = sub(v, 'pop_weight'), sub(t, 'pop_weight'), sub(h, 'pop_weight')
    need('0.030' in tw, 'TGR no longer raises the LEADER_POPULARITY multiplier in ig_landowners')
    need('0.0025' in hw, 'HC ig_landowners no longer carries the vanilla LEADER_POPULARITY multiplier')
    merged = merge3(vw, tw, hw, 'ig_landowners/pop_weight', resolve=_ig_resolve)
    need('0.030' in merged and 'USFP' in merged,
         'ig_landowners/pop_weight merge lost either TGR\'s multiplier or HC\'s planters rule')
    body = replace_sub(h, 'pop_weight', merged)

    body = _merge_vc_into_ig(v, body, vc_body, ('on_enable', 'pop_potential', 'pop_weight'),
                              'ig_landowners')
    oe, pp, pw = sub(body, 'on_enable'), sub(body, 'pop_potential'), sub(body, 'pop_weight')
    need('ig_trait_owner_of_land' in oe, 'VC no longer reworks ig_landowners on_enable (Russian nobles trait missing)')
    need('usfp_country_is_american' in oe and 'cu:yankee' not in oe,
         'ig_landowners on_enable: HC\'s usfp_country_is_american swap was lost merging in VC')
    need('is_pop_type = capitalists' in pp and 'is_pop_type = bureaucrats' in pp and 'is_pop_type = peasants' in pp,
         'VC no longer widens ig_landowners pop_potential to capitalists/bureaucrats/peasants')
    need('POP_PRUSSIAN_NOBLES_CAP' in pw, 'VC no longer adds its Prussian-nobles pop_weight rules to ig_landowners')
    need('0.030' in pw and 'No more Southern Planters' in pw,
         'ig_landowners pop_weight lost TGR\'s multiplier or HC\'s Southern-planters rule merging in VC')
    body = replace_sub(body, 'pop_weight', _safe_scope(pw, 'ig_landowners/pop_weight'))

    note('ig_landowners: HC+TGR body + VC\'s on_enable/pop_potential/pop_weight rework merged in '
         '(three-way against vanilla per sub-block); scope:interest_group restored to the safe ?= form '
         'throughout, including one occurrence TGR itself had already silently downgraded')
    return banner(
        'ComPatch HC+GoB+MoH x The Great Revision + Victorian Century -- ig_landowners',
        '',
        'TGR reworks this interest group from TGR_POLITICS_landowners.txt with',
        'REPLACE_OR_CREATE:.  Victorian Century reworks it wholesale from',
        'joi_landowners.txt, also REPLACE_OR_CREATE:.  Hail, Columbia! ships',
        'common/interest_groups/00_landowners.txt -- the vanilla path, a bare body --',
        'and loads last of the three, so both TGR\'s and VC\'s versions are gone',
        'entirely.  Silent; the interest group still exists, it just has vanilla\'s',
        'content back.',
        '',
        'What TGR actually changes here is one line: in pop_weight, the LEADER_POPULARITY',
        'multiplier goes from 0.0025 to 0.030, i.e. a popular leader pulls twelve times',
        'as hard.  Everything else in TGR\'s 772-line body is vanilla.',
        '',
        'What HC changes: usfp_country_is_american in on_enable, and a pop_weight rule',
        'that zeroes Southern planters outside slave states during the Civil War.',
        '',
        'What VC changes, in three sub-blocks: on_enable gets nation-specific noble',
        'trait sets for Russia, Japan, Prussia, Austria, China, Turkey and Spain (in',
        'place of vanilla\'s shared noble_privileges/family_ties pair), a German-nobles',
        'ideology switch, and reworked Prussian/Turkish/British blocks; pop_potential',
        'widens from {aristocrats, clergymen, officers, farmers} to also allow',
        'capitalists, bureaucrats and peasants; pop_weight adds weight rules for',
        'Prussian capitalists/farmers/peasants "joining the Junkers", a European',
        '(non-French) freeman bonus, and a Chinese-officer bonus.',
        '',
        'Merged below: HC\'s body with TGR\'s multiplier folded into pop_weight, then',
        'VC\'s rework of on_enable/pop_potential/pop_weight folded in on top, each',
        'sub-block three-way against vanilla, so a future edit by any of the three',
        'authors conflicts loudly instead of being dropped.  VC does not touch the',
        'American-culture branch in on_enable, so HC\'s usfp_country_is_american swap',
        'survives untouched; VC does not touch pop_potential\'s vanilla types, so its',
        'three new ones are a pure addition; VC does not touch farmers/peasants/',
        'aristocrats/clergymen/officers in pop_weight, so TGR\'s multiplier and HC\'s',
        'Southern-planters rule both survive untouched next to VC\'s new rules.',
        '',
        'Neither TGR\'s nor VC\'s `scope:interest_group ?= {` -> `= {` downgrade is',
        'carried (both make the identical change, independently, in the same',
        'LEADER_POPULARITY block): vanilla and HC use the safe-scope form, and the',
        'strict form is the one that can go wrong.  Restored to `?=` throughout --',
        'this also retroactively fixes the one occurrence TGR\'s own change had already',
        'let through undetected before VC was ever in this build (the banner used to',
        'claim TGR\'s downgrade "is NOT carried", but LEADER_POPULARITY specifically',
        'was; caught while adding this VC layer, fixed here).',
        '',
        'VARIANTS: safe in every megapack composition -- the merged body names no TGR',
        'or VC entity, only numbers and vanilla trait/ideology keys.',
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


def _merge_vc_into_ig(van_body, body, vc_body, names, label):
    """Layer Victorian Century's REPLACE_OR_CREATE: rework of an interest group
    on top of an already-built (HC [+ TGR] [+ MoH]) body, one named sub-block at
    a time, three-way against vanilla -- so a real overlap stops the build
    instead of one side's edit silently winning."""
    for nm in names:
        merged = merge3(sub(van_body, nm), sub(body, nm), sub(vc_body, nm),
                        '%s/%s x VC' % (label, nm), resolve=_ig_resolve)
        body = replace_sub(body, nm, merged)
    return body


def _safe_scope(text, label):
    """Restore `scope:interest_group ?= {` wherever a source silently dropped
    the `?`.  Asserts the total count is unchanged (4, in both ig_landowners and
    ig_rural_folk's pop_weight) so a real structural change is caught rather than
    papered over."""
    fixed = text.replace('scope:interest_group = {', 'scope:interest_group ?= {')
    n = fixed.count('scope:interest_group ?= {')
    need(n == 4 and 'scope:interest_group = {' not in fixed,
         '%s: expected exactly 4 scope:interest_group references after the safety '
         'fix, found %d (plus %d still unsafe) -- re-read the merged pop_weight'
         % (label, n, fixed.count('scope:interest_group = {')))
    return fixed


def _ig_rural_folk(van, tgr, hc, moh, vc):
    v = entry(van, 'ig_rural_folk')[1]
    t = entry(tgr, 'ig_rural_folk', prefix='REPLACE_OR_CREATE:')[1]
    h = entry(hc,  'ig_rural_folk')[1]
    m = entry(moh, 'ig_rural_folk', prefix='INJECT:')[1]
    vc_body = entry(vc, 'ig_rural_folk', prefix='REPLACE_OR_CREATE:')[1]

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

    body = _merge_vc_into_ig(v, body, vc_body, ('on_enable', 'pop_potential', 'pop_weight'),
                              'ig_rural_folk')
    oe, pp, pw = sub(body, 'on_enable'), sub(body, 'pop_potential'), sub(body, 'pop_weight')
    need('ideology_agrarian_russian' in oe and 'ideology_british_tory_conservatism_old' in oe
         and 'ideology_indian_farmer_sovereignist' in oe,
         'VC no longer adds its three ideology-switch blocks to ig_rural_folk on_enable')
    need('usfp_country_is_american' in oe, 'HC\'s Jeffersonian block was lost merging VC into ig_rural_folk on_enable')
    need('Nongmin' in oe, 'MoH\'s Nongmin rename was lost merging VC into ig_rural_folk on_enable')
    need('exists = c:CHI' in pp, 'VC no longer adds its China-officer clause to ig_rural_folk pop_potential')
    need('cu:usfp_american_indian' in pp, 'HC\'s American-culture exemption was lost merging VC into ig_rural_folk pop_potential')
    need(pw.count('POP_CHINESE_OFFICER') == 2, 'VC no longer adds its two Chinese-officer pop_weight rules to ig_rural_folk')
    need('value = 250' in pw and 'value = 150' in pw, 'ig_rural_folk pop_weight lost TGR\'s farmer/peasant numbers merging in VC')
    body = replace_sub(body, 'pop_weight', _safe_scope(pw, 'ig_rural_folk/pop_weight'))

    note('ig_rural_folk: HC body + TGR farmers/peasants/leader numbers + MoH kmt ideology and Nongmin rename '
         '(dropped as stale pre-1.13 copies: %s) + VC\'s on_enable/pop_potential/pop_weight rework merged in '
         'on top; scope:interest_group restored to the safe ?= form throughout, including one occurrence TGR '
         'itself had already silently downgraded' % ', '.join(n for n, _ in dropped))
    return banner(
        'ComPatch HC+GoB+MoH x The Great Revision + Victorian Century -- ig_rural_folk',
        '',
        'Four mods write this entry:',
        '',
        '  TGR   REPLACE_OR_CREATE: from TGR_POLITICS_rural_folk.txt.  Its real change',
        '        is three numbers in pop_weight: POP_FARMERS 200 -> 250, POP_PEASANTS',
        '        200 -> 150, LEADER_POPULARITY 0.0025 -> 0.030.',
        '  HC    a bare body at the vanilla path 00_rural_folk.txt -- so all of TGR is',
        '        gone.  HC\'s own changes: usfp_country_is_american in on_enable and an',
        '        aristocrat/American-culture rule in pop_potential.',
        '  MoH   INJECT: from moh_rural_folk.txt, 316 lines.',
        '  VC    REPLACE_OR_CREATE: from joi_rural_folk.txt.  Adds three ideology-switch',
        '        blocks to on_enable (Russia, Britain, the British East India Company),',
        '        a China-officers/soldiers clause to pop_potential, and two Chinese-',
        '        officer pop_weight bonuses (desc "POP_CHINESE_OFFICER" twice -- VC\'s',
        '        own naming, not a bug introduced here).  All last-loaded and outright',
        '        overwrite everything before them.',
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
        'numbers merged into pop_weight three-way against vanilla, MoH\'s two real',
        'additions appended, and VC\'s rework of on_enable/pop_potential/pop_weight',
        'folded in on top of all of that -- each sub-block three-way against vanilla,',
        'so a future edit by any author conflicts loudly instead of being dropped.',
        'Nothing from MoH\'s stale copy is carried.',
        '',
        'Neither TGR\'s nor VC\'s `scope:interest_group ?= {` -> `= {` downgrade is',
        'carried, for the same reason as in ig_landowners -- restored to `?=`',
        'throughout, retroactively fixing the one occurrence TGR\'s own change had',
        'already let through before VC entered this build.',
        '',
        'VARIANTS: safe in every composition -- ideology_moh_kmt and the Nongmin rename',
        'come from Mandate of Heaven, which is part of this addon\'s own block; the TGR',
        'contribution is numbers only; VC\'s ideology-switch blocks and pop_weight',
        'bonuses name only vanilla ideology/country keys.',
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
    vc  = read(os.path.join(p.out, '_vc/tgr+vc done/common/ideologies/zz_vc_tgr_stances_on_vc_laws.txt'))
    h = entry(hc,  'ideology_jacksonian_democrat', prefix='REPLACE_OR_CREATE:')[1]
    t = entry(tgr, 'ideology_jacksonian_democrat', prefix='INJECT:')[1]
    v = entry(vc,  'ideology_jacksonian_democrat', prefix='INJECT:')[1]

    tgr_add = [nm for nm in sub_names(t)]
    need(tgr_add == ['lawgroup_election_system', 'lawgroup_legislative_process'],
         'TGR now injects %s into ideology_jacksonian_democrat' % tgr_add)
    for nm in tgr_add:
        need(sub(h, nm) is None, 'HC now defines %s itself -- decide which stance wins' % nm)

    vc_groups = sub_names(v)
    need(vc_groups == ['lawgroup_taxation', 'lawgroup_education_system', 'lawgroup_economic_system',
                        'lawgroup_bureaucracy', 'lawgroup_trade_policy', 'lawgroup_citizenship',
                        'lawgroup_policing', 'lawgroup_distribution_of_power'],
         'VC x TGR now injects %s into ideology_jacksonian_democrat -- update the merge' % vc_groups)

    # Two of VC's eight law groups are ones HC already has an opinion on
    # (bureaucracy, distribution_of_power) -- VC adds exactly one new law to each,
    # so that line is folded into HC's existing block instead of creating a
    # second block with the same key, which would be invalid.  The other six
    # groups do not exist in HC's body at all and are appended whole, same as
    # TGR's two.
    vc_merge = [nm for nm in vc_groups if sub(h, nm) is not None]
    vc_new   = [nm for nm in vc_groups if sub(h, nm) is None]
    need(vc_merge == ['lawgroup_bureaucracy', 'lawgroup_distribution_of_power'],
         'HC now overlaps VC on a different set of law groups (%s) -- update the merge' % vc_merge)

    h_merged = h
    for nm in vc_merge:
        extra = sub(v, nm)[1:-1].strip()
        need('\n' not in extra, '%s now carries more than one new VC law -- update the merge' % nm)
        new_block = _open_block(sub(h_merged, nm)).rstrip() + '\n        ' + extra + '\n    }'
        h_merged = replace_sub(h_merged, nm, new_block)

    tgr_lines = ['\n\t# The Great Revision\n\t%s = %s' % (nm, sub(t, nm)) for nm in tgr_add]
    vc_lines  = ['\n\t# Victorian Century\n\t%s = %s' % (nm, sub(v, nm)) for nm in vc_new]
    tail = '\n'.join(tgr_lines + vc_lines)
    body = _open_block('{' + h_merged + '}')[1:].rstrip() + '\n' + tail + '\n}'
    note('ideology_jacksonian_democrat: HC body + VC laws folded into bureaucracy/distribution_of_power '
         '+ TGR two law-group stances + VC six law-group stances appended')
    return banner(
        'ComPatch HC+GoB+MoH x The Great Revision x Victorian Century -- ideology_jacksonian_democrat',
        '',
        'TGR INJECT:s two law stances into this ideology -- lawgroup_election_system and',
        'lawgroup_legislative_process, five laws each.  VC INJECT:s eight more: one new',
        'law apiece in lawgroup_bureaucracy and lawgroup_distribution_of_power (both of',
        'which HC already has an opinion on), plus six whole new groups for its own new',
        'laws (taxation, education_system, economic_system, trade_policy, citizenship,',
        'policing).  Hail, Columbia! then rewrites the whole ideology with',
        'REPLACE_OR_CREATE: and names none of this, so all ten stances are dropped:',
        'REPLACE swaps the entry, it does not patch the sub-blocks a mod happens to',
        'list.  A Jacksonian leader ends up with no opinion at all on any of these laws,',
        'which reads as "neutral" everywhere and is logged nowhere.',
        '',
        'Merged below: HC\'s body, with VC\'s two new laws folded into the',
        'lawgroup_bureaucracy and lawgroup_distribution_of_power blocks it already had,',
        'then TGR\'s two stance blocks and VC\'s six new stance blocks appended.  None of',
        'these overlap each other -- HC names governance_principles,',
        'distribution_of_power, bureaucracy, colonization and land_reform; TGR and VC',
        'both fall outside that list except for the two folded-in laws.',
        '',
        'Source for VC\'s stances: _vc/tgr+vc done/common/ideologies/',
        'zz_vc_tgr_stances_on_vc_laws.txt, itself generated by regen_vc_tgr.py against',
        'vc_tgr_ideology_grid.xlsx (sheet "Обратно", row ideology_jacksonian_democrat).',
        '',
        'VARIANTS: needs TGR and VC, with the tgr+vc done compatch already built -- this',
        'reads that compatch\'s output, not the two mods directly.  Drop this file from',
        'a composition without both -- the appended blocks are their balance, not',
        'vanilla\'s.') \
        + 'REPLACE_OR_CREATE:ideology_jacksonian_democrat = {' + body[:-1] + '}\n'


def _history_merge(p, relpath, winner_dir, winner_name, tgr_anchor, hdr_lines, pre=None):
    """Country history file that a mod of this addon overrides at the vanilla path,
    dropping TGR's addition to the same country.  `pre`, if given, transforms the
    winning body (e.g. splicing in a third mod's content) before TGR's company is
    appended."""
    tgr = read(os.path.join(p.tgr, relpath))
    win = read(os.path.join(winner_dir, relpath))
    if pre is not None:
        win = pre(win)
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


def _check_china_activate_law_vs_vc(p):
    """China's activate_law list is the one place where MoH's and VC's rewrites
    of this file look, on a skim, like they might need reconciling.  They do
    not: every VC choice is either identical to MoH's, a competing pick for a
    law group MoH's own chain already has a load-bearing reason to own, or an
    addition whose own prerequisite MoH's choices leave unmet.  Asserted here so
    a future update to either file re-opens this decision instead of letting it
    silently drift out from under the write-up in the banner below."""
    moh = read(os.path.join(p.moh, 'common/history/countries/chi - china.txt'))
    vc  = read(os.path.join(p.vc,  'common/history/countries/chi - china.txt'))
    vc_laws = re.findall(r'activate_law = law_type:(\S+)', vc)
    need(vc_laws == ['law_monarchy', 'law_autocracy', 'law_serfdom', 'law_land_based_taxation',
                      'law_imperial_examination', 'law_subjecthood', 'law_traditionalism',
                      'law_censorship', 'law_closed_borders', 'law_canton_system',
                      'law_freedom_of_conscience', 'law_classical_learning'],
         'VC china.txt activate_law list is now %s -- re-check the china.txt VC-vs-MoH write-up' % vc_laws)
    moh_laws = re.findall(r'activate_law = law_type:(\S+)', moh)
    need(moh_laws == ['law_monarchy', 'law_autocracy', 'law_tenant_farmers', 'law_land_based_taxation',
                       'law_imperial_examinations', 'law_subjecthood', 'law_traditionalism',
                       'law_censorship', 'law_closed_borders', 'law_freedom_of_conscience',
                       'law_canton_system', 'law_night_watchmen'],
         'MoH china.txt activate_law list is now %s -- re-check the china.txt VC-vs-MoH write-up' % moh_laws)
    need('active_law:lawgroup_land_reform' in moh and 'amendment_chinese_traditional_land_system' in moh,
         'MoH china.txt no longer amends lawgroup_land_reform -- re-check why law_tenant_farmers is kept')
    vc_edu = read(os.path.join(p.vc, 'common/laws/joi_education_system.txt'))
    need('law_classical_learning' in vc_edu and 'requires_law_or' in vc_edu
         and 'law_serfdom' in vc_edu and 'law_imperial_examination' in vc_edu,
         'VC\'s law_classical_learning prerequisite changed -- re-check the china.txt VC-vs-MoH write-up')


def _history_china(p):
    _check_china_activate_law_vs_vc(p)
    return _history_merge(
        p, 'common/history/countries/chi - china.txt', p.moh, 'Mandate of Heaven',
        'company_ong_lung_sheng_tea_company',
        ('ComPatch HC+GoB+MoH x The Great Revision x Victorian Century -- China at 1836',
         '',
         'Both TGR and Mandate of Heaven ship common/history/countries/chi - china.txt.',
         'Same relative path, so the later mod wins the file outright and nothing else',
         'is read.  MoH is later, and what it wins is a full rewrite of Chinese setup --',
         'laws, journal entries, variables, the Ewo Hong company, a land amendment.',
         'TGR\'s single addition to the same country, the Ong Lung Sheng tea company,',
         'goes with the file.  A company that never gets founded produces no error.',
         '',
         'Victorian Century ships this same path too -- REPLACE by path overlap, same as',
         'TGR and MoH.  Checked line by line 26.08.2026 and deliberately left out, not',
         'merged:',
         '',
         '  * VC keeps law_serfdom in lawgroup_land_reform; MoH switches to',
         '    law_tenant_farmers and then applies its own amendment',
         '    (amendment_chinese_traditional_land_system) to whatever law is active in',
         '    that group -- written for MoH\'s choice, not vanilla\'s or VC\'s.',
         '  * VC activates its own bureaucracy law law_imperial_examination (singular,',
         '    VC\'s joi_bureaucracy.txt); MoH activates a differently-spelled',
         '    law_imperial_examinations (plural, MoH\'s own, moh_flavoured_laws.txt).',
         '    Same idea, two unrelated law_type keys with no relation to each other --',
         '    MoH\'s own je_keju journal chain is written for its own law, kept.',
         '  * VC adds law_classical_learning, in its own lawgroup_education_system (a',
         '    group that does not exist without VC).  Its requires_law_or gate is',
         '    law_serfdom OR law_imperial_examination -- neither is true once MoH\'s',
         '    land_reform and bureaucracy picks above are kept, so activating it here',
         '    would start China with a law whose own stated prerequisite is false.',
         '    Left out.',
         '  * The rest of VC\'s file -- eight of its own journal entries',
         '    (imperial_examination_system, grand_council, isolationist_policies and',
         '    five more), four law amendments in groups MoH does not touch, and its own',
         '    set_variable/add_modifier calls -- is VC\'s own parallel China',
         '    political-system chain, same class as MoH\'s (je_warlord_china, je_8_flags,',
         '    je_daoguang_reform_main, je_keju, the ig_intelligentsia/ig_armed_forces',
         '    rework, company_ewo_hong).  Running both chains on the same country is not',
         '    something either author designed for -- same call already made for',
         '    CHI_minguo/CHI_republic in flag_definitions (see hc+vc wip).',
         '',
         'Merged below: MoH\'s file with TGR\'s add_company block appended inside the',
         'country effect.  MoH\'s history, and its verdict against VC above, is otherwise',
         'untouched.',
         '',
         'VARIANTS: needs TGR (the company type is TGR\'s).  In a composition without',
         'TGR, ship Mandate of Heaven\'s file unchanged -- that is, drop this one.  VC\'s',
         'own file is superseded either way, with or without TGR present.'))


def _check_ottoman_laws_vs_vc(p):
    """Unlike China, most of what VC does to the Ottomans' file turns out to be
    a clean, verified-safe addition rather than a competing rework -- see the
    banner in _history_ottoman for the reasoning.  Asserted here so a future
    update to either file re-opens the decision instead of drifting under it."""
    gob = read(os.path.join(p.gob, 'common/history/countries/tur - ottoman empire.txt'))
    vc  = read(os.path.join(p.vc,  'common/history/countries/tur - ottoman empire.txt'))
    vc_laws = re.findall(r'activate_law = law_type:(\S+)', vc)
    need(vc_laws == ['law_monarchy', 'law_autocracy', 'law_millet_system', 'law_subjecthood',
                      'law_traditionalism', 'law_censorship', 'law_land_based_taxation',
                      'law_slave_trade', 'law_madrasa'],
         'VC tur - ottoman empire.txt activate_law list is now %s -- re-check the ottoman VC-vs-GoB write-up' % vc_laws)
    need('active_law:lawgroup_taxation' in vc and 'amendment_salt_monopoly' in vc,
         'VC ottoman file no longer amends lawgroup_taxation with amendment_salt_monopoly')
    need('active_law:lawgroup_governance_principles' in vc and 'amendment_kanunname_law' in vc,
         'VC ottoman file no longer amends lawgroup_governance_principles with amendment_kanunname_law')
    gob_laws = re.findall(r'activate_law = law_type:(\S+)', gob)
    need(gob_laws == ['law_monarchy', 'law_imperial_divan', 'law_scribal_bureaucrats', 'law_millet_system',
                       'law_subjecthood', 'law_traditionalism', 'law_censorship', 'law_land_based_taxation',
                       'law_debt_slavery', 'law_migration_controls'],
         'GoB ottoman file activate_law list is now %s -- re-check the ottoman VC-vs-GoB write-up' % gob_laws)
    need('active_law:lawgroup_education_system' in gob and 'amendment_gbbf_elifba' in gob,
         'GoB ottoman file no longer amends lawgroup_education_system -- re-check why VC\'s law_madrasa is added')
    madrasa = read(os.path.join(p.vc, 'common/laws/joi_education_system.txt'))
    need('law_madrasa' in madrasa and 'requires_law_or' in madrasa and 'law_millet_system' in madrasa,
         'VC\'s law_madrasa prerequisite changed -- re-check the ottoman VC-vs-GoB write-up')


def _splice_vc_into_ottoman(win):
    """Add VC's law_madrasa activation and its two amendments into GoB's own
    body, verified safe (see _check_ottoman_laws_vs_vc and the banner in
    _history_ottoman): law_madrasa's own prerequisite (law_millet_system) is
    already active in GoB's list, and both amendments target law groups GoB
    never touches, whose active law (law_monarchy, law_land_based_taxation) is
    already active in every version of this file."""
    anchor1 = '\t\tactivate_law = law_type:law_migration_controls\n'
    need(win.count(anchor1) == 1,
         'ottoman: GoB\'s law_migration_controls line moved or duplicated -- fix the VC splice anchor')
    win = win.replace(anchor1, anchor1 + '\t\tactivate_law = law_type:law_madrasa   # Victorian Century\n', 1)

    anchor2 = '\t\t# The Sick Man of Europe\n'
    need(win.count(anchor2) == 1, 'ottoman: GoB\'s "# The Sick Man of Europe" comment moved -- fix the VC splice anchor')
    vc_block = (
        '\t\t# Victorian Century\n'
        '\t\tactive_law:lawgroup_taxation ?= {\n'
        '\t\t\tadd_amendment = {\n'
        '\t\t\t\ttype = amendment_salt_monopoly\n'
        '\t\t\t\tsponsor = prev.ig:ig_landowners\n'
        '\t\t\t}\n'
        '\t\t}\n'
        '\t\tactive_law:lawgroup_governance_principles ?= {\n'
        '\t\t\tadd_amendment = {\n'
        '\t\t\t\ttype = amendment_kanunname_law\n'
        '\t\t\t\tsponsor = prev.ig:ig_landowners\n'
        '\t\t\t}\n'
        '\t\t}\n\n'
    )
    return win.replace(anchor2, vc_block + anchor2, 1)


def _history_ottoman(p):
    _check_ottoman_laws_vs_vc(p)
    return _history_merge(
        p, 'common/history/countries/tur - ottoman empire.txt', p.gob, 'Gates of the Bosphorus',
        'company_imperial_arsenal',
        ('ComPatch HC+GoB+MoH x The Great Revision x Victorian Century -- the Ottomans at 1836',
         '',
         'Same shape as the China file: TGR and Gates of the Bosphorus both ship',
         'common/history/countries/tur - ottoman empire.txt, GoB is later and takes the',
         'whole file, and TGR\'s addition -- the Imperial Arsenal company -- disappears',
         'with it.  Silent.',
         '',
         'Victorian Century ships this same path too.  Unlike its China file, most of',
         'what VC does here is much closer to vanilla than GoB\'s own rework -- VC keeps',
         'vanilla\'s law_autocracy and law_slave_trade where GoB swaps in',
         'law_imperial_divan/law_scribal_bureaucrats and law_debt_slavery, and adds no',
         'migration_controls law.  Checked line by line 26.08.2026:',
         '',
         '  * VC adds exactly one law GoB does not have: law_madrasa, in',
         '    lawgroup_education_system.  Its own requires_law_or gate is',
         '    law_state_religion OR law_millet_system OR law_people_of_the_book --',
         '    law_millet_system is active in every version of this file, so the',
         '    prerequisite holds.  GoB itself already amends lawgroup_education_system',
         '    (amendment_gbbf_elifba) but never explicitly activates a law there, so',
         '    without VC that amendment attaches to whatever the engine\'s silent',
         '    default is.  Added: gives GoB\'s own amendment something explicit and',
         '    thematically fitting to attach to instead.',
         '  * VC adds two amendments of its own, to lawgroup_taxation',
         '    (amendment_salt_monopoly) and lawgroup_governance_principles',
         '    (amendment_kanunname_law).  GoB\'s four amendments are in different',
         '    groups (army_model, education_system, land_reform, slavery) -- no',
         '    overlap.  Both target laws already active in GoB\'s own list',
         '    (law_land_based_taxation, law_monarchy).  Added.',
         '  * The rest of VC\'s file -- three extra starting techs, its own',
         '    Sublime-Porte/Peter-the-Great-of-Turkey journal chain (seven entries),',
         '    great_ottomanism_var, an extra modifier -- is VC\'s own parallel Ottoman',
         '    political-flavor system, same class as GoB\'s Sick-Man/Tanzimat chain.',
         '    Left out for the same reason as China\'s parallel chain: running two',
         '    independent political systems on the same country is not something',
         '    either author designed for.',
         '',
         'Merged below: GoB\'s file with VC\'s law_madrasa activation and two amendments',
         'spliced in, then TGR\'s add_company block appended.',
         '',
         'VARIANTS: needs TGR for the company; without it, drop just that append. VC\'s',
         'own file is superseded either way. Dropping VC from the composition should',
         'also drop the two spliced-in lines below (marked "# Victorian Century") --',
         'law_madrasa is a VC law and the two amendment types are VC\'s own.'),
        pre=_splice_vc_into_ottoman)


def _extract_lawgroup_amendments(text):
    """Every `active_law:lawgroup_X ?= { add_amendment = { type = ...
    sponsor = ... } }` block in a country history file, as (group, amendment
    type, exact original text) triples, in file order."""
    pattern = re.compile(
        r'active_law:lawgroup_(\w+) \?= \{[^\n]*\n'
        r'\t\t\tadd_amendment = \{\n\t\t\t\ttype = (\S+)\n\t\t\t\tsponsor = \S+\n\t\t\t\}\n\t\t\}')
    return [(m.group(1), m.group(2), m.group(0)) for m in pattern.finditer(text)]


def _check_usa_laws_vs_vc(p):
    """usa - usa.txt is Hail Columbia's flagship file.  Five law groups
    (trade_policy, economic_system, free_speech, taxation, church_and_state) are
    genuine competitions between HC's own custom historical laws and VC's more
    vanilla-adjacent picks -- HC's choices win, same principle as everywhere
    else in this addon.  What VC adds beyond that is a clean, additive
    Bill-of-Rights amendment chain: fourteen active_law:lawgroup_X blocks, of
    which two are byte-identical to ones HC's file already has and twelve are
    new.  Asserted here so a future update to either file re-opens the
    decision instead of drifting under the write-up in the banner below."""
    hc = read(os.path.join(p.hc, 'common/history/countries/usa - usa.txt'))
    vc = read(os.path.join(p.vc, 'common/history/countries/usa - usa.txt'))

    hc_laws = re.findall(r'activate_law = law_type:(\S+)', hc)
    need(hc_laws == ['law_public_schools', 'law_legacy_slavery', 'law_racial_segregation',
                      'law_usfp_american_system', 'law_agrarianism', 'law_frontier_colonization',
                      'law_right_of_assembly', 'law_no_workers_rights', 'law_usfp_devolved_taxation',
                      'law_national_militia', 'law_local_police', 'law_no_womens_rights',
                      'law_usfp_nominal_separation', 'law_homesteading'],
         'HC usa.txt activate_law list is now %s -- re-check the usa.txt VC-vs-HC write-up' % hc_laws)
    need('start_enactment = law_type:law_universal_suffrage' in hc,
         'HC no longer start_enactments law_universal_suffrage in usa.txt -- re-check the usa.txt VC-vs-HC write-up')

    vc_laws = re.findall(r'activate_law = law_type:(\S+)', vc)
    need(vc_laws == ['law_public_schools', 'law_legacy_slavery', 'law_racial_segregation',
                      'law_homesteading', 'law_protectionism', 'law_interventionism',
                      'law_frontier_colonization', 'law_protected_speech', 'law_no_workers_rights',
                      'law_per_capita_based_taxation', 'law_national_militia', 'law_local_police',
                      'law_no_womens_rights', 'law_total_separation'],
         'VC usa.txt activate_law list is now %s -- re-check the usa.txt VC-vs-HC write-up' % vc_laws)

    amendments = _extract_lawgroup_amendments(vc)
    need(len(amendments) == 14,
         'VC usa.txt now has %d lawgroup amendments (expected 14) -- re-check the usa.txt VC-vs-HC write-up'
         % len(amendments))
    dup_types = {'amendment_american_second_amendment', 'amendment_tradition_of_free_elections'}
    dups = [(g, t) for g, t, _ in amendments if t in dup_types]
    need(dups == [('governance_principles', 'amendment_american_second_amendment')]
         or ('distribution_of_power', 'amendment_tradition_of_free_elections') in dups,
         'VC usa.txt amendment duplicates changed -- re-check the usa.txt VC-vs-HC write-up')
    for t in dup_types:
        need(t in hc, 'HC usa.txt no longer has VC\'s supposedly-duplicate %s -- re-check the usa.txt VC-vs-HC write-up' % t)
    new_amendments = [(g, t, blk) for g, t, blk in amendments if t not in dup_types]
    need(len(new_amendments) == 12,
         '%d new (non-duplicate) VC amendments found, expected 12 -- re-check the usa.txt VC-vs-HC write-up'
         % len(new_amendments))
    need(sorted(t for _, t, _ in new_amendments) == sorted([
        'amendment_american_third_amendment', 'amendment_american_forth_amendment',
        'amendment_american_fifth_amendment', 'amendment_american_sixth_amendment',
        'amendment_american_seventh_amendment', 'amendment_american_eighth_amendment',
        'amendment_american_ninth_amendment', 'amendment_american_tenth_amendment',
        'amendment_usa_declaration_of_independence', 'amendment_american_first_amendment',
        'amendment_common_law', 'amendment_american_fugitive_slaves_act']),
         'VC usa.txt\'s twelve new amendment types changed -- re-check the usa.txt VC-vs-HC write-up')
    return new_amendments


def _splice_vc_amendments_into_usa(hc, new_amendments):
    anchor = ('active_law:lawgroup_governance_principles ?= { # Presidential Republic\n'
              '\t\t\tadd_amendment = {\n'
              '\t\t\t\ttype = amendment_american_second_amendment\n'
              '\t\t\t\tsponsor = PREV.ig:ig_rural_folk\n'
              '\t\t\t}\n'
              '\t\t}\n')
    need(hc.count(anchor) == 1, 'usa.txt: HC\'s Presidential Republic amendment block moved -- fix the VC splice anchor')
    block = '\n\t\t# Victorian Century -- see the banner above\n' + '\n'.join(blk for _, _, blk in new_amendments) + '\n'
    return hc.replace(anchor, anchor + block, 1)


def _history_usa(p):
    new_amendments = _check_usa_laws_vs_vc(p)
    hc = read(os.path.join(p.hc, 'common/history/countries/usa - usa.txt'))
    out = _splice_vc_amendments_into_usa(hc, new_amendments)
    note('usa - usa.txt: HC body (its own law choices kept for the five groups VC competes on) '
         '+ 12 of VC\'s 14 lawgroup amendments spliced in (2 were already byte-identical in HC\'s file)')
    return banner(
        'ComPatch HC+GoB+MoH x Victorian Century -- the USA at 1836',
        '',
        'Hail, Columbia! and Victorian Century both ship',
        'common/history/countries/usa - usa.txt at the vanilla path -- this is HC\'s',
        'flagship file, the one the whole "United States Flavor Pack" is built around,',
        'and HC loads later so it wins the path outright.  Checked line by line',
        '26.08.2026.',
        '',
        'Fifteen law groups are explicitly activated by one or both files.  Ten agree',
        '(education_system, slavery, citizenship, colonization, labor_rights,',
        'army_model, policing, rights_of_women, land_reform, and distribution_of_power',
        'left to start_enactment/vanilla default by both).  Five are genuine',
        'competitions, and every one of HC\'s three own custom laws is in this list:',
        '',
        '  * trade_policy: HC\'s own law_usfp_american_system vs VC\'s law_protectionism.',
        '  * economic_system: HC\'s law_agrarianism vs VC\'s law_interventionism.',
        '  * free_speech: HC\'s law_right_of_assembly vs VC\'s law_protected_speech.',
        '  * taxation: HC\'s own law_usfp_devolved_taxation vs VC\'s',
        '    law_per_capita_based_taxation.',
        '  * church_and_state: HC\'s own law_usfp_nominal_separation vs VC\'s',
        '    law_total_separation.',
        '',
        'HC\'s picks win all five, same principle as everywhere else in this addon: a',
        'flavor pack\'s own signature content is what stays, and three of these five',
        'are laws HC wrote for itself.  Also kept as HC-only, untouched by VC: the',
        '`start_enactment = law_type:law_universal_suffrage` (HC deliberately starts',
        'the USA mid-transition, "states are in the middle of piecemeal removing tax',
        'obligations"), and HC\'s entire USFP journal-entry/ideology/interest-group',
        'chain.',
        '',
        'What VC adds beyond the law list is a clean Bill-of-Rights amendment chain --',
        'fourteen `active_law:lawgroup_X ?= { add_amendment = {...} }` blocks, one to',
        'ten amendments plus the Declaration of Independence and common law.  Two are',
        'byte-identical to blocks HC\'s file already has',
        '(amendment_american_second_amendment on governance_principles,',
        'amendment_tradition_of_free_elections on distribution_of_power) -- both mods',
        'clearly draw from the same shared amendment set.  The other twelve are new,',
        'and every one is safe to add regardless of which side won the law list above:',
        'an amendment attaches to whatever law is active in its group, not to a',
        'specific one, and (per the checks in _check_usa_laws_vs_vc) every targeted',
        'group already has an active law under HC\'s own choices, or -- for',
        'governance_principles/bureaucracy/internal_security, which no activate_law in',
        'either file ever explicitly sets -- the same implicit-default mechanic HC\'s',
        'own file already relies on for its pre-existing governance_principles and',
        'bureaucracy amendments.',
        '',
        'NOT merged: VC\'s competing law picks (see above); VC\'s own tariff setting',
        '(g:fabric, tied to VC\'s trade-law assumptions, not HC\'s); and VC\'s entire',
        'parallel USA political/flavor chain -- its own "real manifest destiny"',
        'tracking variables and an active je_texas_usa (HC\'s own manifest_destiny.txt',
        'already deliberately suppresses the vanilla decision in favor of its own',
        '1100-line journal chain -- see hc+tgr done/README.md; a second, VC-driven',
        'Manifest Destiny system would double up), plus VC\'s own missouri_compromise',
        'modifier (HC already has usfp_missouri_compromise_decaying), us_second_bank,',
        'failed_assassination_on_aj_president, and six of VC\'s own journal entries',
        '(before_us_civil_war, supreme_court, united_states_congress,',
        'westward_movement, je_seminole_wars, joi_flavor_usa.1).  Same class of',
        'decision as China\'s and the Ottomans\' parallel chains.',
        '',
        'add_company = company_type:company_william_cramp is byte-identical in both',
        'files (same date, same state) -- nothing to merge.',
        '',
        'VARIANTS: needs VC for the twelve spliced-in amendment types.  Without VC,',
        'ship HC\'s file unchanged -- drop this one.') + out


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
    for probe in (p.van, p.tgr, p.kai, p.morg, p.hc, p.gob, p.moh, p.vc):
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
