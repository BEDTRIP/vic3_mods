# -*- coding: utf-8 -*-
"""Shared helpers for reading Victoria 3 script files.

Everything here is byte-level plumbing on purpose: the generators below build
merged database entries out of other people's files, and a merge that silently
re-indents or drops a BOM makes the next re-diff against an updated foreign mod
unreadable.  See "Правила работы с модами Victoria 3", section 11.
"""
import os, re, hashlib

def read(path):
    """Read a game script file, strip BOM, normalise CRLF -> LF.

    Foreign mods are inconsistent about both; normalising here means every
    diff/merge below compares content rather than line endings.
    """
    with open(path, 'rb') as f:
        b = f.read()
    if b[:3] == b'\xEF\xBB\xBF':
        b = b[3:]
    return b.decode('utf-8').replace('\r\n', '\n')

def sha(text):
    return hashlib.sha256(re.sub(r'\s+', ' ', text).strip().encode('utf-8')).hexdigest()[:12]

def _match_brace(s, i):
    """i points at '{'; return index of the matching '}'."""
    d = 0
    for j in range(i, len(s)):
        c = s[j]
        if c == '{':
            d += 1
        elif c == '}':
            d -= 1
            if d == 0:
                return j
    raise ValueError('unbalanced braces from offset %d' % i)

def entry(text, key, prefix=None):
    """Return (whole_declaration, body_without_outer_braces) for a top-level key.

    prefix, when given, must match exactly ('INJECT:', 'REPLACE:', ...);
    when None, any prefix or none is accepted.
    """
    pat = (re.escape(prefix) if prefix else r'(?:[A-Z_]+:)?')
    m = re.search(r'(?m)^[ \t]*' + pat + re.escape(key) + r'\s*=\s*\{', text)
    if not m:
        raise KeyError('%s not found (prefix=%r)' % (key, prefix))
    i = text.index('{', m.start())
    j = _match_brace(text, i)
    return text[m.start():j + 1], text[i + 1:j]

def _depth0_iter(body):
    """Yield (name, start, brace_open, brace_close) for statements at depth 0 of a body."""
    d = 0
    i = 0
    n = len(body)
    while i < n:
        c = body[i]
        if c == '#':
            j = body.find('\n', i)
            i = n if j < 0 else j + 1
            continue
        if c == '"':
            j = body.find('"', i + 1)
            i = n if j < 0 else j + 1
            continue
        if c == '{':
            d += 1
            i += 1
            continue
        if c == '}':
            d -= 1
            i += 1
            continue
        if d == 0:
            m = re.compile(r'([A-Za-z_][A-Za-z_0-9]*)\s*=\s*\{').match(body, i)
            if m:
                j = _match_brace(body, m.end() - 1)
                yield (m.group(1), m.start(), m.end() - 1, j)
                i = j + 1
                continue
        i += 1


def sub(body, name, level=1):
    """Text of the sub-block `name = { ... }` at depth 0 of `body`, braces included.

    Indentation-agnostic on purpose: Hail, Columbia! indents with spaces and
    Morgenroete with tabs, and a merge that depends on which one is a merge that
    breaks on the next foreign update.
    """
    for nm, a, o, c in _depth0_iter(body):
        if nm == name:
            return body[o:c + 1]
    return None


def sub_span(body, name, level=1):
    """(start, end) covering the whole `name = { ... }` statement at depth 0."""
    for nm, a, o, c in _depth0_iter(body):
        if nm == name:
            return (a, c + 1)
    return None


def sub_names(body):
    return [nm for nm, a, o, c in _depth0_iter(body)]


def replace_sub(body, name, new_block, level=1):
    """Swap one sub-block's body for another. new_block includes braces."""
    for nm, a, o, c in _depth0_iter(body):
        if nm == name:
            return body[:o] + new_block + body[c + 1:]
    raise KeyError('sub-block %s not found' % name)


def write(path, text, bom=None):
    """Write a game file.

    bom=None decides automatically: a BOM is required when the file contains a
    non-ASCII byte outside a comment (section 11 of the rules); pure ASCII files
    are written without one so byte-for-byte copies of foreign files stay
    byte-for-byte.  Writes to a temporary file first: io.open truncates before it
    validates its arguments, and a 2282-line generator was once zeroed that way.
    """
    if bom is None:
        bom = any(ord(ch) > 127 for line in text.split('\n')
                  for ch in line.split('#')[0])
    data = ('﻿' if bom else '') + text
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(data)
    os.replace(tmp, path)

def brace_balance(text):
    n = 0
    for line in text.split('\n'):
        line = line.split('#')[0]
        n += line.count('{') - line.count('}')
    return n
