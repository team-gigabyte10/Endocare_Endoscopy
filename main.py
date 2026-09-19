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


def main():
    # Qt 6 handles high-DPI scaling automatically by default
        
    app = QApplication(sys.argv)
    app.setApplicationName("Endocare")
    app.setOrganizationName("Endocare Medical Systems")
    
    # Set default clean typography
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)
    
    # Application Window Icon
    logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets/logo.png"))
    if os.path.exists(logo_path):
        app.setWindowIcon(QIcon(logo_path))
        
    # Apply modern medical stylesheet
    app.setStyleSheet(get_stylesheet())
    
    # Instantiate and center MainWindow
    window = MainWindow()
    
    # Center on screen
    screen_geo = app.primaryScreen().availableGeometry()
    x = (screen_geo.width() - window.width()) // 2
    y = (screen_geo.height() - window.height()) // 2
    window.move(max(0, x), max(0, y))
    
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
