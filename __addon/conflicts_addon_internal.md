# Аддон к мегапаку: gatesofbosphorus + hailcolumbia + mandateofheaven — разбор совместимости

Дата сверки: 2026-08-24. Игра 1.13, все три мода объявляют `supported_game_version = 1.13.*`.

## Что и как проверялось

Проверяемый набор (в порядке загрузки по README мегапака):

```
Community Mod Framework 1.63.0
Expanded Topbar Framework
The Great Revision (TGR)
Private Sector Construction (PSC)
Kuromi's AI (KAI)
E&F
E&F Hotfix 1.13
Morgenrote
Tech & Res (T&R)
Power Blocs Expanded (PBE)
MegaComPatch  (__megapacks/megapack)
--- дальше аддон ---
[1.13] Gates of the Bosphorus  4.0.8   (id 3384997867)
Hail, Columbia!                8.6-Roosevelt  (id пустой)
Mandate of Heaven              1.4.6.1 (id top.sleepingbed.moh)
```

Все три мода аддона объявляют `dependency` на Community Mod Framework — CMF в наборе уже есть, требование выполнено.

Прогоны:

* `scan_conflicts.py --a --b` — 33 пары: каждый мод аддона против каждого мода набора, мегапака и CMF, плюс три пары внутри аддона.
* Пересечения **по путям файлов** (`scan_conflicts.py` их не ловит) — отдельным проходом, включая перекрытия ванильных путей.
* Ручной разбор каждого найденного пересечения: сравнение тел записей с ванилью, сравнение **набора под-блоков** у `REPLACE:` (кто что реально перекрывает).
* Товары против потолка 128 по виртуальной ФС; престижные товары на базовый товар; `.gui`; `common/defines`; id событий; локализация по языкам; `common/history/*` по скоупам штатов и стран.

Ваниль (`.vanillaVIC3`) использовалась как база сравнения.

---

## Короткий ответ

«Вообще независимые» — не подтвердилось. Между собой три мода почти чисты (одно место, и то безобидное). **С набором конфликтов одиннадцать**, из них один тяжёлый и три заметных. Все — молчаливые: ни строчки в `error.log`, игра грузится и играется, просто часть механик модов набора перестаёт существовать.

| # | Что | Кто теряет | Тяжесть |
|---|-----|-----------|---------|
| 1 | MoH `REPLACE:ai_strategy_default` | KAI целиком, T&R, TGR | **высокая** |
| 2 | HC `ig_landowners` / `ig_rural_folk` без префикса | TGR | средняя |
| 3 | HC `REPLACE:` четырёх законов рабства | T&R (UN-гейт) | средняя |
| 4 | GoB placeholder `gaudi_capital_expansion_level_4_modifier` | Morgenrote | средняя |
| 5 | MoH `REPLACE:je_warlord_china` | T&R | средняя |
| 6 | GoB `REPLACE:revive_olympic_games_decision` | Morgenrote | низкая |
| 7 | MoH `common/achievement_groups.txt` | Morgenrote | низкая (косметика) |
| 8 | HC `common/decisions/manifest_destiny.txt` | TGR | низкая (замысел) |
| 9 | GoB `tur - ottoman empire.txt` | TGR | низкая |
| 10 | MoH `chi - china.txt` | TGR | низкая |
| 11 | HC `REPLACE_OR_CREATE:ideology_jacksonian_democrat` | TGR | низкая |
| + | 22 файла `dna_data` / `character_templates` | Morgenrote | косметика |

Отдельно: **предсуществующая проблема набора** — Morgenrote гасит детект CMF (см. раздел «CMF»), и это меняет то, как все три новых мода цепляются к фреймворку.

---

## 1. MoH затирает весь ИИ набора

`mandateofheaven/common/ai_strategies/moh_default_strategy.txt` — это **полная копия ванильного `00_default_strategy.txt`** с пометкой `REPLACE:`. Она называет все 59 под-блоков `ai_strategy_default`.

Что в набор кладут остальные:

| мод | файл | под-блоки |
|-----|------|-----------|
| KAI | `common/ai_strategies/00_default_strategy.txt` (полная копия, без префикса) | 59, реально отличаются от ванили **12** |
| T&R | `ztr_default_strategy.txt` `INJECT:` | `institution_scores`, `aggression`, `building_group_weights`, `subsidies`, `goods_stances` |
| TGR | `TGR_POLITICS_default_strategy.txt` `INJECT:` | `icon`, `institution_scores` |
| TGR | `TGR_TRADE_default_strategy.txt` `INJECT:` | `wanted_construction_output`, `combat_unit_group_weights`, `conscript_battalion_ratio` |
| TGR | `TGR_ADJUSTMENTS_default_strategy.txt` `INJECT:` | `icon`, `diplomatic_play_support` |

MoH грузится последним и называет **все** эти под-блоки → **выживает ноль**. Kuromi's AI в наборе перестаёт существовать как мод; торговый и политический ИИ TGR и правки T&R откатываются в ваниль. В логе ничего.

Хорошая новость: реальные дельты обоих полных файлов от ванили небольшие и почти не пересекаются.

* KAI меняет 12 под-блоков: `building_group_weights`, `diplomatic_play_support`, `fleet_compositions`, `goods_stances`, `liberate_country_scores`, `max_active_stances`, `secret_goal_scores`, `strategic_region_scores`, `subsidies`, `wanted_construction_output`, `wanted_num_supply_ships`, `wargoal_scores`
* MoH меняет 9: `aggression`, `diplomatic_play_support`, `liberate_country_scores`, `recklessness`, `state_value`, `strategic_region_scores`, `subject_value`, `treaty_port_value`, `wargoal_scores`
* Пересекаются только 4: `diplomatic_play_support`, `liberate_country_scores`, `strategic_region_scores`, `wargoal_scores`

**Чинится** файлом `common/ai_strategies/zzzz_addon_ai_default.txt` в компаче аддона (грузится после MoH), `REPLACE:ai_strategy_default` с телами:

* 8 под-блоков берём у KAI как есть (MoH их не трогал): `building_group_weights`*, `fleet_compositions`, `goods_stances`*, `max_active_stances`, `secret_goal_scores`, `subsidies`*, `wanted_construction_output`*, `wanted_num_supply_ships`
* 4 под-блока — трёхсторонний мердж ваниль/KAI/MoH: `diplomatic_play_support` (+ вставка TGR_ADJUSTMENTS), `liberate_country_scores`, `strategic_region_scores`, `wargoal_scores`
* 4 под-блока восстановить из `INJECT:` T&R и TGR: `institution_scores` (T&R + TGR), `combat_unit_group_weights`, `conscript_battalion_ratio` (TGR), `aggression` (T&R + MoH)
* 5 под-блоков оставить MoH-евские, там ничего не потеряно: `recklessness`, `state_value`, `subject_value`, `treaty_port_value` и `icon`

\* эти под-блоки KAI-версии ещё и дополняются `INJECT:` от T&R/TGR — мердж делать по цепочке KAI → T&R → TGR.

Это работа для генератора в `tools/` (три исходника + ваниль), руками собирать 15 под-блоков на 7900 строк не стоит.

## 2. HC затирает две группы интересов TGR

`hailcolumbia/common/interest_groups/00_landowners.txt` и `00_rural_folk.txt` определяют `ig_landowners` / `ig_rural_folk` **без префикса** — то есть переопределяют запись целиком. TGR определяет обе через `REPLACE_OR_CREATE:` (`TGR_POLITICS_landowners.txt`, `TGR_POLITICS_rural_folk.txt`). HC грузится позже → TGR отваливается.

Потери маленькие и точечные (сравнение с ванилью):

* `ig_rural_folk`: TGR меняет `value = 200 → 250`, второе `value = 200 → 150`, `multiply = 0.0025 → 0.030`
* `ig_landowners`: TGR меняет `multiply = 0.0025 → 0.030`

HC меняет в тех же файлах другое — культурные гейты (`usfp_country_is_american`, `cu:usfp_american`, ветка про рабовладельческие штаты у landowners). Пересечения по строкам нет.

**Чинится** копией HC-версии обоих файлов с внесёнными четырьмя числами TGR, под теми же именами `00_landowners.txt` / `00_rural_folk.txt` (перекрытие по пути — тогда файл в аддоне один, а не два).

`INJECT:ig_rural_folk` / `ig_petty_bourgeoisie` / `ig_intelligentsia` / `ig_armed_forces` у MoH ложатся поверх этого и в конфликт не входят — но порядок внутри аддона важен: файлы MoH (`moh_*.txt`) обязаны идти после файлов HC (`00_*.txt`). При склейке в один мод это выполняется само (`0` < `m`).

## 3. HC затирает UN-гейт T&R в законах рабства

`usfp_law_slavery_overrides.txt` и `ztr_un_updated_slavery.txt` оба делают `REPLACE:` на `law_colonial_slavery`, `law_debt_slavery`, `law_slave_trade`, `law_legacy_slavery`.

T&R добавляет в `can_enact` каждого из четырёх гейт по правам человека ООН:

```
custom_tooltip = {
    text = ztr_un_hr_illegalized_slavery_tt
    OR = {
        NOT = { ztr_is_un_member = yes }
        NOT = { global_var:ztr_un_hr_slavery = 1 }
    }
}
```

плюс ветки под BPM. HC добавляет в `can_enact` свои гейты (`doesnt_have_gag_rule`, `not_has_corwin_amendment`). HC грузится позже:

* `law_colonial_slavery`, `law_debt_slavery`, `law_slave_trade` — HC называет `can_enact` → **гейт ООН пропадает**, рабство можно принять вопреки решению ООН
* `law_legacy_slavery` — HC `can_enact` не называет, гейт ООН выживает

Отдельная находка: **`REPLACE:law_legacy_slavery` у HC — дословная ваниль**, 82 строки против 82 ванильных, отличается только строка с префиксом. Он ничего не добавляет и при этом откатывает правки T&R в `on_activate`, `modifier`, `ai_enact_weight_modifier` и остальных названных под-блоках. Это чистая потеря без выигрыша — в компаче этот блок надо просто выкинуть.

**Чинится** файлом `zzzz_addon_slavery_laws.txt`: три закона с телом HC + вставленным гейтом ООН в `can_enact`; `law_legacy_slavery` не трогать вообще.

## 4. GoB обнуляет модификатор Гауди у Morgenrote

`gatesofbosphorus/common/static_modifiers/zz_gbbf_placeholder_modifiers.txt` целиком:

```
gaudi_capital_expansion_level_4_modifier = {
	icon = gfx/interface/icons/timed_modifier_icons/modifier_framing_positive.dds
}
```

Это заглушка на случай, когда Morgenrote не установлен (GoB ссылается на этот модификатор в `1-20_grefm_byzantium.txt`). Но Morgenrote **установлен и грузится раньше**, а ключ без префикса переопределяет. Настоящее тело MR:

```
state_infrastructure_add = 20
state_urbanization_per_level_mult = -0.1
state_migration_pull_mult = 0.1
state_conscription_rate_mult = 0.1
state_tax_capacity_mult = 0.2
state_mortality_mult = -0.03
state_birth_rate_mult = 0.02
```

Итог: четвёртый уровень расширения столицы у Гауди даёт пустой модификатор. Симптом молчаливый, в панели штата модификатор виден и ничего не делает.

**Чинится** одним из двух: (а) при склейке аддона просто не брать файл `zz_gbbf_placeholder_modifiers.txt`; (б) файлом `zzzz_addon_gaudi.txt` с настоящим телом MR. Вариант (б) надёжнее, если аддон остаётся набором отдельных модов.

## 5. MoH затирает ветку T&R в `je_warlord_china`

Оба делают `REPLACE:je_warlord_china` (T&R — `ztr_vanilla_je.txt`, MoH — `moh_warlord_china.txt`). MoH называет все под-блоки, которые называет T&R, плюс `modifiers_while_active`.

T&R добавляет к ванили развилку по году: до 1940 — `warlord_china_events.200`, после — `the_future_of_china.201`. С MoH эта ветка не выполняется никогда, событие `the_future_of_china.201` из этого JE недостижимо (проверить, зовётся ли оно ещё откуда-то — по грепу больше нигде).

MoH переписывает JE глубоко (мандат Неба, Формоза, `modifiers_while_active`), так что механический мердж тут не проходит: нужно решить, чья версия китайской раздробленности главная. Если MoH — то это осознанная потеря, её надо записать; если нужна ветка T&R — перенести `if year > 1940` в тело MoH.

## 6. GoB затирает олимпийское решение Morgenrote

Morgenrote — `TRY_REPLACE:revive_olympic_games_decision`, GoB — `REPLACE:` того же ключа, и **набор под-блоков совпадает полностью** (`is_shown`, `possible`, `when_taken`, `ai_chance`). GoB позже → версия MR не существует.

Тут надо решить по содержанию: у GoB это часть греческого контента, у MR — своя переработка. Мердж делать на структуре GoB (грузится последним) и переносить содержательные отличия MR.

## 7. MoH затирает группы достижений Morgenrote

`common/achievement_groups.txt` — ванильный файл, который оба мода перекрывают **по пути** целиком: Morgenrote 306 строк (ваниль + свои), MoH 175 (ваниль + четыре своих). MoH позже → в экране достижений пропадают группы Morgenrote.

Ачивки HC (`usfp_achievements.txt`) все закомментированы, их учитывать не надо.

**Чинится** тривиально: в аддон кладётся `common/achievement_groups.txt` = файл Morgenrote + четыре записи MoH (`achievement_wuxu_reform`, `achievement_white_sun`, `achievement_different_routes`, `achievement_dream`).

## 8. HC убивает Manifest Destiny вместе с версией TGR

`hailcolumbia/common/decisions/manifest_destiny.txt` — файл, в котором **всё закомментировано**. Это способ HC удалить ванильное решение (у него своя система через `je_usfp_american_constitution`). TGR держит по тому же пути свою версию с `REPLACE_OR_CREATE:` — она добавляет `trigger_event = { id = great_revision_events.5 }` (Мексикано-американская война), модификатор `great_revision_usa_manifest_destiny` и `ai_chance = 9999`.

Побеждает файл HC → у TGR остаются мёртвыми: событие `great_revision_events.5` (со всей локализацией на 11 языков) и статический модификатор. По грепу больше ниоткуда не зовутся.

Скорее всего это приемлемо — HC как раз и существует, чтобы переписать американский контент. Но записать это надо явно, иначе в следующий раз будешь искать, почему у TGR не срабатывает мексиканская война.

## 9–10. Стартовые компании TGR у Османов и Китая

TGR добавляет в ванильные файлы истории стран ровно по одному блоку:

* `common/history/countries/tur - ottoman empire.txt` → `company_imperial_arsenal`, 1832, `s:STATE_EASTERN_THRACE`
* `common/history/countries/chi - china.txt` → `company_ong_lung_sheng_tea_company`, 1820, `s:STATE_FUJIAN`

GoB и MoH перекрывают оба файла по пути своими версиями. Компании TGR у Османов и Китая на старте не создаются.

**Чинится** двумя строчками: в компаче аддона положить те же два пути с телом GoB/MoH + блоком `add_company` от TGR. Заодно у MoH проверить `set_variable = ryukyu_rival_member` — в ванильном `chi - china.txt` он есть, надо убедиться, что MoH его не потерял.

## 11. `ideology_jacksonian_democrat`

HC — `REPLACE_OR_CREATE:` (полное переопределение, называет `lawgroup_governance_principles`, `distribution_of_power`, `bureaucracy`, `colonization`, `land_reform`). TGR — `INJECT:` с `lawgroup_election_system` и `lawgroup_legislative_process`. HC позже → две группы законов от TGR у джексоновских демократов пропадают.

Чинится добавлением двух блоков TGR в HC-версию идеологии.

## Косметика: dna_data и character_templates

GoB и HC везут собственные редакции файлов Morgenrote и переопределяют их по пути. Все отличаются от MR-овских:

* GoB, 18 файлов `common/dna_data/mr_*` — греческие, румынские, черногорские, боснийские, болгарские, турецкие персонажи
* HC, 2 файла `common/dna_data/ecchi_usa_chrysler.txt`, `ecchi_usa_lindbergh.txt`
* HC, `usa_mark_twain_character_template` (у MR — `TRY_REPLACE:`) и `ecchi_usa_chrysler_character_template`

Это внешность и характеристики персонажей. Механик не задевает, чинить не обязательно — но если решишь, что портреты MR лучше, файлы просто не брать в сборку.

---

## CMF: предсуществующая проблема набора

`community_framework_is_active` — триггер, которым CMF сообщает модам «я здесь».

| мод | как объявлен | значение |
|-----|--------------|----------|
| CMF | `REPLACE_OR_CREATE:` | `yes` |
| **Morgenrote** | `REPLACE_OR_CREATE:` | **`no`** |
| HC | без префикса | `no` |
| MoH | без префикса | `no` |

Morgenrote грузится **после** CMF и своим `REPLACE_OR_CREATE:` переводит триггер в `no` — это фолбэк-заглушка «CMF не установлен», которая в этом наборе срабатывает не по делу. Заглушки HC и MoH безобидны: у `scripted_triggers` простой повтор ключа не переопределяет.

Что от этого едет:

* Morgenrote рисует свою автономную кнопку главного окна вместо того, чтобы жить в топбаре CMF (`MR_general_main_window_sguis.txt:112`)
* MoH идёт по той же ветке (`moh_sguis.txt:6`) — тоже своё окно
* GoB: `gbbf_dependencies_sguis` имеет `is_valid = { community_framework_is_active = yes }` — не проходит

Это не аддон сломал, но аддон делает проблему заметнее (три новых мода, все завязаны на CMF). Одна строка в компаче лечит всё сразу:

```
# common/scripted_triggers/zzzz_addon_cmf_detection.txt
REPLACE_OR_CREATE:community_framework_is_active = { always = yes }
```

Файл обязан грузиться после Morgenrote и после обоих модов аддона, и обязан быть `REPLACE_OR_CREATE:` — для `scripted_triggers` без префикса переопределения не будет.

Свои детект-триггеры все три мода объявляют правильно (`REPLACE_OR_CREATE:` поверх заглушек CMF со значением `no`):
`grefm_is_active = yes` (GoB), `is_usfp_active = yes` (HC), `mandate_o_h_is_active = yes` (MoH).

---

## Что проверено и конфликтом не является

**Заглушки CMF.** CMF везёт урезанные копии файлов этих модов, чтобы работать без них:

* `common/script_values/00_usfp_party_values.txt` (`value = 0`), `localization/*/usfp_parties_l_*.yml` (короче на 11 ключей) — HC перекрывает их по пути настоящими
* `localization/*/moh_parties_l_*.yml` — MoH перекрывает
* `common/ideologies/00_dummy_ideologies_gbbf.txt` — 11 пустышек, GoB определяет настоящие

Аддон грузится после CMF, порядок правильный, всё работает как задумано авторами фреймворка.

**Законы MoH.** `INJECT:law_canton_system` кладёт `country_max_companies_add = 1` в `modifier` — у ключей модификаторов сложение, у TGR такого ключа нет, чистое добавление. `INJECT:law_theocracy` кладёт `is_visible`, а TGR в своём `REPLACE_OR_CREATE:law_theocracy` `is_visible` не называет. Оба чисты.

**`decree_greener_grass_campaign`.** T&R инжектит `country_trigger`, HC своим `REPLACE:` называет `texture`, `state_trigger`, `modifier`, `unlocking_technologies`, `cost`, `ai_weight` — `country_trigger` не тронут, правка T&R выживает.

**`ideology_communist`.** TGR инжектит `lawgroup_working_hours`, MoH — `interest_group_leader_weight`. Разные под-блоки.

**`pmg_luxury_building_glassworks`.** Три `INJECT:` в один список (Morgenrote `TRY_INJECT:`, T&R, MoH) — добавление, а не замена.

**`common/history/*`.** Пересечения по скоупам штатов (`gob↔ef` 3, `hc↔ef` 8, `moh↔ef` 1, `gob↔moh` STATE_ALTAI) — все стороны применяют аддитивные эффекты (`add_modifier`, `add_homeland`, `add_state_trait`), а не `create_state`. `BUILDINGS` и `GLOBAL` аддитивны по правилу движка. Пересечения по `common/history/buildings` (EASTERN_THRACE, NEW_YORK, BEIJING, GUANGDONG и др.) — тоже аддитивны.

**`common/on_actions`.** Пересечения ключей во всех парах — аддитивная категория.

**`common/named_colors` `colors`.** Ключ общий у GoB, HC, E&F, T&R. Набор уже так работает без аддона, конструкция та же.

**`.gui`.** Пересечений путей у аддона с набором нет вообще. `mandateofheaven/gui/frontend/frontend_main.gui` — перекрытие ванильного пути, но по содержанию это **побайтовая ваниль 1.13** (836 строк, отличия только в пробелах и переносах). Виджеты на месте, вылета нет. На заметку в maintenance: после патча игры этот файл будет молча держать старую версию главного меню.

**`common/defines`.** HC трогает только `NAI = { NUM_GROWING_COLONIES_MAX }`. KAI и TGR правят `NAI`, но других ключей — пересечений ноль.

**Id событий.** 0 дублей во всех 33 парах.

**Локализация.** Дубли только в двух местах:

* HC ↔ E&F, 8 ключей через `localization/*/replace/usfp_replace_l_*.yml`: `je_oregon`, `je_oregon_reason`, `oregon_tt`, `native_resettlement.6.{a,d,f,t}`, `country_voting_power_from_literacy_add`. Папка `replace/` выигрывает всегда — тексты E&F по этим ключам не покажутся. Косметика, но `country_voting_power_from_literacy_add` стоит глянуть: E&F менял этот модификатор, а тултип будет от HC.
* HC ↔ MoH, 69 ключей `ecchi_*` (имена американских исторических персонажей). У HC они в `replace/`, у MoH в обычной папке → HC выигрывает по английскому и корейскому, `simp_chinese` остаётся от MoH. Не проблема.

---

## Числовые проверки

**Товары: 106 из 128, без изменений.** Считано по виртуальной ФС (проход по порядку загрузки, поздний файл перекрывает ранний по пути, потом считаются ключи, создаваемые впервые). Цифра совпадает с README мегапака, метод сходится: ваниль 53 + T&R 35 + E&F-с-хотфиксом 8 + Morgenrote 5 + PSC 4 + мегапак 1.

`mandateofheaven/common/goods/moh_goods.txt` **новых товаров не добавляет** — там всё закомментировано либо `REPLACE:`/`INJECT:` существующих. Запас до вылета остаётся 22 товара.

**Престижные товары, потолок 3 на базовый товар.** Аддон добавляет три штуки, и ни один слот не переполняет:

| базовый товар | было | аддон добавляет | стало |
|---|---|---|---|
| `liquor` | 2 | `prestige_good_usfp_coca_cola` (HC) | 3 |
| `fine_art` | 1 | `prestige_good_usfp_hollywood_movies` (HC) | 2 |
| `grain` | 2 | `prestige_bicycle_flour` (MoH) | 3 |

**Предсуществующие переполнения** (не аддон, но раз уж посчитано — четвёртые объявления молча падают в третий слот):

* `manufacture_stock` — 4 (E&F: construction, gbr, gbr_2, usa)
* `railroad_stock` — 4 (E&F: usa, fra, ger, rus)
* `telephones` — 4 (ваниль ericsson + T&R smartphones, apple_iphones, nokia_phones)
* `clothes` — 4 (ваниль generic + T&R levis_denim, nike_shoes, adidas_shoes)

Стоит проверить отдельно от аддона.

---

## Внутри аддона: три мода между собой

Практически чисто.

* Единственное содержательное пересечение — `ig_rural_folk`: HC определяет запись целиком, MoH инжектит в неё. Порядок HC → MoH обязателен, и он выполняется сам (`00_rural_folk.txt` < `moh_rural_folk.txt` при склейке; в списке модов MoH и так после HC).
* GoB ↔ MoH: `s:STATE_ALTAI` в `history/states` — у GoB `add_homeland = cu:altaic`, у MoH `set_state_name` + `add_state_trait`. Аддитивно.
* 69 ключей `ecchi_*` в локализации — разобрано выше.
* Остальное в отчётах пар — обёртки `history/*`, `on_actions`, `colors`.

`common/goods`, `common/buildings`, `common/production_methods`, `common/company_types`, `common/technology/technologies`, `common/cultures`, `common/country_definitions`, `common/journal_entries` — ни одного общего ключа ни внутри аддона, ни с набором (кроме перечисленного выше). Три мода действительно почти не пересекаются контентом, всё найденное — это переопределения ванильных записей, которые каждый из них делает независимо.

---

## Что делать дальше

Минимальный компач аддона — семь файлов:

1. `common/ai_strategies/zzzz_addon_ai_default.txt` — генератором, самая большая работа
2. `common/interest_groups/00_landowners.txt` + `00_rural_folk.txt` — HC + четыре числа TGR
3. `common/laws/zzzz_addon_slavery_laws.txt` — три закона, гейт ООН обратно; `law_legacy_slavery` выкинуть
4. `common/static_modifiers/zzzz_addon_gaudi.txt` — тело модификатора Morgenrote
5. `common/achievement_groups.txt` — Morgenrote + четыре записи MoH
6. `common/history/countries/tur - ottoman empire.txt` + `chi - china.txt` — GoB/MoH + `add_company` от TGR
7. `common/scripted_triggers/zzzz_addon_cmf_detection.txt` — `community_framework_is_active = yes`

Плюс два решения, которые за тебя принять нельзя:

* **`je_warlord_china`** — чья версия китайской раздробленности главная, MoH или T&R с веткой после 1940?
* **`revive_olympic_games_decision`** — версия GoB (греческий контент) или Morgenrote?

И два вопроса на потом, на текущую работу не влияющие:

* Четыре базовых товара с четырьмя престижными объявлениями — предсуществующее, разбирать отдельно от аддона.
* `great_revision_events.5` у TGR становится мёртвым контентом. Если это не устраивает — вешать событие не на решение, а на что-то из системы HC.
