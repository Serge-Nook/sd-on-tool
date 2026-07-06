package ru.sdon.tool;

import ru.sdon.tool.model.AppConfig;

import java.awt.Desktop;
import java.net.URI;

public class App {
    private static final int PORT = 37520;

    public static void main(String[] args) {
        System.out.println("╔══════════════════════════════════════════╗");
        System.out.println("║         SD-ON Tool v1.1.0                ║");
        System.out.println("║         sd-on.ru                         ║");
        System.out.println("╚══════════════════════════════════════════╝");

        AppConfig config = AppConfig.load();

        try {
            WebServer server = new WebServer(PORT, config);
            server.start();

            String url = "http://127.0.0.1:" + PORT;
            System.out.println("Сервер запущен: " + url);

            openBrowser(url);

            System.out.println("Нажмите Ctrl+C для выхода.");

            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                System.out.println("Остановка сервера...");
                config.save();
                server.stop();
            }));

            Thread.currentThread().join();
        } catch (Exception e) {
            System.err.println("Ошибка запуска: " + e.getMessage());
            System.exit(1);
        }
    }

    private static void openBrowser(String url) {
        try {
            if (Desktop.isDesktopSupported() && Desktop.getDesktop().isSupported(Desktop.Action.BROWSE)) {
                Desktop.getDesktop().browse(new URI(url));
                return;
            }
        } catch (Exception ignored) {}

        // Fallback: xdg-open (Linux / SteamOS)
        try {
            new ProcessBuilder("xdg-open", url).start();
        } catch (Exception e) {
            System.out.println("Откройте в браузере: " + url);
        }
    }
}
