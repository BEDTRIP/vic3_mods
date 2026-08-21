import io, re

p = "ef+tr_analysis_2026-08-21.md"
s = open(p, encoding="utf-8-sig").read()

old_advice_start = "**Что делать.** Файл нужен, но его надо пересобрать от текущего T&R:"
old_advice_end = "Файл сжимается со 130 строк до трёх и перестаёт разъезжаться при каждом обновлении T&R.\n"
i = s.index(old_advice_start)
j = s.index(old_advice_end) + len(old_advice_end)

new_advice = """**Что делать.** Первым делом хотелось заменить `REPLACE:` на три строки
`INJECT:` — тогда патч ничего не переизлагает и не может отстать от T&R. Не
годится: `INJECT:` умеет только дописать недостающую группу, но не убрать
устаревшую, а две пересекающиеся группы дата-оптимизации на одном здании
(`pmg_data_optimization_heavy_industry` и `..._algorithmic_dispatch` отличаются
одним PM из шести) дали бы игроку возможность включить обе.

Значит здание надо переизложить — но не руками. `zzzz_ef_tr_fix_buildings_gen.txt`
в фикс-моде собирается из `ztr_vanilla_modified_buildings.txt` как он есть
сегодня, плюс две группы E&F; пересборка — одна команда
(`tools/regen_ef_tr_copies.py`). Ровно тот же приём, что в
`regen_ef_psc_copies.py`.

"""
s = s[:i] + new_advice + s[j:]

old_todo_start = "## Что делать, по убыванию\n"
k = s.index(old_todo_start)
m = s.index("# Сделано 21.08.2026")
new_todo = """## Что делать, по убыванию

1. **Решить вопрос 128 товаров** — до этого остальное смысла не имеет. Отложено
   по договорённости.
2. Всё остальное из списка ниже сделано в тот же день — см. раздел
   «Сделано 21.08.2026» и мод `_ef/ef+tr fix`:
   PMG электростанции и автозавода, чеканка золота, `building_gold_mines`,
   Consumer Electronics и Computer Assembly Plant, канонические имена зданий,
   корзины инфляции, локализация, `relationships`, BOM.
3. **Не закрыто снизу**: дубль инъекций в семь зданий Morgenröte — решается при
   сборке мегапака, выкинуть `zztr_mr_buildings.txt` и
   `zztr_modified_mr_buildings.txt` из компача.

Побочно — кандидаты в `ef hotfix 1.13`, к компачу отношения не имеют:
`building_naval_base` и `building_military_shipyard` удалены из ванили в 1.13, а E&F
их ещё зовёт; `building_vineyard_plantation` не существовал никогда;
`hardwood` стоит в знаменателе трёх корзин инфляции, не появляясь ни в одном
числителе.

---

"""
s = s[:k] + new_todo + s[m:]

open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ок")
