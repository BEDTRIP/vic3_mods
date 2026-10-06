"""ФК1: перенос хотфикса E&F в форк «E&F: Ledgerdemain» — правки вписываются в тела E&F и PSC.

Собирает результат каждый раз заново из нетронутых оригиналов (`vic3_mods_out/E&F`, `vic3_mods_out/PSC`) и хотфикса
(`_ef/ef hotfix 1.13`) и пишет в рабочее дерево форка; перезапуск даёт тот же результат. Затронутые файлы E&F/PSC
перезаписываются целиком, новые файлы — `ld_*`; прежние `ld_*`, которых нет в новом наборе, удаляются (по манифесту
`other/ld_port_manifest.txt`).

  python tools/ld_port_hotfix.py [--fork <папка форка>] [--dry]

common/ — по записям верхнего уровня (`ld_pdx.parse`), для каждого ключа хотфикса в порядке загрузки его файлов:
  • файл хотфикса по тому же пути, что файл E&F, — заменяет его целиком (как и в игре);
  • REPLACE_OR_CREATE / REPLACE / TRY_REPLACE ключа E&F или PSC — встаёт на место действующего определения; прочие
    определения того же ключа в E&F/PSC (мёртвые: REPLACE стирал их) удаляются; директива остаётся, только если ключ
    есть ещё у ванили / CMF / ETF или запись E&F сама была директивой;
  • INJECT / TRY_INJECT ключа E&F или PSC — вливается в тело: под-блок с тем же именем дополняется содержимым в конец
    (движок считает под-блок по порядку — `Правила работы с модами`, INJECT), скаляр с тем же именем заменяется,
    остальное дописывается в конец записи;
  • прочее (новые ключи, правки ванили / CMF / ETF, голые ключи on_actions) — в файл `ld_<имя>` (`zz_ef_X` → `ld_X`,
    `zz_pb_ef_X` → `ld_pb_X`), REPLACE_OR_CREATE у ключа, которого больше нигде нет, снимается.
Отчёт — `_tmp_analysis/ld_port_report.md`.
"""
import argparse
import os
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ld_pdx  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "vic3_mods_out"
EF = OUT / "E&F"
PSC = OUT / "PSC"
HF = ROOT / "vic3_mods" / "_ef" / "ef hotfix 1.13"
TR = ROOT / "vic3_mods" / "__translations" / "Economic and Financial Mod (E&F) - V4 RUS"
OTHERS = {"vanilla": OUT / ".vanillaVIC3", "cmf": OUT / "_cmf", "etf": OUT / "_etf"}
FORK = ROOT / "Economic-and-Financial-Ledgerdemain-Mod"
REPORT = ROOT / "_tmp_analysis" / "ld_port_report.md"
MANIFEST = "other/ld_port_manifest.txt"

# scripted_effects / scripted_triggers / script_values: повтор голого ключа не переопределяет — действует первое
FIRST_WINS = {"common/scripted_effects", "common/scripted_triggers", "common/script_values"}
# on_actions: одноимённые голые определения складываются движком — их не трогаем
ADDITIVE = {"common/on_actions"}
SKIP_DIRS = {"common/history", "common/defines"}
REPLACES = ("REPLACE_OR_CREATE", "REPLACE", "TRY_REPLACE")
INJECTS = ("INJECT", "TRY_INJECT", "INJECT_OR_CREATE")


GUI_TYPE = re.compile(r"^[ \t]*type\s+(\w+)\s*=", re.M)
LOC_LINE = re.compile(r'^(\s*)([\w.\-]+):(\d*)\s*"')
GENERATED = re.compile(r"GENERATED|Rebuilt by|Re-run|[Rr]egenerate|!! MAINTENANCE !!|do not edit by hand")


def strip_generated(text):
    """Шапка «сгенерировано / перегенерировать» у файла, который в форке становится исходником, — убрать."""
    lines = text.split("\n")
    i = 0
    while i < len(lines) and lines[i].lstrip().startswith("#"):
        i += 1
    head = lines[:i]
    if not any(GENERATED.search(l) for l in head):
        return text
    kept = [l for l in head if not GENERATED.search(l) and not re.search(r"tools/\w+\.py|after every E&F update", l)]
    rest = lines[i:]
    while rest and not rest[0].strip() and not kept:
        rest = rest[1:]
    return "\n".join(kept + rest)


def gui_block_end(text, pos):
    """Конец блока `type X = виджет { … }`, начиная с pos (сразу за `=`)."""
    depth = 0
    for t in ld_pdx.TOKEN.finditer(text, pos):
        s = t.group(0)
        if s.startswith("#"):
            continue
        if s == "{":
            depth += 1
        elif s == "}":
            depth -= 1
            if depth == 0:
                return t.end()
    return len(text)


def ld_name(name):
    """Имя файла хотфикса → имя нового файла форка."""
    for pre, new in (("00_00_ef_", "ld_"), ("zz_pb_ef_", "ld_pb_"), ("zz_ef_", "ld_"), ("zz_", "ld_")):
        if name.startswith(pre):
            return new + name[len(pre):]
    return "ld_" + name


def rel(p, root):
    return Path(p).relative_to(root).as_posix()


class Src:
    """Текст файла, который правим: оригинал E&F/PSC (или файл хотфикса по тому же пути) с правками по записям."""

    def __init__(self, path, mod):
        self.path, self.mod = path, mod
        self.text, self.bom, self.eol = ld_pdx.read(path)
        self.changed = False
        self._entries = None

    def entries(self):
        if self._entries is None:
            self._entries = ld_pdx.parse(self.text)[0]
        return self._entries

    def apply(self, edits):
        """edits: [(start, end, new)] по текущему тексту — применяются с конца."""
        for s, e, new in sorted(edits, key=lambda x: -x[0]):
            self.text = self.text[:s] + new + self.text[e:]
        if edits:
            self.changed = True
            self._entries = None


def indent_of(text, pos):
    ls = text.rfind("\n", 0, pos) + 1
    m = re.match(r"[ \t]*", text[ls:pos])
    return m.group(0) if m else ""


def reindent(block_text, ind):
    """Текст под-блока из хотфикса — с отступом ind (у первой строки отступа нет: она встаёт после ключа)."""
    lines = block_text.strip("\n").split("\n")
    base = min((len(re.match(r"[ \t]*", l).group(0)) for l in lines[1:] if l.strip()), default=0)
    out = [lines[0].strip()]
    for l in lines[1:]:
        out.append((ind + l[base:]) if l.strip() else "")
    return "\n".join(out)


def shift(text, ind):
    """Строки text (целиком, с их отступами) — с общим отступом ind вместо своего наименьшего; пустые убираются."""
    lines = [l.rstrip() for l in text.split("\n") if l.strip()]
    base = min(len(re.match(r"[ \t]*", l).group(0)) for l in lines)
    return "\n".join(ind + l[base:] for l in lines)


def inject_merge(src_text, target, inj_text, inj_entry):
    """Тело target (Entry в src_text) + содержимое INJECT inj_entry (в inj_text) → новый текст target (без lead)."""
    body = target.body(src_text)
    items = ld_pdx.block_items(body)
    ibody = inj_entry.body(inj_text)
    iitems = ld_pdx.block_items(ibody)
    rec_ind = indent_of(src_text, target.start) + "\t"
    edits = []          # (start, end, new) по смещениям body
    tail = []           # что дописать в конец тела
    ikeys = [it[0] for it in iitems]
    for key, op, s, e, is_block, o, c in iitems:
        piece = ibody[s:e]
        same = [it for it in items if key is not None and it[0] == key]
        # ключ-список (`entry = { }` несколько раз): новый элемент дописывается, а не вливается в последний
        listlike = len(same) > 1 or ikeys.count(key) > 1
        if key is not None and same and not listlike:
            t = same[-1]
            if is_block and t[4]:
                inner = ibody[o + 1:c]
                sub_ind = indent_of(body, t[2]) + "\t" if "\n" in body[:t[2]] else rec_ind + "\t"
                add = shift(inner, sub_ind)
                if "\n" in body[t[5]:t[6]]:
                    # многострочный под-блок: перед закрывающей скобкой
                    ls = body.rfind("\n", 0, t[6])
                    edits.append((ls, ls, "\n" + add))
                else:
                    edits.append((t[6], t[6], " " + ld_pdx.norm(inner) + " "))
            elif not is_block and not t[4]:
                edits.append((t[2], t[3], piece))
            else:
                tail.append(piece)
        else:
            tail.append(piece)
    nb = body
    for s, e, new in sorted(edits, key=lambda x: -x[0]):
        nb = nb[:s] + new + nb[e:]
    if tail:
        add = "\n".join(rec_ind + reindent(p, rec_ind) for p in tail)
        if "\n" in nb:
            nb = nb.rstrip(" \t\n") + "\n" + add + "\n" + indent_of(src_text, target.start)
        else:
            nb = nb.rstrip() + " " + " ".join(ld_pdx.norm(p) for p in tail) + " "
    head = src_text[target.start:target.open + 1]
    return head + nb + "}"


def git_format(fork, r, bom, eol):
    """BOM и перевод строки файла в git форка (копия Steam в vic3_mods_out — с CRLF, git автора — как есть)."""
    import subprocess
    res = subprocess.run(["git", "-C", str(fork), "cat-file", "-p", f"HEAD:{r}"], capture_output=True)
    if res.returncode != 0:
        return bom, eol
    raw = res.stdout
    return raw.startswith(b"\xef\xbb\xbf"), ("\r\n" if b"\r\n" in raw else "\n")


def folder_of(relpath):
    return relpath.rsplit("/", 1)[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fork", default=str(FORK))
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--force", action="store_true", help="писать, даже если форк уже правили руками")
    args = ap.parse_args()
    fork = Path(args.fork)

    # После ручных правок форка перенос их затрёт (файлы E&F собираются из оригиналов) — только до них.
    if not args.dry and not args.force:
        import subprocess
        log = subprocess.run(["git", "-C", str(fork), "log", "--format=%s", "48c3f70..HEAD"],
                             capture_output=True, text=True, encoding="utf-8").stdout.split("\n")
        foreign = [s for s in log if s.strip() and not s.startswith(("ФК0", "ФК1"))]
        if foreign:
            raise SystemExit(f"в форке есть коммиты после переноса ({foreign[0]!r} …): перенос затрёт ручные правки. "
                             f"--dry — посмотреть отчёт, --force — писать всё равно.")

    report = defaultdict(list)

    # --- файлы common/ оригиналов и хотфикса
    def common_files(root):
        out = {}
        for p in (root / "common").rglob("*.txt"):
            r = rel(p, root)
            if not any(r.startswith(s + "/") for s in SKIP_DIRS):
                out[r] = p
        return out

    ef_files, psc_files, hf_files = common_files(EF), common_files(PSC), common_files(HF)
    other_keys = defaultdict(set)              # папка → ключи ванили / CMF / ETF
    for name, root in OTHERS.items():
        for r, p in common_files(root).items():
            for e in ld_pdx.parse(ld_pdx.read(p)[0])[0]:
                other_keys[folder_of(r)].add(e.key)

    # редактируемые файлы: E&F (с подменой по тому же пути из хотфикса) и PSC
    srcs = {}
    for r, p in ef_files.items():
        if r in hf_files:
            srcs[r] = Src(hf_files[r], "hotfix-same-path")
            srcs[r].text = strip_generated(srcs[r].text)
            srcs[r].changed = True
            report["same_path"].append(r)
        else:
            srcs[r] = Src(p, "ef")
    for r, p in psc_files.items():
        srcs[r] = Src(p, "psc")

    def owners(folder, key):
        """Записи ключа в E&F/PSC в порядке загрузки: [(src_rel, Entry)]."""
        res = []
        for r in sorted((r for r in srcs if folder_of(r) == folder), key=lambda r: r.rsplit("/", 1)[1]):
            for e in srcs[r].entries():
                if e.key == key:
                    res.append((r, e))
        return res

    # записи хотфикса (кроме файлов по тому же пути), в порядке загрузки
    hf_entries = []
    for r in sorted((r for r in hf_files if r not in ef_files), key=lambda r: r.rsplit("/", 1)[1]):
        text = ld_pdx.read(hf_files[r])[0]
        for e in ld_pdx.parse(text)[0]:
            hf_entries.append((r, e))

    _hf_cache = {}

    def hf_text(r):
        if r not in _hf_cache:
            _hf_cache[r] = ld_pdx.read(hf_files[r])[0]
        return _hf_cache[r]

    # сколько раз ключ встречается в хотфиксе (для снятия REPLACE_OR_CREATE у новых)
    hf_count = defaultdict(int)
    for r, e in hf_entries:
        hf_count[(folder_of(r), e.key)] += 1

    ported = defaultdict(set)                  # hotfix rel → {start смещения перенесённых записей}
    leftover_strip = defaultdict(dict)         # hotfix rel → {start: новый текст записи} (снятая директива)
    for r, e in hf_entries:
        folder = folder_of(r)
        htext = hf_text(r)
        own = owners(folder, e.key)
        if folder in ADDITIVE and not e.directive:
            report["additive_kept"].append(f"{folder} | {e.key} | {r}")
            continue
        if not own:
            if e.directive == "REPLACE_OR_CREATE" and e.key not in other_keys[folder] and hf_count[(folder, e.key)] == 1:
                leftover_strip[r][e.start] = e.text(htext)[len("REPLACE_OR_CREATE:"):]
            cls = "vanilla" if e.key in other_keys[folder] else "new"
            report[f"leftover_{cls}"].append(f"{folder} | {e.key} | {e.directive or '-'} | {r}")
            continue
        # действующее определение E&F/PSC
        if folder in FIRST_WINS:
            plain = [o for o in own if not o[1].directive]
            eff = plain[0] if plain else own[-1]
        else:
            eff = own[-1]
        er, ee = eff
        src = srcs[er]
        if e.directive in REPLACES or (not e.directive and folder not in FIRST_WINS):
            # директива остаётся, если ключ есть у ванили / CMF / ETF или запись E&F сама была директивой
            keep_dir = bool(ee.directive) or e.key in other_keys[folder]
            new = e.text(htext)
            if e.directive and not keep_dir:
                new = new.split(":", 1)[1]
            # комментарии хотфикса над записью — вместе с ней
            lead = htext[e.lead:e.start]
            edits = defaultdict(list)
            edits[er].append((ee.start, ee.end, lead + new))
            # прочие определения того же ключа в E&F/PSC — мёртвые (REPLACE стирал их), убрать
            for orr, oe in own:
                if (orr, oe.start) != (er, ee.start):
                    edits[orr].append((oe.lead, oe.end, ""))
                    report["dead_removed"].append(f"{folder} | {e.key} | {oe.directive or '-'} | {orr}")
            for f, ed in edits.items():
                srcs[f].apply(ed)
            report["replaced"].append(f"{folder} | {e.key} | {e.directive or '-'} | {r} → {er}")
            ported[r].add(e.start)
        elif e.directive in INJECTS:
            if not ee.is_block:
                report["problem"].append(f"INJECT в скаляр: {folder} | {e.key} | {r}")
                continue
            new = inject_merge(src.text, ee, htext, e)
            src.apply([(ee.start, ee.end, new)])
            report["injected"].append(f"{folder} | {e.key} | {r} → {er}")
            ported[r].add(e.start)
        else:
            report["problem"].append(f"голый повтор ключа E&F в {folder} (не действует): {e.key} | {r} → {er}")

    # --- остатки файлов хотфикса → ld_*
    written = []
    new_files = {}
    for r, p in hf_files.items():
        if r in ef_files:
            continue
        text, bom, eol = ld_pdx.read(p)
        ents = ld_pdx.parse(text)[0]
        keep = [e for e in ents if e.start not in ported[r]]
        if not keep:
            report["file_fully_ported"].append(r)
            continue
        out = text
        for e in sorted(ents, key=lambda e: -e.start):
            if e.start in ported[r]:
                out = out[:e.lead] + out[e.end:]
            elif e.start in leftover_strip[r]:
                out = out[:e.start] + leftover_strip[r][e.start] + out[e.end:]
        out = re.sub(r"\n{3,}", "\n\n", out)
        dst = folder_of(r) + "/" + ld_name(r.rsplit("/", 1)[1])
        if dst in new_files or dst in srcs:
            report["problem"].append(f"имя {dst} занято ({r})")
            continue
        new_files[dst] = out
        report["leftover_file"].append(f"{r} → {dst} ({len(keep)} из {len(ents)} записей)")

    # --- прочие файлы: common/history, events, gfx — по тому же пути (картинки и история) или ld_* (события)
    copies = {}
    for p in HF.rglob("*"):
        r = rel(p, HF)
        if not p.is_file() or r in hf_files or not r.startswith(("common/", "events/", "gfx/")):
            continue
        if r.startswith("events/") and not (EF / r).exists():
            dst = "events/" + ld_name(p.name)
        else:
            dst = r
        copies[dst] = p
        report["copied_same_path" if (EF / r).exists() else "copied_new"].append(f"{r} → {dst}")

    # --- GUI: файл по тому же пути, что у E&F, — замена; остальные → ld_*, мёртвые определения их типов у E&F/PSC
    # удаляются (тип регистрирует первый файл по имени — `00_00_` хотфикса был нужен только ради этого)
    path_map = {}
    gui_index = defaultdict(list)                 # тип → [rel файла E&F/PSC]
    for root in (EF, PSC):
        for p in (root / "gui").rglob("*.gui"):
            r = rel(p, root)
            for m in GUI_TYPE.finditer(ld_pdx.read(p)[0]):
                gui_index[m.group(1)].append(r)
    for p in sorted((HF / "gui").rglob("*")):
        if not p.is_file():
            continue
        r = rel(p, HF)
        if (EF / r).exists():
            copies[r] = p
            report["copied_same_path"].append(f"{r} → {r}")
            continue
        if any((root / r).exists() for root in OTHERS.values()):
            dst = r                               # подменяет файл ванили / CMF / ETF по пути — путь остаётся
        else:
            dst = r.rsplit("/", 1)[0] + "/" + ld_name(p.name)
            path_map[r] = dst
        text = ld_pdx.read(p)[0]
        new_files[dst] = text
        report["gui_new_file"].append(f"{r} → {dst}")
        for t in GUI_TYPE.findall(text):
            for gr in gui_index.get(t, []):
                if gr not in srcs:
                    srcs[gr] = Src((EF if (EF / gr).exists() else PSC) / gr, "ef" if (EF / gr).exists() else "psc")
                s = srcs[gr]
                m = re.search(r"^[ \t]*type\s+" + re.escape(t) + r"\s*=", s.text, re.M)
                if not m:
                    continue
                key_pos = s.text.index("type", m.start())
                end = gui_block_end(s.text, m.end())
                s.apply([(ld_pdx._lead(s.text, key_pos), end, "")])
                report["gui_dead_type_removed"].append(f"{t} | {gr} (наш — {dst})")

    # --- локализация: ключи из replace/ — на место значения в файле E&F (русский — перевод пользователя);
    # остальное — ld_* (replace/ — тоже в replace/)
    loc_index = {}                                # (язык, ключ) → rel файла E&F
    for lang_dir in sorted((EF / "localization").iterdir()):
        lang = lang_dir.name
        base = (TR / "localization" / lang) if (lang == "russian" and (TR / "localization" / lang).exists()) else lang_dir
        for p in sorted(base.glob("*.yml")):
            r = f"localization/{lang}/{p.name}"
            for line in ld_pdx.read(p)[0].split("\n"):
                m = LOC_LINE.match(line)
                if m and (lang, m.group(2)) not in loc_index:
                    loc_index[(lang, m.group(2))] = (r, p)
    for p in sorted((HF / "localization").rglob("*.yml")):
        r = rel(p, HF)
        lang = r.split("/")[1]
        text = ld_pdx.read(p)[0]
        keep = []
        moved = 0
        for line in text.split("\n"):
            m = LOC_LINE.match(line)
            if m and "/replace/" in r and (lang, m.group(2)) in loc_index:
                orr, op = loc_index[(lang, m.group(2))]
                if orr not in srcs:
                    srcs[orr] = Src(op, "loc")
                s = srcs[orr]
                lm = re.search(r"^[ \t]*" + re.escape(m.group(2)) + r":\d*[ \t]*\".*$", s.text, re.M)
                ind = re.match(r"[ \t]*", lm.group(0)).group(0)
                s.apply([(lm.start(), lm.end(), ind + line.strip())])
                moved += 1
                report["loc_replaced"].append(f"{lang} | {m.group(2)} | {r} → {orr}")
            else:
                keep.append(line)
        if any(LOC_LINE.match(l) for l in keep):
            dst = r.rsplit("/", 1)[0] + "/" + ld_name(p.name)
            new_files[dst] = "\n".join(keep)
            report["loc_file"].append(f"{r} → {dst} ({moved} ключей вписано в E&F)")
        else:
            report["loc_file_fully_ported"].append(r)

    # пути к переименованным GUI — во всём, что пишем
    def remap(t):
        for old, new in path_map.items():
            t = t.replace(old, new)
        return t

    # --- запись
    if not args.dry:
        man = fork / MANIFEST
        old = set(man.read_text(encoding="utf-8").split()) if man.exists() else set()
        for r, p in copies.items():
            (fork / r).parent.mkdir(parents=True, exist_ok=True)
            if p.suffix in (".txt", ".gui", ".yml"):
                t, bom, eol = ld_pdx.read(p)
                ld_pdx.write(fork / r, remap(strip_generated(t)), bom, eol)
            else:
                shutil.copyfile(p, fork / r)
            written.append(r)
        for r, s in srcs.items():
            if s.changed or r in old:
                bom, eol = git_format(fork, r, s.bom, s.eol)
                ld_pdx.write(fork / r, remap(s.text), bom, eol)
                written.append(r)
        for r, t in new_files.items():
            (fork / r).parent.mkdir(parents=True, exist_ok=True)
            ld_pdx.write(fork / r, remap(t), True, "\n")
            written.append(r)
        for r in sorted(old - set(written)):
            if (fork / r).exists() and Path(r).name.startswith("ld_"):
                (fork / r).unlink()
                report["removed_stale"].append(r)
            elif r not in srcs:
                report["problem"].append(f"был в прошлом переносе, теперь не трогается и не восстановлен: {r}")
        man.write_text("\n".join(sorted(written)) + "\n", encoding="utf-8")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as o:
        o.write("# Перенос хотфикса в форк (ФК1) — отчёт `ld_port_hotfix.py`\n\n")
        for k in sorted(report):
            o.write(f"- {k}: {len(report[k])}\n")
        for k in sorted(report):
            o.write(f"\n## {k} ({len(report[k])})\n\n")
            for x in report[k]:
                o.write(f"- {x}\n")
    print({k: len(v) for k, v in sorted(report.items())})
    print(REPORT)


if __name__ == "__main__":
    main()
