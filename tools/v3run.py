"""Запуск команды `v3` пакета `vic3tools` из скриптов `tools/` (старые имена — обёртки над пакетом).

Пакет — `pip install -e ../vic3_tools`; без установки берётся из соседней папки `../../vic3_tools`.
"""
import os
import sys


def v3(*args):
    """Выполнить `v3 <args>`; код выхода команды."""
    try:
        from vic3tools import cli
    except ImportError:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "vic3_tools"))
        from vic3tools import cli
    return cli.main([str(a) for a in args])


HERE = os.path.dirname(os.path.abspath(__file__))
BLOCKS = os.path.join(HERE, "blocks.json")
