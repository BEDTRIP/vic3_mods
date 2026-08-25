# TGR vs KAI — почему это конфликт / почему нет (сверка 23.08.2026)

**Версии:** TGR 2.0 (`3215078236`, 1.13.10, коммит 12.08.2026) · KAI 7.5 (`kai.kuromi`, 1.13.*, 24.07.2026).
**Порядок загрузки:** CMF → TGR → **KAI** → T&R → компач. KAI перебивает TGR, но сам перебивается T&R там, где T&R что-то трогает.

## Итог: из 37 «дубликатов» патчится один

| Категория | Ключей | Патчим | Почему |
|---|---|---|---|
| `laws` | 24 | 0 | **Все 24 записи у KAI — `INJECT:`**, и почти всегда это только `ai_enact_weight_modifier`. Тела законов от TGR остаются целыми. Именно поэтому из компача удалены `law_per_capita_based_taxation` и `law_proportional_taxation`: старая версия переписывала их рукописным телом с пустым `modifier = { }` и молча стирала у TGR `country_capitalists_pol_str_mult = -0.25`. |
| `ai_strategies` | 7 | 2 | Патчим `ai_strategy_resource_expansion`: TGR и KAI оба переопределяют его целиком, T&R не трогает — значит в игре остаётся версия KAI, а у неё нет ресурсных товаров T&R (`good_uranium`, `bauxite`, `copper`, `commonores`, `advancedores`, `rare_earths`, `gas`). AI просто никогда не формирует по ним экспортную позицию; в логе — ничего. `ai_strategy_colonial_extraction` из компача **убран**: T&R 1.6 везёт слитую версию сам и грузится после KAI. `plantation_economy`, `placate_population`, `industrial_expansion` — у обоих авторов полные осознанно разные стратегии, мердж был бы ребалансом. **`ai_strategy_default` — патчим, см. раздел ниже:** здесь у TGR своей стратегии нет, есть три `INJECT:`, и голое тело KAI уносит их все. |
| `buildings` | 1 | 0 | `building_construction_sector`: TGR `REPLACE_OR_CREATE:`, KAI `INJECT:` (только `ai_value`) — сливается. |
| `defines` | 1 (`NAI`) | 0 | Блоки `NAI` сливаются по подключам. Реально пересекаются 8 подключей — все из семейства `MONEY_SPENDING_*` (пороги трат AI). Побеждает KAI. Оба автора выставили их намеренно; выбрать один набор — ребаланс, а не совместимость. |
| `technology/technologies` | 2 | 0 | `atmospheric_engine` и `mechanical_tools` — `INJECT:` с обеих сторон. |
| `treaty_articles` | 1 | 0 | `foreign_investment_rights`: TGR `REPLACE_OR_CREATE:` (тело статьи), KAI `INJECT:` (только блок `ai`) — сливается. |
| `script_values` | 1 | 0 | `wanted_army_size_script_value`: у TGR, KAI и T&R три разные формулы. Побеждает T&R как самый поздний, KAI тут вообще не при чём. Подробнее в `conflicts_tgr_vs_tr_report.md`. |

## `ai_strategy_default` — исправлено 25.08.2026

До этой даты запись стояла в отчёте в одном ряду с `plantation_economy` и
`placate_population`: «у обоих авторов полные осознанно разные стратегии, мердж
был бы ребалансом». Это неверно, и статус пары `done` держался на ошибке.

**У TGR своей стратегии нет.** Он правит ванильную тремя `INJECT:`-файлами:

| файл TGR | строк | под-блоки |
| --- | --- | --- |
| `TGR_ADJUSTMENTS_default_strategy.txt` | 455 | `icon`, `diplomatic_play_support` |
| `TGR_POLITICS_default_strategy.txt` | 70 | `icon`, `institution_scores` |
| `TGR_TRADE_default_strategy.txt` | 193 | `wanted_construction_output`, `combat_unit_group_weights`, `conscript_battalion_ratio` |

**KAI везёт `common/ai_strategies/00_default_strategy.txt`** — ванильный путь,
8736 строк, **без префикса**. Голое полное тело в позднем моде уносит все
`INJECT:` предыдущих модов разом (правила, раздел 3). Все три файла TGR
перестают действовать в момент установки KAI, и в `error.log` про это нет ни
строчки: непринятый инжект — это не отсутствующий ключ, его просто нет.

Что теряется, по под-блокам:

| под-блок | ваниль | TGR | KAI | решение |
| --- | --- | --- | --- | --- |
| `institution_scores` | 7 институтов по 10 | +12 своих институтов; police / health_system / home_affairs 10 → 500 | = ваниль | **восстановлены 12 институтов.** 500 не восстанавливаем: T&R своим инжектом переписывает все семь ванильных обратно в 10 и грузится позже — в порядке самих авторов эти три значения TGR уже мертвы, и вернуть их значило бы решить пару TGR × T&R, а не эту |
| `combat_unit_group_weights` | 8 групп | + `light_ship`, `capital_ship`, `support_ship`; остальные записи побайтово ванильные | = ваниль | **восстановлены три группы** |
| `conscript_battalion_ratio` | `law_national_militia` +2.5 | +4.5; блок открывается `value = 0.5` | = ваниль | **переиздан дословно** |
| `diplomatic_play_support` | 685 строк сценариев | свой список: германское объединение, пять блоков итальянского, гражданские войны, Эльзас-Лотарингия, американо-мексиканская, Северная Африка, Ар-Риф. Открывается `value = 0`, то есть ванильный список обнуляет | ванильный список, 36 изменённых строк | **мердж:** тело KAI без его блока `### German Leadership War` (у TGR своя версия того же сценария, вдвоём они складывались бы) + сценарии TGR |
| `wanted_construction_output` | ванильная формула | своя формула, открывается `value = 0` | своя формула, открывается `value = 0` | **оставлено KAI.** Оба переписали формулу целиком от общего предка; кто последний, тот и владеет, а KAI грузится позже и это его профильная тема |
| `icon` | `placate_population.dds` | то же | то же | нечего делать |

Файл: `common/ai_strategies/zz_tr_kai_tgr_ai_default_strategy.txt`, генератор —
`tools/regen_tgr_kai_ai_default.py`, разбор семантики — в шапке
`tools/tgr_default_strategy.py`.

### Почему `INJECT:`, а не `REPLACE:`

Под-блоки сливаются в запись, а внутри одного под-блока движок считает
скрипт-значение по порядку: `value = X` сбрасывает всё, что накопилось до него,
именованные записи (`institution_*`, `combat_unit_group_*`) переопределяют
одноимённые, безымянные `add = { }` складываются. Файлы TGR написаны ровно под
эту модель: каждый блок, который TGR забирает себе, открывается сбросом
`value =`, а в `institution_scores` TGR закомментировал ровно те четыре
ванильных института, которые не меняет, и оставил ровно те три, которые меняет.
Поэтому дословное переиздание воспроизводит «TGR без KAI» — и поэтому мердж
`diplomatic_play_support` обязан переизложить победившее тело, а не просто
дописать к нему свои сценарии.

### Что из этого следует для аддона 1

Аддон 1 кладёт поверх `REPLACE:ai_strategy_default` полным телом (мердж
KAI + MoH) и уносит переиздание мегапака вместе со всем остальным. Тот же блок,
собранный против смердженного тела, лежит в аддоне отдельным файлом
`zz_hctr_tgr_default_strategy.txt` — между телом и переизданием инжекта T&R, в
том порядке, в каком грузятся сами авторы.

### Найдено попутно, к паре TGR × T&R

`ztr_default_strategy.txt` (T&R) переписывает все семь ванильных институтов
значением 10 — это дословная копия ванильного блока, к которой автор дописал
свой `institution_environmental_policy`. TGR ставит police / health_system /
home_affairs в 500 осознанно (строки помечены `TGR LINE`), но грузится раньше.
То есть копия ванили молча гасит осознанную правку TGR. Пара TGR × T&R стоит
`done`; здесь это не чинится.


## Что проверить при следующем обновлении KAI поимённо

- `kai_has_high_supply` — на нём держится вся `goods_stances` в патче `ai_strategy_resource_expansion`. Если KAI переименует триггер, стратегия загрузится и молча ничего не сделает.
- `kai_gdp_per_capita` — использовался в удалённых налоговых записях; если будете возвращать что-то из них, проверьте, что имя живо.
- Не начал ли KAI писать `ai_strategy_default` через `INJECT:` вместо голого тела по ванильному пути — тогда инжекты TGR выживут сами и файл
  `zz_tr_kai_tgr_ai_default_strategy.txt` станет не нужен. Генератор про это молчит: он собирает мердж из того, что видит.
- Не переехал ли `ai_strategy_resource_expansion` с `REPLACE:` на `INJECT:` — тогда патч станет не нужен, как уже случилось с компаниями и `law_industry_banned` у T&R.

---

Ниже — сырой вывод `tools/scan_conflicts.py` от 23.08.2026, как есть.

# TGR vs KAI — conflict report (key-level heuristic)

- TGR root: `/sessions/rcw-01qfgb8bzfs9xeotduvu9q29/mnt/Projects/vic3_mods_out/TheGreatRevision`
- KAI root: `/sessions/rcw-01qfgb8bzfs9xeotduvu9q29/mnt/Projects/vic3_mods_out/TechRes+Kuromi/kai`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/ai_strategies — 7 duplicates
- `ai_strategy_agricultural_expansion`
  - TGR: `common/ai_strategies/TGR_TRADE_admin_strategies.txt`
  - KAI: `common/ai_strategies/kai_admin_strategies.txt`
- `ai_strategy_colonial_extraction`
  - TGR: `common/ai_strategies/TGR_TRADE_admin_strategies.txt`
  - KAI: `common/ai_strategies/kai_admin_strategies.txt`
- `ai_strategy_default`
  - TGR: `common/ai_strategies/TGR_ADJUSTMENTS_default_strategy.txt`
  - TGR: `common/ai_strategies/TGR_POLITICS_default_strategy.txt`
  - TGR: `common/ai_strategies/TGR_TRADE_default_strategy.txt`
  - KAI: `common/ai_strategies/00_default_strategy.txt`
- `ai_strategy_industrial_expansion`
  - TGR: `common/ai_strategies/TGR_TRADE_admin_strategies.txt`
  - KAI: `common/ai_strategies/kai_admin_strategies.txt`
- `ai_strategy_placate_population`
  - TGR: `common/ai_strategies/TGR_TRADE_admin_strategies.txt`
  - KAI: `common/ai_strategies/kai_admin_strategies.txt`
- `ai_strategy_plantation_economy`
  - TGR: `common/ai_strategies/TGR_TRADE_admin_strategies.txt`
  - KAI: `common/ai_strategies/kai_admin_strategies.txt`
- `ai_strategy_resource_expansion`
  - TGR: `common/ai_strategies/TGR_TRADE_admin_strategies.txt`
  - KAI: `common/ai_strategies/kai_admin_strategies.txt`

### common/buildings — 1 duplicates
- `building_construction_sector`
  - TGR: `common/buildings/TGR_TRADE_construction.txt`
  - KAI: `common/buildings/kai_buildings.txt`

### common/defines — 1 duplicates
- `NAI`
  - TGR: `common/defines/TGR_ADJUSTMENTS_ai.txt`
  - TGR: `common/defines/TGR_GER_UNIFICATION_ai.txt`
  - TGR: `common/defines/TGR_POLITICS_ai.txt`
  - TGR: `common/defines/TGR_TAX_PANEL_ai.txt`
  - TGR: `common/defines/TGR_TRADE_ai.txt`
  - KAI: `common/defines/kai_ai.txt`

### common/laws — 24 duplicates
- `law_agrarianism`
  - TGR: `common/laws/TGR_POLITICS_economic_system.txt`
  - KAI: `common/laws/kai_economic_system.txt`
- `law_charitable_health_system`
  - TGR: `common/laws/TGR_POLITICS_health_system.txt`
  - KAI: `common/laws/kai_health_system.txt`
- `law_colonial_exploitation`
  - TGR: `common/laws/TGR_POLITICS_colonial_affairs.txt`
  - KAI: `common/laws/kai_colonial_affairs.txt`
- `law_colonial_resettlement`
  - TGR: `common/laws/TGR_POLITICS_colonial_affairs.txt`
  - KAI: `common/laws/kai_colonial_affairs.txt`
- `law_commercialized_agriculture`
  - TGR: `common/laws/TGR_POLITICS_land_reform.txt`
  - KAI: `common/laws/kai_land_reform.txt`
- `law_dedicated_police`
  - TGR: `common/laws/TGR_POLITICS_policing.txt`
  - KAI: `common/laws/kai_policing.txt`
- `law_frontier_colonization`
  - TGR: `common/laws/TGR_POLITICS_colonial_affairs.txt`
  - KAI: `common/laws/kai_colonial_affairs.txt`
- `law_guaranteed_liberties`
  - TGR: `common/laws/TGR_POLITICS_internal_security.txt`
  - KAI: `common/laws/kai_internal_security.txt`
- `law_local_police`
  - TGR: `common/laws/TGR_POLITICS_policing.txt`
  - KAI: `common/laws/kai_policing.txt`
- `law_militarized_police`
  - TGR: `common/laws/TGR_POLITICS_policing.txt`
  - KAI: `common/laws/kai_policing.txt`
- `law_national_guard`
  - TGR: `common/laws/TGR_POLITICS_internal_security.txt`
  - KAI: `common/laws/kai_internal_security.txt`
- `law_old_age_pension`
  - TGR: `common/laws/TGR_POLITICS_welfare.txt`
  - KAI: `common/laws/kai_welfare.txt`
- `law_per_capita_based_taxation`
  - TGR: `common/laws/TGR_TAX_PANEL_taxation.txt`
  - KAI: `common/laws/kai_taxation.txt`
- `law_poor_laws`
  - TGR: `common/laws/TGR_POLITICS_welfare.txt`
  - KAI: `common/laws/kai_welfare.txt`
- `law_private_health_insurance`
  - TGR: `common/laws/TGR_POLITICS_health_system.txt`
  - KAI: `common/laws/kai_health_system.txt`
- `law_private_schools`
  - TGR: `common/laws/TGR_POLITICS_education_system.txt`
  - KAI: `common/laws/kai_education_system.txt`
- `law_proportional_taxation`
  - TGR: `common/laws/TGR_TAX_PANEL_taxation.txt`
  - KAI: `common/laws/kai_taxation.txt`
- `law_public_health_insurance`
  - TGR: `common/laws/TGR_POLITICS_health_system.txt`
  - KAI: `common/laws/kai_health_system.txt`
- `law_public_schools`
  - TGR: `common/laws/TGR_POLITICS_education_system.txt`
  - KAI: `common/laws/kai_education_system.txt`
- `law_regulatory_bodies`
  - TGR: `common/laws/TGR_POLITICS_labor_rights.txt`
  - KAI: `common/laws/kai_labor_rights.txt`
- `law_religious_schools`
  - TGR: `common/laws/TGR_POLITICS_education_system.txt`
  - KAI: `common/laws/kai_education_system.txt`
- `law_secret_police`
  - TGR: `common/laws/TGR_POLITICS_internal_security.txt`
  - KAI: `common/laws/kai_internal_security.txt`
- `law_wage_subsidies`
  - TGR: `common/laws/TGR_POLITICS_welfare.txt`
  - KAI: `common/laws/kai_welfare.txt`
- `law_worker_protections`
  - TGR: `common/laws/TGR_POLITICS_labor_rights.txt`
  - KAI: `common/laws/kai_labor_rights.txt`

### common/script_values — 1 duplicates
- `wanted_army_size_script_value`
  - TGR: `common/script_values/TGR_TAX_PANEL_ai_script_values.txt`
  - KAI: `common/script_values/kai_script_values.txt`

### common/technology/technologies — 2 duplicates
- `atmospheric_engine`
  - TGR: `common/technology/technologies/TGR_POLITICS_production.txt`
  - KAI: `common/technology/technologies/kai_technologies.txt`
- `mechanical_tools`
  - TGR: `common/technology/technologies/TGR_POLITICS_production.txt`
  - KAI: `common/technology/technologies/kai_technologies.txt`

### common/treaty_articles — 1 duplicates
- `foreign_investment_rights`
  - TGR: `common/treaty_articles/TGR_TRADE_foreign_investment_rights.txt`
  - KAI: `common/treaty_articles/kai_foreign_investment_rights.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**