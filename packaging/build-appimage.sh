#!/bin/bash
# =================================================================
# SD-ON Tool — Скрипт сборки AppImage
# =================================================================
# Использование:
#   chmod +x packaging/build-appimage.sh
#   ./packaging/build-appimage.sh
#
# Требования:
#   - Python 3.10+
#   - pip
#   - wget (для загрузки appimagetool)
# =================================================================

set -euo pipefail

APP_NAME="SD-ON-Tool"
APP_VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$PROJECT_DIR/build"
APPDIR="$BUILD_DIR/${APP_NAME}.AppDir"

echo "╔══════════════════════════════════════════════╗"
echo "║        SD-ON Tool — Сборка AppImage          ║"
echo "║        Версия: ${APP_VERSION}                        ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Очистка
rm -rf "$BUILD_DIR"
mkdir -p "$APPDIR"

echo "[1/5] Создание виртуального окружения..."
python3 -m venv "$BUILD_DIR/venv"
source "$BUILD_DIR/venv/bin/activate"
pip install --upgrade pip > /dev/null 2>&1
pip install -r "$PROJECT_DIR/requirements.txt" > /dev/null 2>&1
pip install pyinstaller > /dev/null 2>&1

echo "[2/5] Сборка через PyInstaller..."
cd "$PROJECT_DIR"
pyinstaller \
    --noconfirm \
    --clean \
    --name "$APP_NAME" \
    --onedir \
    --windowed \
    --add-data "src:src" \
    --hidden-import "PyQt5.QtCore" \
    --hidden-import "PyQt5.QtGui" \
    --hidden-import "PyQt5.QtWidgets" \
    --distpath "$BUILD_DIR/dist" \
    --workpath "$BUILD_DIR/work" \
    --specpath "$BUILD_DIR" \
    main.py

echo "[3/5] Подготовка AppDir..."

# Структура AppDir
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

# Копирование собранного приложения
cp -r "$BUILD_DIR/dist/$APP_NAME/"* "$APPDIR/usr/bin/"

# Desktop файл
cat > "$APPDIR/usr/share/applications/${APP_NAME}.desktop" << DESKTOP
[Desktop Entry]
Type=Application
Name=SD-ON Tool
Comment=Автономное приложение настройки Steam Deck
Exec=SD-ON-Tool
Icon=sd-on-tool
Categories=Utility;System;
Terminal=false
StartupWMClass=SD-ON Tool
DESKTOP

cp "$APPDIR/usr/share/applications/${APP_NAME}.desktop" "$APPDIR/${APP_NAME}.desktop"

# Создание простой иконки SVG
cat > "$APPDIR/sd-on-tool.svg" << 'SVG'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" xmlns="http://www.w3.org/2000/svg">
  <rect width="256" height="256" rx="40" fill="#1a1a2e"/>
  <rect x="20" y="20" width="216" height="216" rx="30" fill="#16213e" stroke="#0f3460" stroke-width="3"/>
  <text x="128" y="115" font-family="Arial, sans-serif" font-size="52" font-weight="bold" fill="#e94560" text-anchor="middle">SD-ON</text>
  <text x="128" y="165" font-family="Arial, sans-serif" font-size="32" fill="#606080" text-anchor="middle">Tool</text>
</svg>
SVG

cp "$APPDIR/sd-on-tool.svg" "$APPDIR/usr/share/icons/hicolor/256x256/apps/sd-on-tool.svg"

# AppRun скрипт
cat > "$APPDIR/AppRun" << 'APPRUN'
#!/bin/bash
SELF="$(readlink -f "$0")"
HERE="${SELF%/*}"
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH:-}"
exec "${HERE}/usr/bin/SD-ON-Tool" "$@"
APPRUN

chmod +x "$APPDIR/AppRun"

echo "[4/5] Загрузка appimagetool..."
ARCH="$(uname -m)"
TOOL_URL="https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-${ARCH}.AppImage"
TOOL_PATH="$BUILD_DIR/appimagetool"

if [ ! -f "$TOOL_PATH" ]; then
    wget -q "$TOOL_URL" -O "$TOOL_PATH" || {
        echo "  ⚠ Не удалось загрузить appimagetool."
        echo "  Создан AppDir: $APPDIR"
        echo "  Для ручной сборки:"
        echo "    appimagetool $APPDIR $BUILD_DIR/${APP_NAME}-${APP_VERSION}-${ARCH}.AppImage"
        exit 0
    }
    chmod +x "$TOOL_PATH"
fi

echo "[5/5] Сборка AppImage..."
APPIMAGE_OUTPUT="$BUILD_DIR/${APP_NAME}-${APP_VERSION}-${ARCH}.AppImage"
"$TOOL_PATH" --appimage-extract-and-run "$APPDIR" "$APPIMAGE_OUTPUT" 2>/dev/null || {
    echo "  ⚠ Ошибка appimagetool. AppDir готов: $APPDIR"
    exit 0
}

echo ""
echo "═══════════════════════════════════════════════"
echo " ✓ AppImage собран: $APPIMAGE_OUTPUT"
echo " Размер: $(du -h "$APPIMAGE_OUTPUT" | cut -f1)"
echo "═══════════════════════════════════════════════"
echo ""
echo "Установка на Steam Deck:"
echo "  1. Скопируйте .AppImage на Steam Deck"
echo "  2. chmod +x ${APP_NAME}-${APP_VERSION}-${ARCH}.AppImage"
echo "  3. Запустите файл"
