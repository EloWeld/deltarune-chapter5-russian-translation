#!/usr/bin/env python3
"""Собирает dist/ для одно-командного установщика (install.sh).

Вход (dev-машина, всё уже собрано штатным пайплайном):
  - оригинальный game.ios      (бэкап рядом с игрой, game.ios.orig.bak)
  - пропатченный game.ios      (game_patched_ch5.ios в корне репо)
  - собранный lang_ja.json     (lang_ru_trans.json рядом с игрой)

Выход: dist/game_ios.patch.bz2, dist/lang_ja.json, dist/manifest.txt

Формат патча (до bzip2) — построчный заголовок + бинарные потоки:
  DR5RU1 \n sha256(orig) \n sha256(new) \n new_len \n n_ops \n
  далее n_ops строк "C <src_off> <len>" | "E <len>",
  затем подряд: для C — len байт XOR (new ^ old[src:]), для E — len сырых байт.
Применяется perl-скриптом, вшитым в install.sh: out = old[src]^xor | extra.
Патч корректен при ЛЮБОМ разбиении на op'ы (XOR несёт точную разницу);
эвристика сдвигов влияет только на размер файла.

Запуск: python3 scripts/make_dist.py [orig] [patched] [lang]
"""
import bz2, hashlib, os, sys, time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_DIR = os.path.expanduser(
    "~/Library/Application Support/Steam/steamapps/common/DELTARUNE/"
    "DELTARUNE.app/Contents/Resources/chapter5_mac")

ORIG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(GAME_DIR, "game.ios.orig.bak")
NEW  = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BASE, "game_patched_ch5.ios")
LANG = sys.argv[3] if len(sys.argv) > 3 else os.path.join(GAME_DIR, "lang", "lang_ru_trans.json")
DIST = os.path.join(BASE, "dist")

B = 4096          # гранулярность матчера
ANCHOR = 64       # длина якоря для поиска нового сдвига
NOISE = 0.90      # доля ненулевых байт в XOR блока, выше — вставка, не сдвиг
SEG = 1 << 23     # порция при выкладке больших op'ов


def frac(a: bytes, b: bytes) -> float:
    if a == b:
        return 0.0
    x = int.from_bytes(a, "little") ^ int.from_bytes(b, "little")
    return 1 - x.to_bytes(len(a), "little").count(0) / len(a)


def build_ops(old: bytes, new: bytes):
    """Жадный матчер со сдвигом: C = копия old со сдвигом + XOR-поправка,
    E = по-настоящему новые данные (вставленные текстуры и т.п.).
    op: [kind, new_off, src_off, len]"""
    ops, i, d = [], 0, 0                      # new[i] <-> old[i-d]

    def emit(kind, src, ln):
        last = ops[-1] if ops else None
        if (last and last[0] == kind and last[1] + last[3] == i
                and (kind == "E" or last[2] + last[3] == src)):
            last[3] += ln
        else:
            ops.append([kind, i, src, ln])

    while i < len(new):
        step = min(B, len(new) - i)
        blk = new[i:i+step]
        src = i - d
        if 0 <= src and src + step <= len(old) and frac(blk, old[src:src+step]) < NOISE:
            emit("C", src, step)
        else:
            pos = old.find(new[i:i+ANCHOR]) if step >= ANCHOR else -1
            if pos != -1 and pos + step <= len(old) and frac(blk, old[pos:pos+step]) < NOISE:
                d = i - pos
                emit("C", pos, step)
            else:
                emit("E", 0, step)
        i += step
    return ops


def op_payload(op, old, new):
    """Байты бинарного потока op'а, порциями по SEG."""
    kind, noff, soff, ln = op
    for off in range(0, ln, SEG):
        n = min(ln - off, SEG)
        if kind == "E":
            yield new[noff+off : noff+off+n]
        else:
            yield (int.from_bytes(new[noff+off : noff+off+n], "little")
                   ^ int.from_bytes(old[soff+off : soff+off+n], "little")
                   ).to_bytes(n, "little")


def main():
    old, new, lang = (open(p, "rb").read() for p in (ORIG, NEW, LANG))
    sha_old, sha_new, sha_lang = (hashlib.sha256(b).hexdigest() for b in (old, new, lang))
    print(f"orig {len(old):,}  patched {len(new):,}  lang {len(lang):,}")

    t = time.time()
    ops = build_ops(old, new)
    extra = sum(o[3] for o in ops if o[0] == "E")
    print(f"op'ов: {len(ops)}, extra={extra:,} байт, матчер {time.time()-t:.1f}s")
    assert sum(o[3] for o in ops) == len(new)

    head = [b"DR5RU1", sha_old.encode(), sha_new.encode(),
            str(len(new)).encode(), str(len(ops)).encode()]
    head += [f"C {o[2]} {o[3]}".encode() if o[0] == "C" else f"E {o[3]}".encode()
             for o in ops]
    raw = bytearray(b"\n".join(head) + b"\n")
    for op in ops:
        for seg in op_payload(op, old, new):
            raw += seg

    # самопроверка: применяем патч так же, как perl в install.sh
    check = hashlib.sha256()
    cur = sum(len(h) + 1 for h in head)
    for kind, _, soff, ln in ops:
        piece = bytes(memoryview(raw)[cur:cur+ln])
        if kind == "C":
            piece = (int.from_bytes(piece, "little")
                     ^ int.from_bytes(old[soff:soff+ln], "little")
                     ).to_bytes(ln, "little")
        check.update(piece)
        cur += ln
    assert check.hexdigest() == sha_new, "патч не воспроизводит пропатченный файл"
    print("самопроверка применения: ok")

    t = time.time()
    packed = bz2.compress(bytes(raw), 9)
    print(f"патч: {len(raw):,} -> bz2 {len(packed):,} байт ({time.time()-t:.1f}s)")

    os.makedirs(DIST, exist_ok=True)
    open(os.path.join(DIST, "game_ios.patch.bz2"), "wb").write(packed)
    open(os.path.join(DIST, "lang_ja.json"), "wb").write(lang)
    with open(os.path.join(DIST, "manifest.txt"), "w") as m:
        m.write(f"""VERSION={time.strftime('%Y-%m-%d')}
GAME_ORIG_SHA256={sha_old}
GAME_PATCHED_SHA256={sha_new}
GAME_PATCHED_SIZE={len(new)}
LANG_SHA256={sha_lang}
PATCH_FILE=game_ios.patch.bz2
LANG_FILE=lang_ja.json
""")
    print(f"dist/ готов: manifest.txt, game_ios.patch.bz2, lang_ja.json")


if __name__ == "__main__":
    main()
