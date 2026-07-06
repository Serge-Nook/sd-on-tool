import json
import os
from pathlib import Path


class Config:
    """Менеджер конфигурации SD-ON Tool. Хранит все настройки локально."""

    DEFAULT_CONFIG = {
        "version": "1.0.0",
        "theme": "SD-ON Theme",
        "saturation": 100,
        "radio": {
            "volume": 70,
            "last_station": "",
            "custom_stations": []
        }
    }

    def __init__(self):
        self._config_dir = Path.home() / ".config" / "sd-on-tool"
        self._config_file = self._config_dir / "settings.json"
        self._data: dict = {}
        self._load()

    def _load(self):
        if self._config_file.exists():
            try:
                with open(self._config_file, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._data = dict(self.DEFAULT_CONFIG)
        else:
            self._data = dict(self.DEFAULT_CONFIG)

    def save(self):
        self._config_dir.mkdir(parents=True, exist_ok=True)
        with open(self._config_file, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default=None):
        keys = key.split(".")
        val = self._data
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return default
            if val is None:
                return default
        return val

    def set(self, key: str, value):
        keys = key.split(".")
        d = self._data
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value
        self.save()

    @property
    def config_dir(self) -> Path:
        return self._config_dir

    @property
    def data(self) -> dict:
        return self._data
