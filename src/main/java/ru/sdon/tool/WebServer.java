package ru.sdon.tool;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import ru.sdon.tool.api.ConfigApi;
import ru.sdon.tool.api.StationsApi;
import ru.sdon.tool.model.AppConfig;

import java.io.IOException;
import java.io.InputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.Map;

public class WebServer {
    private static final Map<String, String> MIME_TYPES = Map.of(
        "html", "text/html; charset=utf-8",
        "css", "text/css; charset=utf-8",
        "js", "application/javascript; charset=utf-8",
        "json", "application/json; charset=utf-8",
        "svg", "image/svg+xml",
        "png", "image/png",
        "ico", "image/x-icon"
    );

    private final HttpServer server;
    private final StationsApi stationsApi;
    private final ConfigApi configApi;

    public WebServer(int port, AppConfig config) throws IOException {
        this.stationsApi = new StationsApi(config);
        this.configApi = new ConfigApi(config);
        this.server = HttpServer.create(new InetSocketAddress("127.0.0.1", port), 0);
        setupRoutes();
    }

    private void setupRoutes() {
        server.createContext("/api/stations", this::handleStations);
        server.createContext("/api/config", this::handleConfig);
        server.createContext("/", this::handleStatic);
    }

    private void handleStations(HttpExchange exchange) throws IOException {
        String method = exchange.getRequestMethod();
        String path = exchange.getRequestURI().getPath();
        addCorsHeaders(exchange);

        try {
            if ("GET".equals(method) && "/api/stations".equals(path)) {
                stationsApi.handleGetAll(exchange);
            } else if ("POST".equals(method) && "/api/stations".equals(path)) {
                stationsApi.handleAdd(exchange);
            } else if (path.startsWith("/api/stations/")) {
                int index = parseIndex(path, "/api/stations/");
                if ("PUT".equals(method)) {
                    stationsApi.handleUpdate(exchange, index);
                } else if ("DELETE".equals(method)) {
                    stationsApi.handleDelete(exchange, index);
                } else {
                    sendNotFound(exchange);
                }
            } else {
                sendNotFound(exchange);
            }
        } catch (Exception e) {
            sendError(exchange, e.getMessage());
        }
    }

    private void handleConfig(HttpExchange exchange) throws IOException {
        String method = exchange.getRequestMethod();
        addCorsHeaders(exchange);

        try {
            if ("GET".equals(method)) {
                configApi.handleGet(exchange);
            } else if ("PUT".equals(method) || "POST".equals(method)) {
                configApi.handleUpdate(exchange);
            } else {
                sendNotFound(exchange);
            }
        } catch (Exception e) {
            sendError(exchange, e.getMessage());
        }
    }

    private void handleStatic(HttpExchange exchange) throws IOException {
        String path = exchange.getRequestURI().getPath();
        if ("/".equals(path)) path = "/index.html";

        String resourcePath = "web" + path;
        InputStream is = getClass().getClassLoader().getResourceAsStream(resourcePath);

        if (is == null) {
            sendNotFound(exchange);
            return;
        }

        byte[] data = is.readAllBytes();
        is.close();

        String ext = path.contains(".") ? path.substring(path.lastIndexOf('.') + 1) : "html";
        String contentType = MIME_TYPES.getOrDefault(ext, "application/octet-stream");

        exchange.getResponseHeaders().set("Content-Type", contentType);
        exchange.sendResponseHeaders(200, data.length);
        exchange.getResponseBody().write(data);
        exchange.close();
    }

    private static void addCorsHeaders(HttpExchange exchange) {
        exchange.getResponseHeaders().set("Access-Control-Allow-Origin", "*");
        exchange.getResponseHeaders().set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE");
        exchange.getResponseHeaders().set("Access-Control-Allow-Headers", "Content-Type");
    }

    private static int parseIndex(String path, String prefix) {
        String part = path.substring(prefix.length());
        return Integer.parseInt(part);
    }

    private static void sendNotFound(HttpExchange exchange) throws IOException {
        byte[] msg = "404 Not Found".getBytes(StandardCharsets.UTF_8);
        exchange.sendResponseHeaders(404, msg.length);
        exchange.getResponseBody().write(msg);
        exchange.close();
    }

    private static void sendError(HttpExchange exchange, String message) throws IOException {
        byte[] msg = ("500: " + message).getBytes(StandardCharsets.UTF_8);
        exchange.sendResponseHeaders(500, msg.length);
        exchange.getResponseBody().write(msg);
        exchange.close();
    }

    public void start() {
        server.start();
    }

    public void stop() {
        server.stop(0);
    }

    public int getPort() {
        return server.getAddress().getPort();
    }
}
