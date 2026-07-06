"""Главное окно SD-ON Tool."""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QKeyEvent
from PyQt5.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.core.config import Config
from src.core.module_base import ModuleBase
from src.ui.styles import MAIN_STYLE


class MainWindow(QMainWindow):
    """Главное окно приложения SD-ON Tool."""

    NAV_ICONS = {
        "Радио": "📻",
        "Темы": "🎨",
        "Цвета экрана": "🖥",
        "О программе": "ℹ",
    }

    def __init__(self, config: Config, modules: list[ModuleBase]):
        super().__init__()
        self._config = config
        self._modules = modules
        self._current_index = 0
        self._nav_buttons: list[QPushButton] = []
        self.setWindowTitle("SD-ON Tool")
        self.setMinimumSize(1024, 600)
        self.setStyleSheet(MAIN_STYLE)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)

        self._stack = QStackedWidget()
        for module in self._modules:
            self._stack.addWidget(module.get_widget())
        main_layout.addWidget(self._stack, stretch=1)

        if self._nav_buttons:
            self._nav_buttons[0].setChecked(True)
            self._modules[0].on_activate()

    def _create_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(6)

        logo_label = QLabel("SD-ON")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFont(QFont("", 24, QFont.Bold))
        logo_label.setStyleSheet("color: #e94560; padding: 10px 0 4px 0;")
        layout.addWidget(logo_label)

        tool_label = QLabel("Tool")
        tool_label.setAlignment(Qt.AlignCenter)
        tool_label.setStyleSheet(
            "color: #606080; font-size: 13px; padding-bottom: 16px;"
        )
        layout.addWidget(tool_label)

        sep = QWidget()
        sep.setFixedHeight(2)
        sep.setStyleSheet("background-color: #0f3460;")
        layout.addWidget(sep)
        layout.addSpacing(8)

        btn_group = QButtonGroup(self)
        btn_group.setExclusive(True)

        for i, module in enumerate(self._modules):
            name = module.get_name()
            icon = self.NAV_ICONS.get(name, "•")
            btn = QPushButton(f"  {icon}  {name}")
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.setFocusPolicy(Qt.StrongFocus)
            btn.clicked.connect(lambda checked, idx=i: self._switch_module(idx))
            btn_group.addButton(btn, i)
            layout.addWidget(btn)
            self._nav_buttons.append(btn)

        layout.addStretch()

        version_label = QLabel("v1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #404060; font-size: 11px;")
        layout.addWidget(version_label)

        return sidebar

    def _switch_module(self, index: int):
        if index == self._current_index:
            return
        self._modules[self._current_index].on_deactivate()
        self._current_index = index
        self._stack.setCurrentIndex(index)
        self._modules[index].on_activate()

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key in (Qt.Key_Up, Qt.Key_Down):
            direction = -1 if key == Qt.Key_Up else 1
            new_index = (self._current_index + direction) % len(self._modules)
            self._nav_buttons[new_index].setChecked(True)
            self._switch_module(new_index)
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        for module in self._modules:
            module.cleanup()
        self._config.save()
        super().closeEvent(event)
