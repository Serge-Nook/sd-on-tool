"""Данные встроенных тем оформления Steam Deck.

Каждая тема — CSS, инжектируемый в интерфейс Steam через
~/.steam/steam/steamui/libraryroot.custom.css или аналогичный механизм.
"""


class ThemeInfo:
    """Описание темы оформления."""

    __slots__ = ("name", "description", "preview_color", "css")

    def __init__(self, name: str, description: str, preview_color: str, css: str):
        self.name = name
        self.description = description
        self.preview_color = preview_color
        self.css = css


def _make_theme(accent: str, bg: str, text: str, secondary: str) -> str:
    return f"""
/* SD-ON Tool Theme */
:root {{
    --gpSystemLighterGrey: {secondary} !important;
    --gpSystemLightGrey: {secondary} !important;
    --gpSystemDarkGrey: {bg} !important;
    --gpSystemDarkerGrey: {bg} !important;
    --gpSystemDarkestGrey: {bg} !important;
    --gpColor-Blue: {accent} !important;
    --gpColor-Green: {accent} !important;
}}

.basicui_Header_2XTQH,
.gamepadui_Header_2XTQH {{
    background: {bg} !important;
}}

.gamepadui_ItemFocusAnim-darkerGrey-focusRing {{
    border-color: {accent} !important;
}}

.Panel.Focusable {{
    background: {bg} !important;
    color: {text} !important;
}}

.gamepadtabbedpage_Tab_3eEbS.gamepadtabbedpage_Active_1C1EA {{
    background: {accent} !important;
    color: {text} !important;
}}

.DialogBody,
.DialogBodyText,
.DialogHeader {{
    color: {text} !important;
}}

.gamepadui_Button_12EaR {{
    background: {secondary} !important;
}}

.gamepadui_Button_12EaR.gamepadui_ActiveButton_1EN4T,
.gamepadui_Button_12EaR:hover {{
    background: {accent} !important;
}}
"""


BUILTIN_THEMES: list[ThemeInfo] = [
    ThemeInfo(
        "Classic",
        "Классическая тема Steam",
        "#171a21",
        _make_theme("#1a9fff", "#171a21", "#c7d5e0", "#2a475e"),
    ),
    ThemeInfo(
        "Dark",
        "Тёмная тема",
        "#121212",
        _make_theme("#bb86fc", "#121212", "#e0e0e0", "#1e1e1e"),
    ),
    ThemeInfo(
        "OLED Black",
        "Чисто-чёрная тема для OLED",
        "#000000",
        _make_theme("#00e5ff", "#000000", "#ffffff", "#0a0a0a"),
    ),
    ThemeInfo(
        "Neon Blue",
        "Неоновый синий акцент",
        "#0066ff",
        _make_theme("#0066ff", "#0a0a1a", "#e0e8ff", "#101030"),
    ),
    ThemeInfo(
        "Neon Green",
        "Неоновый зелёный акцент",
        "#00ff88",
        _make_theme("#00ff88", "#0a1a0a", "#e0ffe0", "#102010"),
    ),
    ThemeInfo(
        "Purple",
        "Фиолетовая тема",
        "#7b2fbe",
        _make_theme("#7b2fbe", "#1a0a2e", "#e0d0f0", "#2a1540"),
    ),
    ThemeInfo(
        "Crimson",
        "Тёмно-красная тема",
        "#dc143c",
        _make_theme("#dc143c", "#1a0a0a", "#f0d0d0", "#2a1010"),
    ),
    ThemeInfo(
        "Orange",
        "Оранжевая тема",
        "#ff6600",
        _make_theme("#ff6600", "#1a1008", "#f0e0d0", "#2a1a10"),
    ),
    ThemeInfo(
        "White",
        "Светлая тема",
        "#f0f0f0",
        _make_theme("#0066cc", "#f0f0f0", "#1a1a1a", "#e0e0e0"),
    ),
    ThemeInfo(
        "Gray",
        "Серая нейтральная тема",
        "#4a4a4a",
        _make_theme("#808080", "#2a2a2a", "#d0d0d0", "#3a3a3a"),
    ),
    ThemeInfo(
        "Cyber",
        "Киберпанк-стиль",
        "#ff00ff",
        _make_theme("#ff00ff", "#0a0014", "#f0e0ff", "#1a0028"),
    ),
    ThemeInfo(
        "Carbon",
        "Карбоновая тема",
        "#333333",
        _make_theme("#ff4400", "#1a1a1a", "#c8c8c8", "#2a2a2a"),
    ),
    ThemeInfo(
        "Minimal",
        "Минималистичная тема",
        "#2c2c2c",
        _make_theme("#ffffff", "#1c1c1c", "#e0e0e0", "#2c2c2c"),
    ),
    ThemeInfo(
        "Aurora",
        "Северное сияние",
        "#00c9a7",
        _make_theme("#00c9a7", "#0a1628", "#d0f0e8", "#102438"),
    ),
    ThemeInfo(
        "Steam Blue",
        "Фирменный синий Steam",
        "#1b2838",
        _make_theme("#66c0f4", "#1b2838", "#c7d5e0", "#2a475e"),
    ),
    ThemeInfo(
        "Retro",
        "Ретро-стиль",
        "#8b4513",
        _make_theme("#ffa500", "#1a1006", "#f5deb3", "#2a1a0a"),
    ),
    ThemeInfo(
        "Matrix",
        "Стиль «Матрицы»",
        "#003300",
        _make_theme("#00ff00", "#000a00", "#00ff00", "#001a00"),
    ),
    ThemeInfo(
        "Modern",
        "Современная тёмная тема",
        "#1e1e2e",
        _make_theme("#89b4fa", "#1e1e2e", "#cdd6f4", "#313244"),
    ),
    ThemeInfo(
        "Glass",
        "Полупрозрачная тема",
        "#1a1a3e",
        _make_theme("#88ccff", "#0d0d1e", "#c0d0e0", "#1a1a3e"),
    ),
    ThemeInfo(
        "SD-ON Theme",
        "Фирменная тема SD-ON Tool",
        "#e94560",
        _make_theme("#e94560", "#1a1a2e", "#e0e0f0", "#16213e"),
    ),
]

DEFAULT_THEME_NAME = "SD-ON Theme"
