import re

p = "tools/regen_ef_currency_merge.py"
s = open(p, encoding="utf-8").read()

start = s.index('    effects = (BANNER +')
end = s.index('    on_actions = (BANNER +')
new = '''    effects = (BANNER +
               "### Keep the central bank company alive.\\n"
               "###\\n"
               "### ORDER MATTERS AND IT COST A ROUND TO FIND OUT. The slot has to be granted\\n"
               "### BEFORE add_company, not after. Finland owns a central bank and no company\\n"
               "### slots at all in 1836 -- add_company simply had nowhere to put the company,\\n"
               "### and the +1 arrived a line too late to help. Same on the game-start pass.\\n"
               "###\\n"
               "### Run monthly and once at game start. The remove_company branch is what makes\\n"
               "### the generic company step aside for a flavoured one: it is not chosen for the\\n"
               "### country up front, it is granted and then withdrawn once something better\\n"
               "### exists.\\n\\n"
               "zz_ef_cm_bank_company_upkeep = {\\n"
               "\\t### 1. The slot first.\\n"
               "\\tif = {\\n"
               "\\t\\tlimit = {\\n"
               "\\t\\t\\tzz_ef_cm_has_central_bank = yes\\n"
               "\\t\\t\\tNOT = { has_modifier = zz_ef_cm_central_bank_charter }\\n"
               "\\t\\t}\\n"
               "\\t\\tadd_modifier = zz_ef_cm_central_bank_charter\\n"
               "\\t}\\n"
               "\\tif = {\\n"
               "\\t\\tlimit = {\\n"
               "\\t\\t\\thas_modifier = zz_ef_cm_central_bank_charter\\n"
               "\\t\\t\\tNOT = { zz_ef_cm_has_central_bank = yes }\\n"
               "\\t\\t}\\n"
               "\\t\\tremove_modifier = zz_ef_cm_central_bank_charter\\n"
               "\\t}\\n\\n"
               "\\t### 2. Then the company.\\n"
               "\\tif = {\\n"
               "\\t\\tlimit = {\\n"
               "\\t\\t\\tzz_ef_cm_has_central_bank = yes\\n"
               "\\t\\t\\tNOT = { zz_ef_cm_has_bank_company = yes }\\n"
               "\\t\\t}\\n"
               "\\t\\tadd_company = company_type:company_BasicBank\\n"
               "\\t}\\n\\n"
               "\\t### 3. The flavoured company displaces the generic one.\\n"
               "\\tif = {\\n"
               "\\t\\tlimit = {\\n"
               "\\t\\t\\thas_company = company_type:company_BasicBank\\n"
               "\\t\\t\\tzz_ef_cm_has_flavoured_bank_company = yes\\n"
               "\\t\\t}\\n"
               "\\t\\tremove_company = company_type:company_BasicBank\\n"
               "\\t}\\n"
               "}\\n")

'''
s = s[:start] + new + s[end:]
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
