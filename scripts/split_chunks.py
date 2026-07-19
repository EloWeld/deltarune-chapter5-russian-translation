#!/usr/bin/env python3
"""Режет source_ch5.json на чанки для перевода субагентами."""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "source_ch5.json")
CH_DIR = os.path.join(BASE, "chunks")
OUT_DIR = os.path.join(BASE, "out")
SIZE = 120

os.makedirs(CH_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

src = json.load(open(SRC, encoding="utf-8"))
keys = [k for k in src if k != "date"]

n = 0
for i in range(0, len(keys), SIZE):
    part = keys[i:i+SIZE]
    obj = {k: src[k] for k in part}
    idx = i // SIZE
    json.dump(obj, open(os.path.join(CH_DIR, f"chunk_{idx:03d}.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    n += 1

print(f"строк: {len(keys)} | чанков: {n} (по {SIZE}) | дир: {CH_DIR}")
