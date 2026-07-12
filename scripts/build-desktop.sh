#!/usr/bin/env bash
#
# Сборка самодостаточного установщика SD-ON-Tool-Installer.desktop.
#
# Итоговый .desktop содержит внутри себя (в виде base64) все файлы программы:
# install.sh, scripts/, payload/ (js, темы, assets, settings.json). При запуске
# он самораспаковывается во временную директорию и открывает GUI установщика.
#
# Результат: dist/SD-ON-Tool-Installer.desktop
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${SD_ON_TOOL_VERSION:-1.0.0}"
OUT_DIR="$HERE/dist"
OUT="$OUT_DIR/SD-ON-Tool-Installer.desktop"

mkdir -p "$OUT_DIR"

# Собираем полезную нагрузку во временную директорию (с подстановкой версии).
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

mkdir -p "$STAGE/scripts" "$STAGE/payload"
cp "$HERE/install.sh" "$STAGE/install.sh"
cp "$HERE/scripts/installer.sh" "$STAGE/scripts/installer.sh"
cp "$HERE/scripts/gen-themes.sh" "$STAGE/scripts/gen-themes.sh"
cp -r "$HERE/payload/." "$STAGE/payload/"
sed "s/__SD_ON_TOOL_VERSION__/$VERSION/g" "$HERE/payload/sd-on-tool.js" > "$STAGE/payload/sd-on-tool.js"
printf '%s\n' "$VERSION" > "$STAGE/VERSION"

# Архивируем и кодируем в base64.
ARCHIVE_B64="$(cd "$STAGE" && tar -czf - . | base64 -w0 2>/dev/null || (cd "$STAGE" && tar -czf - . | base64))"

# Заголовок .desktop. Exec самораспаковывает архив, спрятанный после маркера
# (каждая строка base64 предварена '#', чтобы файл оставался валидным .desktop),
# и запускает install.sh.
cat > "$OUT" <<'DESKTOP'
[Desktop Entry]
Type=Application
Version=1.0
Name=SD-ON Tool Installer
Name[ru]=Установщик SD-ON Tool
Comment=Установка и удаление SD-ON Tool для Steam Deck
Comment[ru]=Установка и удаление SD-ON Tool для Steam Deck
Terminal=false
Categories=Utility;
StartupNotify=true
Exec=bash -c 'set -e; self="%k"; self="${self#file://}"; work="$(mktemp -d)"; sed -n "/^#SDON_PAYLOAD_BEGIN/,/^#SDON_PAYLOAD_END/p" "$self" | sed "1d;\$d;s/^#//" | base64 -d | tar -xzC "$work"; exec bash "$work/install.sh"'
DESKTOP

# Дописываем полезную нагрузку в виде закомментированных base64-строк.
{
  echo "#SDON_PAYLOAD_BEGIN"
  printf '%s' "$ARCHIVE_B64" | fold -w 120 | sed 's/^/#/'
  echo ""
  echo "#SDON_PAYLOAD_END"
} >> "$OUT"

chmod +x "$OUT"
echo "Собран самодостаточный установщик: $OUT"
echo "Версия: $VERSION, размер: $(wc -c < "$OUT") байт"
