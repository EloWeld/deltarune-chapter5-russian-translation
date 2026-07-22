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
6. **Distribution** — `make_dist.py` packs the result into `dist/`: a checksum-bound binary delta patch (original → patched `game.ios`) plus the built lang file. `install.sh` applies them with tools shipped in every macOS (`perl`, `bunzip2`, `shasum`), so end users need neither Python nor .NET.

### Installation (macOS, Steam)

One command in Terminal. No Python, no .NET, nothing to build — the TUI installer uses only tools already shipped with macOS:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/EloWeld/deltarune-chapter5-russian-translation/main/install.sh)"
```

The installer finds your Steam copy (or asks for a path), shows what it is about to do, and then:

1. backs up the originals (`game.ios.orig.bak`, `lang_ja.json.orig.bak`) — rollback is one menu item away;
2. applies a checksum-verified binary delta patch to `chapter5_mac/game.ios` (Cyrillic fonts + letter-spacing code patch);
3. installs the translated `lang/lang_ja.json`;
4. reminds you of the final step: **in-game, select the 日本語 language** (vanilla Chapter 5 loads external text only from the Japanese slot — the text itself is Russian).

From a cloned repo the same installer runs offline: `./install.sh` (menu) or `./install.sh install|rollback|status`. Custom game location: `DR5_GAME_DIR=/path/to/chapter5_mac ./install.sh`.

The patch is bound to the exact game version it was built for — if Steam updates the game, the installer refuses cleanly and nothing is touched; wait for an updated patch or build from source.

**Rollback**: run the installer again → "Откатить", or verify game files in Steam. Windows (`data.win` in `chapter5_windows`): no installer yet — the source pipeline below applies with minimal path changes.

<details>
<summary><b>Building from source (developers)</b></summary>

Requirements: a legal copy of DELTARUNE, .NET 8+, Python 3 with Pillow, a built [UndertaleModCli](https://github.com/UnderminersTeam/UndertaleModTool).

```bash
git clone https://github.com/EloWeld/deltarune-chapter5-russian-translation.git
cd deltarune-chapter5-russian-translation

# 1. Text: build lang_ja.json and install it into the game (a backup is created automatically)
python3 scripts/build_install.py

# 2. Fonts: inject Cyrillic into the CHAPTER 5 data file.
#    IMPORTANT: patch chapter5_mac/game.ios — the file the game actually loads.
#    Do NOT patch Resources/game.ios: that is only the chapter-select launcher
#    (a separate, YYC-compiled data file with a different, smaller font set).
#    Also edit the hardcoded `workDir` at the top of each csx to your own fontwork/ path.
DLL="$HOME/utmt/UndertaleModCli/bin/Release/net10.0/UndertaleModCli.dll"   # your built CLI
GAME="$HOME/Library/Application Support/Steam/steamapps/common/DELTARUNE/DELTARUNE.app/Contents/Resources/chapter5_mac/game.ios"

[ -f "$GAME.orig.bak" ] || cp "$GAME" "$GAME.orig.bak"                     # back up the original once

# run all four scripts in order, each over the previous output:
dotnet "$DLL" load "$GAME"           -s csx/import_font.csx     -o game_patched.ios
dotnet "$DLL" load game_patched.ios  -s csx/import_ja_fonts.csx -o game_patched.ios
dotnet "$DLL" load game_patched.ios  -s csx/patch_spacing.csx   -o game_patched.ios
dotnet "$DLL" load game_patched.ios  -s csx/patch_round3.csx    -o game_patched.ios

cp game_patched.ios "$GAME"                                                # install into the game

# 3. Repack dist/ for the one-command installer (delta patch + lang file + manifest):
python3 scripts/make_dist.py
```

Steam paths on macOS: `~/Library/Application Support/Steam/steamapps/common/DELTARUNE/DELTARUNE.app/Contents/Resources/chapter5_mac/`.

</details>

### Localizing text sprites

`sprites/` holds all 37 text-bearing sprites (137 frame PNGs) the game shows in translated mode — battle buttons, banners, signs. Redraw a PNG (keep dimensions), run `csx/import_sprites.csx`, and the game picks it up. See [HOWTO.md](docs/HOWTO.md).

### Contributing

Translation progress lives in `out/` (per-chunk). See [HOWTO.md](docs/HOWTO.md) for the chunk workflow (including Claude Code subagents), [PROMPT.md](docs/PROMPT.md) for string formatting rules, and [GLOSSARY_FIXES.md](docs/GLOSSARY_FIXES.md) for known glossary corrections. Pull requests with translation and proofreading are welcome.

### Disclaimer

This repository **contains no game binaries** — no `game.ios`, textures, or music. `dist/` holds only the translation text and a binary *diff* that is useless without your own legal copy of the game. DELTARUNE (c) Toby Fox. Non-commercial fan project, not affiliated with Toby Fox or 8-4.

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
6. **Дистрибуция** — `make_dist.py` собирает результат в `dist/`: бинарный дельта-патч (оригинальный → пропатченный `game.ios`) с привязкой по контрольным суммам плюс готовый lang-файл. `install.sh` применяет их средствами, которые есть в любой macOS (`perl`, `bunzip2`, `shasum`), — конечному пользователю не нужны ни Python, ни .NET.

### Установка (macOS, Steam)

Одна команда в Терминале. Не нужны ни Python, ни .NET, ничего собирать не надо — TUI-установщик использует только то, что уже есть в macOS:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/EloWeld/deltarune-chapter5-russian-translation/main/install.sh)"
```

Установщик сам находит Steam-копию (или спрашивает путь), показывает, что собирается сделать, и дальше:

1. бэкапит оригиналы (`game.ios.orig.bak`, `lang_ja.json.orig.bak`) — откат в один пункт меню;
2. применяет бинарный дельта-патч к `chapter5_mac/game.ios` с проверкой контрольных сумм (кириллические шрифты + патч межбуквенного интервала);
3. ставит переведённый `lang/lang_ja.json`;
4. напоминает последний шаг: **в игре выбрать язык 日本語** (ванильная глава 5 читает внешний текст только из японского слота — сам текст при этом русский).

Из клона репозитория тот же установщик работает офлайн: `./install.sh` (меню) или `./install.sh install|rollback|status`. Нестандартный путь к игре: `DR5_GAME_DIR=/путь/к/chapter5_mac ./install.sh`.

Патч привязан к конкретной версии игры: если Steam обновит игру, установщик честно откажется и ничего не тронет — ждите обновлённый патч или соберите из исходников.

**Откат**: снова запустите установщик → «Откатить», либо проверьте целостность файлов в Steam. Windows (`data.win` в `chapter5_windows`): установщика пока нет — пайплайн сборки ниже применим с минимальной правкой путей.

<details>
<summary><b>Сборка из исходников (для разработчиков)</b></summary>

Понадобятся: лицензионная DELTARUNE, .NET 8+, Python 3 c Pillow, собранный [UndertaleModCli](https://github.com/UnderminersTeam/UndertaleModTool).

```bash
git clone https://github.com/EloWeld/deltarune-chapter5-russian-translation.git
cd deltarune-chapter5-russian-translation

# 1. Текст: собрать lang_ja.json и установить в игру (бэкап создаётся автоматически)
python3 scripts/build_install.py

# 2. Шрифты: вшить кириллицу в data-файл ГЛАВЫ 5.
#    ВАЖНО: патчить chapter5_mac/game.ios — именно его грузит игра.
#    НЕ патчить Resources/game.ios: это лишь лаунчер выбора главы
#    (отдельный YYC-файл с другим, меньшим набором шрифтов).
#    Также поправьте захардкоженный `workDir` вверху каждого csx на свой путь к fontwork/.
DLL="$HOME/utmt/UndertaleModCli/bin/Release/net10.0/UndertaleModCli.dll"   # ваш собранный CLI
GAME="$HOME/Library/Application Support/Steam/steamapps/common/DELTARUNE/DELTARUNE.app/Contents/Resources/chapter5_mac/game.ios"

[ -f "$GAME.orig.bak" ] || cp "$GAME" "$GAME.orig.bak"                     # бэкап оригинала (один раз)

# прогнать все четыре скрипта по порядку, каждый над результатом предыдущего:
dotnet "$DLL" load "$GAME"           -s csx/import_font.csx     -o game_patched.ios
dotnet "$DLL" load game_patched.ios  -s csx/import_ja_fonts.csx -o game_patched.ios
dotnet "$DLL" load game_patched.ios  -s csx/patch_spacing.csx   -o game_patched.ios
dotnet "$DLL" load game_patched.ios  -s csx/patch_round3.csx    -o game_patched.ios

cp game_patched.ios "$GAME"                                                # установить в игру

# 3. Пересобрать dist/ для одно-командного установщика (дельта-патч + lang-файл + манифест):
python3 scripts/make_dist.py
```

Пути Steam-версии на macOS: `~/Library/Application Support/Steam/steamapps/common/DELTARUNE/DELTARUNE.app/Contents/Resources/chapter5_mac/`.

</details>

### Русификация графики

В `sprites/` — все 37 спрайтов с текстом (137 кадров-PNG): кнопки боя, баннеры, вывески. Перерисуйте PNG (размер не менять), запустите `csx/import_sprites.csx` — игра подхватит. Подробнее в [HOWTO.md](docs/HOWTO.md).

### Участие в переводе

Прогресс — по чанкам в `out/`. Как переводить новые чанки (в т.ч. субагентами Claude Code) — в [HOWTO.md](docs/HOWTO.md), правила оформления строк — в [PROMPT.md](docs/PROMPT.md), глоссарные правки — в [GLOSSARY_FIXES.md](docs/GLOSSARY_FIXES.md). PR с переводом и вычиткой приветствуются.

### Дисклеймер

Репозиторий **не содержит бинарников игры** — ни `game.ios`, ни текстур, ни музыки. В `dist/` лежат только текст перевода и бинарный *дифф*, бесполезный без вашей собственной лицензионной копии игры. DELTARUNE (c) Toby Fox. Проект некоммерческий, фанатский, не аффилирован с Toby Fox или 8-4.

### Благодарности

- **Toby Fox** — за DELTARUNE
- [UndertaleModTool / Underminers](https://github.com/UnderminersTeam/UndertaleModTool) — инструменты моддинга GameMaker
- [StackTheFennec — Determination](https://github.com/StackTheFennec/Determination) — кириллический шрифт в стиле Undertale
- undertale-small-font-cyrillic — кириллица для мелкого шрифта
- Перевод и инструментарий: ИИ-ассистент Claude (Anthropic) под руководством [EloWeld](https://github.com/EloWeld)

---

**Keywords**: DELTARUNE Chapter 5 Russian translation, DELTARUNE 5 rus patch, русификатор DELTARUNE глава 5, DELTARUNE 5 на русском, перевод DELTARUNE Chapter 5, fan translation, локализация, GameMaker modding, UndertaleModTool, Cyrillic font injection.
