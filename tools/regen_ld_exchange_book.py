#!/usr/bin/env python3
"""Стакан биржи форка «E&F: Ledgerdemain» (R8б, шаг 7; Д.R8б.19–22): повторяющаяся часть — карты стакана по шагам цены,
их читатели, сведение актива по шагам.

    python3 tools/regen_ld_exchange_book.py [--check]

Пишет `common/scripted_effects/ld_exchange_book.txt` форка целиком (рукописных записей в нём нет). Логика заявок,
расчёта сделок и логов — рукописная, `common/scripted_effects/ld_exchange_trade.txt`.

Цена — доля справедливой: шаг i = 1..STEPS, цена = 1 + (i − MID) × ширина шага (`zz_ef_xq_w`); MID — справедливая.
Карты на стране биржи (ключ — страна-должник, значение — объём в единицах требования):
- `zz_ef_xs_<вид>_<i>` — продажа по цене шага i и ниже; `zz_ef_xb_<вид>_<i>` — покупка по цене шага i и выше;
- итог сведения: `zz_ef_xr_<вид>_c` (шаг цены расчёта, 0 — нет), `_ps` / `_pb` (доля заявок продавцов / покупателей
  крайнего шага, исполненная по цене расчёта), `_fs` / `_fb` (доля остатка, которую взял / отдал фонд), `_is` / `_ib`
  (доля остатка после фонда, которую взял / отдал ЦБ-эмитент в своих валютных точках, Д.R8б.34); `_ls` / `_lb` / `_lc`
  — остаток по справедливой цене и ниже / и выше / по цене покупки фонда и ниже, `_xs` / `_xb` — доля остатка, сведённая
  фондами с другими биржами, `_xf` — доля дешёвого остатка, которую выкупил фонд другой биржи (Д.R8б.36).
Заявки держателя (на его стране): `zz_ef_xa_<держатель>_<вид>` — объём, `zz_ef_xp_<держатель>_<вид>` — шаг (продажа —
1..STEPS, покупка — 10 + шаг).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ld_gen  # noqa: E402

OUT = "common/scripted_effects/ld_exchange_book.txt"
KINDS = ("m", "b")
STEPS = 9
MID = 5
# (holder, kind) pairs that post orders: the maps of the register of claims (ld_claims.txt)
ORDERS = (("cb", "m"), ("bk", "m"), ("pp", "m"), ("tr", "b"), ("bk", "b"))
RESULTS = ("c", "ps", "pb", "fs", "fb", "is", "ib", "ls", "lb", "lc", "xs", "xb", "xf")
# the clearing's tie-break: the step closer to the fair price first
ORDER_OF_STEPS = sorted(range(1, STEPS + 1), key=lambda i: (abs(i - MID), i))


def reader(name):
    return (f"{name}_read = {{\n"
            f"\tset_variable = {{ name = zz_ef_rq_h value = 0 }}\n"
            f"\tif = {{\n"
            f"\t\tlimit = {{ is_key_in_variable_map = {{ name = {name} target = scope:zz_ef_rq_key }} }}\n"
            f"\t\tset_variable = {{ name = zz_ef_rq_h value = \"variable_map({name}|scope:zz_ef_rq_key)\" }}\n"
            f"\t}}\n"
            f"}}\n")


def maps():
    out = []
    for k in KINDS:
        for side in ("s", "b"):
            out += [f"zz_ef_xs_{k}_{i}" if side == "s" else f"zz_ef_xb_{k}_{i}" for i in range(1, STEPS + 1)]
        out += [f"zz_ef_xr_{k}_{r}" for r in RESULTS]
    for h, k in ORDERS:
        out += [f"zz_ef_xa_{h}_{k}", f"zz_ef_xp_{h}_{k}"]
    return out


def book_add(k, side):
    """Exchange scope, key scope:zz_ef_rq_key: var:zz_ef_xm_v more into the step var:zz_ef_xm_s of the side's map."""
    m = "zz_ef_xs" if side == "s" else "zz_ef_xb"
    L = [f"zz_ef_xch_book_add_{k}_{side} = {{"]
    for i in range(1, STEPS + 1):
        kw = "if" if i == 1 else "else_if"
        L.append(f"\t{kw} = {{ limit = {{ var:zz_ef_xm_s = {i} }} zz_ef_xmap_add = {{ MAP = {m}_{k}_{i} }} }}")
    L.append("}")
    return "\n".join(L) + "\n"


def clear_asset(k):
    """Exchange scope, scope:zz_ef_rq_key = the debtor: the single-price auction of (k, debtor) and the fund's share of the
    rest; the results into the maps zz_ef_xr_<k>_*; the week's sums for the logs."""
    L = [f"zz_ef_xch_clear_asset_{k} = {{"]
    # read the book
    for i in range(1, STEPS + 1):
        L.append(f"\tzz_ef_xs_{k}_{i}_read = yes")
        L.append(f"\tset_variable = {{ name = zz_ef_t_s{i} value = var:zz_ef_rq_h }}")
        L.append(f"\tzz_ef_xb_{k}_{i}_read = yes")
        L.append(f"\tset_variable = {{ name = zz_ef_t_b{i} value = var:zz_ef_rq_h }}")
    # cumulative: sells at or below step i, buys at or above it
    L.append("\tset_variable = { name = zz_ef_t_cs1 value = var:zz_ef_t_s1 }")
    for i in range(2, STEPS + 1):
        L.append(f"\tset_variable = {{ name = zz_ef_t_cs{i} value = {{ value = var:zz_ef_t_cs{i - 1} add = var:zz_ef_t_s{i} }} }}")
    L.append(f"\tset_variable = {{ name = zz_ef_t_cb{STEPS} value = var:zz_ef_t_b{STEPS} }}")
    for i in range(STEPS - 1, 0, -1):
        L.append(f"\tset_variable = {{ name = zz_ef_t_cb{i} value = {{ value = var:zz_ef_t_cb{i + 1} add = var:zz_ef_t_b{i} }} }}")
    # the step with the most matched; a tie -- the step closer to the fair price
    L.append("\tset_variable = { name = zz_ef_t_m value = 0 }")
    L.append("\tset_variable = { name = zz_ef_t_c value = 0 }")
    for i in ORDER_OF_STEPS:
        L.append(f"\tset_variable = {{ name = zz_ef_t_x value = {{ value = var:zz_ef_t_cs{i} max = var:zz_ef_t_cb{i} }} }}")
        L.append(f"\tif = {{ limit = {{ var:zz_ef_t_x > var:zz_ef_t_m }} set_variable = {{ name = zz_ef_t_m value = var:zz_ef_t_x }} "
                 f"set_variable = {{ name = zz_ef_t_c value = {i} }} }}")
    # the marginal step's shares: what is left of the matched after the steps that fill whole
    L.append("\tset_variable = { name = zz_ef_t_ps value = 0 }")
    L.append("\tset_variable = { name = zz_ef_t_pb value = 0 }")
    for i in range(1, STEPS + 1):
        below = f"var:zz_ef_t_cs{i - 1}" if i > 1 else "0"
        above = f"var:zz_ef_t_cb{i + 1}" if i < STEPS else "0"
        L.append(f"\tif = {{ limit = {{ var:zz_ef_t_c = {i} }}")
        L.append(f"\t\tif = {{ limit = {{ var:zz_ef_t_s{i} > 0 }} set_variable = {{ name = zz_ef_t_ps value = {{ value = var:zz_ef_t_m "
                 f"subtract = {below} divide = var:zz_ef_t_s{i} min = 0 max = 1 }} }} }}")
        L.append(f"\t\tif = {{ limit = {{ var:zz_ef_t_b{i} > 0 }} set_variable = {{ name = zz_ef_t_pb value = {{ value = var:zz_ef_t_m "
                 f"subtract = {above} divide = var:zz_ef_t_b{i} min = 0 max = 1 }} }} }}")
        L.append("\t}")
    # the rest: sells at or below the fund's bid step not filled, buys at or above its ask step not filled
    L.append("\tset_variable = { name = zz_ef_t_rs value = 0 }")
    L.append("\tset_variable = { name = zz_ef_t_rb value = 0 }")
    for i in range(1, STEPS + 1):
        L.append(f"\tif = {{ limit = {{ var:zz_ef_xr_ib >= {i} }}")
        L.append(f"\t\tif = {{ limit = {{ OR = {{ var:zz_ef_t_c = 0 var:zz_ef_t_c < {i} }} }} change_variable = {{ name = zz_ef_t_rs add = var:zz_ef_t_s{i} }} }}")
        L.append(f"\t\telse_if = {{ limit = {{ var:zz_ef_t_c = {i} }} change_variable = {{ name = zz_ef_t_rs add = {{ value = 1 subtract = var:zz_ef_t_ps multiply = var:zz_ef_t_s{i} }} }} }}")
        L.append("\t}")
        L.append(f"\tif = {{ limit = {{ var:zz_ef_xr_ia <= {i} }}")
        L.append(f"\t\tif = {{ limit = {{ OR = {{ var:zz_ef_t_c = 0 var:zz_ef_t_c > {i} }} }} change_variable = {{ name = zz_ef_t_rb add = var:zz_ef_t_b{i} }} }}")
        L.append(f"\t\telse_if = {{ limit = {{ var:zz_ef_t_c = {i} }} change_variable = {{ name = zz_ef_t_rb add = {{ value = 1 subtract = var:zz_ef_t_pb multiply = var:zz_ef_t_b{i} }} }} }}")
        L.append("\t}")
    L.append(f"\tzz_ef_xch_fund_rest = {{ K = {k} }}")
    # the issuer's CB at its currency points (Д.R8б.34): sells at or below the lower point, buys at or above the upper
    # one not filled by the auction (zz_ef_xch_points_set: var:zz_ef_t_plo / _phi, 0 -- no points)
    L.append(f"\tzz_ef_xch_points_set = {{ K = {k} }}")
    L.append("\tset_variable = { name = zz_ef_t_r2s value = 0 }")
    L.append("\tset_variable = { name = zz_ef_t_r2b value = 0 }")
    for i in range(1, STEPS + 1):
        L.append(f"\tif = {{ limit = {{ var:zz_ef_t_plo >= {i} }}")
        L.append(f"\t\tif = {{ limit = {{ OR = {{ var:zz_ef_t_c = 0 var:zz_ef_t_c < {i} }} }} change_variable = {{ name = zz_ef_t_r2s add = var:zz_ef_t_s{i} }} }}")
        L.append(f"\t\telse_if = {{ limit = {{ var:zz_ef_t_c = {i} }} change_variable = {{ name = zz_ef_t_r2s add = {{ value = 1 subtract = var:zz_ef_t_ps multiply = var:zz_ef_t_s{i} }} }} }}")
        L.append("\t}")
        L.append(f"\tif = {{ limit = {{ var:zz_ef_t_phi > 0 var:zz_ef_t_phi <= {i} }}")
        L.append(f"\t\tif = {{ limit = {{ OR = {{ var:zz_ef_t_c = 0 var:zz_ef_t_c > {i} }} }} change_variable = {{ name = zz_ef_t_r2b add = var:zz_ef_t_b{i} }} }}")
        L.append(f"\t\telse_if = {{ limit = {{ var:zz_ef_t_c = {i} }} change_variable = {{ name = zz_ef_t_r2b add = {{ value = 1 subtract = var:zz_ef_t_pb multiply = var:zz_ef_t_b{i} }} }} }}")
        L.append("\t}")
    # the rest at the fair price for the funds between the exchanges (Д.R8б.36): sells at or below it, buys at or above
    L.append("\tset_variable = { name = zz_ef_t_r3s value = 0 }")
    L.append("\tset_variable = { name = zz_ef_t_r3b value = 0 }")
    for i in range(1, STEPS + 1):
        if i <= MID:
            L.append(f"\tif = {{ limit = {{ OR = {{ var:zz_ef_t_c = 0 var:zz_ef_t_c < {i} }} }} change_variable = {{ name = zz_ef_t_r3s add = var:zz_ef_t_s{i} }} }}")
            L.append(f"\telse_if = {{ limit = {{ var:zz_ef_t_c = {i} }} change_variable = {{ name = zz_ef_t_r3s add = {{ value = 1 subtract = var:zz_ef_t_ps multiply = var:zz_ef_t_s{i} }} }} }}")
        if i >= MID:
            L.append(f"\tif = {{ limit = {{ OR = {{ var:zz_ef_t_c = 0 var:zz_ef_t_c > {i} }} }} change_variable = {{ name = zz_ef_t_r3b add = var:zz_ef_t_b{i} }} }}")
            L.append(f"\telse_if = {{ limit = {{ var:zz_ef_t_c = {i} }} change_variable = {{ name = zz_ef_t_r3b add = {{ value = 1 subtract = var:zz_ef_t_pb multiply = var:zz_ef_t_b{i} }} }} }}")
    L.append(f"\tzz_ef_xch_issuer_rest = {{ K = {k} }}")
    L.append(f"\tzz_ef_xch_left_set = {{ K = {k} }}")
    L.append(f"\tzz_ef_xch_results_set = {{ K = {k} }}")
    for i in range(1, STEPS + 1):
        for v in (f"zz_ef_t_s{i}", f"zz_ef_t_b{i}", f"zz_ef_t_cs{i}", f"zz_ef_t_cb{i}"):
            L.append(f"\tremove_variable = {v}")
    L.append("}")
    return "\n".join(L) + "\n"


def clear_maps():
    """Exchange scope: the book and the results emptied (zz_ef_xch_clear_exchange); holder scope: its orders."""
    L = ["zz_ef_xch_book_empty = {"]
    for k in KINDS:
        for i in range(1, STEPS + 1):
            L.append(f"\tclear_variable_map = zz_ef_xs_{k}_{i}")
            L.append(f"\tclear_variable_map = zz_ef_xb_{k}_{i}")
    L.append("}")
    L.append("zz_ef_xch_results_empty = {")
    for k in KINDS:
        for r in RESULTS:
            L.append(f"\tclear_variable_map = zz_ef_xr_{k}_{r}")
    L.append("}")
    L.append("zz_ef_xch_orders_empty = {")
    for h, k in ORDERS:
        L.append(f"\tclear_variable_map = zz_ef_xa_{h}_{k}")
        L.append(f"\tclear_variable_map = zz_ef_xp_{h}_{k}")
    L.append("}")
    return "\n".join(L) + "\n"


def text():
    head = ("# GENERATED by vic3_mods/tools/regen_ld_exchange_book.py -- do not edit by hand.\n"
            "# The exchange's book (R8б, шаг 7; понятие «Биржа»; Д.R8б.19): per kind of claim and price step, maps on the\n"
            f"# exchange's country keyed by the debtor; a price step i = 1..{STEPS} is the fair price x (1 + (i - {MID}) x\n"
            "# zz_ef_xq_w). The orders' logic -- scripted_effects/ld_exchange_trade.txt.\n\n"
            "# The readers, one per map: the scope's holding of scope:zz_ef_rq_key into var:zz_ef_rq_h (0 if none); the map's\n"
            "# name written out -- a parameter inside the quoted «variable_map(…|…)» is mangled by the engine.\n")
    parts = [head] + [reader(m) for m in maps()]
    parts.append("\n# Exchange scope, key scope:zz_ef_rq_key: var:zz_ef_xm_v more at the step var:zz_ef_xm_s of the book.\n")
    for k in KINDS:
        for side in ("s", "b"):
            parts.append(book_add(k, side))
    parts.append("\n")
    for k in KINDS:
        parts.append(clear_asset(k))
    parts.append("\n")
    parts.append(clear_maps())
    return "".join(parts)


_changed = []


def _put(rel, t):
    import ld_pdx
    dst = os.path.join(ld_gen.FORK, rel)
    old, bom, eol = ld_pdx.read(dst) if os.path.exists(dst) else (None, True, "\n")
    if old is not None and old.replace("\r\n", "\n").lstrip("﻿") == t:
        return
    _changed.append(rel)
    print(f"  {'differs' if ld_gen.CHECK else 'written'}: {rel}")
    if not ld_gen.CHECK:
        ld_pdx.write(dst, t, bom=True if old is None else bom, eol=eol)


def main():
    t = text()
    assert t.count("{") == t.count("}")
    _put(OUT, t)
    print(f"regen_ld_exchange_book: {'расходится' if _changed else 'совпало'}")
    if ld_gen.CHECK and _changed:
        sys.exit(1)


if __name__ == "__main__":
    main()
