#!/bin/bash
# =================================================================
# SD-ON Tool — Установщик / Удаление для Steam Deck
# =================================================================
# Графический установщик с поддержкой zenity (SteamOS).
# Если zenity недоступен, используется терминальный режим.
#
# Возможности:
#   - Установка SD-ON Tool (AppImage + ярлык + иконка)
#   - Удаление SD-ON Tool
#   - Автоматический поиск AppImage рядом с установщиком
# =================================================================

set -euo pipefail

APP_NAME="SD-ON Tool"
APP_ID="sd-on-tool"
INSTALL_DIR="$HOME/Applications"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
CONFIG_DIR="$HOME/.config/sd-on-tool"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APPIMAGE_NAME="SD-ON-Tool.AppImage"

# ─── Определение режима (GUI / терминал) ────────────────────────

HAS_ZENITY=false
if command -v zenity &>/dev/null; then
    HAS_ZENITY=true
fi

msg_info() {
    if $HAS_ZENITY; then
        zenity --info --title="$APP_NAME" --text="$1" --width=400 2>/dev/null
    else
        echo ""
        echo "  $1"
        echo ""
    fi
}

msg_error() {
    if $HAS_ZENITY; then
        zenity --error --title="$APP_NAME — Ошибка" --text="$1" --width=400 2>/dev/null
    else
        echo ""
        echo "  ОШИБКА: $1"
        echo ""
    fi
}

msg_question() {
    if $HAS_ZENITY; then
        zenity --question --title="$APP_NAME" --text="$1" --width=400 2>/dev/null
        return $?
    else
        read -p "  $1 (y/n): " -n 1 -r
        echo ""
        [[ $REPLY =~ ^[Yy]$ ]]
        return $?
    fi
}

# ─── Создание SVG-иконки ────────────────────────────────────────

create_icon() {
    mkdir -p "$ICON_DIR"
    cat > "$ICON_DIR/${APP_ID}.svg" << 'ICON_SVG'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" xmlns="http://www.w3.org/2000/svg">
  <rect width="256" height="256" rx="40" fill="#1a1a2e"/>
  <rect x="20" y="20" width="216" height="216" rx="30" fill="#16213e" stroke="#0f3460" stroke-width="3"/>
  <text x="128" y="115" font-family="Arial, sans-serif" font-size="52" font-weight="bold" fill="#e94560" text-anchor="middle">SD-ON</text>
  <text x="128" y="165" font-family="Arial, sans-serif" font-size="32" fill="#606080" text-anchor="middle">Tool</text>
</svg>
ICON_SVG
}

# ─── Поиск AppImage ─────────────────────────────────────────────

find_appimage() {
    # 1. Рядом с установщиком
    for f in "$SCRIPT_DIR"/SD-ON-Tool*.AppImage; do
        if [ -f "$f" ]; then
            echo "$f"
            return 0
        fi
    done

    # 2. В текущей директории
    for f in "$(pwd)"/SD-ON-Tool*.AppImage; do
        if [ -f "$f" ]; then
            echo "$f"
            return 0
        fi
    done

    # 3. В ~/Downloads
    for f in "$HOME/Downloads"/SD-ON-Tool*.AppImage; do
        if [ -f "$f" ]; then
            echo "$f"
            return 0
        fi
    done

    return 1
}

# ─── Установка ──────────────────────────────────────────────────

do_install() {
    local appimage_path=""

    # Попробовать найти автоматически
    if appimage_path="$(find_appimage)"; then
        if ! msg_question "Найден AppImage:\n$appimage_path\n\nУстановить?"; then
            return 0
        fi
    else
        # Попросить выбрать файл
        if $HAS_ZENITY; then
            appimage_path="$(zenity --file-selection \
                --title="Выберите SD-ON-Tool AppImage" \
                --filename="$HOME/" \
                --file-filter="AppImage | *.AppImage" 2>/dev/null)" || return 0
        else
            echo ""
            read -p "  Путь к AppImage: " appimage_path
            appimage_path="${appimage_path//\'/}"
            appimage_path="${appimage_path//\"/}"
        fi
    fi

    if [ ! -f "$appimage_path" ]; then
        msg_error "Файл не найден: $appimage_path"
        return 1
    fi

    echo "Установка $APP_NAME..."

    # Создание директорий
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$DESKTOP_DIR"

    # Копирование AppImage
    cp "$appimage_path" "$INSTALL_DIR/$APPIMAGE_NAME"
    chmod +x "$INSTALL_DIR/$APPIMAGE_NAME"

    # Иконка
    create_icon

    # Desktop-ярлык
    cat > "$DESKTOP_DIR/${APP_ID}.desktop" << DESKTOP_ENTRY
[Desktop Entry]
Type=Application
Name=SD-ON Tool
Comment=Автономное приложение настройки Steam Deck
Exec=$INSTALL_DIR/$APPIMAGE_NAME
Icon=$APP_ID
Categories=Utility;System;Game;
Terminal=false
StartupWMClass=SD-ON Tool
StartupNotify=true
DESKTOP_ENTRY

    # Обновление кэша иконок и базы .desktop (если доступно)
    if command -v update-desktop-database &>/dev/null; then
        update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    fi
    if command -v gtk-update-icon-cache &>/dev/null; then
        gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
    fi

    msg_info "✅ $APP_NAME установлен!\n\nПуть: $INSTALL_DIR/$APPIMAGE_NAME\nЯрлык добавлен в меню приложений.\n\nДля радио установите mpv:\nsudo pacman -S mpv"
}

# ─── Удаление ───────────────────────────────────────────────────

do_uninstall() {
    local installed=false

    if [ -f "$INSTALL_DIR/$APPIMAGE_NAME" ] || [ -f "$DESKTOP_DIR/${APP_ID}.desktop" ]; then
        installed=true
    fi

    if ! $installed; then
        msg_info "$APP_NAME не установлен."
        return 0
    fi

    if ! msg_question "Удалить $APP_NAME?\n\nБудут удалены:\n• $INSTALL_DIR/$APPIMAGE_NAME\n• Ярлык из меню\n• Иконка"; then
        return 0
    fi

    # Удаление AppImage
    if [ -f "$INSTALL_DIR/$APPIMAGE_NAME" ]; then
        rm -f "$INSTALL_DIR/$APPIMAGE_NAME"
    fi

    # Удаление ярлыка
    if [ -f "$DESKTOP_DIR/${APP_ID}.desktop" ]; then
        rm -f "$DESKTOP_DIR/${APP_ID}.desktop"
    fi

    # Удаление иконки
    if [ -f "$ICON_DIR/${APP_ID}.svg" ]; then
        rm -f "$ICON_DIR/${APP_ID}.svg"
    fi

    # Обновление кэша
    if command -v update-desktop-database &>/dev/null; then
        update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    fi

    # Спросить про настройки
    if [ -d "$CONFIG_DIR" ]; then
        if msg_question "Удалить настройки $APP_NAME?\n(радиостанции, тема, насыщенность)"; then
            rm -rf "$CONFIG_DIR"
        fi
    fi

    msg_info "✅ $APP_NAME удалён."
}

# ─── Главное меню ───────────────────────────────────────────────

main() {
    if $HAS_ZENITY; then
        local choice
        choice="$(zenity --list \
            --title="$APP_NAME — Установщик" \
            --text="Выберите действие:" \
            --column="Действие" --column="Описание" \
            --width=450 --height=300 \
            "Установить" "Установить $APP_NAME на Steam Deck" \
            "Удалить" "Удалить $APP_NAME и ярлык" \
            2>/dev/null)" || exit 0

        case "$choice" in
            "Установить") do_install ;;
            "Удалить")    do_uninstall ;;
        esac
    else
        echo ""
        echo "╔══════════════════════════════════════════════╗"
        echo "║        $APP_NAME — Установщик               ║"
        echo "╚══════════════════════════════════════════════╝"
        echo ""
        echo "  1) Установить"
        echo "  2) Удалить"
        echo "  0) Выход"
        echo ""
        read -p "  Выбор: " -n 1 -r
        echo ""

        case "$REPLY" in
            1) do_install ;;
            2) do_uninstall ;;
            *) echo "  Выход." ;;
        esac
    fi
}

main
