[h1]E&F + Tech & Res ComPatch Fix [1.13][/h1]
Fixes for the [b]Tech & Res + E&F ComPatch[/b] (version 1.6) on Victoria 3 [b]1.13.10[/b], checked against E&F 04.07.2026 and Tech & Res 13.05.2026. It patches the compatch, it does not replace it — run both.

[h2]Load order[/h2]
[list]
[*]Community Mod Framework (CMF)
[*]Expanded Topbar Framework
[*]Economic and Financial (E&F)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3786286962]E&F Hotfix[/url] — [b]required[/b]
[*]Tech & Res
[*]Kuromi's AI
[*]Tech & Res + E&F ComPatch
[*][b]This mod[/b]
[/list]
[i]This mod must load after the compatch. Everything it does is either an INJECT: on top of the compatch's work or a re-statement of a key the compatch already re-stated — put it earlier and it does nothing.[/i]

[h2]The goods ceiling is NOT solved here[/h2]
Victoria 3 1.13 caps the goods database at [b]128[/b] and crashes on entering a campaign above that — silently, with nothing in error.log. Vanilla ships 53, E&F with the Hotfix adds 65, Tech & Res adds 39: [b]157[/b]. E&F and Tech & Res do not run together until roughly 29 more goods are cut. That is a separate job; this mod assumes it is already done.

[h2]What this fixes[/h2]
[list]
[*][b]Gold mines stop minting when you upgrade them[/b]
[list]
[*]The compatch adds three mine tiers above Diesel Pump and gives none of them [i]country_minting_add[/i]. Vanilla's ladder is 250 / 500 / 750 / 1000, the new tiers were 0 — so researching Thermal Cracking and moving one step up cost a gold-standard economy all of its minting while raising gold output.
[*]Restored at 1250 / 1500 / 1750, keeping vanilla's ratio of ~33 minting per unit of gold output.
[/list]

[*][b]Three vanilla buildings rolled back to an older Tech & Res[/b]
[list]
[*]The compatch re-states [i]building_power_plant[/i], [i]building_automotive_industry[/i] and [i]building_synthetics_plant[/i] to put E&F's market liquidity back after T&R replaces them — but from a T&R revision that predates 13.05.
[*]The power plant lost [i]pmg_power_transmission[/i] (the DC / half / AC group tied to the National Electric System laws) and got back the data-optimisation group T&R had removed; the automotive industry fell back from Algorithmic Dispatch to plain data optimisation.
[*]Re-generated from Tech & Res as it is today, plus the two E&F groups.
[/list]

[*][b]Buildings the compatch calls by names that do not exist[/b]
[list]
[*]Eleven vanilla industries were rewritten into their plural [i]aliases[/i] form in the ownership and crisis effects. Nine of those aliases are real; [i]building_artillery_foundries[/i] never existed, and [i]building_military_shipyard[/i] was removed from vanilla in 1.13 altogether.
[*]All of them now also run under their canonical names, so the mechanic works whether or not aliases resolve in script scopes.
[*]Two of E&F's own typos inherited by the compatch are corrected in the same pass: [i]building_financial_centre_TUS[/i] (wrong case) and [i]building_vineyard_plantation[/i] (vanilla calls it [i]building_vineyard[/i]). [i]building_naval_base[/i], gone from vanilla in 1.13, is dropped.
[/list]

[*][b]Consumer Electronics could never go private[/b]
[list]
[*]Its block in the compatch's ownership switch is the only one of 167 written wrong — it tests for the method it is about to set, so the building never leaves "No Manufacture Stock". It also never received the stock PM group in the first place.
[*]Group injected, switch rewritten.
[/list]

[*][b]Two Tech & Res industries were never wired into E&F[/b]
[list]
[*][i]building_computer_assembly_plant[/i] (new in T&R 13.05) and [i]building_consumer_electronics_industry[/i] now get market liquidity and the private-ownership stock group, like the 33 T&R buildings the compatch does cover. Both also join the crisis lists.
[/list]

[*][b]Gold mines got no data layer[/b]
[list]
[*]The compatch injects [i]pmg_data_optimization_primary_sector[/i] into "building_gold_mines" — plural, no such building. Injected into [i]building_gold_mine[/i] instead.
[/list]

[*][b]Inflation measured against the wrong basket[/b]
[list]
[*]Each E&F inflation value is a weighted average — price deviation times buy orders over a basket, divided by the buy orders of the same basket. Two goods were listed on one side only: [i]bauxite[/i] fed the raw-material numerator without a divisor term, [i]alloys[/i] the same in manufactured goods. [i]hardwood[/i] was in the raw-material divisor twice.
[/list]

[*][b]Russian localisation[/b] for the seven production methods the compatch ships in English only.
[/list]

[h2]If you also run the E&F + Morgenröte ComPatch[/h2]
Both compatches redefine [i]inflation_on_consumer_goods[/i] and [i]inflation_on_raw_material[/i]. Two mods redefining one script value means the later one wins outright and the earlier one's goods vanish from the basket — today the T&R compatch loads after Morgenröte's and quietly drops [i]air_travel[/i] and [i]good_uranium[/i].

As shipped, this mod carries the E&F + T&R basket only, matching its declared dependencies. For a build with Morgenröte, regenerate with [i]--morg[/i]: the Morgenröte goods are merged in, and since this mod loads last, its definition is the one the game keeps.

[h2]Known, not fixed here[/h2]
[list]
[*][b]The "building_gold_mines" line still logs.[/b] A later mod can add the right key but cannot delete a wrong one; expect one line in error.log at load until the compatch itself is corrected.
[*][b]Morgenröte buildings are injected twice[/b] if you also run the E&F + Morgenröte ComPatch. Both patch the same seven buildings (Airport, Uranium Mine, Elgar Opera, Instrument Workshops, Manzoni Publishing, both Mendelejew plants) with the same PM groups. Removing the duplicate from here would mean re-stating seven T&R building definitions — exactly the drift this mod exists to remove. Drop [i]zztr_mr_buildings.txt[/i] and [i]zztr_modified_mr_buildings.txt[/i] from the compatch instead, or from your merged pack.
[*][b]E&F divides three inflation baskets by hardwood buy orders[/b] without ever adding hardwood to their numerators, which only dilutes the reading. That is E&F's own, in E&F's own files, and belongs in the E&F Hotfix — this mod leaves it alone except in the raw-material basket, where the compatch already settled it by adding hardwood to the numerator.
[*][b]Kuromi's AI needs no patch with E&F[/b] — zero shared keys, localisation keys, event ids or file paths. The "kai" in the compatch's folder name does not correspond to anything inside it.
[/list]

---

## Maintenance

Три файла мода генерируются, руками не правятся:

| файл | источник |
|---|---|
| `common/buildings/zzzz_ef_tr_fix_buildings_gen.txt` | T&R `ztr_vanilla_modified_buildings.txt` + 2 группы E&F |
| `common/scripted_effects/zzzz_ef_tr_fix_effects_gen.txt` | компач `zef_01_financial_scripted_effects.txt`, имена зданий исправлены |
| `common/script_values/zzzz_ef_tr_fix_inflation_gen.txt` | компач `zef_00_economic_scripted_value.txt`, корзины сведены (+ `ef+morg done` при `--morg`) |

```
python3 tools/regen_ef_tr_copies.py --check    # разъехалось ли
python3 tools/regen_ef_tr_copies.py           # пересобрать (E&F + T&R)
python3 tools/regen_ef_tr_copies.py --morg    # пересобрать для сборки с Morgenröte
```

Гонять после каждого обновления Tech & Res и после каждого обновления компача.
`--check` возвращает 1, если что-то разъехалось, — годится для хука перед сборкой мегапака.
Каждый прогон печатает в шапку сгенерированного файла список того, что он поправил:
если список внезапно пуст или в нём появилось новое — значит источник изменился, и это надо прочитать.

Остальные файлы (`zzzz_ef_tr_fix_buildings.txt`, `..._gold_minting.txt`, `..._effects.txt`,
`..._on_actions.txt`, `history/global`, локализация) правятся руками: они ничего не копируют,
а только дописывают своё.
