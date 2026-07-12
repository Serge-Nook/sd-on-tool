#!/usr/bin/env bash
#
# Сборка самодостаточного установщика SD-ON-Tool-Installer.sh.
#
# Итоговый .sh содержит внутри себя (в виде бинарного архива tar.gz после
# маркера) все файлы программы: install.sh, scripts/, payload/. При запуске
# он самораспаковывается во временную директорию и открывает GUI установщика.
#
# Результат: dist/SD-ON-Tool-Installer.sh
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${SD_ON_TOOL_VERSION:-2.0.0}"
OUT_DIR="$HERE/dist"
OUT="$OUT_DIR/SD-ON-Tool-Installer.sh"

mkdir -p "$OUT_DIR"

# Собираем полезную нагрузку во временную директорию (с подстановкой версии).
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

mkdir -p "$STAGE/scripts" "$STAGE/bin" "$STAGE/packaging" "$STAGE/app"
cp "$HERE/install.sh" "$STAGE/install.sh"
cp "$HERE/scripts/installer.sh" "$STAGE/scripts/installer.sh"
cp "$HERE/scripts/gen-themes.sh" "$STAGE/scripts/gen-themes.sh"
cp "$HERE/bin/sd-on-tool" "$STAGE/bin/sd-on-tool"
cp "$HERE/packaging/sd-on-tool.desktop" "$STAGE/packaging/sd-on-tool.desktop"
cp -r "$HERE/app/." "$STAGE/app/"
sed "s/__SD_ON_TOOL_VERSION__/$VERSION/g" "$HERE/app/app.js" > "$STAGE/app/app.js"
printf '%s\n' "$VERSION" > "$STAGE/VERSION"

# Заголовок-установщик: находит архив после маркера, распаковывает и
# запускает install.sh. Маркер записывается literally, без раскрытия.
cat > "$OUT" <<HEADER
#!/usr/bin/env bash
# =================================================================
# SD-ON Tool — самодостаточный установщик (версия $VERSION)
# =================================================================
# Запустите этот файл для установки или удаления SD-ON Tool:
#   chmod +x SD-ON-Tool-Installer.sh
#   ./SD-ON-Tool-Installer.sh
# =================================================================
set -euo pipefail

MARKER="__SDON_ARCHIVE_BELOW__"
SELF="\$0"
WORK="\$(mktemp -d)"
cleanup() { rm -rf "\$WORK"; }
trap cleanup EXIT

ARCHIVE_LINE="\$(awk "/^\${MARKER}\$/{print NR + 1; exit}" "\$SELF")"
if [ -z "\$ARCHIVE_LINE" ]; then
  echo "Ошибка: архив внутри установщика не найден." >&2
  exit 1
fi

tail -n +"\$ARCHIVE_LINE" "\$SELF" | tar -xzC "\$WORK"
bash "\$WORK/install.sh"
HEADER

echo "__SDON_ARCHIVE_BELOW__" >> "$OUT"

# Дописываем бинарный архив сразу после маркера.
( cd "$STAGE" && tar -czf - . ) >> "$OUT"

chmod +x "$OUT"
echo "Собран самодостаточный установщик: $OUT"
echo "Версия: $VERSION, размер: $(wc -c < "$OUT") байт"
