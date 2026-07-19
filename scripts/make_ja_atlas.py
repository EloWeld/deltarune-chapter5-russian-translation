#!/usr/bin/env python3
"""
Добавляет кириллицу в ЯПОНСКИЕ шрифты (fnt_ja_*) — именно их игра использует
в режиме 日本語, через который грузится наш перевод. Японские глифы сохраняем
(нужны для 1398 строк японского фолбэка).

Метрики (капитель/базовая линия) МЕРЯЕМ по чернилам глифа 'H' прямо из атласа.
Кириллицу пакуем в свободное место под последним глифом; если не влезает —
расширяем атлас вниз до следующей степени двойки.
"""
import json, os
from PIL import Image, ImageFont, ImageDraw

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JA = os.path.join(BASE, "fontwork", "ja")
DET_OTF = os.path.join(os.path.expanduser("~"), "determination-font", "Determination-Regular.otf")
SMALL_OTF = "/Users/mtglitch/Downloads/undertale-small-font-cyrillic/undertale-small-font-cyrillic.otf"

CYR = [0x0401] + list(range(0x0410, 0x0450)) + [0x0451]
FONTS = ["fnt_ja_main", "fnt_ja_mainbig", "fnt_ja_small", "fnt_ja_8bit",
         "fnt_ja_8bit_mixed", "fnt_ja_comicsans", "fnt_ja_dotumche",
         "fnt_ja_tinynoelle", "fnt_ja_kakugo"]

def pow2(n):
    p = 1
    while p < n: p *= 2
    return p

def measure_H(atlas, glyphs):
    """Чернила глифа 'H' → (cap_px, baseline, box_h)."""
    g = next(x for x in glyphs if x["char"] == 0x48)
    box = atlas.crop((g["x"], g["y"], g["x"] + g["w"], g["y"] + g["h"]))
    a = box.getchannel("A")
    rows = [yy for yy in range(a.height) if any(a.getpixel((xx, yy)) > 40 for xx in range(a.width))]
    top, bot = rows[0], rows[-1]
    return bot - top + 1, bot + 1, g["h"]

def find_size_for_cap(cap_px, otf):
    best, bestdiff = 8, 999
    for size in range(5, 90):
        f = ImageFont.truetype(otf, size)
        b = f.getbbox("Н")
        h = b[3] - b[1]
        if abs(h - cap_px) < bestdiff:
            bestdiff, best = abs(h - cap_px), size
        if h > cap_px + 6:
            break
    return best

def render_glyph(font, ch, baseline, box_h):
    ascent, descent = font.getmetrics()
    bbox = font.getbbox(ch)
    ink_w = max(1, bbox[2] - bbox[0])
    w = ink_w + 1
    mask = Image.new("L", (w + 4, box_h + 8), 0)
    d = ImageDraw.Draw(mask)
    d.text((-bbox[0], baseline - ascent), ch, font=font, fill=255)
    mask = mask.crop((0, 0, w, box_h))
    mask = mask.point(lambda a: 255 if a >= 110 else 0)
    return mask, w, w + 1

def process(name):
    atlas = Image.open(os.path.join(JA, f"{name}.png")).convert("RGBA")
    meta = json.load(open(os.path.join(JA, f"{name}.json")))
    glyphs = list(meta["glyphs"])

    cap_px, baseline, box_h = measure_H(atlas, glyphs)
    otf = SMALL_OTF if cap_px <= 6 else DET_OTF
    size = find_size_for_cap(cap_px, otf)
    font = ImageFont.truetype(otf, size)

    # свободное место: ниже самого нижнего глифа
    bottom = max(g["y"] + g["h"] for g in glyphs)
    need_h = (box_h + 2) * 2 + 4          # с запасом на 2 ряда
    W, H = atlas.size
    if bottom + 2 + need_h <= H:
        new = atlas.copy()
    else:
        H2 = pow2(bottom + 2 + need_h)
        new = Image.new("RGBA", (W, H2), (0, 0, 0, 0))
        new.paste(atlas, (0, 0))
        H = H2

    x, y = 1, bottom + 2
    added = 0
    for cp in CYR:
        mask, w, adv = render_glyph(font, chr(cp), baseline, box_h)
        if x + w + 1 > W:
            x = 1; y += box_h + 2
        if y + box_h > H:
            raise SystemExit(f"{name}: не влезло даже после расширения")
        white = Image.new("L", mask.size, 255)
        new.paste(Image.merge("RGBA", (white, white, white, mask)), (x, y))
        glyphs.append({"char": cp, "x": x, "y": y, "w": w, "h": box_h,
                       "shift": adv, "offset": 0})
        x += w + 2
        added += 1

    glyphs.sort(key=lambda g: g["char"])   # ВАЖНО: список глифов должен быть отсортирован
    new.save(os.path.join(JA, f"{name}_new.png"))
    json.dump({"font": name, "atlasW": new.width, "atlasH": new.height, "glyphs": glyphs},
              open(os.path.join(JA, f"{name}_glyphs.json"), "w"), ensure_ascii=False)

    # превью зоны кириллицы
    prev = new.crop((0, bottom, W, min(new.height, y + box_h + 4))).convert("RGBA")
    bg = Image.new("RGBA", prev.size, (100, 100, 120, 255))
    bg.alpha_composite(prev)
    scale = 3 if prev.width <= 1024 else 2
    bg = bg.resize((prev.width * scale, prev.height * scale), Image.NEAREST)
    bg.convert("RGB").save(os.path.join(JA, f"{name}_preview.png"))

    print(f"{name}: cap={cap_px} baseline={baseline} box_h={box_h} "
          f"otf={'small' if otf==SMALL_OTF else 'det'} size={size} "
          f"атлас {atlas.width}x{atlas.height} -> {new.width}x{new.height}, кириллицы {added}")

if __name__ == "__main__":
    for n in FONTS:
        process(n)
