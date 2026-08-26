"""
content_holes.py -- то, чего pair_matrix.py не видит по устройству.

pair_matrix сравнивает ключи, которые определяют ОБА мода. Из этого выпадают
три класса, каждый из которых уже стоил реальной потери в этом наборе:

  1. НОВЫЙ КОНТЕНТ. Здание/товар/закон, объявленный только одним модом, не может
     попасть в пересечение никогда. Чужие рукописные списки по имени (акции E&F,
     building_types компаний, ai_enact_weight законов у KAI) про него не знают.
     Так нашлись LLWA.6 и GR.15.
  2. СЪЕДЕННЫЕ ВКЛАДЫ. Мод, который переопределяет чужую запись полным телом,
     молча выбрасывает под-блоки, которые внесли моды раньше по цепочке.
     Матрица покажет "общий ключ", но не скажет, что именно потерялось.
     Так нашлись GR.5/GR.6-дополнения и llwa+morg (LLWA.7).
  3. СОБРАННЫЕ СБОРКИ. blocks.json содержал только исходные моды -- ни мегапак,
     ни аддоны в матрицу не входили. Блок, который грузится последним, съедает
     уже сделанную работу, и пары для этого не существует. Так нашлась GR.16.

Источник правды о цепочке -- ключ "load_order" в blocks.json (не "order":
тот задаёт лишь порядок колонок матрицы). Ярлыки -- ключ "labels".

Использование:
    python3 tools/content_holes.py --blocks tools/blocks.json
    python3 tools/content_holes.py --only new --source USU
    python3 tools/content_holes.py --only builds
    python3 tools/content_holes.py --rebuild          # пересобрать кэш

Разделы (--only): new | pmg | companies | registry | builds | all (по умолчанию all).

Кэш -- рядом с кэшем pair_matrix, имя = basename + md5(абсолютный путь)[:12].
Индексация Morgenröte ~40 с, остальных заметно быстрее; без кэша полный прогон
не влезет в лимит device_bash, поэтому кэш обязателен.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

KEY_RE = re.compile(r"^(?:([A-Z_]+):)?([A-Za-z0-9_.\-]+)\s*=")
TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")
BLOCK_RE = re.compile(r"^(?:([A-Z_]+):)?([A-Za-z0-9_.\-]+)\s*=\s*\{")

# Категории, где "новый ключ" -- это контент, который чужие моды могут не знать.
# Всё остальное (методы, скрипт-значения, модификаторы) даёт шум на тысячи строк.
CONTENT_CATEGORIES = [
    "common/buildings",
    "common/goods",
    "common/building_groups",
    "common/company_types",
    "common/laws",
    "common/law_groups",
    "common/institutions",
    "common/technology",
    "common/pop_types",
    "common/subject_types",
    "common/diplomatic_actions",
    "common/decrees",
    "common/power_bloc_principles",
    "common/company_charter_types",
    "common/state_traits",
]

# Категории, где общий ключ никогда не конфликт: движок их складывает.
ADDITIVE_CATEGORIES = {
    "common",
    "common/on_actions",
    "common/named_colors",
    "common/modifier_type_definitions",
}
ADDITIVE_PREFIXES = ("common/history/",)

REPLACING_PREFIXES = {"", "REPLACE", "REPLACE_OR_CREATE", "TRY_REPLACE"}

# Поднимать при любой правке парсера: файлы кэша со старой версией просто
# перестают находиться. Удалить их с монтирования нельзя -- переносить в _to_delete.
CACHE_VERSION = "v2"


def cache_path(cache_dir: str, path: str) -> str:
    h = hashlib.md5(os.path.abspath(path).encode("utf-8")).hexdigest()[:12]
    return os.path.join(cache_dir, f"{os.path.basename(path.rstrip('/'))}.{h}.holes.{CACHE_VERSION}.json")


def parse_records(text: str):
    """Верхнеуровневые записи файла: (префикс, ключ, тело). Учитывает BOM и
    записи, начинающиеся в первой строке файла."""
    depth = 0
    cur = None
    body: list[str] = []
    for raw in text.splitlines():
        line = raw.split("#", 1)[0]
        if depth == 0:
            m = BLOCK_RE.match(line.lstrip("﻿"))
            if m:
                cur = (m.group(1) or "", m.group(2))
                body = []
        if cur is not None:
            body.append(line)
        depth += line.count("{") - line.count("}")
        if depth <= 0:
            if cur is not None:
                yield cur[0], cur[1], "\n".join(body)
            cur = None
            depth = 0


def inner_list(body: str, tag: str) -> list[str]:
    m = re.search(tag + r"\s*=\s*\{(.*?)\}", body, re.S)
    return re.findall(r"[A-Za-z0-9_]+", m.group(1)) if m else []


def index_source(root: str) -> dict:
    defs: dict[str, dict[str, list]] = {}
    tokens: set[str] = set()
    buildings: dict[str, list] = {}
    companies: dict[str, list] = {}
    common = os.path.join(root, "common")
    for dp, _dns, fns in os.walk(common):
        for fn in fns:
            if not fn.lower().endswith(".txt"):
                continue
            full = os.path.join(dp, fn)
            rel = os.path.relpath(full, root).replace("\\", "/")
            cat = os.path.dirname(rel)
            try:
                txt = open(full, encoding="utf-8-sig", errors="ignore").read()
            except OSError:
                continue
            tokens.update(TOKEN_RE.findall(txt))
            depth = 0
            for raw in txt.splitlines():
                line = raw.split("#", 1)[0]
                if depth == 0:
                    m = KEY_RE.match(line.lstrip("﻿"))
                    if m:
                        defs.setdefault(cat, {}).setdefault(m.group(2), []).append([m.group(1) or "", rel])
                depth += line.count("{") - line.count("}")
            if cat == "common/buildings":
                for pre, key, body in parse_records(txt):
                    own = re.search(r"ownership_type\s*=\s*(\w+)", body)
                    bg = re.search(r"building_group\s*=\s*([A-Za-z0-9_]+)", body)
                    buildings.setdefault(key, []).append({
                        "pre": pre, "file": rel,
                        "pmg": inner_list(body, "production_method_groups"),
                        "own": own.group(1) if own else None,
                        "bg": bg.group(1) if bg else None})
            elif cat == "common/company_types":
                for pre, key, body in parse_records(txt):
                    companies.setdefault(key, []).append({
                        "pre": pre, "file": rel,
                        "bt": inner_list(body, "building_types"),
                        "ext": inner_list(body, "extension_building_types")})
    return {"defs": defs, "tokens": sorted(tokens),
            "buildings": buildings, "companies": companies}


def load_chain(blocks_file: str, rebuild: bool):
    base = os.path.dirname(os.path.abspath(blocks_file))
    cfg = json.load(open(blocks_file, encoding="utf-8"))
    cache_dir = os.path.abspath(os.path.join(base, cfg.get("cache", "_cache")))
    os.makedirs(cache_dir, exist_ok=True)
    labels = cfg.get("labels", {})
    chain = []
    for relpath in cfg["load_order"]:
        path = os.path.abspath(os.path.join(base, relpath))
        label = labels.get(relpath) or os.path.basename(path)
        if not os.path.isdir(path):
            print(f"  ! путь не существует, пропущен: {relpath}", file=sys.stderr)
            continue
        cf = cache_path(cache_dir, path)
        if rebuild or not os.path.exists(cf):
            data = index_source(path)
            json.dump(data, open(cf + ".tmp", "w"), ensure_ascii=False)
            os.replace(cf + ".tmp", cf)  # атомарно: прогон могут убить по таймауту
            print(f"  индексирован {label}", file=sys.stderr)
        else:
            data = json.load(open(cf))
        data["tokens"] = set(data["tokens"])
        chain.append((label, relpath, data))
    return cfg, chain


def ord_key(e):
    """Порядок переопределения: сначала порядок модов, внутри одного мода --
    байтовый порядок имени файла. Ровно так грузит игра."""
    return (e["i"], e["file"])


def report_new(chain, only_source=None):
    print("\n" + "=" * 78)
    print("1. НОВЫЙ КОНТЕНТ: ключи, которых нет ни у кого другого в цепочке")
    print("=" * 78)
    print("Матрица такие ключи не видит никогда. Смотреть на колонку «упоминают»:")
    print("«никто» значит, что чужие рукописные списки по имени про этот контент не знают.\n")
    for i, (label, _rel, data) in enumerate(chain):
        if only_source and label != only_source:
            continue
        rows = []
        for cat in CONTENT_CATEGORIES:
            mine = data["defs"].get(cat, {})
            for key, occ in sorted(mine.items()):
                if all(p not in REPLACING_PREFIXES for p, _f in occ):
                    continue  # только TRY_* без создания -- запись может не появиться
                if any(key in other["defs"].get(cat, {}) for j, (_l, _r, other) in enumerate(chain) if j != i):
                    continue
                mentions = [l for j, (l, _r, o) in enumerate(chain) if j != i and key in o["tokens"]]
                rows.append((cat, key, occ[0][0] or "голый", mentions))
        if not rows:
            continue
        print(f"--- {label}: {len(rows)} собственных ключей")
        for cat, key, pre, mentions in rows:
            who = ", ".join(mentions) if mentions else "НИКТО"
            print(f"    {cat.replace('common/',''):22} {key:44} [{pre}]  упоминают: {who}")
        print()


def report_pmg(chain, built=frozenset(), strict=False):
    print("\n" + "=" * 78)
    print("2. СЪЕДЕННЫЕ PMG: чьи production_method_groups теряются под чужим телом")
    print("=" * 78)
    print("Для каждого здания берётся ПОСЛЕДНЕЕ замещающее тело в цепочке и из него")
    print("вычитаются группы, которые внесли источники РАНЬШЕ, и всё, что дописано INJECT:")
    print("после него. Что осталось -- потеря. Осознанный редизайн (переименованная группа,")
    print("другая механика того же здания) выглядит так же -- решает человек, не скрипт.\n")
    allb: dict[str, list] = {}
    for i, (label, _rel, data) in enumerate(chain):
        for key, entries in data["buildings"].items():
            for e in entries:
                allb.setdefault(key, []).append({**e, "i": i, "label": label})
    found = 0
    for key, entries in sorted(allb.items()):
        reps = [e for e in entries if e["pre"] in REPLACING_PREFIXES and e["pmg"]]
        if not reps:
            continue
        last = max(reps, key=ord_key)
        # всё, что дописано ПОСЛЕ последнего замещающего тела (INJECT: компача),
        # восстанавливает группу -- иначе каждый уже закрытый мердж читался бы как потеря
        have = set(last["pmg"])
        for e in entries:
            if ord_key(e) > ord_key(last):
                have.update(e["pmg"])
        lost: dict[str, set] = {}
        for e in entries:
            if ord_key(e) >= ord_key(last):
                continue
            for p in e["pmg"]:
                if p not in have:
                    lost.setdefault(p, set()).add(e["label"])
        if not lost:
            continue
        touches_built = any(w in built for who in lost.values() for w in who)
        if strict and not touches_built:
            continue
        found += 1
        mark = " !!" if touches_built else ""
        print(f"### {key}  <- {last['label']} {last['pre'] or 'голое тело'} ({last['file']}){mark}")
        for p, who in sorted(lost.items()):
            print(f"      - {p:46} [{', '.join(sorted(who))}]")
    print(f"\nвсего зданий с потерями: {found}")


def report_companies(chain, built=frozenset(), strict=False):
    print("\n" + "=" * 78)
    print("3. СЪЕДЕННЫЕ КОМПАНИИ: building_types / extension_building_types")
    print("=" * 78)
    print("Тот же приём для компаний. INJECT: складывается и сюда не попадает --")
    print("попадает только то, что стёрто заменяющим телом более позднего источника.\n")
    allc: dict[str, list] = {}
    for i, (label, _rel, data) in enumerate(chain):
        for key, entries in data["companies"].items():
            for e in entries:
                allc.setdefault(key, []).append({**e, "i": i, "label": label})
    found = 0
    for key, entries in sorted(allc.items()):
        reps = [e for e in entries if e["pre"] in REPLACING_PREFIXES and (e["bt"] or e["ext"])]
        if not reps:
            continue
        last = max(reps, key=ord_key)
        have = set(last["bt"]) | set(last["ext"])
        for e in entries:
            if ord_key(e) > ord_key(last):
                have |= set(e["bt"]) | set(e["ext"])
        lost: dict[str, set] = {}
        for e in entries:
            if ord_key(e) >= ord_key(last):
                continue
            for b in set(e["bt"]) | set(e["ext"]):
                if b not in have:
                    lost.setdefault(b, set()).add(e["label"])
        if not lost:
            continue
        touches_built = any(w in built for who in lost.values() for w in who)
        if strict and not touches_built:
            continue
        found += 1
        mark = " !!" if touches_built else ""
        print(f"### {key}  <- {last['label']} {last['pre'] or 'голое тело'} ({last['file']}){mark}")
        for b, who in sorted(lost.items()):
            print(f"      - {b:46} [{', '.join(sorted(who))}]")
    print(f"\nвсего компаний с потерями: {found}")


def report_registry(chain):
    """Главная проверка на класс LLWA.6 / GR.15: приватно владеемое здание,
    которое не попало в финансовую систему E&F и ни в одну компанию.

    E&F цепляет экономику ДВУМЯ рукописными списками по имени здания -- инжектом
    pmg_market_liquidity / pmg_private_ownership_*_stock в само здание и записью
    в private_ownership_production_stocks. Здание без первого не производит
    ликвидность и не выпускает акции; здание с группой, но без второго, навсегда
    залипает на "No Stock". Ни один из списков не работает по building_group,
    поэтому новое здание туда не попадает само.
    """
    print("\n" + "=" * 78)
    print("5. РЕЕСТРЫ: приватные здания вне экономики E&F и вне компаний")
    print("=" * 78)
    print("Считается ИТОГОВОЕ тело здания в цепочке (последнее замещающее + все")
    print("INJECT: после него). ownership_type = self, но нет pmg_market_liquidity")
    print("или нет ни одной pmg_private_ownership_* -- дыра того же класса, что LLWA.6.\n")
    allb: dict[str, list] = {}
    owners: dict[str, set] = {}
    for i, (label, _rel, data) in enumerate(chain):
        for key, entries in data["buildings"].items():
            for e in entries:
                allb.setdefault(key, []).append({**e, "i": i, "label": label})
        for _c, entries in data["companies"].items():
            for e in entries:
                for b in set(e["bt"]) | set(e["ext"]):
                    owners.setdefault(b, set()).add(label)
    rows = []
    for key, entries in sorted(allb.items()):
        reps = [e for e in entries if e["pre"] in REPLACING_PREFIXES]
        if not reps:
            continue
        last = max(reps, key=ord_key)
        pmg = set(last["pmg"])
        own = last["own"]
        for e in entries:
            if ord_key(e) > ord_key(last):
                pmg.update(e["pmg"])
                own = e["own"] or own
        if own != "self":
            continue
        no_liq = "pmg_market_liquidity" not in pmg
        no_stock = not any(p.startswith("pmg_private_ownership") for p in pmg)
        if not (no_liq or no_stock):
            continue
        rows.append((last["label"], key, no_liq, no_stock, sorted(owners.get(key, ()))))
    by_src: dict[str, list] = {}
    for src, key, nl, ns, own in rows:
        by_src.setdefault(src, []).append((key, nl, ns, own))
    for src in [l for l, _r, _d in chain if l in by_src]:
        print(f"--- итоговое тело от: {src} ({len(by_src[src])})")
        for key, nl, ns, own in by_src[src]:
            flags = []
            if nl:
                flags.append("нет ликвидности")
            if ns:
                flags.append("нет акций")
            company = ", ".join(own) if own else "НИ В ОДНОЙ КОМПАНИИ"
            print(f"    {key:46} {' + '.join(flags):32} компании: {company}")
        print()
    print(f"всего приватных зданий вне экономики E&F: {len(rows)}")


def report_builds(cfg, chain):
    print("\n" + "=" * 78)
    print("4. СБОРКИ ПРОТИВ ТОГО, ЧТО ГРУЗИТСЯ ПОСЛЕ НИХ")
    print("=" * 78)
    print("Пары, которых нет в матрице: мегапак и аддоны в блоки не входят.")
    print("Считаются не-аддитивные категории и только замещающие префиксы\nу более позднего источника: INJECT: складывается и потерей не является.\n")
    builds = set(cfg["blocks"].get("_сборки_не_блоки", []))
    idx = {rel: i for i, (_l, rel, _d) in enumerate(chain)}
    for rel in cfg["load_order"]:
        if rel not in builds or rel not in idx:
            continue
        i = idx[rel]
        label = chain[i][0]
        data = chain[i][2]
        print(f"--- {label}")
        for j in range(i + 1, len(chain)):
            other_label, _r, other = chain[j]
            hits: dict[str, list] = {}
            for cat, keys in data["defs"].items():
                if cat in ADDITIVE_CATEGORIES or cat.startswith(ADDITIVE_PREFIXES):
                    continue
                for key in keys:
                    occ = other["defs"].get(cat, {}).get(key)
                    if not occ:
                        continue
                    # INJECT:/TRY_INJECT: складывается -- это не потеря сборки
                    if all(p not in REPLACING_PREFIXES for p, _f in occ):
                        continue
                    hits.setdefault(cat, []).append(key)
            n = sum(len(v) for v in hits.values())
            if not n:
                continue
            print(f"    × {other_label}: {n} ключей")
            for cat, keys in sorted(hits.items()):
                print(f"        {cat.replace('common/','')}: {', '.join(sorted(keys)[:12])}"
                      + (" …" if len(keys) > 12 else ""))
        print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--blocks", default=os.path.join(os.path.dirname(__file__), "blocks.json"))
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--only", default="all", choices=["all", "new", "pmg", "companies", "builds", "registry"])
    ap.add_argument("--source", default=None, help="ярлык источника для раздела new")
    ap.add_argument("--strict", action="store_true",
                    help="в разделах pmg/companies показывать только потери, где пострадал "
                         "вклад сборки или компача -- то есть уже сделанная работа, а не "
                         "чужой редизайн ванильной записи")
    args = ap.parse_args()
    cfg, chain = load_chain(args.blocks, args.rebuild)
    labels = cfg.get("labels", {})
    built = {labels.get(r, os.path.basename(r)) for k, v in cfg["blocks"].items()
             if k.startswith("_сборки") or k.startswith("_чужие") for r in v}
    built.add(labels.get("../_ef/ef hotfix 1.13", "E&F hotfix"))
    print(f"цепочка: {len(chain)} источников -> " + " -> ".join(l for l, _r, _d in chain))
    if args.only in ("all", "new"):
        report_new(chain, args.source)
    if args.only in ("all", "pmg"):
        report_pmg(chain, built, args.strict)
    if args.only in ("all", "companies"):
        report_companies(chain, built, args.strict)
    if args.only in ("all", "registry"):
        report_registry(chain)
    if args.only in ("all", "builds"):
        report_builds(cfg, chain)


if __name__ == "__main__":
    main()
