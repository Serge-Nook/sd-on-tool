from abc import ABC, abstractmethod

from PyQt5.QtWidgets import QWidget

from src.core.config import Config


class ModuleBase(ABC):
    """Базовый класс для всех модулей SD-ON Tool."""

    def __init__(self, config: Config):
        self._config = config

    @abstractmethod
    def get_widget(self) -> QWidget:
        """Возвращает виджет модуля для отображения в главном окне."""

    @abstractmethod
    def get_name(self) -> str:
        """Возвращает название модуля для меню."""

    @abstractmethod
    def get_icon_name(self) -> str:
        """Возвращает название иконки модуля."""

    def on_activate(self):
        """Вызывается при переключении на этот модуль."""

    def on_deactivate(self):
        """Вызывается при уходе с этого модуля."""

    def cleanup(self):
        """Освобождение ресурсов при завершении."""
