"""Кастомные виджеты SD-ON Tool."""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class CardFrame(QFrame):
    """Карточка с закруглёнными углами."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("cardFrame")


class StationCard(QFrame):
    """Карточка радиостанции."""

    clicked = pyqtSignal()
    edit_requested = pyqtSignal()
    delete_requested = pyqtSignal()

    def __init__(self, name: str, url: str, is_active: bool = False,
                 is_custom: bool = False, parent=None):
        super().__init__(parent)
        self.station_name = name
        self.station_url = url
        self.is_custom = is_custom
        self.setObjectName("activeStationCard" if is_active else "stationCard")
        self.setCursor(Qt.PointingHandCursor)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        info_layout = QVBoxLayout()
        name_label = QLabel(self.station_name)
        name_label.setObjectName("sectionLabel")
        name_label.setStyleSheet("font-size: 14px; padding: 0;")
        info_layout.addWidget(name_label)

        url_label = QLabel(self.station_url)
        url_label.setObjectName("subtitleLabel")
        url_label.setStyleSheet("font-size: 11px; color: #606080;")
        url_label.setMaximumWidth(400)
        url_label.setWordWrap(False)
        info_layout.addWidget(url_label)

        layout.addLayout(info_layout, stretch=1)

        if self.is_custom:
            edit_btn = QPushButton("✎")
            edit_btn.setFixedSize(36, 36)
            edit_btn.setStyleSheet(
                "QPushButton { background: #0f3460; color: #a0a0b0; "
                "border-radius: 18px; font-size: 16px; border: none; }"
                "QPushButton:hover { background: #e94560; color: white; }"
            )
            edit_btn.clicked.connect(self.edit_requested.emit)
            layout.addWidget(edit_btn)

            del_btn = QPushButton("✕")
            del_btn.setFixedSize(36, 36)
            del_btn.setStyleSheet(
                "QPushButton { background: #4a1a2e; color: #ff6b81; "
                "border-radius: 18px; font-size: 14px; border: none; }"
                "QPushButton:hover { background: #e94560; color: white; }"
            )
            del_btn.clicked.connect(self.delete_requested.emit)
            layout.addWidget(del_btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class ThemeCard(QFrame):
    """Карточка темы оформления."""

    clicked = pyqtSignal()

    def __init__(self, name: str, description: str, color_preview: str,
                 is_active: bool = False, parent=None):
        super().__init__(parent)
        self.theme_name = name
        self.setObjectName("activeThemeCard" if is_active else "themeCard")
        self.setCursor(Qt.PointingHandCursor)
        self._setup_ui(name, description, color_preview, is_active)

    def _setup_ui(self, name: str, description: str, color_preview: str,
                  is_active: bool):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        preview = QFrame()
        preview.setFixedSize(48, 48)
        preview.setStyleSheet(
            f"background-color: {color_preview}; border-radius: 10px;"
        )
        layout.addWidget(preview)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        name_label = QLabel(name)
        name_label.setStyleSheet(
            "color: #e0e0f0; font-size: 15px; font-weight: 600; padding: 0;"
        )
        info_layout.addWidget(name_label)

        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #808090; font-size: 12px; padding: 0;")
        info_layout.addWidget(desc_label)

        layout.addLayout(info_layout, stretch=1)

        if is_active:
            active_label = QLabel("✓ Активна")
            active_label.setStyleSheet(
                "color: #e94560; font-size: 13px; font-weight: 600;"
            )
            layout.addWidget(active_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class VolumeSlider(QWidget):
    """Слайдер громкости с отображением значения."""

    value_changed = pyqtSignal(int)

    def __init__(self, label: str = "Громкость", min_val: int = 0,
                 max_val: int = 100, initial: int = 70, suffix: str = "%",
                 parent=None):
        super().__init__(parent)
        self._suffix = suffix
        self._setup_ui(label, min_val, max_val, initial)

    def _setup_ui(self, label: str, min_val: int, max_val: int, initial: int):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)

        self._label = QLabel(label)
        self._label.setStyleSheet("color: #a0a0b0; font-size: 13px; min-width: 90px;")
        layout.addWidget(self._label)

        self._slider = QSlider(Qt.Horizontal)
        self._slider.setMinimum(min_val)
        self._slider.setMaximum(max_val)
        self._slider.setValue(initial)
        self._slider.valueChanged.connect(self._on_change)
        layout.addWidget(self._slider, stretch=1)

        self._value_label = QLabel(f"{initial}{self._suffix}")
        self._value_label.setStyleSheet(
            "color: #e94560; font-size: 14px; font-weight: 600; min-width: 50px;"
        )
        self._value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self._value_label)

    def _on_change(self, value: int):
        self._value_label.setText(f"{value}{self._suffix}")
        self.value_changed.emit(value)

    def value(self) -> int:
        return self._slider.value()

    def set_value(self, val: int):
        self._slider.setValue(val)
