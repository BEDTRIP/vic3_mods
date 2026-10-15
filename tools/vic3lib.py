# -*- coding: utf-8 -*-
"""Чтение и запись скриптов Victoria 3 для генераторов — обёртка над пакетом `vic3tools` (`vic3tools.core.script`).

Парсер один на оба репо: здесь только прежние имена. Пакет — `../../vic3_tools` (`pip install -e ../vic3_tools`; без
установки берётся из соседней папки).
"""
import os
import sys

try:
    from vic3tools.core import script as _s
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "vic3_tools"))
    from vic3tools.core import script as _s

sha = _s.sha
entry = _s.entry
sub_names = _s.sub_names
brace_balance = _s.brace_balance
_depth0_iter = _s.depth0_iter


def read(path):
    """Текст файла без BOM, CRLF → LF; битый UTF-8 — ошибка."""
    return _s.read_text(path)


def write(path, text, bom=None):
    """bom=None — BOM, если вне комментариев есть не-ASCII (правила, раздел 11); запись через временный файл."""
    _s.write(path, text, bom=bom)


def sub(body, name, level=1):
    return _s.sub(body, name)


def sub_span(body, name, level=1):
    return _s.sub_span(body, name)


def replace_sub(body, name, new_block, level=1):
    return _s.replace_sub(body, name, new_block)


def _match_brace(s, i):
    """i — индекс '{'; индекс парной '}' (комментарии и строки не мешают)."""
    toks = _s.tokens(s, i)
    j = _s._close(toks, 0)
    if j >= len(toks):
        raise ValueError('unbalanced braces from offset %d' % i)
    return toks[j].pos
