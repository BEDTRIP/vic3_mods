# Аддон 3 (Grey's): пересчёт после добавления `_grey_soft_pop` и `grey_deeper_cinosphere`

Дата: 2026-08-24. Пачка Grey's выросла с шести модов до восьми.

| мод | версия | game в metadata | id | файлов |
| --- | --- | --- | --- | --- |
| `_grey_soft_pop` — Grey's Soft Pop Adjustments | — | — (теги `1.13`) | 3336914177 | 83 |
| `grey_deeper_cinosphere` — Grey's Deeper Sinosphere | — | — (теги **`1.12`**) | 3108195724 | 45 |

## Что изменилось в матрице

| пара | было | стало | прирост |
| --- | --- | --- | --- |
| Grey's × TGR | 84 | **97** | +13 (весь soft_pop) |
| Grey's × T&R+KAI | 124 | **128** | +4 (весь soft_pop) |
| Grey's × HC+GoB+MoH | 3 / 1 путь | **11 / 1 путь** | +8 (5 от cinosphere, 3 от soft_pop) |
| Grey's × E&F+hotfix | 24 | 24 | — |
| Grey's × Morgenrote | 35 | 35 | — |
| Grey's × PBE | 1 | 1 | — |
| Grey's × PSC | 8 | 8 | — |
| Grey's × LLWA | 11 | 11 | — |

Товары пересчитаны на всей цепочке: **111 из 128**, оба новых мода товаров не добавляют. Id событий не пересекаются ни с кем.

---

## 1. КРИТИЧНО: `_grey_soft_pop` выключает Hail, Columbia! целиком

`common/scripted_triggers/00_SPA_mod_compat_active_triggers.txt`:

```
# Hail Columbia
REPLACE_OR_CREATE:is_usfp_active = {
	always = no
}
```

Hail, Columbia! объявляет свой флаг сам, как положено, в `zz_usfp_compatibility_trigger_overwrites.txt`:

```
REPLACE_OR_CREATE:is_usfp_active = {
	always = yes
}
```

Порядок в цепочке: HC грузится в блоке HC+GoB+MoH, soft_pop — в пачке Grey's, то есть **позже**. `REPLACE_OR_CREATE` позднего мода побеждает → флаг остаётся `no` → **каждый гейт `is_usfp_active = yes` внутри Hail Columbia становится ложным.** Ни строчки в логе.

Это тот же класс бага, что `Grey_DIS_is_active` у `grey_diplo`, но с обратным знаком и куда дороже: там мод не включал сам себя, здесь мод выключает чужой контент-мод.

**Лечение:** файл аддона 3, грузящийся после soft_pop, с `REPLACE_OR_CREATE:is_usfp_active = { always = yes }`. Три строки.

**Автору написать:** соглашение CMF — флаг `*_is_active` объявляет CMF (`no`) и сам детектируемый мод (`yes`). Третий мод объявлять чужой флаг не должен: он не знает своей позиции относительно детектируемого мода, и при загрузке позже гасит его.

Там же `REPLACE_OR_CREATE:Ultra_RE_is_active_trigger = { always = no }` — этого мода в наборе нет, безвредно.

## 2. `_grey_soft_pop` × TGR — восемь рангов страны

`common/country_ranks/MoG_SPA_country_ranks.txt`, `TRY_REPLACE:` полным телом на все восемь: `great_power`, `major_power`, `minor_power`, `unrecognized_major_power`, `unrecognized_power`, `unrecognized_regional_power`, `insignificant_power`, `decentralized_power`.

TGR правит те же восемь через `REPLACE_OR_CREATE` в `TGR_POLITICS_country_ranks.txt`. soft_pop позже — **всё, что TGR сделал с рангами, откатывается.**

На примере `great_power`:

| строка | ваниль | TGR | soft_pop (победит) |
| --- | --- | --- | --- |
| `country_construction_add` | нет | **30** (добавка TGR, «BEFORE DIDN'T EXIST») | нет |
| `treaty_article_cost` | 2.0 | убрано | 2.0 |
| `ai_pool_character_multiplier` | 1.0 | убрано | 1.0 |
| `ai_innovation_critical_threshold` | 1.0 | убрано | 0.80 |
| `country_loan_interest_rate_mult` | −0.5 | закомментировано | −0.5 |
| `country_max_unassigned_generals_add` / `_admirals_add` | 3 / 3 | убрано | 3 / 3 |
| `country_agitator_slots_add` | 2 | 2 | 3 |
| `country_support_independence_weekly_liberty_desire_add` | 0.20 | 0.1 | 0.20 |
| `state_migration_pull_mult` | 0.25 | 0.25 | 0.1 |
| `country_leverage_resistance_add` | 1000 | 1000 | 800 |

Самое дорогое — `country_construction_add` по рангам: это добавка TGR, которой в ванили нет вообще, и она уходит на всех восьми рангах. У `major_power` то же самое с 20.

Мердж: взять тело soft_pop (он последний) и вернуть в него правки TGR — убранные строки убрать, `country_construction_add` добавить. По каждой строке решить, чьё значение: TGR тюнил под свою экономику, soft_pop — под свою.

## 3. `_grey_soft_pop` × TGR — четыре закона гражданства

`zMoG_SPA_citizenship.txt`, `TRY_REPLACE:` на `law_ethnostate`, `law_racial_segregation`, `law_cultural_exclusion`, `law_national_supremacy`. Среди названных под-блоков — `acceptance_modifier`.

TGR инжектит ровно в него:

```
INJECT:law_ethnostate       = { acceptance_modifier = { country_political_strength_full_acceptance_mult = -0.25 } }
INJECT:law_national_supremacy = { acceptance_modifier = { country_political_strength_full_acceptance_mult = -0.20 } }
INJECT:law_racial_segregation = { acceptance_modifier = { ... } }
INJECT:law_cultural_exclusion = { acceptance_modifier = { ... } }
```

soft_pop позже и называет `acceptance_modifier` → **все четыре инжекта TGR пропадают.**

Hail Columbia инжектит в `law_ethnostate` под-блок `on_activate` — soft_pop его тоже называет (`on_enact`, `on_activate` — разные ключи, у soft_pop в списке `on_enact`), так что инжект HC должен выжить. Проверить в игре.

## 4. `_grey_soft_pop` × TGR — два define

| define | ваниль | TGR | soft_pop (победит) |
| --- | --- | --- | --- |
| `NPops.MAX_DEMAND_ADJUSTMENT_BASE_AMOUNT` | 0.01 | 0.05 | 0.01 |
| `NPops.MAX_DEMAND_ADJUSTMENT_SCALED_AMOUNT` | 0.09 | 0.10 | 0.09 |

soft_pop возвращает ванильные значения. Остальные 118 его define ни с кем не пересекаются.

## 5. `_grey_soft_pop` × Hail Columbia и T&R — `decree_greener_grass_campaign`

Тройной конфликт, все трое на одну запись:

```
00_decree.txt                         [ваниль]    bare     114L
ztr_decree.txt                        [T&R]       INJECT     7L
usfp_decrees_overwrite.txt            [HC]        REPLACE  119L
zzz_MoG_SPA_greener_grass_decree.txt  [soft_pop]  REPLACE  108L   <- побеждает
```

soft_pop последний → теряются и инжект T&R, и переписанный декрет Hail Columbia. Один файл аддона с объединённым телом.

## 6. `grey_deeper_cinosphere` × Mandate of Heaven — пять культур

`han`, `hakka`, `manchu`, `min`, `yue`:

```
00_cultures.txt              [ваниль]      bare          86L (han)
moh_cultures.txt             [MoH]         INJECT       107L   имена: male/female_common_first_names, noble_last_names, common_last_names
zz_JNI_EINI_extra_imports.txt [cinosphere] TRY_REPLACE  615L   <- побеждает
```

У `manchu` MoH делает не `INJECT`, а `REPLACE` (77L) — и он тоже проигрывает cinosphere (191L).

cinosphere в своём `TRY_REPLACE` называет `male_common_first_names`, `female_common_first_names`, `common_last_names`, `traditions`, `obsessions`, `ethnicities`, `graphics`, `heritage`, `language` — то есть ровно те под-блоки, в которые MoH добавляет свои имена. **Китайские имена от Mandate of Heaven пропадают**, вместе с правками `manchu`.

Заметно и обратное: cinosphere **не называет** `noble_last_names` у `han` (ваниль называет, MoH инжектит) — этот под-блок должен уцелеть от предыдущего слоя. Проверить: если `noble_last_names` останется от MoH, а всё остальное от cinosphere, получится смесь, которую ни один автор не задумывал.

Файлы cinosphere: `zz_JNI_EINI_extra_imports.txt` (han, hakka, manchu, min) и `zMoG_DS_K_cultures_edit.txt` (yue).

## 7. `grey_deeper_cinosphere` объявлен для 1.12

В `metadata.json` тег `1.12`, `supported_game_version` пустой. Мод трогает `common/cultures`, `common/discrimination_traits`, `common/decisions`, `events`. Отдельная задача — сверить его против ванили 1.13: в 1.13 менялись `cultures` (`seal_and_signature_texture` есть в ванильных телах и отсутствует в телах cinosphere) и структура `discrimination_traits`.

Признак того же класса, что стухшая копия `03_political_strategies.txt` у LLWA: тело, скопированное из старой ванили, тихо откатывает то, что игра с тех пор добавила.

## 8. Мелочь и то, что оказалось чисто

* `grey_deeper_cinosphere` добавляет **один** новый `discrimination_trait` и **ни одного** ванильного не перекрывает. Чисто
* cinosphere не пересекается ни с одним другим модом пачки Grey's, ни с E&F, Morgenröte, PBE, PSC, T&R, LLWA
* `_grey_soft_pop` × `_grey_soft_econ` — один общий ключ `common/pop_types|peasants`. Один автор, скорее всего намеренно, но тела не сравнивались
* `_grey_soft_pop` объявляет шесть чужих флагов `com_law_*_alternative_trigger = { always = no }` из реестра CMF. В нашем наборе безвредно: эти флаги объявляет только сам CMF, никто не ставит `yes`. Но шапка файла прямо говорит, что он рассчитан грузиться «сразу после `com_law_blocker_triggers.txt`» — то есть автор считал порядок по имени файла. При реальном порядке (по модам) soft_pop окажется позже любого мода, который поставит такой флаг в `yes`, и погасит его. Записать в правила, автору сказать
* Оба новых мода товаров не добавляют, id событий не пересекают
