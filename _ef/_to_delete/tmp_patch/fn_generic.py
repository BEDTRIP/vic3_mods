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

    buildings, dropped = _strip_bank_buildings(block("building_types"), "building_types", True)
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
            f"### {dropped} ownership entries dropped from E&F's list (railway, trade centre) and\n"
            "### building_bank added: a central bank owns banks, not railways.\n"
            "###\n"
            "### `replaces_company` is deliberately not copied from BasicBank -- it points at\n"
            "### company_basic_bank, which exists nowhere.\n\n"
            + body)
