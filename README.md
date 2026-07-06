# SD-ON Tool

**Автономное приложение для Steam Deck** — дополнительные возможности настройки системы без использования сторонних плагинов и магазина расширений.

## Возможности

### 📻 Радио
- 8 встроенных интернет-радиостанций
- Поддержка MP3, AAC, AAC+, HTTP/HTTPS потоков
- Воспроизведение через HTML5 `<audio>` — без дополнительного ПО
- Добавление/удаление/редактирование пользовательских станций
- Управление воспроизведением и громкостью
- Автоматическое переподключение при обрыве

### ℹ О программе
- Версия, автор, сайт

## Технологии

- **Backend**: Java 17, встроенный HTTP-сервер (`com.sun.net.httpserver`)
- **Frontend**: HTML5 / CSS / JavaScript
- **Аудио**: HTML5 `<audio>` — проигрывание потоков как в браузере
- **Упаковка**: AppImage с встроенным JRE (jlink)

## Установка

### Через установщик (рекомендуется)

```bash
chmod +x SD-ON-Tool-Installer.sh
./SD-ON-Tool-Installer.sh
```

Нажмите «Установить» — приложение установится и появится в меню.
Для удаления запустите тот же файл и нажмите «Удалить».

### AppImage

```bash
chmod +x SD-ON-Tool-1.1.0-x86_64.AppImage
./SD-ON-Tool-1.1.0-x86_64.AppImage
```

### Из исходников

```bash
./gradlew jar
java -jar build/libs/sd-on-tool-1.1.0.jar
```

## Сборка AppImage

```bash
./gradlew jar
jlink --add-modules java.base,java.desktop,java.net.http,java.logging,jdk.httpserver \
      --strip-debug --no-man-pages --no-header-files --compress=2 --output build/jre
# Далее: создание AppDir и appimagetool
```

## Структура проекта

```
SD-ON Tool
├── src/main/
│   ├── java/ru/sdon/tool/
│   │   ├── App.java           # Точка входа, запуск сервера + браузера
│   │   ├── WebServer.java     # Встроенный HTTP-сервер
│   │   ├── api/               # REST API (станции, конфигурация)
│   │   └── model/             # Модели данных
│   └── resources/web/
│       ├── index.html          # Главная страница
│       ├── css/style.css       # Стили
│       └── js/app.js           # Клиентская логика + аудиоплеер
├── packaging/                  # Скрипты сборки и установки
├── build.gradle
└── gradlew
```

## Требования

- Steam Deck / SteamOS
- Дополнительные программы не требуются (JRE встроен в AppImage)

## Язык интерфейса

Русский

## Автор

**Serge Nook** — [SD-ON.RU](https://sd-on.ru)

## Лицензия

MIT
