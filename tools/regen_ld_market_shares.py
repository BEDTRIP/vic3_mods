#!/usr/bin/env python3
"""
R8в.1 (Д.R8в.1, Д.R8в.8): a member's share of its market's production and consumption, read monthly.

The engine gives a country's share of a market only as a comparison trigger (market scope):
`market_production_share = { target = <country> value > x }` (and `market_consumption_share`). The share is found by a
binary search over a fixed list of 127 thresholds -- 7 comparisons per share: geometric below 5 % (small members of
a big market keep their size within ~9 %), then 1 % steps up to 99 %. Each leaf sets the middle of its interval.

Generated: `zz_ef_msh_read` -- scripted effect, any scope; `$S$` = production / consumption, `$V$` -- the country
variable to set; the market is scope:zz_ef_msh_mk, the country scope:zz_ef_msh_who (set by zz_ef_msh_world_step,
ld_market_shares.txt, hand-written part of the same file).

Output: common/scripted_effects/ld_market_shares.txt (by entry keys, ld_gen).

Usage:
    python3 tools/regen_ld_market_shares.py [--check]
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ld_gen  # noqa: E402

OUT = "common/scripted_effects/ld_market_shares.txt"

LOW = 0.0002     # the smallest threshold
GEO_TOP = 0.05   # geometric steps below, 1 % steps from here
N_GEO = 32       # thresholds below GEO_TOP; 32 + 95 = 127 = 2^7 - 1


def thresholds():
    r = (GEO_TOP / LOW) ** (1.0 / N_GEO)
    t = [round(LOW * r ** i, 5) for i in range(N_GEO)]
    t += [round(0.05 + 0.01 * i, 2) for i in range(95)]
    assert len(t) == 127 and t == sorted(t) and len(set(t)) == 127, t
    return t


def fmt(x):
    s = f"{x:.5f}".rstrip("0").rstrip(".")
    return s if s else "0"


def tree(t, lo, hi, a, b, depth):
    """t[a:b] -- thresholds of the node; lo, hi -- the interval's bounds."""
    tab = "\t" * depth
    if a >= b:
        return f"{tab}set_variable = {{ name = $V$ value = {fmt((lo + hi) / 2)} }}\n"
    m = (a + b) // 2
    x = t[m]
    out = (f"{tab}if = {{\n{tab}\tlimit = {{ scope:zz_ef_msh_mk = {{ market_$S$_share = {{ target = scope:zz_ef_msh_who "
           f"value > {fmt(x)} }} }} }}\n")
    out += tree(t, x, hi, m + 1, b, depth + 1)
    out += f"{tab}}}\n{tab}else = {{\n"
    out += tree(t, lo, x, a, m, depth + 1)
    out += f"{tab}}}\n"
    return out


def text():
    t = thresholds()
    return ("# GENERATED part (zz_ef_msh_read) by tools/regen_ld_market_shares.py -- do not edit by hand.\n"
            "# The share of scope:zz_ef_msh_mk's $S$ (production / consumption) coming from scope:zz_ef_msh_who, into\n"
            "# var:$V$ of the current scope: a binary search over 127 thresholds (7 comparisons).\n"
            "zz_ef_msh_read = {\n" + tree(t, 0.0, 1.0, 0, len(t), 1) + "}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.parse_args()
    ld_gen.emit(OUT, text())
    ld_gen.report("regen_ld_market_shares")


if __name__ == "__main__":
    main()
