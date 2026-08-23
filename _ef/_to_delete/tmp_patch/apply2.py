import io, os, re

p = "tools/regen_ef_currency_merge.py"
s = io.open(p, encoding="utf-8").read()

def swap(s, start, end, path):
    a = s.index(start)
    b = s.index(end, a + 1)
    new = io.open(path, encoding="utf-8").read().rstrip("\n")
    return s[:a] + new + "\n\n\n" + s[b:]

s = swap(s, "def gen_generic_banks(", "def gen_upkeep(", "tmp_patch/fn_generic.py")
s = swap(s, "def gen_upkeep(", "def gen_modifier_types(", "tmp_patch/fn_upkeep.py")
s = swap(s, "def gen_ownership(", "\n\n# --- the monopoly on central banks", "tmp_patch/fn_ownership.py")
s = swap(s, "def bank_company_priority(", "\n\n# --- the market panel's currency section",
         "tmp_patch/fn_monopoly.py")

# --- constants --------------------------------------------------------------
CONST = '''# The one central bank company every country without a historical one gets.
# It was ninety-five types, one per currency law, identical but for the key --
# see gen_generic_banks for what that cost and why it is one now.
GENERIC_COMPANY = "zz_ef_cm_central_bank"
CENTRAL_BANK_ICON = "gfx/interface/icons/building_icons/banks/central_bank.dds"

'''
if "GENERIC_COMPANY = " not in s:
    m = re.search(r"^CENTRAL_BANK_FORBIDDEN = ", s, re.M)
    s = s[:m.start()] + CONST + s[m.start():]

# --- gen_companies: BasicBank is no longer a central bank owner --------------
old = ('    out.append("INJECT:company_BasicBank = {\\n"\n'
       '               "\\tbuilding_types = {\\n\\t\\tbuilding_bank\\n\\t}\\n"\n'
       '               "}\\n")\n')
assert old in s, "BasicBank INJECT block not found"
s = s.replace(old, "")

old = ('            "### company_BasicBank gets the building and no currency: it is the fallback owner\\n"\n'
       '            "### for a country with neither a historical central bank nor a currency law. It\\n"\n'
       '            "### stays an INJECT: -- E&F offers it to every country as an ordinary company,\\n"\n'
       '            "### not only as a central bank, so its railways are not ours to take away.\\n\\n")')
new = ('            "### company_BasicBank is NOT here any more. It used to be the fallback owner,\\n"\n'
       '            "### with building_bank injected onto it -- but E&F offers it to every country\\n"\n'
       '            "### as an ordinary company, so that quietly let any bank company anywhere buy\\n"\n'
       '            "### a central bank, and it showed up in Bunyoro as a company called \\"Bank\\"\\n"\n'
       '            "### owning railways. The fallback is zz_ef_cm_central_bank now; see\\n"\n'
       '            "### zz_ef_cm_generic_banks.txt.\\n\\n")')
assert old in s, "BasicBank header not found"
s = s.replace(old, new)

s = s.replace("return head + \"\".join(out), len(hist) + 1, notes",
              "return head + \"\".join(out), len(hist), notes")

# --- gen_loc: one company name, not ninety-five ------------------------------
old = '''        body += "\\n" + ((" # Тип компании центробанка — по одному на валютный закон, но стране\\n"
                          " # видна ровно одна: остальные скрыты `potential`. Игрок видит\\n"
                          " # сгенерированное имя, а это подпись под ним.\\n") if ru else
                         (" # The central bank company type -- one per currency law, but a country\\n"
                          " # only ever sees one, the rest are hidden by `potential`. The player\\n"
                          " # reads the generated name; this is the label under it.\\n"))
        for cur in names:
            body += f' {GENERIC_BANK}{cur}:0 "{company}"\\n\''''
new = '''        body += "\\n" + ((" # Компания центробанка для стран без своего исторического банка.\\n"
                          " # Одна на всех: престижный товар выбирает закон денежного стандарта,\\n"
                          " # а не валюта, так что 95 отдельных типов не давали ничего.\\n") if ru else
                         (" # The central bank company, for countries with no historical bank of\\n"
                          " # their own. One for all of them: the prestige good is chosen by the\\n"
                          " # monetary standard law, not by the currency, so ninety-five separate\\n"
                          " # types selected nothing.\\n"))
        body += f' {GENERIC_COMPANY}:0 "{company}"\\n\''''
assert old in s, "gen_loc company block not found"
s = s.replace(old, new)

tmp = p + ".tmp"
with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
    f.write(s)
os.replace(tmp, p)
print("patched", len(s.splitlines()), "lines")
