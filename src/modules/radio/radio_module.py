"""Модуль интернет-радио."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.core.config import Config
from src.core.module_base import ModuleBase
from src.modules.radio.player import RadioPlayer
from src.modules.radio.stations import StationManager
from src.ui.widgets import StationCard, VolumeSlider


class AddStationDialog(QDialog):
    """Диалог добавления/редактирования станции."""

    def __init__(self, parent=None, name: str = "", url: str = "",
                 title: str = "Добавить станцию"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(450)
        self.setStyleSheet("""
            QDialog { background-color: #1a1a2e; }
            QLabel { color: #c0c0d0; font-size: 14px; }
        """)
        self._setup_ui(name, url)

    def _setup_ui(self, name: str, url: str):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        layout.addWidget(QLabel("Название станции:"))
        self.name_input = QLineEdit(name)
        self.name_input.setPlaceholderText("Например: Моё радио")
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("URL потока:"))
        self.url_input = QLineEdit(url)
        self.url_input.setPlaceholderText("http:// или https://")
        layout.addWidget(self.url_input)

        hint = QLabel("Поддерживаемые форматы: MP3, AAC, AAC+, HTTP/HTTPS")
        hint.setStyleSheet("color: #606080; font-size: 11px;")
        layout.addWidget(hint)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Сохранить")
        save_btn.setObjectName("actionButton")
        save_btn.clicked.connect(self._validate_and_accept)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _validate_and_accept(self):
        name = self.name_input.text().strip()
        url = self.url_input.text().strip()
        if not name:
            self.name_input.setStyleSheet("border-color: #e94560;")
            return
        if not url or not (url.startswith("http://") or url.startswith("https://")):
            self.url_input.setStyleSheet("border-color: #e94560;")
            return
        self.accept()

    def get_data(self) -> tuple[str, str]:
        return self.name_input.text().strip(), self.url_input.text().strip()


class RadioModule(ModuleBase):
    """Модуль интернет-радио с поддержкой MP3, AAC, AAC+, HTTP/HTTPS."""

    def __init__(self, config: Config):
        super().__init__(config)
        self._station_mgr = StationManager(config)
        self._player = RadioPlayer()
        self._widget: QWidget | None = None
        self._station_list_widget: QWidget | None = None
        self._status_label: QLabel | None = None
        self._active_station_url: str = ""

    def get_name(self) -> str:
        return "Радио"

    def get_icon_name(self) -> str:
        return "radio"

    def get_widget(self) -> QWidget:
        if self._widget is not None:
            return self._widget

        self._widget = QWidget()
        layout = QVBoxLayout(self._widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        title = QLabel("📻 Радио")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        subtitle = QLabel("Интернет-радиостанции • MP3, AAC, AAC+")
        subtitle.setObjectName("subtitleLabel")
        layout.addWidget(subtitle)

        # Статус и управление
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)

        self._status_label = QLabel("⏹ Остановлено")
        self._status_label.setStyleSheet(
            "color: #e94560; font-size: 15px; font-weight: 600; "
            "background: #16213e; border-radius: 10px; padding: 10px 16px;"
        )
        controls_layout.addWidget(self._status_label, stretch=1)

        play_btn = QPushButton("▶")
        play_btn.setObjectName("actionButton")
        play_btn.setFixedSize(48, 48)
        play_btn.setStyleSheet(
            "QPushButton { background: #e94560; color: white; border-radius: 24px; "
            "font-size: 18px; } QPushButton:hover { background: #ff6b81; }"
        )
        play_btn.clicked.connect(self._on_play_pause)
        controls_layout.addWidget(play_btn)

        stop_btn = QPushButton("⏹")
        stop_btn.setObjectName("secondaryButton")
        stop_btn.setFixedSize(48, 48)
        stop_btn.setStyleSheet(
            "QPushButton { background: #0f3460; color: #a0a0b0; border-radius: 24px; "
            "font-size: 18px; } QPushButton:hover { background: #1a4a7a; color: white; }"
        )
        stop_btn.clicked.connect(self._on_stop)
        controls_layout.addWidget(stop_btn)

        layout.addLayout(controls_layout)

        # Громкость
        saved_volume = self._config.get("radio.volume", 70)
        volume_slider = VolumeSlider(
            "Громкость", 0, 100, saved_volume, "%"
        )
        volume_slider.value_changed.connect(self._on_volume_change)
        self._player.set_volume(saved_volume)
        layout.addWidget(volume_slider)

        # Кнопка добавления
        add_layout = QHBoxLayout()
        add_layout.addStretch()
        add_btn = QPushButton("+ Добавить станцию")
        add_btn.setObjectName("secondaryButton")
        add_btn.clicked.connect(self._on_add_station)
        add_layout.addWidget(add_btn)
        layout.addLayout(add_layout)

        # Список станций
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._station_list_widget = QWidget()
        self._station_list_layout = QVBoxLayout(self._station_list_widget)
        self._station_list_layout.setSpacing(8)
        self._station_list_layout.setContentsMargins(0, 0, 8, 0)
        self._station_list_layout.addStretch()

        scroll.setWidget(self._station_list_widget)
        layout.addWidget(scroll, stretch=1)

        self._player.status_changed.connect(self._on_status_changed)
        self._player.error_occurred.connect(self._on_error)

        self._rebuild_station_list()

        # Восстановление последней станции
        last = self._config.get("radio.last_station", "")
        if last:
            self._active_station_url = last

        return self._widget

    def _rebuild_station_list(self):
        layout = self._station_list_layout
        while layout.count() > 1:
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        default_stations = self._station_mgr.get_default_stations()
        custom_stations = self._station_mgr.get_custom_stations()

        if default_stations:
            header = QLabel("Встроенные станции")
            header.setObjectName("sectionLabel")
            layout.insertWidget(layout.count() - 1, header)

            for station in default_stations:
                is_active = station["url"] == self._active_station_url
                card = StationCard(
                    station["name"], station["url"], is_active, is_custom=False
                )
                card.clicked.connect(
                    lambda u=station["url"], n=station["name"]: self._on_station_click(u, n)
                )
                layout.insertWidget(layout.count() - 1, card)

        if custom_stations:
            header = QLabel("Мои станции")
            header.setObjectName("sectionLabel")
            header.setStyleSheet("padding-top: 12px;")
            layout.insertWidget(layout.count() - 1, header)

            for i, station in enumerate(custom_stations):
                is_active = station["url"] == self._active_station_url
                card = StationCard(
                    station["name"], station["url"], is_active, is_custom=True
                )
                card.clicked.connect(
                    lambda u=station["url"], n=station["name"]: self._on_station_click(u, n)
                )
                card.edit_requested.connect(
                    lambda idx=i: self._on_edit_station(idx)
                )
                card.delete_requested.connect(
                    lambda idx=i: self._on_delete_station(idx)
                )
                layout.insertWidget(layout.count() - 1, card)

    def _on_station_click(self, url: str, name: str):
        self._active_station_url = url
        self._config.set("radio.last_station", url)
        self._player.play(url, name)
        self._rebuild_station_list()

    def _on_play_pause(self):
        if self._player.is_paused:
            self._player.resume()
        elif self._player.is_playing:
            self._player.pause()
        elif self._active_station_url:
            stations = self._station_mgr.get_all_stations()
            name = ""
            for s in stations:
                if s["url"] == self._active_station_url:
                    name = s["name"]
                    break
            self._player.play(self._active_station_url, name)

    def _on_stop(self):
        self._player.stop()

    def _on_volume_change(self, value: int):
        self._player.set_volume(value)
        self._config.set("radio.volume", value)

    def _on_status_changed(self, status: str):
        if self._status_label:
            self._status_label.setText(status)

    def _on_error(self, error: str):
        if self._widget:
            QMessageBox.warning(self._widget, "Ошибка", error)

    def _on_add_station(self):
        dialog = AddStationDialog(self._widget)
        if dialog.exec_() == QDialog.Accepted:
            name, url = dialog.get_data()
            self._station_mgr.add_custom_station(name, url)
            self._rebuild_station_list()

    def _on_edit_station(self, index: int):
        stations = self._station_mgr.get_custom_stations()
        if 0 <= index < len(stations):
            station = stations[index]
            dialog = AddStationDialog(
                self._widget,
                name=station["name"],
                url=station["url"],
                title="Редактировать станцию"
            )
            if dialog.exec_() == QDialog.Accepted:
                name, url = dialog.get_data()
                self._station_mgr.update_custom_station(index, name, url)
                self._rebuild_station_list()

    def _on_delete_station(self, index: int):
        stations = self._station_mgr.get_custom_stations()
        if 0 <= index < len(stations):
            reply = QMessageBox.question(
                self._widget,
                "Удалить станцию",
                f"Удалить «{stations[index]['name']}»?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self._station_mgr.remove_custom_station(index)
                self._rebuild_station_list()

    def on_activate(self):
        self._rebuild_station_list()

    def cleanup(self):
        self._player.cleanup()
