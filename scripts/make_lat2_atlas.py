#!/usr/bin/env python3
"""
Кириллица для оставшихся латинских шрифтов (fnt_8bit, fnt_dotumche,
fnt_comicsans, fnt_tinynoelle) — их используют экраны миниигр и пр.
Метрики меряем по чернилам 'H'; Shift кириллицы = чернила + латинский зазор + 1.
"""
import json, os
from PIL import Image, ImageFont, ImageDraw

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(BASE, "fontwork", "lat2")
DET_OTF = os.path.join(os.path.expanduser("~"), "determination-font", "Determination-Regular.otf")
SMALL_OTF = "/Users/mtglitch/Downloads/undertale-small-font-cyrillic/undertale-small-font-cyrillic.otf"

CYR = [0x0401] + list(range(0x0410, 0x0450)) + [0x0451]
FONTS = ["fnt_8bit", "fnt_dotumche", "fnt_comicsans", "fnt_tinynoelle"]

def pow2(n):
    p = 1
    while p < n: p *= 2
    return p

def ink_cols(a):
    return [xx for xx in range(a.width) if any(a.getpixel((xx, yy)) > 40 for yy in range(a.height))]

def measure_H(atlas, gl):
    g = gl[0x48]
    a = atlas.crop((g["x"], g["y"], g["x"] + g["w"], g["y"] + g["h"])).getchannel("A")
    rows = [yy for yy in range(a.height) if any(a.getpixel((xx, yy)) > 40 for xx in range(a.width))]
    return rows[-1] - rows[0] + 1, rows[-1] + 1, g["h"]

def latin_gap(atlas, gl):
    gaps = []
    for c in list(range(65, 91)) + list(range(97, 123)):
        if c not in gl: continue
        g = gl[c]
        a = atlas.crop((g["x"], g["y"], g["x"] + g["w"], g["y"] + g["h"])).getchannel("A")
        cols = ink_cols(a)
        if cols:
            gaps.append(g["shift"] - (cols[-1] - cols[0] + 1))
    return round(sum(gaps) / len(gaps))

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
    ascent, _ = font.getmetrics()
    bbox = font.getbbox(ch)
    w = max(1, bbox[2] - bbox[0]) + 1
    mask = Image.new("L", (w + 4, box_h + 8), 0)
    ImageDraw.Draw(mask).text((-bbox[0], baseline - ascent), ch, font=font, fill=255)
    mask = mask.crop((0, 0, w, box_h)).point(lambda a: 255 if a >= 110 else 0)
    return mask, w

def process(name):
    atlas = Image.open(os.path.join(DIR, f"{name}.png")).convert("RGBA")
    meta = json.load(open(os.path.join(DIR, f"{name}.json")))
    glyphs = list(meta["glyphs"])
    gl = {g["char"]: g for g in glyphs}

    cap_px, baseline, box_h = measure_H(atlas, gl)
    gap = latin_gap(atlas, gl)
    otf = SMALL_OTF if cap_px <= 6 else DET_OTF
    size = find_size_for_cap(cap_px, otf)
    font = ImageFont.truetype(otf, size)

    bottom = max(g["y"] + g["h"] for g in glyphs)
    W, H = atlas.size
    need_h = (box_h + 2) * 3 + 4
    if bottom + 2 + need_h > H:
        H = pow2(bottom + 2 + need_h)
    new = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    new.paste(atlas, (0, 0))

    x, y = 1, bottom + 2
    for cp in CYR:
        mask, w = render_glyph(font, chr(cp), baseline, box_h)
        if x + w + 1 > W:
            x = 1; y += box_h + 2
        if y + box_h > H:
            raise SystemExit(f"{name}: не влезло")
        a = mask
        cols = ink_cols(a)
        ink = (cols[-1] - cols[0] + 1) if cols else w
        white = Image.new("L", mask.size, 255)
        new.paste(Image.merge("RGBA", (white, white, white, mask)), (x, y))
        glyphs.append({"char": cp, "x": x, "y": y, "w": w, "h": box_h,
                       "shift": max(2, ink + gap + 1), "offset": 0})
        x += w + 2

    glyphs.sort(key=lambda g: g["char"])
    new.save(os.path.join(DIR, f"{name}_new.png"))
    json.dump({"font": name, "glyphs": glyphs},
              open(os.path.join(DIR, f"{name}_glyphs.json"), "w"), ensure_ascii=False)

    prev = new.crop((0, bottom, W, min(H, y + box_h + 4))).convert("RGBA")
    bg = Image.new("RGBA", prev.size, (100, 100, 120, 255))
    bg.alpha_composite(prev)
    bg = bg.resize((prev.width * 4, prev.height * 4), Image.NEAREST)
    bg.convert("RGB").save(os.path.join(DIR, f"{name}_preview.png"))
    print(f"{name}: cap={cap_px} baseline={baseline} box_h={box_h} gap={gap:+d} "
          f"otf={'small' if otf==SMALL_OTF else 'det'} size={size} атлас -> {W}x{H}")

if __name__ == "__main__":
    for n in FONTS:
        process(n)
