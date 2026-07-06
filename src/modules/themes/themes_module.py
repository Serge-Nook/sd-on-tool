"""Модуль управления темами оформления Steam Deck."""

import logging
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.core.config import Config
from src.core.module_base import ModuleBase
from src.modules.themes.theme_data import BUILTIN_THEMES, DEFAULT_THEME_NAME, ThemeInfo
from src.ui.widgets import ThemeCard

log = logging.getLogger(__name__)

# Возможные пути для инъекции CSS в Steam UI
_STEAM_CSS_PATHS = [
    Path.home() / ".steam" / "steam" / "steamui" / "libraryroot.custom.css",
    Path.home() / ".local" / "share" / "Steam" / "steamui" / "libraryroot.custom.css",
]


class ThemesModule(ModuleBase):
    """Модуль тем оформления интерфейса Steam Deck."""

    def __init__(self, config: Config):
        super().__init__(config)
        self._widget: QWidget | None = None
        self._themes_layout: QVBoxLayout | None = None
        self._current_theme = config.get("theme", DEFAULT_THEME_NAME)
        self._status_label: QLabel | None = None

    def get_name(self) -> str:
        return "Темы"

    def get_icon_name(self) -> str:
        return "themes"

    def get_widget(self) -> QWidget:
        if self._widget is not None:
            return self._widget

        self._widget = QWidget()
        layout = QVBoxLayout(self._widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        title = QLabel("🎨 Темы оформления")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        subtitle = QLabel(
            "Встроенные темы для интерфейса Steam Deck • "
            "Все темы работают автономно"
        )
        subtitle.setObjectName("subtitleLabel")
        layout.addWidget(subtitle)

        # Статус
        status_layout = QHBoxLayout()
        self._status_label = QLabel(f"Текущая тема: {self._current_theme}")
        self._status_label.setStyleSheet(
            "color: #e94560; font-size: 15px; font-weight: 600; "
            "background: #16213e; border-radius: 10px; padding: 10px 16px;"
        )
        status_layout.addWidget(self._status_label, stretch=1)

        reset_btn = QPushButton("Сбросить по умолчанию")
        reset_btn.setObjectName("secondaryButton")
        reset_btn.clicked.connect(self._on_reset)
        status_layout.addWidget(reset_btn)

        layout.addLayout(status_layout)

        # Список тем
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        themes_widget = QWidget()
        self._themes_layout = QVBoxLayout(themes_widget)
        self._themes_layout.setSpacing(8)
        self._themes_layout.setContentsMargins(0, 0, 8, 0)
        self._themes_layout.addStretch()

        scroll.setWidget(themes_widget)
        layout.addWidget(scroll, stretch=1)

        self._rebuild_theme_list()
        return self._widget

    def _rebuild_theme_list(self):
        layout = self._themes_layout
        while layout.count() > 1:
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for theme in BUILTIN_THEMES:
            is_active = theme.name == self._current_theme
            card = ThemeCard(
                theme.name,
                theme.description,
                theme.preview_color,
                is_active,
            )
            card.clicked.connect(
                lambda t=theme: self._on_apply_theme(t)
            )
            layout.insertWidget(layout.count() - 1, card)

    def _on_apply_theme(self, theme: ThemeInfo):
        self._current_theme = theme.name
        self._config.set("theme", theme.name)
        self._apply_css(theme.css)
        if self._status_label:
            self._status_label.setText(f"Текущая тема: {theme.name}")
        self._rebuild_theme_list()

    def _on_reset(self):
        default = next(
            (t for t in BUILTIN_THEMES if t.name == DEFAULT_THEME_NAME),
            BUILTIN_THEMES[-1],
        )
        self._on_apply_theme(default)

    @staticmethod
    def _apply_css(css: str):
        applied = False
        for css_path in _STEAM_CSS_PATHS:
            if css_path.parent.exists():
                try:
                    css_path.write_text(css, encoding="utf-8")
                    applied = True
                    log.info("Тема применена: %s", css_path)
                    break
                except OSError as e:
                    log.warning("Не удалось записать %s: %s", css_path, e)

        if not applied:
            backup_dir = Path.home() / ".config" / "sd-on-tool" / "themes"
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup = backup_dir / "current_theme.css"
            try:
                backup.write_text(css, encoding="utf-8")
                log.info("Тема сохранена в резервную копию: %s", backup)
            except OSError as e:
                log.error("Не удалось сохранить тему: %s", e)

    @staticmethod
    def _remove_css():
        for css_path in _STEAM_CSS_PATHS:
            if css_path.exists():
                try:
                    css_path.unlink()
                    log.info("CSS удалён: %s", css_path)
                except OSError as e:
                    log.warning("Не удалось удалить %s: %s", css_path, e)

    def on_activate(self):
        self._rebuild_theme_list()

    def cleanup(self):
        pass
