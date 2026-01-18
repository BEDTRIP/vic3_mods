### PSC + PBE compatch (`pb+pbe`)

Совместимость для:
- `private_construction_sector` (PSC)
- `PowerBlocksExpanded` (PBE)

### Что фиксит

Оба мода добавляют свои хуки в `common/on_actions` и **оба определяют `on_monthly_pulse`**.
Если игра/загрузчик в текущей версии **не мерджит** два определения одного и того же on_action, то один из модов может “перезатереть” второй и его ежемесячная логика перестанет запускаться.

Этот компач **объединяет** содержимое `on_monthly_pulse`, сохраняя:
- PSC: `set_construction_weekly_on_action`
- PBE: `kates_weekly_global_on_action` + задержки 7/14/21

Файл: `common/on_actions/zz_pb_pbe_on_actions.txt`

### Порядок загрузки

1. `private_construction_sector`
2. `PowerBlocksExpanded`
3. `pb+pbe` (этот компач)

