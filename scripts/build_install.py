#!/usr/bin/env python3
"""
Собирает переведённые чанки в единый lang-файл и вшивает его в игру.

Итог: полный файл всех 17521 строк = русский там, где переведено (out/chunk_*.json),
и английский/японский (source_ch5.json) там, где ещё нет. Записывается на место
lang_ja.json главы 5 (с бэкапом), потому что в ванильной ch5 внешний текст грузится
только под японский язык. Оригинал сохраняется в lang_ja.json.orig.bak.

Запуск:  python3 build_install.py
"""
import json, os, re, collections, glob, shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_LANG = "/Users/mtglitch/Library/Application Support/Steam/steamapps/common/DELTARUNE/DELTARUNE.app/Contents/Resources/chapter5_mac/lang"
JA_PATH   = os.path.join(GAME_LANG, "lang_ja.json")
BAK_PATH  = os.path.join(GAME_LANG, "lang_ja.json.orig.bak")
RU_PATH   = os.path.join(GAME_LANG, "lang_ru_trans.json")   # копия для будущего/записи

# Пусто: обе строки, что тут раньше висели, починены прямо в out/ и прошли
# validate_all.py. Хардкод откатывал бы унификацию статов обратно на «АТ/ЗЩ».
FIXES = {}

# Перевод рендерится ЯПОНСКИМИ шрифтами (fnt_ja_*, режим 日本語) — в их наборе
# глифов нет « » — „ №. Подменяем на присутствующие: — -> ― (U+2015, визуально
# идентичное тире), « » „ -> ", № -> #. Эти символы не встречаются в японском
# фолбэке, поэтому замена безопасна для всех строк. Источники (out/) не трогаем —
# правка только на записи, обратима. Когда глифы появятся в шрифте — убрать карту.
GLYPH_FALLBACK = str.maketrans({"—": "―", "«": '"', "»": '"', "„": '"', "№": "#"})

CODE_RE = re.compile(r"\\[A-Za-z][A-Za-z0-9]?|\^[0-9]|[&%]|\\\\")
def sig(s): return collections.Counter(CODE_RE.findall(s))

def main():
    source = json.load(open(os.path.join(BASE, "source_ch5.json"), encoding="utf-8"))
    merged = collections.OrderedDict(source)   # порядок ключей сохраняется

    translated = 0
    skipped = []
    for f in sorted(glob.glob(os.path.join(BASE, "out", "chunk_*.json"))):
        part = json.load(open(f, encoding="utf-8"))
        for k, v in part.items():
            if k not in merged:
                continue
            if sig(source[k]) == sig(v):      # коды совпали — берём перевод
                merged[k] = v; translated += 1
            else:                              # битые коды — оставляем английский
                skipped.append(k)

    for k, v in FIXES.items():
        if k in merged:
            merged[k] = v; translated += 1
            if k in skipped: skipped.remove(k)

    # ручные override'ы (например строки меню) — применяются последними
    ovr = {}
    ovr_path = os.path.join(BASE, "out", "overrides.json")
    if os.path.exists(ovr_path):
        ovr = json.load(open(ovr_path, encoding="utf-8"))
        applied = 0
        for k, v in ovr.items():
            if k in merged:
                merged[k] = v; translated += 1; applied += 1
        print(f"override'ов применено: {applied}")

    # обрубки английского извлечения: для ~967 строк extract_en_bytecode дал "ja"
    # вместо реплики (напр. NPC с акцентным "ja"). В японском слоте такой обрубок
    # без терминатора /% вешает диалог намертво — откатываем на японский оригинал
    # (штатный fallback: «the rest falls back to the official Japanese text»).
    orig = json.load(open(BAK_PATH if os.path.exists(BAK_PATH) else JA_PATH, encoding="utf-8"))
    ja_fallback_keys = set()
    for k in merged:
        if isinstance(merged[k], str) and merged[k].strip() == "ja" \
           and isinstance(orig.get(k), str) and orig[k].strip() != "ja":
            merged[k] = orig[k]; ja_fallback_keys.add(k)
    print(f"обрубки 'ja' -> японский оригинал: {len(ja_fallback_keys)}")

    # проверка кодов по всему, что считаем переведённым
    bad = 0
    for f in sorted(glob.glob(os.path.join(BASE, "out", "chunk_*.json"))):
        for k in json.load(open(f, encoding="utf-8")):
            if k in source and k not in ja_fallback_keys and k not in ovr and sig(source[k]) != sig(merged[k]):
                bad += 1
    print(f"переведено строк: {translated}/{len(source)}  ({100*translated/len(source):.1f}%)")
    print(f"откат на английский (битые коды): {len(skipped)}  -> см. skipped.json")
    print(f"кодовых расхождений в собранном файле: {bad}  (должно быть 0)")
    json.dump(skipped, open(os.path.join(BASE, "skipped.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # date из оригинального lang_ja (orig уже загружен выше для ja-fallback)
    out = collections.OrderedDict()
    out["date"] = orig.get("date", "0")
    for k, v in merged.items():
        if k != "date":
            out[k] = v.translate(GLYPH_FALLBACK) if isinstance(v, str) else v

    # бэкап оригинала один раз
    if not os.path.exists(BAK_PATH):
        shutil.copy2(JA_PATH, BAK_PATH)
        print(f"бэкап оригинала: {BAK_PATH}")

    json.dump(out, open(JA_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(out, open(RU_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"вшито в: {JA_PATH}")
    print(f"копия:   {RU_PATH}")

if __name__ == "__main__":
    main()
