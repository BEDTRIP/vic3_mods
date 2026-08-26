"""
regen_llwa_kai.py -- builds the LLWA x Kuromi's AI compatch in
`_llwa/llwa+kai done`.

The bug (LLWA.2/plan): LLWA carries `common/ai_strategies/
03_political_strategies.txt` at the EXACT vanilla relative path, and its
content is a stale pre-1.13 vanilla copy -- 125-line diff against current
vanilla, the string "LLWA" does not appear in the file once. Per the engine's
path-resolution model (section 3 of the rules file), a file at an identical
relative path is a FILE-level override: the single latest mod's file at that
path wins entirely, vanilla's own file at that path drops out of the merge
altogether, not just key-by-key. LLWA loads last in the target chain, so its
stale file wins -- reverting all nine `ai_strategy_*` records the file
defines to their pre-1.13 shape and, because a bare key with no prefix also
overrides (section 3), wiping every INJECT: any earlier mod (Kuromi's AI in
particular) had already applied to them.

Nine keys, three different outcomes:

  * ai_strategy_default -- NOT in this file (checked: grep for the key in
    both LLWA's copy and current vanilla's 03_political_strategies.txt finds
    nothing in either -- it's defined elsewhere in vanilla's ai_strategies).
    LLWA's only touch to it is a separate, purely additive
    INJECT:subsidies file. Noneed -- not handled here, see the README.

  * ai_strategy_maintain_mandate_of_heaven -- touched by nobody else (not
    KAI, not VC, not TGR per the machine matrix). Restoring current vanilla
    at this path is enough; there's no INJECT to reapply on top.

  * The other seven -- ai_strategy_conservative_agenda, _reactionary_agenda,
    _progressive_agenda, _egalitarian_agenda, _nationalist_agenda (KAI-only,
    5 keys) and ai_strategy_great_reforms, _tanzimat_reforms,
    _meiji_restoration (three-way with VC too -- LLWA.3/plan; VC and KAI
    already have a closed merge for these three in `_vc/kai+vc done`, reused
    here rather than re-derived) -- all need KAI's contribution reapplied on
    top of a restored-vanilla base.

The fix is three files, loaded in this order WITHIN our own mod (filename
sort: "0" < "z"):

  1. `03_political_strategies.txt` at the identical vanilla relative path --
     an exact byte-for-content copy of CURRENT vanilla. Our mod loads after
     LLWA, so this file wins the same file-level override LLWA's stale copy
     currently wins, and vanilla's real content is back in the merge.
  2. `zzz_llwa_kai_political_strategies.txt` -- KAI's five pure-agenda
     INJECT:s, read live from KAI's own file and reapplied verbatim on top
     of the now-current vanilla base.
  3. `zzzz_llwa_kai_vc_reforms.txt` -- the three shared-with-VC keys, reused
     record-for-record from the already-closed, already-verified
     `_vc/kai+vc done/common/ai_strategies/zz_vc_kai_ai_strategies.txt`
     rather than re-deriving the same three-way merge a second time. This
     also serves the ai_strategies half of LLWA.3 (LLWA x VC) -- see
     `_llwa/llwa+vc done/README.md`, which points back here for exactly
     this reason (one file, not duplicated across two compatch folders).

Usage:
    python3 regen_llwa_kai.py            # write the compatch
    python3 regen_llwa_kai.py --check    # report only, exit 1 if sources drifted
"""

from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vic3merge3 import brace_balance, needs_bom, read_lines  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
res = lambda p: os.path.normpath(os.path.join(HERE, p))

VANILLA = res("../../vic3_mods_out/.vanillaVIC3")
KAI = res("../../vic3_mods_out/TechRes+Kuromi/kai")
KAI_VC_MERGE = res("../_vc/kai+vc done/common/ai_strategies/zz_vc_kai_ai_strategies.txt")
OUT = res("../_llwa/llwa+kai done")

DATE = "2026-08-26"
CHECK_ONLY = False
WRITTEN: dict[str, bytes] = {}

AGENDA_KEYS = [
    "ai_strategy_conservative_agenda",
    "ai_strategy_reactionary_agenda",
    "ai_strategy_progressive_agenda",
    "ai_strategy_egalitarian_agenda",
    "ai_strategy_nationalist_agenda",
]
REFORM_KEYS = [
    "ai_strategy_great_reforms",
    "ai_strategy_tanzimat_reforms",
    "ai_strategy_meiji_restoration",
]


def block(lines: list[str], i: int) -> tuple[list[str], int]:
    depth = 0
    started = False
    for j in range(i, len(lines)):
        code = lines[j].split("#", 1)[0]
        depth += code.count("{") - code.count("}")
        if "{" in code:
            started = True
        if started and depth <= 0:
            return lines[i:j + 1], j + 1
    return lines[i:], len(lines)


def record(path: str, key: str) -> list[str] | None:
    """Lines of one top-level record, key line included, prefix stripped off
    (callers that care about the original prefix use raw_prefix())."""
    lines = read_lines(path)
    pat = re.compile(r"^(?:[A-Z_]+:)?" + re.escape(key) + r"\s*=\s*\{")
    for i, raw in enumerate(lines):
        if pat.match(raw.split("#", 1)[0].lstrip("﻿")):
            body, _ = block(lines, i)
            body[0] = re.sub(r"^﻿?(?:[A-Z_]+:)?", "", body[0])
            return body
    return None


def raw_prefix(path: str, key: str) -> str:
    """The literal prefix (e.g. 'INJECT:', '' for bare) the source file uses
    for this key -- used when we want to reissue verbatim, not decide our
    own prefix."""
    lines = read_lines(path)
    pat = re.compile(r"^((?:[A-Z_]+:)?)" + re.escape(key) + r"\s*=\s*\{")
    for raw in lines:
        m = pat.match(raw.split("#", 1)[0].lstrip("﻿"))
        if m:
            return m.group(1)
    raise AssertionError(f"{key} not found in {path}")


def write(rel: str, text: str, bom: bool | None = None):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    body = text.rstrip("\n") + "\n"
    balance = brace_balance(body)
    assert balance == 0, f"{rel}: brace balance {balance}"
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


def build_vanilla_restore():
    """File 1: exact current-vanilla content at the identical relative path
    LLWA's stale file occupies. A file-level path override, not a key-level
    REPLACE: -- see module docstring."""
    src = os.path.join(VANILLA, "common/ai_strategies/03_political_strategies.txt")
    assert os.path.isfile(src), "vanilla 03_political_strategies.txt not found -- game update?"
    lines = read_lines(src)

    for key in AGENDA_KEYS + REFORM_KEYS + ["ai_strategy_maintain_mandate_of_heaven"]:
        assert record(src, key) is not None, (
            f"current vanilla no longer defines {key} in this file -- "
            f"the path-restore fix needs re-checking against the new file")
    assert record(src, "ai_strategy_default") is None, (
        "vanilla now defines ai_strategy_default in 03_political_strategies.txt -- "
        "the noneed reasoning for that key (separate INJECT:subsidies file, "
        "never touched by this file) needs re-checking")

    header = (
        "# LLWA x Kuromi's AI / VC compatch -- restore current-vanilla common/ai_strategies/03_political_strategies.txt\n"
        "# Generated by tools/regen_llwa_kai.py on " + DATE + ". Do not hand-edit: the next\n"
        "# run overwrites this file. Change the generator instead.\n"
        "#\n"
        "# Why this file exists: LLWA carries a stale pre-1.13 copy of this exact\n"
        "# vanilla file (125-line diff, zero LLWA content -- word 'LLWA' does not\n"
        "# appear). Same relative path => file-level override (rules section 3):\n"
        "# LLWA loading last wins the path entirely, vanilla's real content drops\n"
        "# out of the merge, and every ai_strategy_* record this file defines\n"
        "# reverts to its pre-1.13 shape -- wiping any earlier mod's INJECT: on\n"
        "# them along the way (bare key with no prefix also overrides). This file\n"
        "# is byte-identical to current vanilla's own content at this path; our\n"
        "# mod loads after LLWA, so it wins the same file-level override LLWA\n"
        "# currently wins, and restores vanilla to the merge. The two files that\n"
        "# follow it (sorted after by filename) re-apply what KAI and VC had\n"
        "# already put on top before LLWA broke it.\n"
    )
    write("common/ai_strategies/03_political_strategies.txt", header + "\n" + "\n".join(lines))


def build_kai_agendas():
    """File 2: KAI's five pure-agenda INJECT:s, read live and reapplied
    verbatim on top of the restored vanilla base."""
    kai_f = os.path.join(KAI, "common/ai_strategies/kai_political_strategies.txt")
    assert os.path.isfile(kai_f), "KAI's kai_political_strategies.txt not found -- did KAI rename it?"

    out_records = []
    for key in AGENDA_KEYS:
        prefix = raw_prefix(kai_f, key)
        assert prefix == "INJECT:", (
            f"KAI's {key} is no longer a plain INJECT: (got {prefix!r}) -- "
            f"re-check whether this is still a clean re-apply")
        body = record(kai_f, key)
        assert body, f"KAI has no {key} -- re-check the key list"
        text = "INJECT:" + "\n".join(body)
        out_records.append(text)

    header = (
        "# LLWA x Kuromi's AI compatch -- reapply KAI's five agenda-strategy AI tunings\n"
        "# Generated by tools/regen_llwa_kai.py on " + DATE + ". Do not hand-edit: the next\n"
        "# run overwrites this file. Change the generator instead.\n"
        "#\n"
        "# Load order: Kuromi's AI -> ... -> LLWA -> 03_political_strategies.txt (this\n"
        "# folder) -> THIS.\n"
        "# Why this file exists: LLWA's stale 03_political_strategies.txt (see the\n"
        "# other file in this folder) wipes KAI's INJECT:s into these five agenda\n"
        "# strategies along with everything else at that path. Copied live from\n"
        "# KAI's own kai_political_strategies.txt, unchanged -- these five are plain\n"
        "# INJECT:s with no VC involvement, so a verbatim re-apply is all that's\n"
        "# needed once the vanilla base is restored.\n"
    )
    write("common/ai_strategies/zzz_llwa_kai_political_strategies.txt",
          header + "\n" + "\n\n".join(out_records))


def build_kai_vc_reforms():
    """File 3: the three keys shared with VC too, reused from the already-
    closed `_vc/kai+vc done` merge rather than re-derived."""
    assert os.path.isfile(KAI_VC_MERGE), (
        "_vc/kai+vc done/common/ai_strategies/zz_vc_kai_ai_strategies.txt not "
        "found -- did that compatch move or get renamed? This generator "
        "reuses its output rather than re-deriving the VC x KAI merge.")

    out_records = []
    for key in REFORM_KEYS:
        prefix = raw_prefix(KAI_VC_MERGE, key)
        assert prefix in ("INJECT:", "REPLACE_OR_CREATE:"), (
            f"unexpected prefix {prefix!r} for {key} in the kai+vc merge file -- re-check")
        body = record(KAI_VC_MERGE, key)
        assert body, f"kai+vc merge file has no {key} -- did the merge change shape?"
        out_records.append(prefix + "\n".join(body))

    header = (
        "# LLWA x Kuromi's AI x VC compatch -- reapply the closed KAI x VC merge on three ai_strategies\n"
        "# Generated by tools/regen_llwa_kai.py on " + DATE + ". Do not hand-edit: the next\n"
        "# run overwrites this file. Change the generator instead.\n"
        "#\n"
        "# Load order: Kuromi's AI -> ... -> Victorian Century -> addon-VC (incl.\n"
        "# _vc/kai+vc done) -> ... -> LLWA -> 03_political_strategies.txt (this\n"
        "# folder) -> THIS.\n"
        "# Why this file exists: ai_strategy_great_reforms, _tanzimat_reforms and\n"
        "# _meiji_restoration are shared three ways -- KAI, VC, and LLWA (LLWA.2 AND\n"
        "# LLWA.3 in the plan, same three keys). addon-VC already carries a closed,\n"
        "# verified three-way merge for exactly these three\n"
        "# (_vc/kai+vc done/common/ai_strategies/zz_vc_kai_ai_strategies.txt) --\n"
        "# LLWA's stale 03_political_strategies.txt wipes it along with everything\n"
        "# else at that path. Rather than re-derive the same merge a second time,\n"
        "# this file copies that compatch's own record bodies verbatim (read live,\n"
        "# not hand-pasted) and reissues them here, after the vanilla restore. Also\n"
        "# serves the ai_strategies half of the LLWA x VC pair -- see\n"
        "# _llwa/llwa+vc done/README.md, which points back here instead of writing\n"
        "# these same three keys a second time.\n"
    )
    write("common/ai_strategies/zzzz_llwa_kai_vc_reforms.txt",
          header + "\n" + "\n\n".join(out_records))


def self_check() -> int:
    bad = 0
    # This generator deliberately layers files WITHIN one mod (filename-
    # sorted): file 1 bare-restores vanilla as a floor, files 2/3 explicitly
    # REPLACE_OR_CREATE:/INJECT: specific keys on top of it. A bare key
    # followed by ONE later explicit override of the SAME key is that
    # intentional chain, not a bug -- so bare and explicit sightings are
    # tracked separately and only duplicates WITHIN each category are
    # flagged (two bare definitions of the same key, or two competing
    # REPLACE:/REPLACE_OR_CREATE: on the same key -- both still real bugs).
    seen_bare: dict[tuple[str, str], str] = {}
    seen_explicit: dict[tuple[str, str], str] = {}
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
        depth = 0
        for raw in text.split("\n"):
            code = raw.split("#", 1)[0]
            if depth == 0:
                m = re.match(r"^﻿?([A-Z_]+:)?([A-Za-z0-9_.\-]+)\s*=\s*\{", code)
                prefix = (m.group(1) or "").rstrip(":") if m else None
                if m and prefix in ("INJECT", "TRY_INJECT"):
                    m = None
                if m and m.group(2) not in ("COUNTRIES", "GLOBAL", "BUILDINGS", "POPS"):
                    where = (category, m.group(2))
                    bucket = seen_bare if prefix == "" else seen_explicit
                    kind = "bare" if prefix == "" else "explicit"
                    if where in bucket:
                        print(f"  FAIL duplicate {kind} key {m.group(2)} in {category}: "
                              f"{bucket[where]} and {rel}")
                        bad += 1
                    bucket[where] = rel
            depth += code.count("{") - code.count("}")
    total_keys = len(set(seen_bare) | set(seen_explicit))
    print(f"  self-check: {len(WRITTEN)} files, {total_keys} top-level keys, "
          f"{bad} problem(s)")
    return bad


def main() -> int:
    global CHECK_ONLY
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only, do not write")
    args = ap.parse_args()
    CHECK_ONLY = args.check

    print(f"regen_llwa_kai.py -> {OUT}")
    for name, fn in (
        ("vanilla restore", build_vanilla_restore),
        ("kai agendas", build_kai_agendas),
        ("kai+vc reforms", build_kai_vc_reforms),
    ):
        print(f"[{name}]")
        fn()

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
        print("\nall files match the current vanilla / LLWA / KAI / kai+vc sources")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
