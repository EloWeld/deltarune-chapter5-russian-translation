# DELTARUNE Chapter 5 Russian Translation — Русификатор DELTARUNE (глава 5)

![DELTARUNE](https://img.shields.io/badge/DELTARUNE-Chapter%205-black)
![Translation](https://img.shields.io/badge/translation-100%25-brightgreen)
![Fonts](https://img.shields.io/badge/cyrillic%20fonts-13%2F13-brightgreen)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-blue)
![Status](https://img.shields.io/badge/status-beta-blue)

**EN**: A fan-made Russian localization toolkit for DELTARUNE Chapter 5 — game text translation plus Cyrillic font injection for the GameMaker data file. Applies on top of your own legal Steam copy.

**RU**: Фанатский русификатор DELTARUNE Chapter 5 — перевод текста игры и кириллические шрифты, вшиваемые прямо в игру. Ставится поверх вашей лицензионной Steam-копии. [Перейти к русской версии](#русская-версия).

---

## English

### About

- Game: [DELTARUNE](https://store.steampowered.com/app/1671210/DELTARUNE/) by Toby Fox. Chapter 5 shipped in 2026 with no official Russian localization.
- Translation is AI-assisted (Claude) with manual proofreading; the glossary matches the established fan translation of Chapters 1–4 (Kris = Крис, Susie = Сьюзи, Ralsei = Ральзей, Noelle = Ноэлль, Berdly = Бёрдли).
- Cyrillic glyphs are injected into **all 13 game fonts**, including the Japanese `fnt_ja_*` set.

### Status

| Area | Progress |
|---|---|
| Fonts (Cyrillic glyphs, letter spacing) | done, 13/13 |
| Menus, UI | done |
| Story text | done, 17 521/17 521 strings |
| Proofreading | in progress |

### How it works

Vanilla Chapter 5 loads external text **only for the Japanese language** (`lang/lang_ja.json`), so the translation ships in the Japanese slot and the game runs in 日本語 mode:

1. **English source extraction** — `extract_en_bytecode.py` decodes GameMaker bytecode (`push.String` instruction pairs in the `CODE` chunk of `game.ios`) and reconstructs key/string pairs: 16 123 of 17 521 keys; the rest falls back to the official Japanese text.
2. **Translation** — 120-string chunks (`chunks/`), rules and glossary in [PROMPT.md](docs/PROMPT.md), workflow in [HOWTO.md](docs/HOWTO.md). Control codes (`^4`, `\E2`, `&`, `%%`, etc.) are validated: any string whose codes mismatch the source falls back to English instead of breaking dialogue.
3. **Build** — `build_install.py` merges translated chunks with the English fallback into a complete `lang_ja.json` and installs it (backing up the original).
4. **Fonts** — the game fonts contain no Cyrillic, so it is added: glyphs are rasterized from [Determination](https://github.com/StackTheFennec/Determination) (and undertale-small-font-cyrillic for the smallest fonts) to each atlas's measured pixel metrics (cap height, baseline, and letter gap are measured from the existing Latin ink), packed into an extended atlas, and injected via [UndertaleModTool](https://github.com/UnderminersTeam/UndertaleModTool) CLI as a new texture with rewritten glyph tables. The Japanese `fnt_ja_*` fonts are patched too — they are what the game actually renders with in 日本語 mode.
5. **Letter spacing** — in Japanese mode the text engine advances every non-ASCII character at full CJK width. A GML code patch (`obj_writer`, `obj_battleblcon`): decompile, adjust the threshold, recompile — Cyrillic advances at half width like Latin.

### Installation (macOS, Steam)

Requirements: a legal copy of DELTARUNE, .NET 8+, Python 3 with Pillow, a built [UndertaleModCli](https://github.com/UnderminersTeam/UndertaleModTool).

```bash
git clone https://github.com/EloWeld/deltarune-chapter5-russian-translation.git
cd deltarune-chapter5-russian-translation

# 1. Text: build lang_ja.json and install it into the game (a backup is created automatically)
python3 scripts/build_install.py

# 2. Fonts: inject Cyrillic into game.ios (paths are configured inside the scripts)
#    order: import_font.csx -> import_ja_fonts.csx -> patch_spacing.csx -> patch_round3.csx
dotnet UndertaleModCli.dll load <path to game.ios> -s csx/import_font.csx -o game_patched.ios
# ... see HOWTO.md for the full sequence

# 3. In-game, select the 日本語 language
```

Steam paths on macOS: `~/Library/Application Support/Steam/steamapps/common/DELTARUNE/DELTARUNE.app/Contents/Resources/chapter5_mac/`. For Windows (`data.win` in `chapter5_windows`) the scripts apply with minimal path changes.

**Rollback**: backups `game.ios.orig.bak` and `lang_ja.json.orig.bak` sit next to the modified files — restore them, or verify game files in Steam.

### Contributing

Translation progress lives in `out/` (per-chunk). See [HOWTO.md](docs/HOWTO.md) for the chunk workflow (including Claude Code subagents), [PROMPT.md](docs/PROMPT.md) for string formatting rules, and [GLOSSARY_FIXES.md](docs/GLOSSARY_FIXES.md) for known glossary corrections. Pull requests with translation and proofreading are welcome.

### Disclaimer

This repository **contains no game files** — no `game.ios`, textures, or music. It is a toolkit plus translation text applied to your own legal copy. DELTARUNE (c) Toby Fox. Non-commercial fan project, not affiliated with Toby Fox or 8-4.

### Credits

- **Toby Fox** — DELTARUNE
- [UndertaleModTool / Underminers](https://github.com/UnderminersTeam/UndertaleModTool) — GameMaker modding tools
- [StackTheFennec — Determination](https://github.com/StackTheFennec/Determination) — Undertale-style Cyrillic font
- undertale-small-font-cyrillic — Cyrillic for the small font
- Translation and tooling: Claude (Anthropic) AI assistant, directed by [EloWeld](https://github.com/EloWeld)

---

## Русская версия

### О проекте

- Игра: [DELTARUNE](https://store.steampowered.com/app/1671210/DELTARUNE/) от Toby Fox. Глава 5 вышла в 2026 — официального русского перевода нет.
- Перевод выполняется ИИ (Claude) с ручной вычиткой; глоссарий согласован с фанатским переводом глав 1–4 (Крис, Сьюзи, Ральзей, Ноэлль, Бёрдли).
- Кириллица вшита во **все 13 шрифтов** игры, включая японский набор `fnt_ja_*`.

### Статус

| Что | Готово |
|---|---|
| Шрифты (кириллица, межбуквенные интервалы) | готово, 13/13 |
| Меню, интерфейс | готово |
| Сюжетный текст | готово, 17 521/17 521 строк |
| Вычитка | в работе |

### Как это устроено

Ванильная глава 5 загружает внешний текст **только для японского языка** (`lang/lang_ja.json`), поэтому перевод ставится в японский слот, а игра запускается на языке 日本語:

1. **Извлечение английского текста** — `extract_en_bytecode.py` декодирует байткод GameMaker (chunk `CODE`, инструкции `push.String`) из `game.ios` и восстанавливает пары ключ/строка: 16 123 из 17 521 ключей; остальное берётся из официального японского текста.
2. **Перевод** — чанки по 120 строк (`chunks/`), правила и глоссарий в [PROMPT.md](docs/PROMPT.md), процесс в [HOWTO.md](docs/HOWTO.md). Управляющие коды (`^4`, `\E2`, `&`, `%%` и т.д.) проверяются валидатором: строка с побитыми кодами откатывается на английский, а не ломает игру.
3. **Сборка** — `build_install.py` собирает переведённое + английский фолбэк в полный `lang_ja.json` и кладёт в игру (с бэкапом оригинала).
4. **Шрифты** — в шрифтах игры нет кириллицы, поэтому она дорисовывается: глифы растеризуются из [Determination](https://github.com/StackTheFennec/Determination) (и undertale-small-font-cyrillic для мелких шрифтов) точно под метрики каждого атласа (капитель, базовая линия и зазор меряются по пикселям существующей латиницы), пакуются в расширенный атлас и вшиваются через [UndertaleModTool](https://github.com/UnderminersTeam/UndertaleModTool) CLI: новая текстура + переписанные глифы. Патчатся **и японские** шрифты (`fnt_ja_*`) — именно ими игра рисует текст в японском режиме.
5. **Межбуквенный интервал** — текстовый движок в японском режиме двигает все не-ASCII символы полноширинным шагом (как иероглифы). Патч GML-кода (`obj_writer`, `obj_battleblcon`): декомпиляция, правка порога, рекомпиляция — кириллица получает узкий шаг, как латиница.

### Установка (macOS, Steam)

Понадобятся: лицензионная DELTARUNE, .NET 8+, Python 3 c Pillow, собранный [UndertaleModCli](https://github.com/UnderminersTeam/UndertaleModTool).

```bash
git clone https://github.com/EloWeld/deltarune-chapter5-russian-translation.git
cd deltarune-chapter5-russian-translation

# 1. Текст: собрать lang_ja.json и установить в игру (бэкап создаётся автоматически)
python3 scripts/build_install.py

# 2. Шрифты: вшить кириллицу в game.ios (пути внутри скриптов)
#    порядок: import_font.csx -> import_ja_fonts.csx -> patch_spacing.csx -> patch_round3.csx
dotnet UndertaleModCli.dll load <путь к game.ios> -s csx/import_font.csx -o game_patched.ios
# ... полная последовательность — в HOWTO.md

# 3. В игре выбрать язык 日本語
```

Пути Steam-версии на macOS: `~/Library/Application Support/Steam/steamapps/common/DELTARUNE/DELTARUNE.app/Contents/Resources/chapter5_mac/`. Для Windows (`data.win` в `chapter5_windows`) скрипты применимы с минимальной правкой путей.

**Откат**: рядом с изменёнными файлами лежат бэкапы `game.ios.orig.bak` и `lang_ja.json.orig.bak` — просто верните их на место, либо проверьте целостность файлов в Steam.

### Участие в переводе

Прогресс — по чанкам в `out/`. Как переводить новые чанки (в т.ч. субагентами Claude Code) — в [HOWTO.md](docs/HOWTO.md), правила оформления строк — в [PROMPT.md](docs/PROMPT.md), глоссарные правки — в [GLOSSARY_FIXES.md](docs/GLOSSARY_FIXES.md). PR с переводом и вычиткой приветствуются.

### Дисклеймер

Репозиторий **не содержит файлов игры** — ни `game.ios`, ни текстур, ни музыки. Это набор инструментов и текст перевода, применяемые к вашей собственной лицензионной копии. DELTARUNE (c) Toby Fox. Проект некоммерческий, фанатский, не аффилирован с Toby Fox или 8-4.

### Благодарности

- **Toby Fox** — за DELTARUNE
- [UndertaleModTool / Underminers](https://github.com/UnderminersTeam/UndertaleModTool) — инструменты моддинга GameMaker
- [StackTheFennec — Determination](https://github.com/StackTheFennec/Determination) — кириллический шрифт в стиле Undertale
- undertale-small-font-cyrillic — кириллица для мелкого шрифта
- Перевод и инструментарий: ИИ-ассистент Claude (Anthropic) под руководством [EloWeld](https://github.com/EloWeld)

---

**Keywords**: DELTARUNE Chapter 5 Russian translation, DELTARUNE 5 rus patch, русификатор DELTARUNE глава 5, DELTARUNE 5 на русском, перевод DELTARUNE Chapter 5, fan translation, локализация, GameMaker modding, UndertaleModTool, Cyrillic font injection.
