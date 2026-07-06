"""Стили интерфейса SD-ON Tool."""

MAIN_STYLE = """
QMainWindow {
    background-color: #1a1a2e;
}

QWidget#centralWidget {
    background-color: #1a1a2e;
}

QWidget#sidebar {
    background-color: #16213e;
    border-right: 2px solid #0f3460;
}

QPushButton#navButton {
    background-color: transparent;
    color: #a0a0b0;
    border: none;
    border-radius: 12px;
    padding: 16px 20px;
    font-size: 15px;
    font-weight: 500;
    text-align: left;
    min-height: 48px;
}

QPushButton#navButton:hover {
    background-color: #0f3460;
    color: #e0e0f0;
}

QPushButton#navButton:checked {
    background-color: #e94560;
    color: #ffffff;
    font-weight: 600;
}

QLabel#titleLabel {
    color: #e94560;
    font-size: 22px;
    font-weight: 700;
    padding: 10px 0;
}

QLabel#subtitleLabel {
    color: #a0a0b0;
    font-size: 13px;
    padding: 2px 0;
}

QLabel#sectionLabel {
    color: #e0e0f0;
    font-size: 16px;
    font-weight: 600;
    padding: 8px 0;
}

QLabel {
    color: #c0c0d0;
    font-size: 14px;
}

QPushButton#actionButton {
    background-color: #e94560;
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 600;
    min-height: 44px;
}

QPushButton#actionButton:hover {
    background-color: #ff6b81;
}

QPushButton#actionButton:pressed {
    background-color: #c73e54;
}

QPushButton#actionButton:disabled {
    background-color: #3a3a4e;
    color: #606070;
}

QPushButton#secondaryButton {
    background-color: #0f3460;
    color: #c0c0d0;
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 500;
    min-height: 44px;
}

QPushButton#secondaryButton:hover {
    background-color: #1a4a7a;
    color: #e0e0f0;
}

QPushButton#dangerButton {
    background-color: #4a1a2e;
    color: #ff6b81;
    border: 1px solid #e94560;
    border-radius: 10px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 500;
    min-height: 44px;
}

QPushButton#dangerButton:hover {
    background-color: #e94560;
    color: #ffffff;
}

QSlider::groove:horizontal {
    border: none;
    height: 8px;
    background: #0f3460;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #e94560;
    border: none;
    width: 24px;
    height: 24px;
    margin: -8px 0;
    border-radius: 12px;
}

QSlider::sub-page:horizontal {
    background: #e94560;
    border-radius: 4px;
}

QLineEdit {
    background-color: #16213e;
    color: #e0e0f0;
    border: 2px solid #0f3460;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 14px;
    min-height: 40px;
}

QLineEdit:focus {
    border-color: #e94560;
}

QLineEdit::placeholder {
    color: #606070;
}

QScrollArea {
    background-color: transparent;
    border: none;
}

QScrollBar:vertical {
    background: #1a1a2e;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #0f3460;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #e94560;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QFrame#cardFrame {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 12px;
    padding: 16px;
}

QFrame#stationCard {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 12px;
    padding: 12px 16px;
}

QFrame#stationCard:hover {
    border-color: #e94560;
}

QFrame#activeStationCard {
    background-color: #1e2a4a;
    border: 2px solid #e94560;
    border-radius: 12px;
    padding: 12px 16px;
}

QFrame#themeCard {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 12px;
    padding: 16px;
    min-height: 80px;
}

QFrame#themeCard:hover {
    border-color: #e94560;
}

QFrame#activeThemeCard {
    background-color: #1e2a4a;
    border: 2px solid #e94560;
    border-radius: 12px;
    padding: 16px;
    min-height: 80px;
}

QFrame#separator {
    background-color: #0f3460;
    max-height: 2px;
    min-height: 2px;
}

QDialog {
    background-color: #1a1a2e;
}

QMessageBox {
    background-color: #1a1a2e;
}

QMessageBox QLabel {
    color: #e0e0f0;
}

QMessageBox QPushButton {
    background-color: #0f3460;
    color: #e0e0f0;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    min-width: 80px;
}

QMessageBox QPushButton:hover {
    background-color: #e94560;
    color: #ffffff;
}
"""

LOGO_TEXT = """
███████╗██████╗        ██████╗ ███╗   ██╗
██╔════╝██╔══██╗      ██╔═══██╗████╗  ██║
███████╗██║  ██║█████╗██║   ██║██╔██╗ ██║
╚════██║██║  ██║╚════╝██║   ██║██║╚██╗██║
███████║██████╔╝      ╚██████╔╝██║ ╚████║
╚══════╝╚═════╝        ╚═════╝ ╚═╝  ╚═══╝
"""
