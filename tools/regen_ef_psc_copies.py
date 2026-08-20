#!/usr/bin/env python3
"""
Regenerate the bulk copies that the E&F + PSC compatch has to carry.

Why this script exists
----------------------
The compatch unifies E&F's `building_ef_private_construction` into PSC's
`building_construction_sector`. Four places in E&F name that building in bulk
and cannot be patched surgically (no INJECT into an effect body, no INJECT into
a history BUILDINGS block that already names the type, no partial override of a
localization line):

  1. common/company_types/00_ef_companies.txt      -- company building_types
  2. common/history/buildings/00_ef_building.txt   -- campaign start buildings
  3. establish_bank_and_ef_compagnie               -- 9k-line scripted_effect
  4. localization/*/01_ef_je_localization_*        -- strings naming the building

So the compatch ships whole-file / whole-key copies with the building name
substituted. Hand-maintaining them rots fast: between E&F v4.1.1 and the
04.07.2026 build the history file grew 2624 -> 4221 lines and the effect
3713 -> 9659 lines, and the stale copies silently deleted 24 add_company and
83 create_building entries. Run this after every E&F update instead of editing
by hand.

THE HOTFIX IS THE SOURCE OF TRUTH, NOT E&F
------------------------------------------
Load order is: E&F -> E&F hotfix -> compatch. Both the hotfix and the compatch
override files by path, and the compatch loads last, so whatever the compatch
copies is what the game ends up using. If the compatch copied plain E&F for a
file the hotfix also overrides, the compatch would silently undo the hotfix.

`pick_source()` therefore looks in the hotfix first and falls back to E&F, and
the run prints which one it used for every file. Today that matters for
00_ef_building.txt (the hotfix fixes STATE_LOWER_ANDALUSIA and a GRE block that
built in a NULL state); if the hotfix ever starts overriding 00_ef_companies.txt
as well, this picks it up on its own.

The same check runs the other way: --check reports any E&F file the hotfix
overrides that this script does NOT copy, so a new hotfix override cannot
quietly fall out of the compatch's view.

Localization is emitted as a small `zz_` overlay instead of a same-path copy.
The old build shipped the whole 01_ef_je_localization file per language, which
dropped 73 keys E&F had added since (fc_fso_situation, the crisis counters, the
new widget strings) and, in Russian, shadowed the dedicated E&F RU mod with a
stale partial translation. Now only the ~15 lines that actually name the
building are re-emitted -- taken from the RU translation mod for Russian so the
overlay does not knock those strings back to English.

Usage:
    python3 regen_ef_psc_copies.py                 # uses the default layout
    python3 regen_ef_psc_copies.py --check         # report drift, write nothing
"""

from __future__ import annotations

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

# Files copied wholesale, relative to a mod root. Order is cosmetic.
WHOLE_FILE_JOBS = [
    "common/company_types/00_ef_companies.txt",
    "common/history/buildings/00_ef_building.txt",
]

# Single key lifted out of a much bigger E&F file.
KEY_JOB = (
    "common/scripted_effects/01_financial_scripted_effects.txt",   # source
    "establish_bank_and_ef_compagnie",                             # key
    "common/scripted_effects/zz_financial_scripted_effects.txt",   # destination
)

# Hand-authored in localization/*/zz_pb_ef_psc_l_*.yml -- never regenerate these.
MANUAL_LOC_KEYS = {
    "concept_building_urban_center_lvl_by_base_rate_desc",
    "concept_maximum_pcs_capacity_desc",
    "speculative_share_9_button_tt_2",
    "speculative_share_10_button_tt_2",
    "speculative_share_11_button_tt_2",
    "speculative_share_12_button_tt_2",
}

LOC_KEY_RE = re.compile(r'^\s*([^\s:#][^:#]*?)\s*:\s*[0-9]*\s*"')

BANNER = (
    "# GENERATED FILE -- do not edit by hand.\n"
    "# Rebuilt by tools/regen_ef_psc_copies.py from {origin}: {src}\n"
    "# with {old} -> {new}.\n"
    "# Re-run that script after every E&F update.\n"
)

HISTORY_NOTE = (
    "#\n"
    "# LOAD ORDER MATTERS: this path exists in E&F, in the E&F hotfix and here.\n"
    "# Order is E&F -> hotfix -> compatch, so this copy is the one the game uses,\n"
    "# and it is generated FROM the hotfix's version -- it already carries the\n"
    "# hotfix's two fixes (STATE_LOWER_ANDALUSIA, and the GRE block that built in\n"
    "# a NULL state). If the compatch ever ends up loading before the hotfix, the\n"
    "# rename below is undone and E&F starts creating the disabled\n"
    "# building_ef_private_construction again, silently.\n"
    "#\n"
    "# Quick check in game: the error at financial_center_modifier should report\n"
    "# this file at the line number of THIS copy, not the hotfix's.\n"
)

EXTRA_NOTES = {"common/history/buildings/00_ef_building.txt": HISTORY_NOTE}

LOC_BANNER = (
    "# GENERATED FILE -- do not edit by hand.\n"
    "# Rebuilt by tools/regen_ef_psc_copies.py from {origin}: {src}\n"
    "# keeping only the lines that name {old}, renamed to {new}.\n"
    "# Hand-written strings live in zz_pb_ef_psc_l_{lang}.yml and are skipped here.\n"
    "# ScriptValue('{old}_lvl') is left alone on purpose: that key name stays,\n"
    "# the compatch remaps its value to sum {new} instead.\n"
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


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    here = Path(__file__).resolve().parent            # .../vic3_mods/tools
    repo = here.parent                                 # .../vic3_mods
    ap.add_argument("--ef", default=str(repo.parent / "vic3_mods_out" / "E&F"))
    ap.add_argument("--hotfix", default=str(repo / "_ef" / "ef hotfix 1.13"))
    ap.add_argument("--out", default=str(repo / "_ef" / "ef+psc done"))
    ap.add_argument(
        "--ru-loc",
        default=str(repo / "__translations" / "Economic and Financial Mod (E&F) - V4 RUS"),
        help="E&F Russian translation mod; source for l_russian so the overlay "
             "keeps Russian instead of reverting to E&F's English",
    )
    ap.add_argument("--check", action="store_true", help="report drift, write nothing")
    a = ap.parse_args()

    ef, hotfix, out, ru_loc = Path(a.ef), Path(a.hotfix), Path(a.out), Path(a.ru_loc)
    for p, label in ((ef, "--ef"), (hotfix, "--hotfix"), (out, "--out")):
        if not p.is_dir():
            print(f"ERROR: {label} is not a directory: {p}", file=sys.stderr)
            return 2

    def pick_source(rel: str) -> tuple[Path, str]:
        """Hotfix wins over E&F -- it loads later, so its version is the live one."""
        cand = hotfix / rel
        if cand.is_file():
            return cand, "hotfix"
        return ef / rel, "E&F"

    rc = 0

    # --- guard: hotfix overrides we are not tracking ------------------------
    tracked = set(WHOLE_FILE_JOBS) | {KEY_JOB[0]}
    hotfix_overrides = []
    for p in sorted(hotfix.rglob("*.txt")):
        rel = p.relative_to(hotfix).as_posix()
        if (ef / rel).is_file():
            hotfix_overrides.append(rel)
    print("Hotfix overrides these E&F files:")
    for rel in hotfix_overrides:
        mark = "copied here" if rel in tracked else "not copied by the compatch"
        print(f"  {rel:<52} {mark}")
    print()

    # --- build the job list -------------------------------------------------
    jobs = []   # (relpath_out, src, body, is_loc)

    for rel in WHOLE_FILE_JOBS:
        src, origin = pick_source(rel)
        jobs.append((rel, src, origin, read(src), False))

    src_rel, key, dst_rel = KEY_JOB
    src, origin = pick_source(src_rel)
    block = extract_block(read(src), key)
    block = "REPLACE_OR_CREATE:" + block.lstrip("﻿").lstrip()
    jobs.append((dst_rel, src, origin, block, False))

    for lang_dir in sorted(p for p in (ef / "localization").iterdir() if p.is_dir()):
        lang = lang_dir.name
        name = f"01_ef_je_localization_l_{lang}.yml"
        rel = f"localization/{lang}/{name}"
        src, origin = pick_source(rel)
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
        jobs.append((f"localization/{lang}/zz_pb_ef_psc_je_l_{lang}.yml", src, origin, text, True))

    # --- emit ---------------------------------------------------------------
    for rel, src, origin, body, is_loc in jobs:
        if is_loc:
            text, n, bal = body, body.count(NEW_NAME), 0
        else:
            body, n = BUILDING_RE.subn(NEW_NAME, body)
            banner = BANNER.format(origin=origin, src=src.name, old=OLD_NAME, new=NEW_NAME)
            text = banner + EXTRA_NOTES.get(rel, "") + "\n" + body
            if not text.endswith("\n"):
                text += "\n"
            bal = balance(text)

        dst = out / rel
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
        if not a.check and changed:
            write_bom(dst, text)
            print(f"        written : {dst}")

    if a.check:
        print("\n--check: nothing written.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
