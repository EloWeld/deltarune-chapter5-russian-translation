#!/bin/bash
# Русификатор DELTARUNE Chapter 5 — установщик для macOS (Steam).
#
# Одна команда, без зависимостей: только то, что уже есть в macOS
# (bash, curl, bunzip2, perl, shasum). Python и .NET НЕ нужны.
#
#   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/EloWeld/deltarune-chapter5-russian-translation/main/install.sh)"
#
# Что делает: 1) бэкапит оригиналы; 2) применяет бинарный дельта-патч к
# chapter5_mac/game.ios (кириллические шрифты + межбуквенный интервал);
# 3) ставит переведённый lang/lang_ja.json. Игру после этого переключить
# на язык 日本語 — ванильная глава 5 грузит внешний текст только из него.
#
# Можно и без меню: ./install.sh install|rollback|status
# Нестандартный путь к игре: DR5_GAME_DIR=/путь/к/chapter5_mac ./install.sh

set -u -o pipefail

RAW_BASE="https://raw.githubusercontent.com/EloWeld/deltarune-chapter5-russian-translation/main"
GAME_DIR="${DR5_GAME_DIR:-$HOME/Library/Application Support/Steam/steamapps/common/DELTARUNE/DELTARUNE.app/Contents/Resources/chapter5_mac}"
GAME="$GAME_DIR/game.ios"
GAME_BAK="$GAME.orig.bak"
LANG_JA="$GAME_DIR/lang/lang_ja.json"
LANG_BAK="$LANG_JA.orig.bak"

TMP="$(mktemp -d /tmp/dr5ru.XXXXXX)"
trap 'rm -rf "$TMP"' EXIT

# ── оформление ──────────────────────────────────────────────────────────
B=$'\033[1m'; DIM=$'\033[2m'; R=$'\033[0m'
RED=$'\033[31m'; GRN=$'\033[32m'; YLW=$'\033[33m'; CYN=$'\033[36m'

line() { printf '%s\n' "${DIM}────────────────────────────────────────────────────────────${R}"; }
say()  { printf '%s\n' "$@"; }
pause(){ printf '\n%s' "${DIM}нажмите Enter…${R}"; read -r _ < /dev/tty; }
fail() { printf '\n%s✗ %s%s\n' "$RED" "$1" "$R"; pause; }

header() {
    clear
    printf '%s' "$CYN"
    say '  ╔══════════════════════════════════════════════════════╗'
    say '  ║        DELTARUNE  Chapter 5  —  РУСИФИКАТОР          ║'
    say '  ╚══════════════════════════════════════════════════════╝'
    printf '%s' "$R"
    say "  ${DIM}перевод: 100% строк (17 521), шрифты: 13/13, вычитка: идёт${R}"
    say "  ${DIM}фанатский неофициальный перевод; нужна лицензионная копия${R}"
    echo
}

# ── данные dist: локально (из клона репо) или с GitHub ─────────────────
SELF_DIR=""
[ -n "${BASH_SOURCE[0]:-}" ] && SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"

fetch() {  # fetch <имя-файла-в-dist> <куда> [показывать-прогресс]
    if [ -n "$SELF_DIR" ] && [ -f "$SELF_DIR/dist/$1" ]; then
        cp "$SELF_DIR/dist/$1" "$2"
    else
        local flag="--silent"; [ -n "${3:-}" ] && flag="--progress-bar"
        curl -fL "$flag" "$RAW_BASE/dist/$1" -o "$2"
    fi
}

manifest() { sed -n "s/^$1=//p" "$TMP/manifest.txt"; }

sha() { shasum -a 256 "$1" | cut -d' ' -f1; }

# ── состояние ──────────────────────────────────────────────────────────
GAME_STATE="?" LANG_STATE="?"

detect_state() {
    printf '%s' "  ${DIM}проверяю файлы игры…${R}"
    local g l
    g="$(sha "$GAME")"
    if   [ "$g" = "$SHA_PATCHED" ]; then GAME_STATE="ru"
    elif [ "$g" = "$SHA_ORIG"    ]; then GAME_STATE="orig"
    else GAME_STATE="unknown"; fi
    if [ -f "$LANG_JA" ]; then
        l="$(sha "$LANG_JA")"
        [ "$l" = "$SHA_LANG" ] && LANG_STATE="ru" || LANG_STATE="other"
    else
        LANG_STATE="missing"
    fi
    printf '\r\033[K'
}

state_line() {
    local g_txt l_txt
    case "$GAME_STATE" in
        ru)      g_txt="${GRN}русифицирован${R}";;
        orig)    g_txt="оригинал";;
        unknown) g_txt="${YLW}неизвестная версия${R}";;
    esac
    case "$LANG_STATE" in
        ru)    l_txt="${GRN}установлен${R}";;
        *)     l_txt="оригинал";;
    esac
    say "  игра:    $GAME_DIR"
    say "  шрифты и код (game.ios):  $g_txt"
    say "  текст (lang_ja.json):     $l_txt"
    [ -f "$GAME_BAK" ] && say "  бэкап:   есть — откат доступен в любой момент" \
                       || say "  бэкап:   ещё не создан (создастся при установке)"
}

# ── perl-аппликатор дельта-патча (формат DR5RU1, см. scripts/make_dist.py)
apply_patch() {  # apply_patch <patch.raw> <old> <out>
    /usr/bin/perl -e '
        use strict; use warnings;
        my ($pf, $of, $outf) = @ARGV;
        open(my $P, "<", $pf) or die "patch: $!"; binmode $P;
        my $m = <$P>; $m eq "DR5RU1\n" or die "bad patch magic";
        scalar <$P>; scalar <$P>;                       # sha-строки (проверяет bash)
        chomp(my $newlen = <$P>); chomp(my $nops = <$P>);
        my @ops; for (1..$nops) { chomp(my $s = <$P>); push @ops, [split / /, $s]; }
        open(my $O, "<", $of) or die "old: $!"; binmode $O;
        my $old = do { local $/; <$O> }; close $O;
        open(my $W, ">", $outf) or die "out: $!"; binmode $W;
        my $done = 0;
        for my $op (@ops) {
            my $len = $op->[0] eq "C" ? $op->[2] : $op->[1];
            read($P, my $x, $len) == $len or die "truncated patch";
            print $W ($op->[0] eq "C" ? (substr($old, $op->[1], $len) ^ $x) : $x);
            $done += $len;
        }
        close $W or die "write: $!";
        $done == $newlen or die "size mismatch";
    ' "$1" "$2" "$3"
}

# ── действия ───────────────────────────────────────────────────────────
do_install() {
    header
    say "  ${B}Установка${R}"
    line
    if [ "$GAME_STATE" = "unknown" ]; then
        say "  ${YLW}Ваш game.ios не совпадает ни с оригиналом, ни с уже${R}"
        say "  ${YLW}русифицированной версией.${R} Обычно это значит, что игра"
        say "  обновилась (русификатор собран под другую версию) или на ней"
        say "  стоят другие моды."
        say ""
        say "  Что делать: Steam → DELTARUNE → Свойства → Установленные"
        say "  файлы → Проверить целостность — а затем запустите установку"
        say "  заново. Если игра просто новее — ждите обновления русификатора."
        pause; return
    fi

    if [ "$GAME_STATE" = "orig" ]; then
        # бэкап оригинала (один раз)
        if [ ! -f "$GAME_BAK" ]; then
            say "  → бэкап оригинала: game.ios.orig.bak"
            cp "$GAME" "$GAME_BAK" || { fail "не удалось создать бэкап"; return; }
        fi
        say "  → загрузка патча шрифтов (~14 МБ)…"
        fetch "$PATCH_FILE" "$TMP/patch.bz2" progress || { fail "не скачался патч"; return; }
        say "  → распаковка и применение патча (~166 МБ, до минуты)…"
        bunzip2 -c "$TMP/patch.bz2" > "$TMP/patch.raw" || { fail "битый архив патча"; return; }
        apply_patch "$TMP/patch.raw" "$GAME" "$TMP/game.new" || { fail "патч не применился"; return; }
        [ "$(sha "$TMP/game.new")" = "$SHA_PATCHED" ] || { fail "контрольная сумма не сошлась — файл не тронут"; return; }
        mv "$TMP/game.new" "$GAME" || { fail "не удалось записать game.ios"; return; }
        say "    ${GRN}✓ шрифты и код: готово${R}"
    else
        say "  ✓ game.ios уже русифицирован — пропускаю"
    fi

    # текст: бэкапим оригинальный lang_ja.json, если он ещё оригинальный
    if [ ! -f "$LANG_BAK" ] && [ -f "$LANG_JA" ] && [ "$LANG_STATE" != "ru" ]; then
        cp "$LANG_JA" "$LANG_BAK" || { fail "не удалось создать бэкап lang_ja.json"; return; }
    fi
    say "  → установка перевода (lang_ja.json)…"
    fetch "$LANG_FILE" "$TMP/lang.json" || { fail "не скачался файл перевода"; return; }
    [ "$(sha "$TMP/lang.json")" = "$SHA_LANG" ] || { fail "битый файл перевода"; return; }
    cp "$TMP/lang.json" "$LANG_JA" || { fail "не удалось записать lang_ja.json"; return; }
    say "    ${GRN}✓ текст: готово${R}"

    detect_state
    line
    say "  ${GRN}${B}Готово!${R} Осталось одно:"
    say ""
    say "  ${B}в игре откройте настройки (Settings) и выберите язык 日本語${R}"
    say "  ${DIM}(да, японский — глава 5 читает внешний перевод только из${R}"
    say "  ${DIM}японского слота; текст при этом будет русским)${R}"
    say ""
    say "  Откат: снова запустите установщик → пункт «Откатить»,"
    say "  либо проверьте целостность файлов в Steam."
    pause
}

do_rollback() {
    header
    say "  ${B}Откат на оригинал${R}"
    line
    local done=0
    if [ -f "$GAME_BAK" ]; then
        cp "$GAME_BAK" "$GAME" && { say "  ✓ game.ios восстановлен"; done=1; }
    else
        say "  – бэкапа game.ios нет"
    fi
    if [ -f "$LANG_BAK" ]; then
        cp "$LANG_BAK" "$LANG_JA" && { say "  ✓ lang_ja.json восстановлен"; done=1; }
    else
        say "  – бэкапа lang_ja.json нет"
    fi
    if [ "$done" = 0 ]; then
        say ""
        say "  Бэкапов не нашлось. Восстановить оригинал можно через Steam:"
        say "  DELTARUNE → Свойства → Установленные файлы → Проверить целостность."
    fi
    detect_state
    pause
}

# ── старт ──────────────────────────────────────────────────────────────
[ "$(uname)" = "Darwin" ] || { echo "Этот установщик — только для macOS."; exit 1; }
[ -t 0 ] || exec < /dev/tty || { echo "Нужен интерактивный терминал."; exit 1; }

header
if [ ! -f "$GAME" ]; then
    say "  ${YLW}Не нашёл игру:${R} $GAME"
    say ""
    say "  Если DELTARUNE установлена не в стандартную папку Steam,"
    say "  укажите путь к папке ${B}chapter5_mac${R} (или Enter для выхода):"
    printf '\n  > '
    read -r -e CUSTOM < /dev/tty
    [ -z "$CUSTOM" ] && exit 0
    GAME_DIR="${CUSTOM%/}"; GAME="$GAME_DIR/game.ios"
    GAME_BAK="$GAME.orig.bak"; LANG_JA="$GAME_DIR/lang/lang_ja.json"; LANG_BAK="$LANG_JA.orig.bak"
    [ -f "$GAME" ] || { say ""; say "  ${RED}game.ios там не нашёлся — выхожу.${R}"; exit 1; }
fi

printf '%s' "  ${DIM}получаю манифест…${R}"
fetch manifest.txt "$TMP/manifest.txt" || { echo; echo "  ${RED}Не удалось получить манифест (нет сети?)${R}"; exit 1; }
printf '\r\033[K'
VERSION="$(manifest VERSION)"
SHA_ORIG="$(manifest GAME_ORIG_SHA256)"
SHA_PATCHED="$(manifest GAME_PATCHED_SHA256)"
SHA_LANG="$(manifest LANG_SHA256)"
PATCH_FILE="$(manifest PATCH_FILE)"
LANG_FILE="$(manifest LANG_FILE)"
[ -n "$SHA_ORIG" ] && [ -n "$SHA_PATCHED" ] || { echo "  ${RED}Битый манифест.${R}"; exit 1; }

detect_state

# режим без меню: install.sh install|rollback|status
case "${1:-}" in
    install)  do_install;  exit 0;;
    rollback) do_rollback; exit 0;;
    status)   header; say "  версия русификатора: $VERSION"; state_line; echo; exit 0;;
esac

while :; do
    header
    say "  версия русификатора: ${B}$VERSION${R}"
    state_line
    line
    if [ "$GAME_STATE" = "ru" ] && [ "$LANG_STATE" = "ru" ]; then
        say "  ${GRN}Всё установлено.${R} В игре должен быть выбран язык ${B}日本語${R}."
        line
    fi
    say "  ${B}1${R}  Установить / обновить русификатор"
    say "  ${B}2${R}  Откатить на оригинал"
    say "  ${B}q${R}  Выход"
    printf '\n  выбор: '
    read -r -n 1 CH < /dev/tty; echo
    case "$CH" in
        1) do_install;;
        2) do_rollback;;
        q|Q) clear; exit 0;;
    esac
done
