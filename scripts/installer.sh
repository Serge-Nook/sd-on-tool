#!/usr/bin/env bash
#
# SD-ON Tool — базовая логика установки и удаления.
#
# Использование:
#   installer.sh install     # установить SD-ON Tool
#   installer.sh uninstall   # удалить SD-ON Tool и откатить изменения
#   installer.sh status      # проверить состояние установки
#
# Права root не требуются: всё выполняется от текущего пользователя
# (на Steam Deck — deck).
#
set -euo pipefail

VERSION="${SD_ON_TOOL_VERSION:-2.0.0}"

# Директория репозитория/дистрибутива (payload лежит рядом со scripts).
DIST_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PAYLOAD_DIR="$DIST_ROOT/payload"

TARGET_USER="${SUDO_USER:-${USER:-$(id -un)}}"
TARGET_HOME="$(getent passwd "$TARGET_USER" 2>/dev/null | cut -d: -f6 || true)"
if [[ -z "${TARGET_HOME:-}" ]]; then
  TARGET_HOME="$HOME"
fi

BASE_DIR="$TARGET_HOME/.local/share/sd-on-tool"
BACKUP_DIR="$BASE_DIR/backup"
FLAG_FILE="$BASE_DIR/.installed"

INJECT_LINE='<script src="file:///home/deck/.local/share/sd-on-tool/sd-on-tool.js"></script>'
INJECT_MARKER="sd-on-tool.js"

log() { printf '%s\n' "$*"; }
err() { printf 'Ошибка: %s\n' "$*" >&2; }

# Определяет путь к steamui/index.html клиента Steam (проверяется автоматически).
find_steamui_index() {
  local candidates=(
    "$TARGET_HOME/.steam/steam/steamui/index.html"
    "$TARGET_HOME/.local/share/Steam/steamui/index.html"
    "$TARGET_HOME/.steam/root/steamui/index.html"
  )
  local c
  for c in "${candidates[@]}"; do
    if [[ -f "$c" ]]; then
      printf '%s' "$c"
      return 0
    fi
  done
  return 1
}

do_install() {
  log "Установка SD-ON Tool ($VERSION)…"

  local steam_index
  if ! steam_index="$(find_steamui_index)"; then
    err "Не найден index.html интерфейса Steam (steamui/index.html). Запустите Steam хотя бы один раз."
    return 1
  fi
  log "Файл интерфейса Steam: $steam_index"

  mkdir -p "$BASE_DIR" "$BASE_DIR/themes" "$BASE_DIR/assets" "$BACKUP_DIR"

  # Копирование компонентов.
  sed "s/__SD_ON_TOOL_VERSION__/$VERSION/g" "$PAYLOAD_DIR/sd-on-tool.js" > "$BASE_DIR/sd-on-tool.js"
  cp -r "$PAYLOAD_DIR/themes/." "$BASE_DIR/themes/"
  cp -r "$PAYLOAD_DIR/assets/." "$BASE_DIR/assets/"

  # settings.json создаётся только при первом запуске, чтобы не терять данные.
  if [[ ! -f "$BASE_DIR/settings.json" ]]; then
    cp "$PAYLOAD_DIR/settings.json" "$BASE_DIR/settings.json"
  fi

  # Резервная копия оригинального index.html (только если её ещё нет).
  if [[ ! -f "$BACKUP_DIR/index.html" ]]; then
    cp "$steam_index" "$BACKUP_DIR/index.html"
    log "Создана резервная копия: $BACKUP_DIR/index.html"
  fi

  # Минимальная модификация: добавить <script> перед </body>, если ещё не добавлен.
  if grep -q "$INJECT_MARKER" "$steam_index"; then
    log "Скрипт уже внедрён — пропуск модификации."
  else
    local tmp
    tmp="$(mktemp)"
    # Вставка перед последним закрывающим тегом </body> (без учёта регистра).
    awk -v line="$INJECT_LINE" '
      BEGIN { IGNORECASE = 1 }
      {
        if (tolower($0) ~ /<\/body>/ && !done) {
          sub(/<\/body>/, line "\n</body>")
          done = 1
        }
        print
      }
      END {
        if (!done) { print line }
      }
    ' "$steam_index" > "$tmp"
    cat "$tmp" > "$steam_index"
    rm -f "$tmp"
    log "Скрипт внедрён в интерфейс Steam."
  fi

  printf 'installed=%s\nversion=%s\nsteam_index=%s\n' "$(date -u +%FT%TZ)" "$VERSION" "$steam_index" > "$FLAG_FILE"
  log "Установка завершена. Перезапустите Steam или игровой режим для применения."
}

do_uninstall() {
  log "Удаление SD-ON Tool…"

  local steam_index=""
  if [[ -f "$FLAG_FILE" ]]; then
    steam_index="$(sed -n 's/^steam_index=//p' "$FLAG_FILE")"
  fi
  if [[ -z "$steam_index" || ! -f "$steam_index" ]]; then
    steam_index="$(find_steamui_index || true)"
  fi

  # Восстановление оригинального index.html из резервной копии.
  if [[ -f "$BACKUP_DIR/index.html" && -n "$steam_index" ]]; then
    cp "$BACKUP_DIR/index.html" "$steam_index"
    log "Восстановлен оригинальный index.html."
  elif [[ -n "$steam_index" && -f "$steam_index" ]]; then
    # Резервной копии нет — удаляем только внедрённую строку.
    local tmp
    tmp="$(mktemp)"
    grep -v "$INJECT_MARKER" "$steam_index" > "$tmp" || true
    cat "$tmp" > "$steam_index"
    rm -f "$tmp"
    log "Удалена внедрённая строка из index.html."
  fi

  # Удаление рабочей директории целиком.
  if [[ -d "$BASE_DIR" ]]; then
    rm -rf "$BASE_DIR"
    log "Удалена директория $BASE_DIR."
  fi

  log "Удаление завершено."
}

do_status() {
  if [[ -f "$FLAG_FILE" ]]; then
    log "SD-ON Tool установлен:"
    cat "$FLAG_FILE"
  else
    log "SD-ON Tool не установлен."
  fi
}

main() {
  local cmd="${1:-}"
  case "$cmd" in
    install)   do_install ;;
    uninstall) do_uninstall ;;
    status)    do_status ;;
    *)
      err "Неизвестная команда: '$cmd'. Используйте install | uninstall | status."
      return 2
      ;;
  esac
}

main "$@"
