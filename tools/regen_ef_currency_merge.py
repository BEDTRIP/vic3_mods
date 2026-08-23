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

# Goods merged into the shared currency good that are NOT one of the 95 currency
# laws, and so are invisible to the inventory below.
#
# local_currency is E&F's money for the ~600 countries with no monetary system. It
# was a second currency on the belt at its own, lower price, and any currency
# satisfies popneed_currency -- so pops in real nations covered their currency need
# with somebody else's cheap local money instead of their own. The hotfix already
# fought that by recomputing how much of it gets issued; merging it removes the
# cause instead of the symptom, because there is no longer a cheaper currency to
# switch to. It is the same good at the same price.
#
# It also gives a goods slot back, and frees its icon -- which spe_uni_c now wears,
# since "the plain money everyone makes" is exactly what it is.
MERGED_EXTRA = ["local_currency"]

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

    # Goods merged in that do not end in _c and so are not in `active`.
    live = top_keys(read(goods_src))
    extra = [g for g in MERGED_EXTRA if g in live]
    missing = [g for g in MERGED_EXTRA if g not in live]
    if missing:
        raise SystemExit(f"MERGED_EXTRA: {missing} not found in {goods_src}")

    commented_out = [g for g in active if g != keep] + extra   # still live today
    # NOTE the parentheses: `A | B - {keep}` binds as `A | (B - {keep})` and would
    # leave the surviving good inside `dead`, which quietly deletes its own entries.
    dead = sorted(({f"{n}_c" for n in names} | set(active) | set(extra)) - {keep})
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
            f"### popneed_currency now keeps ONE entry: {keep}. local_currency was merged\n"
            "### into it and dropped with the rest, so a country with no monetary system\n"
            "### covers the same need out of the same good as everyone else -- and can no\n"
            "### longer undercut a real currency in a shared market, because there is no\n"
            "### second, cheaper currency left to undercut it with.\n"
            "###\n"
            f"### The {n} dropped entries all carried the same weights, so a pop's currency\n"
            "### need is satisfied exactly as before -- out of one good instead of 95.\n\n"
            ) + out, n


def gen_modtypes(src: str, dead: set[str]) -> tuple[str, int]:
    out, n = src, 0
    # NOT `([a-z0-9_]+_c)`. local_currency was merged in too and does not end in _c;
    # anchoring on the suffix left its two modifier types behind, pointing at a good
    # that no longer exists.
    pat = re.compile(r"^[ \t]*(?:goods_(?:input|output)|state_sell_orders)_([a-z0-9_]+?)_(?:add|mult|max_add)\s*=\s*\{", re.M)
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


def gen_static(src: str, path_name: str, dead: set[str], keep: str,
               rt: "Retarget | None" = None) -> tuple[str, list[str]]:
    """95 identical per-currency lines collapse to one line for the kept good.

    The collapse only fires on lines that are part of a per-currency LIST. A lone
    reference somewhere else in the same file is not a list and is not collapsed --
    no_money_production carries a single `state_sell_orders_local_currency_add`
    and nothing else. Those are swept at the end by the ordinary retarget, or they
    survive pointing at a good that no longer exists.
    """
    notes: list[str] = []
    out: list[str] = []
    seen: set[str] = set()
    for line in src.split("\n"):
        # The trailing `\s*$` used to be `\s*$` with no room for a comment, and E&F
        # marks the end of its currency lists with `#end_tag_1` on the same line as
        # the last entry. One line out of 95 slipped through every time.
        m = re.match(r"^([ \t]*)(goods_(?:input|output)|state_sell_orders)_([a-z0-9_]+?)_(add|mult|max_add)\s*=\s*(\S+)\s*(#.*)?$", line)
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
            ) + (rt("\n".join(out)) if rt else "\n".join(out)), notes


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


def gen_loc(keep: str, names: list[str]) -> dict[str, str]:
    """The shared good and the three regime currencies, in every language.

    English text everywhere, Russian in Russian. Every language gets a file even
    though most of them get the same words: a key with no entry for the player's
    language renders as the raw key on screen -- `zz_ef_cm_pegged_currency` -- not
    as the English name. E&F itself ships all eleven, so leaving one out is the
    one that breaks.

    The shared good is named after local_currency, which was merged into it, and
    wears its icon. That is what it is: the plain money every country makes,
    whether or not it has a monetary system. A central bank raises it to one of the
    three standard-backed variants -- and a country without a monetary system has
    no central bank, so it never gets past this.
    """
    head = {
        "english": (" # The shared currency good -- local_currency was merged into it, and this is\n"
                    " # its name and icon. Plain money; a central bank raises it to one of the\n"
                    " # three standard-backed variants below, picked by the monetary system law.\n"),
        "russian": (" # Общий товар-валюта — в него слит local_currency, отсюда имя и иконка.\n"
                    " # Просто деньги; центробанк поднимает их до одного из трёх обеспеченных\n"
                    " # вариантов ниже, а какого именно — решает закон денежной системы.\n"),
    }
    out = {}
    for lang in LANGUAGES:
        ru = lang == "russian"
        goods = NAMES_RU if ru else NAMES_EN
        extra = EXTRA_RU if ru else EXTRA_EN
        company = COMPANY_NAME_RU if ru else COMPANY_NAME_EN
        note = head.get(lang, head["english"])

        body = f' {keep}:0 "{goods[keep]}"\n\n'
        for key, _, _ in PRESTIGE_REGIMES:
            body += f' {key}:0 "{goods[key]}"\n'

        body += "\n" + (" # Модификатор, который держит слот компании и оплачивает патент.\n"
                         if ru else
                         " # The modifier that holds the company slot and pays for the patent.\n")
        for key, text in extra.items():
            body += f' {key}:0 "{text}"\n'

        body += "\n" + ((" # Компания центробанка для стран без своего исторического банка.\n"
                          " # Одна на всех: престижный товар выбирает закон денежного стандарта,\n"
                          " # а не валюта, так что 95 отдельных типов не давали ничего.\n") if ru else
                         (" # The central bank company, for countries with no historical bank of\n"
                          " # their own. One for all of them: the prestige good is chosen by the\n"
                          " # monetary standard law, not by the currency, so ninety-five separate\n"
                          " # types selected nothing.\n"))
        body += f' {GENERIC_COMPANY}:0 "{company}"\n'

        out[lang] = f"l_{lang}:\n\n" + note + "\n" + body
    return out


EF_GOODS_LOC = "localization/{lang}/01_ef_goods_localization_l_{lang}.yml"


def gen_goods_loc(ef: Path, keep: str) -> dict[str, str]:
    """Rename the shared good by OVERRIDING E&F'S OWN FILE, not by adding ours.

    LOCALISATION DOES NOT WORK LIKE THE REST OF THE MOD. Everywhere else, a later
    mod's definition of a key wins. For localisation the FIRST file to define a key
    keeps it, and load order does not save you -- so the only way to change a key
    somebody else already defined is to ship a file with the SAME NAME and let the
    path override do the work.

    That is why the shared good stayed "Uni" through three attempts. Our own
    zz_ef_cm_goods_l_*.yml works perfectly for keys nobody else defines -- the three
    regime currencies, the companies, the modifier -- and did nothing at all for
    spe_uni_c, which E&F names in 01_ef_goods_localization_l_<lang>.yml. E&F's
    Russian file spells it "Uni" in Latin too, which is why turning the Russian
    translation off changed nothing.

    The whole file is copied and one line is swapped: a path override replaces the
    file entirely, so dropping the other ~300 goods names would blank them.
    """
    out = {}
    for lang in LANGUAGES:
        src = ef / EF_GOODS_LOC.format(lang=lang)
        if not src.exists():
            continue
        text = read(src)
        name = (NAMES_RU if lang == "russian" else NAMES_EN)[keep]
        hit = 0
        lines = []
        for line in text.split("\n"):
            m = re.match(r"^(\s*)" + re.escape(keep) + r"\s*:\s*\d*\s+\".*\"\s*$", line)
            if m:
                lines.append(f'{m.group(1)}{keep}:0 "{name}"')
                hit += 1
            else:
                lines.append(line)
        if not hit:
            raise SystemExit(f"{src}: no {keep} entry to override")
        out[lang] = "\n".join(lines)
    return out


# --- prestige currencies ----------------------------------------------------


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


def currency_by_tag(ef: Path) -> dict[str, str]:
    """tag -> the currency E&F starts that country on.

    E&F's global history is one long tree of `if = { limit = { c:XXX ?= this } ...
    activate_law = law_type:law_<cur>_currency }`, 154 assignments over 73 tags.
    Read structurally, not by proximity: the tags come from the *direct* `limit`
    child of the enclosing if-block, so an activate_law nested three blocks deep
    inside a great-power branch is not misfiled to whoever was mentioned last.
    """
    src = strip_comments(read(ef / CURRENCY_LAW_FILE))
    law_re = re.compile(r"activate_law\s*=\s*law_type:(law_(\w+)_currency)\b")
    key_re = re.compile(r"(\w+)\s*=\s*\{")
    out: dict[str, str] = {}

    def walk(start: int, end: int, tags: list[str]) -> None:
        i = start
        while i < end:
            m = key_re.match(src, i)
            if m:
                open_at = src.index("{", m.start())
                close_at = block_span(src, open_at)
                key = m.group(1)
                if key == "limit":                       # already consumed by the parent
                    i = close_at + 1
                    continue
                sub = tags
                if key in ("if", "else_if", "else"):
                    lm = re.compile(r"\s*limit\s*=\s*\{").match(src, open_at + 1)
                    if lm:
                        lb = src.index("{", lm.start())
                        found = list(dict.fromkeys(TAG_IS_THIS.findall(src[lb: block_span(src, lb)])))
                        if found:
                            sub = found
                walk(open_at + 1, close_at, sub)
                i = close_at + 1
                continue
            m2 = law_re.match(src, i)
            if m2:
                for t in tags:
                    out.setdefault(t, m2.group(2))
                i = m2.end()
                continue
            i += 1

    walk(0, len(src), [])
    return out


def currency_tags(ef: Path) -> dict[str, list[str]]:
    """currency -> the tags E&F starts on it. The inverse of currency_by_tag."""
    out: dict[str, list[str]] = {}
    for tag, cur in currency_by_tag(ef).items():
        out.setdefault(cur, []).append(tag)
    for cur in out:
        out[cur].sort()
    return out


BANK_COMPANY_SKIP = {
    "company_private_construction", "company_basic_gold_and_silver_mining_2",
    "company_basic_silver_mining_mex", "company_basic_gold_mining_rus",
    "company_PennsylvaniaRailroad", "company_standard_oil",
}
CURRENCY_LAW_FILE = "common/history/global/99_ef_history_global_variable.txt"
GENERIC_BANK = "zz_ef_cm_bank_"

NATIONAL_CURRENCY = "zz_ef_cm_national_currency"

# The three prestige currencies, one per monetary regime.
#
# THREE IS THE CEILING, MEASURED. Only the first three declarations of a base
# good's prestige variants become real slots; anything past them falls back to the
# third. Three declared -> Britain minted the pound, France the franc, everyone
# else the generic one, all correct. Ten declared -> Britain kept the pound and
# every other country minted the FRANC, the third declaration. Ninety-five
# declared -> the whole world minted the Iraqi dinar, again the third. Vanilla
# never exceeds three either: of its 40 base goods with prestige variants, 17 have
# one, 14 two, 9 three, none four. No define controls it.
#
# So the three slots go to the three monetary regimes instead of to three
# arbitrary countries. Every central bank company carries all three and the good's
# own `possible` picks which one applies.
#
# THAT `possible` IS THE OPEN QUESTION THIS BUILD ANSWERS. It was tried once
# before, with `has_law = law_type:law_<cur>_currency` on 95 goods, and every
# country minted the same one -- but that test was ruined by the count, not by the
# gate, and the gate was removed before it was ever tried at three. Vanilla only
# ever writes has_dlc_feature here, so the files cannot settle whether it is
# evaluated in country scope. If it is, a country switching its monetary system
# law switches currency by itself, with no company change and no rebuild.
#
# law_no_monetary_system is deliberately absent: a country without a monetary
# system has no central bank, so nothing mints anything.
MAX_BANK_LEVEL = 100

GENERIC_COMPANY = "zz_ef_cm_central_bank"
CENTRAL_BANK_ICON = "gfx/interface/icons/building_icons/banks/central_bank.dds"

PRESTIGE_REGIMES = [
    ("zz_ef_cm_representative_currency",
     ["law_gold_standard", "law_silver_standard", "law_bimetallism_standard"],
     "gfx/interface/icons/goods_icons/currencies/zz_ef_cm_representative_currency.dds"),
    ("zz_ef_cm_pegged_currency",
     ["law_gold_exchange_standard", "law_external_exchange_standard"],
     "gfx/interface/icons/goods_icons/currencies/zz_ef_cm_pegged_currency.dds"),
    ("zz_ef_cm_fiat_currency",
     ["law_fiat_standard"],
     "gfx/interface/icons/goods_icons/currencies/spe_uni.dds"),
]

# Every language the game ships. English text in all of them, Russian in Russian --
# a missing key falls back to the raw key on screen, not to English, so a language
# left out would show `zz_ef_cm_pegged_currency` to that player.
LANGUAGES = ["braz_por", "english", "french", "german", "japanese", "korean",
             "polish", "russian", "simp_chinese", "spanish", "turkish"]

NAMES_EN = {
    "spe_uni_c": "Local Currency",
    "zz_ef_cm_representative_currency": "Representative Currency",
    "zz_ef_cm_pegged_currency": "Pegged Currency",
    "zz_ef_cm_fiat_currency": "Fiat Currency",
}
NAMES_RU = {
    "spe_uni_c": "Местная валюта",
    "zz_ef_cm_representative_currency": "Обеспеченная валюта",
    "zz_ef_cm_pegged_currency": "Привязанная валюта",
    "zz_ef_cm_fiat_currency": "Фиатная валюта",
}

# Everything else this mod puts on screen. A key with no entry renders as the raw
# key -- the company panel read ZZ_EF_CM_BANK_DOLLAR_UNITED_STATES_DOLLAR and the
# modifier tooltip read "+1 from zz_ef_cm_central_bank_charter" until these existed.
#
# The 95 generated companies all share one type name on purpose. Only one of them is
# ever visible to a country -- `potential` gates them on the currency law -- so there
# is nothing to tell apart, and the name the player actually sees is the generated
# one anyway. This is the label under it.
EXTRA_EN = {
    "zz_ef_cm_central_bank_charter": "Central Bank Charter",
}
EXTRA_RU = {
    "zz_ef_cm_central_bank_charter": "Устав центрального банка",
}
COMPANY_NAME_EN = "Central Bank"
COMPANY_NAME_RU = "Центральный банк"


def gen_prestige(ef: Path, names: list[str], keep: str) -> tuple[str, int]:
    """One prestige variant per monetary regime, gated by the law behind it.

    Ninety-five, one per currency, is not possible: see the note on
    PRESTIGE_REGIMES. Three is, and the three regimes are what fits in three.

    Icons: two drawn for this mod, in E&F's own idiom -- period coins for the
    representative standards, a sovereign exchanging into colonial notes for the
    pegged ones -- and E&F's spe_uni banknote for fiat, which came free when the
    shared good took local_currency's icon instead.
    """
    out = []
    for key, laws, icon in PRESTIGE_REGIMES:
        if len(laws) == 1:
            gate = f"\t\thas_law = law_type:{laws[0]}\n"
        else:
            gate = ("\t\tOR = {\n"
                    + "".join(f"\t\t\thas_law = law_type:{l}\n" for l in laws)
                    + "\t\t}\n")
        out.append(f"{key} = {{\n"
                   f"\tpossible = {{\n{gate}\t}}\n"
                   f"\tbase_good = {keep}\n"
                   f"\tprestige_bonus = 0.1\n"
                   f'\ttexture = "{icon}"\n'
                   f"}}\n\n")
    head = (BANNER +
            "### Three prestige variants of the shared currency good, one per monetary\n"
            "### regime. Every central bank company carries all three; the good's own\n"
            "### `possible` decides which one a country actually mints.\n"
            "###\n"
            "### WHY THREE AND NOT NINETY-FIVE. Only the first three declarations of a base\n"
            "### good's variants become real slots; anything past them falls back to the\n"
            "### third. Measured three times over: 3 declared -> all three correct; 10\n"
            "### declared -> Britain kept the pound and every other country minted the franc,\n"
            "### the third declaration; 95 declared -> the whole world minted the Iraqi\n"
            "### dinar, again the third. Vanilla never exceeds three either, and no define\n"
            "### controls it -- the number is in the executable.\n"
            "###\n"
            "### THE `possible` GATE IS UNPROVEN AT THIS SIZE. It was tried once with 95\n"
            "### goods and appeared to do nothing, but that test was ruined by the count,\n"
            "### and the gate was dropped before it was ever tried at three. Vanilla writes\n"
            "### nothing but has_dlc_feature here, so the files cannot say whether it is\n"
            "### evaluated in country scope. If it is, changing the monetary system law\n"
            "### changes the minted currency by itself -- no company swap, no rebuild, no\n"
            "### ownership lost. If it is not, every country will mint the metallic one and\n"
            "### the answer is that regimes have to be split across companies instead.\n"
            "###\n"
            "### law_no_monetary_system has no entry on purpose: no monetary system means no\n"
            "### central bank, so there is nothing to mint.\n\n")
    return head + "".join(out), len(PRESTIGE_REGIMES)


def bank_companies(ef: Path) -> list[str]:
    """Every company E&F itself calls a bank, straight out of E&F.

    Source: the `private_bank_type` block in
    common/customizable_localization/00_ef_localization_ custom.txt -- 99 entries,
    one `is_company_type = company_type:X` per bank, which is E&F's own answer to
    "is this company a bank" and the only list of them it keeps.

    This replaces a hand-written table, and the table is why the Imperial Bank of
    China never became China's central bank: CENTRAL_BANK_COMPANY named the
    Da-Qing Bank for CHI, the Da-Qing Bank is founded in 1905, and the bank China
    actually holds in 1836 is company_BankIBC -- which was on no list of ours at
    all. Mexico, Persia, Turkey and Sicily were the same shape of miss. Any table
    written here is a race against E&F's roster that it eventually loses.

    company_BasicBank is dropped: it is E&F's generic bank, offered to every
    country, and letting it stand for "this country has its own historical bank"
    would mean nobody ever gets the generated one.
    """
    src = read(ef / "common/customizable_localization/00_ef_localization_ custom.txt")
    m = re.search(r"^private_bank_type\s*=\s*\{", src, re.M)
    if not m:
        return []
    blk = src[m.start():block_span(src, m.end() - 1)]
    # The list is checked against the company types that actually exist: E&F's own
    # copy of it names company_BankSBoBS, and the company is company_BankSBoBSA.
    # A REPLACE: of a key that does not exist is a load error, not a warning.
    real = {k for k, _, _ in iter_top_blocks(read(ef / "common/company_types/00_ef_companies.txt"))}
    out, seen = [], set()
    for name in re.findall(r"is_company_type\s*=\s*company_type:(\w+)", blk):
        if name != "company_BasicBank" and name not in seen and name in real:
            seen.add(name)
            out.append(name)
    return out


def historical_central_banks(ef: Path) -> tuple[list[str], list[str]]:
    """Every bank company E&F ships, best candidate for the central bank first.

    ORDER, NOT MEMBERSHIP, is what CENTRAL_BANK_COMPANY decides now. It used to
    decide both, and that is why four countries kept a stand-in they should have
    handed over: the table named one bank per tag, and the bank the country
    actually held was a different one. China holds the Imperial Bank of China in
    1836, not the Da-Qing Bank of 1905. The rule that survives contact is the
    loose one -- whatever bank this country holds is its central bank -- with the
    curated table breaking ties, because Britain holds six and the Bank of England
    should win.

    E&F's grants are still checked against the table, so a rename is reported
    rather than quietly producing a branch that can never fire.
    """
    notes: list[str] = []
    every = bank_companies(ef)
    if not every:
        notes.append("WARNING private_bank_type: no bank list found in E&F, "
                     "falling back to the curated table alone")
    known = set(every)
    real = {k for k, _, _ in iter_top_blocks(read(ef / "common/company_types/00_ef_companies.txt"))}
    granted = establish_mapping(ef, known | {c for cs in CENTRAL_BANK_COMPANY.values()
                                             for c in ([cs] if isinstance(cs, str) else cs)})
    table = {t: ([c] if isinstance(c, str) else list(c))
             for t, c in CENTRAL_BANK_COMPANY.items()}
    out: list[str] = []
    for tag in sorted(table):
        for comp in table[tag]:
            if comp not in real:
                notes.append(f"WARNING {comp}: no such company in E&F any more")
                continue
            if comp not in known:
                notes.append(f"NOTE {comp}: curated, but missing from E&F's private_bank_type "
                             f"list -- kept anyway")
            if comp not in granted:
                notes.append(f"WARNING {comp}: E&F grants it to nobody")
            elif tag not in granted[comp]:
                notes.append(f"WARNING {comp}: E&F grants it to {granted[comp]}, not {tag}")
            if comp not in out:
                out.append(comp)
    curated = len(out)
    for comp in every:
        if comp not in out:
            out.append(comp)
    notes.append(f"bank companies: {len(out)} ({curated} curated first, "
                 f"{len(out) - curated} from E&F's own list)")
    return out, notes


def _add_bank_to_list(body: str, name: str) -> str:
    """Put building_bank at the top of one building list, if it is not there.

    Only the uncommented entries count: E&F keeps `#building_bank` in several of
    these lists as a note to itself, and reading that as "already present" would
    leave the company unable to own the thing.
    """
    m = re.search(r"\b" + name + r"\s*=\s*\{", body)
    if not m:
        return body
    end = block_span(body, m.end() - 1)
    lines = body[m.end():end - 1].splitlines()
    if any(ln.strip() == "building_bank" for ln in lines):
        return body
    indent = next((re.match(r"[ \t]*", ln).group(0) for ln in lines if ln.strip()), "\t\t")
    # after the leading empty line, not before it: the slice starts right after the
    # brace, so index 0 is the tail of the `building_types = {` line itself and
    # inserting there welds the entry onto it.
    lines.insert(1 if lines and not lines[0].strip() else 0, indent + "building_bank")
    return body[:m.end()] + "\n".join(lines) + body[end - 1:]


def _merge_prestige(body: str, goods: list[str]) -> str:
    """Add the three regime currencies to possible_prestige_goods, creating the
    block when E&F gave the company none."""
    have = sub_block(body, "possible_prestige_goods")
    lines = "".join(f"\t\t{g}\n" for g in goods)
    if have is None:
        return body[:body.rindex("}")].rstrip() + f"\n\n\tpossible_prestige_goods = {{\n{lines}\t}}\n}}"
    at = body.index(have)
    # rstrip the old block's tail before appending, or the last existing good keeps
    # its trailing newline and indent and the first new one lands on that line
    merged = have[:-1].rstrip(" \t\n") + "\n" + lines + "\t}"
    return body[:at] + merged + body[at + len(have):]


def gen_companies(ef: Path, names: list[str]) -> tuple[str, int, list[str]]:
    """building_bank and the three regime currencies, for every bank company E&F
    ships.

    INJECT:, because adding is all this does. It was a REPLACE: for one round, in
    order to take building_railway and building_trade_center off the central
    banks' lists -- INJECT: can only add, so removing an entry means restating the
    whole entry. That reason has expired: while there were ninety-five generated
    company types the railways came with a company that was ONLY ever a central
    bank, and now there is one generated type and the rest are E&F's own banks,
    which are ordinary companies that happen to be eligible. Taking the Bank of
    England's railways away because it might hold a central bank is the tail
    wagging the dog, so they keep what E&F gave them.

    Which also means 98 REPLACE: blocks of E&F's text -- some 7,000 lines that had
    to be re-diffed against every E&F update -- collapse back to 98 four-line
    additions.

    WHY ALL OF THEM, and not a curated few. See historical_central_banks: the
    curated table decides ORDER, not membership. Whatever bank a country holds is
    its central bank, so any of them can end up owning one, and every one of them
    needs building_bank on its list -- that list is the only real lock on who may
    own a building.
    """
    hist, notes = historical_central_banks(ef)
    goods = "".join(f"\t\t{k}\n" for k, _, _ in PRESTIGE_REGIMES)
    out = []
    for c in hist:
        out.append(f"INJECT:{c} = {{\n"
                   f"\tbuilding_types = {{\n\t\tbuilding_bank\n\t}}\n\n"
                   f"\tpossible_prestige_goods = {{\n{goods}\t}}\n"
                   f"}}\n\n")
    head = (BANNER +
            f"### Source: the {len(hist)} bank companies E&F itself lists in private_bank_type,\n"
            "### ordered by CENTRAL_BANK_COMPANY -- see historical_central_banks in the\n"
            "### generator for why that table decides order and not membership.\n"
            "###\n"
            "### Two additions each, and nothing taken away:\n"
            "###\n"
            "###   building_bank -- `building_types` is the only real lock on who may own a\n"
            "###   building, and any of these can end up holding a central bank. Without it\n"
            "###   the add_ownership in zz_ef_cm_bank_ownership.txt has nothing to hand the\n"
            "###   bank to and the country's own bank never takes it over.\n"
            "###\n"
            "###   the three regime currencies -- E&F's own prestige goods are left in place;\n"
            "###   they sit on other base goods (manufacture_stock and friends) and never\n"
            "###   compete with the three currencies, which all share spe_uni_c.\n"
            "###\n"
            "### INJECT:, which can only add, and that is now enough. For one round this file\n"
            "### was 98 REPLACE: blocks carrying E&F's full definitions, in order to strip\n"
            "### building_railway and building_trade_center -- 7,000 lines of E&F's text to\n"
            "### re-diff on every update. These are ordinary companies that happen to be\n"
            "### eligible for a central bank, not central banks as such, so they keep the\n"
            "### buildings E&F gave them.\n\n")
    return head + "".join(out), len(hist), notes


def gen_generic_banks(ef: Path, names: list[str]) -> str:
    """ONE central bank company, for every country without a historical one.

    There used to be ninety-five of these, one per currency law, and every one was
    the same block with a different key: same icon, same building list, the same
    three prestige goods. Which prestige good a central bank makes is decided by
    the MONETARY STANDARD law, not by the currency -- so the currency never had
    anything left to select, and the ninety-five types bought nothing. What they
    cost:

      * a 145-branch if/else_if chain in the ownership dispatcher, another in the
        monopoly pass, another in the grant. An if/else_if chain NESTS, so a
        country that matched no branch walked all 145 frames down, inside E&F's
        own already-deep call stack. That is
        `Unhandled Exception C00000FD (EXCEPTION_STACK_OVERFLOW)` in
        crashes/victoria3_.../exception.txt -- the crash on researching the
        central bank in a country whose currency is not one of the ninety-five,
        because that country is exactly the one that reaches the bottom.
      * ninety-five ways for the dispatcher, the grant, the retire list and the
        triggers to disagree about which company a country is meant to hold. That
        is where Austria's and Spain's ghost companies came from.

    So: one type, one name, one branch. It also replaces company_BasicBank as the
    fallback owner, which fixes the last of the three complaints -- BasicBank is
    E&F's ordinary bank company, offered to every country, and it came with a
    railway and a trade centre and the name "Bank".

    flavored_company = yes ON PURPOSE, and it is not the usual meaning. It blocks
    dynamic naming -- all ten of vanilla's naming patterns carry
    use_for_flavored_companies = no -- and the game then falls back to the type's
    localisation key. That key is the name we want: "Central Bank". Dynamic naming
    would splice the tag into the middle of the pattern instead
    ("[Adjective] $TAG$ $TYPE_NAME$"), which is how the panel came to read
    "Австрийская ZZ_EF_CM_BANK_GULDEN_DYNAMIC_NAME_TAG_SINGULAR компания".
    """
    src = read(ef / "common/company_types/00_ef_companies.txt")
    basic = next(src[a:b] for k, a, b in iter_top_blocks(src) if k == "company_BasicBank")

    def block(name: str) -> str:
        s = sub_block(basic, name)
        return s if s else f"{name} = {{\n}}"

    buildings = _add_bank_to_list(block("building_types"), "building_types")
    goods = "".join(f"\t\t{k}\n" for k, _, _ in PRESTIGE_REGIMES)

    body = (f"{GENERIC_COMPANY} = {{\n"
            f'\ticon = "{CENTRAL_BANK_ICON}"\n'
            f'\tbackground = "gfx/interface/icons/company_icons/company_backgrounds/'
            f'comp_illu_manufacturing_light.dds"\n\n'
            f"\tflavored_company = yes\n\n"
            f"\t{buildings.strip()}\n\n"
            f"\tpossible_prestige_goods = {{\n{goods}\t}}\n\n"
            f"\tpotential = {{\n"
            f"\t\t### Not offered to a country that already holds the bank that WAS its\n"
            f"\t\t### central bank. Britain has the Bank of England; it has no use for this.\n"
            f"\t\tNOT = {{ zz_ef_cm_holds_own_historical_bank = yes }}\n"
            f"\t}}\n\n"
            f"\t{block('possible').strip()}\n\n"
            f"\t{block('prosperity_modifier').strip()}\n\n"
            f"\tai_will_do = {{\n\t\talways = yes\n\t}}\n\n"
            f"\tai_weight = {{\n\t\tvalue = 3\n\t}}\n"
            f"}}\n")

    return (BANNER +
            "### Source: E&F's own company_BasicBank, with the building list filtered and the\n"
            "### three regime currencies added.\n"
            "###\n"
            "### ONE company for every country that has no historical central bank of its own.\n"
            "### There were ninety-five of these, one per currency law, identical but for the\n"
            "### key -- and the branch chains they forced on the dispatcher, the grant and the\n"
            "### monopoly pass overflowed the stack for any country that fell through all of\n"
            "### them. See gen_generic_banks in the generator for the crash report.\n"
            "###\n"
            "### `replaces_company` is deliberately not copied from BasicBank -- it points at\n"
            "### company_basic_bank, which exists nowhere.\n\n"
            + body)


def gen_upkeep(ef: Path, names: list[str]) -> dict[str, str]:
    """Every country with a central bank has a bank company, and cannot lose it.

    Three things the engine has no single switch for:

      * spawn it -- the bank is created already owned (zz_ef_cm_create_owned_bank),
        and this pass is the safety net for a central bank that arrived by some
        path that was not rewritten;
      * do not charge a slot for it -- a country modifier with
        country_max_companies_add = 1 while the central bank stands;
      * make it undeletable -- there is no such flag, so it is imitated: delete it
        and the monthly pass puts it back.

    NO TAG GATE ANY MORE, and that is the fix for Prussia. The old
    zz_ef_cm_holds_own_historical_bank asked "is this country AUS and does it hold
    the Oesterreichische Nationalbank" -- a table of tag-to-company written here,
    against which E&F's actual grants were only checked, not derived. E&F hands the
    Preussische Seehandlung to PRU; the table said NGF. So Prussia held its own
    historical bank, the trigger said no, the upkeep pass concluded it had no bank
    company and granted it a second one. That is the duplicate in the screenshot.

    The question that actually matters has no tag in it: does this country hold one
    of the curated central bank companies at all? Whoever E&F gave it to is the
    country it belongs to.

    Everything is additive. on_actions stack, GLOBAL blocks stack, the modifier and
    the triggers are new keys. Nothing of E&F's is overridden.
    """
    hist, _ = historical_central_banks(ef)
    any_of = "\n".join(f"\t\thas_company = company_type:{c}"
                       for c in hist + [GENERIC_COMPANY])
    own_hist = "\n".join(f"\t\thas_company = company_type:{c}" for c in hist)

    rebuild_levels = "".join(
        f"\t\t\tif = {{\n"
        f"\t\t\t\tlimit = {{\n"
        f"\t\t\t\t\tany_scope_building = {{\n"
        f"\t\t\t\t\t\tis_building_type = building_bank\n"
        f"\t\t\t\t\t\tlevel = {n}\n"
        f"\t\t\t\t\t}}\n"
        f"\t\t\t\t}}\n"
        f"\t\t\t\tzz_ef_cm_create_owned_bank = {{ BANK_BLDG_TYPE = building_bank CB_SIZE = {n} }}\n"
        f"\t\t\t}}\n"
        for n in range(1, MAX_BANK_LEVEL + 1))

    triggers = (BANNER +
                "### Source: the curated central bank companies in E&F's own\n"
                "### 00_ef_companies.txt plus the one generated in zz_ef_cm_generic_banks.txt.\n"
                "###\n"
                "### FLAT `has_company` LISTS. Two separate reasons, both paid for in test\n"
                "### rounds.\n"
                "###\n"
                "### `has_company` and not `any_company = { is_company_type = ... }`: the second\n"
                "### shape is what E&F itself commented out in 08_list_effect.txt, and it is the\n"
                "### only construct in this file that was never independently confirmed to fire.\n"
                "### `has_company = company_type:X` is what E&F uses everywhere and what the\n"
                "### dispatcher has been picking the right owner with all along.\n"
                "###\n"
                "### Flat, not if/else_if. A chain nests, and the\n"
                "### previous version of this file had a 49-deep one inside an OR. Between that\n"
                "### one, the 145-deep chain in the dispatcher and the 145-deep chain in the\n"
                "### monopoly pass, a country that matched nothing walked far enough down to\n"
                "### take the game with it:\n"
                "###\n"
                "###   Unhandled Exception C00000FD (EXCEPTION_STACK_OVERFLOW)\n"
                "###\n"
                f"### Does this country hold any central bank company at all -- one of the\n"
                f"### {len(hist)} curated historical ones, or the generated one?\n"
                "zz_ef_cm_has_bank_company = {\n"
                "\tOR = {\n" + any_of + "\n\t}\n}\n\n"
                "### Does this country hold the bank that WAS its central bank?\n"
                "###\n"
                "### No tag gate. The table of tag-to-company this used to test against\n"
                "### disagreed with E&F -- E&F gives the Preussische Seehandlung to PRU, the\n"
                "### table said NGF -- and every disagreement produced a country holding two\n"
                "### central bank companies at once. Whoever E&F handed the bank to is who it\n"
                "### belongs to.\n"
                "zz_ef_cm_holds_own_historical_bank = {\n"
                "\tOR = {\n" + own_hist + "\n\t}\n}\n\n"
                "### ...and the generated stand-in, which it should not still be holding once\n"
                "### the real one has arrived.\n"
                "zz_ef_cm_holds_stand_in_bank = {\n"
                f"\thas_company = company_type:{GENERIC_COMPANY}\n"
                "}\n\n"
                "### The central bank is a state building placed by E&F, not something anyone\n"
                "### builds, so ownership of it is the only honest test for \"has a central bank\".\n"
                "zz_ef_cm_has_central_bank = {\n"
                "\tany_scope_state = {\n"
                "\t\thas_building = building_bank\n"
                "\t}\n}\n")

    effects = (BANNER +
               "### Country scope. Give the country a central bank company if it has none.\n"
               "###\n"
               "### ORDER MATTERS AND IT COST A ROUND TO FIND OUT. The slot has to be granted\n"
               "### BEFORE add_company, not after. Finland owns a central bank and no company\n"
               "### slots at all in 1836 -- add_company simply had nowhere to put the company,\n"
               "### and the +1 arrived a line too late to help.\n"
               "###\n"
               "### There is nothing to choose between any more. The historical banks are\n"
               "### E&F's to hand out and it has already done so by the time this runs; the\n"
               "### generated one is a single type for everybody else. The ninety-five-branch\n"
               "### chain that used to stand here is what overflowed the stack.\n\n"
               "zz_ef_cm_grant_bank_company = {\n"
               "\tif = {\n"
               "\t\tlimit = { NOT = { has_modifier = zz_ef_cm_central_bank_charter } }\n"
               "\t\tadd_modifier = zz_ef_cm_central_bank_charter\n"
               "\t}\n\n"
               "\tif = {\n"
               "\t\tlimit = { NOT = { zz_ef_cm_has_bank_company = yes } }\n"
               "\t\tlog = \"ZZCM grant: [This.GetName] gets the generated central bank company\"\n"
               f"\t\tadd_company = company_type:{GENERIC_COMPANY}\n"
               "\t}\n"
               "}\n\n"
               "### Keep the central bank company alive.\n"
               "###\n"
               "### This is the safety net, not the main road. The company that owns a central\n"
               "### bank is chosen when the bank is built -- zz_ef_cm_create_owned_bank -- and\n"
               "### this pass only catches a country that ended up with a central bank and no\n"
               "### bank company at all.\n\n"
               "zz_ef_cm_bank_company_upkeep = {\n"
               "\tif = {\n"
               "\t\tlimit = {\n"
               "\t\t\tzz_ef_cm_has_central_bank = yes\n"
               "\t\t\tNOT = { zz_ef_cm_has_bank_company = yes }\n"
               "\t\t}\n"
               "\t\tzz_ef_cm_grant_bank_company = yes\n"
               "\t}\n\n"
               "\t### The slot, for a country whose company arrived with the bank.\n"
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
               "\t### The historical bank has turned up while the stand-in holds the central\n"
               "\t### bank. Ownership cannot be moved -- add_ownership exists only inside\n"
               "\t### create_building -- so the only way to hand it over is to build it again.\n"
               "\t###\n"
               "\t### THE REBUILD IS CALLED FROM HERE, not merely asked for. The old version set\n"
               "\t### zz_ef_cm_bank_rebuild and waited for E&F to call a spawner again, which is\n"
               "\t### why Austria and Spain sat on their stand-in for the rest of the campaign:\n"
               "\t### E&F calls macro_facilities_bc when gdp_view crosses a threshold, not on a\n"
               "\t### schedule, so for a country whose economy is not growing that call never\n"
               "\t### comes. The variable still goes up, because it is what makes the dispatcher\n"
               "\t### stop skipping a bank that is already the right size.\n"
               "\t###\n"
               "\t### THE SIZE IS A LITERAL, one branch per level, and that is not verbosity.\n"
               "\t### $CB_SIZE$ is a macro argument -- pasted in as text, and it lands inside\n"
               "\t### `add_ownership = { company = { levels = $CB_SIZE$ } }`, where a `var:` read\n"
               "\t### does not resolve. Passing one there cost four countries their central bank\n"
               "\t### outright: the dispatcher removed the building, created it with zero levels,\n"
               "\t### and logged nothing at all -- Persia, Turkey, Sicily and Spain simply had no\n"
               "\t### bank any more. Every one of E&F's own 1,004 call sites passes a literal.\n"
               "\t###\n"
               "\t### Only one branch can match: they test the level for equality, and a rebuild\n"
               "\t### puts back exactly what it took away.\n"
               "\tif = {\n"
               "\t\tlimit = {\n"
               "\t\t\tzz_ef_cm_has_central_bank = yes\n"
               "\t\t\tzz_ef_cm_holds_own_historical_bank = yes\n"
               "\t\t\tzz_ef_cm_holds_stand_in_bank = yes\n"
               "\t\t}\n"
               "\t\tset_variable = zz_ef_cm_bank_rebuild\n"
               "\t\trandom_scope_state = {\n"
               "\t\t\tlimit = { has_building = building_bank }\n"
               + rebuild_levels +
               "\t\t}\n"
               "\t}\n\n"
               "\t### ...and once it has, the stand-in owns nothing and has no reason to exist.\n"
               "\t### Retired only after the rebuild cleared the variable, so the country is\n"
               "\t### never left with a central bank and nobody holding it.\n"
               "\tif = {\n"
               "\t\tlimit = {\n"
               "\t\t\tzz_ef_cm_holds_own_historical_bank = yes\n"
               "\t\t\tzz_ef_cm_holds_stand_in_bank = yes\n"
               "\t\t\tNOT = { has_variable = zz_ef_cm_bank_rebuild }\n"
               "\t\t}\n"
               "\t\tzz_ef_cm_retire_stand_in_bank = yes\n"
               "\t}\n\n"
               "\t### And the monopoly on central banks goes to whoever holds it.\n"
               "\tif = {\n"
               "\t\tlimit = { zz_ef_cm_has_central_bank = yes }\n"
               "\t\tzz_ef_cm_bank_monopoly = yes\n"
               "\t}\n"
               "}\n"
               "\n### Drop the generated stand-in once the country's own historical bank has\n"
               "### taken the central bank over. One line now: there is one stand-in type.\n\n"
               "zz_ef_cm_retire_stand_in_bank = {\n"
               "\tif = {\n"
               f"\t\tlimit = {{ has_company = company_type:{GENERIC_COMPANY} }}\n"
               "\t\tlog = \"ZZCM retire: [This.GetName] drops the generated stand-in\"\n"
               f"\t\tremove_company = company_type:{GENERIC_COMPANY}\n"
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
                "### its prosperity_modifier -- that is, only once the company is prosperous. This\n"
                "### is unconditional and applies to the flavoured companies too.\n"
                "###\n"
                "### country_free_charters_add pays for the monopoly patent the player is meant to\n"
                "### hand this company. Vanilla's monopoly_charter (00_company_charter_types.txt)\n"
                "### has no `possible` block and no cooldown, so it can be granted from the first\n"
                "### day; this only makes it free instead of spending one of the country's four.\n\n"
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


def gen_modifier_types(keep: str) -> str:
    """The state-scope sell-orders modifier for the shared good.

    Modifier types are NOT generated per good by the engine -- E&F declares each one
    by hand, which is why state_sell_orders_local_currency_add exists in
    00_ef_state_modifier_types.txt and no equivalent exists for spe_uni_c. Merging
    local_currency into it needs that equivalent, or the recomputed issuance in
    zz_ef_local_currency_fix.txt points at a modifier that is not there.

    A new key, so a plain declaration is right -- REPLACE_OR_CREATE: is for
    overriding something that already exists.
    """
    return (BANNER +
            f"### Source: the shape of state_sell_orders_local_currency_add in E&F's own\n"
            f"### common/modifier_type_definitions/00_ef_state_modifier_types.txt.\n"
            f"###\n"
            f"### Needed because local_currency is merged into {keep} and the issuance for\n"
            f"### countries without a monetary system has to land somewhere.\n\n"
            f"state_sell_orders_{keep}_add = {{\n"
            f"\tdecimals = 0\n"
            f"\tcolor = good\n"
            f"\tgame_data = {{\n"
            f"\t\tai_value = 0\n"
            f"\t}}\n"
            f"}}\n")


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
    # This one spells the building out instead of taking it as a parameter, and it
    # is the path a country takes when it adopts a currency mid-game. Missed on the
    # first pass, which left one way for a central bank to appear state-owned.
    "introduction_new_currency",
]

CREATE_BANK_RE = re.compile(
    r"create_building\s*=\s*\{\s*"
    r"building\s*=\s*(\$BANK_BLDG_TYPE\$|building_bank)\s*"
    r"level\s*=\s*(\S+)\s*"
    r"reserves\s*=\s*1\s*\}")


# E&F writes the tag test both ways -- `c:GBR ?= this` and `c:CAN?= this`. A
# regex that demands the space silently finds 8 of the 154 currency assignments.
TAG_IS_THIS = re.compile(r"c:(\w+)\s*\?=\s*this")


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
                    out.setdefault(m.group(1), []).extend(TAG_IS_THIS.findall(head))
        elif depth == 1 and body.startswith("if = {", k):
            starts.append(k)
        k += 1
    return out


def gen_ownership(ef: Path, names: list[str]) -> tuple[dict[str, str], list[str]]:
    """Create the central bank already owned by a bank company, and keep it that way.

    Why at creation and nowhere else: there is no effect in the game that hands an
    existing building to a company. `add_ownership` exists only as a field of
    `create_building` -- all ~1900 uses in vanilla are inside one, and neither
    effects_l_english.yml nor common/effect_localization/ knows any other ownership
    effect. Privatisation is the only other route, and it is the AI's decision on
    its own schedule -- and it does NOT respect the company monopoly: in the Papal
    States, Banca d'Italia privatised 4 of the state's levels out from under the
    company that held the monopoly.

    WHICH COMPANY. Whatever central bank company the country already holds --
    E&F's flavoured one if it has one, the generated one otherwise. No `c:TAG`
    conditions: E&F hands its banks out more loosely than any table written here
    can predict, and every disagreement between the table and E&F produced a
    country holding two central bank companies at once.

    FLAT `if` BLOCKS, NOT AN if/else_if CHAIN, and this is the whole reason the
    game stopped crashing. A chain nests: `else_if` number fifty is fifty frames
    deep, and this one had 145 branches sitting inside E&F's own deep call stack.
    A country that matched an early branch was fine; a country that matched none
    -- one whose currency was not among the ninety-five -- walked to the bottom
    and took the process with it:

      Unhandled Exception C00000FD (EXCEPTION_STACK_OVERFLOW) at 0x00007FF67B9E2FC7

    So the branches are siblings now, and a variable on the owner carries the "not
    built yet" state between them instead of the else chain. Depth 1, whatever the
    country.
    """
    notes: list[str] = []
    hist, hnotes = historical_central_banks(ef)
    notes.extend(hnotes)
    priority = hist + [GENERIC_COMPANY]
    notes.append(f"bank companies in the dispatcher: {len(priority)} "
                 f"({len(hist)} historical, flat branches)")

    def owned_branch(comp: str) -> str:
        return ("\t\tif = {\n"
                "\t\t\tlimit = {\n"
                "\t\t\t\tscope:zz_ef_cm_bank_owner = {\n"
                "\t\t\t\t\thas_variable = zz_ef_cm_bank_unbuilt\n"
                f"\t\t\t\t\thas_company = company_type:{comp}\n"
                "\t\t\t\t}\n"
                "\t\t\t}\n"
                "\t\t\tcreate_building = {\n"
                "\t\t\t\tbuilding = $BANK_BLDG_TYPE$\n"
                "\t\t\t\treserves = 1\n"
                "\t\t\t\tadd_ownership = {\n"
                "\t\t\t\t\tcompany = {\n"
                f"\t\t\t\t\t\ttype    = {comp}\n"
                "\t\t\t\t\t\tcountry = scope:zz_ef_cm_bank_owner\n"
                "\t\t\t\t\t\tlevels  = $CB_SIZE$\n"
                "\t\t\t\t\t}\n"
                "\t\t\t\t}\n"
                "\t\t\t}\n"
                "\t\t\tscope:zz_ef_cm_bank_owner = {\n"
                "\t\t\t\tremove_variable = zz_ef_cm_bank_unbuilt\n"
                "\t\t\t}\n"
                "\t\t}\n")

    branches = "".join(owned_branch(c) for c in priority)

    dispatch = (BANNER +
                "### Source: the curated central bank companies in E&F's own\n"
                "### 00_ef_companies.txt, in CENTRAL_BANK_COMPANY order, then the generated one.\n"
                "###\n"
                "### WHY THIS EXISTS\n"
                "###\n"
                "### There is no effect in the game that gives an existing building to a company.\n"
                "### add_ownership is a field of create_building and nothing else -- all ~1900\n"
                "### uses in vanilla are inside one, and no ownership effect appears in\n"
                "### effects_l_english.yml or common/effect_localization/. The only other route\n"
                "### into company hands is privatisation, which is the AI's call, on its own\n"
                "### schedule, and which ignores the company monopoly: in the Papal States a\n"
                "### rival bank company privatised 4 levels away from the monopoly holder.\n"
                "### That is why the central bank has to be born owned.\n"
                "###\n"
                "### State scope. $CB_SIZE$ and $BANK_BLDG_TYPE$ come straight through from\n"
                "### whichever E&F spawner called it.\n"
                "###\n"
                "### FLAT BRANCHES, AND THAT IS NOT A STYLE CHOICE. This was a 145-deep\n"
                "### if/else_if chain, and an else_if chain nests. A country that matched no\n"
                "### branch -- one whose currency was not among the ninety-five -- walked every\n"
                "### frame of it inside E&F's own deep call stack, and the game died with\n"
                "###\n"
                "###   Unhandled Exception C00000FD (EXCEPTION_STACK_OVERFLOW)\n"
                "###\n"
                "### in crashes/victoria3_.../exception.txt, with nothing at all in error.log.\n"
                "### zz_ef_cm_bank_unbuilt is what replaces the chain: set on the owner before\n"
                "### the branches, cleared by whichever one fires, tested by all of them. Same\n"
                "### first-match-wins behaviour, depth 1.\n"
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
                "### not one line about it in error.log -- it is in debug.log.\n"
                "###\n"
                "### NO `level` FIELD WHERE add_ownership IS PRESENT. The level is the sum of\n"
                "### the ownership levels; writing both makes the engine throw the whole block\n"
                "### away at load:\n"
                "###\n"
                "###   [jomini_effect.cpp:141]: PostValidate of effect 'create_building'\n"
                "###   returned false at common/scripted_effects/zz_ef_cm_bank_ownership.txt:982\n"
                "###\n"
                "### Vanilla says the same thing by example: 3128 create_building blocks in\n"
                "### common/history/buildings/ carry add_ownership, and not one of them sets\n"
                "### level. Only the last-resort branch, which grants no ownership, still does.\n\n"
                "zz_ef_cm_create_owned_bank = {\n"
                "\towner = {\n"
                "\t\tsave_scope_as = zz_ef_cm_bank_owner\n"
                "\t}\n\n"
                "\t### Already at least this big -- nothing to do. E&F calls its spawners on a\n"
                "\t### pulse and lets create_building expand the bank as gdp_view rises, so this\n"
                "\t### effect runs over and over on a bank that is already the right size.\n"
                "\t###\n"
                "\t### zz_ef_cm_bank_rebuild is how the swap gets asked for. Ownership cannot be\n"
                "\t### moved -- add_ownership exists only inside create_building -- so when a\n"
                "\t### country's historical bank finally shows up years after its central bank\n"
                "\t### was built, the only way to hand it over is to build the thing again. The\n"
                "\t### monthly pass sets the variable; this is what makes it stop skipping.\n"
                "\tif = {\n"
                "\t\tlimit = {\n"
                "\t\t\tany_scope_building = {\n"
                "\t\t\t\tis_building_type = $BANK_BLDG_TYPE$\n"
                "\t\t\t\tlevel >= $CB_SIZE$\n"
                "\t\t\t}\n"
                "\t\t\tNOT = {\n"
                "\t\t\t\tscope:zz_ef_cm_bank_owner = {\n"
                "\t\t\t\t\thas_variable = zz_ef_cm_bank_rebuild\n"
                "\t\t\t\t}\n"
                "\t\t\t}\n"
                "\t\t}\n"
                "\t}\n"
                "\telse = {\n"
                "\t\t### THE BANK IS REBUILT, NOT EXPANDED, AND THAT IS DELIBERATE.\n"
                "\t\t### Expanding an existing building hands the NEW levels to the state --\n"
                "\t\t### add_ownership only covers levels created together with the building.\n"
                "\t\t### E&F grows the central bank exactly that way, by calling create_building\n"
                "\t\t### again with a bigger level, so Finland came out 5 levels company-owned\n"
                "\t\t### and 5 state-owned, and in the Papal States a rival bank company then\n"
                "\t\t### privatised 4 of the state's five. Rebuilding is the only way to keep\n"
                "\t\t### the whole bank in one pair of hands.\n"
                "\t\tif = {\n"
                "\t\t\tlimit = { has_building = $BANK_BLDG_TYPE$ }\n"
                "\t\t\tremove_building = $BANK_BLDG_TYPE$\n"
                "\t\t}\n\n"
                "\t\t### Make sure there is somebody to hand it to, and arm the flag the\n"
                "\t\t### branches below read. grant is a no-op for a country that already holds\n"
                "\t\t### a central bank company.\n"
                "\t\tscope:zz_ef_cm_bank_owner = {\n"
                "\t\t\tzz_ef_cm_grant_bank_company = yes\n"
                "\t\t\tset_variable = zz_ef_cm_bank_unbuilt\n"
                "\t\t}\n\n"
                + branches +
                "\n"
                "\t\t### LAST RESORT, AND IT EXISTS FOR A REASON. E&F's own line, untouched.\n"
                "\t\t### When the dispatcher failed once before, every central bank in the\n"
                "\t\t### world simply stopped existing -- there was no path left that just\n"
                "\t\t### builds the thing. A state-owned bank beats no bank.\n"
                "\t\tif = {\n"
                "\t\t\tlimit = {\n"
                "\t\t\t\tscope:zz_ef_cm_bank_owner = {\n"
                "\t\t\t\t\thas_variable = zz_ef_cm_bank_unbuilt\n"
                "\t\t\t\t}\n"
                "\t\t\t}\n"
                "\t\t\tcreate_building = {\n"
                "\t\t\t\tbuilding = $BANK_BLDG_TYPE$\n"
                "\t\t\t\tlevel    = $CB_SIZE$\n"
                "\t\t\t\treserves = 1\n"
                "\t\t\t}\n"
                "\t\t}\n\n"
                "\t\t### The rebuild resets the production methods. This is E&F's own effect for\n"
                "\t\t### choosing them -- the same call its spawners make after building a bank.\n"
                "\t\towner = {\n"
                "\t\t\tcentral_bank_production_methods = yes\n"
                "\t\t\tremove_variable = zz_ef_cm_bank_rebuild\n"
                "\t\t\tremove_variable = zz_ef_cm_bank_unbuilt\n"
                "\t\t}\n"
                "\t}\n"
                "}\n")

    src = read(ef / SPAWN_FILE)
    rewritten, total = [], 0
    for name in BANK_SPAWN_EFFECTS:
        body = effect_body(src, name)
        body, n = CREATE_BANK_RE.subn(
            lambda m: ("zz_ef_cm_create_owned_bank = { BANK_BLDG_TYPE = %s CB_SIZE = %s }"
                       % (m.group(1), m.group(2))), body)
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
                "### because macro_facilities_bc alone is 12,000 lines and 1,001 of those call\n"
                "### sites -- a switch over gdp_view crossed with the country list. All 1,001\n"
                "### are shaped identically, which is what makes one regex enough.\n\n"
                + "\n\n".join(rewritten) + "\n")

    return {
        "common/scripted_effects/zz_ef_cm_bank_ownership.txt": dispatch,
        "common/scripted_effects/zz_ef_cm_bank_spawn.txt": override,
    }, notes




# --- the monopoly on central banks ------------------------------------------


def bank_company_priority(ef: Path, names: list[str]) -> list[str]:
    """Who may own a central bank, best first.

    The curated historical central banks, then the one generated company. France
    holds the Banque de France, so France's central bank goes to the Banque de
    France and keeps the assets it already has; a country with no such bank gets
    the generated one.

    E&F's other bank companies are deliberately absent, and stay absent from
    building_types too -- see gen_companies for what happened in the Papal States
    while they were on the list.
    """
    hist, _ = historical_central_banks(ef)
    return hist + [GENERIC_COMPANY]


def gen_monopoly(ef: Path, names: list[str]) -> str:
    """Give the bank company a company monopoly on building_bank.

    SYNTAX CONFIRMED IN GAME 2026-08-22. Nothing in vanilla or in any mod here
    calls these, so the shape was inferred from the loc:

      * common/effect_localization/00_country_effects_loc.txt names
        add_company_monopoly, add_country_monopoly and remove_monopoly;
      * ADD_COMPANY_MONOPOLY_FIRST reads "[COMPANY.GetName] gains a company
        monopoly on [TARGET_BUILDING_TYPE.GetName]", and a `first` slot of COMPANY
        is how effect_localization marks the scope an effect runs in -- so company
        scope, one building type as the value;
      * building types are addressed as `bt:building_x`
        (mp1_charters_of_commerce_achievements.txt:146).

    The engine confirmed it by complaining about the second grant rather than the
    syntax: "pdx_assert.cpp:641: Assertion failed: already have monopoly granted to
    a company". Hence the guard below looks at every company in the country.

    FLAT `if` BLOCKS. This was a 145-deep else_if chain and it was one of the three
    that overflowed the stack (see gen_ownership). Siblings are safe here without
    any extra bookkeeping, because every branch already carries the guard that
    makes it first-match-wins: once one company has the monopoly, the
    `NOT = { any_company = { company_has_building_type_monopoly } }` test fails for
    all the rest.

    Note what the monopoly does NOT do: it does not stop another company
    privatising the building. In the Papal States, Banca d'Italia bought 4 levels
    that the state had gained through E&F's growth step while the monopoly sat
    with someone else. That is what the rebuild in zz_ef_cm_create_owned_bank is
    for -- the monopoly is a price and construction rule, not a lock.
    """
    order = bank_company_priority(ef, names)

    def branch(comp: str) -> str:
        return ("\tif = {\n"
                "\t\tlimit = {\n"
                f"\t\t\thas_company = company_type:{comp}\n"
                "\t\t\t### Any company holding it, not just this one -- guarding on\n"
                "\t\t\t### company:{this} alone tripped the engine's own assertion. It is\n"
                "\t\t\t### also what makes these flat branches first-match-wins.\n"
                "\t\t\tNOT = {\n"
                "\t\t\t\tany_company = {\n"
                "\t\t\t\t\tcompany_has_building_type_monopoly = bt:building_bank\n"
                "\t\t\t\t}\n"
                "\t\t\t}\n"
                "\t\t}\n"
                f"\t\tcompany:{comp} = {{\n"
                "\t\t\tadd_company_monopoly = bt:building_bank\n"
                "\t\t}\n"
                "\t}\n")

    out = [branch(c) for c in order]

    return (BANNER +
            "### Source: the same company order as zz_ef_cm_bank_ownership.txt, so the\n"
            "### monopoly lands on the same company that owns the bank.\n"
            "###\n"
            "### add_company_monopoly = bt:building_bank in company scope. Confirmed in game\n"
            "### 2026-08-22 -- see the docstring of gen_monopoly in the generator for how the\n"
            "### shape was read off common/effect_localization/ and what the engine answered.\n"
            "###\n"
            "### The +1 free charter on zz_ef_cm_central_bank_charter stays either way: it is\n"
            "### what lets the player hand the company a monopoly charter without spending one\n"
            "### of the country's four, which is the route the game itself offers.\n\n"
            "zz_ef_cm_bank_monopoly = {\n" + "".join(out) + "}\n")




# --- the market panel's currency section -------------------------------------

MARKET_PANEL = "gui/market_panel.gui"


def gen_market_panel(ef: Path) -> tuple[str, list[str]]:
    """Drop E&F's "Currency in Circulation" section from the market panel.

    TWO PROBLEMS, ONE CAUSE. E&F does not show currency goods in the ordinary goods
    grid; it adds a section of its own underneath, fed by

        datamodel = "[GetGlobalList('gui_market_currency_list')]"

    and that list is a GLOBAL variable list, rebuilt by a scripted GUI from
    whichever market the panel last ran its `update_cache` / `build_list` states
    for. Open the currency section on any other market and you are looking at the
    market it was last built for -- Britain's, in the report that started this.

    A global cannot hold per-market contents, so there is nothing to repair inside
    it. The section goes, and the currency shows up in the ordinary goods grid
    above it like any other good -- which is where one currency good belongs, now
    that there is one instead of fifty-seven.

    The two `on_finish` calls that build the list go with it, so the scripted GUI
    stops running per frame as well. The financial-products section is left exactly
    as E&F wrote it: same shape, same latent problem, not ours to change today.
    """
    notes: list[str] = []
    src = read(ef / MARKET_PANEL)

    marker = src.index('text = "currency_GOODS"')
    best = None
    for m in re.finditer(r"flowcontainer\s*=\s*\{", src):
        open_at = src.index("{", m.start())
        if open_at > marker:
            break
        close_at = block_span(src, open_at)
        if close_at > marker and (best is None or open_at > best[0]):
            best = (m.start(), close_at)
    if best is None:
        raise SystemExit(f"{MARKET_PANEL}: cannot find the flowcontainer around currency_GOODS")

    start, end = best
    line_start = src.rfind("\n", 0, start) + 1
    cut = src[line_start:end]
    notes.append(f"currency section removed: {cut.count(chr(10)) + 1} lines")
    src = src[:line_start] + src[end:].lstrip("\n")

    kept = []
    dropped = 0
    for line in src.split("\n"):
        if "market_gui_market_currency_list" in line and "on_finish" in line:
            dropped += 1
            continue
        kept.append(line)
    notes.append(f"list-building on_finish calls removed: {dropped}")
    src = "\n".join(kept)

    # And the reason the currency still did not show up in the ordinary grid: E&F
    # hides it there by name. goods_entry_button carries a `visible` built from 105
    # EqualTo_string(Goods.GetKey, ...) terms -- every financial product and every
    # one of its currencies, spe_uni_c included. 94 of those goods do not exist any
    # more, so the whole expression is rebuilt from the eight that do.
    hidden = ["bond", "manufacture_stock", "agricultural_stock", "mining_stock",
              "railroad_stock", "war_bond", "mutual_funds", "paper_gold"]
    expr = "EqualTo_string(Goods.GetKey,'%s')" % hidden[0]
    for k in hidden[1:]:
        expr = "Or(%s,EqualTo_string(Goods.GetKey,'%s'))" % (expr, k)
    replacement = '[Not(%s)]' % expr

    out, swapped = [], 0
    for line in src.split("\n"):
        if "EqualTo_string(Goods.GetKey,'spe_uni_c')" in line and "visible" in line:
            indent = line[:len(line) - len(line.lstrip())]
            out.append(f'{indent}visible = "{replacement}"')
            swapped += 1
        else:
            out.append(line)
    if not swapped:
        raise SystemExit(f"{MARKET_PANEL}: the goods_entry_button visible filter changed shape")
    notes.append(f"goods_entry_button filters rebuilt: {swapped} "
                 f"(105 keys -> {len(hidden)}, spe_uni_c no longer hidden)")
    src = "\n".join(out)

    head = ("### E&F Currency Merge -- GENERATED FILE, DO NOT EDIT\n"
            "### Rebuild with tools/regen_ef_currency_merge.py after any E&F or hotfix update.\n"
            "###\n"
            f"### Source: E&F's own {MARKET_PANEL}, with its \"Currency in Circulation\"\n"
            "### section removed and the two on_finish calls that built the list with it.\n"
            "###\n"
            "### The section was fed by GetGlobalList('gui_market_currency_list') -- a GLOBAL\n"
            "### variable list, rebuilt for whichever market the panel last cached. Opening it\n"
            "### on any other market showed the market it was last built for. A global cannot\n"
            "### hold per-market contents, so there was nothing to repair inside it.\n"
            "###\n"
            "### The currency now appears in the ordinary goods grid above, like any other\n"
            "### good -- which is where one currency good belongs, now that there is one\n"
            "### instead of fifty-seven. That took a second change: goods_entry_button hides\n"
            "### goods by name through a `visible` built from 105 EqualTo_string terms, and\n"
            "### spe_uni_c was one of them. 94 of those goods no longer exist, so the filter\n"
            "### is rebuilt from the eight financial products that do.\n"
            "###\n"
            "### GUI files are overridden by PATH: this replaces E&F's file wholesale, so it\n"
            "### is copied rather than edited, and has to be regenerated after an E&F update.\n\n")
    return head + src, notes


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

    emit(mod / "common/modifier_type_definitions/zz_ef_cm_modifier_types.txt",
         gen_modifier_types(args.keep), args.check, acc)

    text, n = gen_modtypes(read(ef / MODTYPE_FILE), dead)
    print(f"     modifier types dropped: {n}")
    emit(mod / MODTYPE_FILE, text, args.check, acc)

    for f in STATIC_FILES:
        text, notes = gen_static(read(ef / f), f, dead, args.keep, rt)
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

    text, n, cnotes = gen_companies(ef, names)
    print(f"     bank companies wired: {n}")
    for x in cnotes:
        print(f"     {x}")
    emit(mod / "common/company_types/zz_ef_cm_companies.txt", text, args.check, acc)

    emit(mod / "common/company_types/zz_ef_cm_generic_banks.txt",
         gen_generic_banks(ef, names), args.check, acc)

    bank, group = gen_bank(ef, args.private_bank)
    emit(mod / "common/buildings/zz_ef_cm_bank.txt", bank, args.check, acc)
    gpath = mod / "common/building_groups/zz_ef_cm_bank_group.txt"
    if group is not None:
        emit(gpath, group, args.check, acc)
    elif gpath.exists() and not args.check:
        # This can fail: the desktop bridge that reaches the disk refuses unlink
        # outright ("Operation not permitted"). A leftover file is a wrong bg_bank,
        # not a crash -- name it and let the rest of the run finish.
        try:
            gpath.unlink()
            print("  removed    zz_ef_cm_bank_group.txt (no --private-bank)")
        except OSError as e:
            print(f"  DELETE ME  {gpath} ({e.strerror}) -- stale --private-bank output")

    emit(mod / "common/scripted_effects/zz_ef_cm_bank_monopoly.txt", gen_monopoly(ef, names), args.check, acc)

    files, notes = gen_ownership(ef, names)
    for x in notes:
        print(f"     {x}")
    for rel, text in files.items():
        emit(mod / rel, text, args.check, acc)

    for rel, text in gen_upkeep(ef, names).items():
        emit(mod / rel, text, args.check, acc)

    text, mnotes = gen_market_panel(ef)
    for x in mnotes:
        print(f"     {x}")
    emit(mod / MARKET_PANEL, text, args.check, acc)

    goods_loc = gen_goods_loc(ef, args.keep)
    print(f"     E&F goods localisation overridden: {len(goods_loc)} languages")
    for lang, text in goods_loc.items():
        emit(mod / EF_GOODS_LOC.format(lang=lang), text, args.check, acc)

    loc = gen_loc(args.keep, names)
    print(f"     localisation: {len(loc)} languages")
    for lang, text in loc.items():
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
