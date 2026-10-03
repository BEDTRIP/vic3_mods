#!/usr/bin/env python3
"""
В1.3 (3.10.2026, decided by the user): buildings E&F creates by script start
with an empty cash register instead of a full one.

E&F's create_building calls carry `reserves = 1` -- the new building is born
with 100% of its maximum cash, money from nowhere. Run e0_2: 1 January 1837
Britain's Manchester Stock Exchange (level 5) appears with 2 000 000, 1841 the
Hong Kong Stock Exchange with 750 000 -- the yearly "business cash jump" of
block В. The user chose `reserves = 0`: the building fills its register from
its own revenue.

Covered:
  - this script: every top-level scripted effect of E&F's
    09_introduction_building_lvl.txt that has `reserves = 1` and that the
    hotfix does not already override (the exchanges: macro_facilities_fc_*,
    initialize_historic_macro_facilities_fc, financial_center_respawn_after_crisis)
    -> common/scripted_effects/zz_ef_create_building_no_cash.txt, each as
    REPLACE_OR_CREATE: with `reserves = 0`;
  - establish_bank_and_ef_compagnie (01_financial_scripted_effects.txt) --
    tools/regen_ef_psc_copies.py applies the same substitution;
  - the central banks (zz_ef_cm_bank_ownership.txt, hand-maintained) -- by hand.
Not covered on purpose: common/history/buildings (campaign start capital).

A plain repeated key does not override a scripted effect -- REPLACE_OR_CREATE:
is required (Правила работы с модами, «Ключ без префикса»).

Usage:
    python3 tools/regen_ef_create_building_no_cash.py           # write
    python3 tools/regen_ef_create_building_no_cash.py --check   # report, write nothing
"""

import argparse
import re
import sys
from pathlib import Path

SRC_REL = "common/scripted_effects/09_introduction_building_lvl.txt"
DST_REL = "common/scripted_effects/zz_ef_create_building_no_cash.txt"
RESERVES_RE = re.compile(r"(\breserves\s*=\s*)1\b")
KEY_RE = re.compile(r"^\s*(?:(REPLACE_OR_CREATE|REPLACE|TRY_REPLACE|INJECT|TRY_INJECT):)?([A-Za-z_][\w.]*)\s*=\s*\{")

BANNER = (
    "# GENERATED FILE -- do not edit by hand.\n"
    "# Rebuilt by tools/regen_ef_create_building_no_cash.py from E&F: {src}\n"
    "# (В1.3, 3.10.2026): every effect with create_building ... reserves = 1 that the\n"
    "# hotfix does not override elsewhere, with reserves = 0 -- E&F's buildings\n"
    "# created by script start with an empty cash register, not a full one from\n"
    "# nowhere. {n} effect(s), {sites} site(s). Re-run after every E&F update.\n"
)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8-sig", errors="replace").replace("\r\n", "\n")


def top_blocks(text: str):
    """(prefix, key, block text) for every top-level `key = { ... }`."""
    out, depth, start, key, prefix, pos = [], 0, None, None, None, 0
    for ln in text.split("\n"):
        code = ln.split("#", 1)[0]
        if depth == 0:
            m = KEY_RE.match(code)
            if m:
                prefix, key, start = m.group(1), m.group(2), pos
        depth += code.count("{") - code.count("}")
        pos += len(ln) + 1
        if depth == 0 and key is not None:
            out.append((prefix, key, text[start:pos]))
            key = None
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    repo = Path(__file__).resolve().parent.parent
    ap.add_argument("--ef", default=str(repo.parent / "vic3_mods_out" / "E&F"))
    ap.add_argument("--hotfix", default=str(repo / "_ef" / "ef hotfix 1.13"))
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    ef, hotfix = Path(a.ef), Path(a.hotfix)
    src = ef / SRC_REL
    if not src.is_file():
        print(f"ERROR: no {src}", file=sys.stderr)
        return 2

    # keys the hotfix already defines in another scripted_effects file
    overridden = {}
    for p in sorted((hotfix / "common" / "scripted_effects").glob("*.txt")):
        if p.name == Path(DST_REL).name:
            continue
        for prefix, key, _ in top_blocks(read(p)):
            overridden[key] = p.name

    blocks, skipped, sites = [], [], 0
    for _prefix, key, body in top_blocks(read(src)):
        if not RESERVES_RE.search(body):
            continue
        if key in overridden:
            skipped.append((key, overridden[key]))
            continue
        new, n = RESERVES_RE.subn(r"\g<1>0", body)
        sites += n
        blocks.append("REPLACE_OR_CREATE:" + new.lstrip())

    for key, where in skipped:
        print(f"  skip {key}: overridden in {where}")
    text = BANNER.format(src=src.name, n=len(blocks), sites=sites) + "\n" + "\n".join(blocks)
    dst = hotfix / DST_REL
    old = read(dst) if dst.is_file() else None
    print(f"{DST_REL}: {len(blocks)} effect(s), {sites} site(s), "
          f"{'unchanged' if old == text else 'CHANGED'}")
    if a.check:
        return 1 if old != text else 0
    if old != text:
        dst.write_bytes(text.encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
