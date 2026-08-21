import re, os
H = os.environ["HOME"] + "/mnt/Projects/"
EF = H + "vic3_mods_out/E&F/"
MOD = H + "vic3_mods/_ef/bank ownership test/"

def block(path, key):
    s = open(path, encoding="utf-8-sig", errors="replace").read().replace("\r\n", "\n")
    m = re.search(r"^((?:\w+:)?)" + re.escape(key) + r"\s*=\s*\{", s, re.M)
    i = m.end() - 1
    d = 0
    for j in range(i, len(s)):
        if s[j] == "{":
            d += 1
        elif s[j] == "}":
            d -= 1
            if d == 0:
                break
    return s[m.start(): j + 1]

HEAD_B = '''### STEP B -- building_bank becomes ownable.
###
### THE WHOLE DEFINITION IS RESTATED. The first version of this file was just
###
###     REPLACE:building_bank = { ownership_type = self }
###
### and in game the central bank vanished outright. REPLACE: swaps the ENTIRE
### entry, not the fields a mod names, so the bank was left with nothing but an
### ownership type -- no building_group, no production method groups, no icon.
###
### That is the second independent proof of the rule. The first was the currency
### merge: 285 production methods restated with only `building_modifiers` lost
### their `unlocking_laws`, and the central bank started offering all 95
### currencies in a dropdown that is supposed to show one.
###
### Everything below is E&F's own building_bank, byte for byte, with a single
### field changed:
###
###     ownership_type = no_ownership   ->   ownership_type = self
###
### Re-copy from E&F after an E&F update; nothing here is generated automatically.

'''

HEAD_B2 = '''### STEP B2 -- bg_bank stops being government funded.
###
### Same rule as step B: the whole group is restated, because REPLACE: replaces
### the entry. A lone `is_government_funded = no` would have left bg_bank with no
### category, no lens and no urbanization.
###
### One field changed from E&F's own definition:
###
###     is_government_funded = yes   ->   is_government_funded = no
###
### WHAT THIS COSTS. is_government_funded means the treasury pays the building's
### inputs and wages and takes its output -- the "Правительственные расходы" line
### in the building panel. Off, the central bank is an ordinary private business.
### On the current save it makes 200 bonds (~10.4K) plus currency against ~2.5K of
### inputs and wages; as a government building that gap is state expenditure, as a
### private one it is profit and dividends, every month, for whoever owns the bank.
###
### So the number that decides whether this path is usable is not "did ownership
### work" but "what does the investment pool look like a decade in".

'''

b = block(EF + "common/buildings/ef_15_bank.txt", "building_bank")
assert "ownership_type = no_ownership" in b
b = b.replace("ownership_type = no_ownership", "ownership_type = self", 1)
b = "REPLACE:" + b

g = block(EF + "common/building_groups/00_ef_building_groups.txt", "bg_bank")
assert "is_government_funded = yes" in g
g = g.replace("is_government_funded = yes", "is_government_funded = no", 1)
g = "REPLACE:" + g

for path, text in [
    (MOD + "common/buildings/zz_bot_step_b_building.txt.off", HEAD_B + b + "\n"),
    (MOD + "common/building_groups/zz_bot_step_b2_group.txt.off", HEAD_B2 + g + "\n"),
]:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    assert text.count("{") == text.count("}"), path
    open(path, "w", encoding="utf-8-sig", newline="\n").write(text)
    print("написан", os.path.basename(path), len(text), "байт")
