### PSC + Morgenrote compatch (`pb+mr`)

Совместимость для:
- `private_construction_sector` (PSC)
- `Morgenrote` (MR)

### Что фиксит

Оба мода добавляют свои хуки в `common/on_actions` и **оба определяют `on_monthly_pulse`**.
Если игра/загрузчик в текущей версии **не мерджит** два определения одного и того же on_action, то один из модов может “перезатереть” второй и его ежемесячная логика перестанет запускаться.

Этот компач **объединяет** `on_monthly_pulse`, сохраняя:
- PSC: `set_construction_weekly_on_action`
- MR: `mr_on_monthly_pulse` + `mr_on_weekly_pulse`

Файл: `common/on_actions/zz_pb_mr_on_actions.txt`

### Порядок загрузки

1. `private_construction_sector`
2. `Morgenrote` (и его зависимости, например CMF, если используются)
3. `pb+mr` (этот компач)

