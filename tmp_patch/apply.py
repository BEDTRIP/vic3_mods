import io, os, re

p = "tools/regen_ef_currency_merge.py"
s = io.open(p, encoding="utf-8").read()
new = io.open("tmp_patch/newfn.py", encoding="utf-8").read()

# 1. swap gen_companies (and its two new helpers) in
a = s.index("def gen_companies(")
b = s.index("def gen_generic_banks(")
assert a < b
s = s[:a] + new.rstrip("\n") + "\n\n\n" + s[b:]

# 2. the constant, above PRESTIGE_REGIMES
CONST = '''# Two buildings a central bank must never end up holding. E&F's flavoured bank
# companies -- the Bank of England, the Banque de France -- carry both, and once
# such a company becomes the country's central bank the player is handed a railway
# monopoly nobody asked for. 97 building_railway and 98 building_trade_center lines
# across E&F's companies file; only the curated central banks are touched here.
CENTRAL_BANK_FORBIDDEN = {"building_railway", "building_trade_center"}

'''
if "CENTRAL_BANK_FORBIDDEN = {" not in s:
    m = re.search(r"^PRESTIGE_REGIMES = \[", s, re.M)
    s = s[:m.start()] + CONST + s[m.start():]

# 3. never crash on an undeletable leftover
old = '        gpath.unlink()\n        print("  removed    zz_ef_cm_bank_group.txt (no --private-bank)")'
newdel = ('        # This can fail: the desktop bridge that reaches the disk refuses unlink\n'
          '        # outright ("Operation not permitted"). A leftover file is a wrong bg_bank,\n'
          '        # not a crash -- name it and let the rest of the run finish.\n'
          '        try:\n'
          '            gpath.unlink()\n'
          '            print("  removed    zz_ef_cm_bank_group.txt (no --private-bank)")\n'
          '        except OSError as e:\n'
          '            print(f"  DELETE ME  {gpath} ({e.strerror}) -- stale --private-bank output")')
if old in s:
    s = s.replace(old, newdel)

tmp = p + ".tmp"
with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
    f.write(s)
os.replace(tmp, p)
print("patched", len(s.splitlines()), "lines")
