"""Аудиоплеер для интернет-радио.

Поддерживает mpv, ffplay, gst-play-1.0.
Корректно обрабатывает потоки AAC+ (.aacp).
"""

import shutil
import subprocess
import threading
import time

from PyQt5.QtCore import QObject, pyqtSignal


class RadioPlayer(QObject):
    """Плеер потокового радио с автопереподключением."""

    status_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._process: subprocess.Popen | None = None
        self._current_url: str = ""
        self._current_name: str = ""
        self._volume: int = 70
        self._is_playing: bool = False
        self._is_paused: bool = False
        self._reconnect_thread: threading.Thread | None = None
        self._should_reconnect: bool = False
        self._player_cmd = self._detect_player()

    @staticmethod
    def _detect_player() -> str:
        for player in ("mpv", "ffplay", "gst-play-1.0"):
            if shutil.which(player):
                return player
        return "mpv"

    def play(self, url: str, name: str = ""):
        self.stop()
        self._current_url = url
        self._current_name = name
        self._should_reconnect = True
        self._start_playback()

    @staticmethod
    def _is_aacp_stream(url: str) -> bool:
        lower = url.lower()
        return lower.endswith(".aacp") or lower.endswith(".aac") or "aacp" in lower

    def _build_command(self) -> list[str]:
        url = self._current_url
        is_aacp = self._is_aacp_stream(url)

        if self._player_cmd == "mpv":
            cmd = [
                "mpv",
                "--no-video",
                "--no-terminal",
                f"--volume={self._volume}",
                "--network-timeout=10",
                "--demuxer-readahead-secs=5",
                "--demuxer=lavf",
                "--user-agent=SD-ON-Tool/1.0",
            ]
            if is_aacp:
                cmd.extend([
                    "--demuxer-lavf-format=aac",
                    "--demuxer-lavf-o=live_start_index=-1",
                ])
            cmd.append(url)
            return cmd

        if self._player_cmd == "ffplay":
            cmd = [
                "ffplay",
                "-nodisp",
                "-autoexit",
                "-volume", str(self._volume),
                "-user_agent", "SD-ON-Tool/1.0",
            ]
            if is_aacp:
                cmd.extend(["-f", "aac"])
            cmd.append(url)
            return cmd

        # gst-play-1.0
        return ["gst-play-1.0", "--volume", str(self._volume / 100.0), url]

    def _start_playback(self):
        try:
            cmd = self._build_command()

            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.PIPE,
            )
            self._is_playing = True
            self._is_paused = False
            self.status_changed.emit(f"▶ {self._current_name}")
            self._start_watchdog()

        except FileNotFoundError:
            self._is_playing = False
            self.error_occurred.emit(
                f"Плеер '{self._player_cmd}' не найден. "
                "Установите mpv: sudo pacman -S mpv"
            )
        except OSError as e:
            self._is_playing = False
            self.error_occurred.emit(f"Ошибка запуска: {e}")

    def _start_watchdog(self):
        def _watchdog():
            if self._process is None:
                return
            self._process.wait()
            if self._should_reconnect and self._is_playing:
                self.status_changed.emit(f"🔄 Переподключение: {self._current_name}")
                time.sleep(3)
                if self._should_reconnect:
                    self._start_playback()

        self._reconnect_thread = threading.Thread(target=_watchdog, daemon=True)
        self._reconnect_thread.start()

    def pause(self):
        if self._process and self._is_playing and not self._is_paused:
            if self._player_cmd == "mpv" and self._process.stdin:
                try:
                    self._process.stdin.write(b" ")
                    self._process.stdin.flush()
                except OSError:
                    pass
            self._is_paused = True
            self.status_changed.emit(f"⏸ {self._current_name}")

    def resume(self):
        if self._process and self._is_paused:
            if self._player_cmd == "mpv" and self._process.stdin:
                try:
                    self._process.stdin.write(b" ")
                    self._process.stdin.flush()
                except OSError:
                    pass
            self._is_paused = False
            self.status_changed.emit(f"▶ {self._current_name}")

    def stop(self):
        self._should_reconnect = False
        self._is_playing = False
        self._is_paused = False
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=3)
            except (subprocess.TimeoutExpired, OSError):
                try:
                    self._process.kill()
                except OSError:
                    pass
            self._process = None
        self.status_changed.emit("⏹ Остановлено")

    def set_volume(self, volume: int):
        self._volume = max(0, min(100, volume))
        if self._is_playing and self._current_url:
            self.stop()
            self._should_reconnect = True
            self._start_playback()

    @property
    def is_playing(self) -> bool:
        return self._is_playing

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    @property
    def current_name(self) -> str:
        return self._current_name

    @property
    def volume(self) -> int:
        return self._volume

    def cleanup(self):
        self.stop()
