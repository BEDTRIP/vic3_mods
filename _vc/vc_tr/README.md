### Готово: конфликты найдены и перепроверены вручную

Я прогнал ваш `tools/scan_conflicts.py` **отдельно для трёх корней TechRes+Kuromi** `t&r/`, `kai/`, `cmf/`) против *`Victorian Century/`**, плюс проверил GUI‑идентификаторы и руками посмотрел самые критичные места (buy_packages / pop_needs / defines / on_actions).

### Отчёты в рабочей папке

- `conflicts_tr_vs_vc_report.md` — **T&R vs VC** (common‑дубликаты: **137**, совпадений путей файлов: **0**)
- `conflicts_kai_vs_vc_report.md` — **KAI vs VC** (common‑дубликаты: **1** `NAI`), совпадений путей: **0**)
- `conflicts_cmf_vs_vc_report.md` — **CMF vs VC** (совпадений путей: **4**, common‑дубликаты: **6**)
- GUI:
  - `conflicts_tr_vs_vc_gui_ids.txt`
  - `conflicts_cmf_vs_vc_gui_ids.txt`
- Единый “человеческий” итог с приоритетами под ваш load order:
  - `conflicts_tr_kai_cmf_vs_vc_master.md`

### Ключевые конфликты (важно при порядке: T&R → KAI → CMF → VC)

- **T&R vs VC**:
  - `common/buy_packages`: `wealth_10..wealth_99` — у T&R `TRY_INJECT`, у VC `REPLACE_OR_CREATE` ⇒ **VC перезатирает, инжекты T&R пропадают**
  - `common/pop_needs`: `popneed_*` — у VC `REPLACE_OR_CREATE` ⇒ **VC перезатирает потребление новых goods из T&R**
  - `common/on_actions`: `on_monthly_pulse_country` / `on_yearly_pulse_country` ⇒ **VC перезатирает, T&R-пульсы перестают работать**
  - `common/defines`: `NPops` ⇒ **VC перезатирает блок, демография/поп‑рост T&R теряются**
  - `common/company_types`: 32 `company_*` ⇒ **будут версии VC**
- **KAI vs VC**:
  - `common/defines`: `NAI` ⇒ **VC перезатирает, Kuromi AI фактически не применится без компача**
- **CMF vs VC**:
  - Жёсткие совпадения путей: `common/parties/{conservative,liberal,radical}_party.txt` и `gui/00_MDF_frontend_dlc.gui` ⇒ **всегда будут версии VC**
  - `common/on_actions`: `on_new_ruler` ⇒ **VC перезатирает, CMF‑блокировка регентств может пропасть**
  - `common/political_movements`: `movement_bonapartist`, `movement_utilitarian` ⇒ **будут версии V**

