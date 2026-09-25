import os
from datetime import datetime
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, 
    QToolButton, QWidget, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QIcon, QPixmap
from app.core.paths import get_asset_path


class HeaderBar(QFrame):
    """
    Fixed top header component for Endocare Desktop Application.
    Contains branding, live system clock, user profile status, and window controls.
    """
    minimize_requested = Signal()
    maximize_requested = Signal()
    close_requested = Signal()
    settings_requested = Signal()
    
    def __init__(self, parent=None, is_frameless=True):
        super().__init__(parent)
        self.setObjectName("headerBar")
        self.is_frameless = is_frameless
        self._drag_pos = None
        self._init_ui()
        self._init_timer()
        
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 14, 0)
        layout.setSpacing(16)
        
        # ----------------- LEFT: Branding -----------------
        left_layout = QHBoxLayout()
        left_layout.setSpacing(12)
        
        # Official Endo Care Brand Logo Badge
        logo_badge = QFrame()
        logo_badge.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 8px;
                padding: 3px 10px;
                border: 1px solid rgba(255, 255, 255, 0.25);
            }
        """)
        badge_layout = QHBoxLayout(logo_badge)
        badge_layout.setContentsMargins(4, 2, 4, 2)
        badge_layout.setSpacing(0)
        
        self.logo_label = QLabel()
        logo_img_path = get_asset_path("logo.png")
        if os.path.exists(logo_img_path):
            pix = QPixmap(logo_img_path).scaled(140, 42, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(pix)
        else:
            self.logo_label.setText("Endo Care")
            self.logo_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #F58220;")
        badge_layout.addWidget(self.logo_label)
        left_layout.addWidget(logo_badge)
        
        # Hospital / System Subtitle
        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(2)
        brand_layout.setAlignment(Qt.AlignVCenter)
        
        self.title_label = QLabel("ENDOSCOPY MANAGEMENT SYSTEM")
        self.title_label.setStyleSheet("color: #FFFFFF; font-size: 13px; font-weight: 700; letter-spacing: 0.8px;")
        
        self.subtitle_label = QLabel("Clinical Diagnostic Station • USB Capture Active")
        self.subtitle_label.setStyleSheet("color: #38BDF8; font-size: 11px; font-weight: 500;")
        
        brand_layout.addWidget(self.title_label)
        brand_layout.addWidget(self.subtitle_label)
        left_layout.addLayout(brand_layout)
        
        layout.addLayout(left_layout)
        
        # Spacer between left and right
        layout.addStretch()
        
        # ----------------- RIGHT: Meta Controls -----------------
        right_layout = QHBoxLayout()
        right_layout.setSpacing(12)
        right_layout.setAlignment(Qt.AlignVCenter)
        
        # Live System Date & Time
        self.clock_label = QLabel()
        self.clock_label.setObjectName("headerClock")
        self._update_clock()
        right_layout.addWidget(self.clock_label)
        
        # Clinician Profile Badge
        user_badge = QFrame()
        user_badge.setObjectName("userBadge")
        user_badge_layout = QHBoxLayout(user_badge)
        user_badge_layout.setContentsMargins(8, 4, 10, 4)
        user_badge_layout.setSpacing(8)
        
        # User Icon / Avatar
        user_icon_label = QLabel()
        user_icon_path = get_asset_path("user.svg")
        if os.path.exists(user_icon_path):
            user_pix = QPixmap(user_icon_path).scaled(18, 18, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            user_icon_label.setPixmap(user_pix)
        else:
            user_icon_label.setText("👤")
            user_icon_label.setStyleSheet("font-size: 16px; color: #E0F2FE;")
        user_badge_layout.addWidget(user_icon_label)
        
        user_info_layout = QVBoxLayout()
        user_info_layout.setSpacing(0)
        self.user_name = QLabel("Dr. Sarah Jenkins")
        self.user_name.setObjectName("userName")
        self.user_role = QLabel("Senior Gastroenterologist • Suite 1")
        self.user_role.setObjectName("userRole")
        user_info_layout.addWidget(self.user_name)
        user_info_layout.addWidget(self.user_role)
        user_badge_layout.addLayout(user_info_layout)
        
        # Online pulse indicator
        online_dot = QLabel("●")
        online_dot.setStyleSheet("color: #10B981; font-size: 12px; margin-left: 4px;")
        user_badge_layout.addWidget(online_dot)
        
        right_layout.addWidget(user_badge)
        
        # Settings Button
        self.settings_btn = QToolButton()
        self.settings_btn.setObjectName("headerButton")
        self.settings_btn.setToolTip("System Configuration & Settings")
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        settings_icon_path = get_asset_path("settings.svg")
        if os.path.exists(settings_icon_path):
            self.settings_btn.setIcon(QIcon(settings_icon_path))
        else:
            self.settings_btn.setText("⚙")
        self.settings_btn.clicked.connect(self.settings_requested.emit)
        right_layout.addWidget(self.settings_btn)
        
        # Window Controls (Minimize, Maximize, Close)
        if self.is_frameless:
            win_controls_frame = QFrame()
            win_layout = QHBoxLayout(win_controls_frame)
            win_layout.setContentsMargins(6, 0, 0, 0)
            win_layout.setSpacing(4)
            
            self.min_btn = QToolButton()
            self.min_btn.setObjectName("winControlBtn")
            self.min_btn.setText("—")
            self.min_btn.setToolTip("Minimize Window")
            self.min_btn.clicked.connect(self.minimize_requested.emit)
            win_layout.addWidget(self.min_btn)
            
            self.max_btn = QToolButton()
            self.max_btn.setObjectName("winControlBtn")
            self.max_btn.setText("🗖")
            self.max_btn.setToolTip("Maximize / Restore")
            self.max_btn.clicked.connect(self.maximize_requested.emit)
            win_layout.addWidget(self.max_btn)
            
            self.close_btn = QToolButton()
            self.close_btn.setObjectName("winCloseBtn")
            self.close_btn.setText("✕")
            self.close_btn.setToolTip("Close Application")
            self.close_btn.clicked.connect(self.close_requested.emit)
            win_layout.addWidget(self.close_btn)
            
            right_layout.addWidget(win_controls_frame)
            
        layout.addLayout(right_layout)

    def _init_timer(self):
        """Timer to keep the header clock updated every second."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_clock)
        self.timer.start(1000)

    def _update_clock(self):
        now = datetime.now()
        date_str = now.strftime("%A, %b %d, %Y")
        time_str = now.strftime("%I:%M:%S %p")
        self.clock_label.setText(f"{date_str}   |   {time_str}")

    # Allow dragging window from header when frameless
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_frameless:
            window = self.window()
            if window and not window.isMaximized():
                self._drag_pos = event.globalPosition().toPoint() - window.frameGeometry().topLeft()
                event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.LeftButton and self.is_frameless:
            window = self.window()
            if window and not window.isMaximized():
                window.move(event.globalPosition().toPoint() - self._drag_pos)
                event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_frameless:
            self.maximize_requested.emit()
            event.accept()
        super().mouseDoubleClickEvent(event)
