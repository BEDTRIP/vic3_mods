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
