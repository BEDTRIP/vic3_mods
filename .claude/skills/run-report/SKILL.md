---
name: run-report
description: The run report of the fork «E&F: Ledgerdemain» — one HTML page, the same for every sandbox run (checks, summary with thresholds, money, «прочее», levels bought, metal, the pops' hoard, pool, budget and debt, people, construction, exchanges, banks, by year against a base run). Use after every sandbox run of the fork, or when the user says "отчёт по прогону", "сделай html по прогону", "аналитика прогона", "сравни прогоны".
---

# Отчёт по прогону форка

Страница одинакова для всех прогонов (пользователь 12.10: «чтоб я тоже понимал, что происходит»): тот же порядок
разделов, те же графики, в начале раздела — что показано и какая норма; сводка «Коротко» — по фиксированным порогам.
Скрипт — `tools/ld_run_report.py` (что читает — его docstring); строки лога, на которых он стоит, — `docs/entry-points.md`
форка, «Логи» (`EFW|all`, `EFV|mkt`, `EFJ|lvl`, `EFD|xch_month`, …).

## Когда

- после **каждого** прогона форка навыком `vic3-sandbox` — до разбора и до ответа пользователю;
- по просьбе — по любому прогону из `runs/` моста;
- два прогона — с `--base`: таблица «по годам» с числами базы рядом.

## Как (из облака, через мост `vic3-pc`)

1. Скрипт и форк на ПК — свежие: `checkout("main")` (сверить хеш).
2. На ПК — данные и страница:
   `py_tool("ld_run_report", ["runs/<id>", "runs/<id>/report.html", "--until", "1847.12", "--data", "runs/<id>/report.jsonl"])`.
   Прогоны этапов — до конца 1847 (`план.md` форка): `--until 1847.12`, чтобы прогоны сравнивались по годам.
3. Данные сюда: `python3 tools/pc_bridge/pc_fetch.py runs/<id>/report.jsonl <scratchpad>/report_<id>.jsonl`; база —
   так же её `report.jsonl` (прошлый прогон этапа; у старых прогонов без файла — сначала шаг 2 по ним).
4. Страница здесь: `python3 tools/ld_run_report.py --from-data <scratchpad>/report_<id>.jsonl <scratchpad>/report_<id>.html
   [--base <scratchpad>/report_<base>.jsonl] [--title "Прогон <id> — <этап>"]`.
5. Опубликовать артефактом (новый на прогон; заголовок — «Прогон <id>»), ссылку — пользователю и в файл этапа форка
   у строки прогона. Свой разбор — текстом в ответе и в файле этапа; на странице только то, что считает скрипт.

## Локально (пользователь на ПК)

`py tools/ld_run_report.py runs/<id> runs/<id>/report.html --until 1847.12 [--base runs/<base>/report.jsonl]` — открыть
`report.html` в браузере. `--data runs/<id>/report.jsonl` сохраняет данные прогона, чтобы потом сравнивать с ним.

## Что править где

- Новый показатель: строка лога в форке (`ld_acc_log.txt` и др.), её разбор и место на странице — в
  `tools/ld_run_report.py` (`read_run` — разбор, `charts` — графики, `SECTIONS` — разделы и пояснения, `summary` —
  пороги сводки); документ логов форка — в том же коммите.
- Пороги сводки — в `summary`: «прочее» < 1 % M2; металл на счетах 0,8–1,15 от добычи; кубышка населения ± 5 п. п. от
  цели; пул < 25 % M2; капитал банков < ×5 за прогон; ошибок по файлам форка (`ld_*`) — 0.
- Страница не меняется от прогона к прогону: свой разбор не вписывать в неё, а писать в ответ и в файл этапа.
