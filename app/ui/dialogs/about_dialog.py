from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import os
import platform


class AboutDialog(QDialog):
    """
    Modern Clinical About & System Diagnostics Dialog.
    Displays software version, credits, and imaging subsystem status.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Endocare")
        self.setFixedSize(520, 420)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._init_ui()

    def _init_ui(self):
        container = QFrame(self)
        container.setObjectName("aboutModalContainer")
        container.setStyleSheet("""
            QFrame#aboutModalContainer {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0F172A, stop:1 #090E17);
                border: 2px solid #0284C7;
                border-radius: 14px;
            }
            QLabel {
                color: #E2E8F0;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)
        
        # Header with Logo & Title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)
        
        logo_label = QLabel()
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../assets/logo.png"))
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(110, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pix)
        
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        
        app_name = QLabel("ENDOCARE")
        app_name.setStyleSheet("font-size: 20px; font-weight: 800; color: #38BDF8; letter-spacing: 1px;")
        
        app_desc = QLabel("Medical Image Processing & Report Printing Software")
        app_desc.setStyleSheet("font-size: 11px; color: #94A3B8; font-weight: 500;")
        
        ver_tag = QLabel("Release Version 2.42  •  Build 2026.09 (64-bit)")
        ver_tag.setStyleSheet("font-size: 11px; color: #10B981; font-weight: 600;")
        
        title_box.addWidget(app_name)
        title_box.addWidget(app_desc)
        title_box.addWidget(ver_tag)
        
        header_layout.addWidget(logo_label)
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Separator Line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #1E293B; max-height: 1px;")
        layout.addWidget(line)
        
        # Metadata / Spec Grid
        info_frame = QFrame()
        info_frame.setObjectName("specBox")
        info_frame.setStyleSheet("""
            QFrame#specBox {
                background-color: rgba(255, 255, 255, 0.04);
                border: 1px solid #1E293B;
                border-radius: 8px;
            }
            QLabel {
                background: transparent;
                border: none;
                padding: 2px 0px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(14, 12, 14, 12)
        info_layout.setSpacing(6)
        
        credits_lbl = QLabel("<b>Development & Engineering:</b> Team Gigabyte")
        credits_lbl.setStyleSheet("font-size: 12px; color: #E2E8F0;")
        
        tagline_lbl = QLabel("<b>Motto:</b> All Solution of Endoscopy")
        tagline_lbl.setStyleSheet("font-size: 12px; color: #94A3B8;")
        
        license_lbl = QLabel("<b>License:</b> Commercial Clinical Workstation License (Active)")
        license_lbl.setStyleSheet("font-size: 12px; color: #10B981;")
        
        system_lbl = QLabel(f"<b>System:</b> {platform.system()} {platform.release()}  |  Python {platform.python_version()}  |  Qt 6.x")
        system_lbl.setStyleSheet("font-size: 11px; color: #64748B;")
        
        grabber_lbl = QLabel("<b>Hardware Engine:</b> USB2 / DirectShow 4K Capture Pipeline")
        grabber_lbl.setStyleSheet("font-size: 11px; color: #38BDF8;")
        
        info_layout.addWidget(credits_lbl)
        info_layout.addWidget(tagline_lbl)
        info_layout.addWidget(license_lbl)
        info_layout.addWidget(system_lbl)
        info_layout.addWidget(grabber_lbl)
        layout.addWidget(info_frame)
        
        # Bottom Close Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setFixedSize(110, 36)
        close_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0284C7, stop:1 #0369A1);
                color: #FFFFFF;
                border: 1px solid #38BDF8;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #0284C7;
                border-color: #7DD3FC;
            }
        """)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
