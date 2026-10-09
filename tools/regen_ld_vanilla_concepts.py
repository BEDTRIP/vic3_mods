"""Ванильные понятия игры (Vickypedia, подсказки-понятия) — граф заметок `ваниль/` форка «E&F: Ledgerdemain».

    py tools/regen_ld_vanilla_concepts.py [--vanilla <game>] [--fork <путь>] [--lang russian] [--check]

Источник — ваниль: `common/game_concepts/*.txt` (ключи понятий) и вся локализация `localization/<язык>/` (текст, имена
законов, зданий, типов населения, на которые ссылаются подсказки) плюс английская — для синонимов. Пишет по заметке на
понятие: `ваниль/<имя понятия>.md` — имя, синонимы (формы имени, английское, ключ), описание из игры; ссылки
`[Concept('concept_x', 'текст')]`, `[concept_x]`, `$concept_x$` — вики-ссылками `[[Имя|текст]]`. Формы одного понятия
(`concept_radicals`, `concept_radicalism`) — синонимы заметки `concept_radical`. Имя, совпавшее с заметкой мода
(`понятия/`), получает « (ваниль)». Плюс `ваниль/_Карта ванили.md`. Руками заметки не править — правится генератор.

Два графа заметок форка: `понятия/` (мод) и `ваниль/` (игра) — заметки мода ссылаются на ванильные там, где механика
мода стоит на механике игры (принцип 14).

`--check` — только сравнить, код выхода 1 при расхождении. Ваниль по умолчанию — первая найденная: `vic3_mods_out/
.vanillaVIC3(/game)` рядом с репо (на ПК и в worktree моста), установленная игра.
"""
import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOC_LINE = re.compile(r'^\s*([A-Za-z0-9_.\-]+):\d*\s*"(.*)"\s*(#.*)?$')
BAD_NAME = re.compile(r'[\\/:*?"<>|#^\[\]]')


def load_loc(folder):
    loc = {}
    for dp, dn, fn in os.walk(folder):
        dn.sort()
        for f in sorted(fn):
            if not f.endswith(".yml"):
                continue
            with open(os.path.join(dp, f), encoding="utf-8-sig", errors="replace") as fh:
                for line in fh:
                    m = LOC_LINE.match(line)
                    if m and m.group(1) not in loc:
                        loc[m.group(1)] = m.group(2)
    return loc


def load_concepts(folder):
    keys = []
    for f in sorted(os.listdir(folder)):
        if f.endswith(".txt"):
            with open(os.path.join(folder, f), encoding="utf-8-sig") as fh:
                for line in fh:
                    m = re.match(r"^(concept_\w+)\s*=", line)
                    if m and m.group(1) not in keys:
                        keys.append(m.group(1))
    return keys


class Gen:
    def __init__(self, concepts, loc, en, mod_names):
        self.concepts = concepts
        self.cset = set(concepts)
        self.loc, self.en = loc, en
        self.base_cache = {}
        self.nolink = 0
        self.names = {}
        used = {}
        for c in concepts:
            name = self.clean_name(loc.get(c) or en.get(c) or c)
            if name in mod_names:
                name += " (ваниль)"
            if name in used:
                name = f"{name} ({c[len('concept_'):]})"
            used[name] = c
            self.names[c] = name

    @staticmethod
    def clean_name(s):
        s = re.sub(r"#\w+(;\w+)*\s?|#!|@\w+!", "", s)
        s = re.sub(r"\[[^\]]*\]|\$[^$]*\$", "", s)
        s = BAD_NAME.sub("", s).strip(" .")
        return s or "?"

    def base(self, key):
        """The concept a localization key is a form of: concept_radicals -> concept_radical."""
        if key in self.base_cache:
            return self.base_cache[key]
        best = None
        if key in self.cset:
            best = key
        else:
            for c in self.concepts:
                if key.startswith(c) and (best is None or len(c) > len(best)):
                    best = c
        self.base_cache[key] = best
        return best

    @staticmethod
    def low(s, fmt):
        """`|l` in a game text call — lowercase first letter."""
        return s[:1].lower() + s[1:] if fmt and "l" in fmt else s

    def link(self, key, text=None, fmt=None):
        c = self.base(key)
        if not c:
            return text or self.loc.get(key, key)
        name = self.names[c]
        shown = text if text is not None else self.loc.get(key) or name
        shown = self.clean_name(self.plain(shown) if self.nolink < 4 else shown) if shown else name
        shown = self.low(shown, fmt)
        if self.nolink:
            return shown
        self.ph.append(f"[[{name}]]" if shown == name else f"[[{name}|{shown}]]")
        return f"\x00{len(self.ph) - 1}\x00"

    def plain(self, s, depth=3):
        """Game text without links — for link captions and names."""
        self.nolink += 1
        try:
            return self.conv(s, depth)
        finally:
            self.nolink -= 1

    def game_name(self, key, depth=3):
        v = self.loc.get(key) or self.en.get(key)
        if not v:
            return key
        return self.clean_name(self.plain(v, depth + 1) if depth < 6 else v)

    def conv(self, s, depth=0):
        """Game text -> markdown; links are kept as placeholders until the outermost call returns."""
        outer = depth == 0
        if outer:
            self.ph = []
        s = s.replace("\\n", "\n").replace('\\"', '"')
        s = re.sub(r"\n?\$EFFECT_LIST_BULLET\$", "\n- ", s)
        s = re.sub(r"\n?#indent_newline(:\d+)?\s*", "\n", s)
        s = re.sub(r"#tooltip:\S*\s?", "", s)
        s = s.replace("[Nbsp]", " ")
        # [Concept('concept_x', 'text')|fmt]
        s = re.sub(r"\[Concept\(\s*'(concept_\w+)'\s*,\s*'([^']*)'\s*\)(\|[^\]]*)?\]",
                   lambda m: self.link(m.group(1), m.group(2), m.group(3)), s)
        s = re.sub(r"\[(concept_\w+)(\|\w+)?\]", lambda m: self.link(m.group(1), None, m.group(2)), s)
        s = re.sub(r"\$(concept_\w+)(\|\w+)?\$", lambda m: self.link(m.group(1)), s)
        s = re.sub(r"\[GetDefine\('(\w+)',\s*'(\w+)'\)(\|[^\]]*)?\]", r"`\1.\2`", s)
        # [SelectLocalization(GetPlayer.IsValid, 'KEY_IF_PLAYER', 'key_or_text')|fmt] — the text without a player
        s = re.sub(r"\[SelectLocalization\([^,]+,\s*'\w+',\s*'([^']+)'\)(\|[^\]]*)?\]",
                   lambda m: self.low(self.game_name(m.group(1), depth), m.group(2)), s)
        s = re.sub(r"\[AddLocalizationIf\([^,]+,\s*'(\w+)'\)\]",
                   lambda m: self.conv(self.loc[m.group(1)], depth + 1) if depth < 6 and m.group(1) in self.loc else "",
                   s)
        s = re.sub(r"\[Get\w+\('(\w+)'[^\]|]*(\|[^\]]*)?\]",
                   lambda m: self.low(self.game_name(m.group(1), depth), m.group(2)), s)

        def key(m):
            k = m.group(1)
            if depth < 6 and k in self.loc:
                return self.conv(self.loc[k], depth + 1)
            return k
        s = re.sub(r"\$([A-Za-z0-9_]+)(\|\w+)?\$", key, s)
        s = re.sub(r"\[[^\[\]]*\]", lambda m: f"`{m.group(0)[1:-1]}`", s)
        s = re.sub(r"#(v|b|bold|title) ([^#]*)#!", r"**\2**", s)
        s = re.sub(r"#(i|italic) ([^#]*)#!", r"*\2*", s)
        s = re.sub(r"#\w+([;:]\S*)?\s?", "", s).replace("#!", "")
        s = re.sub(r"@\w+!", "", s)
        s = re.sub(r"^\s*[•·]\s*", "- ", s, flags=re.M)
        s = re.sub(r"(?<=\S) {2,}", " ", s)
        s = re.sub(r"[ \t]+$", "", s, flags=re.M)
        if outer:
            while "\x00" in s:
                s = re.sub(r"\x00(\d+)\x00", lambda m: self.ph[int(m.group(1))], s)
        return s.strip()

    def aliases(self, c):
        al = []
        for k, v in self.loc.items():
            if k.startswith(c) and not k.endswith("_desc") and self.base(k) == c and k != c:
                n = self.clean_name(v)
                if n and n != self.names[c] and n not in al and len(n) < 60:
                    al.append(n)
        en = self.clean_name(self.en.get(c, ""))
        if en and en != "?" and en not in al:
            al.append(en)
        al.append(c)
        return al

    def note(self, c):
        name = self.names[c]
        desc = self.loc.get(c + "_desc") or self.en.get(c + "_desc") or ""
        al = ", ".join('"' + a.replace('"', "'") + '"' for a in self.aliases(c))
        body = self.conv(desc) if desc else "_Описания в игре нет._"
        return (f"---\naliases: [{al}]\ntags: [ваниль]\nsource: игра, `{c}` (tools/regen_ld_vanilla_concepts.py)\n---\n"
                f"# {name}\n\n{body}\n")

    def index(self):
        rows = sorted(self.concepts, key=lambda c: self.names[c].lower())
        out = ["---", "tags: [ваниль, карта]", "---", "# Карта ванили",
               "",
               "Понятия игры — подсказки-понятия Victoria 3 1.13 (`common/game_concepts`, локализация), по заметке на понятие.",
               "Сгенерировано `../vic3_mods/tools/regen_ld_vanilla_concepts.py` — руками не править. Понятия мода — [[_Карта понятий]];",
               "заметки мода ссылаются на ванильные там, где механика мода стоит на механике игры.", ""]
        letter = None
        for c in rows:
            n = self.names[c]
            first = n[:1].upper()
            if first != letter:
                letter = first
                out += ["", f"## {letter}", ""]
            out.append(f"- [[{n}]]")
        return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vanilla", default=None)
    ap.add_argument("--fork", default=str(ROOT / "Economic-and-Financial-Ledgerdemain-Mod"))
    ap.add_argument("--lang", default="russian")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    cands = [Path(a.vanilla)] if a.vanilla else [ROOT / "vic3_mods_out" / ".vanillaVIC3" / "game",
                                                 ROOT / "vic3_mods_out" / ".vanillaVIC3",
                                                 Path(r"C:\games\steam\steamapps\common\Victoria 3\game")]
    van = next((c for c in cands if (c / "common" / "game_concepts").is_dir()), cands[0])
    fork = Path(a.fork)
    concepts = load_concepts(van / "common" / "game_concepts")
    loc = load_loc(van / "localization" / a.lang)
    en = load_loc(van / "localization" / "english")
    mod = fork / "понятия"
    mod_names = {f[:-3] for f in os.listdir(mod) if f.endswith(".md")} if mod.is_dir() else set()
    g = Gen(concepts, loc, en, mod_names)
    out = {f"{g.names[c]}.md": g.note(c) for c in concepts}
    out["_Карта ванили.md"] = g.index()
    dst = fork / "ваниль"
    have = {f for f in os.listdir(dst) if f.endswith(".md")} if dst.is_dir() else set()
    changed = [f for f, t in out.items() if not (dst / f).is_file() or (dst / f).read_text(encoding="utf-8") != t]
    stale = sorted(have - set(out))
    print(f"regen_ld_vanilla_concepts: понятий {len(concepts)}, локализация {len(loc)} ключей; "
          f"изменено {len(changed)}, лишних {len(stale)}")
    if a.check:
        sys.exit(1 if changed or stale else 0)
    dst.mkdir(exist_ok=True)
    for f in changed:
        (dst / f).write_text(out[f], encoding="utf-8", newline="\n")
    for f in stale:
        (dst / f).unlink()


if __name__ == "__main__":
    main()
