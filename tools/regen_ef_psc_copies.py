#!/usr/bin/env python3
"""
Regenerate the three bulk copies that the E&F + PSC compatch has to carry.

Why this script exists
----------------------
The compatch unifies E&F's `building_ef_private_construction` into PSC's
`building_construction_sector`. Three places in E&F create/reference that
building in bulk and cannot be patched surgically (no INJECT into an effect
body, no INJECT into a history BUILDINGS block that already names the type):

  1. common/company_types/00_ef_companies.txt      -- company building_types
  2. common/history/buildings/00_ef_building.txt   -- campaign start buildings
  3. establish_bank_and_ef_compagnie               -- 9k-line scripted_effect
  4. localization/*/01_ef_je_localization_*        -- strings naming the building

So the compatch ships whole-file / whole-key copies with the building name
substituted. Hand-maintaining them rots fast: between E&F v4.1.1 and the
04.07.2026 build the history file grew 2624 -> 4221 lines and the effect
3713 -> 9659 lines, and the stale copies silently deleted 24 add_company
and 83 create_building entries.

Run this after every E&F update instead of editing by hand.

Localization is emitted as a small `zz_` overlay instead of a same-path copy.
The old build shipped the whole 01_ef_je_localization file per language, which
dropped 73 keys E&F had added since (fc_fso_situation, the crisis counters, the
new widget strings) and, in Russian, shadowed the dedicated E&F RU mod with a
stale partial translation. Now only the ~15 lines that actually name the
building are re-emitted -- taken from the RU translation mod for Russian so the
overlay does not knock those strings back to English.

Source of truth for the history file is the E&F hotfix, NOT E&F itself:
`ef hotfix 1.13` ships the same relative path with two fixes on top
(STATE_ANDALUSIA -> STATE_LOWER_ANDALUSIA, and a GRE block that created
buildings in a NULL state). If the compatch copied plain E&F, whichever of
the two mods loaded last would win and undo the other.

Usage:
    python3 regen_ef_psc_copies.py                 # uses default layout
    python3 regen_ef_psc_copies.py --check         # report drift, write nothing
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# `building_ef_private_construction` but never `bg_ef_private_construction`,
# and never a longer identifier such as `building_ef_private_construction_lvl`
# (those are script_values, remapped separately in zz_pb_ef_remap_pcs_values.txt).
BUILDING_RE = re.compile(r"\bbuilding_ef_private_construction\b(?![A-Za-z0-9_])")
OLD_NAME = "building_ef_private_construction"
NEW_NAME = "building_construction_sector"

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

LOC_BANNER = (
    "# GENERATED FILE -- do not edit by hand.\n"
    "# Rebuilt by tools/regen_ef_psc_copies.py from {src}\n"
    "# keeping only the lines that name {old}, renamed to {new}.\n"
    "# Hand-written strings live in zz_pb_ef_psc_l_{lang}.yml and are skipped here.\n"
    "# ScriptValue('{old}_lvl') is left alone on purpose: that key name stays,\n"
    "# the compatch remaps its value to sum {new} instead.\n"
)

BANNER = (
    "# GENERATED FILE -- do not edit by hand.\n"
    "# Rebuilt by tools/regen_ef_psc_copies.py from {src}\n"
    "# with {old} -> {new}.\n"
    "# Re-run that script after every E&F update.\n"
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
    lines = text.split("\n")
    depth = 0
    buf: list[str] | None = None
    for raw in lines:
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


def substitute(text: str) -> tuple[str, int]:
    out, n = BUILDING_RE.subn(NEW_NAME, text)
    return out, n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    here = Path(__file__).resolve().parent            # .../vic3_mods/tools
    repo = here.parent                                 # .../vic3_mods
    ap.add_argument("--ef", default=str(repo.parent / "vic3_mods_out" / "E&F"))
    ap.add_argument("--hotfix", default=str(repo / "_ef" / "ef hotfix 1.13"))
    ap.add_argument("--out", default=str(repo / "_ef" / "ef+psc done"))
    ap.add_argument("--ru-loc", default=str(repo / "__translations" / "Economic and Financial Mod (E&F) - V4 RUS"),
                    help="E&F Russian translation mod; used as the source for l_russian "
                         "so the overlay keeps Russian instead of reverting to E&F's English")
    ap.add_argument("--check", action="store_true", help="report drift, write nothing")
    a = ap.parse_args()

    ef, hotfix, out = Path(a.ef), Path(a.hotfix), Path(a.out)
    for p, label in ((ef, "--ef"), (hotfix, "--hotfix"), (out, "--out")):
        if not p.is_dir():
            print(f"ERROR: {label} not a directory: {p}", file=sys.stderr)
            return 2

    jobs = []

    # 1) company_types -- whole file from E&F
    src = ef / "common/company_types/00_ef_companies.txt"
    jobs.append(("common/company_types/00_ef_companies.txt", src, read(src)))

    # 2) history/buildings -- whole file from the HOTFIX, see module docstring
    src = hotfix / "common/history/buildings/00_ef_building.txt"
    note = (
        "#\n"
        "# LOAD ORDER MATTERS: this path collides with both E&F and the E&F hotfix.\n"
        "# The compatch MUST load after the hotfix. It already contains the hotfix's\n"
        "# two fixes (STATE_LOWER_ANDALUSIA, and the GRE block that built in a NULL\n"
        "# state), so loading last loses nothing -- but if the hotfix ends up after\n"
        "# the compatch, the rename below is undone and E&F starts creating the\n"
        "# disabled building_ef_private_construction again, silently.\n"
    )
    jobs.append(("common/history/buildings/00_ef_building.txt", src, read(src), False, note))

    # 3) establish_bank_and_ef_compagnie -- single key, re-emitted as REPLACE_OR_CREATE
    src = ef / "common/scripted_effects/01_financial_scripted_effects.txt"
    block = extract_block(read(src), "establish_bank_and_ef_compagnie")
    block = "REPLACE_OR_CREATE:" + block.lstrip("﻿").lstrip()
    jobs.append(("common/scripted_effects/zz_financial_scripted_effects.txt", src, block))

    # 4) localization overlay -- one small zz_ file per language
    ru_loc = Path(a.ru_loc)
    loc_dir = ef / "localization"
    for lang_dir in sorted(p for p in loc_dir.iterdir() if p.is_dir()):
        lang = lang_dir.name
        name = f"01_ef_je_localization_l_{lang}.yml"
        src = lang_dir / name
        if lang == "russian":
            ru_src = ru_loc / "localization" / "russian" / name
            if ru_src.is_file():
                src = ru_src
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
        text = (LOC_BANNER.format(src=src.name, old=OLD_NAME, new=NEW_NAME, lang=lang)
                + f"\nl_{lang}:\n" + "\n".join(kept) + "\n")
        jobs.append((f"localization/{lang}/zz_pb_ef_psc_je_l_{lang}.yml", src, text, True))

    rc = 0
    for job in jobs:
        rel, src, body = job[0], job[1], job[2]
        is_loc = len(job) > 3 and job[3] is True
        extra_note = job[4] if len(job) > 4 else ""
        if is_loc:
            text, n = body, body.count(NEW_NAME)
            bal = 0
        else:
            body, n = substitute(body)
            banner = BANNER.format(src=src.name, old=OLD_NAME, new=NEW_NAME) + extra_note
            text = banner + "\n" + body
            if not text.endswith("\n"):
                text += "\n"
            bal = balance(text)
        dst = out / rel
        old = read(dst) if dst.exists() else ""
        changed = old != text

        status = "OK " if bal == 0 else "BAD"
        print(f"[{status}] {rel}")
        print(f"        source     : {src}")
        print(f"        renamed    : {n} occurrence(s) of {OLD_NAME}")
        print(f"        lines      : {old.count(chr(10))} -> {text.count(chr(10))}")
        print(f"        braces     : {bal:+d} (must be 0)")
        print(f"        changed    : {'yes' if changed else 'no'}")

        if bal != 0:
            print(f"        REFUSING TO WRITE: unbalanced braces", file=sys.stderr)
            rc = 1
            continue
        if n == 0:
            print(f"        WARNING: nothing renamed -- did E&F drop {OLD_NAME}?", file=sys.stderr)
        if not a.check and changed:
            write_bom(dst, text)
            print(f"        written    : {dst}")

    if a.check:
        print("\n--check: nothing written.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
