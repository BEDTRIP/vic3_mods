# ComPatch: Hail, Columbia! + Gates of the Bosphorus + E&F

<!-- meta
пара: HC+GoB × E&F
статус: done
версии: Game 1.13 (exe 1.13.11) — Hail, Columbia! 8.6-Roosevelt, Gates of the Bosphorus 4.0.8, E&F V4
позиция: грузится после E&F, Hail Columbia и Gates of the Bosphorus
файлов: 4
генератор: tools/regen_hc_ef.py
зависит от: E&F (обязателен), HC и GoB (TRY_INJECT — работает и с одним из двух)
-->

## Для мастерской

[h1]ComPatch: Hail, Columbia! + Gates of the Bosphorus + E&F[/h1]
[b]Game 1.13 (exe 1.13.11) — Hail, Columbia! 8.6-Roosevelt, Gates of the Bosphorus 4.0.8, Economic and Financial Mod (E&F) - V4.[/b]

E&F registers stocks and liquidity through a hand-written list of building names. That list predates both flavor packs, so the three privately-ownable buildings they add are simply not in it:

[list]
[*][i]building_usfp_fur_trapper[/i] — Hail, Columbia!
[*][i]usfp_hippo_ranch[/i] — Hail, Columbia!
[*][i]gbbf_building_esparto_plantation[/i] — Gates of the Bosphorus
[/list]

All three are [i]ownership_type = self[/i], so private ownership should apply — but with E&F installed they produce no liquidity, issue no stock and never switch to private-ownership methods. Nothing appears in the error log; the buildings just stay outside the financial layer of the mod.

This compatch wires all three into E&F's [b]agricultural stock[/b], which is where E&F already puts logging camps, fishing wharves, whaling stations, plantations and the livestock ranch. Same approach E&F + Morgenroete uses for Morgenroete's 62 custom buildings.

[h2]Load order[/h2]
[list]
[*]Economic and Financial (E&F)
[*]Hail, Columbia! / Gates of the Bosphorus
[*][b]this ComPatch[/b]
[/list]

Works with either flavor pack alone: the injects are [i]TRY_INJECT[/i], so a missing building is skipped silently instead of erroring.

---

## Что теряется без этого компача

E&F цепляет свою экономику к зданиям **двумя рукописными списками по имени**, ни один не работает по `building_group`:

1. `common/buildings/ef_*.txt` — `INJECT:` групп `pmg_market_liquidity` и `pmg_private_ownership_*_stock`;
2. `private_ownership_production_stocks` в `common/scripted_effects/01_financial_scripted_effects.txt` — 49 зданий, на каждое рукописная пара `if`-ов (доля > 0.5 → включить stock-метод, ≤ 0.5 → выключить).

Здание без первого не производит ликвидность и не выпускает акции. Здание с группой, но без второго, навсегда залипает на «No Stock».

Ни одно из трёх имён не встречается **ни разу** ни в E&F, ни в хотфиксе, ни в мегапаке, ни в самом собранном аддоне-HC — сверено грепом 26.08.2026.

## Как это нашлось

Пара `HC+GoB+MoH × E&F+hotfix` числилась `noneed` с 25.08.2026 с обоснованием «пересекаются только 7 ключей локализации». Обоснование верное — и слепое: `pair_matrix.py` сравнивает ключи, которые определяют **оба** мода, поэтому здание, добавленное только одним, не может попасть в пересечение никогда.

Нашлось прогоном `tools/content_holes.py --only registry` 26.08.2026 — тем же классом, что LLWA.6 и GR.15.

## Что внутри

| файл | что делает |
| --- | --- |
| `common/buildings/zz_hc_ef_buildings_inject.txt` | `TRY_INJECT:` групп `pmg_market_liquidity` + `pmg_private_ownership_agricultural_stock` в три здания |
| `common/scripted_effects/zz_hc_ef_private_ownership_effects.txt` | свой `hc_private_ownership_production_stocks` — та же пара `if`-ов, что у E&F |
| `common/on_actions/zz_hc_ef_on_actions.txt` | аддитивный хук в `on_yearly_pulse_country` |
| `common/history/global/zz_hc_ef_stocks_init.txt` | тот же вызов на старте игры |

Без последнего файла первый игровой год всё висело бы на «No Stock»: `on_yearly_pulse_country` срабатывает только через год после старта.

## Почему agricultural stock

Не выбор на глаз: у самого E&F в агрокатегории уже лежат добывающие постройки рядом с фермами — `building_logging_camp`, `building_fishing_wharf`, `building_whaling_station` соседствуют с плантациями и `building_livestock_ranch`. Пушной промысел встаёт рядом с китобойным и лесозаготовкой, гиппопотамье ранчо — рядом с ранчо, плантация эспарто — рядом с плантациями.

Один тип акций на все три означает, что **новой группы методов и новой локализации не требуется**: имя группы уже приходит в цепочку из loc-файла `ef+morg done`.

## Что намеренно не тронуто

* `building_usfp_national_park` (HC) и правительственные с монументами у GoB — не `ownership_type = self`, приватным владением быть не могут. Та же логика, по которой `LLWA_building_logistics_hub` не попал в `_llwa/llwa+ef done`.
* Компании. Ни одна компания набора не знает этих трёх зданий — но это раздача, а не потеря, и решается отдельно, как в LLWA.8.

## Пересборка

```
python3 tools/regen_hc_ef.py            # переписать
python3 tools/regen_hc_ef.py --check    # сверить с текущими исходниками, код 1 при расхождении
```

Генератор проверяет перед записью: оба мода всё ещё определяют свои здания в тех же файлах, у всех трёх `ownership_type = self`, E&F всё ещё определяет `pm_no_private_ownership_agricultural_stock` / `pm_private_ownership_majority_agricultural_stock` и `pmg_private_ownership_agricultural_stock`, и **E&F ещё не начал переключать эти здания сам** — иначе наш переключатель дублировал бы его.
