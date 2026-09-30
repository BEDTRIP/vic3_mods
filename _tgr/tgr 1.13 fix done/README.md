# ComPatch: The Great Revision — 1.13 Fields Fix (TGR.1, TGR.3)

<!-- meta
пара: TGR (одиночный фикс, не пара)
статус: done
версии: Game 1.13 (exe 1.13.11) — TGR 1.13.11 (мастерская, 24.09.2026).
позиция: после The Great Revision; в наборе с Grey's его перекрывает `_greys/greys+tgr done` (так и задумано)
файлов: 8
генератор: tools/regen_tgr_113_fix.py (пишет и сюда, и в `megapack`, `megapack no t&r`)
зависит от: —
-->

> **25.09.2026 — TGR.3, папка переименована из `tgr ranks fix done`.** TGR переиздаёт не только ранги:
> ещё ряд записей написан до 1.13. Однозначные поля 1.13 возвращаются через `INJECT:` (дописывает,
> ничего не стирая), каждое читается из ванили: лимит вовлечённости (`max_target_involvement`,
> `target_involvement_applies_to`) у договоров `military_assistance` и `foreign_investment_rights` и
> `non_fulfillment` у первого; `category` у четырёх компаний (EIC, Российско-американская, Imperial
> Arsenal, LKAB), `prestige_goods_trigger` у пяти; `obsession_chance` у рыбы и бакалеи; `aliases` у
> девяти промышленных зданий; у законов — содержимое DLC 1.13, которого старые тела TGR не знают
> (Сакоку и система Эдо у Японии, мэнориализм у Австрии, анархия и фабричные советы, варианты законов
> через `parent`, открытие Японии) — 19 законов; `ai_value` у `pm_simple_organization`;
> `is_shown_in_lobby` у трёх дневников объединений. Файлы `common/<категория>/zz_tgr_113_fields.txt`. Остальное, что находит
> скан (законы, налоги TGR, дневники объединений, формирование Германии, методы ТЦ и охлаждения), — это
> переделка TGR или перекрыто более поздним модом; разбор — в плане, TGR.3. С Grey's договор
> `foreign_investment_rights` переиздаёт `grey_diplo` — те же два поля добавлены в `greys_kai_fix done`.

> **25.09.2026 — создан (TGR.1).** TGR переиздаёт все восемь рангов стран телами, написанными до
> 1.13, и в игре пропадают поля 1.13: `treaty_article_cost`, `ai_pool_character_multiplier`,
> `ai_innovation_critical_threshold`, `country_max_unassigned_generals_add` / `_admirals_add`. Здесь —
> тела ванили 1.13 и поверх них собственные правки TGR, прочитанные из его файлов:
> `country_construction_add` (+30 великие, +20 крупные), ослабленная поддержка независимости,
> торговое преимущество из `TGR_TRADE_country_ranks.txt` (иначе наш полный перевыпуск его бы стёр).
> Ставка по займам в зависимости от ранга не возвращается — решение 27.08.2026 (GR.7a): у TGR своя
> система займов. Любое новое расхождение TGR с ванилью останавливает генератор — его надо
> разобрать руками. С пачкой Grey's эти ранги перекрывает `greys+tgr done` (тела soft_pop + поля TGR).

## Для мастерской

This is part of [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3640735868]this MegaComPatch[/url]
[h1]ComPatch: The Great Revision — Country Ranks Fix[/h1]
[b]Game 1.13 (exe 1.13.11) — The Great Revision.[/b]

[h2]Load order[/h2]
[list]
[*]The Great Revision
[*][b]This patch[/b]
[/list]

[h2]What it does[/h2]
The Great Revision re-issues all eight country ranks with bodies written before game 1.13, so every rank silently loses the fields 1.13 added: treaty article cost, AI character pool and innovation thresholds, and the extra unassigned generals and admirals. This patch re-issues the ranks on the 1.13 vanilla bodies and keeps everything TGR changes on purpose: construction for great and major powers, lower support for independence, TGR's trade advantages, and no rank-dependent loan interest (TGR has its own loan system).
