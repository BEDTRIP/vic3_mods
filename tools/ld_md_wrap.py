"""Перенос строк заметок форка (`понятия/`, разделы форка в `ваниль/`, `docs/`) по 120 знаков: абзацы и пункты
списков; вики-ссылка `[[…]]` и код в обратных кавычках не разрываются — ссылка через перенос строки в Obsidian не
работает. Таблицы, заголовки, frontmatter, блоки кода, пустые строки — как есть. В заметке `ваниль/` переносится
только раздел «### Как используется в форке» — текст игры генератор держит одной строкой на абзац. Раздел
«## Подсказка» заметки понятия не переносится, а склеивается: абзац и пункт списка — одной строкой, как текст
подсказки в игре.

    py tools/ld_md_wrap.py <файл.md>...
"""
import re
import sys

W = 120
ITEM = re.compile(r"^(\s*)(- |\d+\. )")


def tokens(text):
    """Split on spaces outside [[links]] and `code`."""
    out, cur, link, code, i = [], "", False, False, 0
    while i < len(text):
        c = text[i]
        if not code and text.startswith("[[", i):
            link = True
        elif not code and link and text.startswith("]]", i):
            link = False
        elif c == "`" and not link:
            code = not code
        if c == " " and not link and not code:
            if cur:
                out.append(cur)
            cur = ""
        else:
            cur += c
        i += 1
    if cur:
        out.append(cur)
    return out


def wrap(words, first, rest):
    out, cur, empty = [], first, True
    for w in words:
        if not empty and len(cur) + 1 + len(w) > W:
            out.append(cur)
            cur = rest + w
        else:
            cur = cur + w if empty else cur + " " + w
        empty = False
    out.append(cur)
    return out


def flush(block, out, join=False):
    if not block:
        return
    m = ITEM.match(block[0])
    if m:
        first = m.group(1) + m.group(2)
        rest = " " * len(first)
        text = " ".join(l.strip() for l in block)[len(first.strip()):].strip()
    else:
        first = rest = re.match(r"^\s*", block[0]).group(0)
        text = " ".join(l.strip() for l in block)
    out += [first + text] if join else wrap(tokens(text), first, rest)


def main():
    for path in sys.argv[1:]:
        text = open(path, encoding="utf-8").read()
        keep = ""
        if text.startswith("---\nalias") and "\nsource: игра," in text:
            i = text.find("\n### Как используется в форке")
            if i < 0:
                continue
            keep, text = text[:i + 1], text[i + 1:]
        lines = text.split("\n")
        out, block, fm, fence, tip = [], [], 0, False, False
        for i, l in enumerate(lines):
            if i == 0 and l == "---":
                fm = 1
                out.append(l)
                continue
            if fm == 1:
                out.append(l)
                if l == "---":
                    fm = 2
                continue
            if l.startswith("```"):
                flush(block, out); block = []
                fence = not fence
                out.append(l)
                continue
            if fence or not l.strip() or l.lstrip().startswith(("|", "#")):
                flush(block, out, tip); block = []
                if l.startswith("## "):
                    tip = l == "## Подсказка"
                out.append(l)
                continue
            if ITEM.match(l):
                flush(block, out, tip); block = []
            block.append(l)
        flush(block, out, tip)
        open(path, "w", encoding="utf-8", newline="\n").write(keep + "\n".join(out))


if __name__ == "__main__":
    main()
