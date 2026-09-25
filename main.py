"""
Endocare - Endoscopy Management System
Main Entrypoint for Desktop Healthcare Application
Target OS: Windows Desktop (Optimized for 1366x768 and 1920x1080)
Framework: PySide6 (Qt for Python)
"""

import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont

from app.ui.main_window import MainWindow
from app.styles.theme import get_stylesheet
from app.core.paths import get_asset_path, get_data_dir


def main():
    # Ensure persistent directories and initial database are initialized
    get_data_dir()
    
    app = QApplication(sys.argv)
    app.setApplicationName("Endocare")
    app.setOrganizationName("Endocare Medical Systems")
    
    # Set default clean typography
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)
    
    # Application Window Icon
    logo_ico = get_asset_path("logo.ico")
    logo_png = get_asset_path("logo.png")
    if os.path.exists(logo_ico):
        app.setWindowIcon(QIcon(logo_ico))
    elif os.path.exists(logo_png):
        app.setWindowIcon(QIcon(logo_png))
        
    # Apply modern medical stylesheet
    app.setStyleSheet(get_stylesheet())
    
    # Instantiate and center MainWindow
    window = MainWindow()
    
    # Safe desktop bounds: strictly respect availableGeometry (never overlap Windows desktop taskbar)
    screen = app.primaryScreen()
    avail = screen.availableGeometry() if screen else None
    if avail:
        win_w = min(window.width(), avail.width() - 16)
        win_h = min(window.height(), avail.height() - 20)
        window.resize(win_w, win_h)
        x = avail.x() + (avail.width() - window.width()) // 2
        y = avail.y() + (avail.height() - window.height()) // 2
        window.move(max(avail.x(), x), max(avail.y(), y))
    
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
