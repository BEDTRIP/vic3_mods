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
