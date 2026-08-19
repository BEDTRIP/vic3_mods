# E&F vs PBE — отчёт о конфликтах

- Дата сверки: **2026-08-19**
- E&F: `vic3_mods_out/E&F` (metadata пустая — версия в файле не проставлена)
- PBE: `vic3_mods_out/PowerBlocksExpanded`, `[1.13] Power Blocs Expanded`, id `3623185901`, `supported_game_version = 1.13*`
- Эталон: `vic3_mods_out/.vanillaVIC3` (1.13)

## Вывод

**Компач не нужен. Более того — старый компач нужно снять с загрузки, он вредит.**

Папка остаётся в статусе `noneed`. Файл `common/on_actions/zz_ef_pbe_on_actions.txt` держать в игровой папке нельзя (см. «Почему старый компач вреден»).

---

## Почему старый компач вреден (а не просто лишний)

Старый компач мержил `on_monthly_pulse_country` двух модов в один блок. Две причины выбросить:

1. **Он зовёт несуществующий on_action.** PBE переименовал весь свой префикс `kates_` → `vokaes_`.
   В компаче стоит `kates_dynamic_modifier_on_action`, в PBE 1.13 такого ключа больше нет — это `vokaes_dynamic_modifier_on_action`. Ссылка мёртвая.
2. **`common/on_actions/` аддитивен — блок не заменяет, а дописывается.** То есть компач не «мержит», а добавляет третий список поверх двух уже работающих. Итог: `ef_on_monthly_pulse_country` вызывается **дважды в месяц** (двойное ежемесячное финансовое обслуживание E&F), а хендлер PBE ставится в очередь ещё раз.

Исходная посылка README («Vic3 не мержит on_actions, последний загруженный побеждает») для 1.13 неверна — файлы с разными именами внутри `common/on_actions/` складываются.

---

## Что проверено

### 1. Пересечение по путям файлов

| | |
|---|---|
| файлов в E&F | 1302 |
| файлов в PBE | 67 |
| общих относительных путей | **1** — `thumbnail.png` |

Ни одного общего файла в `common/`, `gui/`, `events/`, `localization/`. Перекрытия по путям нет вообще.

### 2. `scan_conflicts.py --a E&F --b PowerBlocksExpanded`

```
common_categories_intersection = 13
common_key_dups = 1
loc_key_dups    = 0
event_id_dups   = 0
```

Единственный общий ключ:

- `on_monthly_pulse_country`
  - E&F: `common/on_actions/00_ef_on_action.txt` → `ef_on_monthly_pulse_country`
  - PBE: `common/on_actions/vokaes_power_bloc_on_actions.txt` → `vokaes_dynamic_modifier_on_action` ×4 через `delay`

Разные файлы → списки складываются, оба хука работают. **Это не конфликт.**

### 3. Базы данных, где пересечение было бы конфликтом

Считались ключи верхнего уровня, префиксы `INJECT:`/`REPLACE:` снимались.

| категория | E&F | PBE | общих |
|---|---:|---:|---:|
| `common/goods` | 74 | 0 | 0 |
| `common/defines` | `NEconomy` | `NPowerBlocs` | 0 |
| `common/modifier_type_definitions` | 540 | 37 | **0** |
| `common/static_modifiers` | 303 | 20 | **0** |
| `common/messages` | 130 | 2 | 0 |
| `common/game_rules` | 2 | 14 | 0 |
| `common/scripted_rules` | 0 | 12 | 0 |
| `common/cohesion_levels` | 0 | 5 | 0 |
| `common/power_bloc_identities` | 0 | 5 (все `REPLACE:`) | 0 |
| `common/power_bloc_principles` | 0 | 117 | 0 |
| `common/power_bloc_principle_groups` | 0 | 37 | 0 |
| `common/diplomatic_actions` | 0 | 6 | 0 |
| `common/diplomatic_plays` | 0 | 1 | 0 |

E&F не трогает систему power bloc'ов вообще (кроме чтения `is_power_bloc_leader` в двух treaty_articles про монетарные союзы), PBE не трогает экономику E&F.

### 4. Потолок 128 товаров

```
ваниль 1.13     53
E&F   +73 новых  (+ INJECT:gold — не новый товар, дописывание)
PBE   + 0        (у PBE нет common/goods)
────────────────
итого           126   при потолке 128
```

**Свободно 2 слота.** PBE ничего не съедает. Но при добавлении третьего мода в сборку с E&F запас — два товара, дальше вылет при входе в игру без строчки в логе.

### 5. Группы законов

`list_lawgroups_diff.py` не запускался: у PBE нет ни `common/laws`, ни `common/law_groups`. Проверять нечего.

PBE переопределяет ванильный scripted_rule `can_impose_law_default` и добавляет свои триггеры `vokaes_custom_law_imposition_trigger_*` (навязывание законов внутри блока). У E&F `common/scripted_rules/` пустой — пересечения нет.

### 6. Здания и building_group

PBE не содержит `common/buildings` и `common/building_groups`.

PBE определяет две PMG — `pmg_entrenched_building_manor_house` и `pmg_sovereign_wealth_fund_company_headquarter` — но **никуда их не подключает**: строк с `INJECT:building_manor_house` / `INJECT:building_company_headquarter` в PBE 1.13 нет. Это мёртвый код внутри самого PBE, к компачу отношения не имеет.

Со стороны E&F единственное упоминание `building_manor_house` в `common/buildings/ef_11_private_infrastructure.txt` — **закомментировано** (`# INJECT:building_manor_house` с `pmg_market_liquidity` / `pmg_private_ownership_infrastructure_stock`). Столкнуться нечему.

> Что смотреть при следующем обновлении PBE: если PBE вернёт `common/buildings/` и подключит свои PMG через `REPLACE:building_manor_house` вместо `INJECT:` — вот тогда возникнет конфликт с приватной инфраструктурой E&F. Пока `INJECT:` — конфликта не будет и в этом случае.

### 7. GUI

Самый опасный класс (пропавший виджет = вылет без записи в лог), поэтому разбиралось построчно.

- Общих `.gui`-файлов у модов нет. PBE держит только `gui/power_bloc_panel.gui` и `gui/power_bloc_formation_panel.gui`, E&F ни один из них не перекрывает.
- Копии PBE сделаны с **1.13**, не со старой версии: диффы против ванили `−32/+169` и `−7/+45` соответственно. Признака «минус сотни строк, плюс две-три» нет.
- E&F перекрывает 32 ванильных `.gui`. Типы, которые при этом теряются: `RegularTooltip_CoastalBuildingMarker`, `RegularTooltip_NavalMissionMarker`, `RegularTooltip_NavalMissionMarkerEnemy`, `coastal_building_marker_tooltip_row`, `naval_mission_marker_tooltip_fleet`, `treaty_tooltip_article_entry` (все из `custom_tooltip.gui`), `dropdown_menu_round`, `naval_mission_marker_dot`, `military_formation_cancel_invasion_button`.
  **Ни один из них не используется в gui-файлах PBE** — проверено поиском по обоим файлам PBE. Это отдельная проблема E&F против ванили, к паре E&F+PBE не относится.
- Ни один из модов не перекрывает `interface/` — все шаблоны (`default_button_action`, `tooltip_above`, `entry_bg` и остальные 49 `using =` из панелей PBE) берутся из ванили нетронутыми.

### 8. События и локализация

- Общих id событий: 0. У PBE один файл `events/vokaes_power_bloc_events.txt` (holy war), E&F его пространство имён не использует.
- Общих ключей локализации: 0. У PBE один `localization/english/vokaes_power_blocs_l_english.yml`, папки `localization/replace/` в версии 1.13 больше нет.

---

## Семантические пересечения (не конфликты, но иметь в виду)

**Минтинг.** PBE вводит `principle_currency_union_1..3` с `country_minting_mult = -0.2` у не-лидеров и новым модификатором `country_minting_from_bloc_members_mult` (до +0.5) у лидера. E&F использует `country_minting_mult` в 22 местах (`common/production_methods/15_ef_bank.txt`, `static_modifiers`, технологии, компании). Модификаторы складываются штатно — ни один не перетирает другой, но лидер блока с валютным союзом при E&F получает минтинг заметно выше, чем задумывал автор PBE. Это вопрос баланса, а не совместимости; правкой не лечится без вмешательства в замысел обоих авторов.

**Валюты.** Валютная система E&F реализована товарами (`*_c`, 73 штуки), валютный союз PBE — модификаторами на страну. Разные механизмы, общих данных нет. Treaty articles E&F про Латинский и Скандинавский монетарные союзы читают `is_power_bloc_leader`, но не трогают ни принципы, ни identity PBE.

---

## Что сделать

1. Держать `_ef/ef+pbe noneed` без изменений, компач не публиковать и **убрать из игровой папки `mod/`**, если он там ещё лежит (в этой сессии `mod/` не был подключён — не проверено).
2. Если мод уже опубликован в мастерской (id `3637386955`) — там сейчас лежит `on_actions` с мёртвым `kates_*`. Либо снять с публикации, либо залить пустую сборку с пометкой «no longer needed on 1.13».
3. `.metadata/metadata.json` компача остался на `1.12.2` / `supported_game_version = 1.12.*` — если мод не снимается, это тоже надо править.

## Чеклист проверки в игре (если всё-таки захочется убедиться)

По убыванию риска.

1. **E&F + PBE без компача, вход в игру и до 1837.** Ожидание: `error.log` без строк с `kates_` и без `Unknown on_action`. Годно / не годно.
2. **Панель Power Bloc открывается, слотов принципов до 12, кнопка Switch Identity на месте.** Проверяет, что gui-файлы PBE не спорят с 32 перекрытыми gui E&F. Годно / не годно.
3. **Ежемесячный пульс E&F срабатывает один раз в месяц.** Открыть бюджет/финансовую панель E&F и убедиться, что ежемесячные начисления не удвоены — это прямой индикатор того, что старого компача в загрузке нет. Годно / не годно.
4. **Товары загрузились полностью.** Экран рынка: должны быть все валютные товары E&F. Если игра вылетела при входе без ошибок в логе — превышен потолок 128 (значит, в сборке есть третий мод с товарами). Годно / не годно.
5. **Валютный союз PBE.** Взять принцип `principle_currency_union_3` лидером блока, посмотреть тултип минтинга: модификаторы E&F и PBE должны быть видны в тултипе оба. Годно / не годно.
