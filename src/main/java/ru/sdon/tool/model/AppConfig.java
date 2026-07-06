package ru.sdon.tool.model;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public class AppConfig {
    private static final Path CONFIG_DIR = Path.of(System.getProperty("user.home"), ".config", "sd-on-tool");
    private static final Path CONFIG_FILE = CONFIG_DIR.resolve("settings.json");
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();

    private int volume = 70;
    private String lastStation = "";
    private List<Station> customStations = new ArrayList<>();

    public static AppConfig load() {
        if (Files.exists(CONFIG_FILE)) {
            try {
                String json = Files.readString(CONFIG_FILE, StandardCharsets.UTF_8);
                AppConfig cfg = GSON.fromJson(json, AppConfig.class);
                return cfg != null ? cfg : new AppConfig();
            } catch (Exception e) {
                System.err.println("Ошибка загрузки конфигурации: " + e.getMessage());
            }
        }
        return new AppConfig();
    }

    public void save() {
        try {
            Files.createDirectories(CONFIG_DIR);
            Files.writeString(CONFIG_FILE, GSON.toJson(this), StandardCharsets.UTF_8);
        } catch (IOException e) {
            System.err.println("Ошибка сохранения конфигурации: " + e.getMessage());
        }
    }

    public int getVolume() { return volume; }
    public void setVolume(int volume) { this.volume = Math.max(0, Math.min(100, volume)); }

    public String getLastStation() { return lastStation; }
    public void setLastStation(String lastStation) { this.lastStation = lastStation; }

    public List<Station> getCustomStations() { return customStations; }
    public void setCustomStations(List<Station> customStations) { this.customStations = customStations; }
}
