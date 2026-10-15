"""Разбор скриптов Paradox: верхнеуровневые записи с точными границами — обёртка над `vic3tools.core.script`.

Для `ld_port_hotfix.py`, `ld_verify_port.py` и генераторов форка. Парсер один на оба репо: здесь только прежние имена
(`write` по умолчанию с BOM, как раньше). Пакет — `../../vic3_tools`.
"""
import os
import sys

try:
    from vic3tools.core import script as _s
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "vic3_tools"))
    from vic3tools.core import script as _s

DIRECTIVES, OPS, TOKEN = _s.DIRECTIVES, _s.OPS, _s.TOKEN
Tok, Entry = _s.Tok, _s.Entry
tokens, split_directive, parse, block_items, norm = _s.tokens, _s.split_directive, _s.parse, _s.block_items, _s.norm
_lead = _s._lead


def read(path):
    """(текст без BOM, был_ли_BOM, перевод строки файла)."""
    return tuple(_s.read(path))


def write(path, text, bom=True, eol="\n"):
    _s.write(path, text, bom=bom, eol=eol)
