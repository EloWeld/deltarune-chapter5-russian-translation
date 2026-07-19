#!/usr/bin/env python3
"""Сводная валидация переведённых чанков против source_ch5.json.

Считает управляющие коды с фиксированной длиной (backslash + буква-тип + один
символ-аргумент), поэтому не склеивает код со следующим за ним словом — в отличие
от check_codes.py, который жадно проглатывал `\\cYYellow` целиком.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source_ch5.json"
OUT = ROOT / "out"

# \M1 \E0 \cY \C1 \T4 \F0 \V2 \O1 \I3 — тип + один символ аргумента
BACKSLASH_CODE = re.compile(r"\\([A-Za-z])(.)")
# одиночные управляющие символы
SINGLES = "^&%#~/"


def codes(s):
    """Мультимножество управляющих кодов строки."""
    c = Counter()
    for m in BACKSLASH_CODE.finditer(s):
        c["\\" + m.group(1) + m.group(2)] += 1
    # затираем распознанные backslash-коды, чтобы их аргументы
    # (например `%` в `\M%`) не посчитались повторно как одиночные
    stripped = BACKSLASH_CODE.sub("", s)
    for ch in stripped:
        if ch in SINGLES:
            c[ch] += 1
    return c


def main():
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    translated = {}
    dup_keys = []

    for f in sorted(OUT.glob("chunk_*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        for k, v in data.items():
            if k in translated:
                dup_keys.append((k, f.name))
            translated[k] = (v, f.name)

    missing = [k for k in source if k not in translated]
    extra = [k for k in translated if k not in source]

    mismatches = []
    untranslated = []
    for k, (val, fname) in translated.items():
        if k not in source:
            continue
        orig = source[k]
        if not isinstance(val, str) or not isinstance(orig, str):
            continue
        if codes(orig) != codes(val):
            diff = codes(orig) - codes(val), codes(val) - codes(orig)
            mismatches.append((fname, k, diff))
        # строка не тронута переводчиком, хотя содержит латиницу и не плейсхолдер
        if val == orig and re.search(r"[A-Za-z]{4,}", orig) and orig.strip() not in ("ja", ""):
            untranslated.append((fname, k))

    print(f"ключей в source:      {len(source)}")
    print(f"ключей в out:         {len(translated)}")
    print(f"дубликаты ключей:     {len(dup_keys)}")
    print(f"не покрыто переводом: {len(missing)}")
    print(f"лишние ключи:         {len(extra)}")
    print(f"расхождения по кодам: {len(mismatches)}")
    print(f"похоже не переведено: {len(untranslated)}")

    for k, fname in dup_keys[:20]:
        print(f"  DUP  {fname}  {k}")
    for k in missing[:20]:
        print(f"  MISS {k}")
    for fname, k, (lost, added) in mismatches[:60]:
        print(f"  CODE {fname}  {k}  потеряно={dict(lost)} лишнее={dict(added)}")
    if len(mismatches) > 60:
        print(f"  … ещё {len(mismatches) - 60}")

    return 1 if (missing or mismatches or dup_keys) else 0


if __name__ == "__main__":
    sys.exit(main())
