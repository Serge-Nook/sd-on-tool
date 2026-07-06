#!/bin/bash
# =================================================================
# SD-ON Tool — Скрипт удаления
# =================================================================

set -euo pipefail

INSTALL_DIR="$HOME/Applications"
DESKTOP_DIR="$HOME/.local/share/applications"
CONFIG_DIR="$HOME/.config/sd-on-tool"

echo "╔══════════════════════════════════════════╗"
echo "║     SD-ON Tool — Удаление               ║"
echo "╚══════════════════════════════════════════╝"

echo ""
read -p "Удалить SD-ON Tool? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Отменено."
    exit 0
fi

# Удаление AppImage
if [ -f "$INSTALL_DIR/SD-ON-Tool.AppImage" ]; then
    rm "$INSTALL_DIR/SD-ON-Tool.AppImage"
    echo "✓ Удалён: $INSTALL_DIR/SD-ON-Tool.AppImage"
fi

# Удаление ярлыка
if [ -f "$DESKTOP_DIR/sd-on-tool.desktop" ]; then
    rm "$DESKTOP_DIR/sd-on-tool.desktop"
    echo "✓ Удалён: $DESKTOP_DIR/sd-on-tool.desktop"
fi

# Спросить про настройки
echo ""
read -p "Удалить настройки? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "$CONFIG_DIR" ]; then
        rm -rf "$CONFIG_DIR"
        echo "✓ Настройки удалены: $CONFIG_DIR"
    fi
fi

echo ""
echo "SD-ON Tool удалён."
