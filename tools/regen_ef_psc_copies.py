#!/usr/bin/env python3
"""
Regenerate the E&F files the E&F hotfix carries with PSC's construction sector.

Why this script exists
----------------------
Since 2026-10-02 (СТР.6) the E&F x PSC compatch lives inside the E&F hotfix
("E&F: Rebalance", depends on PSC). It unifies E&F's
`building_ef_private_construction` into PSC's `building_construction_sector`.
Four places in E&F name that building in bulk and cannot be patched surgically
(no INJECT into an effect body, no INJECT into a history BUILDINGS block that
already names the type, no partial override of a localization line):

  1. common/company_types/00_ef_companies.txt      -- company building_types
  2. common/history/buildings/00_ef_building.txt   -- campaign start buildings
  3. establish_bank_and_ef_compagnie               -- 9k-line scripted_effect
  4. localization/*/01_ef_je_localization_*        -- strings naming the building

Hand-maintaining them rots fast: between E&F v4.1.1 and the 04.07.2026 build
the history file grew 2624 -> 4221 lines and the effect 3713 -> 9659 lines, and
stale copies silently deleted 24 add_company and 83 create_building entries.
Run this after every E&F update instead of editing by hand.

Two kinds of job
----------------
COPY_JOBS / KEY_JOB / localization: E&F (or the RU translation mod) is the
source, the hotfix gets a generated copy with the rename. Never edit those
copies by hand -- the next run overwrites them. A hotfix file at a COPY_JOBS
path WITHOUT our banner is a hand override and stops the run.

IN_PLACE_JOBS: the hotfix already overrides that E&F file by hand
(00_ef_building.txt: STATE_LOWER_ANDALUSIA, the GRE block that built in a NULL
state, the companies pulled up before the central banks). That file IS the
source; the rename is applied inside it and a short note is kept at the top,
so the hand edits are never overwritten. After an E&F update re-merge E&F's
new file into it by hand first, then run this. The run prints E&F's and the
hotfix's line counts as a drift hint.

Order inside one mod
--------------------
Inside one mod files load by name (byte order). The hotfix INJECT:s into the
98 bank companies of 00_ef_companies.txt from zz_ef_cm_companies.txt -- that
works only because zz_ sorts after 00_. --check fails if any other hotfix file
in a generated file's folder touches one of its keys from a file that sorts
BEFORE it (an INJECT would be eaten by our full body), or redefines one with a
full body from a file that sorts AFTER it (our version would be overridden).

Localization is emitted as a small `zz_` overlay in localization/<lang>/replace/
instead of a same-path copy (a plain zz_ file next to E&F's never wins -- the
first file to define a key does). Only the ~15 lines that name the building
are re-emitted -- taken from the RU translation mod for Russian so the overlay
does not knock those strings back to English.

Usage:
    python3 regen_ef_psc_copies.py                 # uses the default layout
    python3 regen_ef_psc_copies.py --check         # report drift, write nothing
"""

import argparse
import re
import sys
from pathlib import Path

# `building_ef_private_construction` but never `bg_ef_private_construction`,
# and never a longer identifier such as `building_ef_private_construction_lvl`
# (that one is a script_value, remapped separately in zz_pb_ef_remap_pcs_values.txt).
BUILDING_RE = re.compile(r"\bbuilding_ef_private_construction\b(?![A-Za-z0-9_])")
OLD_NAME = "building_ef_private_construction"
NEW_NAME = "building_construction_sector"

# E&F files copied wholesale into the hotfix, with the rename. Order is cosmetic.
COPY_JOBS = [
    "common/company_types/00_ef_companies.txt",
]

# Hotfix files that override an E&F file by hand: the rename is applied inside
# them, nothing is copied over them.
IN_PLACE_JOBS = [
    "common/history/buildings/00_ef_building.txt",
]

# Single key lifted out of a much bigger E&F file.
KEY_JOB = (
    "common/scripted_effects/01_financial_scripted_effects.txt",   # source
    "establish_bank_and_ef_compagnie",                             # key
    "common/scripted_effects/zz_financial_scripted_effects.txt",   # destination
)

# Hand-authored in localization/*/replace/zz_pb_ef_psc_l_*.yml -- never regenerate these.
MANUAL_LOC_KEYS = {
    # EF.18 v2 (2026-09-24): E&F's text describes the old mechanics
    # (x (1 - rate x 10), +1 a month, the bubble cutting construction).
    "financial_center_je_2_reason",
    "financial_center_je_2_reason_2",
    "concept_building_urban_center_lvl_by_base_rate_desc",
    "concept_maximum_pcs_capacity_desc",
    "speculative_share_9_button_tt_2",
    "speculative_share_10_button_tt_2",
    "speculative_share_11_button_tt_2",
    "speculative_share_12_button_tt_2",
    # 2026-09-25: stimulus buttons 9-12 reworked -- no sectors built any more.
    "speculative_share_9_button_desc",
    "speculative_share_10_button_desc",
    "speculative_share_11_button_desc",
    "speculative_share_12_button_desc",
    "speculative_share_9_button_tt_effect_1_1",
    "speculative_share_10_button_tt_effect_1_1",
    "speculative_share_11_button_tt_effect_1_1",
    "speculative_share_12_button_tt_effect_1_1",
}

LOC_KEY_RE = re.compile(r'^\s*([^\s:#][^:#]*?)\s*:\s*[0-9]*\s*"')

BANNER_MARK = "# GENERATED FILE -- do not edit by hand."
BANNER = (
    BANNER_MARK + "\n"
    "# Rebuilt by tools/regen_ef_psc_copies.py from {origin}: {src}\n"
    "# with {old} -> {new}.\n"
    "# Re-run that script after every E&F update.\n"
)

IN_PLACE_MARK = "# PSC RENAME APPLIED IN PLACE"
IN_PLACE_NOTE = (
    IN_PLACE_MARK + " by tools/regen_ef_psc_copies.py:\n"
    "# {old} -> {new} ({n} occurrence(s)).\n"
    "# This is the hotfix's own, hand-maintained override of E&F's {name}\n"
    "# (STATE_LOWER_ANDALUSIA, the GRE block that built in a NULL state, the\n"
    "# companies pulled up before the central banks). Edit it by hand; after an\n"
    "# E&F update re-merge E&F's file first, then re-run the script.\n"
)

LOC_BANNER = (
    "# GENERATED FILE -- do not edit by hand.\n"
    "# Rebuilt by tools/regen_ef_psc_copies.py from {origin}: {src}\n"
    "# keeping only the lines that name {old}, renamed to {new}.\n"
    "# Hand-written strings live in zz_pb_ef_psc_l_{lang}.yml and are skipped here.\n"
    "# ScriptValue('{old}_lvl') is left alone on purpose: that key name stays,\n"
    "# the hotfix remaps its value to sum {new} instead.\n"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore")


def write_bom(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8-sig", newline="\n")


def balance(text: str) -> int:
    """Brace balance ignoring line comments. Must be 0."""
    depth = 0
    for raw in text.split("\n"):
        line = raw.split("#", 1)[0]
        depth += line.count("{") - line.count("}")
    return depth


TOP_KEY_RE = re.compile(r"^\s*([A-Za-z0-9_.\-:]+)\s*=\s*\{")

# Keys that ADD rather than override when several files declare them.
# history/buildings and history/global stack their blocks; on_actions root hooks
# (on_*) stack too.
ADDITIVE_KEYS = {"BUILDINGS", "GLOBAL", "POPS", "STATES", "COUNTRIES", "CHARACTERS"}


def top_level_prefixed(text: str) -> list[tuple[str, str]]:
    """Top-level `[PREFIX:]key = {` as (key, prefix); prefix '' for a bare body."""
    depth = 0
    out: list[tuple[str, str]] = []
    for raw in text.split("\n"):
        line = raw.split("#", 1)[0]
        if depth == 0:
            m = TOP_KEY_RE.match(line)
            if m:
                prefix, _, key = m.group(1).rpartition(":")
                out.append((key, prefix))
        depth += line.count("{") - line.count("}")
    return out


def extract_block(text: str, key: str) -> str:
    """Pull one top-level `key = { ... }` block out of a Vic3 script file."""
    key_re = re.compile(r"^\s*([A-Za-z0-9_.\-:]+)\s*=")
    depth = 0
    buf: list[str] | None = None
    for raw in text.split("\n"):
        line = raw.split("#", 1)[0]
        if depth == 0:
            m = key_re.match(line)
            if m and m.group(1).split(":")[-1] == key:
                buf = []
        if buf is not None:
            buf.append(raw)
        prev = depth
        depth += line.count("{") - line.count("}")
        if buf is not None and depth == 0 and prev > 0:
            return "\n".join(buf)
    raise KeyError(f"top-level key {key!r} not found")


# СТР.5 (2026-10-02, decided by the user): E&F's ~100 bank companies list
# railways, trade centres, mines and construction in building_types, so there is
# a bank company for almost any building and banks took ~30% of all company
# construction (run 1836.7 -> 1841.1: +2011 levels). Banks keep only banking:
# the bank (the hotfix INJECTs building_bank in zz_ef_cm_companies.txt), the
# national exchanges, the financial district. Everything else in their
# building_types is commented out, marked `### СТР.5`. Start buildings E&F's
# history gives them stay theirs -- only new investment follows building_types.
# Bank companies = the keys zz_ef_cm_companies.txt INJECTs into.
BANK_TYPES_FILE = "common/company_types/00_ef_companies.txt"
BANK_KEEP_RE = re.compile(r"^building_(bank|financial_centre\w*|financial_district)$")


def bank_companies(hotfix: Path) -> set[str]:
    return set(re.findall(r"(?m)^INJECT:(\w+)\s*=",
                          read(hotfix / "common/company_types/zz_ef_cm_companies.txt")))


def trim_bank_building_types(body: str, banks: set[str]) -> tuple[str, int]:
    out, cut = [], 0
    depth, company, in_types, types_depth = 0, None, False, 0
    for raw in body.split("\n"):
        line = raw.split("#", 1)[0]
        if depth == 0:
            m = TOP_KEY_RE.match(line)
            company = m.group(1).split(":")[-1] if m else None
        if company in banks and depth == 1 and re.match(r"^\s*building_types\s*=\s*\{", line):
            in_types, types_depth = True, depth + 1
        elif in_types and depth == types_depth:
            tok = line.strip()
            if tok and tok != "}" and not BANK_KEEP_RE.match(tok):
                indent = raw[:len(raw) - len(raw.lstrip())]
                raw = f"{indent}#{raw.lstrip()} ### СТР.5: banks keep only banking"
                line = ""
                cut += 1
        depth += line.count("{") - line.count("}")
        if in_types and depth < types_depth:
            in_types = False
        out.append(raw)
    return "\n".join(out), cut


def strip_note(text: str) -> str:
    """Drop our own header (generated banner or in-place note) from the top."""
    text = text.lstrip("﻿")
    lines = text.split("\n")
    if not (lines[0].startswith(BANNER_MARK) or lines[0].startswith(IN_PLACE_MARK)):
        return text
    i = 0
    while i < len(lines) and (lines[i].startswith("#") or not lines[i].strip()):
        i += 1
    return "\n".join(lines[i:])


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    here = Path(__file__).resolve().parent            # .../vic3_mods/tools
    repo = here.parent                                 # .../vic3_mods
    ap.add_argument("--ef", default=str(repo.parent / "vic3_mods_out" / "E&F"))
    ap.add_argument("--hotfix", default=str(repo / "_ef" / "ef hotfix 1.13"))
    ap.add_argument(
        "--ru-loc",
        default=str(repo / "__translations" / "Economic and Financial Mod (E&F) - V4 RUS"),
        help="E&F Russian translation mod; source for l_russian so the overlay "
             "keeps Russian instead of reverting to E&F's English",
    )
    ap.add_argument("--check", action="store_true", help="report drift, write nothing")
    a = ap.parse_args()

    ef, hotfix, ru_loc = Path(a.ef), Path(a.hotfix), Path(a.ru_loc)
    for p, label in ((ef, "--ef"), (hotfix, "--hotfix")):
        if not p.is_dir():
            print(f"ERROR: {label} is not a directory: {p}", file=sys.stderr)
            return 2

    rc = 0

    # --- hotfix files at E&F's paths, for the record -------------------------
    generated = set(COPY_JOBS)
    print("Hotfix files at E&F's paths:")
    for p in sorted(hotfix.rglob("*.txt")):
        rel = p.relative_to(hotfix).as_posix()
        if not (ef / rel).is_file():
            continue
        if rel in generated:
            mark = "generated here from E&F"
        elif rel in IN_PLACE_JOBS:
            mark = "hand override, rename applied in place"
        else:
            mark = "hand override, not touched by this script"
        print(f"  {rel:<52} {mark}")
    print()

    # --- build the job list -------------------------------------------------
    jobs = []   # (relpath, src, origin, text, renamed, is_loc)

    for rel in COPY_JOBS:
        src, dst = ef / rel, hotfix / rel
        if dst.is_file() and not read(dst).startswith(BANNER_MARK):
            print(f"ERROR: {rel} in the hotfix has no generated banner -- it is a "
                  f"hand override and would be overwritten", file=sys.stderr)
            rc = 1
            continue
        body, n = BUILDING_RE.subn(NEW_NAME, read(src))
        if rel == BANK_TYPES_FILE:
            body, cut = trim_bank_building_types(body, bank_companies(hotfix))
            print(f"[banks] {rel}: {cut} building_types line(s) commented out (СТР.5)")
        text = BANNER.format(origin="E&F", src=src.name, old=OLD_NAME, new=NEW_NAME) + "\n" + body
        jobs.append((rel, src, "E&F", text, n, False))

    for rel in IN_PLACE_JOBS:
        src = hotfix / rel
        if not src.is_file():
            print(f"ERROR: in-place job missing from the hotfix: {rel}", file=sys.stderr)
            rc = 1
            continue
        body = strip_note(read(src))
        body = BUILDING_RE.sub(NEW_NAME, body)
        n = body.count(NEW_NAME)
        text = IN_PLACE_NOTE.format(old=OLD_NAME, new=NEW_NAME, n=n, name=src.name) + "\n" + body
        ef_lines = read(ef / rel).count("\n") if (ef / rel).is_file() else 0
        print(f"[drift hint] {rel}: E&F {ef_lines} lines, hotfix {body.count(chr(10))} lines")
        jobs.append((rel, src, "hotfix (in place)", text, n, False))

    src_rel, key, dst_rel = KEY_JOB
    src = ef / src_rel
    block = extract_block(read(src), key)
    block = "REPLACE_OR_CREATE:" + block.lstrip("﻿").lstrip()
    block, n = BUILDING_RE.subn(NEW_NAME, block)
    text = BANNER.format(origin="E&F", src=src.name, old=OLD_NAME, new=NEW_NAME) + "\n" + block
    jobs.append((dst_rel, src, "E&F", text, n, False))

    for lang_dir in sorted(p for p in (ef / "localization").iterdir() if p.is_dir()):
        lang = lang_dir.name
        name = f"01_ef_je_localization_l_{lang}.yml"
        rel = f"localization/{lang}/{name}"
        src, origin = ef / rel, "E&F"
        if lang == "russian" and (ru_loc / rel).is_file():
            src, origin = ru_loc / rel, "RU translation mod"
        if not src.is_file():
            continue
        kept = []
        for line in read(src).split("\n"):
            if not BUILDING_RE.search(line):
                continue
            m = LOC_KEY_RE.match(line)
            if m and m.group(1) in MANUAL_LOC_KEYS:
                continue
            kept.append(BUILDING_RE.sub(NEW_NAME, line).rstrip())
        if not kept:
            continue
        text = (
            LOC_BANNER.format(origin=origin, src=src.name, old=OLD_NAME, new=NEW_NAME, lang=lang)
            + f"\nl_{lang}:\n"
            + "\n".join(kept)
            + "\n"
        )
        # replace/: localization is first-come, the first file to define a key
        # wins whatever the mod order, and E&F / the RU mod define these first.
        # Keys under localization/<lang>/replace/ override (as Morgenroete does
        # on vanilla).
        jobs.append((f"localization/{lang}/replace/zz_pb_ef_psc_je_l_{lang}.yml",
                     src, origin, text, text.count(NEW_NAME), True))

    # --- guard: order of the generated files inside the hotfix ---------------
    # Inside one mod files load by name. Another hotfix file touching a key of a
    # generated file must INJECT, from a name that sorts AFTER it; a full body
    # (bare / REPLACE*) from any other file is a fight over the key.
    print("Hotfix keys touching a generated file:")
    any_hit = False
    for rel, _src, _origin, text, _n, is_loc in jobs:
        if is_loc or rel.startswith("common/history/"):
            continue
        ours = {k for k, _ in top_level_prefixed(text)}
        folder, fname = rel.rsplit("/", 1)
        for p in sorted((hotfix / folder).glob("*.txt")):
            if p.name == fname:
                continue
            for k, prefix in top_level_prefixed(read(p)):
                if k not in ours or k in ADDITIVE_KEYS or k.startswith("on_"):
                    continue
                any_hit = True
                ok = prefix in ("INJECT", "TRY_INJECT") and p.name > fname
                if ok:
                    continue
                print(f"  {p.name} {prefix or 'bare'}:{k} -> {fname}: WRONG ORDER")
                print(f"ERROR: {folder}/{p.name} touches {k} of the generated {fname} "
                      f"and loads {'after' if p.name > fname else 'before'} it with "
                      f"{prefix or 'a bare body'}", file=sys.stderr)
                rc = 1
    print("  all INJECTs load after the generated files" if any_hit else "  none")
    print()

    # --- emit ---------------------------------------------------------------
    for rel, src, origin, text, n, is_loc in jobs:
        if not text.endswith("\n"):
            text += "\n"
        bal = 0 if is_loc else balance(text)

        dst = hotfix / rel
        old = read(dst) if dst.exists() else ""
        changed = old != text

        print(f"[{'OK ' if bal == 0 else 'BAD'}] {rel}")
        print(f"        source  : {origin} -- {src}")
        print(f"        renamed : {n} occurrence(s)")
        print(f"        lines   : {old.count(chr(10))} -> {text.count(chr(10))}")
        print(f"        braces  : {bal:+d} (must be 0)")
        print(f"        changed : {'yes' if changed else 'no'}")

        if bal != 0:
            print("        REFUSING TO WRITE: unbalanced braces", file=sys.stderr)
            rc = 1
            continue
        if n == 0:
            print(f"        WARNING: nothing renamed -- did E&F drop {OLD_NAME}?", file=sys.stderr)
        if changed and a.check:
            rc = 1
        if not a.check and changed:
            write_bom(dst, text)
            print(f"        written : {dst}")

    if a.check:
        print("\n--check: nothing written." + (" DRIFT FOUND." if rc else ""))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
