#!/usr/bin/env python3
"""
Пайплайн ИИ-перевода DELTARUNE глава 5 (EN/JA -> RU) через Claude Sonnet.

Схема:
  source_ch5.json (ключ -> англ./яп. текст)
        │  батчинг по BATCH_SIZE
        ▼
  «сжатие»: шлём в модель ТОЛЬКО массив значений (без ключей) -> экономия токенов
        ▼
  Claude Sonnet (system-промпт кэшируется; ответ — structured JSON {translations:[...]})
        ▼
  валидация управляющих кодов (^ & % \\M \\E ...) для каждой строки
        │  битые строки -> повторный проход поштучно
        ▼
  «восстановление»: сшиваем RU-значения с ключами по индексу
        ▼
  lang_ru_trans.json  (+ checkpoint для докачки, + flagged.json для ручной проверки)

Запуск:
  export ANTHROPIC_API_KEY=...        # или `ant auth login`
  python3 translate.py                # можно прерывать и запускать снова — продолжит с места
  python3 translate.py --dry-run      # оценка объёма и стоимости без вызовов API
"""
import json, os, re, time, argparse, collections
# anthropic импортируется лениво в main() — чтобы --dry-run работал без установленного пакета

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PATH   = os.path.join(BASE, "source_ch5.json")
OUT_PATH   = os.path.join(BASE, "lang_ru_trans.json")
CKPT_PATH  = os.path.join(BASE, "translate_checkpoint.json")   # {key: ru}
FLAG_PATH  = os.path.join(BASE, "flagged.json")                # ключи, не прошедшие валидацию
PROMPT_PATH = os.path.join(BASE, "PROMPT.md")

MODEL       = "claude-sonnet-5"
BATCH_SIZE  = 40           # строк в одном запросе
MAX_TOKENS  = 8000
MAX_RETRIES = 3            # повторы всего батча при ошибке API/JSON
CACHE_TTL   = "1h"         # кэш system-промпта на час — переживает весь прогон

# ---- управляющие коды: то, что модель обязана сохранить дословно ----
CODE_RE = re.compile(r"\\[A-Za-z][A-Za-z0-9]?|\^[0-9]|[&%]|\\\\")

def code_signature(s: str):
    """Мультимножество управляющих кодов строки (для сравнения ориг. и перевода)."""
    return collections.Counter(CODE_RE.findall(s))

def codes_ok(src: str, dst: str) -> bool:
    return code_signature(src) == code_signature(dst)

# ---- структурированный вывод: гарантированный JSON-массив переводов ----
OUTPUT_FORMAT = {
    "type": "json_schema",
    "schema": {
        "type": "object",
        "properties": {
            "translations": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["translations"],
        "additionalProperties": False,
    },
}

def load_system_prompt():
    text = open(PROMPT_PATH, encoding="utf-8").read()
    # system как список блоков с кэшированием: стабильный префикс -> дешёвые повторы
    return [{"type": "text", "text": text, "cache_control": {"type": "ephemeral", "ttl": CACHE_TTL}}]

def call_model(client, system, values):
    """Один запрос: массив строк -> массив переводов той же длины."""
    user = json.dumps(values, ensure_ascii=False)
    resp = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        output_config={"format": OUTPUT_FORMAT},
        messages=[{"role": "user", "content": user}],
    )
    text = next(b.text for b in resp.content if b.type == "text")
    data = json.loads(text)
    out = data["translations"]
    usage = resp.usage
    return out, usage

def translate_batch(client, system, keys, src):
    """Переводит батч ключей, валидирует коды, поштучно чинит битые строки.
    Возвращает (result: {key: ru}, flagged: [key])."""
    values = [src[k] for k in keys]
    try:
        out, usage = call_model(client, system, values)
    except Exception as e:
        print(f"    ! ошибка запроса батча: {e}")
        return {}, list(keys), None

    if len(out) != len(values):
        print(f"    ! длина ответа {len(out)} != {len(values)} — поштучный режим")
        out = [None] * len(values)

    result, bad = {}, []
    for k, v_src, v_dst in zip(keys, values, out):
        if v_dst is not None and codes_ok(v_src, v_dst):
            result[k] = v_dst
        else:
            bad.append(k)

    # починка битых по одному (свежий контекст на строку)
    flagged = []
    for k in bad:
        fixed = None
        for _ in range(2):
            try:
                one, _u = call_model(client, system, [src[k]])
                if one and codes_ok(src[k], one[0]):
                    fixed = one[0]; break
            except Exception:
                pass
        if fixed is not None:
            result[k] = fixed
        else:
            result[k] = src[k]   # оставляем исходник, чтобы игра не сломалась
            flagged.append(k)
    return result, flagged, usage

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    src = json.load(open(SRC_PATH, encoding="utf-8"))
    keys = [k for k in src if k != "date"]

    # докачка: уже переведённые ключи из чекпоинта
    done = {}
    if os.path.exists(CKPT_PATH):
        done = json.load(open(CKPT_PATH, encoding="utf-8"))
    todo = [k for k in keys if k not in done]

    if args.dry_run:
        chars = sum(len(src[k]) for k in todo)
        approx_in = chars // 4 + len(todo) * 4
        approx_out = chars // 2                     # RU ~ дороже по токенам
        print(f"строк всего: {len(keys)} | осталось: {len(todo)}")
        print(f"символов на входе: {chars}")
        print(f"~вход {approx_in//1000}k ток, ~выход {approx_out//1000}k ток (грубо)")
        print(f"~стоимость Sonnet: ${approx_in/1e6*3 + approx_out/1e6*15:.2f} (без учёта кэша)")
        return

    import anthropic                          # ленивый импорт: нужен только для реального прогона
    client = anthropic.Anthropic()            # ключ из env или профиля `ant`
    system = load_system_prompt()

    flagged_all = json.load(open(FLAG_PATH, encoding="utf-8")) if os.path.exists(FLAG_PATH) else []
    tot_in = tot_out = tot_cache_r = 0
    t0 = time.time()

    batches = [todo[i:i+BATCH_SIZE] for i in range(0, len(todo), BATCH_SIZE)]
    for bi, batch in enumerate(batches, 1):
        res, flagged, usage = translate_batch(client, system, batch, src)
        done.update(res)
        flagged_all.extend(flagged)
        if usage is not None:
            tot_in += usage.input_tokens
            tot_out += usage.output_tokens
            tot_cache_r += getattr(usage, "cache_read_input_tokens", 0) or 0

        # чекпоинт после каждого батча
        json.dump(done, open(CKPT_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        json.dump(flagged_all, open(FLAG_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

        pct = 100 * len(done) / len(keys)
        print(f"[{bi}/{len(batches)}] переведено {len(done)}/{len(keys)} ({pct:.1f}%) "
              f"| флагов: {len(flagged_all)} | вход {tot_in//1000}k (кэш {tot_cache_r//1000}k) выход {tot_out//1000}k")

    # ---- восстановление: сборка финального lang_ru_trans.json в порядке ключей ----
    out = collections.OrderedDict()
    if "date" in src:
        out["date"] = src["date"]
    for k in keys:
        out[k] = done.get(k, src[k])
    json.dump(out, open(OUT_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    dt = time.time() - t0
    cost = tot_in/1e6*3 + tot_out/1e6*15
    print(f"\nготово за {dt/60:.1f} мин")
    print(f"токены: вход {tot_in} (из них кэш {tot_cache_r}) | выход {tot_out}")
    print(f"≈ стоимость: ${cost:.2f}")
    print(f"не прошли валидацию (оставлены исходником): {len(flagged_all)} — см. {FLAG_PATH}")
    print(f"результат: {OUT_PATH}")

if __name__ == "__main__":
    main()
