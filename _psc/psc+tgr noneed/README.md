### PSC + The Great Revision (TGR) ComPatch (`pb+tgr`)

Совместимость для:
- `TheGreatRevision` (TGR)
- `private_construction_sector` (PSC)

### Порядок загрузки

1. `TheGreatRevision`
2. `private_construction_sector`
3. `pb+tgr` (этот компач)

### Что фиксит

Оба мода переопределяют здание **`building_construction_sector`**:
- TGR задаёт базовую структуру здания и важные флаги (например `has_max_level`).
- PSC превращает строительный сектор в **частный** и перепрошивает его поведение под свою систему строительных товаров/регулятора.

Этот компач поставляет **merged-версию** `building_construction_sector`, чтобы не терялись правки ни одной из сторон.

Файл: `common/buildings/zz_pb_tgr_psc_construction.txt`

