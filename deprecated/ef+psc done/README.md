# PSC + E&F ComPatch

<!-- meta
пара: E&F × PSC
статус: done
версии: —
позиция: —
файлов: 80
генератор: —
зависит от: —
-->

> **25.09.2026, поздняя ночь — кнопки стимула 9-12 (по прогону 1850, решение пользователя).**
> `scripted_guis/zz_pb_ef_speculative_pcs_sguis.txt`: кнопки больше не строят секторы (частная очередь их
> не брала) и не требуют нулевого штрафа. Теперь это снижение ставки на 1-4% с ценой: +10 пунктов штрафа
> мощностей за каждый 1%, доступно при штрафе < 90 / 80 / 70 / 60, откат 12 месяцев. ИИ-ветка
> (`scripted_buttons/zz_ef_buttons.txt`) выключена: ставку ИИ она не снижала. Тексты — в
> `zz_pb_ef_psc_l_*.yml` (ключи внесены в `MANUAL_LOC_KEYS` генератора), описание секции дополнено
> абзацем «Стимул». ИИ снимает запрет частных секторов при штрафе < 10 (было «= 0», запрет залипал).

> **25.09.2026, ночь — шкалы в панели через CMF.** Убран `gui/journal_entry.gui` (копия ванили с одной
> правкой): CMF сам переопределяет `journal_entry_panel`, и наша копия в мегапаке, грузящемся после
> CMF, могла перебить его панель. Вместо неё запись журнала кладёт пустой виджет
> `zz_pb_ef_fso_hide_bars_widget` в `com_custom_widget_container_scripted_progress_bars` — так CMF
> не рисует стандартные шкалы этой записи. Без CMF шкалы в панели задвоятся, и только.

> **25.09.2026, поздний вечер — пузырь ушёл в хотфикс (EF.29).** Месячный пересчёт пузыря,
> уведомление, значения шага и модификатор без штрафа стройки — теперь в E&F Hotfix. Здесь из пузыря
> остался только вид секции в журнале; она читает `zz_ef_bubble_step_eff` хотфикса, поэтому компач
> зависит от хотфикса (добавлено в `metadata.json`).

> **25.09.2026, вечер — шкалы v5.** Шкалы снова внутри секций, как было (текст «Избыточные
> строительные мощности: n», «Спекулятивный пузырь: n%»); шкалы записи журнала оставлены только для
> выносного дневника — в панели журнала их прячет `gui/journal_entry.gui` (ванильный файл, одна
> строка: `JournalEntry.GetType.GetKey` ≠ `financial_center_je_2`). Секции снова в контейнере 3.
> Кнопка запрета / разрешения по центру.

> **25.09.2026, днём — секция стройки v4** (по прогону до 1847). Значения — таблица 2 × 4 в стиле
> плиток бюджета E&F: секторы, городские центры, ставка, лимит (% и уровни) / соотношение к лимиту
> (выше 100% красное), целевой штраф, динамика, текущий штраф. Под ней статус запрета и кнопка
> запрета / разрешения, под ними кнопки E&F 9-12 — теперь всегда (неактивны с подсказкой, пока
> штраф не ноль). Описание — абзацы, начинающиеся с термина, формулы там. Обе секции раскрыты по
> умолчанию. Шкалы — снова шкалы записи журнала (их показывает выносной дневник), подписаны нашими
> названиями в `replace/zz_pb_ef_psc_l_*`; секции перенесены в `custom_widget_container_4`, прямо
> под шкалы, собственных шкал у секций больше нет (и ошибки `ScriptedProgressBar` в `error.log`).

> **25.09.2026 — избыточные мощности v3** (по прогону 1837: при −85% эффективности стройки
> Британия нарастила стройку 400 → 750). Штраф теперь на выработку секторов стройки
> (`building_construction_sector_throughput_add` −1% за пункт, виден в подсказке сектора). Индекс
> идёт к цели `round(100 × (1 − лимит / секторы))` по 2 в месяц при разрыве > 10, иначе по 1;
> таблица шагов снята. В секции — строка цели; кнопка запрета над кнопками E&F 9-12.

> **24.09.2026, поздний вечер — журнал УФС.** Свои секции пузыря и избыточных мощностей
> (`gui/scripted_widgets/zz_pb_ef_fso_widgets.gui`, sgui — `scripted_guis/zz_pb_ef_fso_sguis.txt`):
> шкала → вычисленные значения (выше/ниже лимита, ±n в месяц, красное/зелёное) → кнопки → описание.
> Термин «перестроенная экономика» → «избыточные строительные мощности». Шкалы журнала снова
> закомментированы, общее описание журнала пустое, кнопки запрета у игрока в секции, журнальные —
> только ИИ; `has_role = character_role_executive`; `zz_pb_ef_hide_pcs_demolish.txt` удалён.

> **24.09.2026, второй заход — локализация и кнопка 13.** Все наши перекрытия чужих строк
> перенесены в `localization/<язык>/replace/` (`zz_pb_ef_psc_l_*`, генерируемые
> `zz_pb_ef_psc_je_l_*`, `zz_ef_psc_modifiers_l_*`, `zz_ef_tgr_private_ownership_stock_l_*`):
> локализация — «кто первый», E&F и V4 RUS определяют эти ключи раньше, и вне `replace/` файлы
> не действовали. Генератор `regen_ef_psc_copies.py` пишет в `replace/`. Описание журнала УФС
> (`financial_center_je_2_reason`, `_reason_2`) и два концепта лимита переписаны под EF.18 v2
> (en + ru, прочие языки — английский). Кнопка 13 у игрока спрятана
> (`scripted_guis/zz_pb_ef_hide_pcs_demolish.txt`, `no_PCS_growing_visibility` → нет).

> **24.09.2026, вечер — EF.18 v2, перестроенная экономика** (заменяет v1 от 24.09; не проверено в игре).
> Лимит секторов = уровни городских центров × (1 − 5 × ставка ЦБ) — переиздан
> `building_urban_center_lvl_by_base_rate` (`script_values/zz_pb_ef_overbuild_values.txt`,
> ручка `zz_pb_ef_css_rate_mult`). Счётчик `speculative_share_2` ведёт наш
> `on_actions/zz_pb_ef_overbuild_counter.txt` раз в месяц по утверждённой таблице шагов
> (+5…−10), штраф — модификатор страны `zz_pb_ef_overbuilt_economy`: −1% эффективности
> стройки (`state_construction_mult`) за пункт; `throughput` регулятора PSC сам гасит каждую
> неделю, поэтому не он. Журнал `financial_center_je_2` переиздан
> (`journal_entries/zz_pb_ef_financial_center_je.txt`): обе шкалы видны, кнопки 13 нет,
> строительная часть — в нашем счётчике, две кнопки «запретить / разрешить частные секторы
> стройки» (`scripted_buttons/zz_pb_ef_css_private_ban_buttons.txt`, флаг в `can_build_private`
> и `ai_nationalization_desire` сектора). Пузырь больше не режет стройку
> (`static_modifiers/zz_pb_ef_bubble_no_construction.txt`). Уведомления в ленту, когда пузырь
> или перестройка входят в новую десятку (`common/messages/zz_pb_ef_overbuild_messages.txt`).
> Старые сейвы: один раз снимаются модификаторы v0/v1 с секторов. Файлы v1 переименованы:
> `zz_pb_ef_overbuilt_brake_values.txt` → `zz_pb_ef_overbuild_values.txt`,
> `zz_pb_ef_psc_overbuilt_off.txt` → `zz_pb_ef_overbuild_counter.txt`,
> `zz_pb_ef_overbuilt_brake.txt` → `zz_pb_ef_overbuild_modifiers.txt`, локализация →
> `zz_pb_ef_overbuild_l_*.yml`. Из `zz_pb_ef_psc_l_*.yml` убрана строка «перестройка отключена
> компачем».

## Для мастерской

This is part of [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3638078714]this MegaComPatch[/url]
[h1]PSC + E&F ComPatch[/h1]
E&F's "private construction sector" breaks the economy once you are rich enough: it is in a building group with [i]is_government_funded = no[/i], so nothing it consumes ever reaches your budget, yet it still hands the country construction points. Its top method gives [b]double[/b] the construction of the vanilla sector for [b]a quarter[/b] of the input goods, and sells stock on top. Delete your government construction sectors and you build for free.

This compatch fixes that by handing construction over to PSC. PSC turns construction sectors into a real market — they produce construction goods, a regulator converts those into construction points, and the treasury and the investment pool are billed for every unit. E&F's monetary and financial layer is then rewired onto that same sector, so both mods talk about one building instead of two.

[h2]Load order[/h2]
[list]
[*]Expanded Topbar Framework (or [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3333043079]Dence UI[/url])
[*]Private Sector Construction (PSC)
[*]Economic & Financial (E&F)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3520140574]my E&F RU Localization (if u need)[/url]
[*][b]E&F 1.13.10 Hotfix[/b] — [b]required[/b], see below
[*][b]PSC + E&F ComPatch (this mod)[/b]
[/list]

[i]Place other mods after this only if they do not overwrite the same files in common/.[/i]

[h2]The hotfix is not optional[/h2]
Victoria 3 caps the goods database at 128 entries and crashes on entering a campaign if you go over — silently, with nothing in error.log. Vanilla ships 53 goods, E&F adds 73 and PSC adds 4, which lands on 130. The [b]E&F 1.13.10 Hotfix[/b] trims eight unused currency goods and brings the total to 122. Run E&F and PSC together without it and the game will not start.

[h2]What this patch does[/h2]
[list]
[*][b]Unifies the "private construction" building[/b]
[list]
[*]Disables E&F's separate [i]building_ef_private_construction[/i] (not buildable).
[*]Uses PSC's [i]building_construction_sector[/i] as the single construction sector for both mods.
[*]Injects E&F [i]pmg_market_liquidity[/i] into [i]building_construction_sector[/i], so the currency drain sees construction.
[*]Repoints E&F's history, its companies and its bank-founding effect at the unified sector, so starting sectors and company ownership still land where they should.
[*]Adds an investment score entry for [i]bg_construction[/i] so E&F's financial district logic has a target.
[*]Caps total sectors with E&F's Urban Center formula, and gives the AI a nudge to build sectors when construction goods are overpriced.
[/list]

[*][b]Overbuilt Economy is switched off, on purpose[/b]
[list]
[*]E&F's "Overbuilt Economy" counts private sectors against an Urban Center cap and debuffs them. Under PSC that would be a second punishment for something you already pay for in goods and money.
[*]Its only release valve in E&F demolishes a whole construction building at a time. In PSC a state holds exactly one construction sector whose level [i]is[/i] that state's entire capacity, so the AI would flatten 20–50 levels a month.
[*]So the counter is held at zero instead. The stimulus buttons stay usable and the journal bar reads what is actually happening.
[/list]

[*][b]One PSC bug fixed along the way[/b]
[list]
[*]PSC's per-state construction price lookup reads the regulator's production method in every state, including states that have no regulator yet. That produces [i]has_active_production_method [ Wrong scope for trigger: none, expected building ][/i] at every startup. Guarded here.
[/list]
[/list]

[i]E&F's own bugs — the divisions by zero in its stock demand values and the missing-scope crash in the private bank currency sale — used to live in this compatch. They have nothing to do with PSC, so they moved to the E&F Hotfix, which is a dependency anyway.[/i]

[h2]Localization[/h2]
[list]
[*]English
[*]Russian
[*]Other — English placeholder
[/list]

[h2]Notes / Compatibility[/h2]
[list]
[*]This patch only overrides what PSC + E&F integration needs. Where it has to copy bulk content from E&F, that copy is regenerated by a script rather than maintained by hand.
[*]It will conflict with other mods that heavily overwrite the same areas (especially [i]common/buildings[/i], [i]common/scripted_buttons[/i], [i]common/script_values[/i]).
[*][b]Known gap:[/b] E&F and PSC both redefine the vanilla [i]construction_panel[/i] and the state building list, in different files. One of them loses. This compatch does not merge them yet.
[/list]
[url=https://github.com/BEDTRIP/vic3_mods]my github[/url]

---

## Подробности

_Пока только описание для мастерской: подробного разбора для этого компача не писали._
