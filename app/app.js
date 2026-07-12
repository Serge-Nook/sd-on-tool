/*
 * SD-ON Tool — автономное приложение (без инъекции в интерфейс Steam).
 *
 * Весь интерфейс рендерится как обычная веб-страница в окне приложения.
 * Разделы: Радио, Темы, Цвета экрана, О программе.
 * Настройки хранятся в localStorage.
 */
(function () {
  "use strict";

  var VERSION = "__SD_ON_TOOL_VERSION__";
  var SETTINGS_KEY = "sd-on-tool.settings";

  /* Встроенные радиостанции (жёстко в коде). */
  var BUILTIN_STATIONS = [
    { name: "Hard Rock Heaven", url: "http://hydra.cdnstream.com:80/1521_128" },
    { name: "НАШЕ Радио", url: "https://nashe1.hostingradio.ru/nashe-128.mp3" },
    { name: "Европа Плюс", url: "http://ep256.hostingradio.ru:8052/europaplus256.mp3" },
    { name: "Relax FM", url: "http://23.105.238.4/gpm-relaxfm495.aacp" },
    { name: "Love Radio", url: "http://microit.n340.com:9000/VgMv0WV17ZVx1uuo_12_love_" },
    { name: "ENERGY FM", url: "http://23.105.238.4/gpm-energyfm495.aacp" },
    { name: "Радио Maximum", url: "http://23.105.238.4/maximum96.aacp" },
    { name: "ULTRA", url: "https://nashe1.hostingradio.ru/ultra-128.mp3" }
  ];

  var BUILTIN_THEMES = [
    "Classic", "Dark", "OLED Black", "Neon Blue", "Neon Green", "Purple",
    "Crimson", "Orange", "White", "Gray", "Cyber", "Carbon", "Minimal",
    "Aurora", "Steam Blue", "Retro", "Matrix", "Modern", "Glass", "SD-ON Theme"
  ];

  function themeFileName(name) {
    return name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "") + ".css";
  }

  var DEFAULT_SETTINGS = {
    theme: "По умолчанию",
    saturation: 100,
    radio_stations: [],
    last_radio_station: "",
    radio_volume: 0.8
  };

  var Store = {
    settings: null,
    load: function () {
      var raw = null;
      try { raw = window.localStorage.getItem(SETTINGS_KEY); } catch (e) { raw = null; }
      if (raw) {
        try { this.settings = mergeDefaults(JSON.parse(raw)); return; } catch (e) { /* fallthrough */ }
      }
      this.settings = clone(DEFAULT_SETTINGS);
    },
    save: function () {
      try { window.localStorage.setItem(SETTINGS_KEY, JSON.stringify(this.settings)); } catch (e) { /* ignore */ }
    },
    get: function (key) { return this.settings[key]; },
    set: function (key, value) { this.settings[key] = value; this.save(); }
  };

  function mergeDefaults(obj) {
    var out = clone(DEFAULT_SETTINGS);
    for (var k in obj) {
      if (Object.prototype.hasOwnProperty.call(obj, k)) { out[k] = obj[k]; }
    }
    if (!Array.isArray(out.radio_stations)) { out.radio_stations = []; }
    return out;
  }

  function clone(obj) { return JSON.parse(JSON.stringify(obj)); }

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      for (var k in attrs) {
        if (!Object.prototype.hasOwnProperty.call(attrs, k)) { continue; }
        if (k === "class") { node.className = attrs[k]; }
        else if (k === "text") { node.textContent = attrs[k]; }
        else if (k.indexOf("on") === 0 && typeof attrs[k] === "function") {
          node.addEventListener(k.slice(2).toLowerCase(), attrs[k]);
        } else { node.setAttribute(k, attrs[k]); }
      }
    }
    if (children) {
      for (var i = 0; i < children.length; i++) {
        var c = children[i];
        if (c == null) { continue; }
        node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
      }
    }
    return node;
  }

  function clampVolume(v) {
    v = parseFloat(v);
    if (isNaN(v)) { return 0.8; }
    return Math.max(0, Math.min(1, v));
  }

  /* -------------------- Радио -------------------- */
  var Radio = {
    audio: null, current: null, reconnectTimer: null, reconnectDelay: 3000, onStatus: null,
    init: function () {
      this.audio = new Audio();
      this.audio.preload = "none";
      this.audio.volume = clampVolume(Store.get("radio_volume"));
      var self = this;
      this.audio.addEventListener("error", function () { self.scheduleReconnect(); });
      this.audio.addEventListener("stalled", function () { self.scheduleReconnect(); });
      this.audio.addEventListener("playing", function () { self.reconnectDelay = 3000; self.emit("playing"); });
      this.audio.addEventListener("pause", function () { self.emit("paused"); });
    },
    stations: function () { return BUILTIN_STATIONS.concat(Store.get("radio_stations") || []); },
    findByName: function (name) {
      var all = this.stations();
      for (var i = 0; i < all.length; i++) { if (all[i].name === name) { return all[i]; } }
      return null;
    },
    play: function (station) {
      if (!station) { return; }
      this.current = station;
      this.clearReconnect();
      this.audio.src = station.url;
      var self = this;
      var p = this.audio.play();
      if (p && typeof p.catch === "function") { p.catch(function () { self.scheduleReconnect(); }); }
      Store.set("last_radio_station", station.name);
      this.emit("loading");
    },
    resume: function () {
      if (this.current) {
        if (this.audio.src) { this.audio.play(); } else { this.play(this.current); }
      }
    },
    pause: function () { this.clearReconnect(); this.audio.pause(); },
    stop: function () {
      this.clearReconnect();
      this.audio.pause();
      this.audio.removeAttribute("src");
      this.audio.load();
      this.emit("stopped");
    },
    setVolume: function (v) { v = clampVolume(v); this.audio.volume = v; Store.set("radio_volume", v); },
    scheduleReconnect: function () {
      if (!this.current || this.reconnectTimer) { return; }
      var self = this;
      this.emit("reconnecting");
      this.reconnectTimer = window.setTimeout(function () {
        self.reconnectTimer = null;
        self.reconnectDelay = Math.min(self.reconnectDelay * 2, 30000);
        self.play(self.current);
      }, this.reconnectDelay);
    },
    clearReconnect: function () {
      if (this.reconnectTimer) { window.clearTimeout(this.reconnectTimer); this.reconnectTimer = null; }
    },
    emit: function (state) { if (typeof this.onStatus === "function") { this.onStatus(state, this.current); } }
  };

  /* -------------------- Темы -------------------- */
  var Themes = {
    LINK_ID: "sd-on-tool-theme",
    names: function () { return ["По умолчанию"].concat(BUILTIN_THEMES); },
    apply: function (name) {
      this.remove();
      if (name && name !== "По умолчанию") {
        document.head.appendChild(el("link", {
          id: this.LINK_ID, rel: "stylesheet", type: "text/css",
          href: "themes/" + themeFileName(name)
        }));
      }
      Store.set("theme", name || "По умолчанию");
    },
    remove: function () {
      var existing = document.getElementById(this.LINK_ID);
      if (existing && existing.parentNode) { existing.parentNode.removeChild(existing); }
    },
    restore: function () { this.apply(Store.get("theme")); }
  };

  /* -------------------- Цвета экрана -------------------- */
  var Display = {
    STYLE_ID: "sd-on-tool-saturation",
    apply: function (percent) {
      percent = this.clamp(percent);
      var factor = percent / 100;
      var style = document.getElementById(this.STYLE_ID);
      if (!style) { style = el("style", { id: this.STYLE_ID }); document.head.appendChild(style); }
      style.textContent = "html{filter:saturate(" + factor + ");}";
      Store.set("saturation", percent);
    },
    reset: function () { this.apply(100); },
    restore: function () { this.apply(Store.get("saturation")); },
    clamp: function (p) {
      p = parseInt(p, 10);
      if (isNaN(p)) { return 100; }
      return Math.max(100, Math.min(200, p));
    }
  };

  /* -------------------- Интерфейс -------------------- */
  var UI = {
    body: null, active: "radio",
    tabs: [
      { id: "radio", label: "Радио" },
      { id: "themes", label: "Темы" },
      { id: "display", label: "Цвета экрана" },
      { id: "about", label: "О программе" }
    ],
    mount: function () {
      var self = this;
      var tabButtons = this.tabs.map(function (t) {
        return el("button", {
          class: "sd-tab" + (t.id === self.active ? " active" : ""),
          "data-tab": t.id, text: t.label,
          onClick: function () { self.select(t.id); }
        });
      });
      this.body = el("div", { class: "sd-body" });
      var app = el("div", { class: "sd-app" }, [
        el("div", { class: "sd-header" }, [
          el("img", { src: "assets/icons/sd-on-tool.svg", alt: "SD-ON Tool" }),
          el("h1", { text: "SD-ON Tool" })
        ]),
        el("div", { class: "sd-tabs" }, tabButtons),
        this.body
      ]);
      document.body.appendChild(app);
      this.render();
    },
    select: function (id) {
      this.active = id;
      var tabs = document.querySelectorAll(".sd-tab");
      for (var i = 0; i < tabs.length; i++) {
        tabs[i].classList.toggle("active", tabs[i].getAttribute("data-tab") === id);
      }
      this.render();
    },
    render: function () {
      this.body.innerHTML = "";
      if (this.active === "radio") { this.renderRadio(); }
      else if (this.active === "themes") { this.renderThemes(); }
      else if (this.active === "display") { this.renderDisplay(); }
      else { this.renderAbout(); }
    },
    renderRadio: function () {
      var self = this;
      var nowPlaying = el("div", { class: "sd-now-playing", text: "Станция не выбрана" });
      if (Radio.current) { nowPlaying.textContent = "Играет: " + Radio.current.name; }
      Radio.onStatus = function (state, station) {
        var label = station ? station.name : "";
        var map = {
          loading: "Загрузка: " + label, playing: "Играет: " + label,
          paused: "Пауза: " + label, stopped: "Остановлено",
          reconnecting: "Переподключение: " + label
        };
        nowPlaying.textContent = map[state] || "";
      };
      var controls = el("div", { class: "sd-controls" }, [
        el("button", { class: "sd-btn", text: "▶", title: "Воспроизвести", onClick: function () { Radio.resume(); } }),
        el("button", { class: "sd-btn", text: "⏸", title: "Пауза", onClick: function () { Radio.pause(); } }),
        el("button", { class: "sd-btn", text: "⏹", title: "Остановить", onClick: function () { Radio.stop(); } })
      ]);
      var volume = el("input", {
        class: "sd-slider", type: "range", min: "0", max: "100",
        value: String(Math.round(clampVolume(Store.get("radio_volume")) * 100)),
        onInput: function (e) { Radio.setVolume(e.target.value / 100); }
      });
      this.body.appendChild(nowPlaying);
      this.body.appendChild(controls);
      this.body.appendChild(el("div", { class: "sd-muted", text: "Громкость (не влияет на системную)" }));
      this.body.appendChild(volume);

      var list = el("div", {});
      var stations = Radio.stations();
      var userStart = BUILTIN_STATIONS.length;
      stations.forEach(function (st, idx) {
        var isUser = idx >= userStart;
        list.appendChild(el("div", {
          class: "sd-row" + (Radio.current && Radio.current.name === st.name ? " active" : "")
        }, [
          el("span", { text: st.name }),
          el("span", {}, [
            el("button", { class: "sd-btn", text: "▶", onClick: function () { Radio.play(st); self.render(); } }),
            isUser ? el("button", { class: "sd-btn", text: "✎", onClick: function () { self.editStation(idx - userStart); } }) : null,
            isUser ? el("button", { class: "sd-btn", text: "🗑", onClick: function () { self.deleteStation(idx - userStart); } }) : null
          ])
        ]));
      });
      this.body.appendChild(el("h3", { text: "Станции" }));
      this.body.appendChild(list);

      this.body.appendChild(el("h3", { text: "Добавить станцию" }));
      var nameInput = el("input", { class: "sd-input", type: "text", placeholder: "Название" });
      var urlInput = el("input", { class: "sd-input", type: "text", placeholder: "http:// или https://" });
      this.body.appendChild(nameInput);
      this.body.appendChild(urlInput);
      this.body.appendChild(el("button", {
        class: "sd-btn", text: "Добавить",
        onClick: function () { self.addStation(nameInput.value, urlInput.value); }
      }));
    },
    addStation: function (name, url) {
      name = (name || "").trim(); url = (url || "").trim();
      if (!name) { this.notify("Укажите название станции"); return; }
      if (!/^https?:\/\//i.test(url)) { this.notify("URL должен начинаться с http:// или https://"); return; }
      var list = Store.get("radio_stations") || [];
      list.push({ name: name, url: url });
      Store.set("radio_stations", list);
      this.render();
    },
    editStation: function (userIdx) {
      var list = Store.get("radio_stations") || [];
      var st = list[userIdx];
      if (!st) { return; }
      var name = window.prompt("Название станции", st.name);
      if (name === null) { return; }
      var url = window.prompt("URL потока", st.url);
      if (url === null) { return; }
      if (!/^https?:\/\//i.test(url)) { this.notify("URL должен начинаться с http:// или https://"); return; }
      list[userIdx] = { name: name.trim() || st.name, url: url.trim() };
      Store.set("radio_stations", list);
      this.render();
    },
    deleteStation: function (userIdx) {
      var list = Store.get("radio_stations") || [];
      list.splice(userIdx, 1);
      Store.set("radio_stations", list);
      this.render();
    },
    renderThemes: function () {
      var self = this;
      var current = Store.get("theme");
      var list = el("div", {});
      Themes.names().forEach(function (name) {
        list.appendChild(el("div", { class: "sd-row" + (name === current ? " active" : "") }, [
          el("span", { text: name }),
          el("button", { class: "sd-btn", text: "Применить", onClick: function () { Themes.apply(name); self.render(); } })
        ]));
      });
      this.body.appendChild(el("div", { class: "sd-muted", text: "Загрузка тем из сети исключена." }));
      this.body.appendChild(list);
    },
    renderDisplay: function () {
      var self = this;
      var current = Display.clamp(Store.get("saturation"));
      var valueLabel = el("span", { text: current + "%" });
      var slider = el("input", {
        class: "sd-slider", type: "range", min: "100", max: "200", step: "1",
        value: String(current),
        onInput: function (e) { valueLabel.textContent = e.target.value + "%"; Display.apply(e.target.value); }
      });
      this.body.appendChild(el("h3", { text: "Насыщенность" }));
      this.body.appendChild(el("div", { class: "sd-controls" }, [valueLabel]));
      this.body.appendChild(slider);
      this.body.appendChild(el("button", { class: "sd-btn", text: "Сбросить", onClick: function () { Display.reset(); self.render(); } }));
      this.body.appendChild(el("p", { class: "sd-muted", text: "Диапазон 100%–200%. Значение по умолчанию — 100%." }));
      this.body.appendChild(el("p", { class: "sd-muted", text: "В автономном приложении насыщенность применяется к окну программы." }));
    },
    renderAbout: function () {
      this.body.appendChild(el("h3", { text: "SD-ON Tool" }));
      this.body.appendChild(el("p", {}, [
        el("div", { text: "Версия: " + VERSION }),
        el("div", { text: "Разработчик: Serge Nook" })
      ]));
      this.body.appendChild(el("p", {}, [
        el("span", { text: "Сайт: " }),
        el("a", { href: "https://sd-on.ru/", target: "_blank", text: "SD-ON.RU" })
      ]));
    },
    notify: function (msg) { window.alert(msg); }
  };

  function boot() {
    Store.load();
    Radio.init();
    UI.mount();
    Themes.restore();
    Display.restore();
    var last = Store.get("last_radio_station");
    if (last) {
      var st = Radio.findByName(last);
      if (st) { Radio.current = st; }
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
