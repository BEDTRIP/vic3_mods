"""
regen_greys_vc.py -- builds the Grey's x Victorian Century compatch in
`_greys/greys+vc done`.  Task GR.1, the biggest pair of the Grey's addon
(129 shared keys out of `pair_matrix.py --pair "VC,Grey's"`).

WHY THIS PAIR HURTS
-------------------
Victorian Century writes most of its economy with full bodies
(`REPLACE_OR_CREATE:`), Grey's pack loads after it and writes the same records
with full bodies too (`TRY_REPLACE:` / `REPLACE:` / `REPLACE_OR_CREATE:`).
Last body wins, so VC's contribution to every shared record is gone -- silently,
nothing in error.log.

WHAT IS AND IS NOT A CONFLICT (checked 2026-08-27, all 129 keys)
----------------------------------------------------------------
Real losses, and what this compatch does about each:

  60 common/state_traits    VC REPLACE_OR_CREATE vs USU TRY_REPLACE, both full
                            bodies.  Merged: USU's body is the base (its river
                            ports and its infrastructure rebalance are one
                            system), VC's fields are appended where USU does not
                            name them.  39 field-level collisions in ~30 traits
                            stay USU's -- 22 of them state_infrastructure_add,
                            which USU cuts on purpose because it hands the same
                            infrastructure back as state_building_river_port_max_level_add.
   6 common/company_types   USU TRY_REPLACE with a full body over VC's full body.
                            Merged per company, USU's body as the base.
  10 common/production_methods  VC INJECT:, USU re-issues the whole record.
                            Re-issued VC's own INJECT verbatim after USU:
                            "переиздать чужой INJECT: поверх более позднего тела
                            -- точное восстановление" (Правила работы с модами,
                            раздел "Переопределение").  Semantics-agnostic: it
                            does not depend on how the open REPLACE:/sub-block
                            question is resolved.
   2 common/buildings       same shape: VC TRY_INJECT can_build_private (its
                            autonomous-investment gate), grey_food / grey_food_2_ranch
                            re-issue the building.  VC's inject re-issued verbatim.
   1 common/pop_needs       popneed_basic_food only.  grey_food_2_ranch's body is
                            vanilla verbatim, so VC's groceries weight (1.5) is not
                            lost to a redesign, it is lost to a copy of vanilla.
   1 common/script_values   cultural_community_creation_weight: soft_pop rewrote the
                            script, VC extended the harbour trait list with its own
                            17 port traits.  soft_pop's body plus VC's trait names.

Not a conflict, deliberately no file (write-up in README):

  10 common/combat_unit_types    both sides INJECT: the same upkeep_modifier but
                                 disjoint leaf keys (VC arms/ammo, USU
                                 goods_input_usu_logistics_add) -- modifier blocks
                                 accumulate, both survive.
   3 common/mobilization_options VC INJECT:s upkeep_modifier, USU INJECT:s
                                 upkeep_modifier_unscaled -- different sub-blocks.
  27 common/company_types        USU uses TRY_INJECT:; `INJECT:` into a list adds,
                                 it does not replace, and into a modifier block it
                                 accumulates.  Nothing of VC's is displaced.
   5 popneed_*                   popneed_heating: VC's body is vanilla verbatim,
                                 nothing to lose.  communication / free_movement /
                                 leisure / luxury_food: Grey's redesign is
                                 deliberate (services entries and min_supply_share
                                 everywhere, whole scale recomputed) and wins.
   3 common/defines              NAI and NEconomy share the group name only, no leaf
                                 key.  NPops shares 6 leaves, 4 of them differ; the
                                 decision (2026-08-27) is that soft_pop's demography
                                 is one system and its numbers stay.
   1 common/static_modifiers     state_region_devastation: soft_econ's rework is
                                 deliberate and touches the one field VC changes
                                 (state_devastation_decay_mult), so it wins by the
                                 same rule as the traits.

VC-ONLY: every file here exists because of Victorian Century.  Since decision #11
(2026-08-26) VC is optional, so the whole folder is deletable as one -- the banner
on every file says so.

Usage:
    python3 regen_greys_vc.py            # write the compatch
    python3 regen_greys_vc.py --check    # report only, exit 1 if sources drifted
"""

from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vic3lib as V  # noqa: E402
from vic3merge3 import brace_balance, merge3, needs_bom  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
res = lambda p: os.path.normpath(os.path.join(HERE, p))

OUT = res("../_greys/greys+vc done")
MODS = {
    "VANILLA": res("../../vic3_mods_out/.vanillaVIC3"),
    "VC": res("../../vic3_mods_out/VC"),
    "soft_econ": res("../../vic3_mods_out/grey_add_alot_of_things/_grey_soft_econ"),
    "soft_pop": res("../../vic3_mods_out/grey_add_alot_of_things/_grey_soft_pop"),
    "USU": res("../../vic3_mods_out/grey_add_alot_of_things/grey_usu"),
    "cinosphere": res("../../vic3_mods_out/grey_add_alot_of_things/grey_deeper_cinosphere"),
    "food": res("../../vic3_mods_out/grey_add_alot_of_things/grey_food"),
    "ranch": res("../../vic3_mods_out/grey_add_alot_of_things/grey_food_2_ranch"),
    "diplo": res("../../vic3_mods_out/grey_add_alot_of_things/grey_diplo"),
    "subject": res("../../vic3_mods_out/grey_add_alot_of_things/grey_subject"),
}
# Everything that loads between VC and this compatch, in load order.  Used to
# find the body that actually wins a record -- not just USU's, in case another
# Grey's mod (or the LLWA addon) re-issues the same key later.
ADDON_LLWA = res("../__addon/addon llwa")
LLWA_EXT_FILE = os.path.join(ADDON_LLWA, "common/company_types/zz_llwa_companies_extensions.txt")

CHAIN_AFTER_VC = [
    ("MEGAPACK", res("../__megapacks/megapack no t&r")),
    ("ADDON-VC", res("../__addon/addon vc")),
    ("LLWA", res("../../vic3_mods_out/llwa")),
    ("llwa+morg", res("../_llwa/llwa+morg out")),
    ("usu_llwa", res("../_greys/usu_llwa out outdate")),
    ("ADDON-LLWA", res("../__addon/addon llwa")),
    ("soft_econ", MODS["soft_econ"]),
    ("soft_pop", MODS["soft_pop"]),
    ("USU", MODS["USU"]),
    ("cinosphere", MODS["cinosphere"]),
    ("food", MODS["food"]),
    ("ranch", MODS["ranch"]),
    ("diplo", MODS["diplo"]),
    ("subject", MODS["subject"]),
]
FULL_BODY = ("", "REPLACE", "REPLACE_OR_CREATE", "TRY_REPLACE")

DATE = "2026-08-27"
CHECK_ONLY = False
WRITTEN: dict[str, bytes] = {}
NOTES: list[str] = []

BANNER = """### === VC-ONLY FILE === delete "{fname}" to play without
### Victorian Century. This whole compatch is the VC layer -- deleting
### this file changes nothing else. To drop VC entirely, delete this
### whole compatch folder (_greys/greys+vc done) and nothing else --
### no other Grey's compatch references it.
"""

# zz_gvc_companies.txt is the one file in this folder that ISN'T VC-only any
# more (added 2026-08-27, GR.16): six of its records also restore addon-LLWA's
# extension_building_types, which every addon-LLWA player needs regardless of
# VC. Decision #9 in the project plan: base body carries the mandatory
# grey_usu+LLWA fix, VC's own contribution is folded in as the optional layer.
BANNER_CARRIES_VC = """### === CARRIES A VC LAYER === this file's base content (addon-LLWA's
### extension_building_types on six railway companies, see GR.16) is needed by
### every addon-LLWA player, whether or not Victorian Century is installed.
### Victorian Century's own contribution to these same six companies is folded
### in as an additional, optional layer. Playing with addon-LLWA but WITHOUT
### Victorian Century: rename "{fname}.off" to "{fname}" (replacing this
### file) to drop that layer. Playing with neither addon-LLWA nor Victorian
### Century: delete this whole compatch folder as usual (see decision #9).
"""

BANNER_OFF_TWIN = """### === INACTIVE -- NO-VC VARIANT (.off) === Victoria 3 does not load
### unrecognized file extensions, so this file does nothing while named
### "{fname}.off". It has the same six railway companies with addon-LLWA's
### extension_building_types restored (see GR.16), but WITHOUT Victorian
### Century's contribution folded in. Rename it to "{fname}" (replacing the
### active file) if you use addon-LLWA WITHOUT Victorian Century. If you use
### neither, delete this whole compatch folder instead -- do not use this file.
"""

HEADER = """
### ComPatch Grey's x Victorian Century -- {what}
###
{why}###
### Generated by tools/regen_greys_vc.py on {date}. Do not hand-edit: the next
### run overwrites this file. Change the generator instead.
### Load order: ... -> Victorian Century -> ... -> the whole Grey's pack -> THIS.
"""

KEYRE = re.compile(r"(?:([A-Z_]+):)?([A-Za-z0-9_.\-]+)\s*=\s*\{")


def match_brace(text: str, i: int) -> int:
    """Index of the brace matching text[i], skipping comments and quoted strings.

    vic3lib._match_brace counts braces inside `# comments` too, and at least one
    file in the chain (a commented-out block in a script value) trips it.
    """
    d = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == "#":
            j = text.find("\n", i)
            i = n if j < 0 else j + 1
            continue
        if c == '"':
            j = text.find('"', i + 1)
            i = n if j < 0 else j + 1
            continue
        if c == "{":
            d += 1
        elif c == "}":
            d -= 1
            if d == 0:
                return i
        i += 1
    raise ValueError("unbalanced braces from offset %d" % i)


def top_entries(text: str):
    """Yield (prefix, key, body) for every depth-0 record in a game file.

    A malformed prefix (`TRY_INJECT::company_x`, three of them in USU) does not
    match and is skipped -- which is what the engine does with it too, so the
    scan agrees with the game.
    """
    d = i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == "#":
            j = text.find("\n", i)
            i = n if j < 0 else j + 1
            continue
        if c == '"':
            j = text.find('"', i + 1)
            i = n if j < 0 else j + 1
            continue
        if c == "{":
            d += 1; i += 1; continue
        if c == "}":
            d -= 1; i += 1; continue
        if d == 0:
            m = KEYRE.match(text, i)
            if m:
                o = text.index("{", m.start())
                cl = match_brace(text, o)
                yield (m.group(1) or "", m.group(2), text[o + 1:cl])
                i = cl + 1
                continue
        i += 1


def scan(root: str, cat: str) -> dict:
    """{key: [(prefix, relpath, body), ...]} for one mod folder, one category."""
    out: dict = {}
    d = os.path.join(root, cat)
    if not os.path.isdir(d):
        return out
    for dp, _, fs in os.walk(d):
        for fn in sorted(fs):
            if not fn.endswith(".txt"):
                continue
            p = os.path.join(dp, fn)
            for pref, key, body in top_entries(V.read(p)):
                out.setdefault(key, []).append(
                    (pref, os.path.relpath(p, root).replace("\\", "/"), body))
    return out


_CACHE: dict = {}


def cat_of(who: str, cat: str) -> dict:
    if (who, cat) not in _CACHE:
        root = MODS.get(who) or dict(CHAIN_AFTER_VC)[who]
        _CACHE[(who, cat)] = scan(root, cat)
    return _CACHE[(who, cat)]


def winner(cat: str, key: str):
    """(who, prefix, relpath, body) of the last full body in the chain after VC."""
    found = None
    for who, _root in CHAIN_AFTER_VC:
        for pref, rel, body in cat_of(who, cat).get(key, []):
            if pref in FULL_BODY:
                found = (who, pref, rel, body)
    return found


def scalars(body: str) -> "list[tuple[str, str]]":
    """Depth-0 `k = v` pairs of a body, comments stripped, order kept."""
    txt = re.sub(r"#[^\n]*", "", body)
    flat = []
    d = 0
    for ch in txt:
        if ch == "{":
            d += 1
        elif ch == "}":
            d -= 1
        elif d == 0:
            flat.append(ch)
    return re.findall(r"([A-Za-z_][A-Za-z_0-9]*)\s*=\s*(\"[^\"]*\"|[^\s{}]+)", "".join(flat))


def write(rel: str, text: str, what: str, why: str, bom: bool | None = None, banner: str | None = None):
    fname = os.path.basename(rel).removesuffix(".off")
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    body = ((banner or BANNER).format(fname=fname)
            + HEADER.format(what=what, why=why, date=DATE)
            + "\n" + text.rstrip("\n") + "\n")
    bal = brace_balance(body)
    assert bal == 0, f"{rel}: brace balance {bal}"
    if bom is None:
        bom = needs_bom(body)
    blob = body.encode("utf-8-sig" if bom else "utf-8")
    WRITTEN[rel] = blob
    if CHECK_ONLY:
        old = open(path, "rb").read() if os.path.isfile(path) else None
        print(f"  {'SAME  ' if old == blob else 'DRIFT '} {rel}")
        return
    tmp = path + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(blob)
    os.replace(tmp, path)
    print(f"  wrote {rel}  ({len(body.splitlines())} lines, bom={bom})")


# --------------------------------------------------------------------------
# 1. state_traits -- 60 records, USU's body plus VC's un-collided fields
# --------------------------------------------------------------------------

def merge_trait(van: str, base: str, vcb: str):
    """grey_usu's body with VC's modifier fields folded back in.

    One rule everywhere in this generator: intent is a difference from vanilla.
    A full body re-states every field, so grey_usu carrying a field with vanilla's
    own value is inheritance, not a decision -- there VC's number stands. Where
    grey_usu actually moved a number, or deliberately dropped a vanilla field, it
    wins (decision 2026-08-27: its river ports and the infrastructure it takes
    away are one system).
    """
    span = V.sub_span(base, "modifier")
    assert span, "base trait body has no modifier block"
    fv = dict(scalars(V.sub(van, "modifier")[1:-1])) if V.sub(van, "modifier") else {}
    fb = dict(scalars(V.sub(base, "modifier")[1:-1]))
    vmod = V.sub(vcb, "modifier")
    added, retuned, dropped = [], [], []
    body = base
    for k, x in scalars(vmod[1:-1] if vmod else ""):
        if k not in fb:
            if k in fv:
                dropped.append(k)             # grey_usu removed a vanilla field on purpose
            else:
                added.append((k, x))
        elif fb[k] == fv.get(k) and x != fb[k]:
            pat = re.compile(r"(?m)^([ \t]*)" + re.escape(k) + r"\s*=\s*" + re.escape(fb[k]) + r"\b")
            hits = pat.findall(body)
            assert len(hits) == 1, f"{k}: {len(hits)} places to substitute in the trait body"
            body = pat.sub(lambda m: f"{m.group(1)}{k} = {x}\t# VC (grey_usu only re-stated vanilla's {fb[k]})", body, count=1)
            retuned.append(k)
    if added:
        span = V.sub_span(body, "modifier")
        lines = "".join("\t\t%s = %s\t# VC\n" % kv for kv in added)
        close = span[1] - 1                   # index of the modifier's closing brace
        ls = body.rfind("\n", 0, close) + 1   # keep that brace's own indentation
        body = body[:ls] + lines + body[ls:]
    return body, [k for k, _ in added], retuned, dropped


def build_state_traits():
    vc = cat_of("VC", "common/state_traits")
    usu = cat_of("USU", "common/state_traits")
    keys = sorted(k for k in vc if k in usu)
    assert len(keys) == 60, f"expected 60 shared state traits, found {len(keys)}"
    records, carried, untouched = [], 0, []
    stats = [0, 0, 0]
    for k in keys:
        assert len(vc[k]) == 1, f"VC defines {k} {len(vc[k])} times"
        vcp, vcf, vcb = vc[k][0]
        assert vcp == "REPLACE_OR_CREATE", f"VC changed its prefix on {k}: {vcp}"
        w = winner("common/state_traits", k)
        assert w, f"nobody after VC re-issues {k} -- is this still a conflict?"
        who, pref, rel, base = w
        assert who == "USU", f"{k} is now won by {who} ({rel}), not USU -- re-check the merge"
        vanb = cat_of("VANILLA", "common/state_traits").get(k, [("", "", "")])[0][2]
        merged, added, retuned, dropped = merge_trait(vanb, base, vcb)
        carried += len(added) + len(retuned)
        stats[0] += len(added); stats[1] += len(retuned); stats[2] += len(dropped)
        if not (added or retuned):
            untouched.append(k)
        note = "; ".join(x for x in (
            ("VC adds: " + ", ".join(added)) if added else "",
            ("VC's number kept where grey_usu only re-stated vanilla: " + ", ".join(retuned)) if retuned else "",
            ("grey_usu drops these vanilla fields on purpose, VC's version not restored: "
             + ", ".join(dropped)) if dropped else "",
        ) if x) or "nothing of VC's survives: grey_usu retuned every field VC touches"
        records.append(f"# {k}\n# base: {who} {rel} ({pref}). {note}\n"
                       f"REPLACE_OR_CREATE:{k} = {{{merged}}}")
    NOTES.append(f"state_traits: 60 records, {carried} VC fields carried "
                 f"({stats[0]} added, {stats[1]} where grey_usu only re-stated vanilla), "
                 f"{stats[2]} VC fields left out because grey_usu drops them on purpose, "
                 f"{len(untouched)} traits where VC had nothing left to carry")
    write("common/state_traits/zz_gvc_state_traits.txt", "\n\n".join(records),
          "60 state traits VC and grey_usu both rewrite",
          "### VC writes these with REPLACE_OR_CREATE: and full bodies, grey_usu with\n"
          "### TRY_REPLACE: and full bodies, and grey_usu loads later -- so with both mods\n"
          "### installed not one of VC's 60 traits does anything. Base here is grey_usu's\n"
          "### body: its state_building_river_port_max_level_add is one system with the\n"
          "### infrastructure it takes away, and splitting the two would give rivers both.\n"
          "### VC's fields are appended only where grey_usu does not name the same field\n"
          "### (decision 2026-08-27); every added line is marked # VC.\n")


# --------------------------------------------------------------------------
# 2. company_types -- 6 records, three-way merge over vanilla
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Structural record merge (used by the company_types builder)
#
# A line-based three-way merge is wrong for these records: on company_mantetsu
# it dropped grey_usu's `building_river_port` INTO the middle of a block VC adds
# right above it (possible_prestige_goods), because an insertion by one side sat
# inside a range the other side replaced. Records here are a bag of named
# sub-blocks, so merge them as such: same rule as the state traits -- grey_usu's
# version wins any sub-block both sides rewrote, VC's survives where grey_usu is
# silent -- but applied per sub-block, and per list item / per modifier field one
# level down, where that is unambiguous.
# --------------------------------------------------------------------------

def items_of(body: str):
    """[(name, text)] for every depth-0 statement, in order, comments attached."""
    out, pend = [], []
    i, n, d = 0, len(body), 0
    line_start = 0
    while i < n:
        c = body[i]
        if c == "#":
            j = body.find("\n", i)
            if d == 0:
                pend.append(body[i:(n if j < 0 else j)].strip())
            i = n if j < 0 else j + 1
            continue
        if c == '"':
            j = body.find('"', i + 1)
            i = n if j < 0 else j + 1
            continue
        if c == "{":
            d += 1; i += 1; continue
        if c == "}":
            d -= 1; i += 1; continue
        if d == 0:
            m = re.compile(r"([A-Za-z_][A-Za-z_0-9]*)\s*=\s*").match(body, i)
            if m:
                rest = body[m.end():]
                if rest[:1] == "{":
                    o = m.end()
                    cl = match_brace(body, o)
                    out.append((m.group(1), body[m.start():cl + 1], pend)); pend = []
                    i = cl + 1
                    continue
                mv = re.compile(r'("[^"]*"|[^\s{}#]+)').match(rest)
                if mv:
                    out.append((m.group(1), body[m.start():m.end() + mv.end()], pend)); pend = []
                    i = m.end() + mv.end()
                    continue
        i += 1
    return out


def _inner(text: str) -> str:
    o = text.index("{")
    return text[o + 1:match_brace(text, o)]


def _kind(*texts: str) -> str:
    """Classify a sub-block by ALL the versions of it, not just one side's.

    Deciding on grey_usu's text alone called company_mantetsu's `potential` a flat
    field bag -- true of grey_usu's one-liner, false of VC's, which wraps two
    cultures in an OR. The merge then silently dropped VC's second culture instead
    of reporting a both-sides rewrite.
    """
    kinds = set()
    for text in texts:
        if not text or "{" not in text:
            kinds.add("scalar"); continue
        inner = re.sub(r"#[^\n]*", "", _inner(text))
        if "=" not in inner:
            kinds.add("list"); continue
        kinds.add("complex" if [nm for nm, a, o, c in V._depth0_iter(inner)] else "fields")
    if "complex" in kinds:
        return "complex"
    if kinds == {"list"} or kinds == {"list", "scalar"}:
        return "list"
    return "fields" if "fields" in kinds else "scalar"


def _tokens(text: str):
    return [t for t in re.sub(r"#[^\n]*", "", _inner(text)).split() if t]


def _fields(text: str):
    return scalars(_inner(text))


def _render(name: str, kind: str, payload) -> str:
    if kind == "list":
        return "%s = {\n%s\t}" % (name, "".join("\t\t%s\n" % t for t in payload))
    if kind == "fields":
        return "%s = {\n%s\t}" % (name, "".join("\t\t%s = %s\n" % kv for kv in payload))
    return payload


def merge_record(van: str, vc: str, usu: str, key: str):
    """grey_usu's record with VC's surviving contribution folded back in."""
    Iv = {n: t for n, t, _c in items_of(van)}
    Ic = {n: t for n, t, _c in items_of(vc)}
    order = items_of(usu)
    Iu = {n: t for n, t, _c in order}
    norm = lambda s: re.sub(r"\s+", " ", re.sub(r"#[^\n]*", "", s or "")).strip()

    lines, notes = [], []
    seen = set()
    for name, text, comments in order:
        seen.add(name)
        for c in comments:
            lines.append("\t" + c)
        v, a, b = Iv.get(name), Ic.get(name), text
        vc_changed = a is not None and norm(a) != norm(v)
        usu_changed = norm(b) != norm(v)
        if not vc_changed or a is None:
            lines.append("\t" + b.strip())
            continue
        if not usu_changed:
            lines.append("\t" + a.strip())
            notes.append(f"{name}: VC's version (grey_usu leaves vanilla alone)")
            continue
        kind = _kind(v, a, b)
        if kind == "list":
            # A full body re-states everything, so "grey_usu also has this item" is not
            # evidence that grey_usu wants it -- only an item grey_usu ADDED (not in
            # vanilla) is. So VC's removals stand unless grey_usu added the item back.
            vanl, vcl, usul = _tokens(v or "{}"), _tokens(a), _tokens(b)
            dropped = [t for t in vanl if t not in vcl and t in usul]
            merged = [t for t in usul if t not in dropped]
            merged += [t for t in vcl if t not in merged]
            lines.append("\t" + _render(name, "list", merged))
            notes.append(f"{name}: VC adds {[t for t in vcl if t not in usul]}, "
                         f"VC drops {dropped}, grey_usu adds "
                         f"{[t for t in usul if t not in vanl]}")
        elif kind == "fields":
            # Same reasoning one level down: a field grey_usu re-states with vanilla's
            # own value is inherited, not chosen, so VC's removal of it stands.
            fv, fa, fb = dict(_fields(v or "{}")), dict(_fields(a)), dict(_fields(b))
            gone = [k2 for k2 in fv if k2 not in fa and fb.get(k2) == fv[k2]]
            kept_gone = [k2 for k2 in fv if k2 not in fa and k2 in fb and k2 not in gone]
            merged = []
            for k2, x in _fields(b):
                if k2 in gone:
                    continue
                if x == fv.get(k2) and k2 in fa and fa[k2] != x:
                    merged.append((k2, fa[k2]))          # grey_usu only re-stated vanilla
                else:
                    merged.append((k2, x))
            add = [(k2, x) for k2, x in _fields(a) if k2 not in fb and k2 not in fv]
            skipped = [k2 for k2, x in _fields(a) if k2 not in fb and k2 in fv]
            merged += add
            lines.append("\t" + _render(name, "fields", merged))
            notes.append(f"{name}: grey_usu's fields plus VC's {[k2 for k2, _ in add]}"
                         + (f"; VC removes {gone}" if gone else "")
                         + (f"; VC removes {kept_gone} but grey_usu retuned them, kept"
                            if kept_gone else "")
                         + (f"; VC retunes {skipped} but grey_usu drops the field, left out"
                            if skipped else ""))
        else:
            lines.append("\t" + b.strip())
            notes.append(f"{name}: both rewrote it, kept grey_usu's")
    extra = [(n, t, c) for n, t, c in items_of(vc) if n not in seen]
    for name, text, comments in extra:
        lines.append("")
        lines.append("\t# VC-only block, grey_usu's body does not have it")
        lines.append("\t" + text.strip())
        notes.append(f"{name}: VC-only block, appended")
    return "\n" + "\n".join(lines) + "\n", notes


COMPANIES = [
    "company_great_indian_railway",
    "company_mantetsu",
    "company_orient_express",
    "company_panama_company",
    "company_prussian_state_railways",
    "company_suez_company",
]
# The seventh full-body collision that is NOT here: company_putilov_company.
# grey_usu writes it as `TRY_INJECT::company_putilov_company` -- two colons. A
# malformed prefix does not load at all (same class as REPLACE:REPLACE:), so USU's
# river port and its usu_railway_line prosperity line never reach that company and
# VC's body survives untouched. Nothing to merge, and fixing USU's typo is a
# Grey's-internal job (it is broken without VC too), not this compatch's.


# Six of these also collide with addon-LLWA (GR.16): grey_usu's full body here
# pre-dates addon-LLWA and does not carry its extension_building_types
# contribution either, same class of loss as VC's. Read live, not hardcoded --
# a future addon-LLWA update that changes what it injects on these six should
# make this fail loudly, not silently keep an old building type.
LLWA_EXTRA_EXPECTED = {
    "company_great_indian_railway": ["LLWA_building_roadway"],
    "company_mantetsu": ["LLWA_building_roadway"],
    "company_orient_express": ["LLWA_building_roadway"],
    "company_prussian_state_railways": ["LLWA_building_roadway"],
    "company_panama_company": ["LLWA_building_riverway", "LLWA_building_waterway"],
    "company_suez_company": ["LLWA_building_riverway", "LLWA_building_waterway"],
}


def llwa_extra_for(k: str) -> list[str]:
    ext_text = V.read(LLWA_EXT_FILE)
    _decl, ext_body = V.entry(ext_text, k, prefix="TRY_INJECT:")
    ext_list = V.sub(ext_body, "extension_building_types")
    assert ext_list is not None, f"{k}: addon-LLWA no longer injects extension_building_types"
    want = LLWA_EXTRA_EXPECTED[k]
    for t in want:
        assert t in ext_list, f"{k}: addon-LLWA's inject changed, {t} not found: {ext_list}"
    return want


def with_llwa_extension(body: str, tokens: list[str]) -> str:
    """Append LLWA building type(s) to body's extension_building_types list, additively."""
    span = V.sub_span(body, "extension_building_types")
    assert span, "no extension_building_types sub-block to extend"
    cur = V.sub(body, "extension_building_types")
    cur_tokens = _tokens(cur)
    missing = [t for t in tokens if t not in cur_tokens]
    assert missing, "LLWA tokens already present -- nothing to add, check by hand"
    lines = "".join("\t\t%s\n" % t for t in missing)
    close = span[1] - 1
    ls = body.rfind("\n", 0, close) + 1
    return body[:ls] + lines + body[ls:]


def build_companies():
    van = cat_of("VANILLA", "common/company_types")
    vc = cat_of("VC", "common/company_types")
    records, off_records = [], []
    for k in COMPANIES:
        assert k in van, f"{k} is no longer a vanilla company -- re-check"
        vcp, vcf, vcb = vc[k][0]
        w = winner("common/company_types", k)
        assert w, f"nobody after VC re-issues {k} any more"
        who, pref, rel, base = w
        assert who == "USU", f"{k} is now won by {who} ({rel})"
        body, notes = merge_record(van[k][0][2], vcb, base, k)
        assert brace_balance(body) == 0, f"{k}: merged body is unbalanced"
        for n in notes:
            print(f"      {k}: {n}")
            NOTES.append(f"{k}: {n}")

        llwa_tokens = llwa_extra_for(k)
        body = with_llwa_extension(body, llwa_tokens)
        off_body = with_llwa_extension(base, llwa_tokens)
        llwa_note = f"extension_building_types: addon-LLWA's {llwa_tokens} restored (GR.16)"
        NOTES.append(f"{k}: {llwa_note}")

        head = "\n".join("# " + n for n in notes + [llwa_note])
        records.append(f"# {k} -- base: grey_usu {rel} ({pref}), VC's contribution folded back\n"
                       f"{head}\nREPLACE_OR_CREATE:{k} = {{{body}}}")
        off_records.append(f"# {k} -- base: grey_usu {rel} ({pref}), no VC (this is the no-VC variant)\n"
                           f"# {llwa_note}\nREPLACE_OR_CREATE:{k} = {{{off_body}}}")

    what = "6 companies grey_usu re-issues with a full body over VC's, addon-LLWA layer restored"
    why = ("### grey_usu moves these six off building_railway onto its own\n"
          "### building_usu_railway_line, and to do that it has to TRY_REPLACE: the whole\n"
          "### record -- which also throws away everything VC wrote into it (prestige goods,\n"
          "### prosperity modifiers, culture gates, ai weights). Merged per sub-block against\n"
          "### vanilla as the common ancestor: grey_usu wins any sub-block both sides\n"
          "### rewrote, lists are unioned, modifier blocks merged field by field, and blocks\n"
          "### only VC has are appended. Every record carries the merge log in its comments.\n"
          "### The other 27 shared companies need no file: grey_usu reaches them with\n"
          "### TRY_INJECT:, which adds to a list and accumulates in a modifier block.\n"
          "### Since 2026-08-27 (GR.16) these same six records also silently drop\n"
          "### addon-LLWA's extension_building_types the same way -- restored here too,\n"
          "### see the CARRIES A VC LAYER banner above for the .off twin.\n")
    write("common/company_types/zz_gvc_companies.txt", "\n\n".join(records),
          what, why, banner=BANNER_CARRIES_VC)
    write("common/company_types/zz_gvc_companies.txt.off", "\n\n".join(off_records),
          what + " (no-VC variant)", why, banner=BANNER_OFF_TWIN)


# --------------------------------------------------------------------------
# 3 & 4. production_methods and buildings -- VC's own INJECT, re-issued
# --------------------------------------------------------------------------

def reissue_vc_injects(cat: str, expect: int, rel: str, what: str, why: str):
    vc = cat_of("VC", cat)
    records, keys = [], []
    for k in sorted(vc):
        for pref, f, body in vc[k]:
            if pref not in ("INJECT", "TRY_INJECT"):
                continue
            w = winner(cat, k)
            if not w:
                continue                      # nobody after VC touches it: nothing lost
            who, wpref, wrel, _wbody = w
            keys.append(k)
            records.append(f"# {k} -- {who} re-issues the whole record in {wrel} ({wpref}),\n"
                           f"# which drops this inject of VC's ({f}). Verbatim copy, nothing added.\n"
                           f"{pref}:{k} = {{{body}}}")
    assert len(records) == expect, \
        f"{cat}: expected {expect} lost VC injects, found {len(records)}: {keys}"
    NOTES.append(f"{cat}: {len(records)} VC injects re-issued ({', '.join(keys)})")
    write(rel, "\n\n".join(records), what, why)


def build_methods():
    reissue_vc_injects(
        "common/production_methods", 10,
        "common/production_methods/zz_gvc_methods.txt",
        "10 production methods VC injects into and grey_usu re-issues whole",
        "### grey_usu rebuilds the construction methods, the three subsistence defaults\n"
        "### and the passenger-train methods with full bodies, so VC's injects into the\n"
        "### same records are gone. These are VC's own inject bodies, copied byte for byte\n"
        "### and loaded after grey_usu: re-issuing a foreign INJECT: over a later body is\n"
        "### exact restoration, and it does not depend on how the open question about\n"
        "### sub-block semantics is answered (Правила работы с модами, Переопределение).\n")


def build_buildings():
    reissue_vc_injects(
        "common/buildings", 2,
        "common/buildings/zz_gvc_buildings.txt",
        "can_build_private on the food industry and the livestock ranch",
        "### VC gates private construction of these two behind its own\n"
        "### zw_trigger_autonom_investment; grey_food and grey_food_2_ranch re-issue both\n"
        "### buildings with REPLACE_OR_CREATE: and full bodies, so the gate disappears and\n"
        "### the two buildings behave differently from every other building VC gates.\n"
        "### VC's own TRY_INJECT:, copied verbatim.\n")


# --------------------------------------------------------------------------
# 5. pop_needs -- popneed_basic_food only
# --------------------------------------------------------------------------

def need_entries(body: str):
    """[(goods, weight, max, min)] of a pop need, order kept."""
    out = []
    txt = re.sub(r"#[^\n]*", "", body)
    for nm, a, o, c in V._depth0_iter(txt):
        if nm != "entry":
            continue
        d = dict(re.findall(r"([a-z_]+)\s*=\s*([^\s{}]+)", txt[o + 1:c]))
        out.append((d.get("goods"), d.get("weight"),
                    d.get("max_supply_share"), d.get("min_supply_share")))
    return out


def build_pop_needs():
    key = "popneed_basic_food"
    van = cat_of("VANILLA", "common/pop_needs")[key][0][2]
    vcb = cat_of("VC", "common/pop_needs")[key][0][2]
    # The assembled VC addon already merged VC's groceries weight with TGR's supply
    # shares for this record (pair VC x TGR, common/pop_needs/zz_vc_tgr_pop_needs.txt).
    # grey_food_2_ranch's body wipes that merge too, not just VC's one number, so the
    # base to restore is the addon's body -- taking VC's alone would silently throw
    # TGR's max/min supply shares away a second time.
    addon = cat_of("ADDON-VC", "common/pop_needs").get(key, [])
    assert len(addon) == 1, f"addon-VC now writes {len(addon)} bodies for {key}"
    base_src, base = f"addon-VC {addon[0][1]}", addon[0][2]
    recs = cat_of("ranch", "common/pop_needs")[key]
    full = [r for r in recs if r[0] in FULL_BODY]
    inj = [r for r in recs if r[0] in ("INJECT", "TRY_INJECT")]
    assert len(full) == 1, f"grey_food_2_ranch now writes {len(full)} full bodies for {key}"
    assert len(inj) == 2, f"grey_food_2_ranch now injects {len(inj)} entries into {key}"
    # The whole argument for this file: ranch's body is vanilla verbatim, so nothing of
    # its own is being overruled here -- a copy of vanilla is.
    assert need_entries(full[0][2]) == need_entries(van), (
        "grey_food_2_ranch's popneed_basic_food is no longer vanilla verbatim -- "
        "it now says something of its own, and then it wins on merit. Re-decide.")
    vg = dict((g, w) for g, w, _a, _b in need_entries(vcb))
    bg = dict((g, w) for g, w, _a, _b in need_entries(base))
    assert vg["groceries"] == "1.5" and bg["groceries"] == "1.5", (
        "VC's groceries weight no longer reaches the addon body -- re-check the VC addon")

    merged = base.rstrip() + "\n"
    for pref, f, b in inj:
        merged += ("\n\t# re-issued from grey_food_2_ranch %s (%s): this file writes the\n"
                   "\t# whole record, so ranch's own injected entries have to come along.\n" % (f, pref))
        merged += b.strip("\n").rstrip() + "\n"
    NOTES.append(f"pop_needs: popneed_basic_food, base {base_src} (VC's groceries 1.5 + TGR's "
                 f"supply shares), plus ranch's two injected entries")
    write("common/pop_needs/zz_gvc_pop_needs.txt",
          f"REPLACE_OR_CREATE:{key} = {{\n{merged}}}",
          "popneed_basic_food -- the VC addon's body, put back under ranch's entries",
          "### grey_food_2_ranch re-issues popneed_basic_food with a body that is vanilla\n"
          "### verbatim (checked entry by entry, and the generator asserts it), then injects\n"
          "### sugar and services into it. So what it overrules is not another design, it is\n"
          "### a copy of vanilla -- and what it overrules is not only VC's groceries weight\n"
          "### (1.15 -> 1.5) but the whole VC x TGR merge the VC addon already made for this\n"
          "### record (TGR's max_supply_share 0.3 / min_supply_share 0.2 on all five entries).\n"
          "### Base here is the VC addon's body; ranch's two injected entries are folded in,\n"
          "### because a full body would otherwise drop them.\n"
          "### The other four shared pop needs are NOT here: communication, free_movement,\n"
          "### leisure and luxury_food are a deliberate Grey's redesign (services entries and\n"
          "### min_supply_share everywhere) and win on merit; popneed_heating needs nothing\n"
          "### because VC's body there is vanilla verbatim.\n")


# --------------------------------------------------------------------------
# 6. script_values -- cultural_community_creation_weight
# --------------------------------------------------------------------------

ANCHOR = "has_state_trait = state_trait_natural_harbors"


def known_traits() -> set:
    known = set()
    for who in ["VANILLA", "VC"] + [w for w, _ in CHAIN_AFTER_VC]:
        try:
            known |= set(cat_of(who, "common/state_traits"))
        except KeyError:
            pass
    return known


def build_script_value():
    key = "cultural_community_creation_weight"
    vcb = cat_of("VC", "common/script_values")[key][0][2]
    w = winner("common/script_values", key)
    assert w, f"nobody after VC re-issues {key}"
    who, pref, rel, base = w
    assert who == "soft_pop", f"{key} is now won by {who} ({rel})"
    have = set(re.findall(r"has_state_trait\s*=\s*(\w+)", base))
    extra = [t for t in dict.fromkeys(re.findall(r"has_state_trait\s*=\s*(\w+)", vcb))
             if t not in have]
    known = known_traits()
    missing = [t for t in extra if t not in known]
    extra = [t for t in extra if t in known]
    for t in missing:
        NOTES.append(f"script_value: VC names {t}, which no mod in the chain defines "
                     f"-- left out (VC's own bug, harmless here)")
    assert extra, "VC no longer adds any port trait to the harbour list -- drop this file"
    assert base.count(ANCHOR) == 1, "the harbour OR block moved in soft_pop's body"
    line_start = base.rfind("\n", 0, base.index(ANCHOR)) + 1
    indent = re.match(r"[ \t]*", base[line_start:]).group(0)
    ins = "".join(f"{indent}has_state_trait = {t}\t# VC\n" for t in extra)
    at = base.index("\n", base.index(ANCHOR)) + 1
    merged = base[:at] + ins + base[at:]
    NOTES.append(f"script_value: {len(extra)} VC port traits added to soft_pop's "
                 f"harbour list, numbers left to soft_pop")
    write("common/script_values/zz_gvc_cultural_community_weight.txt",
          f"REPLACE_OR_CREATE:{key} = {{{merged}}}",
          "cultural_community_creation_weight -- VC's port traits",
          "### _grey_soft_pop rewrites this script value (TRY_REPLACE:, whole body:\n"
          "### building scopes instead of has_port_state, if/else_if chains instead of\n"
          "### stacked multipliers) and wins outright. Its harbour bonus still lists only\n"
          "### the six vanilla harbour traits, so every port trait VC adds counts for\n"
          "### nothing. This is soft_pop's body with VC's trait names added to that one\n"
          "### list -- and nothing else: the numbers in this script are soft_pop's redesign\n"
          "### and stay its own, the same rule the 60 state traits follow.\n"
          "### NOTE: a plain repeat of a script_value key does NOT override -- hence\n"
          "### REPLACE_OR_CREATE: here (Правила работы с модами, Переопределение).\n")


# --------------------------------------------------------------------------

def self_check() -> int:
    bad = 0
    seen: dict = {}
    for rel, blob in sorted(WRITTEN.items()):
        text = blob.decode("utf-8-sig")
        if brace_balance(text) != 0:
            print(f"  FAIL {rel}: brace balance {brace_balance(text)}")
            bad += 1
        if needs_bom(text) and not blob.startswith(b"\xef\xbb\xbf"):
            print(f"  FAIL {rel}: non-ASCII outside a comment, needs a BOM")
            bad += 1
        doubled = re.findall(r"^[A-Z_]+:[A-Z_]+:", text, re.M)
        if doubled:
            print(f"  FAIL {rel}: {len(doubled)} doubled prefix(es), e.g. {doubled[0]}")
            bad += 1
        category = os.path.dirname(rel)
        # .off twins are deliberate inert duplicates (decision #9) -- Victoria 3
        # never loads them, so they must not trip the duplicate-key check.
        if rel.endswith(".off"):
            continue
        depth = 0
        for raw in text.split("\n"):
            code = raw.split("#", 1)[0]
            if depth == 0:
                m = re.match(r"^﻿?([A-Z_]+:)?([A-Za-z0-9_.\-]+)\s*=\s*\{", code)
                if m and (m.group(1) or "").rstrip(":") in ("INJECT", "TRY_INJECT"):
                    m = None
                if m:
                    where = (category, m.group(2))
                    if where in seen:
                        print(f"  FAIL duplicate key {m.group(2)} in {category}: "
                              f"{seen[where]} and {rel}")
                        bad += 1
                    seen[where] = rel
            depth += code.count("{") - code.count("}")
    print(f"  self-check: {len(WRITTEN)} files, {len(seen)} replacing top-level keys, "
          f"{bad} problem(s)")
    return bad


def main() -> int:
    global CHECK_ONLY
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only, do not write")
    args = ap.parse_args()
    CHECK_ONLY = args.check

    print(f"regen_greys_vc.py -> {OUT}")
    for name, fn in (
        ("state_traits", build_state_traits),
        ("company_types", build_companies),
        ("production_methods", build_methods),
        ("buildings", build_buildings),
        ("pop_needs", build_pop_needs),
        ("script_values", build_script_value),
    ):
        print(f"[{name}]")
        fn()

    print("\nwhat this run decided:")
    for n in NOTES:
        print("  * " + n)
    print()
    bad = self_check()
    if args.check:
        drifted = [r for r, blob in WRITTEN.items()
                   if (open(os.path.join(OUT, r), "rb").read()
                       if os.path.isfile(os.path.join(OUT, r)) else None) != blob]
        if drifted:
            print(f"\n{len(drifted)} file(s) on disk no longer match the sources:")
            for r in drifted:
                print("  " + r)
            return 1
        print("\nall files match the current VC / Grey's sources")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
