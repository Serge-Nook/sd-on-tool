package ru.sdon.tool.model;

public class Station {
    private String name;
    private String url;
    private boolean custom;

    public Station() {}

    public Station(String name, String url, boolean custom) {
        this.name = name;
        this.url = url;
        this.custom = custom;
    }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getUrl() { return url; }
    public void setUrl(String url) { this.url = url; }

    public boolean isCustom() { return custom; }
    public void setCustom(boolean custom) { this.custom = custom; }
}
