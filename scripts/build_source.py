#!/usr/bin/env python3
"""
Собирает единый источник для перевода главы 5:
  - где есть чистый English (извлечён из байткода) -> берём его, src="en"
  - иначе -> японский из lang_ja.json, src="ja"

Выход:
  source_ch5.json  — OrderedDict {key: text}  (в порядке lang_ja)
  source_meta.json — {key: "en"|"ja"}  + сводка
"""
import json, os, collections

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JA   = "/Users/mtglitch/Library/Application Support/Steam/steamapps/common/DELTARUNE/DELTARUNE.app/Contents/Resources/chapter5_mac/lang/lang_ja.json"
EN   = os.path.join(BASE, "lang_en_ch5.json")

ja = json.load(open(JA, encoding="utf-8"))
en = json.load(open(EN, encoding="utf-8"))
keys = [k for k in ja.keys() if k != "date"]

source = collections.OrderedDict()
meta = collections.OrderedDict()
n_en = n_ja = 0
for k in keys:
    if k in en:
        source[k] = en[k]; meta[k] = "en"; n_en += 1
    else:
        source[k] = ja[k]; meta[k] = "ja"; n_ja += 1

json.dump(source, open(os.path.join(BASE, "source_ch5.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
json.dump(meta, open(os.path.join(BASE, "source_meta.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

print(f"всего ключей: {len(keys)}")
print(f"  English: {n_en}  ({round(100*n_en/len(keys),1)}%)")
print(f"  Japanese fallback: {n_ja}  ({round(100*n_ja/len(keys),1)}%)")
print("файлы: source_ch5.json, source_meta.json")
