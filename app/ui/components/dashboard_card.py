import os
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QGraphicsDropShadowEffect, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPixmap, QCursor


class DashboardCard(QFrame):
    """
    High-fidelity clinical action card for Endocare Home Dashboard.
    Features icon container, bold title, descriptive subtitle, status badge,
    and responsive hover states.
    """
    clicked = Signal()
    
    def __init__(self, title: str, subtitle: str, icon_file: str, badge_text: str = None, 
                 accent_color: str = "#0284C7", parent=None):
        super().__init__(parent)
        self.setObjectName("dashboardCard")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumHeight(140)
        
        self.accent_color = accent_color
        self.is_hovered = False
        
        # Subtle Drop Shadow
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(16)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(4)
        self.shadow.setColor(QColor(15, 23, 42, 16))
        self.setGraphicsEffect(self.shadow)
        
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)
        
        # Top Row: Icon Container + Badge + Arrow
        top_row = QHBoxLayout()
        top_row.setSpacing(12)
        
        # Icon Container
        self.icon_box = QFrame()
        self.icon_box.setObjectName("cardIconContainer")
        self.icon_box.setStyleSheet(f"""
            QFrame#cardIconContainer {{
                background-color: {self.accent_color}18;
                border: 1px solid {self.accent_color}33;
                border-radius: 12px;
            }}
        """)
        icon_layout = QVBoxLayout(self.icon_box)
        icon_layout.setAlignment(Qt.AlignCenter)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel()
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../assets", icon_file))
        if os.path.exists(icon_path):
            pix = QPixmap(icon_path).scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pix)
        else:
            icon_label.setText("📋")
        icon_layout.addWidget(icon_label)
        top_row.addWidget(self.icon_box)
        
        top_row.addStretch()
        
        # Optional Status / Meta Badge
        if badge_text:
            badge = QLabel(badge_text)
            badge.setStyleSheet(f"""
                QLabel {{
                    background-color: {self.accent_color}14;
                    color: {self.accent_color};
                    font-size: 11px;
                    font-weight: 600;
                    border: 1px solid {self.accent_color}25;
                    border-radius: 6px;
                    padding: 3px 10px;
                }}
            """)
            top_row.addWidget(badge)
            
        # Subtle Arrow
        self.arrow_lbl = QLabel("→")
        self.arrow_lbl.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #94A3B8;
            }
        """)
        top_row.addWidget(self.arrow_lbl)
        layout.addLayout(top_row)
        
        # Bottom text block
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        self.title_lbl = QLabel(title)
        self.title_lbl.setObjectName("cardTitle")
        
        self.subtitle_lbl = QLabel(subtitle)
        self.subtitle_lbl.setObjectName("cardSubtitle")
        self.subtitle_lbl.setWordWrap(True)
        
        text_layout.addWidget(self.title_lbl)
        text_layout.addWidget(self.subtitle_lbl)
        layout.addLayout(text_layout)

    def enterEvent(self, event):
        self.is_hovered = True
        self.shadow.setBlurRadius(24)
        self.shadow.setYOffset(8)
        self.shadow.setColor(QColor(2, 132, 199, 45))
        self.arrow_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #0284C7;")
        self.setStyleSheet(f"""
            QFrame#dashboardCard {{
                background-color: #F8FAFC;
                border: 1.5px solid {self.accent_color};
                border-radius: 12px;
            }}
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.shadow.setBlurRadius(16)
        self.shadow.setYOffset(4)
        self.shadow.setColor(QColor(15, 23, 42, 16))
        self.arrow_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #94A3B8;")
        self.setStyleSheet("""
            QFrame#dashboardCard {
                background-color: #FFFFFF;
                border: 1.5px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
            event.accept()
        super().mousePressEvent(event)
