package ru.sdon.tool.api;

import com.google.gson.Gson;
import com.sun.net.httpserver.HttpExchange;
import ru.sdon.tool.model.AppConfig;
import ru.sdon.tool.model.Station;

import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

public class StationsApi {
    private static final Gson GSON = new Gson();

    private static final List<Station> DEFAULT_STATIONS = List.of(
        new Station("Hard Rock Heaven", "http://hydra.cdnstream.com:80/1521_128", false),
        new Station("НАШЕ Радио", "https://nashe1.hostingradio.ru/nashe-128.mp3", false),
        new Station("Европа Плюс", "http://ep256.hostingradio.ru:8052/europaplus256.mp3", false),
        new Station("Relax FM", "http://23.105.238.4/gpm-relaxfm495.aacp", false),
        new Station("Love Radio", "http://microit.n340.com:9000/VgMv0WV17ZVx1uuo_12_love_128_reg_44", false),
        new Station("ENERGY FM", "http://23.105.238.4/gpm-energyfm495.aacp", false),
        new Station("Радио Maximum", "http://23.105.238.4/maximum96.aacp", false),
        new Station("ULTRA", "https://nashe1.hostingradio.ru/ultra-128.mp3", false)
    );

    private final AppConfig config;

    public StationsApi(AppConfig config) {
        this.config = config;
    }

    public void handleGetAll(HttpExchange exchange) throws IOException {
        List<Station> all = new ArrayList<>(DEFAULT_STATIONS);
        for (Station s : config.getCustomStations()) {
            s.setCustom(true);
            all.add(s);
        }
        sendJson(exchange, 200, GSON.toJson(all));
    }

    public void handleAdd(HttpExchange exchange) throws IOException {
        Station station = GSON.fromJson(
            new InputStreamReader(exchange.getRequestBody(), StandardCharsets.UTF_8),
            Station.class
        );
        if (station == null || station.getName() == null || station.getUrl() == null) {
            sendJson(exchange, 400, "{\"error\":\"Укажите name и url\"}");
            return;
        }
        station.setCustom(true);
        config.getCustomStations().add(station);
        config.save();
        sendJson(exchange, 200, GSON.toJson(station));
    }

    public void handleUpdate(HttpExchange exchange, int index) throws IOException {
        List<Station> custom = config.getCustomStations();
        if (index < 0 || index >= custom.size()) {
            sendJson(exchange, 404, "{\"error\":\"Станция не найдена\"}");
            return;
        }
        Station update = GSON.fromJson(
            new InputStreamReader(exchange.getRequestBody(), StandardCharsets.UTF_8),
            Station.class
        );
        if (update != null) {
            if (update.getName() != null) custom.get(index).setName(update.getName());
            if (update.getUrl() != null) custom.get(index).setUrl(update.getUrl());
            config.save();
        }
        sendJson(exchange, 200, GSON.toJson(custom.get(index)));
    }

    public void handleDelete(HttpExchange exchange, int index) throws IOException {
        List<Station> custom = config.getCustomStations();
        if (index < 0 || index >= custom.size()) {
            sendJson(exchange, 404, "{\"error\":\"Станция не найдена\"}");
            return;
        }
        custom.remove(index);
        config.save();
        sendJson(exchange, 200, "{\"ok\":true}");
    }

    private static void sendJson(HttpExchange exchange, int code, String json) throws IOException {
        byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        exchange.sendResponseHeaders(code, bytes.length);
        exchange.getResponseBody().write(bytes);
        exchange.close();
    }
}
