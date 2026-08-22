#!/usr/bin/env python3
"""
Generate the "E&F Currency Merge" mod: all E&F currency goods collapse into one.

Why
---
Victoria 3 1.13 crashes on entering a campaign above 128 goods, silently, with
nothing in error.log. The megapack sits at 162: vanilla 53, PSC 4, E&F+hotfix 65,
Morgenroete 5, T&R 35. 57 of those 65 E&F goods are currencies, one per monetary
system law.

Collapsing 56 of them into `spe_uni_c` takes the pack to 106 and leaves Tech & Res
whole. Nothing about the monetary system is removed: all 95 currency laws stay,
every country keeps its own law and its own `pm_currency_*`, the bank still mints,
the buildings still pay for liquidity. Only the good on the belt is shared.

What was checked before writing this
------------------------------------
E&F's exchange rates, money supply, gold and silver standard, stockpiles, imports
and exports run on country and global VARIABLES, not on the market data of the
currency goods. Of the 36 script-value families E&F defines per currency, 14 are
referenced nowhere at all -- including every one that reads
`market.mg:<X>_c.market_goods_*`. The only live consumer of a currency good's
market data is `<CUR>_price` -> `base_demande_<CUR>_price` ->
`central_bank_overlord_currency_purchases`, and that is the overlord-buys-subject-
currency path whose PM group E&F already disabled on building_bank
("caché suppretion suite à trop de bug").

So the merge touches goods, production methods, pop needs and the bookkeeping that
names goods -- and nothing else.

95 versus 57
------------
E&F ships 95 currency laws and 95 x 3 production methods against 57 live goods:
38 of those PMs already point at goods its own author commented out, and so do the
matching pop-need entries, modifier types, static-modifier lines and script values.
This generator retargets all 95, so those pre-existing dead references are fixed in
the same pass.

What it generates
-----------------
Path overrides (whole file, rebuilt from the source; the hotfix wins over E&F):
  common/goods/ef_00_goods.txt                       56 goods commented out
  common/pop_needs/00_ef_pop_needs.txt               94 entries dropped
  common/modifier_type_definitions/00_ef_building_modifier_types.txt
                                                     orphaned modifier types dropped
  common/static_modifiers/00_ef_dynamic_modifier_{building,country,state}.txt
                                                     95 identical lines -> 1
  common/named_colors/00_ef_goods_colors.txt         colours for dead goods dropped

Key-level overrides (new files, later definition wins):
  common/production_methods/zz_ef_cm_production_methods.txt   95 x 3 PM
  common/script_values/zz_ef_cm_script_values.txt             the values that read a good
  common/scripted_triggers/zz_ef_cm_scripted_triggers.txt     market_goods_is_currency
  localization/*/zz_ef_cm_goods_l_*.yml                       the good's name

Usage:
    python3 regen_ef_currency_merge.py
    python3 regen_ef_currency_merge.py --check
    python3 regen_ef_currency_merge.py --keep spe_uni_c
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent.parent          # vic3_mods/
DEFAULT_OUT_ROOT = DEFAULT_ROOT.parent / "vic3_mods_out"       # vic3_mods_out/

EF = "E&F"
HOTFIX = "_ef/ef hotfix 1.13"

# Everything is generated straight INTO the hotfix -- one mod in the game.
MOD = HOTFIX

# ...which creates a loop: two of the generated files are built FROM the hotfix's
# own hand-written ones, and if the output lands on the input the generator starts
# eating its own tail on the second run. So the hand-written originals live in
# _gen_source/, a folder the game does not read (it scans common/, events/, gui/,
# localization/, gfx/, map_data/, .metadata/ and nothing else).
#
# The folder is created on first run from whatever is in the mod right now, so the
# bootstrap happens once and by itself. EDIT THE COPIES IN _gen_source/ from then
# on -- the ones under common/ are output and get overwritten.
SRC_DIR = "_gen_source"

GOODS_FILE = "common/goods/ef_00_goods.txt"
POPNEED_FILE = "common/pop_needs/00_ef_pop_needs.txt"
MODTYPE_FILE = "common/modifier_type_definitions/00_ef_building_modifier_types.txt"
COLORS_FILE = "common/named_colors/00_ef_goods_colors.txt"
STATIC_FILES = [
    "common/static_modifiers/00_ef_dynamic_modifier_building.txt",
    "common/static_modifiers/00_ef_dynamic_modifier_country.txt",
    "common/static_modifiers/00_ef_dynamic_modifier_state.txt",
]
BANK_PM_FILE = "common/production_methods/15_ef_bank.txt"
LIQ_PM_FILE = "common/production_methods/00_ef_market_liquidity.txt"
CURVAL_FILE = "common/script_values/01_economic_currency_scripted_value.txt"
ECOVAL_FILE = "common/script_values/00_economic_scripted_value.txt"
TRIGGER_FILE = "common/scripted_triggers/00_ef_custom_trigger.txt"

BANNER = ("### E&F Currency Merge -- GENERATED FILE, DO NOT EDIT\n"
          "### Rebuild with tools/regen_ef_currency_merge.py after any E&F or hotfix update.\n"
          "###\n")

# Overriding an entry that already exists needs the REPLACE_OR_CREATE: prefix.
# Simply repeating the key in a later file DOES NOTHING -- the first definition
# stays live. This cost a full test round to find, and it is invisible except in
# the log: repeating market_goods_is_currency without the prefix left E&F's
# original list of 95 currency goods in play, 94 of which the merge had removed,
# and E&F's market GUI calls that trigger per market good every frame:
#
#   [jomini_script_system.cpp:247]: Script system error!
#     Error: Invalid right side during comparison 'g'
#     Script location: common/scripted_triggers/00_ef_custom_trigger.txt:1467
#     common/scripted_guis/09_ef_other.txt:2095
#
# -- 11,905 of those in two seconds, which rotated the entire error.log buffer and
# made every other problem invisible. The same silence hid the rewritten central
# bank spawners: they were never called, so the bank stayed government property.
#
# REPLACE_OR_CREATE: rather than REPLACE: because these files mix overrides with
# new keys, and REPLACE: on a key that does not exist yet is an error.
#
# This applies to scripted_triggers, scripted_effects and script_values alike.
# It does NOT apply to a file that overrides another file BY PATH (goods,
# pop_needs, the static modifiers) -- there the whole file is replaced.
OVERRIDE = "REPLACE_OR_CREATE:"


def override_keys(text: str) -> str:
    """Prefix every top-level `key = {` in a generated block with REPLACE_OR_CREATE:."""
    return re.sub(r"(?m)^(?![\s#])(?!REPLACE|INJECT|TRY_)([A-Za-z_][A-Za-z0-9_]*)(\s*=\s*\{)",
                  OVERRIDE + r"\1\2", text)


# --- parsing helpers --------------------------------------------------------


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def strip_comments(s: str) -> str:
    out = []
    for line in s.split("\n"):
        q, r = False, ""
        for ch in line:
            if ch == '"':
                q = not q
            if ch == "#" and not q:
                break
            r += ch
        out.append(r)
    return "\n".join(out)


def top_keys(s: str) -> list[str]:
    t = strip_comments(s)
    ks, d = [], 0
    for m in re.finditer(r"([A-Za-z_][\w:]*)\s*=\s*\{|\{|\}", t):
        x = m.group(0)
        if x == "}":
            d -= 1
            continue
        if x == "{":
            d += 1
            continue
        if d == 0:
            ks.append(m.group(1))
        d += 1
    return ks


def block_span(s: str, start: int) -> int:
    """Index just past the closing brace of the block whose `{` is at/after start.

    Comment- and quote-aware. E&F writes things like `#end_tag_1` and the odd brace
    inside a comment; counting raw braces walks off the end of the block and every
    slice after it is silently wrong.
    """
    i = s.index("{", start)
    depth = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == "#":
            j = s.find("\n", i)
            i = n if j < 0 else j
            continue
        if c == '"':
            j = s.find('"', i + 1)
            i = n if j < 0 else j + 1
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unbalanced braces")


def iter_blocks(s: str, name_re: str):
    for m in re.finditer(r"^([ \t]*)((?:\w+:)?)(" + name_re + r")\s*=\s*\{", s, re.M):
        yield m.group(3), m.start(), block_span(s, m.end() - 1)


_TOK = re.compile(r'[#"{}]|[A-Za-z_][\w:]*\s*=\s*\{')


def iter_top_blocks(s: str):
    """Yield (key, start, end) for blocks at brace depth 0 ONLY.

    Two traps this exists to avoid, both of which cost a crash before the main menu:

    * iter_blocks() anchors on `^[ \t]*key = {`, which is fine for one known key but
      catastrophic as a sweep: E&F indents its script values, so every nested
      `value = {`, `if = {`, `subtract = {` matches too. The first sweep emitted 658
      bogus top-level keys called `value`, `if`, `subtract`, `multiply`.
    * the first fix walked a comment-stripped copy to track depth but sliced the
      ORIGINAL string with those offsets. Stripping comments shortens lines, so every
      offset after the first comment pointed somewhere else entirely.

    So: scan the original text, skip comments and quoted strings as we go.
    """
    i, n, depth = 0, len(s), 0
    while i < n:
        m = _TOK.search(s, i)
        if not m:
            return
        tok = m.group(0)
        if tok == "#":
            j = s.find("\n", m.start())
            i = n if j < 0 else j + 1
        elif tok == '"':
            j = s.find('"', m.start() + 1)
            i = n if j < 0 else j + 1
        elif tok == "{":
            depth += 1
            i = m.end()
        elif tok == "}":
            depth -= 1
            i = m.end()
        elif depth == 0:
            end = block_span(s, m.end() - 1)
            yield tok.split("=")[0].strip(), m.start(), end
            i = end
        else:
            depth += 1
            i = m.end()


def sub_block(block: str, name: str) -> str | None:
    m = re.search(r"\b" + name + r"\s*=\s*\{", block)
    return None if not m else block[m.start(): block_span(block, m.end() - 1)]


# --- retargeting ------------------------------------------------------------


class Retarget:
    """Rewrite every reference to a dead currency good into the surviving one.

    Two shapes have to be handled separately, and getting this wrong is silent:

      * a bare key -- `market.mg:pound_sterling_c.`, `g:pound_sterling_c`,
        `goods = pound_sterling_c`, `required_input_goods = pound_sterling_c`.
        A \\b-anchored match is enough.
      * a key baked into a modifier name -- `goods_input_pound_sterling_c_add`,
        `goods_output_pound_sterling_c_mult`, `state_sell_orders_..._add`.
        Here the key is followed by `_`, so \\b does NOT hold and a bare-key
        pattern skips it without a word of complaint.

    Script-value and PM KEYS that merely contain a currency name
    (`pound_sterling_c_market_goods_buy_orders`, `base_demande_pound_sterling`)
    must survive untouched -- they are the identifiers the rest of E&F calls.
    The first is safe because the key there is followed by `_`; the second
    because it has no `_c` at all.
    """

    def __init__(self, dead: list[str], keep: str):
        alt = "|".join(sorted((re.escape(g) for g in dead), key=len, reverse=True))
        self.keep = keep
        self.mod = re.compile(r"\b(goods_(?:input|output)_|state_sell_orders_)(?:" + alt +
                              r")(_add|_mult|_max_add)\b")
        self.bare = re.compile(r"\b(?:" + alt + r")\b")
        self.any = re.compile(r"(?:" + alt + r")")

    def __call__(self, text: str) -> str:
        text = self.mod.sub(lambda m: m.group(1) + self.keep + m.group(2), text)
        return self.bare.sub(self.keep, text)

    def touches(self, text: str) -> bool:
        t = strip_comments(text)
        return bool(self.mod.search(t) or self.bare.search(t))


# --- inventory --------------------------------------------------------------


def hand_written(hf: Path, rel: str) -> Path:
    """The hand-written original of a file the generator overwrites.

    First run moves it into _gen_source/; after that the copy there is the source
    of truth and the one under common/ is output.
    """
    src = hf / SRC_DIR / Path(rel).name
    if not src.exists():
        live = hf / rel
        if not live.exists():
            raise SystemExit(f"neither {src} nor {live} exists")
        src.parent.mkdir(parents=True, exist_ok=True)
        src.write_bytes(live.read_bytes())
        print(f"  bootstrapped  {SRC_DIR}/{src.name}  (hand-written original moved out of the way)")
    return src


def inventory(ef: Path, hf: Path, keep: str):
    goods_src = hand_written(hf, GOODS_FILE)
    active = [k for k in top_keys(read(goods_src)) if k.endswith("_c")]
    if keep not in active:
        raise SystemExit(f"{keep} is not an active good in {goods_src}")

    bank = read(ef / BANK_PM_FILE)
    names = [k[len("pm_currency_"):-len("_currency")]
             for k in top_keys(bank)
             if k.startswith("pm_currency_") and k.endswith("_currency")]

    commented_out = [g for g in active if g != keep]           # still live today
    # NOTE the parentheses: `A | B - {keep}` binds as `A | (B - {keep})` and would
    # leave the surviving good inside `dead`, which quietly deletes its own entries.
    dead = sorted(({f"{n}_c" for n in names} | set(active)) - {keep})
    return active, commented_out, dead, names


# Script values that must be REWRITTEN, not mechanically retargeted.
#
# `currency_market_goods_sell_orders` is the target of E&F's money-issuance
# controller. It reads the market-wide buy orders for the country's own currency:
#
#     target_demand_currency              = currency_market_goods_sell_orders
#     target_demand_currency_for_modifier = (target - current) / current * 100
#     currency_demande on the bank        = goods_output_<cur>_mult 0.01 * that
#
# so the bank drives its output until it equals market demand for its currency.
# That was self-limiting while every country had its OWN good -- "demand for the
# pound" was, near enough, Britain's demand. With one shared good it is the whole
# market's demand, and every bank in the market chases all of it: six banks on the
# British market each issued ~196K against ~192K of buy orders, price -99%.
#
# The rewrite keeps E&F's design -- the market's issuers together still track the
# market's demand -- and splits that demand between them by GDP.
REWRITTEN = {"currency_market_goods_sell_orders"}

SHARE_BLOCK = """
### ---------------------------------------------------------------------------
### Money issuance: split the market's currency demand between its issuers
### ---------------------------------------------------------------------------
###
### See the note above REWRITTEN in tools/regen_ef_currency_merge.py for why this
### is here. Short version: E&F's bank chases `market buy orders for my currency`,
### which stopped meaning `my country' the moment every country minted the same
### good.
###
### The weight is gdp. It is one field, always available, and it tracks both halves
### of currency demand at once -- pops (popneed_currency, roughly half the market's
### buy orders) and buildings (pmg_market_liquidity at 98 per workforce unit on the
### country's own buildings, the other half). Population alone would understate an
### industrial economy; the hotfix's population x SoL curve is the right shape for
### pops but knows nothing about factories.
###
### Countries sitting on law_no_market_liquidity issue nothing and take no share,
### but their pops and buildings still buy -- so their demand is covered by the
### market's issuers pro rata, which is what one expects of a colonial market.

zz_ef_cm_issuer_weight = {
	value = gdp
	min = 1
}

zz_ef_cm_market_issuer_weight = {
	value = 0
	every_country = {
		limit = {
			market = prev.market
			has_modifier = has_central_bank
			NOT = { has_law = law_type:law_no_market_liquidity }
		}
		add = zz_ef_cm_issuer_weight
	}
	min = 1
}

zz_ef_cm_issuer_share = {
	value = zz_ef_cm_issuer_weight
	divide = zz_ef_cm_market_issuer_weight
	min = 0.0001
	max = 1
}

### E&F's original is a 15 KB if-chain over 95 laws, every branch reading the buy
### orders of that law's own good. With one good the chain collapses to one branch,
### and the only thing left to decide is this country's share of it.
currency_market_goods_sell_orders = {
	value = 0
	if = {
		limit = {
			NOT = { has_law = law_type:law_no_market_liquidity }
		}
		add = market.mg:KEEP.market_goods_buy_orders
		multiply = zz_ef_cm_issuer_share
	}
}
"""


# --- output -----------------------------------------------------------------


def emit(path: Path, text: str, check: bool, acc: list[bool]) -> None:
    if text.count("{") != text.count("}"):
        raise ValueError(f"{path.name}: unbalanced braces")
    old = path.read_text(encoding="utf-8-sig") if path.exists() else None
    changed = old != text
    acc.append(changed)
    if check:
        print(f"  {'DRIFT' if changed else 'ok   '}  {path.name}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8-sig", newline="\n")
        print(f"  {'written  ' if changed else 'unchanged'}  {path.name}")


# --- generators -------------------------------------------------------------


def gen_goods(src: str, commented_out: list[str], keep: str) -> str:
    out = src
    for g in commented_out:
        for _, a, b in iter_blocks(out, re.escape(g)):
            out = out[:a] + "\n".join("# " + l for l in out[a:b].split("\n")) + out[b:]
            break
    return (BANNER +
            f"### Source: {SRC_DIR}/{Path(GOODS_FILE).name} -- the hand-written original.\n"
            f"### {len(commented_out)} currency goods commented out; everything mints `{keep}`.\n"
            "### Commented rather than deleted, so the file still diffs against its source --\n"
            "### the same way E&F's own author retired 32 currencies when he moved to 1.13.\n\n"
            ) + out


def gen_popneed(src: str, dead: set[str], keep: str) -> tuple[str, int]:
    """Drop `entry = { goods = <dead> ... }` blocks.

    Brace-matched, not regex-matched: E&F closes the last entry as `}#end_tag_1`,
    a comment on the same line as the brace, and a pattern looking for a lone
    closing brace runs straight past it into the close of popneed_currency itself.
    """
    out, n = src, 0
    while True:
        for m in re.finditer(r"[ \t]*entry\s*=\s*\{", out):
            end = block_span(out, m.end() - 1)
            g = re.search(r"\bgoods\s*=\s*([a-z0-9_]+)", strip_comments(out[m.start():end]))
            if g and g.group(1) in dead:
                nl = out.find("\n", end)
                out = out[:m.start()] + out[(nl + 1 if nl != -1 else end):]
                n += 1
                break
        else:
            break
    return (BANNER +
            f"### Source: {SRC_DIR}/{Path(POPNEED_FILE).name} -- the hand-written original.\n"
            f"### popneed_currency keeps two entries: local_currency (weight 0.1, the fallback\n"
            f"### for countries with no monetary system) and {keep} (0.25). The {n} dropped\n"
            "### entries all carried the same weights, so a pop's currency need is satisfied\n"
            "### exactly as before -- out of one good instead of 95 listed / 57 real ones.\n\n"
            ) + out, n


def gen_modtypes(src: str, dead: set[str]) -> tuple[str, int]:
    out, n = src, 0
    pat = re.compile(r"^[ \t]*(?:goods_(?:input|output)|state_sell_orders)_([a-z0-9_]+_c)_(?:add|mult|max_add)\s*=\s*\{", re.M)
    while True:
        m = pat.search(out)
        while m and m.group(1) not in dead:
            m = pat.search(out, m.end())
        if not m:
            break
        out = out[:m.start()] + out[block_span(out, m.end() - 1):].lstrip("\n")
        n += 1
    return (BANNER +
            f"### Source: E&F's own {MODTYPE_FILE}.\n"
            f"### {n} modifier types dropped. E&F declares goods_input/output_<currency>_mult by\n"
            "### hand for every currency; a declaration whose good no longer exists is an orphan.\n"
            "### The ones for the surviving good are untouched.\n\n"
            ) + out, n


def gen_static(src: str, path_name: str, dead: set[str], keep: str) -> tuple[str, list[str]]:
    """95 identical per-currency lines collapse to one line for the kept good."""
    notes: list[str] = []
    out: list[str] = []
    seen: set[str] = set()
    for line in src.split("\n"):
        # The trailing `\s*$` used to be `\s*$` with no room for a comment, and E&F
        # marks the end of its currency lists with `#end_tag_1` on the same line as
        # the last entry. One line out of 95 slipped through every time.
        m = re.match(r"^([ \t]*)(goods_(?:input|output)|state_sell_orders)_([a-z0-9_]+_c)_(add|mult|max_add)\s*=\s*(\S+)\s*(#.*)?$", line)
        if not m:
            if line.strip() in ("{", "}"):
                seen.clear()
            out.append(line)
            continue
        indent, head, good, suffix, value, comment = m.groups()
        tail = (" " + comment) if comment else ""
        if good not in dead and good != keep:
            out.append(line)          # not a currency we touch
            continue
        # The kept good goes through the SAME dedupe as the dead ones. It has its own
        # line in E&F's list -- it is one of the 95 -- so special-casing it emitted the
        # collapsed line plus the original, and the modifier applied twice.
        tag = f"{head}_{suffix}"
        if tag in seen:
            if comment:
                out.append(f"{indent}{comment}")
            continue
        out.append(f"{indent}{head}_{keep}_{suffix} = {value}{tail}")
        seen.add(tag)
        notes.append(f"{head}_<currency>_{suffix} = {value} -> one line")
    return (BANNER +
            f"### Source: E&F's own {path_name}.\n"
            "### These modifiers list every currency with the same value, which was E&F's way of\n"
            "### saying \"whichever currency this country actually issues\". With one currency good\n"
            "### the list is one line and the effect is identical.\n\n"
            ) + "\n".join(out), notes


def gen_colors(src: str, dead: set[str]) -> tuple[str, int]:
    out, n = [], 0
    for line in src.split("\n"):
        m = re.match(r"^[ \t]*([a-z0-9_]+_c)\s*=", line)
        if m and m.group(1) in dead:
            n += 1
            continue
        out.append(line)
    return (BANNER + f"### Source: E&F's own {COLORS_FILE}. {n} colours for goods that no longer exist.\n\n"
            ) + "\n".join(out), n


def gen_pms(ef: Path, names: list[str], rt: Retarget) -> tuple[str, int, list[str]]:
    bank, liq = read(ef / BANK_PM_FILE), read(ef / LIQ_PM_FILE)
    out: list[str] = []
    missing: list[str] = []
    icons = [0]
    n = 0
    for src, prefix in ((bank, "pm_currency_"), (liq, "pm_market_liquidity_"), (bank, "pm_subject_currency_")):
        out.append(f"\n### {prefix}* -- {len(names)} currencies\n\n")
        for name in names:
            key = f"{prefix}{name}_currency"
            block = next((src[a:b] for k, a, b in iter_blocks(src, re.escape(key))), None)
            if block is None:
                missing.append(key)
                continue
            body = rt(block)
            # E&F points all 95 pm_currency_* at one texture, currency_type.dds, so the
            # bank's dropdown is 95 identical pound signs. Every currency already has
            # its own goods icon shipped with E&F; point the PM at that instead. Only
            # where the file actually exists -- a missing texture is a log line and a
            # blank square.
            if prefix == "pm_currency_":
                icon = f"gfx/interface/icons/goods_icons/currencies/{name}.dds"
                if (ef / icon).exists():
                    body = re.sub(r'texture\s*=\s*"[^"]*"', f'texture = "{icon}"', body, count=1)
                    icons[0] += 1
            body = re.sub(r"^\s*(?:\w+:)?" + re.escape(key) + r"\s*=\s*\{", "", body, count=1).rstrip()
            body = body[:body.rindex("}")].rstrip("\n")
            out.append(f"REPLACE:{key} = {{{body}\n}}\n\n")
            n += 1
    head = (BANNER +
            f"### Source: E&F's own {BANK_PM_FILE}\n"
            f"### and {LIQ_PM_FILE}.\n"
            "###\n"
            "### The WHOLE production method is restated, with the good swapped -- not just\n"
            "### `building_modifiers`.\n"
            "###\n"
            "### The first build restated only building_modifiers, on the theory that REPLACE:\n"
            "### swaps the sub-blocks a mod names and leaves the rest. In game the central\n"
            "### bank then offered all 95 currencies in its dropdown, though every\n"
            "### pm_currency_* carries `unlocking_laws` and `is_hidden_when_unavailable = yes`.\n"
            "### That is what a lost `unlocking_laws` looks like. Whether REPLACE: really\n"
            "### replaces the entry wholesale for production methods was not worth another\n"
            "### round of guessing: emitting the full block is correct under either rule.\n"
            "###\n"
            "### The cost is that texture, unlocking_laws and is_hidden_when_unavailable are\n"
            "### now pinned to E&F. The generator re-derives them from E&F on every run, so\n"
            "### they cannot drift -- but this file MUST be rebuilt after an E&F update.\n"
            "###\n"
            "### All 95 currencies are retargeted, not just the 56 whose goods we remove: E&F\n"
            "### ships 95 laws and 95 PMs against 57 goods, so 38 of these already pointed at\n"
            "### goods their own author had commented out.\n"
            "###\n"
            f"### {icons[0]} of the pm_currency_* got their own currency icon instead of the\n"
            "### shared currency_type.dds.\n")
    return head + "".join(out), n, missing


def gen_values(ef: Path, rt: Retarget) -> tuple[str, int]:
    out: list[str] = []
    n = 0
    for path in (CURVAL_FILE, ECOVAL_FILE):
        src = read(ef / path)
        out.append(f"\n### from {path}\n\n")
        for key, a, b in iter_top_blocks(src):
            block = src[a:b]
            if not rt.touches(block):
                continue
            if key in REWRITTEN:
                continue
            emitted = rt(block).strip()
            # Cheap guard against the depth bug ever coming back: what we write out
            # has to start with the same key we read in.
            if not re.match(r"^" + re.escape(key) + r"\s*=\s*\{", emitted):
                raise ValueError(f"{path}: emitted block does not start with {key!r}")
            out.append(OVERRIDE + emitted + "\n")
            n += 1
    head = (BANNER +
            f"### Source: E&F's own {CURVAL_FILE}\n"
            f"### and {ECOVAL_FILE}.\n"
            "###\n"
            "### Only the script values that actually read a currency GOOD are restated --\n"
            "### `market.mg:<X>_c.*` and `modifier:goods_input_<X>_c_add`. The rest of E&F's\n"
            "### currency machinery works off country and global variables and needs no change;\n"
            "### that is what makes this merge possible at all.\n"
            "###\n"
            "### Most of these are dead weight inside E&F already (nothing references\n"
            "### <CUR>_c_market_goods_buy_orders and friends), but a script value pointing at a\n"
            "### good that does not exist is an error line at load, so they are retargeted\n"
            "### rather than left behind.\n"
            "###\n"
            "### REPLACE_OR_CREATE: on every key -- a bare repeat of the key does not\n"
            "### override anything, see the note next to OVERRIDE in the generator.\n")
    return head + "".join(out) + override_keys(SHARE_BLOCK.replace("KEEP", rt.keep)), n + 4


def gen_triggers(ef: Path, dead: set[str], keep: str) -> str:
    src = read(ef / TRIGGER_FILE)
    block = next((src[a:b] for k, a, b in iter_blocks(src, "market_goods_is_currency")), None)
    if block is None:
        raise SystemExit("market_goods_is_currency not found")
    kept = [g for g in re.findall(r"goods\s*=\s*g:([a-z0-9_]+_c)\b", block) if g not in dead]
    if keep not in kept:
        kept.append(keep)
    body = "\n".join(f"\t\tgoods = g:{g}" for g in dict.fromkeys(kept))
    return (BANNER +
            f"### Source: E&F's own {TRIGGER_FILE}.\n"
            "### The trigger lists every currency good by key, and the ones we remove would be\n"
            "### unresolvable references. local_currency is deliberately NOT added: the trigger\n"
            "### hides currencies from the ordinary market list, and local_currency belongs there.\n"
            "###\n"
            "### REPLACE_OR_CREATE: is what makes this override at all. Without it E&F's\n"
            "### original 95-good list stayed live and its market GUI logged ~12,000 script\n"
            "### errors in two seconds -- see the note next to OVERRIDE in the generator.\n\n"
            + OVERRIDE + "market_goods_is_currency = {\n\tOR = {\n" + body + "\n\t}\n}\n")


def gen_loc(keep: str) -> dict[str, str]:
    return {
        "english": ("l_english:\n\n"
                    " # E&F Currency Merge: one shared currency good. The name is deliberately\n"
                    " # generic -- every country still has its own currency LAW, and that is what\n"
                    " # the monetary-system UI shows.\n"
                    f' {keep}:0 "Currency"\n'),
        "russian": ("l_russian:\n\n"
                    " # E&F Currency Merge: единый товар-валюта. Название намеренно обезличено —\n"
                    " # у каждой страны по-прежнему свой ЗАКОН о валюте, и в интерфейсе денежной\n"
                    " # системы виден именно он.\n"
                    f' {keep}:0 "Валюта"\n'),
    }


# --- prestige currencies ----------------------------------------------------


def gen_prestige(ef: Path, names: list[str], keep: str) -> tuple[str, int]:
    """One prestige variant of the shared good per currency.

    THE KEY IS THE OLD GOOD'S KEY. `pound_sterling_c` stopped being a good when the
    merge commented it out, so the name is free -- and every piece of localisation
    E&F ships for it, in eleven languages, plus the separate Russian translation
    mod, keeps working untouched. Same for the icon. Zero translation work, and no
    second set of names to keep in sync with the first.

    WHICH ONE A COMPANY PRODUCES is decided by `possible`, not by the company.
    Company -> country cannot be derived from the files: only 6 of E&F's 103
    companies name a tag at all, the rest go by interest markers and state regions.
    So every bank company is offered all 95, and each prestige good is gated on the
    currency law behind it. A country holding law_pound_sterling_currency can only
    ever match one of them.

    That gate is the thing to watch in game. Vanilla only ever uses `possible` here
    for `has_dlc_feature`, so whether it is evaluated in country scope is not
    something the files can settle.
    """
    out = []
    n = 0
    for name in names:
        icon = f"gfx/interface/icons/goods_icons/currencies/{name}.dds"
        if not (ef / icon).exists():
            icon = "gfx/interface/icons/goods_icons/currencies/spe_uni.dds"
        out.append(
            f"{name}_c = {{\n"
            f"\tpossible = {{\n"
            f"\t\thas_law = law_type:law_{name}_currency\n"
            f"\t}}\n"
            f"\tbase_good = {keep}\n"
            f"\tprestige_bonus = 0.1\n"
            f'\ttexture = "{icon}"\n'
            f"}}\n\n"
        )
        n += 1
    head = (BANNER +
            "### Source: the 95 currencies E&F declares production methods for.\n"
            "###\n"
            "### Prestige goods do not count against the 128-goods ceiling -- measured, not\n"
            "### assumed: 100 dummies on one base good load fine. So the currencies come back\n"
            "### as prestige variants of the one shared good, with their own names, their own\n"
            "### icons, a prestige bonus and the engine's +20% throughput for buildings that\n"
            "### consume them.\n"
            "###\n"
            "### Produced only by a company that owns a building making the base good -- which\n"
            "### is why building_bank has to be ownable and has to be in the bank companies'\n"
            "### building_types. See zz_ef_cm_bank.txt and zz_ef_cm_companies.txt.\n\n")
    return head + "".join(out), n


BANK_COMPANY_SKIP = {
    "company_private_construction", "company_basic_gold_and_silver_mining_2",
    "company_basic_silver_mining_mex", "company_basic_gold_mining_rus",
    "company_PennsylvaniaRailroad", "company_standard_oil",
}


def gen_companies(ef: Path, names: list[str]) -> tuple[str, int]:
    src = read(ef / "common/company_types/00_ef_companies.txt")
    companies = [k for k, _, _ in iter_top_blocks(src)
                 if k.startswith("company_") and k not in BANK_COMPANY_SKIP]
    goods = "\n".join(f"\t\t{n}_c" for n in names)
    out = []
    for c in companies:
        out.append(
            f"INJECT:{c} = {{\n"
            f"\tbuilding_types = {{\n"
            f"\t\tbuilding_bank\n"
            f"\t}}\n\n"
            f"\tpossible_prestige_goods = {{\n{goods}\n\t}}\n"
            f"}}\n\n"
        )
    head = (BANNER +
            f"### Source: E&F's own common/company_types/00_ef_companies.txt -- all {len(companies)}\n"
            "### of its bank companies.\n"
            "###\n"
            "### Two things per company, both INJECT: so nothing E&F wrote is overridden --\n"
            "### its building list, its prosperity modifier and its existing prestige goods\n"
            "### (manufacture_stock_gbr and the like) stay exactly as they are.\n"
            "###\n"
            "### building_bank: E&F keeps `#building_bank` commented out in every one of them.\n"
            "### It could not have worked before -- the building was no_ownership and its group\n"
            "### government funded, so no company could hold it. zz_ef_cm_bank.txt fixes that.\n"
            "###\n"
            "### All 95 prestige currencies in every company, because company -> country is not\n"
            "### derivable from the files: 6 of 103 companies name a tag, the rest go by\n"
            "### interest markers. The currency law behind each prestige good does the picking\n"
            "### instead -- see zz_ef_cm_prestige_currencies.txt.\n\n")
    return head + "".join(out), len(companies)


def gen_bank(ef: Path, private: bool) -> tuple[str, str | None]:
    """building_bank, ownable. Optionally bg_bank, no longer government funded."""
    b = next((read(ef / "common/buildings/ef_15_bank.txt")[a:c]
              for k, a, c in iter_top_blocks(read(ef / "common/buildings/ef_15_bank.txt"))
              if k == "building_bank"), None)
    if b is None or "ownership_type = no_ownership" not in b:
        raise SystemExit("building_bank: ownership_type = no_ownership not found")
    b = b.replace("ownership_type = no_ownership", "ownership_type = self", 1)
    # A company can only hold PRIVATISED levels. E&F leaves the bank at
    # ai_nationalization_desire = 0, which is exactly the privatise threshold
    # (NATIONALIZATION_DESIRE_PRIVATIZE_THRESHOLD = 0.0, nationalise at >= 1.0) --
    # right on the line, so an AI country may or may not get round to it. Pushed
    # well below the line so the private sector actually takes the bank.
    if "ai_nationalization_desire" in b:
        b = re.sub(r"ai_nationalization_desire\s*=\s*-?[0-9.]+",
                   "ai_nationalization_desire = -5", b, count=1)
    b = "REPLACE:" + b
    head = (BANNER +
            "### Source: E&F's own common/buildings/ef_15_bank.txt, one field changed:\n"
            "###   ownership_type = no_ownership  ->  ownership_type = self\n"
            "###\n"
            "### THE WHOLE DEFINITION IS RESTATED, and it has to be. REPLACE: replaces the\n"
            "### entire entry, not the fields a mod names -- shipping just the one line made\n"
            "### the central bank vanish from the game, because nothing else was left of it.\n"
            "###\n"
            "### Why the field has to change at all: a company can only produce a prestige good\n"
            "### from a building it owns, and no_ownership means the building has no ownership\n"
            "### shares to hold.\n"
            "###\n"
            "### ai_nationalization_desire is also pushed from 0 to -5. Ownership shares alone\n"
            "### are not enough: E&F creates the bank state-owned, and a company can only hold\n"
            "### PRIVATISED levels. 0 sits exactly on the engine's privatise threshold\n"
            "### (NATIONALIZATION_DESIRE_PRIVATIZE_THRESHOLD = 0.0, nationalise at >= 1.0), so\n"
            "### an AI country was as likely to leave it alone as to sell it. -5 is clear of the\n"
            "### line. A human player still has to press privatise once.\n"
            "###\n"
            "### AND THAT IS A DESIGN DECISION, NOT A FIX. A privatised central bank pays its\n"
            "### dividends to its owners instead of the treasury -- on the 1836 British save\n"
            "### that is about 6K a month leaving the budget. Whether the central bank SHOULD be\n"
            "### private is a question about the mod, not about the engine.\n\n")
    bank = head + b + "\n"

    group = None
    if private:
        g = next((read(ef / "common/building_groups/00_ef_building_groups.txt")[a:c]
                  for k, a, c in iter_top_blocks(read(ef / "common/building_groups/00_ef_building_groups.txt"))
                  if k == "bg_bank"), None)
        if g is None or "is_government_funded = yes" not in g:
            raise SystemExit("bg_bank: is_government_funded = yes not found")
        g = "REPLACE:" + g.replace("is_government_funded = yes", "is_government_funded = no", 1)
        ghead = (BANNER +
                 "### Source: E&F's own common/building_groups/00_ef_building_groups.txt,\n"
                 "### one field changed:\n"
                 "###   is_government_funded = yes  ->  is_government_funded = no\n"
                 "###\n"
                 "### EMITTED ONLY UNDER --private-bank, and it is not a free switch.\n"
                 "###\n"
                 "### is_government_funded means the treasury pays the building's inputs and\n"
                 "### wages and takes its output -- the government expenditure line in the\n"
                 "### building panel. Off, the central bank is an ordinary private business, and\n"
                 "### on a 1836 British save it makes 200 bonds plus currency against about 2.5K\n"
                 "### of inputs and wages. As a government building that gap is state spending;\n"
                 "### as a private one it is profit, dividends and investment-pool inflow, every\n"
                 "### month, for whoever owns the central bank.\n"
                 "###\n"
                 "### Turn this on only if ownership does not work without it, and then watch\n"
                 "### the investment pool rather than the ownership tab.\n\n")
        group = ghead + g + "\n"
    return bank, group


# --- the central bank company always exists ---------------------------------


def gen_upkeep(ef: Path) -> dict[str, str]:
    """Every country with a central bank has a bank company, and cannot lose it.

    Three things the engine has no single switch for:

      * spawn it -- `add_company` on a pulse, for any country that owns a central
        bank and has no bank company yet;
      * do not charge a slot for it -- a country modifier with
        country_max_companies_add = 1 while the central bank stands;
      * make it undeletable -- there is no such flag, so it is imitated: delete it
        and the monthly pass puts it back.

    The flavoured company wins where E&F has one. It cannot be picked FOR the
    country -- company -> tag is not in the files, 6 of 103 name a tag -- so the
    generic one is granted and steps aside on its own: the moment the country holds
    any of E&F's 96 flavoured bank companies, company_BasicBank is removed.

    Everything is additive. on_actions stack, GLOBAL blocks stack, the modifier and
    the triggers are new keys. Nothing of E&F's is overridden.
    """
    src = read(ef / "common/company_types/00_ef_companies.txt")
    companies = [k for k, _, _ in iter_top_blocks(src)
                 if k.startswith("company_") and k not in BANK_COMPANY_SKIP]
    flavoured = [c for c in companies if c != "company_BasicBank"]
    types = "\n".join(f"\t\t\tis_company_type = company_type:{c}" for c in flavoured)

    triggers = (BANNER +
                "### Source: the bank companies in E&F's own 00_ef_companies.txt.\n\n"
                "### Does this country hold one of E&F's flavoured bank companies -- Bank of\n"
                "### England, State Bank of the Russian Empire and the other " + str(len(flavoured)) + "?\n"
                "zz_ef_cm_has_flavoured_bank_company = {\n"
                "\tany_company = {\n"
                "\t\tOR = {\n" + types + "\n\t\t}\n\t}\n}\n\n"
                "zz_ef_cm_has_bank_company = {\n"
                "\tOR = {\n"
                "\t\thas_company = company_type:company_BasicBank\n"
                "\t\tzz_ef_cm_has_flavoured_bank_company = yes\n"
                "\t}\n}\n\n"
                "### The central bank is a state building placed by E&F, not something anyone\n"
                "### builds, so ownership of it is the only honest test for \"has a central bank\".\n"
                "zz_ef_cm_has_central_bank = {\n"
                "\tany_scope_state = {\n"
                "\t\thas_building = building_bank\n"
                "\t}\n}\n")

    effects = (BANNER +
               "### Keep the central bank company alive.\n"
               "###\n"
               "### ORDER MATTERS AND IT COST A ROUND TO FIND OUT. The slot has to be granted\n"
               "### BEFORE add_company, not after. Finland owns a central bank and no company\n"
               "### slots at all in 1836 -- add_company simply had nowhere to put the company,\n"
               "### and the +1 arrived a line too late to help. Same on the game-start pass.\n"
               "###\n"
               "### This is the safety net, not the main road. The company that owns a central\n"
               "### bank is chosen when the bank is built -- zz_ef_cm_create_owned_bank -- and\n"
               "### this pass only catches countries that ended up with a central bank and no\n"
               "### bank company at all, from a spawn path that was not rewritten.\n"
               "###\n"
               "### There is deliberately no remove_company here any more. Withdrawing\n"
               "### company_BasicBank in favour of a flavoured company would strip the central\n"
               "### bank of its owner, and nothing in the game can hand those levels to the\n"
               "### replacement: add_ownership only exists inside create_building. The flavoured\n"
               "### company now wins by being picked first, at creation, instead of afterwards.\n\n"
               "zz_ef_cm_bank_company_upkeep = {\n"
               "\t### 1. The slot first.\n"
               "\tif = {\n"
               "\t\tlimit = {\n"
               "\t\t\tzz_ef_cm_has_central_bank = yes\n"
               "\t\t\tNOT = { has_modifier = zz_ef_cm_central_bank_charter }\n"
               "\t\t}\n"
               "\t\tadd_modifier = zz_ef_cm_central_bank_charter\n"
               "\t}\n"
               "\tif = {\n"
               "\t\tlimit = {\n"
               "\t\t\thas_modifier = zz_ef_cm_central_bank_charter\n"
               "\t\t\tNOT = { zz_ef_cm_has_central_bank = yes }\n"
               "\t\t}\n"
               "\t\tremove_modifier = zz_ef_cm_central_bank_charter\n"
               "\t}\n\n"
               "\t### 2. Then the company.\n"
               "\tif = {\n"
               "\t\tlimit = {\n"
               "\t\t\tzz_ef_cm_has_central_bank = yes\n"
               "\t\t\tNOT = { zz_ef_cm_has_bank_company = yes }\n"
               "\t\t}\n"
               "\t\tadd_company = company_type:company_BasicBank\n"
               "\t}\n\n"
               "\t### 3. And the monopoly on central banks goes to whoever holds it.\n"
               "\tif = {\n"
               "\t\tlimit = { zz_ef_cm_has_central_bank = yes }\n"
               "\t\tzz_ef_cm_bank_monopoly = yes\n"
               "\t}\n"
               "}\n")

    on_actions = (BANNER +
                  "### on_actions are additive across mods -- E&F, T&R and the Morgenroete\n"
                  "### compatch all append to on_monthly_pulse_country and so does this.\n\n"
                  "on_monthly_pulse_country = {\n"
                  "\ton_actions = {\n"
                  "\t\tzz_ef_cm_on_monthly_pulse_country\n"
                  "\t}\n}\n\n"
                  "zz_ef_cm_on_monthly_pulse_country = {\n"
                  "\teffect = {\n"
                  "\t\tzz_ef_cm_bank_company_upkeep = yes\n"
                  "\t}\n}\n")

    init = (BANNER +
            "### The monthly pulse does not fire until a month into the campaign, so without\n"
            "### this every central bank in the world spends 1836 without its company. GLOBAL\n"
            "### blocks stack and `zz_` runs after E&F's `99_`, so this appends and overrides\n"
            "### nothing -- the same shape as the E&F hotfix's own currency init.\n\n"
            "GLOBAL = {\n"
            "\tevery_country = {\n"
            "\t\tzz_ef_cm_bank_company_upkeep = yes\n"
            "\t}\n}\n")

    modifier = (BANNER +
                "### Gives back the company slot the central bank company sits in.\n"
                "###\n"
                "### company_BasicBank already carries country_max_companies_add = 1, but inside\n"
                "### its prosperity_modifier -- that is, only once the company is prosperous, and\n"
                "### only for the generic one. This is unconditional and applies to the\n"
                "### flavoured companies too.\n"
                "###\n"
                "### country_free_charters_add pays for the monopoly patent the player is meant to\n"
                "### hand this company. Vanilla's monopoly_charter (00_company_charter_types.txt)\n"
                "### has no `possible` block and no cooldown, so it can be granted from the first\n"
                "### day; this only makes it free instead of spending one of the country's four.\n"
                "### The charter still has to be clicked -- the game has no script effect for\n"
                "### granting one, only the player action and the AI's ai_possible / ai_weight\n"
                "### (which the bank company passes once prosperous and producing its currency).\n\n"
                "zz_ef_cm_central_bank_charter = {\n"
                "\ticon = gfx/interface/icons/timed_modifier_icons/modifier_gear_positive.dds\n"
                "\tcountry_max_companies_add = 1\n"
                "\tcountry_free_charters_add = 1\n"
                "}\n")

    return {
        "common/scripted_triggers/zz_ef_cm_company_triggers.txt": triggers,
        "common/scripted_effects/zz_ef_cm_company_effects.txt": effects,
        "common/on_actions/zz_ef_cm_on_actions.txt": on_actions,
        "common/history/global/zz_ef_cm_init.txt": init,
        "common/static_modifiers/zz_ef_cm_company_modifier.txt": modifier,
    }


# --- the central bank is born owned ----------------------------------------

# tag -> the flavoured E&F bank company that IS that country's central bank.
#
# Every pair here is taken from E&F's own establish_bank_and_ef_compagnie, which
# grants each flavoured bank company to a hardcoded tag -- so company -> country
# IS derivable after all, just not from the company definitions (6 of 103 name a
# tag there). What is not derivable is which of a country's several banks is the
# central one: Britain gets six, Barclays among them, and the earliest founding
# date picks Barclays (1690) over the Bank of England (1694). Hence a table.
#
# A country missing from here, or holding its entry too early to have it yet
# (Germany's Reichsbank is 1876, its central bank is built in 1836), falls back
# to company_BasicBank, which uses dynamic naming and so reads as a real bank.
# Values may be a single company or a priority list: the first one the country
# actually holds wins. Germany is the reason -- the Reichsbank is its central bank
# but only from 1876, and the Preussische Seehandlung (1772) is the honest stand-in
# before that.
CENTRAL_BANK_COMPANY = {
    "GBR": "company_BankofEngland",
    "FRA": "company_BanqueDeFrance",
    "RUS": "company_StateBankRussianEmpire",
    "GER": ["company_Reichsbank", "company_PreussischeSeehandlung"],
    "AUS": "company_OesterreichischeNationalbank",
    "NGF": ["company_PreussischeSeehandlung"],
    "NET": "company_DeNederlandscheBank",
    "BEL": "company_BanqueNationaleDeBelgique",
    "SPA": "company_BankofSpain",
    "POR": "company_BancoDePortugal",
    "ITA": ["company_BancaDItalia", "company_Rothschild_Bank_ita"],
    "SAR": "company_CassaDiRisparmioDiTorino",
    "BAV": "company_BayerischeHypothekenUndWechselBank",
    "SWI": "company_Bankenverein",
    "SWE": "company_HandelsBanken",
    "DEN": "company_LandmandsBanken",
    "NOR": "company_ChristianiaBank",
    "GRE": "company_bankofgreec",
    "TUR": "company_OttomanBank",
    "PER": ["company_BankMelliIran", "company_ImperialBankofPersia"],
    "EGY": "company_BanqueEgyptienne",
    "JAP": ["company_BankOfJapan", "company_Mitsubishiexchangehousebank"],
    "CHI": ["company_DaQingBank", "company_BankHSBC"],
    "BIC": "company_ImperialBankofIndia",
    "CAN": "company_CanadianImperialBankOfCommerce",
    "ONT": "company_RoyalBankofCanada",
    "QUE": "company_BankOfMontreal",
    "NSW": "company_ColonialBankOfAustralia",
    "MEX": "company_BancoDeMexico",
    "COS": "company_BancoCentralDeCostaRica",
    "GUA": "company_BancoCentralDeGuatemala",
    "HON": "company_BancoCentralDeHonduras",
    "PAN": "company_BancoNacionalDePanama",
    "BRZ": "company_BancoDoBrasil",
    "ARG": ["company_BancoNacionArgentina", "company_BancoProvincia"],
    "CHL": ["company_BancoEstado", "company_BancoDeValparaiso"],
    "BOL": "company_BancoNacionalDeBolivia",
    "CLM": "company_BancoRepublicaColombia",
    "VNZ": "company_BancoCentralDeVenezuela",
    "CUB": "company_BancoEspanolDeLaHabana",
    "URU": "company_BancoCentralDelUruguay",
    "PRG": "company_BancoNacionalDelParaguay",
    "SAF": "company_BankSBoBSA",
    # USA is deliberately absent: E&F ships JP Morgan, Goldman Sachs, Chase,
    # Wells Fargo and American Express, and not one of them is a central bank.
}

SPAWN_FILE = "common/scripted_effects/09_introduction_building_lvl.txt"
ESTABLISH_FILE = "common/scripted_effects/01_financial_scripted_effects.txt"

# The three E&F effects that call create_building on the central bank. Every one
# of the 1003 call sites is byte-identically shaped, so one regex rewrites them
# all -- see CREATE_BANK_RE.
BANK_SPAWN_EFFECTS = [
    "initialize_historic_macro_facilities_bc",
    "macro_facilities_bc",
    "central_bank_respawn_after_crisis",
]

CREATE_BANK_RE = re.compile(
    r"create_building\s*=\s*\{\s*"
    r"building\s*=\s*\$BANK_BLDG_TYPE\$\s*"
    r"level\s*=\s*(\S+)\s*"
    r"reserves\s*=\s*1\s*\}")


def effect_body(src: str, name: str) -> str:
    """The whole `name = { ... }` block, braces matched, comments left alone."""
    i = src.index("\n" + name + " = {") + 1
    d, j = 0, i
    while True:
        c = src[j]
        if c == "{":
            d += 1
        elif c == "}":
            d -= 1
            if d == 0:
                break
        j += 1
    return src[i:j + 1]


def establish_mapping(ef: Path, only: set[str] | None = None) -> dict[str, list[str]]:
    """company -> tags, read out of E&F's establish_bank_and_ef_compagnie.

    Used only to check CENTRAL_BANK_COMPANY against E&F: if an E&F update renames
    a company or moves it to another tag, the generator says so instead of
    quietly emitting a branch that can never fire.
    """
    body = strip_comments(effect_body(read(ef / ESTABLISH_FILE),
                                      "establish_bank_and_ef_compagnie"))
    out: dict[str, list[str]] = {}
    depth, k, starts = 0, 0, []
    while k < len(body):
        c = body[k]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 1 and starts:
                blk = body[starts.pop():k + 1]
                m = re.search(r"add_company = company_type:(\w+)", blk)
                if m and (only is None or m.group(1) in only):
                    head = blk[:blk.index("add_company")]
                    out.setdefault(m.group(1), []).extend(re.findall(r"c:(\w+) \?= this", head))
        elif depth == 1 and body.startswith("if = {", k):
            starts.append(k)
        k += 1
    return out


def gen_ownership(ef: Path) -> tuple[dict[str, str], list[str]]:
    """Create the central bank already owned by its company.

    Why at creation and nowhere else: there is no effect in the game that hands an
    existing building to a company. `add_ownership` exists only as a field of
    `create_building` -- it appears 1,900 times in vanilla and every single one is
    inside a create_building, and neither effects_l_english.yml nor
    common/effect_localization/ knows any other ownership effect. Privatisation is
    the only other route, and it is the AI's decision, on its own schedule.

    So E&F's three central-bank spawners are rewritten to call one dispatcher that
    picks the company first and creates the building owned by it.
    """
    notes: list[str] = []
    # The effect grants E&F's industrial companies too (Krupp, Ganz, Skoda...);
    # only the bank ones are relevant, and only they carry a tag worth reading.
    banks = {k for k, _, _ in iter_top_blocks(read(ef / "common/company_types/00_ef_companies.txt"))
             if k.startswith("company_") and k not in BANK_COMPANY_SKIP}
    mapping = establish_mapping(ef, banks)
    table = {t: ([c] if isinstance(c, str) else list(c))
             for t, c in CENTRAL_BANK_COMPANY.items()}
    for tag, comps in sorted(table.items()):
        for comp in comps:
            if comp not in mapping:
                notes.append(f"WARNING {comp}: E&F no longer grants it anywhere")
            elif tag not in mapping[comp]:
                notes.append(f"WARNING {comp}: E&F grants it to {mapping[comp]}, not {tag}")
    covered = {t for tags in mapping.values() for t in tags}
    for tag in sorted(covered - set(CENTRAL_BANK_COMPANY) - {"USA"}):
        notes.append(f"note: {tag} has E&F bank companies but no central bank in the table "
                     f"-> company_BasicBank")

    branches = []
    for tag, comps in sorted(table.items()):
      for comp in comps:
        branches.append(
            f"\t{'if' if not branches else 'else_if'} = {{\n"
            f"\t\tlimit = {{\n"
            f"\t\t\tscope:zz_ef_cm_bank_owner = {{\n"
            f"\t\t\t\tc:{tag} ?= this\n"
            f"\t\t\t\thas_company = company_type:{comp}\n"
            f"\t\t\t}}\n"
            f"\t\t}}\n"
            f"\t\tcreate_building = {{\n"
            f"\t\t\tbuilding = $BANK_BLDG_TYPE$\n"
            f"\t\t\tlevel    = $CB_SIZE$\n"
            f"\t\t\treserves = 1\n"
            f"\t\t\tadd_ownership = {{\n"
            f"\t\t\t\tcompany = {{\n"
            f"\t\t\t\t\ttype    = {comp}\n"
            f"\t\t\t\t\tcountry = \"c:{tag}\"\n"
            f"\t\t\t\t\tlevels  = $CB_SIZE$\n"
            f"\t\t\t\t}}\n"
            f"\t\t\t}}\n"
            f"\t\t}}\n"
            f"\t}}\n")

    dispatch = (BANNER +
                "### Source: the tag -> company pairs in E&F's own\n"
                "### establish_bank_and_ef_compagnie (01_financial_scripted_effects.txt).\n"
                "###\n"
                "### WHY THIS EXISTS\n"
                "###\n"
                "### There is no effect in the game that gives an existing building to a company.\n"
                "### add_ownership is a field of create_building and nothing else -- all ~1900\n"
                "### uses in vanilla are inside one, and no ownership effect appears in\n"
                "### effects_l_english.yml or common/effect_localization/. The only other route\n"
                "### into company hands is privatisation, which is the AI's call and its timing.\n"
                "### That is why the central bank had to be born owned instead of handed over.\n"
                "###\n"
                "### State scope. $CB_SIZE$ and $BANK_BLDG_TYPE$ come straight through from\n"
                "### whichever E&F spawner called it.\n"
                "###\n"
                "### $BANK_BLDG_TYPE$ IS PASSED ON PURPOSE, even though every caller sets it to\n"
                "### building_bank and this could name the building directly. An argument the\n"
                "### callers pass and the effect does not use is a fatal compile error, not a\n"
                "### warning, and it takes the whole effect down with it:\n"
                "###\n"
                "###   [jomini_script_argument.cpp:182]: Compiling source for failed for unknown\n"
                "###   arguments: BANK_BLDG_TYPE. At\n"
                "###   common/scripted_effects/09_introduction_building_lvl.txt:23498\n"
                "###\n"
                "### The result was every central bank in the world missing at game start, and\n"
                "### not one line about it in error.log -- it is in debug.log.\n\n"
                "zz_ef_cm_create_owned_bank = {\n"
                "\towner = {\n"
                "\t\tsave_scope_as = zz_ef_cm_bank_owner\n"
                "\t}\n\n" +
                "".join(branches) +
                "\telse = {\n"
                "\t\t### No flavoured central bank, or the country does not hold it yet --\n"
                "\t\t### Germany's Reichsbank is 1876 and its central bank is built in 1836.\n"
                "\t\t### company_BasicBank has uses_dynamic_naming, so it comes out as a named\n"
                "\t\t### bank rather than a placeholder. The slot is granted first: a country\n"
                "\t\t### with no free company slot -- Finland in 1836 -- cannot take one.\n"
                "\t\tscope:zz_ef_cm_bank_owner = {\n"
                "\t\t\tif = {\n"
                "\t\t\t\tlimit = { NOT = { has_modifier = zz_ef_cm_central_bank_charter } }\n"
                "\t\t\t\tadd_modifier = zz_ef_cm_central_bank_charter\n"
                "\t\t\t}\n"
                "\t\t\tif = {\n"
                "\t\t\t\tlimit = { NOT = { has_company = company_type:company_BasicBank } }\n"
                "\t\t\t\tadd_company = company_type:company_BasicBank\n"
                "\t\t\t}\n"
                "\t\t}\n"
                "\t\tif = {\n"
                "\t\t\tlimit = {\n"
                "\t\t\t\tscope:zz_ef_cm_bank_owner = {\n"
                "\t\t\t\t\thas_company = company_type:company_BasicBank\n"
                "\t\t\t\t}\n"
                "\t\t\t}\n"
                "\t\t\tcreate_building = {\n"
                "\t\t\t\tbuilding = $BANK_BLDG_TYPE$\n"
                "\t\t\t\tlevel    = $CB_SIZE$\n"
                "\t\t\t\treserves = 1\n"
                "\t\t\t\tadd_ownership = {\n"
                "\t\t\t\t\tcompany = {\n"
                "\t\t\t\t\t\ttype    = company_BasicBank\n"
                "\t\t\t\t\t\tcountry = scope:zz_ef_cm_bank_owner\n"
                "\t\t\t\t\t\tlevels  = $CB_SIZE$\n"
                "\t\t\t\t\t}\n"
                "\t\t\t\t}\n"
                "\t\t\t}\n"
                "\t\t}\n"
                "\t\telse = {\n"
                "\t\t\t### LAST RESORT, AND IT EXISTS FOR A REASON. This is E&F's own line,\n"
                "\t\t\t### untouched. When the dispatcher failed the first time, every central\n"
                "\t\t\t### bank in the world simply stopped existing -- there was no path left\n"
                "\t\t\t### that just builds the thing. A state-owned bank beats no bank.\n"
                "\t\t\tcreate_building = {\n"
                "\t\t\t\tbuilding = $BANK_BLDG_TYPE$\n"
                "\t\t\t\tlevel    = $CB_SIZE$\n"
                "\t\t\t\treserves = 1\n"
                "\t\t\t}\n"
                "\t\t}\n"
                "\t}\n"
                "}\n")

    src = read(ef / SPAWN_FILE)
    rewritten, total = [], 0
    for name in BANK_SPAWN_EFFECTS:
        body = effect_body(src, name)
        body, n = CREATE_BANK_RE.subn(
            lambda m: ("zz_ef_cm_create_owned_bank = { BANK_BLDG_TYPE = $BANK_BLDG_TYPE$ "
                       "CB_SIZE = %s }" % m.group(1)), body)
        if n == 0:
            notes.append(f"WARNING {name}: no create_building rewritten -- E&F changed its shape")
        total += n
        rewritten.append(override_keys(body))
    notes.append(f"central bank spawn sites rewritten: {total}")

    override = (BANNER +
                f"### Source: E&F's own {SPAWN_FILE}, three effects taken verbatim with every\n"
                "### create_building of the central bank replaced by zz_ef_cm_create_owned_bank.\n"
                "###\n"
                "### REPLACE_OR_CREATE: is what makes these three override E&F's -- repeating\n"
                "### the key in a later file does nothing on its own, and the first round of\n"
                "### this was silently inert for exactly that reason (see the note next to\n"
                "### OVERRIDE in the generator). They are copied rather than edited by hand\n"
                "### because\n"
                "### macro_facilities_bc alone is 12,000 lines and 1,001 of those call sites --\n"
                "### a switch over gdp_view crossed with the country list. All 1,001 are shaped\n"
                "### identically, which is what makes one regex enough.\n"
                "###\n"
                "### $BANK_BLDG_TYPE$ is dropped on the way: every call site in E&F passes\n"
                "### building_bank, and the dispatcher has to name the building type literally\n"
                "### anyway because add_ownership needs a company that can own that type.\n\n"
                + "\n\n".join(rewritten) + "\n")

    return {
        "common/scripted_effects/zz_ef_cm_bank_ownership.txt": dispatch,
        "common/scripted_effects/zz_ef_cm_bank_spawn.txt": override,
    }, notes


# --- the monopoly on central banks ------------------------------------------


def gen_monopoly(ef: Path) -> str:
    """Give the bank company a company monopoly on building_bank.

    UNVERIFIED SYNTAX -- read error.log after the first run with this.
    Nothing in vanilla or in any of the mods here calls these, so the shape is
    inferred rather than copied:

      * common/effect_localization/00_country_effects_loc.txt names three effects
        -- add_company_monopoly, add_country_monopoly, remove_monopoly;
      * their loc strings are "[COMPANY.GetName] gains a company monopoly on
        [TARGET_BUILDING_TYPE.GetName]" and the `first` slot is COMPANY, which is
        how effect_localization marks the scope the effect runs in -- so
        add_company_monopoly is a COMPANY-scope effect taking a building type;
      * building types are addressed as `bt:building_x`, the one confirmed piece:
        common/achievements/mp1_charters_of_commerce_achievements.txt:146 has
        `country_has_building_type_monopoly = bt:building_food_industry`.

    If the game rejects it, it is one effect in one file and nothing else breaks.

    Which company gets it: company_BasicBank first, because in this mod that
    company exists only as the owner of a central bank -- it is granted when the
    bank is built and never withdrawn. Otherwise the country's own central bank
    company, in the same order zz_ef_cm_create_owned_bank picks it, so the
    monopoly and the ownership land on the same company.
    """
    table = {t: ([c] if isinstance(c, str) else list(c))
             for t, c in CENTRAL_BANK_COMPANY.items()}

    def branch(kind: str, guard: str, comp: str) -> str:
        return (f"\t{kind} = {{\n"
                f"\t\tlimit = {{\n"
                f"{guard}"
                f"\t\t\tcompany:{comp} = {{\n"
                f"\t\t\t\tNOT = {{ company_has_building_type_monopoly = bt:building_bank }}\n"
                f"\t\t\t}}\n"
                f"\t\t}}\n"
                f"\t\tcompany:{comp} = {{\n"
                f"\t\t\tadd_company_monopoly = bt:building_bank\n"
                f"\t\t}}\n"
                f"\t}}\n")

    out = [branch("if", "\t\t\thas_company = company_type:company_BasicBank\n", "company_BasicBank")]
    for tag, comps in sorted(table.items()):
        for comp in comps:
            out.append(branch("else_if",
                              f"\t\t\tc:{tag} ?= this\n"
                              f"\t\t\thas_company = company_type:{comp}\n",
                              comp))

    return (BANNER +
            "### Source: the same tag -> company table as zz_ef_cm_bank_ownership.txt.\n"
            "###\n"
            "### SYNTAX NOT CONFIRMED IN GAME. add_company_monopoly and\n"
            "### company_has_building_type_monopoly are named in vanilla's\n"
            "### effect_localization / trigger_localization but called from nowhere in\n"
            "### vanilla or in any mod in this repo, so their shape is read off the loc\n"
            "### strings: ADD_COMPANY_MONOPOLY_FIRST is \"[COMPANY.GetName] gains a company\n"
            "### monopoly on [TARGET_BUILDING_TYPE.GetName]\", and a `first` slot of COMPANY is\n"
            "### how effect_localization marks the scope an effect runs in -- hence company\n"
            "### scope, one building type as the value. `bt:building_bank` is the one\n"
            "### confirmed part (mp1_charters_of_commerce_achievements.txt:146).\n"
            "###\n"
            "### CHECK error.log AFTER THE FIRST RUN. Kept in its own file so that if the\n"
            "### game rejects it, nothing else in the mod goes down with it.\n"
            "###\n"
            "### This is the direct grant. The +1 free charter on\n"
            "### zz_ef_cm_central_bank_charter stays either way: it is what lets the player\n"
            "### hand the company a monopoly charter without spending one of the country's\n"
            "### four, which is the route the game itself offers.\n\n"
            "zz_ef_cm_bank_monopoly = {\n" + "".join(out) + "}\n")


# --- self-check -------------------------------------------------------------

# Words that can only appear as a top-level key by accident -- they are sub-block
# names. Seeing one means a sweep grabbed nested blocks, which is a database parse
# error and kills the game before the main menu. This list is the tripwire.
NEVER_TOP_LEVEL = {
    "value", "add", "subtract", "multiply", "divide", "min", "max", "if", "else",
    "else_if", "limit", "trigger", "modifier", "building_modifiers",
    "country_modifiers", "state_modifiers", "workforce_scaled", "level_scaled",
    "unscaled", "entry", "goods", "every_country", "every_scope_state",
    "any_scope_state", "set_variable", "change_variable", "production_methods",
    "production_method_groups", "possible", "potential",
}


def validate(mod: Path) -> int:
    """Structural pass over everything we just wrote. Cheap, and it has already
    caught two crashes that files-look-fine-to-me did not."""
    problems = 0
    for path in sorted(mod.rglob("*")):
        if path.suffix not in (".txt", ".yml") or not path.is_file():
            continue
        if SRC_DIR in path.parts:
            continue
        text = path.read_text(encoding="utf-8-sig")
        if path.suffix == ".yml":
            continue

        # braces, comment-aware
        try:
            keys = [k for k, _, _ in iter_top_blocks(text)]
        except ValueError as e:
            print(f"  BROKEN  {path.name}: {e}")
            problems += 1
            continue

        bad = sorted(set(keys) & NEVER_TOP_LEVEL)
        if bad:
            print(f"  BROKEN  {path.name}: sub-block names at top level: {bad}")
            problems += 1

        dupes = sorted({k for k in keys if keys.count(k) > 1})
        if dupes:
            print(f"  BROKEN  {path.name}: duplicate top-level keys: {dupes[:5]}")
            problems += 1

        stray = re.sub(r"[^{}]", "", strip_comments(text))
        if stray.count("{") != stray.count("}"):
            print(f"  BROKEN  {path.name}: unbalanced braces outside comments")
            problems += 1
    return problems


# --- main -------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    ap.add_argument("--keep", default="spe_uni_c")
    ap.add_argument("--private-bank", action="store_true",
                    help="also drop is_government_funded from bg_bank -- see the file it emits")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    ef, hf, mod = args.out_root / EF, args.root / HOTFIX, args.root / MOD
    for p in (ef, hf):
        if not p.is_dir():
            print(f"missing: {p}", file=sys.stderr)
            return 2

    active, commented_out, dead_list, names = inventory(ef, hf, args.keep)
    dead = set(dead_list)
    rt = Retarget(dead_list, args.keep)
    print(f"currencies: {len(names)} laws/PMs, {len(active)} live goods, "
          f"{len(commented_out)} to comment out, {len(dead)} references to retarget, "
          f"keeping {args.keep}")
    acc: list[bool] = []

    emit(mod / GOODS_FILE, gen_goods(read(hand_written(hf, GOODS_FILE)), commented_out, args.keep),
         args.check, acc)

    text, n = gen_popneed(read(hand_written(hf, POPNEED_FILE)), dead, args.keep)
    print(f"     pop-need entries dropped: {n}")
    emit(mod / POPNEED_FILE, text, args.check, acc)

    text, n = gen_modtypes(read(ef / MODTYPE_FILE), dead)
    print(f"     modifier types dropped: {n}")
    emit(mod / MODTYPE_FILE, text, args.check, acc)

    for f in STATIC_FILES:
        text, notes = gen_static(read(ef / f), f, dead, args.keep)
        for x in dict.fromkeys(notes):
            print(f"     {Path(f).stem}: {x}")
        emit(mod / f, text, args.check, acc)

    text, n = gen_colors(read(ef / COLORS_FILE), dead)
    print(f"     goods colours dropped: {n}")
    emit(mod / COLORS_FILE, text, args.check, acc)

    text, n, missing = gen_pms(ef, names, rt)
    print(f"     production methods retargeted: {n}" + (f", missing in E&F: {missing}" if missing else ""))
    emit(mod / "common/production_methods/zz_ef_cm_production_methods.txt", text, args.check, acc)

    text, n = gen_values(ef, rt)
    print(f"     script values retargeted: {n}")
    emit(mod / "common/script_values/zz_ef_cm_script_values.txt", text, args.check, acc)

    emit(mod / "common/scripted_triggers/zz_ef_cm_scripted_triggers.txt",
         gen_triggers(ef, dead, args.keep), args.check, acc)

    text, n = gen_prestige(ef, names, args.keep)
    print(f"     prestige currencies: {n}")
    emit(mod / "common/prestige_goods/zz_ef_cm_prestige_currencies.txt", text, args.check, acc)

    text, n = gen_companies(ef, names)
    print(f"     bank companies wired: {n}")
    emit(mod / "common/company_types/zz_ef_cm_companies.txt", text, args.check, acc)

    bank, group = gen_bank(ef, args.private_bank)
    emit(mod / "common/buildings/zz_ef_cm_bank.txt", bank, args.check, acc)
    gpath = mod / "common/building_groups/zz_ef_cm_bank_group.txt"
    if group is not None:
        emit(gpath, group, args.check, acc)
    elif gpath.exists() and not args.check:
        gpath.unlink()
        print("  removed    zz_ef_cm_bank_group.txt (no --private-bank)")

    emit(mod / "common/scripted_effects/zz_ef_cm_bank_monopoly.txt", gen_monopoly(ef), args.check, acc)

    files, notes = gen_ownership(ef)
    for x in notes:
        print(f"     {x}")
    for rel, text in files.items():
        emit(mod / rel, text, args.check, acc)

    for rel, text in gen_upkeep(ef).items():
        emit(mod / rel, text, args.check, acc)

    for lang, text in gen_loc(args.keep).items():
        emit(mod / f"localization/{lang}/zz_ef_cm_goods_l_{lang}.yml", text, args.check, acc)

    if not args.check:
        print("self-check:")
        problems = validate(mod)
        print("  ok" if not problems else f"  {problems} problem(s) -- DO NOT LOAD")
        if problems:
            return 3

    if args.check and any(acc):
        print("\ndrift detected -- rerun without --check")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
