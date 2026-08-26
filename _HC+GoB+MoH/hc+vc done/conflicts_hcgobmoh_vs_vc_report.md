# HC + GoB + MoH × Victorian Century — разбор пары

Дата разбора: 2026-08-26. Игра 1.13 (exe 1.13.11).
Версии: Hail, Columbia! 8.6-Roosevelt, Gates of the Bosphorus 4.0.8, Mandate of Heaven 1.4.6.1, Victorian Century (unpacked 2026-08-25, мод не объявляет версию).
Порядок: … → Victorian Century → аддон-VC → Hail, Columbia! → Gates of the Bosphorus → Mandate of Heaven → **этот компач**.

Машинный прогон `pair_matrix.py --pair "HC+GoB+MoH,VC"`: **39 общих ключей, 8 общих путей, 0 общих id событий.**

Это только табличка-разбор (аналог `conflicts_tgr_vs_vc_report.md`), а не сам компач: 39+8 позиций разного веса, часть закрывается тут же обоснованием, часть требует отдельного мерджа. Ниже — по каждой позиции факт (кто чем владеет, что реально на кону), не только вывод.

## Как читать

Для каждой позиции: путь(и)/ключ, что несёт каждая сторона (файл, префикс `INJECT:`/`REPLACE:`/`REPLACE_OR_CREATE:`/голое тело, объём), и что происходит при текущем порядке загрузки (VC раньше блока HC+GoB+MoH).

## Не конфликт — подтверждено программно и построчно

| ключ/путь | кто чем владеет | почему цело |
| --- | --- | --- |
| `ig_armed_forces` | MoH `INJECT:` (19 строк, `character_ideologies`+`on_enable`) vs VC `REPLACE_OR_CREATE:` (1009 строк, полное тело) | `character_ideologies` — плоский список, id не пересекаются (`ideology_moh_*` у MoH, `ideology_moderate`/`ideology_anti_slavery`/… у VC). `on_enable` — эффект-блок, MoH добавляет свой `if` (правило «8 Banners» для маньчжур), VC его не трогает. Тело VC переживает MoH — VC грузится раньше, MoH только инжектит в готовое тело |
| `ig_intelligentsia` | MoH `INJECT:` (26 строк) vs VC `REPLACE_OR_CREATE:` (943 строки) | То же: разные id идеологий, `on_enable` MoH — свой `if` под `c:CHI ?= THIS` (переименование в Literati, свои `add_ideology`/`remove_ideology`), в список VC не лезет |
| `ig_petty_bourgeoisie` | MoH `INJECT:` (22 строки) vs VC `REPLACE_OR_CREATE:` (885 строк) | То же: MoH правит под условием ханьской культуры, id идеологий не пересекаются |
| `je_autocracy` | MoH `INJECT: on_complete` (`set_variable = je_autocracy_complete`) vs VC `REPLACE_OR_CREATE:` (119 строк, весь journal entry, свой `on_complete`) | `on_complete` — эффект-блок, две независимые строки складываются построчно, полей с одинаковым именем нет |
| `state_trait_columbia_river` | HC `INJECT: modifier` (`building_group_bg_logging_throughput_add`) vs VC `REPLACE_OR_CREATE:` (`state_infrastructure_add`, `state_market_access_price_impact`, `battle_defense_owned_province_mult`) | Четыре разных поля модификатора, ни одного общего имени — `modifier` копит поля, не конфликтует |
| `NAI` | HC (`NUM_GROWING_COLONIES_MAX`) vs VC (`BUILDING_PRIVATIZATION_CHANCE`, `CONSTRUCTION_MAX_NUM_PRODUCTION_BUILDING_CONSTRUCTIONS_SCALED_MAX`) | Дефайны сливаются по ключу, ни одного общего имени — тот же вывод, что уже дважды подтверждён для HC × TGR и HC × KAI |
| `CHI_minguo` (coat_of_arms) | MoH (bare, 18 строк) vs VC (bare, 18 строк) | Тела **побайтово идентичны** после нормализации (тот же флаг Республики Китая 1928 года, те же два `colored_emblem`) — общий сторонний источник, как DNA в VC.3. Кто бы ни победил по пути, картинка одна и та же |
| `common/decisions/manifest_destiny.txt` | HC — весь ванильный decision закомментирован (245 строк, живой контент — журнальная цепочка в другом файле) vs VC — заглушка 11 байт (`#nothing`) | Оба автора независимо гасят decision. Тот же случай, что уже решён для HC × TGR (см. `hc+tgr done/README.md`): восстанавливать нечего, ставить решение обратно значит дать игроку Manifest Destiny дважды |

Восемь позиций закрыты без единой строки нового кода.

## Требуют работы — авто-решается порядком, только записать

| путь | кто чем владеет | решение |
| --- | --- | --- |
| `map_data/state_regions`: `STATE_GANSU`, `STATE_GUANGDONG`, `STATE_HINGGAN` | MoH — `map_data/state_regions/moh_east_asia.txt`, весь ванильный Восточноазиатский регион голым телом vs VC — `map_data/state_regions/11_east_asia.txt`, свои версии тех же трёх штатов среди прочих | При порядке «VC раньше HC+GoB+MoH» побеждает MoH автоматически — три штата из карты VC гасятся заодно с остальной 16-файловой картой VC по всему земному шару. Компача не нужно, но в README аддона-HC обязательна строка: «после VC карта восточной Азии снова ванильно-MoH-совместимая, а не VC-шная» — на случай если кто-то решит собрать без MoH или без VC |

## Требуют работы — мелкий мердж, один-два байта

| ключ | что теряется | решение |
| --- | --- | --- |
| `common/dna_data/ecchi_usa_polk.txt` (он же `ecchi_dna_james_k_polk`) | HC и VC — оба голым телом по одному пути, 122 строки, различаются **ровно одной строкой**: VC несёт лишний ген `coats = { "american_uniform_coats" 255 "all_coats" 0 }`, которого нет у HC | Тот же класс, что Гитлер в VC.3 (`ecchi_ger_hitler.txt`) — общий источник DNA, расхождение косметическое. Взять тело HC (уже во всех остальных 121 строке идентично VC) плюс строку `coats` от VC |

## Требуют работы — список объединяется, но контейнер REPLACE-ится целиком

Общая механика всех четырёх позиций ниже: MoH `REPLACE:` весь контейнер (не `INJECT:`), значит побеждает MoH целиком и список VC пропадает не потому, что записи спорят за одно имя, а потому что REPLACE не смотрит, что перечислил другой мод. Сами записи внутри не пересекаются по имени ни разу — значит мердж механический (взять список MoH + дописать список VC), редакторского решения не требует.

| ключ | MoH | VC | что внутри у VC (не пересекается с MoH) |
| --- | --- | --- | --- |
| `common/dynamic_country_names/AHU` | `REPLACE:` (28 строк, 2 записи: nian-восстание, аньхойская клика) | `REPLACE_OR_CREATE:` (16 строк, 1 запись) | `dyn_c_ahu_northern_expedition` — своя ветка про Северный поход, триггер по `northern_expedition_name_var` (система, которой у MoH нет вообще) |
| `common/dynamic_country_names/CHI` | `REPLACE:` (121 строка, 10 записей) | `TRY_INJECT:` (75 строк, 5 записей) — единственная из четырёх, что уже пробует не REPLACE, а инжект, но раз ключ создаёт MoH позже голым REPLACE — не спасает | `dyn_c_great_qing`/`dyn_c_empire_of_china` и другие — триггеры по маньчжурской культуре и монархическому CoA, не пересекаются с ванильными именами MoH |
| `common/dynamic_country_names/MCH` | `REPLACE:` (42 строки, 3 записи) | `REPLACE_OR_CREATE:` (47 строк, 3 записи) | не проверено построчно на этом прогоне — то же вероятное «разные name=», проверить при мердже |
| `common/dynamic_country_names/XIN` | `REPLACE:` (14 строк, 1 запись) | `REPLACE_OR_CREATE:` (16 строк, 1 запись) | не проверено построчно |
| `common/flag_definitions/CHI` | `REPLACE:` (209 строк, 15 записей) | `REPLACE_OR_CREATE:` (74 строки, 8 записей) | не проверено построчно — VC.7 (престижные товары) уже показал, что у CHI обе стороны активны в разных версиях, аналогичная проверка тут не помешает |

**Решение по всем пяти:** взять тело MoH, дописать записи VC в конец того же списка (та же техника, что `zzzz_addon_vc_buy_packages.txt` в аддоне-VC — один файл, тело победителя + поля/записи остальных). Перед записью проверить построчно `MCH`, `XIN` и `flag_definitions` на совпадение имён записей — не сделано в этом прогоне из-за объёма, но AHU и CHI уже подтверждают шаблон.

## Требуют работы — большой мердж против ванили (инструмент уже есть: `vic3merge3.py`)

**16 `character_templates`** — не «два независимых замысла без общего предка», как выглядело по первому проходу. 11 из 16 ключей **есть в ванили** (`common/character_templates/country_usa.txt`), HC и VC оба переписывают их `REPLACE_OR_CREATE:`/голым телом независимо, каждый решает `traits` по-своему:

| ключ | в вании? | HC traits (пример) | VC traits (пример) |
| --- | --- | --- | --- |
| `usa_general_grant` | да | `expert_offensive_planner, persistent, honorable, innovative` | `experienced_offensive_planner, persistent, alcoholic, direct` |
| `usa_admiral_dewey` | да | `experienced_naval_commander, persistent, brave` | `experienced_naval_commander, inspirational_orator, convoy_raider_commander` |
| `USA_william_cramp`, `USA_winfield_scott`, `usa_admiral_perry`, `usa_general_jackson`, `usa_general_jesup`, `usa_general_longstreet`, `usa_general_sherman`, `usa_lincoln_character_template`, `chi_daoguang_template`* | да/частично | — | — |

\* `chi_daoguang_template` — единственный не-американский из 16, MoH его только `INJECT:`-ит (`on_created`, 29 строк), см. ниже отдельно.

Остальные 5 — **своих в вании нет**, чистое совпадение id между HC (`historical_commanders_usa.txt`) и VC (`joi_commander_templates.txt`): `usa_admiral_porter`, `usa_admiral_sampson`, `usa_admiral_sigsbee`, `usa_general_bell`, `usa_general_miles`.

**Почему это решаемо тем же способом, что TGR × VC (VC.1):** там тоже казалось, что два автора спорят за одну нишу, и почти везде ваниль оказалась общим предком, а `traits` — единственное поле, где авторы реально пишут разное значение, не разные поля. Здесь ровно тот же профиль:
* для 11 ключей с ванильным предком — трёхсторонний мердж `vic3merge3.py` разрешит все совпадающие поля (`commander_usage`/`executive_usage` и прочее, что оба автора не трогают) автоматически и остановится ровно на строке `traits`, где решение действительно редакторское: чей набор трейтов ставить, или сшивать вручную (у ванили тоже есть свой список — третий вариант);
* для 5 ключей без предка мерджить не с чем — придётся решать вручную, чьё видение персонажа (или комбинация) идёт в компач; технический риск нулевой (оба тела self-contained, 20-30 строк), это чисто редакторский выбор, тот же класс, что «слот престижного товара» в VC.7.

**MoH × VC, `chi_daoguang_template`:** MoH `INJECT: on_created` (29 строк) требует, чтобы ключ уже существовал — он существует, потому что VC грузится раньше и создаёт его `REPLACE_OR_CREATE:` (17 строк, только `traits`). Раз `on_created` — эффект-блок и VC его не занимает, это **отдельно от американской пятёрки не конфликт** — тот же профиль, что `ig_*`/`je_autocracy` выше. Ставить в таблицу «не конфликт», а не в общий список character_templates.

## Требуют работы — четыре готовых файла спорят за один путь

| путь | текущий владелец (после HC.2/hc+tgr done) | что несёт VC | масштаб |
| --- | --- | --- | --- |
| `common/history/countries/chi - china.txt` | MoH (тело) + TGR (`add_company`) — уже смерджено в `hc+tgr done` | Собственная китайская история 1836: 8 `activate_law`, свой набор технологий, `set_market_capital`, 4 `amendment` (соляная монополия, земельный налог, тифа-указ, регистрация домохозяйств) — 101 строка | Большой: активированные законы у VC и у MoH/TGR **не идентичны** (например, HC/MoH-цепочка не активирует `law_type:law_imperial_examination` в этом наборе, а VC — активирует; нужно свести один непротиворечивый список законов Китая на старте, а не просто дописать) |
| `common/history/countries/tur - ottoman empire.txt` | GoB (тело) + TGR (`add_company`) — уже смерджено | Собственная османская история: 8 технологий, налоги, `add_taxed_goods`, 9 `activate_law`, 2 `amendment` (соляная монополия, кануннаме) — 79 строк | Тот же профиль, что China: списки законов пересекаются частично, но не совпадают дословно |
| `common/history/countries/usa - usa.txt` | HC (240 строк) | VC (200 строк) — не читано построчно в этом прогоне | Требует отдельного разбора: обе стороны — полноценная альтернативная история США на старте, не мелкая правка |
| **`ig_landowners`** | HC — `00_landowners.txt`, голое тело, 788 строк (уже используется как база `zz_hct_ig_landowners.txt` с числами TGR внутри) | `REPLACE_OR_CREATE:` (961 строка — крупнее и ванили, и HC) | Дописывать в уже смердженный `zz_hct_ig_landowners.txt`, не в сырой HC. Объём у VC больше ванили почти на 200 строк — велика вероятность содержательной переработки, не только косметики; нужен построчный разбор, не сделан в этом прогоне |
| **`ig_rural_folk`** | HC (560, база) + MoH (`INJECT:`, 316 строк, из которых по HC.2 реально только 2 собственных под-блока) — уже смерджено в `zz_hct_ig_rural_folk.txt` | `REPLACE_OR_CREATE:` (684 строки) | Тройной мердж поверх уже готового файла: HC+TGR+MoH (сделано) + VC (эта задача). Тот же принцип, что аддон-VC уже применил к `ig_landowners`/`ig_rural_folk` в обратную сторону (VC.1: «дописывать надо именно в эти два файла») |
| `common/scripted_buttons`: `ban_opium_button`, `unban_opium_button` | MoH `REPLACE:` (84 / 29 строк) | VC `REPLACE:` (47 / 33 строки) | Оба используют голый `REPLACE:` (не `REPLACE_OR_CREATE:`) — значит запись существует до них (ваниль), и обе стороны переписывают её целиком под свою версию китайской опиумной политики. Нужен построчный разбор вручную — не сделан в этом прогоне |

## Что осталось непроверенным в этом прогоне

* `MCH`, `XIN`, `flag_definitions/CHI` — не сверены построчно на совпадение имён записей (см. таблицу списков выше);
* `usa - usa.txt`, `ban_opium_button`, `unban_opium_button` — не читаны построчно, только объём и префикс;
* 16 `character_templates` — только `traits` и присутствие в вании проверены; `commander_usage`/`executive_usage`/`on_created` не сверены построчно ни для одного ключа;
* соответствие `activate_law` списков VC против MoH+TGR для China и Ottoman Empire — не сверено пункт за пунктом, только визуально «списки разные».

## Итог

39 ключей + 8 путей: **8 закрыто как не-конфликт** (программно и построчно), **1 закрыто как авто-решаемый порядком загрузки** (три штата карты), **1 мелкий мердж на одну строку**, **5 позиций** (`dynamic_country_names` × 4 + `flag_definitions`) — механический мердж списков без редакторского решения, **16 character_templates** — техническая часть решается `vic3merge3.py` по образцу VC.1, редакторская часть (какие `traits`, у пяти ключей — чей персонаж целиком) остаётся открытой, **6 позиций** (`ig_landowners`, `ig_rural_folk`, `chi - china.txt`, `tur - ottoman empire.txt`, `usa - usa.txt`, два opium-кнопки) — крупный контентный мердж, ещё не начат, ключевая часть будущей работы над аддоном-HC.
