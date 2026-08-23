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
