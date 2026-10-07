"""Вариант форка для замера (ФК2, шаг 5): закомментировать строки в рабочей копии форка перед `sync_fork`.

    python tools/ld_measure_variant.py <путь в форке>:<регулярное выражение> [...]
    python tools/ld_measure_variant.py --preset no_step|no_receiver|no_monthly|no_liquidity_pmg|no_ownership_pmg

Каждая строка файла, которая подходит под выражение и ещё не закомментирована, получает `# ` перед текстом (отступ
сохраняется). Только для замера на ПК: мост `checkout_fork` → этот инструмент через `py_tool` → `sync_fork` → прогон;
следующий `checkout_fork` возвращает рабочую копию к ветке. В репозиторий форка такие правки не коммитятся.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ld_gen  # noqa: E402

_PMG_FILES = ["ef_01_industry.txt", "ef_02_agro.txt", "ef_03_mines.txt", "ef_04_plantations.txt", "ef_06_urban_center.txt",
              "ef_09_misc_resource.txt", "ef_11_private_infrastructure.txt"]
PRESETS = {
    # недельный шаг модели денег (цепочка и слот остаются — перезапуск через 7 дней)
    "no_step": ["common/on_actions/ld_money_model_on_actions.txt:^\\s*zz_ef_money_model_step = yes",
                "common/scripted_effects/ld_money_model.txt:^\\s*zz_ef_money_model_step = yes"],
    # приёмник GUI-моста (данные бюджета из геттеров GUI)
    "no_receiver": ["common/scripted_guis/ld_money_hook.txt:^\\s*zz_ef_money_hook_receive = yes"],
    # месячный шаг модели денег (зона валюты, курс серебра, сила валюты, ставка, политика ЦБ)
    "no_monthly": ["common/on_actions/ld_money_model_on_actions.txt:^\\s*zz_ef_money_model_monthly_step = yes"],
    # R0.4: группа методов «ликвидность» (расчёты валютой) — из списков групп зданий
    "no_liquidity_pmg": [f"common/buildings/{f}:^\\s*pmg_market_liquidity\\b" for f in _PMG_FILES + ["zz_PSC_construction.txt"]],
    # R0.4: группы методов «частное владение» (выпуск акций) — из списков групп зданий
    "no_ownership_pmg": [f"common/buildings/{f}:^\\s*pmg_private_ownership_[a-z_]+\\b" for f in _PMG_FILES],
}


def apply(spec):
    rel, rx = spec.split(":", 1)
    p = os.path.join(ld_gen.FORK, rel)
    with open(p, "rb") as f:
        raw = f.read()
    text = raw.decode("utf-8")
    pat = re.compile(rx)
    n = 0
    out = []
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        if pat.search(body) and not body.lstrip().startswith("#"):
            ind = body[: len(body) - len(body.lstrip())]
            line = ind + "# " + body.lstrip() + line[len(body):]
            n += 1
        out.append(line)
    with open(p, "wb") as f:
        f.write("".join(out).encode("utf-8"))
    print(f"{rel}: закомментировано строк {n}")
    return n


def replace(spec):
    """<путь>:<регулярное выражение>:<замена> — заменить в строках файла (для опыта)."""
    rel, rx, rep = spec.split(":", 2)
    p = os.path.join(ld_gen.FORK, rel)
    with open(p, "rb") as f:
        text = f.read().decode("utf-8")
    new, n = re.subn(rx, rep, text, flags=re.M)
    with open(p, "wb") as f:
        f.write(new.encode("utf-8"))
    print(f"{rel}: заменено {n}")
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("specs", nargs="*")
    ap.add_argument("--preset", action="append", default=[])
    ap.add_argument("--replace", action="append", default=[], help="<путь>:<regex>:<замена>")
    a = ap.parse_args()
    if a.replace:
        if sum(replace(s) for s in a.replace) == 0:
            sys.exit("ни одной замены")
        if not a.specs and not a.preset:
            return
    specs = list(a.specs)
    for pr in a.preset:
        specs += PRESETS[pr]
    if not specs:
        sys.exit("нечего делать")
    if sum(apply(s) for s in specs) == 0:
        sys.exit("ни одна строка не подошла")


if __name__ == "__main__":
    main()
