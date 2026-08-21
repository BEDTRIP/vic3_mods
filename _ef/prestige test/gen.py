#!/usr/bin/env python3
# Generates the prestige-goods stress test mod.
# WHY a generator and not hand-written files: the point of the test is to
# change N (how many prestige goods hang on one base good) and re-run.
# Edit N below, run, copy to the game folder.

import json, os

N = 100                      # dummy prestige goods to create
BASE_GOOD = "clothes"       # base good they all hang on
SPLIT = N // 2              # company A takes 1..SPLIT, company B the rest

ROOT = os.path.dirname(os.path.abspath(__file__))

PG_TEX = "gfx/interface/icons/goods_icons/prestige_goods/generic_clothes_prestige.dds"
CO_ICON = "gfx/interface/icons/company_icons/basic_fabrics.dds"
CO_BG = "gfx/interface/icons/company_icons/company_backgrounds/comp_illu_manufacturing_light.dds"


def w(rel, text):
    """Game .txt/.yml must carry a BOM or the parser mangles the first key."""
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write(text)


names = [f"pgtest_{i:02d}" for i in range(1, N + 1)]

# ---------------------------------------------------------------- prestige goods
out = [
    "### Prestige goods stress test.",
    "### %d dummy prestige goods, all on base_good = %s." % (N, BASE_GOOD),
    "### They produce nothing by themselves - they only occupy the database,",
    "### so that we can see how many entries one base good tolerates.",
    "",
]
for n in names:
    out += [
        f"{n} = {{",
        f'\ttexture = "{PG_TEX}"',
        f"\tbase_good = {BASE_GOOD}",
        "\tprestige_bonus = 0.1",
        "}",
        "",
    ]
w("common/prestige_goods/zzz_pgtest_prestige_goods.txt", "\n".join(out))

# ---------------------------------------------------------------- companies
def company(key, icon, pg_list):
    body = [
        f"{key} = {{",
        f'\ticon = "{icon}"',
        f'\tbackground = "{CO_BG}"',
        "",
        "\tflavored_company = yes",
        "\tuses_dynamic_naming = no",
        "",
        "\tbuilding_types = {",
        "\t\tbuilding_textile_mill",
        "\t}",
        "",
        "\tpossible_prestige_goods = {",
    ]
    body += [f"\t\t{n}" for n in pg_list]
    body += [
        "\t}",
        "",
        "\t### Always allowed to produce, so the only thing the test measures",
        "\t### is the engine's own handling of a long possible_prestige_goods list.",
        "\tprestige_goods_trigger = {",
        "\t\talways = yes",
        "\t}",
        "",
        "\tpossible = {",
        "\t\tany_scope_state = {",
        "\t\t\tis_incorporated = yes",
        "\t\t\tany_scope_building = {",
        "\t\t\t\tis_building_type = building_textile_mill",
        "\t\t\t\tlevel >= 1",
        "\t\t\t}",
        "\t\t}",
        "\t}",
        "",
        "\tprosperity_modifier = {",
        "\t\tbuilding_textile_mill_throughput_add = 0.05",
        "\t}",
        "",
        "\tai_will_do = {",
        "\t\talways = no",
        "\t}",
        "}",
        "",
    ]
    return body


co = [
    "### Two companies on the same base good, so one market can hold two",
    "### prestige variants of clothes at once plus plain clothes - that is what",
    "### the price question needs. Both are open to anyone with a textile mill.",
    "### ai_will_do = no: the AI must not take these, they would pollute the run.",
    "",
]
co += company("company_pgtest_a", CO_ICON, names[:SPLIT])
co += company("company_pgtest_b", CO_ICON, names[SPLIT:])
w("common/company_types/zzz_pgtest_companies.txt", "\n".join(co))

# ---------------------------------------------------------------- localization
for lang, a, b in [
    ("english", "PG Test A", "PG Test B"),
    ("russian", "PG-тест A", "PG-тест B"),
]:
    loc = [f"l_{lang}:", f' company_pgtest_a:0 "{a}"', f' company_pgtest_b:0 "{b}"']
    for i, n in enumerate(names, 1):
        loc.append(f' {n}:0 "PG-{i:02d}"')
    w(f"localization/{lang}/zzz_pgtest_l_{lang}.yml", "\n".join(loc) + "\n")

# ---------------------------------------------------------------- metadata
# NB: no BOM here. The launcher parses metadata.json with a strict JSON reader
# and dies on \xEF\xBB\xBF before the opening brace - the mod then silently
# does not load and the launcher only says "could not process metadata".
meta = {
    "name": "ZZ Prestige Goods Stress Test",
    "id": "zz.pgtest",
    "version": "1",
    "supported_game_version": "1.13.*",
    "short_description": "%d dummy prestige goods on one base good, plus two companies to bind them. Test scaffold, not for play." % N,
    "picture": "thumbnail.png",
    "tags": ["Fixes", "1.13"],
    "relationships": [],
    "game_custom_data": {"multiplayer_synchronized": False},
}
p = os.path.join(ROOT, ".metadata/metadata.json")
os.makedirs(os.path.dirname(p), exist_ok=True)
with open(p, "w", encoding="utf-8", newline="\n") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)

raw = open(p, "rb").read()
assert raw[:3] != b"\xef\xbb\xbf", "metadata.json must not have a BOM"
json.loads(raw.decode("utf-8"))

# ---------------------------------------------------------------- brace check
for rel in [
    "common/prestige_goods/zzz_pgtest_prestige_goods.txt",
    "common/company_types/zzz_pgtest_companies.txt",
]:
    s = open(os.path.join(ROOT, rel), encoding="utf-8-sig").read()
    assert s.count("{") == s.count("}"), rel

print("generated: %d prestige goods on %s, company A=%d, company B=%d"
      % (N, BASE_GOOD, SPLIT, N - SPLIT))
