"""Управление станциями радио."""

DEFAULT_STATIONS = [
    {
        "name": "Hard Rock Heaven",
        "url": "http://hydra.cdnstream.com:80/1521_128",
    },
    {
        "name": "НАШЕ Радио",
        "url": "https://nashe1.hostingradio.ru/nashe-128.mp3",
    },
    {
        "name": "Европа Плюс",
        "url": "http://ep256.hostingradio.ru:8052/europaplus256.mp3",
    },
    {
        "name": "Relax FM",
        "url": "http://23.105.238.4/gpm-relaxfm495.aacp",
    },
    {
        "name": "Love Radio",
        "url": "http://microit.n340.com:9000/VgMv0WV17ZVx1uuo_12_love_128_reg_44",
    },
    {
        "name": "ENERGY FM",
        "url": "http://23.105.238.4/gpm-energyfm495.aacp",
    },
    {
        "name": "Радио Maximum",
        "url": "http://23.105.238.4/maximum96.aacp",
    },
    {
        "name": "ULTRA",
        "url": "https://nashe1.hostingradio.ru/ultra-128.mp3",
    },
]


class StationManager:
    """Менеджер радиостанций: встроенные + пользовательские."""

    def __init__(self, config):
        self._config = config

    def get_default_stations(self) -> list[dict]:
        return list(DEFAULT_STATIONS)

    def get_custom_stations(self) -> list[dict]:
        return list(self._config.get("radio.custom_stations", []))

    def get_all_stations(self) -> list[dict]:
        return self.get_default_stations() + self.get_custom_stations()

    def add_custom_station(self, name: str, url: str):
        stations = self.get_custom_stations()
        stations.append({"name": name, "url": url})
        self._config.set("radio.custom_stations", stations)

    def remove_custom_station(self, index: int):
        stations = self.get_custom_stations()
        if 0 <= index < len(stations):
            stations.pop(index)
            self._config.set("radio.custom_stations", stations)

    def update_custom_station(self, index: int, name: str, url: str):
        stations = self.get_custom_stations()
        if 0 <= index < len(stations):
            stations[index] = {"name": name, "url": url}
            self._config.set("radio.custom_stations", stations)
