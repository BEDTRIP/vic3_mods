"""Д2.2 (5.10.2026, decided by the user) -- the population's need for bank settlements (popneed_currency).

The need is E&F's (its buy packages, ~8% of a middle pop's basket); since Д2.1 it buys bank settlements
(liquidity_currency), and run r1005_201105 showed ~90% of the demand coming from the population -- ~8% of GDP for
Britain against the 5% decided for everything. The user split the 5%: population ~2%, businesses ~3%
(production_methods/zz_ef_market_liquidity_input.txt). So every popneed_currency of E&F's packages is scaled by
POP_NEED_FACTOR, in every branch that re-applies E&F's packages:
  * tools/regen_ef_currency_need.py -- the hotfix (E&F's own branch);
  * tools/regen_vc_ef.py -- the E&F x VC compatch, and through it addon-VC (tools/regen_addon_vc.py).
"""
import re

# 0.25 (r1005_214144, 1838): world bank sales ~948K a week = ~8-9% of the logged GDP (~11M a week), population
# ~51% of the units, businesses ~49% -> 0.13 (population ~40% of ~5%).
POP_NEED_FACTOR = 0.13

_NEED = re.compile(r"(popneed_currency\s*=\s*)(\d+(?:\.\d+)?)")


def scale_line(line: str) -> str:
    """A buy-package line with its popneed_currency scaled (at least 1)."""
    return _NEED.sub(lambda m: m.group(1) + str(max(1, round(float(m.group(2)) * POP_NEED_FACTOR))), line)
