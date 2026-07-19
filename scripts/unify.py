#!/usr/bin/env python3
"""Унификация глоссария между чанками, переведёнными разными агентами.

Запуск без аргументов — dry-run (только отчёт). С `--write` — правит out/.

Замены, привязанные к именам (Asgore, Raly, Floradinn), применяются ТОЛЬКО к строкам,
где соответствующее слово есть в оригинале: иначе «Горей» из легитимного `Gorey`
и `Goregore` тоже попали бы под раздачу.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = json.loads((ROOT / "source_ch5.json").read_text(encoding="utf-8"))
OUT = ROOT / "out"

# Уникальные CamelCase-имена предметов и заклинаний — можно менять без оглядки
# на оригинал. Порядок важен: длинные варианты идут раньше своих подстрок.
PLAIN = [
    ("КОСОКОШМАРА", "КОШМАРОКОСЫ"),
    ("КОСОКОШМАР", "КОШМАРОКОСА"),
    ("КОШМАРКОСА", "КОШМАРОКОСА"),
    ("Кошмаркоса", "Кошмарокоса"),
    ("СапожноеМасло", "СапожМасло"),
    ("МаслоСапог", "СапожМасло"),
    ("СапМасло", "СапожМасло"),
    ("КнигаПреступника", "КнигаУлик"),
    ("КнигаВиновн", "КнигаУлик"),
    ("ШарфФлауэри", "ФлауэриШарф"),
    ("ЗелёныйФартук", "ЗелёнФартук"),
    ("ЗелФартук", "ЗелёнФартук"),
    ("ЖёлтыйЛоскут", "ЖёлтЛоскут"),
    ("КраснПятно", "КрасноеПятно"),
    ("СинНиточка", "СиняяНить"),
    ("СинНить", "СиняяНить"),
    ("ЧертежиПоезда", "ПланПоезда"),
    # lookahead: не трогать уже правильный «ПланПоезда», иначе выйдет «ПланПоездаа»
    (re.compile(r"ПланПоезд(?!а)"), "ПланПоезда"),
    ("Бретти", "Брэтти"),
    ("СНЕГОСКОРБЬ", "СТРАННЫЙ ПУТЬ"),
    ("Снегоскорбь", "Странный путь"),
]

# (регексп по переводу, замена, регексп-условие по оригиналу)
GUARDED = [
    # Asgore: и «Асгор*», и ошибочный «Горей*» → «Азгор*» с сохранением падежа
    (r"Асгор", "Азгор", r"asgore"),
    (r"Горей", "Азгор", r"asgore"),
    (r"Горея", "Азгора", r"asgore"),
    (r"Горею", "Азгору", r"asgore"),
    (r"Горее", "Азгоре", r"asgore"),
    (r"Гореем", "Азгором", r"asgore"),
    # Raly → Рэлли (несклоняемое, поглощает кривые падежи Раля/Рали/Ралю)
    (r"Рал[яию]\b|Ралей\b", "Рэлли", r"raly"),
    # Floradinn — добить одиночную «н»
    (r"Флорадин(?!н)", "Флорадинн", r"floradinn"),
]


def main():
    write = "--write" in sys.argv
    total = 0
    per_rule = {}

    for f in sorted(OUT.glob("chunk_*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        changed = False
        for k, v in data.items():
            if not isinstance(v, str):
                continue
            new = v
            for src, dst in PLAIN:
                if isinstance(src, str):
                    if src in new and src != dst:
                        per_rule[src] = per_rule.get(src, 0) + new.count(src)
                        new = new.replace(src, dst)
                else:
                    new2, n = src.subn(dst, new)
                    if n:
                        per_rule[src.pattern] = per_rule.get(src.pattern, 0) + n
                        new = new2
            en = SOURCE.get(k, "")
            for pat, dst, cond in GUARDED:
                if not re.search(cond, en, re.I):
                    continue
                new2, n = re.subn(pat, dst, new)
                if n:
                    per_rule[pat] = per_rule.get(pat, 0) + n
                    new = new2
            if new != v:
                data[k] = new
                changed = True
                total += 1
        if changed and write:
            f.write_text(
                json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8"
            )

    print("правил применено:")
    for rule, n in sorted(per_rule.items(), key=lambda x: -x[1]):
        print(f"  {n:4}  {rule}")
    print(f"\nстрок затронуто: {total}")
    print("режим:", "ЗАПИСЬ" if write else "dry-run (добавь --write)")


if __name__ == "__main__":
    main()
