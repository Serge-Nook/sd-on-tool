#!/usr/bin/env bash
#
# SD-ON Tool — установка/удаление автономного приложения.
#
# Использование:
#   installer.sh install     # установить SD-ON Tool
#   installer.sh uninstall   # удалить SD-ON Tool
#   installer.sh status      # проверить состояние установки
#
# Приложение автономно: не изменяет файлы Steam, не требует прав root,
# не использует фоновые сервисы. Запускается как обычное приложение.
#
set -euo pipefail

VERSION="${SD_ON_TOOL_VERSION:-2.1.0}"

# Директория дистрибутива (payload лежит рядом со scripts).
DIST_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

BASE_DIR="$HOME/.local/share/sd-on-tool"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
DESKTOP_FILE="$DESKTOP_DIR/sd-on-tool.desktop"
LAUNCHER="$BIN_DIR/sd-on-tool"
FLAG_FILE="$BASE_DIR/.installed"

log() { printf '%s\n' "$*"; }
err() { printf 'Ошибка: %s\n' "$*" >&2; }

# Обновляем базу ярлыков (не критично при отсутствии утилиты).
refresh_desktop_db() {
  if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
  fi
}

do_install() {
  log "Установка SD-ON Tool ($VERSION)…"

  mkdir -p "$BASE_DIR" "$BIN_DIR" "$DESKTOP_DIR"

  # Копируем веб-приложение (с подстановкой версии в app.js).
  rm -rf "$BASE_DIR/app"
  mkdir -p "$BASE_DIR/app"
  cp -r "$DIST_ROOT/app/." "$BASE_DIR/app/"
  sed "s/__SD_ON_TOOL_VERSION__/$VERSION/g" "$DIST_ROOT/app/app.js" > "$BASE_DIR/app/app.js"

  # Копируем и делаем исполняемым лаунчер.
  cp "$DIST_ROOT/bin/sd-on-tool" "$BASE_DIR/sd-on-tool"
  chmod +x "$BASE_DIR/sd-on-tool"
  ln -sf "$BASE_DIR/sd-on-tool" "$LAUNCHER"

  # Создаём ярлык в меню приложений.
  local icon="$BASE_DIR/app/assets/icons/sd-on-tool.svg"
  sed -e "s|__EXEC__|$BASE_DIR/sd-on-tool|g" \
      -e "s|__ICON__|$icon|g" \
      "$DIST_ROOT/packaging/sd-on-tool.desktop" > "$DESKTOP_FILE"
  chmod +x "$DESKTOP_FILE"

  refresh_desktop_db

  printf 'installed=%s\nversion=%s\n' "$(date -u +%FT%TZ)" "$VERSION" > "$FLAG_FILE"

  log "Установка завершена."
  log "Запуск: из меню приложений («SD-ON Tool») или командой: $LAUNCHER"
  log "Для игрового режима добавьте $LAUNCHER как стороннюю игру (Add a Non-Steam Game)."
  if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    log "Примечание: $BIN_DIR отсутствует в PATH — используйте полный путь к лаунчеру."
  fi
}

do_uninstall() {
  log "Удаление SD-ON Tool…"
  [[ -L "$LAUNCHER" || -f "$LAUNCHER" ]] && rm -f "$LAUNCHER"
  [[ -f "$DESKTOP_FILE" ]] && rm -f "$DESKTOP_FILE"
  if [[ -d "$BASE_DIR" ]]; then
    rm -rf "$BASE_DIR"
    log "Удалена директория $BASE_DIR."
  fi
  refresh_desktop_db
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
    *) err "Неизвестная команда: '$cmd'. Используйте install | uninstall | status."; return 2 ;;
  esac
}

main "$@"
