# LD Profiler View — окно профилировщика скриптов для замеров

Мод только для прогонов-замеров (в форк и в плейсеты для игры не входит). Подменяет окно встроенного профилировщика
скриптов `gui/script_profiler/script_profiler.gui` (игра грузит его по этому пути, `victoria3.exe`): во весь экран,
таблица «вызываемые текущей записи» с полным именем, файлом:строкой, полным и собственным временем и числом вызовов —
чтобы читать снимком. Строка 1 таблицы — y = 0.155 экрана, шаг 0.0215 (1080p); щелчок по строке выбирает запись,
кнопка «root» (0.02, 0.06) — корень.

Прогон: `sync_mod(repo_folder="tools/ld_profiler_view", live_name="LD Profiler View")`, плейсет
`"Ledgerdemain + LD Profiler View"` (`playset_content_load.py`), команды
`Script.Profiling.Start;end:Script.Profiling.Stop;end:Script.Profiling.Gui;end:ui:wait 3;end:ui:shot prof_root;…`.
Файловый `ScriptProfiling.Dump` в 1.13.11 роняет игру (и на ванили), поэтому окно.
