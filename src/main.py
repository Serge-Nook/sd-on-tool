#!/usr/bin/env python3
"""SD-ON Tool — автономное приложение для Steam Deck.

Точка входа приложения.
"""

import logging
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from src.core.config import Config
from src.modules.about import AboutModule
from src.modules.display import DisplayModule
from src.modules.radio import RadioModule
from src.modules.themes import ThemesModule
from src.ui.main_window import MainWindow


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    setup_logging()
    log = logging.getLogger("sd-on-tool")
    log.info("Запуск SD-ON Tool...")

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("SD-ON Tool")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SD-ON")

    config = Config()

    modules = [
        RadioModule(config),
        ThemesModule(config),
        DisplayModule(config),
        AboutModule(config),
    ]

    window = MainWindow(config, modules)
    window.showMaximized()

    log.info("SD-ON Tool запущен")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
