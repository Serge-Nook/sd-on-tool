#!/bin/bash
# =================================================================
# Создание самодостаточного установщика SD-ON Tool
# =================================================================
# Склеивает скрипт-установщик + AppImage в один файл.
#
# Использование:
#   ./create-installer.sh <путь-к-AppImage>
#
# Результат: SD-ON-Tool-Installer.sh — один файл,
# содержащий установщик и AppImage.
# =================================================================

set -euo pipefail

APPIMAGE="${1:-}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT="${2:-${SCRIPT_DIR}/../build/SD-ON-Tool-Installer.sh}"

if [ -z "$APPIMAGE" ] || [ ! -f "$APPIMAGE" ]; then
    echo "Использование: $0 <путь-к-AppImage> [выходной-файл]"
    exit 1
fi

APPIMAGE_SIZE=$(stat -c%s "$APPIMAGE")

echo "Создание установщика..."
echo "  AppImage: $APPIMAGE ($APPIMAGE_SIZE байт)"

# Записываем скрипт-установщик
cat > "$OUTPUT" << 'INSTALLER_HEADER'
#!/bin/bash
# =================================================================
# SD-ON Tool — Установщик для Steam Deck
# =================================================================
# Самодостаточный установщик. Содержит приложение внутри.
# Запустите этот файл для установки или удаления SD-ON Tool.
# =================================================================

set -euo pipefail

APP_NAME="SD-ON Tool"
APP_ID="sd-on-tool"
APP_VERSION="1.0.0"
APPIMAGE_NAME="SD-ON-Tool.AppImage"
INSTALL_DIR="$HOME/Applications"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
CONFIG_DIR="$HOME/.config/sd-on-tool"

# Размер AppImage (заполняется при сборке)
PAYLOAD_SIZE="__PAYLOAD_SIZE__"

# ─── GUI / Терминал ─────────────────────────────────────────────

HAS_ZENITY=false
if command -v zenity &>/dev/null; then
    HAS_ZENITY=true
fi

HAS_KDIALOG=false
if command -v kdialog &>/dev/null; then
    HAS_KDIALOG=true
fi

gui_message() {
    local title="$1" text="$2"
    if $HAS_ZENITY; then
        zenity --info --title="$title" --text="$text" --width=420 2>/dev/null
    elif $HAS_KDIALOG; then
        kdialog --title "$title" --msgbox "$text" 2>/dev/null
    else
        echo ""
        echo "  $text"
        echo ""
    fi
}

gui_error() {
    local title="$1" text="$2"
    if $HAS_ZENITY; then
        zenity --error --title="$title" --text="$text" --width=420 2>/dev/null
    elif $HAS_KDIALOG; then
        kdialog --title "$title" --error "$text" 2>/dev/null
    else
        echo ""
        echo "  ОШИБКА: $text"
        echo ""
    fi
}

gui_question() {
    local title="$1" text="$2"
    if $HAS_ZENITY; then
        zenity --question --title="$title" --text="$text" --width=420 2>/dev/null
        return $?
    elif $HAS_KDIALOG; then
        kdialog --title "$title" --yesno "$text" 2>/dev/null
        return $?
    else
        read -p "  $text (y/n): " -n 1 -r
        echo ""
        [[ $REPLY =~ ^[Yy]$ ]]
        return $?
    fi
}

gui_menu() {
    if $HAS_ZENITY; then
        zenity --list \
            --title="$APP_NAME v$APP_VERSION" \
            --text="Выберите действие:" \
            --column="" --column="Действие" \
            --hide-column=1 \
            --width=420 --height=280 \
            "install" "🔽  Установить $APP_NAME" \
            "uninstall" "🗑  Удалить $APP_NAME" \
            2>/dev/null || echo ""
    elif $HAS_KDIALOG; then
        kdialog --title "$APP_NAME v$APP_VERSION" \
            --menu "Выберите действие:" \
            "install" "🔽  Установить $APP_NAME" \
            "uninstall" "🗑  Удалить $APP_NAME" \
            2>/dev/null || echo ""
    else
        echo ""
        echo "╔══════════════════════════════════════════════╗"
        echo "║     $APP_NAME v$APP_VERSION — Установщик     ║"
        echo "╚══════════════════════════════════════════════╝"
        echo ""
        echo "  1) Установить $APP_NAME"
        echo "  2) Удалить $APP_NAME"
        echo "  0) Выход"
        echo ""
        read -p "  Выбор [1/2/0]: " -n 1 -r
        echo ""
        case "$REPLY" in
            1) echo "install" ;;
            2) echo "uninstall" ;;
            *) echo "" ;;
        esac
    fi
}

# ─── Извлечение AppImage ────────────────────────────────────────

extract_appimage() {
    local dest="$1"
    local script_size
    # Находим маркер и извлекаем всё после него
    script_size=$(grep -abn "^__PAYLOAD_BELOW__$" "$0" | tail -1 | cut -d: -f1)
    if [ -z "$script_size" ]; then
        gui_error "$APP_NAME" "Ошибка: не удалось найти данные AppImage в установщике."
        return 1
    fi
    tail -n +"$((script_size + 1))" "$0" | head -c "$PAYLOAD_SIZE" > "$dest"
    chmod +x "$dest"
}

# ─── SVG-иконка ─────────────────────────────────────────────────

create_icon() {
    mkdir -p "$ICON_DIR"
    cat > "$ICON_DIR/${APP_ID}.svg" << 'ICON_END'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" xmlns="http://www.w3.org/2000/svg">
  <rect width="256" height="256" rx="40" fill="#1a1a2e"/>
  <rect x="20" y="20" width="216" height="216" rx="30" fill="#16213e" stroke="#0f3460" stroke-width="3"/>
  <text x="128" y="115" font-family="Arial, sans-serif" font-size="52" font-weight="bold" fill="#e94560" text-anchor="middle">SD-ON</text>
  <text x="128" y="165" font-family="Arial, sans-serif" font-size="32" fill="#606080" text-anchor="middle">Tool</text>
</svg>
ICON_END
}

# ─── Установка ──────────────────────────────────────────────────

do_install() {
    echo "Установка $APP_NAME..."

    mkdir -p "$INSTALL_DIR"
    mkdir -p "$DESKTOP_DIR"

    # Прогресс-бар (zenity)
    if $HAS_ZENITY; then
        (
            echo "10"; echo "# Извлечение AppImage..."
            extract_appimage "$INSTALL_DIR/$APPIMAGE_NAME"

            echo "50"; echo "# Создание иконки..."
            create_icon

            echo "70"; echo "# Создание ярлыка..."
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

            echo "90"; echo "# Обновление кэша..."
            if command -v update-desktop-database &>/dev/null; then
                update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
            fi
            if command -v gtk-update-icon-cache &>/dev/null; then
                gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
            fi

            echo "100"; echo "# Готово!"
        ) | zenity --progress --title="Установка $APP_NAME" \
            --text="Подготовка..." --percentage=0 --auto-close --width=400 2>/dev/null

        if [ -f "$INSTALL_DIR/$APPIMAGE_NAME" ]; then
            gui_message "$APP_NAME" "✅ $APP_NAME v$APP_VERSION установлен!\n\n📁 Путь: $INSTALL_DIR/$APPIMAGE_NAME\n📋 Ярлык добавлен в меню приложений\n\n💡 Для радио установите mpv:\nsudo pacman -S mpv"
        else
            gui_error "$APP_NAME" "Не удалось установить $APP_NAME."
        fi
    else
        # Терминальный режим
        echo "  [1/4] Извлечение AppImage..."
        extract_appimage "$INSTALL_DIR/$APPIMAGE_NAME"

        echo "  [2/4] Создание иконки..."
        create_icon

        echo "  [3/4] Создание ярлыка..."
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

        echo "  [4/4] Обновление кэша..."
        if command -v update-desktop-database &>/dev/null; then
            update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
        fi

        echo ""
        echo "  ✅ $APP_NAME v$APP_VERSION установлен!"
        echo "  📁 $INSTALL_DIR/$APPIMAGE_NAME"
        echo "  📋 Ярлык добавлен в меню"
        echo ""
        echo "  💡 Для радио: sudo pacman -S mpv"
        echo ""
    fi
}

# ─── Удаление ───────────────────────────────────────────────────

do_uninstall() {
    if [ ! -f "$INSTALL_DIR/$APPIMAGE_NAME" ] && [ ! -f "$DESKTOP_DIR/${APP_ID}.desktop" ]; then
        gui_message "$APP_NAME" "$APP_NAME не установлен."
        return 0
    fi

    if ! gui_question "$APP_NAME — Удаление" "Удалить $APP_NAME?\n\nБудут удалены:\n• Приложение\n• Ярлык из меню\n• Иконка"; then
        return 0
    fi

    rm -f "$INSTALL_DIR/$APPIMAGE_NAME"
    rm -f "$DESKTOP_DIR/${APP_ID}.desktop"
    rm -f "$ICON_DIR/${APP_ID}.svg"

    if command -v update-desktop-database &>/dev/null; then
        update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    fi

    # Настройки
    if [ -d "$CONFIG_DIR" ]; then
        if gui_question "$APP_NAME" "Удалить настройки?\n(радиостанции, тема, насыщенность)"; then
            rm -rf "$CONFIG_DIR"
        fi
    fi

    gui_message "$APP_NAME" "✅ $APP_NAME удалён."
}

# ─── Главное меню ───────────────────────────────────────────────

main() {
    local choice
    choice="$(gui_menu)"

    case "$choice" in
        install)   do_install ;;
        uninstall) do_uninstall ;;
        *)
            echo "  Выход."
            ;;
    esac
}

main
exit 0

# Маркер начала бинарных данных — не удалять!
__PAYLOAD_BELOW__
INSTALLER_HEADER

# Подставляем реальный размер
sed -i "s/__PAYLOAD_SIZE__/$APPIMAGE_SIZE/" "$OUTPUT"

# Дописываем AppImage как бинарные данные
cat "$APPIMAGE" >> "$OUTPUT"
chmod +x "$OUTPUT"

TOTAL_SIZE=$(stat -c%s "$OUTPUT")
echo "  Установщик: $OUTPUT"
echo "  Размер: $(numfmt --to=iec $TOTAL_SIZE)"
echo "Готово!"
