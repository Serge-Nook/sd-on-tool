#!/usr/bin/env bash
#
# Генератор встроенных CSS-тем SD-ON Tool.
# Создаёт 20 файлов в payload/themes/. Каждая тема — самодостаточный
# локальный CSS-файл (загрузка из сети не используется).
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$HERE/payload/themes"
mkdir -p "$OUT"

# Формат записи: "Имя|slug|bg|panel|accent|text|muted"
THEMES=(
  "Classic|classic|#1b2838|#2a3f5a|#66c0f4|#e6e6e6|#9aa4af"
  "Dark|dark|#121212|#1e1e1e|#4f9dde|#eaeaea|#8a8a8a"
  "OLED Black|oled-black|#000000|#0a0a0a|#00d0ff|#f0f0f0|#6a6a6a"
  "Neon Blue|neon-blue|#0a0f1f|#111a33|#2f8bff|#dbe7ff|#5f77a8"
  "Neon Green|neon-green|#001108|#052112|#22ff88|#c9ffe0|#4f9c74"
  "Purple|purple|#150b24|#241238|#b46cff|#ecdcff|#8a6aa8"
  "Crimson|crimson|#1a0808|#2c0d0d|#ff4d5e|#ffd8dc|#a86b70"
  "Orange|orange|#1e1206|#30200c|#ff9a3c|#ffe6cc|#b0895f"
  "White|white|#f4f4f4|#ffffff|#0a84ff|#1c1c1e|#6b6b6f"
  "Gray|gray|#2b2b2b|#3a3a3a|#9aa4af|#e6e6e6|#8a8a8a"
  "Cyber|cyber|#0d0221|#190a33|#ff2fd6|#e6d6ff|#8a5fb0"
  "Carbon|carbon|#161616|#222222|#00b3a4|#e2e2e2|#7d7d7d"
  "Minimal|minimal|#fafafa|#ffffff|#333333|#222222|#888888"
  "Aurora|aurora|#04121a|#08202e|#3ee6c4|#d6fff5|#5aa898"
  "Steam Blue|steam-blue|#171a21|#1b2838|#417a9b|#dfe3e6|#8f98a0"
  "Retro|retro|#221a10|#33270f|#f2c14e|#f7e6c4|#b39a63"
  "Matrix|matrix|#000800|#031803|#00ff41|#c8ffce|#3f9a52"
  "Modern|modern|#101418|#1a2027|#5b8def|#e8edf2|#7e8896"
  "Glass|glass|#0f1420|#182034|#8fd3ff|#eaf4ff|#7f93ad"
  "SD-ON Theme|sd-on-theme|#12141c|#1c2030|#ff7a18|#f0f2f8|#8890a0"
)

for entry in "${THEMES[@]}"; do
  IFS='|' read -r name slug bg panel accent text muted <<< "$entry"
  cat > "$OUT/$slug.css" <<CSS
/*
 * SD-ON Tool — тема «$name».
 * Локальный CSS-файл, внедряется в интерфейс Steam инъекцией стилей.
 */
:root {
  --sdon-bg: $bg;
  --sdon-panel: $panel;
  --sdon-accent: $accent;
  --sdon-text: $text;
  --sdon-muted: $muted;
}

body,
[class*="mainmenu"],
[class*="quickaccessmenu"],
[class*="QuickAccess"] {
  background-color: var(--sdon-bg) !important;
  color: var(--sdon-text) !important;
}

[class*="Panel"],
[class*="Focusable"],
[class*="Field"] {
  background-color: var(--sdon-panel) !important;
}

a,
[class*="Active"],
[class*="Selected"] {
  color: var(--sdon-accent) !important;
}

[class*="Muted"],
[class*="Subtitle"] {
  color: var(--sdon-muted) !important;
}

/* Акцент SD-ON Tool внутри собственной панели. */
#sd-on-tool-root {
  background: var(--sdon-bg) !important;
  color: var(--sdon-text) !important;
}
#sd-on-tool-root .sd-tab.active {
  box-shadow: inset 0 -2px 0 var(--sdon-accent) !important;
  color: var(--sdon-text) !important;
}
#sd-on-tool-root .sd-btn:hover {
  background: var(--sdon-accent) !important;
}
CSS
done

count="$(find "$OUT" -maxdepth 1 -name '*.css' | wc -l)"
echo "Создано $count файлов тем в $OUT"
