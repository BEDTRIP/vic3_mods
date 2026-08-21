import re, os, sys
EF = os.environ["HOME"] + "/mnt/Projects/vic3_mods_out/E&F/common/company_types/00_ef_companies.txt"
OUT = os.environ["HOME"] + "/mnt/Projects/vic3_mods/_ef/bank ownership test/common/company_types/zz_bot_companies.txt"

s = open(EF, encoding="utf-8-sig", errors="replace").read()
names = [m.group(2) for m in re.finditer(r'^((?:\w+:)?)(company_\w+)\s*=\s*\{', s, re.M)]
SKIP = {"company_private_construction", "company_basic_gold_and_silver_mining_2",
        "company_basic_silver_mining_mex", "company_basic_gold_mining_rus",
        "company_PennsylvaniaRailroad", "company_standard_oil"}
banks = [n for n in names if n not in SKIP]

head = '''### Central Bank Ownership Test -- STEP A, the non-invasive half.
###
### THE QUESTION: will a company take building_bank at all?
###
### E&F has `#building_bank` commented out in every one of its bank companies --
### company_BankofEngland, company_StateBankRussianEmpire, all of them. The author
### evidently tried. The vanilla docs say ownership_type describes what a building
### may OWN, not who may own it ("no_ownership - can't own other buildings,
### dividends if any are payed to the state"), which would make the bank takeable.
### But every one of the 48 buildings listed in vanilla company building_types is
### `self`, without a single exception. Files cannot settle it; the game can.
###
### The first version of this test injected into company_BasicBank only. That was
### useless: Britain gets company_BankofEngland and Russia
### company_StateBankRussianEmpire, so nothing applied to the countries anyone
### actually plays. This one covers all %d of E&F's bank companies.
###
### INJECT: merges into E&F's definitions -- their building lists, prosperity
### modifiers and existing prestige goods are untouched. Nothing is overridden.
###
### Note the prestige good needs `company_is_prosperous = yes`, which is built into
### the engine. Ownership is the first question; the prestige currency only shows
### up once the company is prosperous. Read them in that order.
''' % len(banks)

parts = [head]
for n in banks:
    parts.append(f"""
INJECT:{n} = {{
\tbuilding_types = {{
\t\tbuilding_bank
\t}}

\tpossible_prestige_goods = {{
\t\tzz_bot_prestige_currency
\t}}
}}
""")
text = "﻿" + "".join(parts)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8", newline="\n").write(text)
print("компаний:", len(banks), "| скобки:", text.count("{") - text.count("}"))
