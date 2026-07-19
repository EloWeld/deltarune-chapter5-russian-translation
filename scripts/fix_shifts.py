#!/usr/bin/env python3
"""
Считает правильные Shift для кириллицы в fnt_ja_*: меряет по атласу, какой зазор
(advance - чернильная ширина) у латиницы, и применяет тот же зазор к кириллице.
Выход: fontwork/ja/<font>_shift.json  {codepoint: новый shift}
"""
import json, os
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JA = os.path.join(BASE, "fontwork", "ja")
FONTS = ["fnt_ja_main", "fnt_ja_mainbig", "fnt_ja_small", "fnt_ja_8bit",
         "fnt_ja_8bit_mixed", "fnt_ja_comicsans", "fnt_ja_dotumche",
         "fnt_ja_tinynoelle", "fnt_ja_kakugo"]

def ink_width(atlas, g):
    box = atlas.crop((g["x"], g["y"], g["x"] + g["w"], g["y"] + g["h"]))
    a = box.getchannel("A")
    cols = [xx for xx in range(a.width) if any(a.getpixel((xx, yy)) > 40 for yy in range(a.height))]
    return (cols[-1] - cols[0] + 1) if cols else 0

for name in FONTS:
    atlas = Image.open(os.path.join(JA, f"{name}_new.png")).convert("RGBA")
    meta = json.load(open(os.path.join(JA, f"{name}_glyphs.json")))
    gl = {g["char"]: g for g in meta["glyphs"]}

    # средний зазор латиницы: advance(shift) - чернила, по строчным и заглавным
    lat = [c for c in list(range(65, 91)) + list(range(97, 123)) if c in gl]
    gaps = []
    for c in lat:
        iw = ink_width(atlas, gl[c])
        if iw > 0:
            gaps.append(gl[c]["shift"] - iw)
    gap = round(sum(gaps) / len(gaps))

    EXTRA = 1   # чуть свободнее латиницы: буквы Determination плотнее, впритык сливаются
    shifts = {}
    for c in [0x401] + list(range(0x410, 0x450)) + [0x451]:
        if c not in gl:
            continue
        iw = ink_width(atlas, gl[c])
        shifts[c] = max(2, iw + gap + EXTRA)
    json.dump(shifts, open(os.path.join(JA, f"{name}_shift.json"), "w"))
    sample = [shifts.get(c) for c in (0x41D, 0x43E, 0x0428)]
    print(f"{name}: латинский зазор={gap:+d}, примеры Н/о/Ш -> {sample}")
