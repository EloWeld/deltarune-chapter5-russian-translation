#!/usr/bin/env python3
"""
Дорисовывает кириллицу (из Determination) в атлас шрифта DELTARUNE, не трогая латиницу.
Вход:  fontwork/<font>.png (LA), fontwork/<font>.json (глифы, 0-based коорд.)
Выход: fontwork/<font>_new.png (расширенный атлас, LA),
       fontwork/<font>_glyphs.json (латиница без изменений + кириллица),
       fontwork/<font>_preview.png (крупное превью для глаз)

Модель верт. выравнивания GM-шрифта: у всех глифов верх рект = линия асцендера,
базовая линия на BASELINE px от верха. Кириллицу рисуем так же.
"""
import json, sys, os
from PIL import Image, ImageFont, ImageDraw

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DET_OTF = os.path.join(os.path.expanduser("~"), "determination-font", "Determination-Regular.otf")
SMALL_OTF = "/Users/mtglitch/Downloads/undertale-small-font-cyrillic/undertale-small-font-cyrillic.otf"

# codepoint-ы кириллицы: Ё, А..я, ё
CYR = [0x0401] + list(range(0x0410, 0x0450)) + [0x0451]

def find_size_for_cap(cap_px, otf):
    """Подбираем размер шрифта, чтобы высота капители ('Н') ≈ cap_px."""
    best, bestdiff = 8, 999
    for size in range(5, 60):
        f = ImageFont.truetype(otf, size)
        bbox = f.getbbox("Н")  # (l,t,r,b) чернил
        h = bbox[3] - bbox[1]
        if abs(h - cap_px) < bestdiff:
            bestdiff, best = abs(h - cap_px), size
        if h > cap_px + 4:
            break
    return best

def render_glyph(font, ch, baseline, box_h):
    """Рисует символ в рект шириной по чернилам, высотой box_h, базовая линия на baseline от верха.
    Возвращает (LA_image, ink_width, advance)."""
    ascent, descent = font.getmetrics()
    # чернильная ширина
    bbox = font.getbbox(ch)
    ink_w = max(1, bbox[2] - bbox[0])
    pad = 1
    w = ink_w + pad
    # рисуем на маске-альфе
    mask = Image.new("L", (w + 4, box_h + 8), 0)
    d = ImageDraw.Draw(mask)
    # смещаем так, чтобы левый край чернил был в x=0, базовая линия на row=baseline
    d.text((-bbox[0], baseline - ascent), ch, font=font, fill=255)
    mask = mask.crop((0, 0, w, box_h))
    # БИНАРИЗАЦИЯ: латиница строго 1-битная (0/255), убираем сглаживание
    mask = mask.point(lambda a: 255 if a >= 110 else 0)
    la = Image.merge("LA", (Image.new("L", mask.size, 255), mask))
    advance = w + 1
    return la, w, advance

def process(font_name, otf, cap_px, box_h, baseline, new_w=128, new_h=256):
    atlas = Image.open(os.path.join(BASE, "fontwork", f"{font_name}.png")).convert("LA")
    meta = json.load(open(os.path.join(BASE, "fontwork", f"{font_name}.json")))
    glyphs = list(meta["glyphs"])  # латиница — как есть

    size = find_size_for_cap(cap_px, otf)
    font = ImageFont.truetype(otf, size)

    new = Image.new("LA", (new_w, new_h), (0, 0))
    new.paste(atlas, (0, 0))

    x, y = 1, atlas.height + 2      # пакуем ниже оригинала
    step_y = box_h + 2
    added = 0
    for cp in CYR:
        ch = chr(cp)
        la, w, adv = render_glyph(font, ch, baseline, box_h)
        if x + w + 1 > new_w:
            x = 1; y += step_y
        if y + box_h > new_h:
            raise SystemExit(f"{font_name}: не влезло, увеличь new_h")
        new.paste(la, (x, y))
        glyphs.append({"char": cp, "x": x, "y": y, "w": w, "h": box_h,
                       "shift": adv, "offset": 0})
        x += w + 2
        added += 1

    # сохраняем RGBA (белый цвет + альфа-маска) — GameMaker ждёт 4 канала; LA ломается при конвертации
    a = new.split()[1]
    white = Image.new("L", new.size, 255)
    rgba = Image.merge("RGBA", (white, white, white, a))
    rgba.save(os.path.join(BASE, "fontwork", f"{font_name}_new.png"))
    json.dump({"font": font_name, "atlasW": new_w, "atlasH": new_h, "glyphs": glyphs},
              open(os.path.join(BASE, "fontwork", f"{font_name}_glyphs.json"), "w"),
              ensure_ascii=False)

    # превью 5x на сером фоне
    prev = new.convert("RGBA")
    bg = Image.new("RGBA", prev.size, (100, 100, 120, 255))
    bg.alpha_composite(prev)
    bg = bg.resize((new_w * 5, new_h * 5), Image.NEAREST)
    bg.convert("RGB").save(os.path.join(BASE, "fontwork", f"{font_name}_preview.png"))
    print(f"{font_name}: размер шрифта={size}, добавлено кириллицы={added}, атлас {new_w}x{new_h}")

if __name__ == "__main__":
    process("fnt_main",    DET_OTF,   cap_px=9,  box_h=16, baseline=13, new_w=128, new_h=256)
    process("fnt_mainbig", DET_OTF,   cap_px=18, box_h=32, baseline=26, new_w=256, new_h=512)
    process("fnt_small",   SMALL_OTF, cap_px=5,  box_h=8,  baseline=5,  new_w=128, new_h=128)
