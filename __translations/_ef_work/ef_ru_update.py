# -*- coding: utf-8 -*-
"""
Sync the Russian translation mod with the current E&F localization.

Why a script and not hand editing: E&F generates most of its loc keys per-good
(29 stockpile goods x ~20 GUI families). 1267 keys were missing, but only 178
were unique strings -- the rest are the same sentence with a different good.
Hand-copying those is how inconsistent terminology and typos get in.

Three ways a key gets its Russian value:
  TPL   - a Russian template filled with the good's name in the right case.
          The templates were derived from the already-translated sibling key
          (e.g. store_grain_1 -> "Складирование зерна") so the new goods read
          exactly like the old ones.
  COPY  - the English value is pure markup / script refs ([GetPlayer...],
          @icon!, $ref$) with no words. Copied verbatim: "translating" it can
          only break it.
  LIT   - genuine prose, translated by hand.

Obsolete keys (present in RU, gone from E&F) are dropped.
"""
import os, re, sys, io, json, datetime

ROOT_OUT = os.path.expanduser("~/mnt/Projects/vic3_mods_out/E&F/localization/english")
ROOT_RU  = os.path.expanduser("~/mnt/Projects/vic3_mods/__translations/Economic and Financial Mod (E&F) - V4 RUS/localization/russian")

# --------------------------------------------------------------------------
# Goods: id -> (nominative capitalised, nominative lowercase, genitive)
# Nominative forms are taken verbatim from vanilla goods_l_russian.yml so the
# GUI reads the same as the rest of the game. Genitive is needed because most
# E&F strings are "Выпуск <good>" / "1M <good>" constructions.
# --------------------------------------------------------------------------
G = {
 'ammunition'         : ('Боеприпасы',           'боеприпасы',            'боеприпасов'),
 'small_arms'         : ('Стрелковое оружие',    'стрелковое оружие',     'стрелкового оружия'),
 'artillery'          : ('Артиллерия',           'артиллерия',            'артиллерии'),
 'tanks'              : ('Танки',                'танки',                 'танков'),
 'aeroplanes'         : ('Аэропланы',            'аэропланы',             'аэропланов'),
 'grain'              : ('Зерно',                'зерно',                 'зерна'),
 'fabric'             : ('Ткань',                'ткань',                 'ткани'),
 'wood'               : ('Древесина',            'древесина',             'древесины'),
 'groceries'          : ('Продукты',             'продукты',              'продуктов'),
 'clothes'            : ('Одежда',               'одежда',                'одежды'),
 'paper'              : ('Бумага',               'бумага',                'бумаги'),
 'silk'               : ('Шёлк',                 'шёлк',                  'шёлка'),
 'dye'                : ('Красители',            'красители',             'красителей'),
 'sulfur'             : ('Сера',                 'сера',                  'серы'),
 'coal'               : ('Уголь',                'уголь',                 'угля'),
 'iron'               : ('Железо',               'железо',                'железа'),
 'lead'               : ('Свинец',               'свинец',                'свинца'),
 'hardwood'           : ('Твёрдая древесина',    'твёрдая древесина',     'твёрдой древесины'),
 'rubber'             : ('Каучук',               'каучук',                'каучука'),
 'oil'                : ('ГСМ',                  'ГСМ',                   'ГСМ'),
 'engines'            : ('Двигатели',            'двигатели',             'двигателей'),
 'steel'              : ('Сталь',                'сталь',                 'стали'),
 'fertilizer'         : ('Удобрение',            'удобрение',             'удобрений'),
 'tools'              : ('Инструменты',          'инструменты',           'инструментов'),
 'explosives'         : ('Взрывчатка',           'взрывчатка',            'взрывчатки'),
 'automobiles'        : ('Автомобили',           'автомобили',            'автомобилей'),
 'telephones'         : ('Телефоны',             'телефоны',              'телефонов'),
 'radios'             : ('Радио',                'радио',                 'радио'),
 'opium'              : ('Опиум',                'опиум',                 'опиума'),
 'gold'               : ('Золото',               'золото',                'золота'),
 'silver'             : ('Серебро',              'серебро',               'серебра'),
 'bond'               : ('Облигация',            'облигация',             'облигаций'),
 'manufacture_stock'  : ('Промышленные акции',   'промышленные акции',    'промышленных акций'),
 'mining_stock'       : ('Горнодобывающие акции','горнодобывающие акции', 'горнодобывающих акций'),
 'agricultural_stock' : ('Сельскохозяйственные акции','сельскохозяйственные акции','сельскохозяйственных акций'),
 'railroad_stock'     : ('Железнодорожные акции','железнодорожные акции', 'железнодорожных акций'),
}
# Longest first so 'small_arms' is not matched as 'arms', 'manufacture_stock'
# not as 'stock', etc.
GOOD_IDS = sorted(G.keys(), key=len, reverse=True)

# --------------------------------------------------------------------------
# Templated families. {ID} good id, {NOM}/{NOML} nominative, {GEN} genitive.
# --------------------------------------------------------------------------
TPL = {
 '00_ef_gui_localization': {
  # Stockpile alerts. E&F worded these around a "buy/sell order"; the existing
  # RU translation already calls it "приказ на хранение / на выпуск"
  # (budget_panel_desc_goods), so keep that wording instead of inventing "заявка".
  'alert_buy_sell_{G}_order_name'   : 'Выполняется приказ на покупку/продажу: @{ID}! {NOM}',
  'alert_buy_sell_{G}_order_hint'   : 'Приказ будет исполнен менее чем через 1 месяц.',
  'alert_buy_sell_{G}_order_action' : 'Глобальная панель',
  'alert_store_release_{G}_name'    : 'Хранение/выпуск {GEN} @{ID}! подходит к концу',
  'alert_store_release_{G}_hint'    : 'До конца срока исполнения приказа на хранение/выпуск {GEN} осталось 3 месяца.',
  'alert_store_release_{G}_action'  : 'Панель резерва',

  'alert_selle_{G}_maturity_yers_time_5_Y_name'  : 'Одно из ваших пятилетних вложений в суверенный долг другой страны вышло на последний год до погашения.',
  'alert_selle_{G}_maturity_yers_time_5_Y_hint'  : 'Иностранные долговые обязательства в вашем владении подходят к погашению.',
  'alert_selle_{G}_maturity_yers_time_5_Y_action': 'Глобальная панель',
  'alert_selle_{G}_maturity_yers_time_10_Y_name'  : 'Одно из ваших десятилетних вложений в суверенный долг другой страны вышло на последний год до погашения.',
  'alert_selle_{G}_maturity_yers_time_10_Y_hint'  : 'Иностранные долговые обязательства в вашем владении подходят к погашению.',
  'alert_selle_{G}_maturity_yers_time_10_Y_action': 'Глобальная панель',

  # Market panel. Existing RU siblings: grain_global_price = "Мировая цена на зерно".
  '{G}_global_price'   : 'Мировая цена на {NOML}',
  '{G}_global_offer'   : 'Мировое предложение {GEN}',
  '{G}_global_demande' : 'Мировой спрос на {NOML}',
  '{G}_name'           : '@{ID}! {NOM}',
  '{G}_price'          : 'Цена {GEN}',
  'predicted_{G}_store'   : 'Идет @{ID}! в запас в год',
  'predicted_{G}_release' : 'Идет @{ID}! на выпуск в год',

  # Only gold has these; "Metal Reserves" is the central bank metal vault.
  '{G}_reserve_window'      : 'Резервы металлов',
  'show_{G}_reserve_window' : 'Показать резервы металлов',

  # Stockpile buttons.
  'store_{G}_infinit'            : 'Задать бессрочный приказ на хранение',
  'store_{G}'                    : 'Задать приказ на хранение',
  'release_{G}'                  : 'Задать приказ на выпуск',
  '{G}_sell'                     : 'Переключить хранение / выпуск',
  'set_{G}_0'                    : 'Сбросить только приказ на покупку',
  'increase_{G}_quantity_store'  : 'Увеличить объём хранения',
  'reduce_{G}_quantity_store'    : 'Уменьшить объём хранения',
  'increase_{G}_quantity_release': 'Увеличить объём выпуска',
  'reduce_{G}_quantity_release'  : 'Уменьшить объём выпуска',
  'increase_{G}_month_store'     : 'Увеличить срок хранения',
  'reduce_{G}_month_store'       : 'Уменьшить срок хранения',
  'increase_{G}_month_release'   : 'Увеличить срок выпуска',
  'reduce_{G}_month_release'     : 'Уменьшить срок выпуска',
 },
 '01_ef_modifier_type_localization': {
  # E&F's own English is scrambled here (goods_output_*_add reads "Goods input
  # ... multiply"). The RU siblings were translated from the actual game effect,
  # not from that text -- keep following the siblings.
  'goods_output_{G}_add'      : 'Выпуск {GEN}',
  'goods_output_{G}_add_desc' : 'Множитель выпуска {GEN}',
  'goods_input_{G}_add'       : 'Потребление {GEN}',
  'goods_input_{G}_add_desc'  : 'Множитель потребления {GEN}',
  'goods_input_{G}_mult'      : 'Складирование {GEN}',
  'goods_input_{G}_mult_desc' : 'Складирование {GEN}',
  'goods_output_{G}_mult'     : 'Выпуск {GEN}',
  'goods_output_{G}_mult_desc': 'Выпуск {GEN}',
  'state_buy_orders_{G}_add'        : "[GetGoods('{ID}').GetTextIcon][Nbsp][GetGoods('{ID}').GetNameNoFormatting] Ордера на покупку",
  'state_buy_orders_{G}_add_desc'   : "Увеличение или уменьшение [concept_buy_orders] для [GetGoods('{ID}').GetName] в [concept_state]",
  'state_sell_orders_{G}_add'       : "[GetGoods('{ID}').GetTextIcon][Nbsp][GetGoods('{ID}').GetNameNoFormatting] Ордера на продажу",
  'state_sell_orders_{G}_add_desc'  : "Увеличение или уменьшение [concept_sell_orders] для [GetGoods('{ID}').GetName] в [concept_state]",
 },
 '01_ef_static_modifier_localization': {
  'release_{G}_1' : 'Выпуск {GEN}',
  'store_{G}_1'   : 'Складирование {GEN}',
  'storing_{G}'   : 'Запасание {GEN}',
  'releasing_{G}' : 'Выпуск {GEN}',
 },
 '01_ef_production_method_localization': {
  # "Nothing" PMs -- the RU siblings all say "Пусто".
  'pm_{G}_0'         : 'Пусто',
  'pm_store_{G}_1'   : 'Пусто',
  'pm_release_{G}_1' : 'Пусто',
  'pm_private_ownership_majority_{G}' : '{NOM}',
  'pm_no_private_ownership_{G}'       : 'Без {GEN}',
 },
 '01_ef_tooltips_localization': {
  'buy_{G}_custom_tooltip'  : "#T Купить @{ID}#!\\nУ вас больше чем [Market.GetOwner.MakeScope.ScriptValue('buy_{ID}_market_panel')|D] [Market.GetOwner.GetCustom('currency_good')]\\nУ вас меньше 1M {GEN} @{ID}!\\nУ выбранной страны больше чем [GetPlayer.MakeScope.Var('{ID}_market_panel_quantity').GetValue|D] {GEN} @{ID}!\\nВ этом году не заключено ни одного контракта на этот товар (Осталось контрактов: [GetPlayer.MakeScope.ScriptValue('{ID}_contract_1_year_order')|0])\\nУ вас есть [GetBuildingType('building_financial_centre').GetName]\\nУ выбранной страны есть [GetBuildingType('building_financial_centre').GetName]\\nУ вас есть Договор о поставке материалов с этой страной",
  'sell_{G}_custom_tooltip' : "#T Продать @{ID}#!\\nУ выбранной страны больше чем [Market.GetOwner.MakeScope.ScriptValue('sell_{ID}_market_panel')|D] [Market.GetOwner.GetCustom('currency_good')]\\nУ выбранной страны меньше 1M {GEN} @{ID}!\\nУ вас больше чем [GetPlayer.MakeScope.Var('{ID}_market_panel_quantity').GetValue|D] {GEN} @{ID}!\\nВ этом году не заключено ни одного контракта на этот товар (Осталось контрактов: [GetPlayer.MakeScope.ScriptValue('{ID}_contract_1_year_order')|0])\\nУ вас есть [GetBuildingType('building_financial_centre').GetName]\\nУ выбранной страны есть [GetBuildingType('building_financial_centre').GetName]\\nУ вас есть Договор о поставке материалов с этой страной",
 },
}

# --------------------------------------------------------------------------
# Patterns whose English value carries no words -- only icons, script values
# and $refs$. Copied byte for byte.
# --------------------------------------------------------------------------
COPY = {
 '00_ef_gui_localization': {
   'law_large_monetary_policy_texture',
   '{G}_flag_icon',
   '{G}_flag_var_state', '{G}_flag_green_arow_bellow',
   '{G}_flag_red_arow_bellow', '{G}_flag_status',
   '{G}_flag_var_state_state_panel', '{G}_flag_green_arow_bellow_state_panel',
   '{G}_flag_red_arow_bellow_state_panel', '{G}_flag_status_state_panel',
 },
 '01_ef_event_localization': set(),   # filled below: every *_message_tooltip
 '01_ef_je_localization': {
   'je_ef_efcc_situation_reason',
   'country_bankruptcy_var',
 },
}

# --------------------------------------------------------------------------
# Hand-translated prose, keyed exactly.
# --------------------------------------------------------------------------
LIT = {}

LIT['00_ef_gui_localization'] = {
 'central_bank_metal_purchases' : 'Закупки металла центральным банком',
 # Vault readout: "N stack of 100M" -> "N партий по 100M". The 100M/500M step
 # differs between gold and silver, so these are spelled out rather than templated.
 'EF_gold_gui_stack'   : "#v [GetPlayer.MakeScope.ScriptValue('EF_gold_gui_stack')] #!партий по #v 100M #!@gold!",
 'EF_silver_gui_stack' : "#v [GetPlayer.MakeScope.ScriptValue('EF_silver_gui_stack')] #!партий по #v 500M #!@silver!",
 'EF_gold_gui_room'    : "Золото хранится в #v [GetPlayer.MakeScope.ScriptValue('EF_gold_gui_room')] #! хранилищах",
 'EF_silver_gui_room'  : "Серебро хранится в #v [GetPlayer.MakeScope.ScriptValue('EF_silver_gui_room')] #! хранилищах",
 # The English here is left over in French ("Action displonible dans le ...").
 'alert_fso_alert_name'   : 'Доступно действие в Управлении финансовой стабильности (FSO)',
 'alert_fso_alert_hint'   : "В Управлении финансовой стабильности (FSO) можно выбрать меру, которая повлияет на [GetBuildingType('building_financial_centre').GetName] или на [GetBuildingType('building_ef_private_construction').GetName].",
 'alert_fso_alert_action' : 'Журнал',
 'currency_reserve_window'      : 'Валютные резервы',
 'show_currency_reserve_window' : 'Показать валютные резервы',
 'stockpile_panel_overview_section' : 'Товары в резерве',
}

_ev = '01_ef_event_localization'
LIT[_ev] = {
 '00_ef_economic_event.12.f' :
   "Правительство [SCOPE.sC('target_country').GetName] официально подписало #v договор о Латинском монетном союзе#!, приняв на двадцать лет обязательство следовать единым денежным стандартам, установленным конвенцией.\\n \\n Ратифицировав соглашение, [SCOPE.sC('target_country').GetName] признаёт установленное Францией соотношение золота и серебра, приводит стоимость своей валюты к эталону Союза и соглашается на постепенную унификацию своей монеты с монетой прочих государств-участников.\\n \\n Это обязательство знаменует заметное продвижение к более глубокой финансовой интеграции и свободному обращению стандартных золотых и серебряных монет среди членов Союза.",

 'notification_00_ef_economic_event_30_message_name' :
   "[SCOPE.sC('target_country').GetName] отказывается от размена на металл",
 'notification_00_ef_economic_event_30_message_desc' :
   "Столкнувшись с тяжёлой денежной нестабильностью, [SCOPE.sC('target_country').GetName] ввела чрезвычайные меры, которые приостанавливают любой размен валюты на металл и переводят национальную валюту на #b фиатный стандарт#!.",

 'notification_00_ef_economic_event_26_message_name' :
   "Введение биметаллического стандарта в [SCOPE.sC('target_country').GetName]",
 'notification_00_ef_economic_event_26_message_desc' :
   "Стремясь укрепить денежную стабильность, [SCOPE.sC('target_country').GetName] приняла ряд финансовых мер, вводящих #b биметаллический стандарт#! и дающих полный размен национальной валюты как на #b золото#!, так и на #b серебро#!.",

 'notification_00_ef_economic_event_27_message_name' :
   "Введение золотого стандарта в [SCOPE.sC('target_country').GetName]",
 'notification_00_ef_economic_event_27_message_desc' :
   "Стремясь укрепить денежную стабильность и полнее встроиться в международные финансовые рынки, [SCOPE.sC('target_country').GetName] приняла новое финансовое законодательство, вводящее #b золотой стандарт#!.",

 'notification_00_ef_economic_event_31_message_name' :
   "Девальвация стандарта [SCOPE.sC('target_country').GetCustom('currency_name')] [SCOPE.sC('target_country').GetCustom('currency_symbol')]",
 'notification_00_ef_economic_event_31_message_desc' :
   "Парламент [SCOPE.sC('target_country').GetName] провёл реформу, #b девальвирующую металлический стандарт страны#! — то есть понижающую законодательно установленное металлическое содержание, обеспечивающее национальную валюту.\\n\\nОфициальный паритет [SCOPE.sC('target_country').GetCustom('currency_name')] [SCOPE.sC('target_country').GetCustom('currency_symbol')] меняется с #b 1 [SCOPE.sC('target_country').GetCustom('currency_symbol')] = [SCOPE.sC('target_country').MakeScope.Var('money_value_target_1_old').GetValue] [SCOPE.sC('target_country').GetCustom('monetary_system')]#! на #b девальвированный#! уровень #b 1 [SCOPE.sC('target_country').GetCustom('currency_symbol')] = [SCOPE.sC('target_country').MakeScope.Var('money_value_target_1').GetValue] [SCOPE.sC('target_country').GetCustom('monetary_system')]#!.",

 'notification_00_ef_economic_event_32_message_name' :
   "Ревальвация стандарта [SCOPE.sC('target_country').GetCustom('currency_name')] [SCOPE.sC('target_country').GetCustom('currency_symbol')]",
 'notification_00_ef_economic_event_32_message_desc' :
   "Парламент [SCOPE.sC('target_country').GetName] провёл реформу, #b ревальвирующую металлический стандарт страны#! — то есть повышающую законодательно установленное металлическое содержание, обеспечивающее национальную валюту.\\n\\n Официальный паритет [SCOPE.sC('target_country').GetCustom('currency_name')] [SCOPE.sC('target_country').GetCustom('currency_symbol')] растёт с #b 1 [SCOPE.sC('target_country').GetCustom('currency_symbol')] = [SCOPE.sC('target_country').MakeScope.Var('money_value_target_1_old').GetValue] [SCOPE.sC('target_country').GetCustom('monetary_system')]#! до #b ревальвированного#! уровня #b 1 [SCOPE.sC('target_country').GetCustom('currency_symbol')] = [SCOPE.sC('target_country').MakeScope.Var('money_value_target_1').GetValue] [SCOPE.sC('target_country').GetCustom('monetary_system')]#!.",

 'notification_00_ef_economic_event_95_message_name' :
   "Частные банки атакуют золотые резервы",
 'notification_00_ef_economic_event_95_message_desc' :
   "Идёт согласованная арбитражная операция.\\n\\nПеречисленные частные банки начали пользоваться установленным законом биметаллическим соотношением: они бьют по стоимости [SCOPE.sC('target_country').GetCustom('currency_name')] [SCOPE.sC('target_country').GetCustom('currency_symbol')], выкачивая #v золотые резервы#! @gold! страны через крупномасштабный арбитраж.\\n\\n Приток #p [SCOPE.sC('target_country').MakeScope.Var('silver_state_1_fix').GetValue|D]#! @silver! и отток #n -[SCOPE.sC('target_country').MakeScope.Var('gold_state_1_fix').GetValue|D]#! @gold!.\\n\\nЕсли это продолжится, расхождение между законным соотношением и мировой ценой золота вызовет тяжёлую денежную нестабильность.",

 'notification_00_ef_economic_event_96_message_name' :
   "Частные банки атакуют серебряные резервы",
 'notification_00_ef_economic_event_96_message_desc' :
   "Идёт согласованная арбитражная операция.\\n\\nПеречисленные частные банки начали пользоваться установленным законом биметаллическим соотношением: они бьют по стоимости [SCOPE.sC('target_country').GetCustom('currency_name')] [SCOPE.sC('target_country').GetCustom('currency_symbol')], выкачивая #v серебряные резервы#! @Silver! страны через крупномасштабный арбитраж.\\n\\n Приток #p [SCOPE.sC('target_country').MakeScope.ScriptValue('gold_gained')|D=]#! @gold! и отток #n -[SCOPE.sC('target_country').MakeScope.ScriptValue('silver_lost')|D]#! @silver!.\\n\\n Если это продолжится, расхождение между законным соотношением и мировой ценой серебра вызовет тяжёлую денежную нестабильность.",

 'notification_00_ef_economic_event_97_message_name' :
   "Арбитраж на [SCOPE.sC('seller').GetCustom('currency_name')]",
 'notification_00_ef_economic_event_97_message_desc' :
   "Рост курса повысил привлекательность валюты, и частные банки стали докупать её, чтобы воспользоваться новым паритетом. Это подстёгивает приток металла в страну-эмитент.\\n\\nВ рамках этого банк приобрёл в общей сложности #v [SCOPE.sC('buyer_country').MakeScope.Var('arbitrage_value_in_currency').GetValue|D] [SCOPE.sC('seller').GetCustom('currency_symbol')]#! — что соответствует #v [SCOPE.sC('buyer_country').MakeScope.Var('arbitrage_value_in_metal').GetValue|D]#! [SCOPE.sC('seller').GetCustom('monetary_system_partiel')] — сообразно рыночным условиям и действующему паритету.\\n\\nОперация отражает инвестиционную стратегию банка и возросшее доверие к валюте.",

 'notification_00_ef_economic_event_971_message_name' :
   "Накопление [SCOPE.sC('seller').GetCustom('currency_name')] [SCOPE.sC('seller').GetCustom('currency_symbol')]",
 'notification_00_ef_economic_event_971_message_desc' :
   "Благодаря устойчивости и центральной роли в международных расчётах эта валюта исторически занимает привилегированное место в структуре банковских резервов. Финансовые учреждения естественным образом стремятся держать её значительную долю — и чтобы обезопасить активы, и чтобы облегчить внешние операции.\\n\\nВ рамках этого банк приобрёл в общей сложности #v [SCOPE.sC('buyer_country').MakeScope.Var('arbitrage_value_in_currency').GetValue|D] [SCOPE.sC('seller').GetCustom('currency_symbol')]#! — что соответствует #v [SCOPE.sC('buyer_country').MakeScope.Var('arbitrage_value_in_metal').GetValue|D]#! [SCOPE.sC('seller').GetCustom('monetary_system_partiel')] — сообразно принятой финансовой практике.\\n\\nЭто движение показывает денежный престиж страны-эмитента и структурообразующую роль её валюты в равновесии мировой системы.",

 'notification_00_ef_economic_event_98_message_name' :
   "Продажа [SCOPE.sC('buyer').GetCustom('currency_name')] [SCOPE.sC('seller').GetCustom('currency_symbol')]",
 'notification_00_ef_economic_event_98_message_desc' :
   "Он продал в общей сложности #v [SCOPE.sC('buyer').MakeScope.Var('sell_arbitrage_value_10_in_currency').GetValue|D] [SCOPE.sC('buyer').GetCustom('currency_symbol')]#! — что соответствует #v [SCOPE.sC('buyer').MakeScope.Var('sell_arbitrage_value_in_metal').GetValue|D]#! [SCOPE.sC('buyer').GetCustom('monetary_system_partiel')] — сообразно рыночным условиям.\\n\\nОперация отражает арбитражную стратегию банка после смягчения денежной политики, которое снижает относительную привлекательность валюты на рынках.",

 'notification_00_ef_economic_event_981_message_name' :
   "Продажа [SCOPE.sC('buyer').GetCustom('currency_name')] [SCOPE.sC('seller').GetCustom('currency_symbol')]",
 'notification_00_ef_economic_event_981_message_desc' :
   "Официальная ревальвация стандарта повысила законную стоимость валюты. Частные банки играют на этом, продавая валюту ради металла, ставшего относительно более выгодным.\\n\\nВ рамках этого банк продал в общей сложности #v [SCOPE.sC('buyer').MakeScope.Var('sell_arbitrage_value_10_in_currency').GetValue|D] [SCOPE.sC('buyer').GetCustom('currency_symbol')]#! — что соответствует #v [SCOPE.sC('buyer').MakeScope.Var('sell_arbitrage_value_in_metal').GetValue|D]#! [SCOPE.sC('buyer').GetCustom('monetary_system_partiel')] — сообразно рыночным условиям.\\n\\nЭто примерно #v 10%#! резервов банка, задействованных ради выгоды от разрыва, созданного новым официальным паритетом.",

 'notification_00_ef_economic_event_982_message_name' :
   "Давление на [SCOPE.sC('buyer').GetCustom('currency_name')] [SCOPE.sC('seller').GetCustom('currency_symbol')]",
 'notification_00_ef_economic_event_982_message_desc' :
   "Завися от #v серебра#! @silver!, стоимость валюты напрямую зависит от международных колебаний цены металла. Когда серебро дешевеет, частные банки склонны избавляться от этой валюты, считая её более уязвимой, чем валюты на более устойчивых стандартах.\\n\\nВ этих условиях банк продал в общей сложности #v [SCOPE.sC('buyer').MakeScope.Var('sell_arbitrage_value_10_in_currency').GetValue|D] [SCOPE.sC('buyer').GetCustom('currency_symbol')]#! — что соответствует #v [SCOPE.sC('buyer').MakeScope.Var('sell_arbitrage_value_in_metal').GetValue|D]#! [SCOPE.sC('buyer').GetCustom('monetary_system_partiel')] — сообразно рыночным условиям.\\n\\nДавление финансовых учреждений показывает уязвимость валюты, привязанной к металлу с сильной международной волатильностью.",

 'notification_00_ef_economic_event_1_message_name' :
   "Новый центральный банк и национальная валюта в [SCOPE.sC('target_country').GetName]",
 'notification_00_ef_economic_event_1_message_desc' :
   "Правительство [SCOPE.sC('target_country').GetName] официально объявило об учреждении современного центрального банка и о введении новой национальной валюты: [SCOPE.sC('target_country').GetCustom('currency_name')]#! [SCOPE.sC('target_country').GetCustom('currency_symbol')].",

 '00_ef_economic_event.106.t' : "Денежный дисбаланс",
 '00_ef_economic_event.106.d' : "Политическое давление нарастает",
 '00_ef_economic_event.106.f' :
   "Доля металлического покрытия центрального банка опустилась ниже 75% или поднялась выше 125%, опасно отойдя от целевого уровня. Доверие к нынешнему денежному устройству слабеет, и [concept_interest_group] по всей стране всё настойчивее требуют широких денежных реформ. [SCOPE.gsInterestGroup('ig_want_a_large_monetary_policy').GetName] может принять идеологию [GetIdeology('ideology_monetary_policy').GetName], усилив поддержку принятия закона [GetLawType('law_large_monetary_policy').GetName].",
 '00_ef_economic_event.106.a' : "Спор разгорается.",
 '00_ef_economic_event.107.t' : "Денежная стабильность",
 '00_ef_economic_event.107.d' : "Доверие восстановлено",
 '00_ef_economic_event.107.f' :
   "Доля металлического покрытия центрального банка вернулась к приемлемым значениям, восстановив доверие к денежному устройству страны. Валюта вновь держится в намеченных границах, и поддержка чрезвычайных денежных мер сходит на нет. [SCOPE.gsInterestGroup('ig_want_a_large_monetary_policy').GetName] может отказаться от идеологии [GetIdeology('ideology_monetary_policy').GetName], снизив поддержку принятия закона [GetLawType('law_large_monetary_policy').GetName].",
 '00_ef_economic_event.107.a' : "Стабильность возвращается.",
}

LIT['01_ef_ideologie_localization'] = {
 'ideology_monetary_policy' : 'Денежный интервенционизм',
 'ideology_monetary_policy_desc' :
   'Эта группа считает, что денежную политику следует активно использовать для управления экономикой. Расширение или сжатие денежной массы, интервенции на рынке, управление курсом — государство должно обладать широкими полномочиями ради своих экономических целей.',
}

LIT['01_ef_law_localization'] = {
 'law_large_monetary_policy' : 'Широкая денежная политика',
 'law_large_monetary_policy_desc' :
   'Центральный банк получает широкие полномочия вмешиваться в денежные дела, вплоть до масштабного расширения или сжатия денежной массы. Это позволяет правительству решительно отвечать на экономические кризисы, подстёгивать рост, покрывать чрезвычайные расходы и при необходимости удерживать национальную валюту. Группы интересов охотнее принимают этот закон, если доля металлического покрытия центрального банка падает ниже 75% или поднимается выше 125%.',
 'private_liquidity_provision' : 'Частное предоставление ликвидности',
 'private_liquidity_provision_desc' :
   'Частные банки сами снабжают финансовую систему краткосрочной ликвидностью, сглаживая рыночное напряжение и поддерживая кредитование без прямого вмешательства центрального банка.',
 'advanced_interbank_refinancing' : 'Развитое межбанковское рефинансирование',
 'advanced_interbank_refinancing_desc' :
   'Развитая система межбанковского рефинансирования даёт банкам доступ к ликвидности через организованные межбанковские рынки, повышая финансовую устойчивость, обращение капитала и сопротивляемость кризисам.',
}

LIT['01_ef_static_modifier_localization'] = {
 'UNI_modifier_1' : 'Престижный товар действительно необходим',
}

# ---- journal entries ------------------------------------------------------
_je = '01_ef_je_localization'
_PC  = "[GetBuildingType('building_ef_private_construction').GetName]"
_FC  = "[GetBuildingType('building_financial_centre').GetName]"
_SM  = lambda n: "[GetStaticModifier('%s').GetName|v]" % n

def _ban_block(pl="[GetPlayer.GetName]"):
    return ("\\n\\nЭффект:\\n"
            "- %s полностью запрещает [GetGoods('bond').GetName]\\n"
            "- %s полностью запрещает [GetGoods('manufacture_stock').GetName]\\n"
            "- %s полностью запрещает [GetGoods('agricultural_stock').GetName]\\n"
            "- %s полностью запрещает [GetGoods('mining_stock').GetName]\\n"
            "- %s полностью запрещает [GetGoods('railroad_stock').GetName] \\n"
            "- %s получает модификатор %s на 12 месяцев"
            % (pl,pl,pl,pl,pl,pl,_SM('speculative_share_modifier_1')))

def _tt_new(n, extra=''):
    pl = "[GetPlayer.GetName]"
    s = ("$speculative_share_%d_button$ \\n$speculative_share_%d_button_desc$\\n\\nВозможно: \\n"
         "- $speculative_share_%d_button_tt$\\n"
         "- У %s нет модификатора %s\\n"
         "- У %s нет модификатора %s\\n"
         "- У %s нет модификатора %s   " % (
          n,n,n, pl,_SM('speculative_share_modifier_2'),
                 pl,_SM('speculative_share_modifier_3'),
                 pl,_SM('speculative_share_modifier_4')))
    return s + _ban_block() + extra

def _fc_tt(n):
    return ("$speculative_share_%d_button$\\n\\n$speculative_share_%d_button_desc$\\n\\nВозможно:\\n"
            "- Нет модификатора %s\\n- Есть модификатор %s\\n"
            "- $speculative_share_%d_button_tt_1$\\n- $speculative_share_%d_button_tt_2$\\n"
            "- $speculative_share_%d_button_tt_3$\\n- $speculative_share_%d_button_tt_4$\\n\\n"
            "Эффект:\\n $speculative_share_%d_button_tt_effect_1$"
            % (n,n,_SM('speculative_share_modifier_5'),_SM('has_financial_center'),n,n,n,n,n))

def _fc_effect(lvl):
    return ("- Начать строительство %d уровней %s в случайном штате силами частного строительства\\n"
            "- Блокирует расширение %s на 12 месяцев\\n"
            "- Даёт модификатор %s на 12 месяцев" % (lvl,_FC,_FC,_SM('down_base_rate')))

def _pc_tt(n):
    return ("$speculative_share_%d_button$\\n\\n$speculative_share_%d_button_desc$\\n\\nВозможно:\\n"
            "- Нет модификатора %s\\n- Есть модификатор %s\\n"
            "- $speculative_share_%d_button_tt_1$\\n- $speculative_share_%d_button_tt_2$\\n"
            "- $speculative_share_%d_button_tt_3$\\n\\n Эффект:\\n$speculative_share_%d_button_tt_effect_1_1$"
            % (n,n,_SM('speculative_share_modifier_5'),_SM('has_financial_center'),n,n,n,n))

def _pc_effect(n, lvl, second):
    pl = "[GetPlayer.GetName]"
    mid = ("- $speculative_share_%d_button_tt_effect_1$\\n" % n)
    if second:
        mid += ("- $speculative_share_%d_button_tt_effect_2$\\n" % n)
    return ("- Построить %d %s в случайном штате\\n"
            "- Блокирует расширение %s на 12 месяцев\\n"
            "%s"
            "- %s получает %s на 12 месяцев\\n"
            "- %s получает %s на 12 месяцев\\n"
            "- %s получает %s на 12 месяцев"
            % (lvl,_PC,_PC, mid,
               pl,_SM('down_base_rate'),
               pl,_SM('speculative_share_modifier_5'),
               pl,_SM('speculative_share_modifier_6')))

LIT[_je] = {
 'financial_center_je_2_reason_1' :
   "Спекулятивный рынок#! сейчас составляет #b [GetPlayer.MakeScope.ScriptValue('fiancial_center_week_balance_in_ratio')|%|]#! национального #b [concept_gdp]#!.",
 'financial_center_je_2_reason_1_2' :
   "#U - 0–10% → спекулятивное напряжение сильно снижено (−3)\\n - 10–20% → напряжение спадает (−2)\\n - 20–30% → небольшой спад (−1)\\n - 30–40% → небольшой рост (+1)\\n - 40–50% → заметный рост (+2)\\n - 50%+ → сильный рост пузыря (+3)#!",
 # The English string is untranslated French in E&F itself.
 'financial_center_je_2_reason_1_3' :
   "Чем выше уровень ваших финансовых центров, тем больше частный сектор реинвестирует инвестиционный пул, тем больше создаётся финансовых продуктов — и тем выше потенциал спекулятивного пузыря.",
 'financial_center_je_2_reason_2' :
   "#b Текущее значение:#!\\n - Число %s в стране: #p [GetPlayer.MakeScope.ScriptValue('building_ef_private_construction_lvl')]#!\\n - Суммарный уровень [GetBuildingType('building_urban_center').GetName]: #p [GetPlayer.MakeScope.ScriptValue('building_urban_center_lvl')]#!\\n - Текущая [concept_base_rate_percentage]: #p [GetPlayer.MakeScope.ScriptValue('base_rate_percentage_decimal')]%%#!\\n - Теоретический максимум уровня частного строительства: #p [GetPlayer.MakeScope.ScriptValue('building_urban_center_lvl_by_base_rate')]#! #b (то есть [GetPlayer.MakeScope.ScriptValue('base_rate_to_pcs_factor')|%%] от [GetPlayer.MakeScope.ScriptValue('building_urban_center_lvl')])#!" % _PC,

 'speculative_share_13_button' : "#b Отрегулировать частный строительный сектор #!",
 'speculative_share_13_button_desc' :
   "Частное строительство разрослось сверх устойчивого уровня. Вмешательство государства призвано вернуть равновесие и не дать перекосу усилиться.",
 'speculative_share_13_button_tt_1' :
   "- Теоретический максимум уровня %s (сейчас: #p [GetPlayer.MakeScope.ScriptValue('building_urban_center_lvl_by_base_rate')]#!) превышает нынешнее число %s в стране (сейчас: #p [GetPlayer.MakeScope.ScriptValue('building_ef_private_construction_lvl')]#!).\\n- Нет модификатора %s" % (_PC,_PC,_SM('speculative_share_modifier_7')),

 'status_central_bank_3' :
   " Пока Япония остаётся под властью сёгуната, современные финансовые учреждения создать невозможно.\\n Завершение Реставрации империи покончит с этой замкнутостью и откроет создание национального центрального банка.",
 'speculative_share_modifier_7' : "Недавнее регулирование %s" % _PC,
 'fc_fso_situation'  : "Устойчивость финансового сектора",
 'pcs_fso_situation' : "Устойчивость строительного сектора",

 'speculative_share_1_button_tt_new' : _tt_new(1),
 'speculative_share_2_button_tt_new' : _tt_new(2,
   "\\n- [GetPlayer.GetName] получает модификатор %s на 12 месяцев, что снизит поступление финансовых продуктов в %s на #r -25%%#!" % (_SM('speculative_share_modifier_2'),_FC)),
 'speculative_share_3_button_tt_new' : _tt_new(3,
   "\\n- [GetPlayer.GetName] получает модификатор %s на 12 месяцев, что снизит поступление финансовых продуктов в %s на #r -50%%#!" % (_SM('speculative_share_modifier_3'),_FC)),
 'speculative_share_4_button_tt_new' : _tt_new(4,
   "\\n- [GetPlayer.GetName] получает модификатор %s на 12 месяцев, что снизит поступление финансовых продуктов в %s на #r -75%%#!" % (_SM('speculative_share_modifier_4'),_FC)),

 'speculative_share_5_button_tt' : _fc_tt(5),
 'speculative_share_5_button_tt_effect_1' : _fc_effect(5),
 'speculative_share_6_button_tt' : _fc_tt(6),
 'speculative_share_6_button_tt_effect_1' : _fc_effect(10),
 'speculative_share_7_button_tt' : _fc_tt(7),
 'speculative_share_7_button_tt_effect_1' : _fc_effect(15),
 'speculative_share_8_button_tt' : _fc_tt(8),
 'speculative_share_8_button_tt_effect_1' : _fc_effect(20),

 'speculative_share_9_button_tt'  : _pc_tt(9),
 'speculative_share_9_button_tt_effect_1_1'  : _pc_effect(9, 5, False),
 'speculative_share_10_button_tt' : _pc_tt(10),
 'speculative_share_10_button_tt_effect_1_1' : _pc_effect(10, 10, True),
 'speculative_share_11_button_tt' : _pc_tt(11),
 'speculative_share_11_button_tt_effect_1_1' : _pc_effect(11, 15, True),
 'speculative_share_12_button_tt' : _pc_tt(12),
 'speculative_share_12_button_tt_effect_1_1' : _pc_effect(12, 20, True),

 'speculative_share_13_button_tt' :
   "$speculative_share_13_button$\\n\\n$speculative_share_13_button_desc$\\n\\nВозможно:\\n$speculative_share_13_button_tt_1$\\n\\nЭффект:\\n- $speculative_share_13_button_tt_effect_1_1$",
 'speculative_share_13_button_tt_effect_1_1' :
   "Один %s в случайном штате будет полностью снесён, что уменьшит общее число %s в стране." % (_PC,_PC),

 'je_ef_efcc_situation' : "Комитет по экономическому и финансовому кризису",
 'je_efcc_progress_bar' : "Экономическая стабилизация",
 'je_efcc_progress_bar_desc' :
   "Ход экономической стабилизации: #T [GetPlayer.MakeScope.Var('je_efcc_1_global_variable_progress_bar_1').GetValue|0] мес./ 12 мес.#!",
 'current_modifiers_efcc' : "Текущие основные модификаторы",
 'current_situation' : "Обзор экономического и финансового кризиса",

 'active'      : "#N #l Активен#!#!",
 'stabilizing' : "#blue #l Стабилизация#!#!",
 'critical'    : "#gold #l Критический#!#!",
 'inactive'    : "#P #l Неактивен#!#!",
 'active_desc' :
   "$active$: После срабатывания кризис накладывает собственные модификаторы на #l 2 года.#!",
 'critical_desc' :
   "$critical$: У вас есть год, чтобы восстановить металлические резервы центрального банка — например, массовой продажей иностранной валюты, прямой рекапитализацией со стороны государства или международными займами для центрального банка.",
 'stabilizing_desc' :
   "$stabilizing$: Если за целый год не случится ни одного кризиса, счётчики экономической нестабильности и кризисов обнулятся — но только если страна #l не находится в состоянии войны.#!",

 'economic_instability_count' :
   "(Счёт: #T [GetPlayer.MakeScope.Var('economic_instability_count').GetValue|0]/2#!)",
 'central_bank_bankruptcy_country_count' :
   "(Счёт: #T [GetPlayer.MakeScope.Var('central_bank_bankruptcy').GetValue|0]#!)",
 'currency_crisis_country_count' :
   "(Счёт: #T [GetPlayer.MakeScope.Var('currency_crisis').GetValue|0]#!)",
 'economic_crisis_country_count' :
   "(Счёт: #T [GetPlayer.MakeScope.Var('economic_crisis').GetValue|0]#!)",
 'financial_crash_country_count' :
   "(Счёт: #T [GetPlayer.MakeScope.Var('financial_crash').GetValue|0]#!)",
 'country_bankruptcy_count' :
   "(Счёт: #T [GetPlayer.MakeScope.Var('country_bankruptcy').GetValue|0]#!)",

 'status_economic_crisis_1' : "#p Экономическая стабильность #!поддерживает ровный рост страны.",
 'status_economic_crisis_2' : "#gold Замедление экономики #!ослабляет производство и торговлю.",
 'status_economic_crisis_3' : "#N Экономический кризис #!тяжело расстраивает хозяйство страны.",
 'status_currency_crisis_1' : "\\n#p Денежная стабильность #!сохраняет доверие к национальной валюте.",
 'status_currency_crisis_2' : "\\n#gold Валютная нестабильность #!начинает давить на денежные рынки.",
 'status_currency_crisis_3' : "\\n#N Валютный кризис #!расшатывает национальную валюту.",
 'status_financial_crash_1' : "\\n#p Финансовая стабильность #!держит рынки в здоровом состоянии.",
 'status_financial_crash_2' : "\\n#gold Финансовая нестабильность #!расползается по финансовым рынкам.",
 'status_financial_crash_3' : "\\n#N Финансовый крах #!рушит рынки повсеместно.",
 'status_central_bank_bankruptcy_1' : "\\n#p Устойчивость центрального банка #!обеспечивает доверие к деньгам.",
 'status_central_bank_bankruptcy_2' : "\\n#gold Бедственное положение центрального банка #!— на то, чтобы избежать банкротства, есть год.",
 'status_central_bank_bankruptcy_3' : "\\n#N Банкротство центрального банка #!нарушило денежное управление страной.",
 'status_country_bankruptcy_1' : "\\n#p Бюджетная устойчивость #!удерживает государственные финансы в порядке.",
 'status_country_bankruptcy_2' : "\\n#gold Долговые затруднения государства #!усиливают давление на казну.",
 'status_country_bankruptcy_3' : "\\n#N Банкротство страны #!тяжело подорвало доверие к государству и его финансы.",

 'central_bank_bankruptcy_country_tooltip' :
   "#T #l Стоимость денег в золоте:#! [GetPlayer.MakeScope.ScriptValue('money_value_in_gold')|D]@gold!#! \\nНынешняя золотая стоимость национальной валюты @gold! — #b [GetPlayer.MakeScope.ScriptValue('money_value_in_gold')|D]#! @gold!. Если она держится ниже #n 0.01#! @gold! дольше #bold 1 года#!, может наступить #l #n банкротство центрального банка#!#!. Если страна уже переживает экономическую или финансовую нестабильность, падение ниже #n 0.01#! @gold! немедленно вызовет #n многофакторный экономический кризис#!.\\n > #u 2 года#! страна будет в кризисе и не сможет прокладывать [concept_trade]-пути (через #u 3 года#! после кризиса можно будет ввести новую валюту).",
 'currency_crisis_country_tooltip' :
   "#T #l Изменение стоимости денег за 1 год:#! [GetPlayer.MakeScope.ScriptValue('money_value_dif_1_final')|%|=+]#! \\nЕсли стоимость национальной валюты падает более чем на #n -50%#! за #bold 1 год#!, может наступить #l #n валютный кризис#!#!. Если страна уже переживает экономическую или финансовую нестабильность, обесценение валюты сильнее #n -50%#! немедленно вызовет #n многофакторный экономический кризис#!.\\n > #u 2 года#! страна будет в кризисе и не сможет прокладывать [concept_trade]-пути (через #u 3 года#! после кризиса можно будет ввести новую валюту).",
 'economic_crisis_country_tooltip' :
   "#T #l [concept_gdp] за 1 год:#! [GetPlayer.MakeScope.ScriptValue('GDP_dif_1_final')|%|=+]#! \\nЕсли [concept_gdp] страны падает более чем на #n -50%#! за #bold 1 год#!, может наступить #l #n экономический кризис#!#!. Если страна уже переживает экономическую или финансовую нестабильность, сжатие экономики сильнее #n -50%#! немедленно вызовет #n многофакторный экономический кризис#!.\\n > #u 2 года#! #t все здания#! в стране получат модификатор, снижающий их производительность более чем на #N 50%#!.",
 'financial_crash_country_tooltip' :
   "#T #l Изменение биржевого индекса за 1 год:#! [GetPlayer.MakeScope.ScriptValue('GDP_dif_1_final')|%|=+]#! \\nЕсли биржевой индекс страны падает более чем на #n -50%#! за #bold 1 год#!, может наступить #l #n финансовый крах#!#!. Если страна уже переживает экономическую или финансовую нестабильность, обвал рынка сильнее #n -50%#! немедленно вызовет #n многофакторный экономический кризис#!.\\n > #u 2 года#! #t все частные здания#! в стране получат модификатор, снижающий их производительность более чем на #N 50%#!.",
 'country_bankruptcy_tooltip' :
   "#T #l Банкротство страны:#!#! \\n Объявив банкротство, страна входит в полосу экономической нестабильности на весь срок действия модификатора. Из крупных кризисов этот наносит экономике наименьший ущерб, но создаёт крайне уязвимое положение: любой новый кризис немедленно перерастёт в #n многофакторный экономический кризис#!.",
}

# --------------------------------------------------------------------------
KEY_RE = re.compile(r'^(\s*)([A-Za-z0-9_.\-\']+):\s*(\d*)\s*"(.*)"\s*$')

def load(path):
    d, order = {}, []
    for line in io.open(path, encoding='utf-8-sig'):
        m = KEY_RE.match(line.rstrip('\n'))
        if m:
            d[m.group(2)] = m.group(4)
            order.append(m.group(2))
    return d, order

def good_of(key):
    for g in GOOD_IDS:
        if re.search(r'(?<![a-z])' + re.escape(g) + r'(?![a-z])', key):
            return g
    return None

def pattern_of(key, g):
    if not g:
        return key
    return re.sub(r'(?<![a-z])' + re.escape(g) + r'(?![a-z])', '{G}', key)

def main(write=True):
    stamp = '2026-08-19'
    report = {'added': {}, 'removed': {}, 'unresolved': []}
    for enfile in sorted(os.listdir(ROOT_OUT)):
        if not re.match(r'^0[01]_ef_.*_l_english\.yml$', enfile):
            continue
        base = enfile[:-len('_l_english.yml')]
        rufile = os.path.join(ROOT_RU, base + '_l_russian.yml')
        if not os.path.exists(rufile):
            report['unresolved'].append('MISSING RU FILE: ' + rufile)
            continue
        en, en_order = load(os.path.join(ROOT_OUT, enfile))
        ru, ru_order = load(rufile)

        new = [k for k in en_order if k not in ru]
        obsolete = set(k for k in ru_order if k not in en)

        lit  = LIT.get(base, {})
        tpl  = TPL.get(base, {})
        cp   = set(COPY.get(base, set()))
        if base == '01_ef_event_localization':
            cp |= set(p for p in (pattern_of(k, good_of(k)) for k in new)
                      if p.endswith('_message_tooltip'))

        out = []
        seen = set()
        for k in new:
            if k in seen:
                continue
            seen.add(k)
            g = good_of(k)
            p = pattern_of(k, g)
            if k in lit:
                val = lit[k]
            elif p in cp:
                val = en[k]                      # markup only, keep as-is
            elif p in tpl:
                if g is None:
                    report['unresolved'].append(base + ' :: ' + k + ' (template needs a good)')
                    continue
                nom, noml, gen = G[g]
                val = (tpl[p].replace('{ID}', g).replace('{NOM}', nom)
                             .replace('{NOML}', noml).replace('{GEN}', gen))
            else:
                report['unresolved'].append(base + ' :: ' + k + ' :: ' + en[k][:90])
                continue
            if '"' in val:
                report['unresolved'].append(base + ' :: ' + k + ' :: RAW QUOTE IN VALUE')
                continue
            out.append(' %s:0 "%s"' % (k, val))

        if not write:
            report['added'][base] = len(out)
            report['removed'][base] = len(obsolete)
            continue

        lines = io.open(rufile, encoding='utf-8-sig').read().split('\n')
        kept = []
        for line in lines:
            m = KEY_RE.match(line.rstrip('\n'))
            if m and m.group(2) in obsolete:
                continue
            kept.append(line)
        while kept and kept[-1].strip() == '':
            kept.pop()
        if out:
            kept.append('')
            kept.append('# --- sync with E&F build 04.07.2026, %s ---' % stamp)
            kept += out
        kept.append('')
        io.open(rufile, 'w', encoding='utf-8-sig', newline='\n').write('\n'.join(kept))
        report['added'][base] = len(out)
        report['removed'][base] = len(obsolete)

    print(json.dumps(report, ensure_ascii=False, indent=1))

if __name__ == '__main__':
    main(write=('--dry' not in sys.argv))
