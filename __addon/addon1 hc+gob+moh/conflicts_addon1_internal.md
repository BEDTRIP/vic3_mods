# Аддон 1 — внутренний разбор сборки

Дата: 2026-08-24. Игра 1.13 (exe 1.13.11).
Собран `tools/build_addon1.py` из трёх компачей `_HC+GoB+MoH/hc+morg done`, `hc+tgr done`, `hc+tr+kai done`.
Пары разобраны отдельно — см. `conflicts_hcgobmoh_vs_morgenrote_report.md`, `…_vs_tgr_report.md`, `…_vs_trkai_report.md` рядом с компачами.

## Машинный вывод `check_megapack_conflicts.py`

```
Summary: common_key_dups= 3  loc_key_dups= 0  event_id_dups= 0

common               group                 1 файл   common/achievement_groups.txt
common/ai_strategies ai_strategy_default   3 файла  zz_hctr_ai_strategy_default.txt
                                                    zz_hctr_tgr_default_strategy.txt
                                                    zzz_hctr_tr_default_strategy.txt
common/history/countries COUNTRIES         2 файла  chi - china.txt
                                                    tur - ottoman empire.txt
```

## 1. Требуют работы — сделано

Ни одного. Три компача не делят **ни одного ключа и ни одного пути** между собой, поэтому файлов «только для сборки» (`zzzz_addon_*.txt`) у аддона 1 нет. Это проверяется при каждой сборке: `build_addon1.py` падает, если два компача начнут везти один и тот же относительный путь.

Полный список того, что аддон меняет и почему, — в разборах пар и в README.

## 2. Не конфликты

| находка | почему не конфликт |
| --- | --- |
| `group` × 16 в `common/achievement_groups.txt` | у файла нет базы ключей: это список анонимных блоков `group = {}`. Повторы — сами группы достижений. Скрипт считает `group` идентификатором, потому что синтаксически он им выглядит |
| `ai_strategy_default` в трёх файлах | намеренно и по порядку: `zz_hctr_ai_strategy_default` несёт смердженное тело `REPLACE:`, `zz_hctr_tgr_default_strategy` переиздаёт поверх него инжект The Great Revision, `zzz_hctr_tr_default_strategy` — инжект Tech & Res. Это порядок, в котором грузятся сами авторы, и он же порядок имён файлов: внутри мода имя решает побайтово, `zz_a` < `zz_t` < `zzz_` |
| `COUNTRIES` в двух файлах истории | контейнерный ключ, аддитивен между файлами — по одному файлу на страну, ровно как в ванили |
| дублей локализации 0, id событий 0 | аддон не добавляет ни ключей локализации, ни событий |

Все три задекларированы в `DECLARED_DUPS` внутри `build_addon1.py` вместе с причиной, так что молча в «ноль» они не превращаются.

## 3. Пересечения сборки с самими модами

`scan_conflicts.py --a <аддон> --b <мод>` по каждому блоку набора, плюс сверка по кэшированным индексам для Morgenröte (полный обход мода в 8200 файлов не укладывается в таймаут моста). Контейнерные `COUNTRIES` и `group` из таблицы исключены.

| мод | общих ключей | общих путей | что именно |
| --- | --- | --- | --- |
| E&F | 0 | 0 | — |
| E&F Hotfix | 0 | 0 | — |
| PSC | 0 | 0 | — |
| PBE | 0 | 0 | — |
| **MegaComPatch** | **0** | **0** | аддон не наступает на сборку ни в одном ключе |
| Morgenröte | 5 | 1 | `gaudi_capital_expansion_level_4_modifier`, `revive_olympic_games_decision`, два `*_character_template`, `common/achievement_groups.txt` |
| TGR | 4 | 2 | `ai_strategy_default`, `ideology_jacksonian_democrat`, `ig_landowners`, `ig_rural_folk`; оба файла истории |
| KAI | 1 | 0 | `ai_strategy_default` |
| Tech & Res | 7 | 0 | `ai_strategy_default`, `decree_greener_grass_campaign`, `je_warlord_china`, четыре закона рабства |
| Hail, Columbia! | 10 | 0 | два `*_character_template`, `decree_greener_grass_campaign`, `ideology_jacksonian_democrat`, `ig_landowners`, `ig_rural_folk`, четыре закона рабства |
| Gates of the Bosphorus | 2 | 1 | `revive_olympic_games_decision`, `gaudi_…_modifier`; `tur - ottoman empire.txt` |
| Mandate of Heaven | 3 | 2 | `ai_strategy_default`, `ig_rural_folk`, `je_warlord_china`; `chi - china.txt`, `common/achievement_groups.txt` |
| LLWA (аддон 2, грузится позже) | 1 | 0 | `ai_strategy_default` — `INJECT: subsidies` LLWA ложится **поверх** нашего тела, цело |

Каждое пересечение — ровно то, ради чего аддон существует: он последний в порядке и должен быть последним словом по этим ключам. Неожиданных нет. **Ноль пересечений с E&F, хотфиксом, PSC и PBE** — на этом держится утверждение, что аддон 1 работает с вариантом мегапака `no e&f+psc` как есть.

Локализация: 0 общих ключей ни с одним модом. Id событий: 0.

## 4. Проверки сборки

| проверка | результат |
| --- | --- |
| файлов | 15 (+ `.metadata/metadata.json`, `README.md`, `thumbnail.png`) |
| покрытие компачей, побайтово (`filecmp`) | `hc+morg done` 4/0/0, `hc+tgr done` 5/0/0, `hc+tr+kai done` 6/0/0 (файлов / отсутствует / отличается). `.md`-отчёты в покрытие не входят: документация — не содержимое мода |
| файлов «только сборка» | 0, и ни одного незадекларированного |
| баланс скобок | 0 во всех `.txt` |
| кодировки | ни одного файла с байтом > 127 вне комментария без BOM |
| дубли top-level ключей внутри сборки | 3, все задекларированы с причиной (см. выше) |
| дубли локализации по языкам | 0 (аддон не везёт локализацию) |
| id событий | 0 |
| товары против 128 | аддон не добавляет ни одного товара — набор остаётся **111 из 128**, запас 17 |
| синхронизация в игровую папку | `Documents/Paradox Interactive/Victoria 3/mod/addon1 hc+gob+moh`, `diff -rq` чист |

Отдельная проверка мерджа `ai_strategy_default`: в смердженном теле все 11 маркеров `# KAI` из исходника KAI; кусков расхождения с ванилью 76 при 53 у KAI и 22 у MoH по отдельности — то есть мердж аддитивен и ничего не съел.

## 5. Открытые вопросы

* **`role` рядом с `executive_usage` / `agitator_usage`** у Крайслера и Твена — конструкции нет ни в ванили, ни у обоих авторов. Влияет только на этих двух персонажей; проверять в игре, не спавнятся ли они дважды и не ругается ли `debug.log` на `PostValidate`.
* ~~**Три `INJECT:` TGR в `ai_strategy_default`** гибнут под голым телом KAI ещё до аддона.~~ **Сделано 25.08.2026.** Отчёт пары TGR × KAI утверждал, что у обоих авторов здесь «полные осознанно разные стратегии»; на деле у TGR стратегии нет, есть три `INJECT:`, и голое тело KAI уносит их целиком. Мегапак теперь их переиздаёт (`zz_tr_kai_tgr_ai_default_strategy.txt`), аддон — поверх своего смердженного тела (`zz_hctr_tgr_default_strategy.txt`). Разбор по под-блокам — в `_tgr/tgr+tr+kai done/conflicts_tgr_vs_kai_report.md`.
* **Порядок внутри блока.** Требование «Mandate of Heaven после Hail, Columbia!» аддон не отменяет и не проверяет: при обратном порядке `INJECT:` MoH в `ig_rural_folk` пропадает ещё до нас, а наш файл несёт добавления MoH уже вшитыми — то есть аддон замаскирует нарушение порядка вместо того, чтобы его показать. Строка про порядок есть в README.
