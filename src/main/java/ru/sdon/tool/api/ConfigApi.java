package ru.sdon.tool.api;

import com.google.gson.Gson;
import com.sun.net.httpserver.HttpExchange;
import ru.sdon.tool.model.AppConfig;

import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Map;

public class ConfigApi {
    private static final Gson GSON = new Gson();
    private final AppConfig config;

    public ConfigApi(AppConfig config) {
        this.config = config;
    }

    public void handleGet(HttpExchange exchange) throws IOException {
        String json = GSON.toJson(Map.of(
            "volume", config.getVolume(),
            "lastStation", config.getLastStation()
        ));
        sendJson(exchange, 200, json);
    }

    @SuppressWarnings("unchecked")
    public void handleUpdate(HttpExchange exchange) throws IOException {
        Map<String, Object> data = GSON.fromJson(
            new InputStreamReader(exchange.getRequestBody(), StandardCharsets.UTF_8),
            Map.class
        );
        if (data == null) {
            sendJson(exchange, 400, "{\"error\":\"Неверные данные\"}");
            return;
        }
        if (data.containsKey("volume")) {
            config.setVolume(((Number) data.get("volume")).intValue());
        }
        if (data.containsKey("lastStation")) {
            config.setLastStation((String) data.get("lastStation"));
        }
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
