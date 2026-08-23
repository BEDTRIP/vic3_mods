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
    any_of = "\n".join(f"\t\t\tis_company_type = company_type:{c}"
                       for c in hist + [GENERIC_COMPANY])
    own_hist = "\n".join(f"\t\t\tis_company_type = company_type:{c}" for c in hist)

    triggers = (BANNER +
                "### Source: the curated central bank companies in E&F's own\n"
                "### 00_ef_companies.txt plus the one generated in zz_ef_cm_generic_banks.txt.\n"
                "###\n"
                "### FLAT `any_company` LISTS, NOT if/else_if CHAINS. A chain nests, and the\n"
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
                "\tany_company = {\n"
                "\t\tOR = {\n" + any_of + "\n\t\t}\n\t}\n}\n\n"
                "### Does this country hold the bank that WAS its central bank?\n"
                "###\n"
                "### No tag gate. The table of tag-to-company this used to test against\n"
                "### disagreed with E&F -- E&F gives the Preussische Seehandlung to PRU, the\n"
                "### table said NGF -- and every disagreement produced a country holding two\n"
                "### central bank companies at once. Whoever E&F handed the bank to is who it\n"
                "### belongs to.\n"
                "zz_ef_cm_holds_own_historical_bank = {\n"
                "\tany_company = {\n"
                "\t\tOR = {\n" + own_hist + "\n\t\t}\n\t}\n}\n\n"
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
               "\t### bank. Ownership cannot be moved, so ask zz_ef_cm_create_owned_bank to\n"
               "\t### build the thing again -- it picks the historical bank first.\n"
               "\tif = {\n"
               "\t\tlimit = {\n"
               "\t\t\tzz_ef_cm_has_central_bank = yes\n"
               "\t\t\tzz_ef_cm_holds_own_historical_bank = yes\n"
               "\t\t\tzz_ef_cm_holds_stand_in_bank = yes\n"
               "\t\t\tNOT = { has_variable = zz_ef_cm_bank_rebuild }\n"
               "\t\t}\n"
               "\t\tset_variable = zz_ef_cm_bank_rebuild\n"
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


