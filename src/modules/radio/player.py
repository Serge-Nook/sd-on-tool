"""Аудиоплеер для интернет-радио.

Использует встроенный PyQt5 QMediaPlayer — не требует установки
сторонних программ (mpv, ffplay и т.д.).
Поддерживает MP3, AAC, AAC+, HTTP/HTTPS потоки.
"""

from PyQt5.QtCore import QObject, QTimer, QUrl, pyqtSignal
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer


class RadioPlayer(QObject):
    """Плеер потокового радио с автопереподключением."""

    status_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    RECONNECT_DELAY_MS = 3000

    def __init__(self):
        super().__init__()
        self._player = QMediaPlayer()
        self._player.error.connect(self._on_error)
        self._player.stateChanged.connect(self._on_state_changed)
        self._player.mediaStatusChanged.connect(self._on_media_status_changed)

        self._current_url: str = ""
        self._current_name: str = ""
        self._is_playing: bool = False
        self._should_reconnect: bool = False

        self._reconnect_timer = QTimer()
        self._reconnect_timer.setSingleShot(True)
        self._reconnect_timer.timeout.connect(self._do_reconnect)

    def play(self, url: str, name: str = ""):
        self.stop()
        self._current_url = url
        self._current_name = name
        self._should_reconnect = True
        self._start_playback()

    def _start_playback(self):
        content = QMediaContent(QUrl(self._current_url))
        self._player.setMedia(content)
        self._player.play()
        self._is_playing = True
        self.status_changed.emit(f"▶ {self._current_name}")

    def pause(self):
        if self._is_playing and self._player.state() == QMediaPlayer.PlayingState:
            self._player.pause()
            self.status_changed.emit(f"⏸ {self._current_name}")

    def resume(self):
        if self._player.state() == QMediaPlayer.PausedState:
            self._player.play()
            self.status_changed.emit(f"▶ {self._current_name}")

    def stop(self):
        self._should_reconnect = False
        self._is_playing = False
        self._reconnect_timer.stop()
        self._player.stop()
        self._player.setMedia(QMediaContent())
        self.status_changed.emit("⏹ Остановлено")

    def set_volume(self, volume: int):
        self._player.setVolume(max(0, min(100, volume)))

    def _on_error(self):
        err = self._player.errorString()
        if self._should_reconnect and self._is_playing:
            self.status_changed.emit(f"🔄 Переподключение: {self._current_name}")
            self._reconnect_timer.start(self.RECONNECT_DELAY_MS)
        elif err:
            self.error_occurred.emit(f"Ошибка воспроизведения: {err}")

    def _on_state_changed(self, state: int):
        if state == QMediaPlayer.StoppedState and self._should_reconnect and self._is_playing:
            self.status_changed.emit(f"🔄 Переподключение: {self._current_name}")
            self._reconnect_timer.start(self.RECONNECT_DELAY_MS)

    def _on_media_status_changed(self, status: int):
        if status == QMediaPlayer.EndOfMedia and self._should_reconnect and self._is_playing:
            self.status_changed.emit(f"🔄 Переподключение: {self._current_name}")
            self._reconnect_timer.start(self.RECONNECT_DELAY_MS)

    def _do_reconnect(self):
        if self._should_reconnect and self._current_url:
            self._start_playback()

    @property
    def is_playing(self) -> bool:
        return self._is_playing

    @property
    def is_paused(self) -> bool:
        return self._player.state() == QMediaPlayer.PausedState

    @property
    def current_name(self) -> str:
        return self._current_name

    @property
    def volume(self) -> int:
        return self._player.volume()

    def cleanup(self):
        self.stop()
