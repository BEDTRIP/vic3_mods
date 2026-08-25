# TGR vs T&R — почему это конфликт / почему нет (сверка 23.08.2026)

**Версии:** TGR 2.0 (`3215078236`, 1.13.10, коммит 12.08.2026) · T&R 1.6 (`tech.res`, 1.13.*, 13.05.2026) · KAI 7.5 (`kai.kuromi`, 24.07.2026).
**Порядок загрузки:** CMF → TGR → KAI → **T&R** → компач. T&R грузится последним из трёх — это изменение относительно комментария в старой версии компача, где было написано «KAI последний». Комментарий был неверен.

**Главное, что изменилось с прошлой сверки:** T&R массово перешёл с `REPLACE:` на `INJECT:`-дельты
(здания кроме двух, компании, `law_industry_banned`, `law_extraction_economy`, `buy_packages`).
Из-за этого больше половины «дубликатов» в машинном отчёте ниже — ложные срабатывания,
зато появились новые настоящие конфликты в `common/laws` (UN-система T&R) и `common/goods`.

## Итог по категориям

| Категория | Ключей в отчёте | Патчим | Почему |
|---|---|---|---|
| `buildings` | 17 | 2 | Только `building_automotive_industry` и `building_synthetics_plant` остались у T&R полным `REPLACE:`. Остальные 15 — `INJECT:`-дельты (только `production_method_groups`), они сливаются с телами TGR сами. Патчим ради `building_group`: TGR держит свои `bg_industry_heavy` / `bg_industry_light` и вешает на них декрет и законы экономических стимулов; `bg_heavy_industry` от T&R — сестринская группа, не родитель, `is_building_group` до неё не дотягивается. Цена выбора: бонусы T&R `building_group_bg_heavy_industry_throughput_add` (±0.01–0.02, законы экологии и две автокомпании) до этих двух зданий не доходят. |
| `company_types` | 6 | 0 (**файл удалён**) | T&R 1.6 перевёл все шесть компаний на `INJECT:` с одними лишь добавками (`building_types`, `extension_building_types`). `INJECT:` в список **добавляет**, а не заменяет, — тела TGR остаются целыми, слияние происходит само. Старый `zz_tr_kai_tgr_company_types.txt` не просто стал не нужен, он **вредил**: там лежали копии тел TGR полугодовой давности (у Krupp — `food_industry/glassworks/chemical_plant` вместо нынешнего `coal_mine`, у LKAB — лишний `motor_industry`), плюс `company_imperial_arsenal`, которого T&R вообще больше не трогает. Файл перенесён в `_to_delete/tgr_tr_kai_2026-08-23/`. |
| `production_methods` | 16 | 9 | 6 железнодорожных PM и 3 портовых — там TGR добавляет `state_market_access_price_impact = 0.05`, которого в ванили нет и о котором T&R не имеет мнения. Порты пересобраны на числах T&R 1.6 (старый компач стоял на 1.5) и из них **убран `country_convoys_capacity_add`**: его выпилили и TGR, и T&R независимо, компач возвращал ёмкость конвоев, которой не хочет ни один автор. Удалены 5 записей, ставших дословными копиями T&R (три `pm_assembly_lines_*`, `pm_automatic_power_looms`, `pm_electric_fencing`) — они не делали ничего. Не патчим `pm_compression_ignition_tractors` и `pm_rail_transport_mine`: расхождение чисто числовое, `state_market_access_price_impact` там ни у кого нет. |
| `laws` | 9 | 4 | См. таблицу ниже. |
| `goods` | 3 | 3 (**новый файл**) | TGR переписывает все 53 ванильных товара, систематически срезая `traded_quantity` и поднимая `convoy_cost_multiplier` — на этом держится его торговая система. T&R переиздаёт ровно три (`aeroplanes`, `automobiles`, `clothes`) с околованильными числами и грузится позже, так что три товара тихо выпадают из оверхола. Мердж: `cost`/`prestige_factor` от T&R, `traded_quantity`/`convoy_cost_multiplier` от TGR. Плюс `obsession_chance` у `aeroplanes` — ваниль и TGR его ставят, T&R при переписывании просто не переносит ключ, и товар молча перестаёт быть obsession. |
| `technology/technologies` | 4 | 1 (**новый файл**) | `atmospheric_engine`, `mechanical_tools` — `INJECT:` с обеих сторон, сливаются. `mutual_funds` — TGR `REPLACE_OR_CREATE:` + T&R `INJECT:`, тоже сливается. `malaria_prevention` — TGR `INJECT:`, T&R `REPLACE_OR_CREATE:` и грузится позже, поэтому строка TGR `country_institution_environment_max_investment_add = 1` теряется. Патчим одной записью. |
| `buy_packages` | 90 | 0 | Ложное срабатывание. TGR определяет `wealth_1..99` без префикса (это переопределяет ваниль), T&R сверху делает `TRY_INJECT:` — аддитивно. Порядок TGR → T&R как раз правильный. |
| `pop_needs` | 6 | 0 | 4 из 6 у T&R — `INJECT:`. `popneed_basic_food` T&R не трогает. Реально спорный один — `popneed_heating`: T&R делает `REPLACE:` и добавляет `gas` и `homeappliances`, TGR правит `max_supply_share`/`min_supply_share`/`weight`. Не патчим: чтобы сохранить схему долей TGR, пришлось бы придумывать доли для двух новых товаров, которых TGR не видел. Это уже ребаланс. |
| `ai_strategies` | 4 | 1 | `ai_strategy_resource_expansion` — TGR и KAI переопределяют, T&R не трогает, побеждает KAI, и у него нет ресурсных товаров T&R. Патчим. `ai_strategy_colonial_extraction` **больше не патчим**: T&R 1.6 сам везёт слитую версию (`kai_has_high_supply` + те же семь товаров) и грузится после KAI. `ai_strategy_industrial_expansion` и `ai_strategy_default` — у обоих полные, осознанно разные стратегии; гейт по `law_industry_banned`/`law_extraction_economy` в версии T&R сохранён, структурно ничего не теряется. |
| `defines`, `on_actions`, `history/*` | — | 0 | `NEconomy`/`NPops` — разные подключи внутри блока; `on_actions` и `history/global`, `history/buildings` аддитивны. |
| `script_values` | 1 | 0 | `wanted_army_size_script_value`: у обоих полностью своя формула, побеждает T&R. Выбрать одну — ребаланс, а не совместимость. |

## Законы: построчно

| Ключ | Ваниль | TGR | T&R 1.6 | Решение |
|---|---|---|---|---|
| `law_industry_banned` | базовый список сноса (8 зданий) | `REPLACE_OR_CREATE:`, тот же список + свои модификаторы | **`INJECT:`** только `on_activate`, список = те же 8 + производства T&R | **Патч удалён.** Список T&R — строгое надмножество, остальное тело TGR `INJECT:` не трогает. Старая запись лишь повторяла то, что и так получается. |
| `law_extraction_economy` | список сноса + `can_enact = is_subject` | список сноса **+ своп централизации** в `on_activate`, `can_enact` с защитой от даты 1836, свои модификаторы, без `disallowing_laws` | **`INJECT:`** `on_activate` со своим списком | **Патч оставлен, тело пересобрано.** `on_activate` — блок, а не список; инъекция T&R встаёт на место TGR-овского, и своп `law_administrative_centralism` → `law_local_autonomies` пропадает **без единой строчки в логе**. В старом компаче тело было от TGR полугодовой давности: плоский `is_subject = yes` вместо защиты по дате (закон отваливался бы на старте 1836), лишние `disallowing_laws` и `state_bureaucrats_investment_pool_efficiency_mult`, которых у TGR больше нет. |
| `law_per_capita_based_taxation`, `law_proportional_taxation` | — | `REPLACE_OR_CREATE:`, у proportional `country_capitalists_pol_str_mult = -0.25` | KAI (не T&R) делает `INJECT:` только `ai_enact_weight_modifier` | **Патч удалён, и это был баг.** Старый компач переписывал оба закона рукописным телом с пустым `modifier = { }` и **молча стирал** `country_capitalists_pol_str_mult = -0.25` у TGR. Инъекция KAI тела TGR не трогает вовсе. Из весов TGR теряется только `has_modifier = shogun_ig_forced_to_open_market` — он дублируется KAI-овским `has_journal_entry = je_meiji_main`. |
| `law_colonial_exploitation`, `law_colonial_resettlement`, `law_frontier_colonization` | — | `REPLACE_OR_CREATE:` + **`institution_modifier`** (`country_engineers_pol_str_mult` / `country_farmers_pol_str_mult = 0.20`) | **`REPLACE:`** целиком, UN-гейтинг, `has_law_or_variant`, `institution_modifier` **отсутствует** | **Новый патч.** Тело T&R + блок `institution_modifier` от TGR. Ключа `institution_modifier` у T&R нет вообще — это чистый перенос, а не спор двух авторов. `progressiveness` (TGR 25 против T&R 0 у двух законов) **не переносим**: там оба автора выставили значение осознанно. |
| `law_no_womens_rights`, `law_women_own_property`, `law_child_labor_allowed`, `law_restricted_child_labor` | — | свои числа | T&R определяет те же ключи (у детских — `INJECT:` только `can_enact`) | **Не патчим.** Расхождение чисто числовое (`state_birth_rate_mult` 0.10 → 0.05, `state_working_adult_ratio_add` 0.10 → 0.05). Взять числа TGR — ребаланс. |

## Товары и потолок 128

Ваниль 53 + T&R 39 + TGR 0 + KAI 0 = **92**. До потолка 128 запас 36. Компач новых товаров не добавляет.

## Чего в этом отчёте нет

Пары TGR × KAI разобраны в `conflicts_tgr_vs_kai_report.md`.

---

Ниже — сырой вывод `tools/scan_conflicts.py` от 23.08.2026, как есть.

# TGR vs T&R — conflict report (key-level heuristic)

- TGR root: `/sessions/rcw-01qfgb8bzfs9xeotduvu9q29/mnt/Projects/vic3_mods_out/TheGreatRevision`
- T&R root: `/sessions/rcw-01qfgb8bzfs9xeotduvu9q29/mnt/Projects/vic3_mods_out/TechRes+Kuromi/t&r`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/ai_strategies — 4 duplicates
- `ai_strategy_colonial_extraction`
  - TGR: `common/ai_strategies/TGR_TRADE_admin_strategies.txt`
  - T&R: `common/ai_strategies/ztr_admin_strategies.txt`
- `ai_strategy_default`
  - TGR: `common/ai_strategies/TGR_ADJUSTMENTS_default_strategy.txt`
  - TGR: `common/ai_strategies/TGR_POLITICS_default_strategy.txt`
  - TGR: `common/ai_strategies/TGR_TRADE_default_strategy.txt`
  - T&R: `common/ai_strategies/ztr_default_strategy.txt`
- `ai_strategy_industrial_expansion`
  - TGR: `common/ai_strategies/TGR_TRADE_admin_strategies.txt`
  - T&R: `common/ai_strategies/ztr_admin_strategies.txt`
- `ai_strategy_resource_expansion`
  - TGR: `common/ai_strategies/TGR_TRADE_admin_strategies.txt`
  - T&R: `common/ai_strategies/ztr_admin_strategies.txt`

### common/buildings — 17 duplicates
- `building_arms_industry`
  - TGR: `common/buildings/TGR_POLITICS_industry.txt`
  - T&R: `common/buildings/ztr_vanilla_optimization_buildings.txt`
- `building_artillery_foundry`
  - TGR: `common/buildings/TGR_POLITICS_industry.txt`
  - T&R: `common/buildings/ztr_vanilla_optimization_buildings.txt`
- `building_automotive_industry`
  - TGR: `common/buildings/TGR_POLITICS_industry.txt`
  - T&R: `common/buildings/ztr_vanilla_modified_buildings.txt`
- `building_chemical_plant`
  - TGR: `common/buildings/TGR_POLITICS_industry.txt`
  - T&R: `common/buildings/ztr_vanilla_modified_buildings.txt`
- `building_electrics_industry`
  - TGR: `common/buildings/TGR_POLITICS_industry.txt`
  - T&R: `common/buildings/ztr_vanilla_modified_buildings.txt`
- `building_explosives_factory`
  - TGR: `common/buildings/TGR_POLITICS_industry.txt`
  - T&R: `common/buildings/ztr_vanilla_modified_buildings.txt`
- `building_food_industry`
  - TGR: `common/buildings/TGR_POLITICS_industry.txt`
  - T&R: `common/buildings/ztr_vanilla_modified_buildings.txt`
- `building_furniture_manufactory`
  - TGR: `common/buildings/TGR_POLITICS_industry.txt`
  - T&R: `common/buildings/ztr_vanilla_optimization_buildings.txt`
- `building_glassworks`
  - TGR: `common/buildings/TGR_POLITICS_industry.txt`
  - T&R: `common/buildings/ztr_vanilla_optimization_buildings.txt`
- `building_motor_industry`
  - TGR: `common/buildings/TGR_POLITICS_industry.txt`
  - T&R: `common/buildings/ztr_vanilla_optimization_buildings.txt`
- `building_munition_plant`
  - TGR: `common/buildings/TGR_POLITICS_industry.txt`
  - T&R: `common/buildings/ztr_vanilla_modified_buildings.txt`
- `building_paper_mill`
  - TGR: `common/buildings/TGR_POLITICS_industry.txt`
  - T&R: `common/buildings/ztr_vanilla_optimization_buildings.txt`
- `building_shipyard`
  - TGR: `common/buildings/TGR_POLITICS_industry.txt`
  - T&R: `common/buildings/ztr_vanilla_optimization_buildings.txt`
- `building_steel_mill`
  - TGR: `common/buildings/TGR_POLITICS_industry.txt`
  - T&R: `common/buildings/ztr_vanilla_modified_buildings.txt`
- `building_synthetics_plant`
  - TGR: `common/buildings/TGR_POLITICS_industry.txt`
  - T&R: `common/buildings/ztr_vanilla_modified_buildings.txt`
- `building_textile_mill`
  - TGR: `common/buildings/TGR_POLITICS_industry.txt`
  - T&R: `common/buildings/ztr_vanilla_optimization_buildings.txt`
- `building_tooling_workshop`
  - TGR: `common/buildings/TGR_POLITICS_industry.txt`
  - T&R: `common/buildings/ztr_vanilla_optimization_buildings.txt`

### common/buy_packages — 90 duplicates
- `wealth_10`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_11`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_12`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_13`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_14`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_15`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_16`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_17`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_18`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_19`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_20`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_21`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_22`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_23`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_24`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_25`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_26`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_27`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_28`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_29`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_30`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_31`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_32`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_33`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_34`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_35`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_36`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_37`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_38`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_39`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_40`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_41`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_42`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_43`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_44`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_45`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_46`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_47`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_48`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_49`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_50`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_51`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_52`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_53`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_54`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_55`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_56`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_57`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_58`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_59`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_60`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_61`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_62`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_63`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_64`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_65`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_66`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_67`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_68`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_69`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_70`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_71`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_72`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_73`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_74`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_75`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_76`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_77`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_78`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_79`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_80`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_81`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_82`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_83`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_84`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_85`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_86`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_87`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_88`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_89`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_90`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_91`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_92`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_93`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_94`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_95`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_96`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_97`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_98`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`
- `wealth_99`
  - TGR: `common/buy_packages/00_buy_packages.txt`
  - T&R: `common/buy_packages/ztr_buy_packages.txt`

### common/company_types — 6 duplicates
- `company_altos_hornos_de_vizcaya`
  - TGR: `common/company_types/TGR_TRADE_companies.txt`
  - T&R: `common/company_types/ztr_companies_europe.txt`
- `company_east_india_company`
  - TGR: `common/company_types/TGR_TRADE_companies.txt`
  - T&R: `common/company_types/ztr_companies_asia.txt`
- `company_krupp`
  - TGR: `common/company_types/TGR_TRADE_companies.txt`
  - T&R: `common/company_types/ztr_companies_germany.txt`
- `company_lkab`
  - TGR: `common/company_types/TGR_TRADE_companies.txt`
  - T&R: `common/company_types/ztr_companies_europe.txt`
- `company_philips`
  - TGR: `common/company_types/TGR_TRADE_companies.txt`
  - T&R: `common/company_types/ztr_companies_europe.txt`
- `company_united_fruit`
  - TGR: `common/company_types/TGR_TRADE_companies.txt`
  - T&R: `common/company_types/ztr_companies_usa.txt`

### common/defines — 2 duplicates
- `NEconomy`
  - TGR: `common/defines/TGR_TRADE_defines.txt`
  - T&R: `common/defines/ztr_defines.txt`
- `NPops`
  - TGR: `common/defines/TGR_POPS_defines.txt`
  - TGR: `common/defines/TGR_TRADE_defines.txt`
  - T&R: `common/defines/ztr_defines.txt`

### common/goods — 3 duplicates
- `aeroplanes`
  - TGR: `common/goods/TGR_TRADE_goods.txt`
  - T&R: `common/goods/ztr_vanilla_goods.txt`
- `automobiles`
  - TGR: `common/goods/TGR_TRADE_goods.txt`
  - T&R: `common/goods/ztr_vanilla_goods.txt`
- `clothes`
  - TGR: `common/goods/TGR_TRADE_goods.txt`
  - T&R: `common/goods/ztr_vanilla_goods.txt`

### common/history/buildings — 1 duplicates
- `BUILDINGS`
  - TGR: `common/history/buildings/TGR_TRADE_austria_setup.txt`
  - TGR: `common/history/buildings/TGR_TRADE_net_setup.txt`
  - TGR: `common/history/buildings/TGR_TRADE_ottomans_setup.txt`
  - TGR: `common/history/buildings/TGR_TRADE_russia_setup.txt`
  - TGR: `common/history/buildings/TGR_TRADE_spain_setup.txt`
  - T&R: `common/history/buildings/elgar_opera.txt`
  - T&R: `common/history/buildings/manzoni_printing.txt`
  - T&R: `common/history/buildings/mr_buildings.txt`
  - T&R: `common/history/buildings/ztr_buildings.txt`

### common/history/global — 1 duplicates
- `GLOBAL`
  - TGR: `common/history/global/TGR_LOANS_global.txt`
  - TGR: `common/history/global/TGR_POLITICS_global.txt`
  - TGR: `common/history/global/TGR_TAX_PANEL_global.txt`
  - TGR: `common/history/global/TGR_TRADE_global.txt`
  - TGR: `common/history/global/TGR_TRADE_obsessions.txt`
  - T&R: `common/history/global/ztr_global.txt`

### common/laws — 9 duplicates
- `law_child_labor_allowed`
  - TGR: `common/laws/TGR_POLITICS_childrens_rights.txt`
  - T&R: `common/laws/ztr_un_updated_children_rights.txt`
- `law_colonial_exploitation`
  - TGR: `common/laws/TGR_POLITICS_colonial_affairs.txt`
  - T&R: `common/laws/ztr_un_updated_colonial_affairs.txt`
- `law_colonial_resettlement`
  - TGR: `common/laws/TGR_POLITICS_colonial_affairs.txt`
  - T&R: `common/laws/ztr_un_updated_colonial_affairs.txt`
- `law_extraction_economy`
  - TGR: `common/laws/TGR_POLITICS_economic_system.txt`
  - T&R: `common/laws/ztr_economic_system.txt`
- `law_frontier_colonization`
  - TGR: `common/laws/TGR_POLITICS_colonial_affairs.txt`
  - T&R: `common/laws/ztr_un_updated_colonial_affairs.txt`
- `law_industry_banned`
  - TGR: `common/laws/TGR_POLITICS_economic_system.txt`
  - T&R: `common/laws/ztr_economic_system.txt`
- `law_no_womens_rights`
  - TGR: `common/laws/TGR_POLITICS_rights_of_women.txt`
  - T&R: `common/laws/ztr_un_updated_rights_of_women.txt`
- `law_restricted_child_labor`
  - TGR: `common/laws/TGR_POLITICS_childrens_rights.txt`
  - T&R: `common/laws/ztr_un_updated_children_rights.txt`
- `law_women_own_property`
  - TGR: `common/laws/TGR_POLITICS_rights_of_women.txt`
  - T&R: `common/laws/ztr_un_updated_rights_of_women.txt`

### common/on_actions — 2 duplicates
- `on_monthly_pulse_country`
  - TGR: `common/on_actions/TGR_ADJUSTMENTS_code_on_actions.txt`
  - TGR: `common/on_actions/TGR_GER_UNIFICATION_code_on_actions.txt`
  - TGR: `common/on_actions/TGR_ITA_UNIFICATION_code_on_actions.txt`
  - T&R: `common/on_actions/ztr_on_actions.txt`
- `on_yearly_pulse_country`
  - TGR: `common/on_actions/TGR_ADJUSTMENTS_code_on_actions.txt`
  - TGR: `common/on_actions/TGR_GER_UNIFICATION_code_on_actions.txt`
  - TGR: `common/on_actions/TGR_ITA_UNIFICATION_code_on_actions.txt`
  - TGR: `common/on_actions/TGR_POLITICS_gain_ideology.txt`
  - TGR: `common/on_actions/TGR_TRADE_code_on_actions.txt`
  - T&R: `common/on_actions/ztr_on_actions.txt`

### common/pop_needs — 6 duplicates
- `popneed_basic_food`
  - TGR: `common/pop_needs/TGR_TRADE_pop_needs.txt`
  - T&R: `common/pop_needs/ztr_pop_needs.txt`
- `popneed_heating`
  - TGR: `common/pop_needs/TGR_TRADE_pop_needs.txt`
  - T&R: `common/pop_needs/ztr_pop_needs.txt`
- `popneed_household_items`
  - TGR: `common/pop_needs/TGR_TRADE_pop_needs.txt`
  - T&R: `common/pop_needs/ztr_pop_needs.txt`
- `popneed_intoxicants`
  - TGR: `common/pop_needs/TGR_TRADE_pop_needs.txt`
  - T&R: `common/pop_needs/ztr_pop_needs.txt`
- `popneed_luxury_drinks`
  - TGR: `common/pop_needs/TGR_TRADE_pop_needs.txt`
  - T&R: `common/pop_needs/ztr_pop_needs.txt`
- `popneed_luxury_food`
  - TGR: `common/pop_needs/TGR_TRADE_pop_needs.txt`
  - T&R: `common/pop_needs/ztr_pop_needs.txt`

### common/production_methods — 16 duplicates
- `pm_assembly_lines_building_arms_industry`
  - TGR: `common/production_methods/TGR_TRADE_automation.txt`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
- `pm_assembly_lines_building_automotive_industry`
  - TGR: `common/production_methods/TGR_TRADE_automation.txt`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
- `pm_assembly_lines_building_motor_industry`
  - TGR: `common/production_methods/TGR_TRADE_automation.txt`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
- `pm_automatic_power_looms`
  - TGR: `common/production_methods/TGR_TRADE_automation.txt`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
- `pm_basic_port`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_ports.txt`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
- `pm_compression_ignition_tractors`
  - TGR: `common/production_methods/TGR_TRADE_automation.txt`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
- `pm_diesel_trains`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
- `pm_diesel_trains_principle_transport_3`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
- `pm_electric_fencing`
  - TGR: `common/production_methods/TGR_TRADE_automation.txt`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
- `pm_electric_trains`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
- `pm_electric_trains_principle_transport_3`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
- `pm_industrial_port`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_ports.txt`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
- `pm_modern_port`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_ports.txt`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
- `pm_rail_transport_mine`
  - TGR: `common/production_methods/TGR_TRADE_automation.txt`
  - T&R: `common/production_methods/ztr_new_production_methods.txt`
- `pm_steam_trains`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
- `pm_steam_trains_principle_transport_3`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`

### common/script_values — 1 duplicates
- `wanted_army_size_script_value`
  - TGR: `common/script_values/TGR_TAX_PANEL_ai_script_values.txt`
  - T&R: `common/script_values/ztr_ai_script_values.txt`

### common/technology/technologies — 4 duplicates
- `atmospheric_engine`
  - TGR: `common/technology/technologies/TGR_POLITICS_production.txt`
  - T&R: `common/technology/technologies/ztr_modified_vanilla_production.txt`
- `malaria_prevention`
  - TGR: `common/technology/technologies/TGR_POLITICS_society.txt`
  - T&R: `common/technology/technologies/ztr_mr_society.txt`
- `mechanical_tools`
  - TGR: `common/technology/technologies/TGR_POLITICS_production.txt`
  - T&R: `common/technology/technologies/ztr_modified_vanilla_production.txt`
- `mutual_funds`
  - TGR: `common/technology/technologies/TGR_LOANS_society.txt`
  - TGR: `common/technology/technologies/TGR_TRADE_society.txt`
  - T&R: `common/technology/technologies/ztr_modified_vanilla_society.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**