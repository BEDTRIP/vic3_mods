# Сборка мегапака «no E&F no PSC» — 23.08.2026

Мегапак: `vic3_mods/__megapacks/megapack no e&f no psc`
Steam id: `3638941732` («MegaComPatch TGR + MR + T&R + PBE»)
Игра 1.13 (exe 1.13.11), метадата объявляет `1.13.*`.

## 1. Из чего собрано

Моды сборки: TGR, Kuromi's AI, Morgenröte, Tech & Res, Power Blocs Expanded.
Пары берутся в алфавитном порядке без дублирования, всё что `noneed` — не берётся.

| Пара | Папка | Взято |
|---|---|---|
| MR + T&R (+KAI) | `_morg/morg+tr+kai out fixed` | 12 файлов |
| PBE + TGR | `_pbe/pbe+tgr done` | 1 файл |
| TGR + T&R (+KAI) | `_tgr/tgr+tr+kai done` | 5 файлов из 6 (см. §3) |
| MR + PBE | `_morg/morg+pbe noneed` | — |
| MR + PSC | `_morg/morg+psc noneed` | — (PSC не в сборке) |
| MR + TGR | `_morg/morg+tgr noneed` | — |
| PBE + PSC | `_pbe/pbe+psc noneed` | — (PSC не в сборке) |
| PBE + T&R | `_pbe/pbe+tr+kai noneed` | — |

Плюс общий набор `__megapacks/dlc menu icons` (иконки DLC-меню) — только записи PBE и TGR,
без PSC и без E&F.

## 2. Что удалено из старой сборки

Старая сборка была собрана из компачей поколения 1.12 и несла 16 файлов, которых
в актуальных компачах уже нет. Все перенесены в
`vic3_mods/_to_delete/megapack_no_ef_no_psc_2026-08-23/`.

| Файл | Почему |
|---|---|
| `common/buy_packages/zzz_compatch_buy_packages.txt` | 38 КБ, дословно повторял `TRY_INJECT` обоих модов; удалён из компача 21.08 |
| `common/journal_entries/zzmr_science_agassiz_journal_entries.txt` | блок Агассица: MR 2.8.3e переделал геолога, шахты T&R покрыты `bg_mining` |
| `common/scripted_triggers/zzmr_agassiz_scripted_triggers.txt` | то же |
| `common/scripted_guis/zzz_mr_agassiz_geologist_sguis.txt` | то же |
| `localization/{english,russian}/zmr_agassiz_l_*.yml` | то же (4 файла вместе с `gui/zmr_gui_science_l_*.yml`) |
| `common/journal_entries/zzz_compatch_journal_entries.txt` | MR перешёл на `modifier:goods_output_aeroplanes_add > 0` |
| `common/mobilization_option_groups/zzz_mr_compatch_mobilization_option_groups.txt` | наборы групп у MR и T&R не пересекаются |
| `common/scripted_triggers/zzz_compatch_scripted_triggers.txt` | удалён из компача ещё 04.05 |
| `common/technology/technologies/ztr_mr_military.txt` | плейсхолдер-заглушка ради одного `ai_weight` |
| `common/technology/technologies/ztr_mr_production.txt` | плейсхолдер; T&R там только добавляет скорость исследования |
| `common/technology/technologies/ztr_mr_society.txt` | заглушка заменена точечными `REPLACE:` (`zzz_compatch_mr_society.txt`) |
| `common/on_actions/zzz_megapack_on_actions.txt` | **см. ниже** |

### `zzz_megapack_on_actions.txt` — отдельно

Файл мерджил `on_monthly_pulse` / `on_monthly_pulse_country` от MR, T&R и PBE
явными списками. Он был неправ трижды и должен был уйти вместе со своим
близнецом из `_morg/morg+pbe`:

1. `common/on_actions/` в 1.13 **аддитивен** — корневые хуки из разных файлов
   складываются, а не перетираются. Доказательство внутри самого Morgenröte:
   он объявляет `on_yearly_pulse_country` в 19 своих файлах.
2. Файл ссылался на `kates_weekly_global_on_action` и
   `kates_dynamic_modifier_on_action`. PBE переименовал весь префикс
   `kates_` → `vokaes_`. Имена резолвятся в ничто, молча, без строки в `error.log`.
3. Загружаясь последним, он добавлял свой список поверх двух уже правильных —
   то есть **удваивал** вызовы обработчиков PBE.

## 3. Единственный мердж внутри мегапака: `malaria_prevention`

Ключ определяют оба компача:

| | тело | что добавляет |
|---|---|---|
| `_tgr/…/zz_tr_kai_tgr_technologies.txt` | T&R | `country_institution_environment_max_investment_add = 1` (TGR) |
| `_morg/…/zzz_compatch_mr_society.txt` | T&R | `state_harvest_condition_panum_yellow_fever_condition_impact_mult = -0.25` (MR) |

Тела совпадают дословно — оба это редакция T&R, отличаются только модификаторы.

**Решение:** файл TGR-компача в мегапак не кладётся вовсе (в нём только этот один
ключ), а его строка дописана в копию `zzz_compatch_mr_society.txt`, которая
грузится последней. Итог: ключ определён в мегапаке **ровно один раз**, победитель
не зависит от порядка имён файлов.

Цена решения: копия `common/technology/technologies/zzz_compatch_mr_society.txt`
**не байт-в-байт** равна оригиналу в `_morg/morg+tr+kai out fixed`. Расхождение —
одна строка плюс комментарии, помеченные `MEGAPACK ONLY` и шапкой файла.
**При каждой пересинхронизации компача строку надо вернуть.**

Что теряется, если её потерять: институт Environment у TGR упирается в потолок
инвестиций на уровень ниже. Симптом молчаливый — модификатор не отсутствует,
он просто никогда не применялся.

## 4. Проверки

* `tools/check_megapack_conflicts.py` → `common_key_dups = 0`, `event_id_dups = 0`.
  `loc_key_dups = 6` — это `dlc_pbe`/`dlc_tgr`/`dlc_psc` (+`_desc`) в 11 языковых
  файлах одного набора, ложное срабатывание эвристики (один ключ на язык).
* Баланс скобок по всем `.txt` — 0.
* BOM есть во всех `.txt` и `.yml`; в `.metadata/metadata.json` BOM **нет**,
  `json.loads` проходит.
* Перекрытий по путям: ни один файл мегапака не совпадает по относительному пути
  ни с ванилью, ни с MR / TGR / T&R / KAI / PBE. Ни одного перекрытия файла целиком.
* **Потолок товаров:** ваниль 53 + MR 5 (`air_travel`, `elgar_instruments`,
  `elgar_music`, `good_uranium`, `manzoni_prints`) + T&R 35 = **93** из 128.
  TGR, KAI и PBE новых товаров не заводят. Запас 35.
  `zz_tr_kai_tgr_goods.txt` — три `REPLACE:` ванильных, новых ключей не добавляет.
* `.gui` в мегапаке нет, `compare_gui_names.py` не нужен.

## 5. Метадата

* `version` 1.12.2 → **1.13.0**, `supported_game_version` 1.12.* → **1.13.\***.
* У зависимости PBE был **пустой `id`** — проставлен `3623185901`.
* Убрана зависимость **Expanded Topbar Framework**: она досталась в наследство от
  версии мегапака с E&F. Ни TGR, ни MR, ни T&R, ни KAI, ни PBE её не объявляют, и
  ни один файл этой сборки не трогает топбар. Лишняя зависимость = ложный варн
  «мод не найден» у тех, кто ETF не ставит.
* `tested_with` пересобран по `tested_with` самих компачей: CMF 1.40.3,
  TGR 2.0 (1.13.10, коммит 12.08.2026), KAI 7.5, MR 2.8.3e Mitsopoulos,
  T&R 1.6' (коммит 13.05.2026), PBE 1.13*.

## 6. Открытый вопрос: версия TGR

В активном плейсете лаунчера мод из мастерской называется
**«The Great Revision - 1.13.11»**, а распаковка в `vic3_mods_out/TheGreatRevision`
объявляет `supported_game_version = 1.13.10` и зовётся «The Great Revision - 1.13.10».
Похоже, в мастерской TGR уже обновился, а локальная распаковка отстала.
Компачи `_tgr/tgr+tr+kai done` и `_pbe/pbe+tgr done` сверялись с **распаковкой**.
Перед публикацией стоит перекачать TGR и прогнать `scan_conflicts.py` заново.

## 7. Чеклист проверки в игре

Порядок по убыванию риска. Полные чеклисты по каждой паре — в самих компачах
(`_tgr/tgr+tr+kai done/checklist_ingame_2026-08-23.md`,
`_morg/morg+tr+kai out fixed/отчёт_morg+tr+kai_сверка_2026-08-21.md` §7).
Здесь — только то, что проверяется именно на мегапаке.

1. **Лаунчер.** Мегапак без варна «Не удалось обработать метаданные».
   Включён ровно **один** экземпляр: либо локальная папка, либо мастерская.
   Три отдельных компача (TGR+T&R, MR+T&R, PBE+TGR) **выключены** — мегапак их содержит.
   → годно / не годно
2. **Порядок:** CMF → TGR → KAI → Morgenröte → Tech & Res → PBE → мегапак.
   Косвенная проверка порядка MR перед T&R: компания Steinway от Morgenröte
   не предлагается. → годно / не годно
3. **`logs/error.log` после главного меню и старта 1836.** Нет строк с именами
   файлов мегапака (`zz_tr_kai_tgr_*`, `zztr_compatch_*`, `zzz_mr_compatch_*`,
   `zzz_compatch_*`, `zz_pbe_tgr_*`). → годно / не годно
4. **Старт 1836 за Британию.** Игра стартует. Вылет без ошибок в логе при 93 товарах
   из 128 — не потолок товаров, искать в другом месте (`crashes/`). → годно / не годно
5. **Malaria Prevention, тултип теха.** Видно **и** `+1` к инвестициям в колониальные
   дела, **и** `+1` к институту Environment (TGR), **и** −25 % к жёлтой лихорадке (MR).
   Ровно этот пункт — единственный мердж мегапака. → годно / не годно
6. **Аэропорт производит air travel** (не только transportation), и журнальная запись
   `je_mr_prestige_goods_flights` доступна. → годно / не годно
7. **`on_monthly_pulse`.** Механики PBE (динамические модификаторы блока) тикают
   **один раз**, а не вчетверо — удалённый `zzz_megapack_on_actions.txt` их удваивал.
   Проверять по скорости роста когезии/модификаторов блока. → годно / не годно
8. **`force_regime_change`** доступен и работает с блоками PBE. → годно / не годно
9. **Extraction Economy** сносит производства T&R **и** выбрасывает страну из
   централизации TGR. → годно / не годно
