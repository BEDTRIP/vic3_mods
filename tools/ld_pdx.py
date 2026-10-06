"""Разбор скриптов Paradox для форка «E&F: Ledgerdemain» (ФК1): верхнеуровневые записи с точными границами в тексте.

Общий модуль для `ld_port_hotfix.py` (перенос хотфикса в тела E&F) и `ld_verify_port.py` (сверка). Ничего не пишет.

Запись: `[ДИРЕКТИВА:]ключ <оп> значение`, значение — блок `{ … }` или одно слово/строка. Границы — смещения в тексте:
`start` — начало ключа, `end` — сразу за значением; `lead` — начало комментариев над ключом (сплошные строки `#`
вплотную над ним), иначе `start`. У блока `open` / `close` — смещения `{` и `}`.
"""
import re
from dataclasses import dataclass, field

DIRECTIVES = ("REPLACE_OR_CREATE", "TRY_REPLACE", "REPLACE", "TRY_INJECT", "INJECT_OR_CREATE", "INJECT", "CREATE")
OPS = ("=", "?=", "<", ">", "<=", ">=", "!=", "==")
TOKEN = re.compile(r'#[^\n]*|"(?:[^"\\\n]|\\.)*"|[{}]|[<>!=?]=|[<>=]|[^\s{}<>!=?#"]+')


@dataclass
class Tok:
    s: str
    pos: int

    @property
    def end(self):
        return self.pos + len(self.s)


@dataclass
class Entry:
    key: str
    directive: str          # '' — без директивы
    op: str
    start: int
    end: int
    lead: int
    open: int = -1          # -1 — скаляр
    close: int = -1
    value: str = ""         # для скаляра — само значение

    @property
    def is_block(self):
        return self.open >= 0

    def text(self, src, with_lead=False):
        return src[self.lead if with_lead else self.start:self.end]

    def body(self, src):
        return src[self.open + 1:self.close] if self.is_block else self.value


def tokens(text):
    """Токены без комментариев."""
    return [Tok(m.group(0), m.start()) for m in TOKEN.finditer(text) if not m.group(0).startswith("#")]


def split_directive(key):
    if ":" in key:
        d, rest = key.split(":", 1)
        if d in DIRECTIVES:
            return d, rest
    return "", key


def _lead(text, start):
    """Начало сплошных строк-комментариев вплотную над строкой start (ключ должен начинать строку)."""
    ls = text.rfind("\n", 0, start) + 1
    if text[ls:start].strip():
        return start                       # перед ключом на той же строке что-то есть
    lead = ls
    while lead > 0:
        pe = lead - 1                      # '\n' предыдущей строки
        ps = text.rfind("\n", 0, pe) + 1
        line = text[ps:pe].strip()
        if line.startswith("#"):
            lead = ps
        else:
            break
    return lead


def parse(text):
    """Верхнеуровневые записи. Ошибки разбора (лишняя `}`, незакрытый блок) — в списке `problems`."""
    toks = tokens(text)
    entries, problems = [], []
    i, n = 0, len(toks)
    while i < n:
        t = toks[i]
        if t.s == "}":
            problems.append(f"лишняя '}}' на смещении {t.pos}")
            i += 1
            continue
        if t.s == "{":
            # безымянный блок верхнего уровня — пропустить целиком
            depth, j = 0, i
            while j < n:
                depth += (toks[j].s == "{") - (toks[j].s == "}")
                if depth == 0:
                    break
                j += 1
            problems.append(f"безымянный блок на смещении {t.pos}")
            i = j + 1
            continue
        if i + 1 < n and toks[i + 1].s in OPS:
            d, key = split_directive(t.s)
            op = toks[i + 1].s
            if i + 2 >= n:
                problems.append(f"обрыв после '{t.s} {op}'")
                break
            v = toks[i + 2]
            # значение может быть `тип {`, напр. `x = hsv { … }` / `color = rgb { }` — слово и сразу блок
            if v.s == "{" or (i + 3 < n and toks[i + 3].s == "{" and v.s not in OPS and v.s not in "{}"
                              and toks[i + 3].pos - v.end <= 1 and v.s in ("hsv", "rgb", "hsv360")):
                oi = i + 2 if v.s == "{" else i + 3
                depth, j = 0, oi
                while j < n:
                    depth += (toks[j].s == "{") - (toks[j].s == "}")
                    if depth == 0:
                        break
                    j += 1
                if j >= n:
                    problems.append(f"незакрытый блок '{t.s}' на смещении {t.pos}")
                    break
                entries.append(Entry(key, d, op, t.pos, toks[j].end, _lead(text, t.pos),
                                     toks[oi].pos, toks[j].pos))
                i = j + 1
            else:
                entries.append(Entry(key, d, op, t.pos, v.end, _lead(text, t.pos), value=v.s))
                i += 3
        else:
            problems.append(f"слово без значения '{t.s}' на смещении {t.pos}")
            i += 1
    return entries, problems


def block_items(body):
    """Поля тела блока: [(ключ|None, оп|None, Entry-подобный кортеж)] — для слияния INJECT.

    Возвращает список (key, op, start, end, is_block, open, close) по смещениям внутри body; голые слова (элементы
    списка вида `building_types = { a b }`) — key=None.
    """
    toks = tokens(body)
    out, i, n = [], 0, len(toks)
    while i < n:
        t = toks[i]
        if i + 1 < n and toks[i + 1].s in OPS and t.s not in "{}":
            v = toks[i + 2] if i + 2 < n else None
            if v is None:
                break
            if v.s == "{" or (i + 3 < n and toks[i + 3].s == "{" and v.s in ("hsv", "rgb", "hsv360")):
                oi = i + 2 if v.s == "{" else i + 3
                depth, j = 0, oi
                while j < n:
                    depth += (toks[j].s == "{") - (toks[j].s == "}")
                    if depth == 0:
                        break
                    j += 1
                out.append((t.s, toks[i + 1].s, t.pos, toks[j].end, True, toks[oi].pos, toks[j].pos))
                i = j + 1
            else:
                out.append((t.s, toks[i + 1].s, t.pos, v.end, False, -1, -1))
                i += 3
        elif t.s == "{":
            depth, j = 0, i
            while j < n:
                depth += (toks[j].s == "{") - (toks[j].s == "}")
                if depth == 0:
                    break
                j += 1
            out.append((None, None, t.pos, toks[j].end, True, t.pos, toks[j].pos))
            i = j + 1
        else:
            out.append((None, None, t.pos, t.end, False, -1, -1))
            i += 1
    return out


def norm(text):
    """Текст без комментариев и пробельной разницы — для сверки «то же самое»."""
    return " ".join(t.s for t in tokens(text))


def read(path):
    """(текст без BOM, был_ли_BOM, перевод строки файла)."""
    raw = open(path, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw[3:].decode("utf-8", errors="replace") if bom else raw.decode("utf-8", errors="replace")
    eol = "\r\n" if b"\r\n" in raw else "\n"
    return text.replace("\r\n", "\n"), bom, eol


def write(path, text, bom=True, eol="\n"):
    data = text.replace("\r\n", "\n")
    if eol != "\n":
        data = data.replace("\n", eol)
    with open(path, "wb") as f:
        f.write((b"\xef\xbb\xbf" if bom else b"") + data.encode("utf-8"))
