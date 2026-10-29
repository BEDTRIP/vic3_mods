# Мегапак no-t&r + KAI — сделано 25.08.2026

Закрыто. Перенесено из `Архив задач.md` 26.08.2026.


Сборка `megapack no t&r` теперь основная и знает про KAI. Steam id `3640735868`, название стало **«MegaComPatch TGR + PSC + KAI + E&F + MR + PBE»**, версия `1.13.11-1` → `1.13.11-2`. Подробный отчёт — `__megapacks/megapack no t&r/build_report_2026-08-25_kai.md`.

### Сначала пришлось разделить компачи `*+tr+kai`

Они были не устаревшими, а слипшимися: один компач обслуживал две пары сразу. Разделены 25.08.2026, **KAI-половинки остались в папке своего блока, T&R-половинки собраны в новую папку `_tr/` одним набором.**

| было | KAI-половина | T&R-половина |
| --- | --- | --- |
| `_tgr/tgr+tr+kai done` | `_tgr/tgr+kai done` — один файл, `zz_kai_tgr_ai_default_strategy.txt` | `_tr/tgr+tr done` — пять файлов, переименованы `zz_tr_kai_tgr_*` → `zz_tr_tgr_*`; плюс `_tr/kai+tr done` (`ai_strategy_resource_expansion` — это пара KAI × T&R, к TGR отношения не имеет) |
| `_ef/ef+tr+kai out fixed` | `_ef/ef+kai noneed` | `_tr/ef+tr out fixed` |
| `_morg/morg+tr+kai out fixed` | `_morg/morg+kai noneed` | `_tr/morg+tr out fixed` |
| `_psc/psc+tr+kai out fixed` | `_psc/psc+kai done` (новый файл, см. МП.3) | `_tr/psc+tr out fixed` |
| `_pbe/pbe+tr+kai noneed` | `_pbe/pbe+kai noneed` | `_tr/pbe+tr noneed` |
| `stuff/_tr/tr+kai+vc` | — | `_tr/tr+kai+vc`, пока не разделён (это задача VC.4) |

`_tr/` — отдельный живой набор для тех, кто играет с Tech & Res. Из нашего набора T&R убран, но компачи для него остаются рабочими и проверенными.

**VC.4 закрыт 26.08.2026 не разделением этого файла, а заново с нуля** — `_vc/kai+vc done`, генератор читает текущие KAI и VC живьём. `_tr/tr+kai+vc` из этой строки таблицы на диске не найден (видимо переехал в `_vc/kai+vc outdate` вместе с остальными VC-компачами января 2026); T&R-половина там, если понадобится набору `_tr/`, ещё ждёт разбора.

### Что сделано по пунктам

- [x] **МП.1 KAI × TGR — 37 ключей, патчится один.** Разбор — `_tgr/tgr+kai done/conflicts_tgr_vs_kai_report.md`. 24 закона — у KAI везде `INJECT: ai_enact_weight_modifier`, тела TGR целы. `building_construction_sector` и `foreign_investment_rights` — TGR пишет тело, KAI инжектит один под-блок, сливается. `atmospheric_engine` и `mechanical_tools` — инжекты с обеих сторон в разные под-блоки. `NAI` — сливается поключево, реально пересекаются восемь `MONEY_SPENDING_*`, оба автора выставили намеренно. Шесть остальных `ai_strategies` — у обоих полные осознанно разные стратегии. **Единственный настоящий конфликт — `ai_strategy_default`**, и он закрыт файлом `zz_kai_tgr_ai_default_strategy.txt` (генератор `tools/regen_tgr_kai_ai_default.py`). Прежний список из восьми пунктов в этом плане был составлен по именам файлов трёхстороннего компача, а не по отчёту пары; в файлах `zz_tr_kai_tgr_laws/goods/buildings/production_methods/technologies` KAI не было ни строки — всё это пары TGR × T&R.
  * **Изменение содержания:** блок TGR теперь переиздаётся целиком, 15 утверждений вместо 12 — вернулись 10 → 500 на `institution_police`, `institution_health_system`, `institution_home_affairs`. Раньше их отдавали T&R, который переобъявлял все семь ванильных на 10 позже. См. T&R.2c.
  * **`wanted_army_size_script_value` сменил владельца.** Оба автора переписали ванильную формулу целиком и оба открывают блок `value = 0` — владеет последний. Раньше это был T&R, теперь KAI. У TGR остаются за бортом бонусы ранга (+100/+50 против +25/+10 у KAI) и слагаемое `fixed_income`. Ребаланс, не поломка; записано, не патчится.
- [x] **МП.2 KAI × Morgenrote — 2 ключа, `noneed`.** `building_government_administration`: KAI `INJECT: ai_value`, MR `TRY_INJECT: production_method_groups`. `atmospheric_engine`: KAI `INJECT: ai_weight`, MR `TRY_INJECT: unlocking_technologies`, TGR `INJECT: modifier` — три автора, три разных под-блока. Обоснование — `_morg/morg+kai noneed/README.md`.
- [x] **МП.3 KAI × PSC — 1 ключ, и это НЕ `noneed`.** Прежний вывод держался на утверждении «`kai_` грузится раньше `zz_PSC_`» — это порядок имён файлов, а решает порядок модов, и **KAI грузится после PSC** (позиция 5 против 4 в плейсете, и так же в целевой цепочке). KAI инжектит `ai_value` блоком, который открывается `value = 1000`; внутри под-блока это сбрасывает всё, что накопилось раньше, то есть у PSC пропадают база 2500 и бонус за первый стройсектор. В логе — ничего. Написан компач `_psc/psc+kai done` (одна запись, полное тело PSC). **В мегапак он не входит намеренно:** сборка везёт свой `zz_pb_ef_construction_sector.txt` — полный `REPLACE:` этого здания с блоком PSC внутри — и грузится последней. Основание держится на порядке: **мегапак после Kuromi's AI**, строка есть в README сборки.
- [x] **МП.4 KAI × E&F+hotfix и KAI × PBE — 0/0.** Обоснования — `_ef/ef+kai noneed/README.md` и `_pbe/pbe+kai noneed/README.md`.
- [x] **МП.5 README, metadata, покрытие.** KAI в `relationships` (между PSC и E&F) и в порядок загрузки README. `scan_conflicts.py` сборка × KAI — два общих ключа, оба намеренные (`ai_strategy_default` — наш новый файл; `building_construction_sector` — файл сборки поверх инжекта KAI). Внутренние дубли сборки не изменились (98 `company_types` — штатная конструкция `ef+psc`). Локализация: 418 ключей, 11 языков по 38, дублей внутри языка нет. **Товары пересчитаны по виртуальной ФС на всей цепочке сборки: 69 из 128, запас 59** (ваниль 53 + хотфикс 7 + Morgenröte 5 + PSC 4). В README сборки стояло 70 — исправлено. У KAI папки `common/goods` нет вообще. Синхронизировано в игровую папку, `diff -rq` чист.

### Найдено попутно

* **`_tr/tr+kai+vc/common/company_types/zz_vc_tr_company_types.txt` был без BOM**, а в нём путь к иконке `…forges_et_chantiers_de_la_méditerranée.dds` в некомментарной строке. Без BOM игра читает такой путь неверно и иконка молча не находится. BOM добавлен.
* **`tools/regen_ef_tr_copies.py` смотрел на папки, которых нет** (`_ef/ef+tr+kai out`, `_ef/ef+tr+kai fixed`). Перенацелен на `_tr/ef+tr out` / `_tr/ef+tr out fixed`. Папки-источника `_tr/ef+tr out` на диске **нет**, и `--check` в этом случае печатает `missing:` и выходит с кодом 0 — то есть выглядит как «всё сошлось». Написано в шапке скрипта; распаковать текущую версию чужого компача туда до следующего прогона.
* **`_tr/ef+tr out fixed` определяет четыре PM золотой шахты дважды** — в `zef_mines_production_methods.txt` (копия чужого компача) и в `zzzz_ef_tr_fix_gold_minting.txt` (наша починка, имя сортируется позже и побеждает). Это задумано, но нигде не задекларировано.
* **`_tr/psc+tr out fixed` создаёт свой товар `concrete_construction`.** В нашем наборе он не считается — T&R-набор отдельный, — но при любом сведении двух наборов это +1 к потолку 128.
