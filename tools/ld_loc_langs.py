"""ФК4: локализация форка «E&F: Ledgerdemain» на девяти языках — копия английской.

Полные локализации у форка две — русская (перевод пользователя) и английская (решение пользователя 6.10); остальные
языки — английский текст, чтобы у них не было ни пропущенных ключей, ни устаревших строк. Скрипт удаляет все .yml
языка в форке и пишет копии `localization/english/**` с заменой `_l_english` → `_l_<язык>` в имени и `l_english:`
→ `l_<язык>:` в шапке. Запускать после каждой правки английской локализации.

  python tools/ld_loc_langs.py [--fork <папка форка>]
"""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORK = ROOT / "Economic-and-Financial-Ledgerdemain-Mod"
LANGS = ("braz_por", "french", "german", "japanese", "korean", "polish", "simp_chinese", "spanish", "turkish")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fork", default=str(FORK))
    args = ap.parse_args()
    loc = Path(args.fork) / "localization"
    en = sorted(p for p in (loc / "english").rglob("*.yml"))
    for lang in LANGS:
        for p in (loc / lang).rglob("*.yml"):
            p.unlink()
        for p in en:
            rel = p.relative_to(loc / "english")
            dst = loc / lang / rel.parent / rel.name.replace("_l_english", f"_l_{lang}")
            dst.parent.mkdir(parents=True, exist_ok=True)
            raw = p.read_bytes()
            bom = raw.startswith(b"\xef\xbb\xbf")
            text = raw[3:] if bom else raw
            text = text.replace(b"l_english:", f"l_{lang}:".encode(), 1)
            dst.write_bytes((b"\xef\xbb\xbf" if bom else b"") + text)
        print(lang, len(en), "files")


if __name__ == "__main__":
    main()
