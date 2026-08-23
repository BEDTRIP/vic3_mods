def _strip_bank_buildings(body: str, name: str, add_bank: bool) -> tuple[str, int]:
    """Drop building_railway / building_trade_center from one building list.

    Only uncommented entries are touched: E&F keeps `#building_port` and
    `#building_bank` in these lists as notes to itself, and rewriting those would
    make every diff against a new E&F version unreadable.
    """
    m = re.search(r"\b" + name + r"\s*=\s*\{", body)
    if not m:
        return body, 0
    end = block_span(body, m.end() - 1)
    inner = body[m.end():end - 1]
    kept, dropped = [], 0
    for ln in inner.splitlines():
        if ln.strip() in CENTRAL_BANK_FORBIDDEN:
            dropped += 1
            continue
        kept.append(ln)
    indent = next((re.match(r"[ \t]*", ln).group(0) for ln in kept if ln.strip()), "\t\t")
    if add_bank and not any(ln.strip() == "building_bank" for ln in kept):
        kept.insert(0, indent + "building_bank")
    return body[:m.end()] + "\n".join(kept) + body[end - 1:], dropped


def _merge_prestige(body: str, goods: list[str]) -> str:
    """Add the three regime currencies to possible_prestige_goods, creating the
    block when E&F gave the company none."""
    have = sub_block(body, "possible_prestige_goods")
    lines = "".join(f"\t\t{g}\n" for g in goods)
    if have is None:
        return body[:body.rindex("}")] + f"\n\tpossible_prestige_goods = {{\n{lines}\t}}\n}}"
    at = body.index(have)
    return body[:at + len(have) - 1] + lines + "\t" + body[at + len(have) - 1:]


def gen_companies(ef: Path, names: list[str]) -> tuple[str, int, list[str]]:
    """building_bank and the three regime currencies, for the historical central
    banks only -- plus company_BasicBank as the last-resort owner.

    NOT for all 97 of E&F's bank companies, and the difference matters.
    `building_types` is the only real lock on who may hold a building: while every
    bank company had building_bank on its list, Banca d'Italia privatised four
    levels of the Papal central bank out from under the company that held the
    monopoly. A monopoly is a price and construction rule; the building list is the
    lock.

    So the list is the curated one: the bank that actually was the country's
    central bank -- the Bank of England for Britain, the Banque de France for
    France, the State Bank for Russia. Those keep the assets they already own, and
    the generated per-currency company is used only where no such bank exists.

    REPLACE:, not INJECT:, and that is the second half of the same lesson. INJECT:
    can only add, so the first version of this file added building_bank and left
    E&F's own building_railway and building_trade_center sitting on the list --
    the Bank of England went on buying railways exactly as before. Taking an entry
    off a list needs the whole entry restated.

    Restating it means copying E&F's block verbatim and editing only the building
    list and the prestige goods, so everything else -- the flavoured icon,
    replaces_company, potential, attainable, the prosperity modifier -- keeps
    working and keeps tracking E&F on the next regeneration.
    """
    hist, notes = historical_central_banks(ef)
    src = read(ef / "common/company_types/00_ef_companies.txt")
    blocks = {k: src[a:b] for k, a, b in iter_top_blocks(src)}
    goods = [k for k, _, _ in PRESTIGE_REGIMES]
    out, dropped = [], 0
    for c in hist:
        body = blocks.get(c)
        if body is None:
            notes.append(f"WARNING {c}: no block in E&F to replace, skipped")
            continue
        for lst in ("building_types", "extension_building_types"):
            body, n = _strip_bank_buildings(body, lst, add_bank=(lst == "building_types"))
            dropped += n
        out.append("REPLACE:" + _merge_prestige(body, goods).rstrip() + "\n\n")
    notes.append(f"{dropped} railway/trade-centre entries removed across {len(hist)} companies")
    out.append("INJECT:company_BasicBank = {\n"
               "\tbuilding_types = {\n\t\tbuilding_bank\n\t}\n"
               "}\n")
    head = (BANNER +
            f"### Source: CENTRAL_BANK_COMPANY in the generator -- {len(hist)} of E&F's bank\n"
            "### companies, the ones that were their country's actual central bank, checked\n"
            "### against the tag E&F grants each of them in establish_bank_and_ef_compagnie.\n"
            "###\n"
            "### NOT all 97, and that is the whole point. `building_types` is the only real\n"
            "### lock on who may own a building: while every bank company carried\n"
            "### building_bank, Banca d'Italia privatised four levels of the Papal central\n"
            "### bank away from the company holding the monopoly. A monopoly is a price and\n"
            "### construction rule; this list is the lock.\n"
            "###\n"
            "### These keep the assets they already own -- the Banque de France comes with\n"
            "### its ten levels of private construction and five of the Bourse de Paris -- and\n"
            "### the generated per-currency company is used only where no historical central\n"
            "### bank exists. See zz_ef_cm_generic_banks.txt.\n"
            "###\n"
            "### REPLACE:, because INJECT: can only add. The first version of this file was an\n"
            "### INJECT: and the Bank of England kept buying railways: E&F's own list still\n"
            "### held building_railway and building_trade_center, and nothing short of\n"
            "### restating the entry takes an entry off it. Each block below is E&F's own,\n"
            "### copied verbatim, with three edits -- building_bank added, those two removed,\n"
            "### the three regime currencies appended to possible_prestige_goods.\n"
            "###\n"
            "### E&F's own prestige goods stay: they sit on other base goods\n"
            "### (manufacture_stock and friends) and never compete with the three currencies,\n"
            "### which all share spe_uni_c.\n"
            "###\n"
            "### company_BasicBank gets the building and no currency: it is the fallback owner\n"
            "### for a country with neither a historical central bank nor a currency law. It\n"
            "### stays an INJECT: -- E&F offers it to every country as an ordinary company,\n"
            "### not only as a central bank, so its railways are not ours to take away.\n\n")
    return head + "".join(out), len(hist) + 1, notes
