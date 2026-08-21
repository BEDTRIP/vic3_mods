import re

p = "tools/regen_ef_currency_merge.py"
s = open(p, encoding="utf-8").read()

old = '''EF = "E&F"
HOTFIX = "_ef/ef hotfix 1.13"
MOD = "_ef/ef currency merge"'''
new = '''EF = "E&F"
HOTFIX = "_ef/ef hotfix 1.13"

# Everything is generated straight INTO the hotfix -- one mod in the game.
MOD = HOTFIX

# ...which creates a loop: two of the generated files are built FROM the hotfix's
# own hand-written ones, and if the output lands on the input the generator starts
# eating its own tail on the second run. So the hand-written originals live in
# _gen_source/, a folder the game does not read (it scans common/, events/, gui/,
# localization/, gfx/, map_data/, .metadata/ and nothing else).
#
# The folder is created on first run from whatever is in the mod right now, so the
# bootstrap happens once and by itself. EDIT THE COPIES IN _gen_source/ from then
# on -- the ones under common/ are output and get overwritten.
SRC_DIR = "_gen_source"'''
assert old in s
s = s.replace(old, new)

# bootstrap + source resolution
old2 = '''def inventory(ef: Path, hf: Path, keep: str):
    goods_src = hf / GOODS_FILE if (hf / GOODS_FILE).exists() else ef / GOODS_FILE'''
new2 = '''def hand_written(hf: Path, rel: str) -> Path:
    """The hand-written original of a file the generator overwrites.

    First run moves it into _gen_source/; after that the copy there is the source
    of truth and the one under common/ is output.
    """
    src = hf / SRC_DIR / Path(rel).name
    if not src.exists():
        live = hf / rel
        if not live.exists():
            raise SystemExit(f"neither {src} nor {live} exists")
        src.parent.mkdir(parents=True, exist_ok=True)
        src.write_bytes(live.read_bytes())
        print(f"  bootstrapped  {SRC_DIR}/{src.name}  (hand-written original moved out of the way)")
    return src


def inventory(ef: Path, hf: Path, keep: str):
    goods_src = hand_written(hf, GOODS_FILE)'''
assert old2 in s
s = s.replace(old2, new2)

old3 = """    emit(mod / GOODS_FILE, gen_goods(read(hf / GOODS_FILE), commented_out, args.keep), args.check, acc)

    text, n = gen_popneed(read(hf / POPNEED_FILE), dead, args.keep)"""
new3 = """    emit(mod / GOODS_FILE, gen_goods(read(hand_written(hf, GOODS_FILE)), commented_out, args.keep),
         args.check, acc)

    text, n = gen_popneed(read(hand_written(hf, POPNEED_FILE)), dead, args.keep)"""
assert old3 in s
s = s.replace(old3, new3)

# headers should say where the source really is
s = s.replace('f"### Source: the hotfix\'s own {GOODS_FILE}.\\n"',
              'f"### Source: {SRC_DIR}/{Path(GOODS_FILE).name} -- the hand-written original.\\n"')
s = s.replace('f"### Source: the hotfix\'s own {POPNEED_FILE}.\\n"',
              'f"### Source: {SRC_DIR}/{Path(POPNEED_FILE).name} -- the hand-written original.\\n"')

# self-check must not walk _gen_source
old4 = '''    for path in sorted(mod.rglob("*")):
        if path.suffix not in (".txt", ".yml") or not path.is_file():
            continue'''
new4 = '''    for path in sorted(mod.rglob("*")):
        if path.suffix not in (".txt", ".yml") or not path.is_file():
            continue
        if SRC_DIR in path.parts:
            continue'''
assert old4 in s
s = s.replace(old4, new4)

open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
