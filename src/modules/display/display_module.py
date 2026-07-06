"""Модуль управления цветами экрана (насыщенность).

Использует xrandr CTM (Color Transform Matrix) для управления
насыщенностью цвета, аналогично VibrantDeck.
"""

import logging
import subprocess

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.core.config import Config
from src.core.module_base import ModuleBase
from src.ui.widgets import VolumeSlider

log = logging.getLogger(__name__)


def _build_ctm_matrix(saturation_pct: int) -> str:
    """Построить матрицу CTM для заданного уровня насыщенности.

    saturation_pct: 100 = нормальная, 200 = максимальная насыщенность.
    Используется алгоритм, аналогичный VibrantDeck.
    """
    s = saturation_pct / 100.0

    # Коэффициенты яркости (BT.709)
    lr, lg, lb = 0.2126, 0.7152, 0.0722

    r_r = (1.0 - s) * lr + s
    r_g = (1.0 - s) * lg
    r_b = (1.0 - s) * lb

    g_r = (1.0 - s) * lr
    g_g = (1.0 - s) * lg + s
    g_b = (1.0 - s) * lb

    b_r = (1.0 - s) * lr
    b_g = (1.0 - s) * lg
    b_b = (1.0 - s) * lb + s

    def _to_ctm(val: float) -> str:
        if val < 0:
            val = abs(val)
            sign = 1 << 63
        else:
            sign = 0
        integer = int(val)
        frac = int((val - integer) * (1 << 32))
        raw = sign | (integer << 32) | frac
        return str(raw)

    values = [r_r, r_g, r_b, g_r, g_g, g_b, b_r, b_g, b_b]
    return ":".join(_to_ctm(v) for v in values)


def _get_display_output() -> str:
    """Определить текущий подключённый выход дисплея."""
    try:
        result = subprocess.run(
            ["xrandr", "--listmonitors"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.splitlines():
            line = line.strip()
            # Формат: " 0: +*eDP-1 1280/..."
            if ":" in line and "/" in line:
                parts = line.split()
                for part in parts:
                    if any(
                        part.startswith(prefix)
                        for prefix in ("eDP", "DP", "HDMI", "DSI")
                    ):
                        return part.lstrip("+*")
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return "eDP-1"


class DisplayModule(ModuleBase):
    """Модуль настройки насыщенности экрана (аналог VibrantDeck)."""

    def __init__(self, config: Config):
        super().__init__(config)
        self._widget: QWidget | None = None
        self._saturation = config.get("saturation", 100)
        self._status_label: QLabel | None = None
        self._display_output = ""

    def get_name(self) -> str:
        return "Цвета экрана"

    def get_icon_name(self) -> str:
        return "display"

    def get_widget(self) -> QWidget:
        if self._widget is not None:
            return self._widget

        self._widget = QWidget()
        layout = QVBoxLayout(self._widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        title = QLabel("🖥 Цвета экрана")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        subtitle = QLabel(
            "Расширенная настройка насыщенности изображения • "
            "Аналог VibrantDeck"
        )
        subtitle.setObjectName("subtitleLabel")
        layout.addWidget(subtitle)

        # Информационная карточка
        info_card = QFrame()
        info_card.setObjectName("cardFrame")
        info_layout = QVBoxLayout(info_card)
        info_layout.setSpacing(8)

        info_title = QLabel("Как это работает")
        info_title.setObjectName("sectionLabel")
        info_layout.addWidget(info_title)

        info_text = QLabel(
            "Регулировка насыщенности расширяет диапазон цветов за пределы "
            "стандартных настроек SteamOS.\n"
            "100% — стандартный уровень, 200% — максимальная насыщенность.\n"
            "Используется матрица преобразования цветов (CTM) через xrandr."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #808090; font-size: 13px;")
        info_layout.addWidget(info_text)

        layout.addWidget(info_card)

        # Статус
        self._status_label = QLabel(f"Текущая насыщенность: {self._saturation}%")
        self._status_label.setStyleSheet(
            "color: #e94560; font-size: 16px; font-weight: 600; "
            "background: #16213e; border-radius: 10px; padding: 12px 16px;"
        )
        self._status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._status_label)

        # Слайдер насыщенности
        self._slider = VolumeSlider(
            "Насыщенность", 100, 200, self._saturation, "%"
        )
        self._slider.value_changed.connect(self._on_saturation_change)
        layout.addWidget(self._slider)

        # Быстрые пресеты
        presets_label = QLabel("Быстрые пресеты")
        presets_label.setObjectName("sectionLabel")
        layout.addWidget(presets_label)

        presets_layout = QHBoxLayout()
        presets_layout.setSpacing(12)
        presets = [
            ("100%\nСтандарт", 100),
            ("120%\nЛёгкое", 120),
            ("140%\nУмеренное", 140),
            ("160%\nВысокое", 160),
            ("180%\nОчень\nвысокое", 180),
            ("200%\nМаксимум", 200),
        ]
        for label, value in presets:
            btn = QPushButton(label)
            btn.setObjectName("secondaryButton")
            btn.setStyleSheet(
                "QPushButton { min-height: 64px; font-size: 12px; }"
                "QPushButton:hover { background: #e94560; color: white; }"
            )
            btn.clicked.connect(lambda checked, v=value: self._set_saturation(v))
            presets_layout.addWidget(btn)
        layout.addLayout(presets_layout)

        # Кнопки применения
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        apply_btn = QPushButton("Применить")
        apply_btn.setObjectName("actionButton")
        apply_btn.clicked.connect(self._on_apply)
        btn_layout.addWidget(apply_btn)

        reset_btn = QPushButton("Сбросить")
        reset_btn.setObjectName("secondaryButton")
        reset_btn.clicked.connect(self._on_reset)
        btn_layout.addWidget(reset_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

        return self._widget

    def _on_saturation_change(self, value: int):
        self._saturation = value
        if self._status_label:
            self._status_label.setText(f"Текущая насыщенность: {value}%")

    def _set_saturation(self, value: int):
        self._saturation = value
        self._slider.set_value(value)
        if self._status_label:
            self._status_label.setText(f"Текущая насыщенность: {value}%")

    def _on_apply(self):
        self._apply_saturation(self._saturation)
        self._config.set("saturation", self._saturation)

    def _on_reset(self):
        self._set_saturation(100)
        self._apply_saturation(100)
        self._config.set("saturation", 100)

    def _apply_saturation(self, saturation: int):
        if not self._display_output:
            self._display_output = _get_display_output()

        ctm = _build_ctm_matrix(saturation)
        try:
            subprocess.run(
                [
                    "xrandr",
                    "--output", self._display_output,
                    "--set", "CTM", ctm,
                ],
                capture_output=True, text=True, timeout=5,
            )
            log.info(
                "Насыщенность применена: %d%% на %s",
                saturation, self._display_output,
            )
        except FileNotFoundError:
            log.error("xrandr не найден")
        except subprocess.TimeoutExpired:
            log.error("Таймаут xrandr")
        except OSError as e:
            log.error("Ошибка xrandr: %s", e)

    def on_activate(self):
        saved = self._config.get("saturation", 100)
        if saved != self._saturation:
            self._set_saturation(saved)

    def cleanup(self):
        pass
