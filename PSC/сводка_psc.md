### Общая идея PSC (по папке `common`)

**PSC радикально перестраивает систему строительства относительно ванили: делает строительство через отдельные товары-строительство, регуляторные здания и сложную логику распределения гос/частных расходов.**

- **Defines / buildings / history**  
  - `PSC_defines.txt`: ванильный `CONSTRUCTION_CAMP_BUILDING` переназначается на новое здание `building_construction_regulator`.  
  - `zz_PSC_construction.txt` (buildings): `building_construction_sector` переопределён (другая `ai_value`, требования, логика), добавлено/создано невидимое здание `building_construction_regulator` (не строится игроком, не расширяется, не продаётся) в группе `bg_construction_regulator`.  
  - `PSC_buildings.txt` (history): всем странам, у которых уже есть технология `urbanization`, в каждом штате создаётся по 1 уровню `building_construction_regulator`; если в штате есть `building_construction_sector` – включается особая логика выбора метода «перевода» строительства (`set_new_point_conversion_method`), плюс вызывается `set_point_conversion_method_from_tech`.

- **Goods / production_methods / production_method_groups / script_values**  
  - `PSC_goods.txt`: добавляются/переопределяются специальные товары `wood_construction`, `iron_construction`, `steel_construction`, `arc_welded_construction` с собственными ценами и иконками – это отдельные «строительные товары», а не абстрактные очки.  
  - `zz_PSC_construction.txt` (PM): ванильные PM зданий строительства (`pm_wooden_buildings`, `pm_iron_frame_buildings`, `pm_steel_frame_buildings`, `pm_arc_welded_buildings`) переопределены с новыми входами/выходами (они производят именно эти товары-строительство) и новой структурой занятости.  
  - Добавлены PM типа `pm_*_point_conversion`, которые **конвертируют произведённые строительные товары в реальную `country_construction`** через бюрократов в `building_construction_regulator`.  
  - `PSC_construction.txt` (PMG): создаётся `pmg_construction_regulator` со списком этих PM-конверсий; это новая группа для регуляторного здания.  
  - `PSC_construction_values.txt` и `PSC_set_values.txt`: вводится большая математика для:  
    - разделения частных и госрасходов на строительство;  
    - оценки доли приватизации (`privatisation_spending_percent`, `weekly_income_multiplier_base`, и т.п.);  
    - вычисления «предельного» и «ограниченного» гос.строительства;  
    - распределения строительства по штатам в зависимости от локального выпуска строительных товаров, цен и эффективности (включая расчёт через приближённый `calculate_sqrt`).  
    - фактически, **скорость строительства теперь привязана к реальному выпуску строительных товаров + инвестиционному пулу, а не к фиксированным абстрактным очкам**.

- **On_actions / scripted_effects / script_values (событийная обвязка)**  
  - `PSC_global.txt`: глобальный сценарий на старте игры запускает on_action `set_construction_start`.  
  - `PSC_on_actions.txt`:  
    - ежемесячный `on_monthly_pulse` вызывает `set_construction_weekly_on_action`, который через `delay_event_switch` раскладывает по дням вызовы перерасчёта:  
      - `set_construction_country` – пересчёт спроса на строительство, баланса гос/частных расходов и распределения по штатам;  
      - `set_spending_value` – обновление фактического гос.уровня строительства для игрока.  
    - хуки на смену PM, полученные технологии и постройку сектора заставляют `building_construction_sector` обновлять метод конверсии (`set_new_point_conversion_method`, `set_point_conversion_method_from_tech`).  
  - `PSC_event_values.txt`: служебные значения для календаря (длина месяца, «день недели» в логике игры), чтобы график недельных перерасчётов был стабильным.  

- **Static_modifiers / alert_types / game_concepts / scripted_guis**  
  - `PSC_modifiers.txt`:  
    - `construction_throughput_mult` – модификатор, который накидывает throughput именно регуляторному зданию;  
    - `country_private_construction_allocation_add` – хранит долю частного строительства;  
    - `state_construction_efficiency_increase` – модификатор штатной эффективности строительства.  
  - `PSC_alert_types.txt`: переопределяет ванильный алерт `insufficient_construction_for_investment` – он теперь учитывает новый показатель `construction_demand_ratio`, связанный с новой системой спроса/предложения на строительство.  
  - `PSC_game_concepts.txt`: добавляет пустой `concept_construction_spending` (под это идёт локализация/всплыв.подсказки, чтобы объяснить игроку новую механику).  
  - `PSC_construction_sguis.txt`: набор скриптовых GUI-кнопок (`psc_button_*`), которые **позволяют игроку изменять переменную `construction_spending_level` (по 0.01/0.05/0.1 с модификаторами Shift/Ctrl)**, автоматически пересчитывая лимит гос.строительства; плюс служебные эффекты для сохранения и отображения фактических расходов (`psc_save_real_construction_cost`, `psc_test_show`).  

Итого по сравнению с ванилью: **PSC превращает строительство в «рыночную» систему, где очки строительства – это результат производства специальных строительных товаров + регулятора в каждом штате, с динамическим разделением гос/частных расходов, более сложным распределением по штатам и отдельным управляемым уровнем гос.строительных трат через интерфейс.** Если нужно, могу отдельно выписать поведение ИИ (как он выбирает уровень строительства и штаты для приоритета) или разложить по шагам, как именно игра каждую неделю пересчитывает строительство в PSC.