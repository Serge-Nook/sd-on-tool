#!/usr/bin/env bash
#
# SD-ON Tool — графический установщик.
#
# Запускается из SD-ON-Tool-Installer.desktop. Открывает окно с выбором
# «Установить» / «Удалить» и вызывает scripts/installer.sh.
# Если графические диалоги недоступны, работает в текстовом режиме.
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALLER="$HERE/scripts/installer.sh"

run() {
  local action="$1"
  bash "$INSTALLER" "$action"
}

# Определяем доступный инструмент диалогов.
DIALOG=""
if command -v zenity >/dev/null 2>&1; then
  DIALOG="zenity"
elif command -v kdialog >/dev/null 2>&1; then
  DIALOG="kdialog"
fi

gui_zenity() {
  local choice
  choice="$(zenity --list --title="SD-ON Tool" \
    --text="Выберите действие:" \
    --radiolist --column="" --column="Действие" \
    TRUE "Установить" FALSE "Удалить" \
    --width=360 --height=220 2>/dev/null || true)"
  case "$choice" in
    "Установить")
      if out="$(run install 2>&1)"; then
        zenity --info --title="SD-ON Tool" --text="$out" --width=420
      else
        zenity --error --title="SD-ON Tool" --text="$out" --width=420
      fi
      ;;
    "Удалить")
      if out="$(run uninstall 2>&1)"; then
        zenity --info --title="SD-ON Tool" --text="$out" --width=420
      else
        zenity --error --title="SD-ON Tool" --text="$out" --width=420
      fi
      ;;
    *) : ;;
  esac
}

gui_kdialog() {
  if kdialog --title "SD-ON Tool" \
      --yesno "Установить SD-ON Tool?\n(Нет — открыть удаление)"; then
    if out="$(run install 2>&1)"; then kdialog --msgbox "$out"; else kdialog --error "$out"; fi
  else
    if kdialog --title "SD-ON Tool" --yesno "Удалить SD-ON Tool?"; then
      if out="$(run uninstall 2>&1)"; then kdialog --msgbox "$out"; else kdialog --error "$out"; fi
    fi
  fi
}

cli() {
  echo "SD-ON Tool — установщик"
  echo "1) Установить"
  echo "2) Удалить"
  echo "3) Состояние"
  echo "0) Выход"
  read -r -p "Выбор: " ans
  case "$ans" in
    1) run install ;;
    2) run uninstall ;;
    3) run status ;;
    *) echo "Отмена." ;;
  esac
}

case "$DIALOG" in
  zenity)  gui_zenity ;;
  kdialog) gui_kdialog ;;
  *)       cli ;;
esac
