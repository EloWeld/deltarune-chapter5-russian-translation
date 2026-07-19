#!/usr/bin/env python3
"""
Корректное извлечение английского текста DELTARUNE из game.ios через БАЙТКОД.

Английские дефолты собраны в генерируемых code-entry как последовательность
push "KEY"; push "VALUE"; ... (вызовы ds_map_add). Читаем операнды push.String
из байткода — это индексы в STRG, поэтому дедупликация строк НЕ ломает пары
(в отличие от наивного соседства в таблице строк).

Паттерн: в потоке push-строк, если строка == известный ключ (из lang_ja.json),
то СЛЕДУЮЩАЯ push-строка = её английское значение.

Использование:
    python3 extract_en_bytecode.py <game.ios> <lang_ja.json> <out lang_en.json>
"""
import json, struct, sys, os, collections

def chunks(d):
    pos, end, c = 8, 8 + struct.unpack_from("<I", d, 4)[0], {}
    while pos < end:
        name = d[pos:pos+4].decode("latin-1"); sz = struct.unpack_from("<I", d, pos+4)[0]
        c[name] = (pos+8, sz); pos += 8 + sz
    return c

DT_STR = 0x06
def decode_push_strings(data, bc_start, length, scount):
    """Список индексов строк в порядке инструкций push.String данного entry."""
    pos, endp, out = bc_start, bc_start + length, []
    n = len(data)
    while pos + 4 <= endp:
        op = data[pos+3]
        t1 = data[pos+2] & 0x0F
        ilen = 4
        if op in (0xC0, 0xC1, 0xC2, 0xC3):            # Push / PushLoc / PushGlb / PushBltn
            if t1 == 0x0F:                             # Int16 — операнд в самом слове
                ilen = 4
            elif t1 in (0x02, 0x05, 0x06):             # Int32 / Variable / String -> +4
                if t1 == DT_STR:
                    if pos + 8 <= n:
                        sidx = struct.unpack_from("<I", data, pos+4)[0]
                        if 0 <= sidx < scount:
                            out.append(sidx)
                ilen = 8
            elif t1 in (0x00, 0x03):                   # Double / Int64 -> +8
                ilen = 12
            else:
                ilen = 8
        elif op == 0xD9:                                # Call -> +4
            ilen = 8
        pos += ilen
    return out

def main():
    game = sys.argv[1] if len(sys.argv) > 1 else \
        "/Users/mtglitch/Library/Application Support/Steam/steamapps/common/DELTARUNE/DELTARUNE.app/Contents/Resources/chapter5_mac/game.ios"
    ja_path = sys.argv[2] if len(sys.argv) > 2 else \
        "/Users/mtglitch/Library/Application Support/Steam/steamapps/common/DELTARUNE/DELTARUNE.app/Contents/Resources/chapter5_mac/lang/lang_ja.json"
    out_path = sys.argv[3] if len(sys.argv) > 3 else \
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lang_en_ch5.json")

    ja = json.load(open(ja_path, encoding="utf-8"))
    keys_order = [k for k in ja.keys() if k != "date"]
    keyset = set(keys_order)

    data = open(game, "rb").read()
    N = len(data)
    C = chunks(data)

    # все строки STRG по индексу
    soff = C["STRG"][0]; scount = struct.unpack_from("<I", data, soff)[0]
    strings = []
    for i in range(scount):
        p = struct.unpack_from("<I", data, soff+4+i*4)[0]
        ln = struct.unpack_from("<I", data, p)[0]
        strings.append(data[p+4:p+4+ln].decode("utf-8", "replace"))

    # code entries
    co = C["CODE"][0]; ccount = struct.unpack_from("<I", data, co)[0]

    found = {}
    for i in range(ccount):
        ep = struct.unpack_from("<I", data, co+4+i*4)[0]
        length = struct.unpack_from("<I", data, ep+4)[0]
        if length == 0:
            continue
        brel = struct.unpack_from("<i", data, ep+12)[0]
        bc_start = (ep+12) + brel
        if bc_start < 0 or bc_start + length > N:
            continue
        pushes = decode_push_strings(data, bc_start, length, scount)
        for j in range(len(pushes) - 1):
            s = strings[pushes[j]]
            if s in keyset and s not in found:
                found[s] = strings[pushes[j+1]]

    out = collections.OrderedDict()
    if "date" in ja:
        out["date"] = ja["date"]
    for k in keys_order:
        if k in found:
            out[k] = found[k]

    json.dump(out, open(out_path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    got = len(found)
    missing = [k for k in keys_order if k not in found]
    suspicious = [k for k in found if found[k] in keyset]
    print(f"ключей в lang_ja:        {len(keys_order)}")
    print(f"извлечено англ. пар:     {got}  ({round(100*got/len(keys_order),1)}%)")
    print(f"пропущено:               {len(missing)}")
    print(f"подозрительных (val==ключ): {len(suspicious)}")
    if missing[:6]:
        print("примеры пропущенных:", missing[:6])
    print(f"файл: {out_path}")

if __name__ == "__main__":
    main()
