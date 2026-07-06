"""Модуль «О программе»."""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDesktopServices, QFont
from PyQt5.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.core.config import Config
from src.core.module_base import ModuleBase


VERSION = "1.0.0"


class AboutModule(ModuleBase):
    """Раздел информации о программе."""

    def __init__(self, config: Config):
        super().__init__(config)
        self._widget: QWidget | None = None

    def get_name(self) -> str:
        return "О программе"

    def get_icon_name(self) -> str:
        return "about"

    def get_widget(self) -> QWidget:
        if self._widget is not None:
            return self._widget

        self._widget = QWidget()
        layout = QVBoxLayout(self._widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        layout.addStretch()

        # Логотип
        logo = QLabel("SD-ON")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFont(QFont("", 48, QFont.Bold))
        logo.setStyleSheet("color: #e94560;")
        layout.addWidget(logo)

        tool_label = QLabel("Tool")
        tool_label.setAlignment(Qt.AlignCenter)
        tool_label.setFont(QFont("", 20))
        tool_label.setStyleSheet("color: #606080;")
        layout.addWidget(tool_label)

        layout.addSpacing(16)

        # Информационная карточка
        card = QFrame()
        card.setObjectName("cardFrame")
        card.setMaximumWidth(500)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        card_layout.setAlignment(Qt.AlignCenter)

        info_items = [
            ("Версия программы", VERSION),
            ("Разработал", "Serge Nook"),
            ("Сайт", "SD-ON.RU"),
            ("Платформа", "Steam Deck / SteamOS"),
            ("Лицензия", "MIT"),
        ]

        for label_text, value_text in info_items:
            row = QLabel(f"<b>{label_text}:</b>  {value_text}")
            row.setAlignment(Qt.AlignCenter)
            row.setStyleSheet("color: #c0c0d0; font-size: 15px;")
            card_layout.addWidget(row)

        # Центрирование карточки
        card_wrapper = QWidget()
        card_wrapper_layout = QVBoxLayout(card_wrapper)
        card_wrapper_layout.setAlignment(Qt.AlignCenter)
        card_wrapper_layout.addWidget(card)
        layout.addWidget(card_wrapper)

        layout.addSpacing(16)

        # Описание
        desc = QLabel(
            "SD-ON Tool — автономное приложение для Steam Deck,\n"
            "предоставляющее дополнительные возможности настройки\n"
            "системы без использования сторонних плагинов."
        )
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #808090; font-size: 13px; line-height: 1.4;")
        layout.addWidget(desc)

        layout.addSpacing(8)

        # Кнопка сайта
        site_btn = QPushButton("Открыть SD-ON.RU")
        site_btn.setObjectName("secondaryButton")
        site_btn.setMaximumWidth(250)
        site_btn.clicked.connect(self._open_site)

        btn_wrapper = QWidget()
        btn_layout = QVBoxLayout(btn_wrapper)
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(site_btn)
        layout.addWidget(btn_wrapper)

        layout.addStretch()

        # Копирайт
        copyright_label = QLabel("© 2025 Serge Nook. Все права защищены.")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("color: #404060; font-size: 11px;")
        layout.addWidget(copyright_label)

        return self._widget

    @staticmethod
    def _open_site():
        from PyQt5.QtCore import QUrl
        QDesktopServices.openUrl(QUrl("https://sd-on.ru"))

    def cleanup(self):
        pass
