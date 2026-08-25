# Аддон 1 — внутренний разбор сборки

Дата: 2026-08-25 (пересборка без Tech & Res; первая сборка — 2026-08-24). Игра 1.13 (exe 1.13.11).
Собран `tools/build_addon1.py` из трёх компачей `_HC+GoB+MoH/hc+morg done`, `hc+tgr done`, `hc+kai done`.
Пары разобраны отдельно — см. `conflicts_hcgobmoh_vs_morgenrote_report.md`, `…_vs_tgr_report.md`, `…_vs_trkai_report.md` рядом с компачами.

**Что изменилось 25.08.2026.** Tech & Res убран из набора (развилка №6 в `План проекта.md`). Из сборки ушли четыре файла — `common/laws/zz_hctr_slavery.txt`, `common/decrees/zz_hctr_greener_grass.txt`, `common/journal_entries/zz_hctr_warlord_china.txt`, `common/ai_strategies/zzz_hctr_tr_default_strategy.txt`. Каждый из них нёс тело T&R, вмерджённое в тело HC или MoH; без T&R они ставят в игру контент отсутствующего мода, а `je_warlord_china` вдобавок указывает `on_complete` на событие `the_future_of_china.201`, которого больше нет. Компач `hc+tr+kai done` переименован в `hc+kai done`, файлы — в его `_to_delete/tr_removed_2026-08-25/`.

**Содержательное следствие, а не только удаление.** `tools/tgr_default_strategy.py` намеренно НЕ восстанавливал три ванильных института, которым TGR поднимает вес с 10 до 500 (`institution_police`, `institution_health_system`, `institution_home_affairs`): T&R переобъявлял все семь ванильных институтов на 10 в инжекте, который грузился позже, поэтому в порядке самих авторов значения TGR были уже мертвы, и восстановление решало бы пару TGR × T&R, а не эту. В коде на этот случай стоял assert. С уходом T&R ниже по цепочке эти три ключа не трогает никто, и блок TGR теперь переиздаётся целиком — все 15 утверждений вместо 12.

## Машинный вывод `check_megapack_conflicts.py` / `build_addon1.py`

```
files: 11
brace balance: ok
encodings: ok
duplicate top-level keys inside the addon: none beyond the 3 declared
    common                    group                 achievement_groups.txt
    common/ai_strategies      ai_strategy_default   zz_hctr_ai_strategy_default.txt
                                                    zz_hctr_tgr_default_strategy.txt
    common/history/countries  COUNTRIES             chi - china.txt
                                                    tur - ottoman empire.txt
localization: 0 keys, duplicates per language: none
goods files in the addon: 0
ALL CHECKS PASS
```

## 1. Требуют работы — сделано

Ни одного. Три компача не делят **ни одного ключа и ни одного пути** между собой, поэтому файлов «только для сборки» (`zzzz_addon_*.txt`) у аддона 1 нет. Это проверяется при каждой сборке: `build_addon1.py` падает, если два компача начнут везти один и тот же относительный путь.

Полный список того, что аддон меняет и почему, — в разборах пар и в README.

## 2. Не конфликты

| находка | почему не конфликт |
| --- | --- |
| `group` × 16 в `common/achievement_groups.txt` | у файла нет базы ключей: это список анонимных блоков `group = {}`. Повторы — сами группы достижений. Скрипт считает `group` идентификатором, потому что синтаксически он им выглядит |
| `ai_strategy_default` в двух файлах | намеренно и по порядку: `zz_hctr_ai_strategy_default` несёт смердженное тело `REPLACE:`, `zz_hctr_tgr_default_strategy` переиздаёт поверх него инжект The Great Revision. Это порядок, в котором грузятся сами авторы, и он же порядок имён файлов: внутри мода имя решает побайтово, `zz_a` < `zz_t`. Третьим тут был `zzz_hctr_tr_default_strategy` (инжект T&R) — ушёл вместе с T&R |
| `COUNTRIES` в двух файлах истории | контейнерный ключ, аддитивен между файлами — по одному файлу на страну, ровно как в ванили |
| дублей локализации 0, id событий 0 | аддон не добавляет ни ключей локализации, ни событий |

Все три задекларированы в `DECLARED_DUPS` внутри `build_addon1.py` вместе с причиной, так что молча в «ноль» они не превращаются.

## 3. Пересечения сборки с самими модами

`scan_conflicts.py --a <аддон> --b <мод>`, прогон 25.08.2026. Контейнерные `COUNTRIES` и `group` из подсчёта исключены. Отчёты прогона — в `_tmp_analysis/scan_2026-08-25/`.

| мод | общих ключей | общих путей | что именно |
| --- | --- | --- | --- |
| E&F | 0 | 0 | — |
| E&F Hotfix | 0 | 0 | — |
| PSC | 0 | 0 | — |
| PBE | 0 | 0 | — |
| **MegaComPatch `no t&r`** | **0** | **0** | аддон не наступает на сборку ни в одном ключе |
| Morgenröte | 5 | 1 | `gaudi_capital_expansion_level_4_modifier`, `revive_olympic_games_decision`, два `*_character_template`; `common/achievement_groups.txt`. Файлы пары `hc+morg` не менялись при пересборке |
| TGR | 4 | 2 | `ai_strategy_default`, `ideology_jacksonian_democrat`, `ig_landowners`, `ig_rural_folk`; оба файла истории |
| KAI | 1 | 0 | `ai_strategy_default` |
| Hail, Columbia! | 5 | 0 | два `*_character_template`, `ideology_jacksonian_democrat`, `ig_landowners`, `ig_rural_folk`. Было 10: ушли `decree_greener_grass_campaign` и четыре закона рабства |
| Gates of the Bosphorus | 2 | 1 | `revive_olympic_games_decision`, `gaudi_…_modifier`; `tur - ottoman empire.txt` |
| Mandate of Heaven | 2 | 2 | `ai_strategy_default`, `ig_rural_folk`; `chi - china.txt`, `common/achievement_groups.txt`. Было 3: ушёл `je_warlord_china` |
| ~~Tech & Res~~ | — | — | мод убран из набора 25.08.2026 |
| LLWA (аддон 2, грузится позже) | 1 | 0 | `ai_strategy_default` — `INJECT: subsidies` LLWA ложится **поверх** нашего тела, цело |

Каждое пересечение — ровно то, ради чего аддон существует: он последний в порядке и должен быть последним словом по этим ключам. Неожиданных нет. **Ноль пересечений с E&F, хотфиксом, PSC и PBE** — на этом держится утверждение, что аддон 1 работает с вариантом мегапака `no e&f+psc` как есть.

Локализация: 0 общих ключей ни с одним модом. Id событий: 0.

## 4. Проверки сборки

| проверка | результат |
| --- | --- |
| файлов | 11 (+ `.metadata/metadata.json`, `README.md`, `thumbnail.png`) — было 15 |
| покрытие компачей, побайтово (`filecmp`) | `hc+morg done` 4/0/0, `hc+tgr done` 5/0/0, `hc+kai done` 2/0/0 (файлов / отсутствует / отличается). `.md`-отчёты в покрытие не входят: документация — не содержимое мода |
| файлов «только сборка» | 0, и ни одного незадекларированного |
| баланс скобок | 0 во всех `.txt` |
| кодировки | ни одного файла с байтом > 127 вне комментария без BOM |
| дубли top-level ключей внутри сборки | 3, все задекларированы с причиной (см. выше) |
| дубли локализации по языкам | 0 (аддон не везёт локализацию) |
| id событий | 0 |
| товары против 128 | аддон не добавляет ни одного товара — набор после ухода T&R **74 из 128**, запас 54 |
| синхронизация в игровую папку | `Documents/Paradox Interactive/Victoria 3/mod/addon1 hc+gob+moh`, четыре T&R-файла перенесены в `_to_delete/sync_2026-08-25/`, `diff -rq` чист |

Отдельная проверка мерджа `ai_strategy_default`: три-сторонний мердж KAI × MoH против ванили прошёл с **0 конфликтами** (все расхождения — переотступы MoH или совпадение текста), маркеры `# KAI` на месте, `naval_power_projection` из KAI на месте — оба проверяются assert'ами в генераторе.

## 5. Открытые вопросы

* **`role` рядом с `executive_usage` / `agitator_usage`** у Крайслера и Твена — конструкции нет ни в ванили, ни у обоих авторов. Влияет только на этих двух персонажей; проверять в игре, не спавнятся ли они дважды и не ругается ли `debug.log` на `PostValidate`. (Задача HC.9.)
* **Пара HC × VC не закрыта.** По целевой цепочке Victorian Century грузится ДО Hail, Columbia!, и у пары 39 общих ключей и 8 общих путей — в том числе те самые `ig_landowners`, `ig_rural_folk`, `chi - china.txt` и `tur - ottoman empire.txt`, которые аддон уже мерджит. Это задача HC.7; до неё утверждение «аддон — последнее слово по этим ключам» верно только без VC.
* **Мегапак `no t&r` пока не знает про KAI.** Аддон от этого не страдает — он несёт свой мердж KAI × MoH и своё переиздание инжектов TGR, — но пара KAI × TGR в самом мегапаке сейчас не пропатчена ни одной строкой (задача МП.1).
* **Порядок внутри блока.** Требование «Mandate of Heaven после Hail, Columbia!» аддон не отменяет и не проверяет: при обратном порядке `INJECT:` MoH в `ig_rural_folk` пропадает ещё до нас, а наш файл несёт добавления MoH уже вшитыми — то есть аддон замаскирует нарушение порядка вместо того, чтобы его показать. Строка про порядок есть в README.
