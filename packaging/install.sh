#!/bin/bash
# =================================================================
# SD-ON Tool — Скрипт установки на Steam Deck
# =================================================================
# Использование:
#   chmod +x install.sh
#   ./install.sh SD-ON-Tool-1.0.0-x86_64.AppImage
# =================================================================

set -euo pipefail

APPIMAGE="${1:-}"
INSTALL_DIR="$HOME/Applications"
DESKTOP_DIR="$HOME/.local/share/applications"

if [ -z "$APPIMAGE" ]; then
    echo "Использование: $0 <путь-к-AppImage>"
    exit 1
fi

if [ ! -f "$APPIMAGE" ]; then
    echo "Файл не найден: $APPIMAGE"
    exit 1
fi

echo "╔══════════════════════════════════════════╗"
echo "║     SD-ON Tool — Установка              ║"
echo "╚══════════════════════════════════════════╝"

# Создание директорий
mkdir -p "$INSTALL_DIR"
mkdir -p "$DESKTOP_DIR"

# Копирование AppImage
cp "$APPIMAGE" "$INSTALL_DIR/SD-ON-Tool.AppImage"
chmod +x "$INSTALL_DIR/SD-ON-Tool.AppImage"

# Создание ярлыка
cat > "$DESKTOP_DIR/sd-on-tool.desktop" << DESKTOP
[Desktop Entry]
Type=Application
Name=SD-ON Tool
Comment=Автономное приложение настройки Steam Deck
Exec=$INSTALL_DIR/SD-ON-Tool.AppImage
Icon=sd-on-tool
Categories=Utility;System;
Terminal=false
StartupWMClass=SD-ON Tool
DESKTOP

echo ""
echo "✓ SD-ON Tool установлен в: $INSTALL_DIR/SD-ON-Tool.AppImage"
echo "✓ Ярлык создан: $DESKTOP_DIR/sd-on-tool.desktop"
echo ""
echo "Запуск:"
echo "  $INSTALL_DIR/SD-ON-Tool.AppImage"
