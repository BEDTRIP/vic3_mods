import os
p = os.environ["HOME"] + "/mnt/Projects/vic3_mods/_ef/ef+tr fix/common/production_methods/zzzz_ef_tr_fix_gold_minting.txt"
s = open(p, encoding="utf-8-sig").read()
if "pm_diesel_pump_building_gold_mine" in s:
    print("уже есть"); raise SystemExit

add = '''
### CORRECTION, 21.08.2026 -- the diesel pump loses its minting too.
###
### The original version of this file left pm_diesel_pump_building_gold_mine alone,
### reasoning that the compatch's REPLACE: of it does not name country_modifiers, so
### vanilla's country_minting_add = 1000 survives.
###
### That reasoning was wrong. REPLACE: replaces the ENTIRE entry, not the sub-blocks
### a mod names. Proved twice in game on 21.08.2026:
###
###   * `REPLACE:building_bank = { ownership_type = self }` made the central bank
###     disappear from the game -- nothing was left but that one field;
###   * 285 production methods restated with only `building_modifiers` lost their
###     `unlocking_laws`, and E&F's central bank started offering all 95 currencies
###     in a dropdown meant to show one.
###
### So the compatch's diesel pump has no country_modifiers at all, and the gold-mine
### minting ladder was 250 / 500 / 750 / 0 before this line, not 250 / 500 / 750 / 1000.
### Restored to vanilla's and T&R's own 1000.

INJECT:pm_diesel_pump_building_gold_mine = {
\tcountry_modifiers = {
\t\tworkforce_scaled = {
\t\t\tcountry_minting_add = 1000
\t\t}
\t}
}
'''
s = s.rstrip("\n") + "\n" + add
assert s.count("{") == s.count("}")
open(p, "w", encoding="utf-8-sig", newline="\n").write(s)
print("дописано, скобки OK")
