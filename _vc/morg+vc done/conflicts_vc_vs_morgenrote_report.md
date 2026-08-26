# VC × Morgenrote — разбор пары (VC.3)

Машинная матрица (`tools/pair_matrix.py --pair "VC,Morgenrote"`, 26.08.2026): **101 общий ключ, 1 общий путь**, 0 общих id событий. Порядок загрузки: Morgenrote (в основной пачке) → … → Victorian Century. Компач — `zz_vc_morg_*`, грузится после VC.

## Итог по кластерам

| кластер | ключей | реальный конфликт? | что сделано |
| --- | --- | --- | --- |
| `common/buy_packages` (`wealth_10`…`wealth_99`) | 90 | да | `zz_vc_morg_buy_packages.txt` — переиздан `TRY_INJECT` |
| `common/pop_needs` (`popneed_free_movement`, `_leisure`, `_luxury_items`) | 3 | да | `zz_vc_morg_pop_needs.txt` — переиздан `TRY_INJECT` |
| `common/character_templates` (Диккенс, Карл Юхан Бернадот) | 2 | да | `zz_vc_morg_character_templates.txt` — переиздан `INJECT` |
| `common/mobilization_options` (aerial_recon, balloon_recon, chemical_weapons) | 3 | 2 из 3 нет, 1 не выяснен | не патчится, см. ниже |
| `common/technology/technologies` (civilizing_mission, organized_sports) | 2 | нет | не патчится, оба инжекта в разные под-блоки/поля |
| `common/dna_data/ecchi_ger_hitler.txt` (путь) + `ecchi_dna_adolf_hitler` (ключ) | 1+1 | нет | не патчится, см. ниже |

90 + 3 + 2 = 95 ключей ушли в компач тремя файлами. 3 + 2 = 5 ключей — не конфликт, ничего не потерялось. 1 ключ (`chemical_weapons`) — не выяснен, оставлен открытым пунктом. Путь `ecchi_ger_hitler.txt` — не конфликт.

## Реальные конфликты (написан компач)

### `common/buy_packages` — 90 ключей, `wealth_10`…`wealth_99`

Механика та же, что в паре E&F × VC (`ef+vc done`) и в старом компаче T&R × VC (`_vc/kai+vc outdate/.../zz_vc_tr_buy_packages.txt`): VC грузится последним и делает `REPLACE_OR_CREATE:wealth_N` — полное тело без `popneed_entertainment` (собственная потребность Morgenrote, привязанная к его же товарам `manzoni_prints`, `elgar_music`, `fine_art`, `air_travel`, `services`). Morgenrote инжектит эту потребность в `wealth_10`…`wealth_99` (90 из 99 уровней; `wealth_1`…`wealth_9` не трогает). VC нигде не упоминает `popneed_entertainment` — проверено генератором по всему файлу перед записью.

**Совпадение с T&R — не копирование.** Значения `popneed_entertainment` по всем 90 уровням у Morgenrote байт-в-байт совпадают с тем, что раньше восстанавливал компач против T&R. Это не значит, что один компач наследует данные другого — генератор читает Morgenrote «живьём» из его собственного `mr_buy_packages.txt`. Совпадение — общий сторонний источник у T&R и Morgenrote (см. `Правила работы...`, раздел 279: «общая не-ванильная база — обычное дело»).

### `common/pop_needs` — 3 ключа

VC делает `REPLACE_OR_CREATE:` на все три потребности полными телами. Morgenrote инжектит в них по одной-три записи `entry`:

* `popneed_free_movement` — Morgenrote добавляет `air_travel` (вес 4). У VC в теле — `transportation`, `automobiles`; `air_travel` нет.
* `popneed_leisure` — Morgenrote добавляет `air_travel` (вес 1.0). У VC в теле девять товаров (`services`, `fine_art`, `small_arms`, `aeroplanes`, `automobiles`, `radios`, `opium`, `clippers`, `steamers`); `air_travel` нет.
* `popneed_luxury_items` — Morgenrote добавляет три записи: `fine_art`, `elgar_instruments` (собственный товар Morgenrote), `rubber`. У VC в теле — `silk`, `luxury_clothes`, `luxury_furniture`, `porcelain`, `radios`; ни одного совпадения.

Ни один товар из добавок Morgenrote не встречается в теле VC — компач дописывает эти `entry` обратно через `TRY_INJECT`, без риска задвоить существующую запись (генератор проверяет это перед записью).

### `common/character_templates` — 2 ключа

Оба — персонажи, которых VC переиздаёт `REPLACE_OR_CREATE:` целиком (тела сгенерированы под события/DNA VC), а Morgenrote инжектит в них отдельные поля:

* **`gbr_charles_dickens_character_template`.** Morgenrote добавляет `role = character_role_manzoni_writer`, два трейта (`manzoni_writer_fiction`, `manzoni_genre_social_critic`) и `on_created = { mr_make_character_writer_effect = yes }` — всё это часть механики Morgenrote «персонаж-писатель». У VC в теле нет ни `role`, ни `on_created`, а список трейтов свой (`cautious`, `literary`, `persistent`) — ни имя поля, ни содержимое трейтов не пересекаются.
* **`swe_karl_johan_bernadotte_template`.** Morgenrote добавляет один трейт, `mr_ruler_trait_karl_xiv`, в список `traits`. У VC список трейтов свой (шесть штук, вплоть до `special_character_old_marshal`), этого трейта там нет.

Оба случая — чистая надстройка (список `traits` — `INJECT` дописывает в него, не заменяет, как в прецеденте `company_standard_oil` из `regen_vc_ef.py`), полей с одинаковым именем нет ни там, ни там.

## Не конфликт, компач не нужен

### `common/mobilization_options` — 3 ключа

Ни VC, ни Morgenrote не делают `REPLACE_OR_CREATE:` — оба используют аддитивные префиксы (`INJECT:`/`TRY_INJECT:`/`TRY_REPLACE:`) на одних и тех же ванильных записях, значит вопрос не «что съедено», а «пересекаются ли поля».

* **`mobilization_option_aerial_recon`, `mobilization_option_balloon_recon`.** Morgenrote (`TRY_INJECT:`) трогает только `group`; VC (`INJECT:`) — только `upkeep_modifier`. Разные поля, оба применяются, компач не нужен — тот же случай, что `mutual_funds` в паре E&F × VC.
* **`mobilization_option_chemical_weapons` — не выяснено, компач НЕ написан.** Morgenrote (`TRY_REPLACE:`, грузится раньше) переиздаёт под-блок `upkeep_modifier` целиком: `goods_input_fertilizer_add = 2`. VC (`INJECT:`, грузится позже) добавляет свой `upkeep_modifier = { goods_input_fertilizer_add = 0.5, goods_input_small_arms_add = 1, goods_input_artillery_add = 1 }` — то же имя под-блока, и `goods_input_fertilizer_add` в нём тоже.

  Прецедент `base_values` (пара E&F × VC) показал, что поля с суффиксом `_add` суммируются по всем источникам — но там речь о `common/static_modifiers`, стране-уровневом пуле модификаторов, который движок агрегирует по определению. Здесь `upkeep_modifier` — часть тела ОДНОЙ записи `mobilization_option`, и не установлено, суммируются ли повторные `_add`-поля внутри одного такого под-блока так же, как в пуле статических модификаторов, или второе объявление (VC, оно позже) просто перекрывает первое (Morgenrote). Оба исхода правдоподобны, честной проверки в игре не было.

  Писать компач вслепую опасно в обе стороны: если поля и так суммируются, свой файл добавит третье значение и `goods_input_fertilizer_add` утроится; если срабатывает «второе перекрывает первое», ничего страшного и без компача не происходит — но если наоборот, добавка Morgenrote тихо исчезнет, и это не будет видно без похода в игру. Оставлено открытым пунктом (см. ниже), решение — только после проверки, а не догадкой.

### `common/technology/technologies` — 2 ключа

Оба мода используют только `INJECT:`/`TRY_INJECT:`, `REPLACE_OR_CREATE:` не встречается — значит вопрос снова в пересечении полей.

* **`civilizing_mission`.** Morgenrote трогает `modifier` (`country_infamy_generation_against_unrecognized_mult`), VC — `on_researched` (эффект при исследовании). Разные поля верхнего уровня, ничего не пересекается.
* **`organized_sports`.** Оба трогают `modifier`, но разными полями: Morgenrote — `country_prestige_mult`; VC — `country_authority_mult`, `country_influence_mult`, `building_group_bg_service_employee_mult`. Тот же случай, что `mutual_funds` в паре E&F × VC («блоки `modifier` накапливаются, а не конфликтуют»). Morgenrote отдельно меняет `era` (со 2-й на 3-ю) и добавляет `unlocking_technologies` — VC этого не трогает вообще.

### `common/dna_data/ecchi_ger_hitler.txt` — 1 путь, 1 ключ (`ecchi_dna_adolf_hitler`)

Единственное настоящее совпадение пути в паре. VC грузится последним и подменяет файл целиком (это не INJECT — оба мода кладут файл под одним и тем же ванильным путём). Сравнение показало: тела **побайтово идентичны по содержанию**, отличается только форматирование (Morgenrote — по 4 значения гена в строку, VC — по одному). Расхождений в цифрах ровно два:

* у VC есть один лишний ген, `coats` (Morgenrote его не задаёт) — не потеря, VC и так побеждает;
* `gene_stubble`: у Morgenrote `"stubble_low" 0 "stubble_low" 0`, у VC `"stubble_low" 127 "stubble_low" 127` — одно косметическое значение интенсивности щетины.

Собственного контента Morgenrote здесь нет — оба автора явно взяли DNA-портрет Гитлера из одного стороннего источника (см. `Правила работы...`, раздел 279). Мерджить нечего: побеждает VC, ничего осмысленного не теряется.

## Открытые пункты

* **`mobilization_option_chemical_weapons`.** Проверить в игре: включить только Morgenrote + VC (или их компач-заготовку без этого файла) и посмотреть фактический расход `fertilizer` у мобилизационной опции «химическое оружие» — 2.5 означает сложение, 0.5 означает «выигрывает поздний INJECT». Дешёвая проверка, как и вариант с `enfield_rifle` в VC.7.
