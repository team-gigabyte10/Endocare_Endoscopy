import sys
import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QFrame, QPushButton, QComboBox,
    QToolButton, QMessageBox, QGraphicsDropShadowEffect, QDialog, QSizePolicy
)
from PySide6.QtCore import Qt, QPoint, QSize
from PySide6.QtGui import QIcon, QPixmap, QColor, QFont, QCursor

from app.ui.dialogs.about_dialog import AboutDialog
from app.ui.dialogs.capture_card_dialog import CaptureCardDialog
from app.ui.dialogs.new_patient_dialog import NewPatientDialog
from app.ui.dialogs.archive_dialog import ArchiveDialog
from app.ui.dialogs.doctors_dialog import DoctorsDialog
from app.ui.dialogs.referrers_dialog import ReferrersDialog
from app.ui.dialogs.templates_dialog import TemplatesDialog


class ImagePreviewModal(QDialog):
    """Simple high-definition viewport zoom modal when user clicks a thumbnail."""
    def __init__(self, img_path: str, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(680, 520)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        container = QFrame(self)
        container.setStyleSheet("""
            QFrame {
                background-color: #0B131E;
                border: 2px solid #0284C7;
                border-radius: 12px;
            }
        """)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(container)
        
        lay = QVBoxLayout(container)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(12)
        
        header = QHBoxLayout()
        t_lbl = QLabel(title)
        t_lbl.setStyleSheet("color: #38BDF8; font-size: 16px; font-weight: 700;")
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #1E293B;
                color: #CBD5E1;
                border: 1px solid #334155;
                border-radius: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #DC2626;
                color: #FFFFFF;
                border-color: #F87171;
            }
        """)
        close_btn.clicked.connect(self.accept)
        header.addWidget(t_lbl)
        header.addStretch()
        header.addWidget(close_btn)
        lay.addLayout(header)
        
        img_lbl = QLabel()
        img_lbl.setAlignment(Qt.AlignCenter)
        if os.path.exists(img_path):
            pix = QPixmap(img_path).scaled(640, 420, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img_lbl.setPixmap(pix)
        lay.addWidget(img_lbl)


class MainWindow(QMainWindow):
    """
    Main Launcher Window for Endocare Endoscopy Management System.
    Non-fullscreen, professional clinical desktop launcher for Endocare.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Endocare - Medical Image Processing & Report Printing Software")
        self.setFixedSize(1040, 620)
        
        # Frameless window with custom sleek title bar & rounded container
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # State for dragging frameless window
        self._drag_pos = QPoint()
        self._is_dragging = False
        
        self._assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../assets"))
        self._init_ui()

    def _init_ui(self):
        central_widget = QWidget(self)
        central_widget.setObjectName("launcherRoot")
        self.setCentralWidget(central_widget)
        
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(10, 10, 10, 10)
        
        # Outer Card Container
        self.container = QFrame()
        self.container.setObjectName("launcherCentralContainer")
        
        # Add modern drop shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 8)
        self.container.setGraphicsEffect(shadow)
        
        root_layout.addWidget(self.container)
        
        # Main Layout inside the launcher container
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(24, 18, 24, 20)
        container_layout.setSpacing(12)
        
        # -------------------------------------------------------------
        # 1. TOP BAR: [ABOUT] ... SUBTITLE ... [MINIMIZE] [EXIT]
        # -------------------------------------------------------------
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        
        # ABOUT Circular Button
        self.btn_about = QPushButton("ABOUT")
        self.btn_about.setObjectName("aboutCornerBtn")
        self.btn_about.setFixedSize(84, 42)
        self.btn_about.setCursor(Qt.PointingHandCursor)
        self.btn_about.clicked.connect(self._open_about)
        top_bar.addWidget(self.btn_about)
        
        top_bar.addStretch()
        
        # Medical Image Processing Subtitle
        self.lbl_subtitle = QLabel("Medical Image Processing & Report Printing Software")
        self.lbl_subtitle.setObjectName("heroAppSubtitle")
        self.lbl_subtitle.setAlignment(Qt.AlignCenter)
        top_bar.addWidget(self.lbl_subtitle)
        
        top_bar.addStretch()
        
        # Top-right controls: Minimize & EXIT
        top_right_layout = QHBoxLayout()
        top_right_layout.setSpacing(10)
        
        btn_min = QToolButton()
        btn_min.setText("—")
        btn_min.setObjectName("winControlBtn")
        btn_min.setToolTip("Minimize")
        btn_min.setCursor(Qt.PointingHandCursor)
        btn_min.clicked.connect(self.showMinimized)
        top_right_layout.addWidget(btn_min)
        
        self.btn_exit = QPushButton("EXIT")
        self.btn_exit.setObjectName("exitCornerBtn")
        self.btn_exit.setFixedSize(84, 42)
        self.btn_exit.setCursor(Qt.PointingHandCursor)
        self.btn_exit.clicked.connect(self._confirm_exit)
        top_right_layout.addWidget(self.btn_exit)
        
        top_bar.addLayout(top_right_layout)
        container_layout.addLayout(top_bar)
        
        # -------------------------------------------------------------
        # 2. HERO SECTION: Endocare Brand Logo & Version
        # -------------------------------------------------------------
        hero_layout = QVBoxLayout()
        hero_layout.setSpacing(4)
        
        title_row = QHBoxLayout()
        title_row.addStretch()
        
        # Center Endocare Brand Logo
        self.lbl_title = QLabel()
        self.lbl_title.setObjectName("heroLogoLabel")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        logo_path = os.path.join(self._assets_dir, "logo.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(340, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_title.setPixmap(pix)
        else:
            self.lbl_title.setText("ENDOCARE")
            self.lbl_title.setObjectName("heroAppTitle")
        title_row.addWidget(self.lbl_title)
        
        title_row.addStretch()
        
        # Version Tag aligned right
        ver_tag = QLabel("ver: 2.42")
        ver_tag.setObjectName("heroVerTag")
        ver_tag.setAlignment(Qt.AlignBottom | Qt.AlignRight)
        title_row.addWidget(ver_tag)
        
        hero_layout.addLayout(title_row)
        
        # Horizontal Cyan Glowing Divider Line
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 transparent, stop:0.2 #0284C7, stop:0.5 #38BDF8, stop:0.8 #0284C7, stop:1 transparent);
            max-height: 2px;
            margin-top: 2px;
            margin-bottom: 2px;
        """)
        hero_layout.addWidget(divider)
        
        # Metadata Sub-Bar: "developed by Team Gigabyte" and "Clinical Edition"
        meta_row = QHBoxLayout()
        meta_row.setContentsMargins(4, 2, 4, 4)
        
        lbl_dev = QLabel("developed by  Team Gigabyte")
        lbl_dev.setObjectName("devCreditText")
        meta_row.addWidget(lbl_dev)
        
        meta_row.addStretch()
        
        lbl_edition = QLabel("Clinical Edition")
        lbl_edition.setObjectName("editionBadge")
        lbl_edition.setFixedHeight(24)
        meta_row.addWidget(lbl_edition)
        
        hero_layout.addLayout(meta_row)
        container_layout.addLayout(hero_layout)
        
        # Add flexible spacer between hero title and workspace
        container_layout.addStretch(1)
        
        # -------------------------------------------------------------
        # 3. LOWER WORKSPACE: (Left Brand, Center Previews, Right Actions)
        # -------------------------------------------------------------
        workspace_layout = QHBoxLayout()
        workspace_layout.setContentsMargins(6, 4, 6, 8)
        workspace_layout.setSpacing(16)
        workspace_layout.setAlignment(Qt.AlignBottom)
        
        # === A. LEFT COLUMN: Bissoft Brand & System Status ===
        left_col = QVBoxLayout()
        left_col.setContentsMargins(0, 0, 0, 0)
        left_col.setSpacing(10)
        left_col.setAlignment(Qt.AlignBottom)
        
        # Bissoft Logo Frame
        logo_frame = QFrame()
        logo_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(6, 20, 30, 0.6);
                border: 1.5px solid rgba(16, 185, 129, 0.4);
                border-radius: 10px;
                padding: 6px;
            }
        """)
        lf_layout = QVBoxLayout(logo_frame)
        lf_layout.setContentsMargins(4, 4, 4, 4)
        
        self.lbl_logo = QLabel()
        self.lbl_logo.setAlignment(Qt.AlignCenter)
        logo_file = os.path.join(self._assets_dir, "bissoft_logo.png")
        if os.path.exists(logo_file):
            pix = QPixmap(logo_file).scaled(220, 115, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_logo.setPixmap(pix)
        else:
            self.lbl_logo.setText("bissoft")
            self.lbl_logo.setStyleSheet("color: #10B981; font-size: 26px; font-weight: bold;")
        lf_layout.addWidget(self.lbl_logo)
        left_col.addWidget(logo_frame)
        
        # Hardware Status Tag
        status_box = QFrame()
        status_box.setStyleSheet("""
            QFrame {
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid rgba(16, 185, 129, 0.4);
                border-radius: 6px;
                padding: 5px 8px;
            }
        """)
        s_lay = QHBoxLayout(status_box)
        s_lay.setContentsMargins(6, 4, 6, 4)
        s_lay.setSpacing(8)
        
        dot = QLabel("●")
        dot.setStyleSheet("color: #10B981; font-size: 12px;")
        s_txt = QLabel("USB2 Video Grabber Ready")
        s_txt.setStyleSheet("color: #F1F5F9; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;")
        s_lay.addWidget(dot)
        s_lay.addWidget(s_txt)
        s_lay.addStretch()
        
        left_col.addWidget(status_box)
        workspace_layout.addLayout(left_col, stretch=24)
        
        # === B. CENTER COLUMN: 3 Endoscopy Viewports + Capture Card Bar ===
        center_col = QVBoxLayout()
        center_col.setContentsMargins(0, 0, 0, 0)
        center_col.setSpacing(10)
        center_col.setAlignment(Qt.AlignBottom)
        
        # Row of 3 Viewports
        previews_row = QHBoxLayout()
        previews_row.setSpacing(8)
        
        self.vp1 = self._create_viewport_card("preview_ercp.png", "ERCP / Fluoro")
        self.vp2 = self._create_viewport_card("preview_endo.png", "Endoscopy HD")
        self.vp3 = self._create_viewport_card("preview_usg.png", "Doppler US")
        
        previews_row.addWidget(self.vp1)
        previews_row.addWidget(self.vp2)
        previews_row.addWidget(self.vp3)
        center_col.addLayout(previews_row)
        
        # Capture Card Selection Bar
        capture_bar = QHBoxLayout()
        capture_bar.setSpacing(8)
        
        lbl_cc = QLabel("Capture Card")
        lbl_cc.setObjectName("captureCardLabel")
        capture_bar.addWidget(lbl_cc)
        
        self.combo_capture = QComboBox()
        self.combo_capture.setObjectName("captureCardCombo")
        self.combo_capture.addItem("1. USB2 Video (1080p @ 60 FPS)")
        self.combo_capture.addItem("2. HDMI Medical Grabber (DirectShow)")
        self.combo_capture.addItem("3. Olympus EVIS X1 Direct Stream")
        self.combo_capture.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        capture_bar.addWidget(self.combo_capture)
        
        btn_cc_settings = QToolButton()
        btn_cc_settings.setText("⚙")
        btn_cc_settings.setToolTip("Open Capture Card Library & Settings")
        btn_cc_settings.setCursor(Qt.PointingHandCursor)
        btn_cc_settings.setStyleSheet("""
            QToolButton {
                background: #1E293B;
                color: #38BDF8;
                border: 1px solid #0284C7;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
                font-weight: bold;
            }
            QToolButton:hover {
                background: #0284C7;
                color: #FFFFFF;
                border-color: #7DD3FC;
            }
        """)
        btn_cc_settings.clicked.connect(lambda: self._open_capture_cards("library"))
        capture_bar.addWidget(btn_cc_settings)
        
        btn_launch_capture = QPushButton("📹 Capture")
        btn_launch_capture.setToolTip("Open Live Endoscopy Capture Workstation")
        btn_launch_capture.setCursor(Qt.PointingHandCursor)
        btn_launch_capture.setStyleSheet("""
            QPushButton {
                background: #0284C7;
                color: #FFFFFF;
                border: 1.5px solid #38BDF8;
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 800;
            }
            QPushButton:hover {
                background: #0369A1;
                border-color: #7DD3FC;
            }
        """)
        btn_launch_capture.clicked.connect(self._open_capture_window)
        capture_bar.addWidget(btn_launch_capture)
        
        center_col.addLayout(capture_bar)
        workspace_layout.addLayout(center_col, stretch=48)
        
        # === C. RIGHT COLUMN: 5 Clinical Action Buttons ===
        right_col = QVBoxLayout()
        right_col.setContentsMargins(0, 0, 0, 0)
        right_col.setSpacing(8)
        right_col.setAlignment(Qt.AlignBottom)
        
        # 2x2 Grid for Top 4 Actions
        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)
        
        # 1. New Patient (Alt+N)
        self.btn_new_patient = QPushButton("&New Patient")
        self.btn_new_patient.setProperty("class", "clinicalActionBtn")
        self.btn_new_patient.setToolTip("Register New Patient (Alt+N)")
        self.btn_new_patient.setCursor(Qt.PointingHandCursor)
        self.btn_new_patient.setFixedHeight(50)
        self._set_button_icon(self.btn_new_patient, "patient.svg")
        self.btn_new_patient.clicked.connect(self._open_new_patient)
        grid.addWidget(self.btn_new_patient, 0, 0)
        
        # 2. Patients Archive (Alt+A)
        self.btn_archive = QPushButton("Patients &Archive")
        self.btn_archive.setProperty("class", "clinicalActionBtn")
        self.btn_archive.setToolTip("Open Patient Archive (Alt+A)")
        self.btn_archive.setCursor(Qt.PointingHandCursor)
        self.btn_archive.setFixedHeight(50)
        self._set_button_icon(self.btn_archive, "archive.svg")
        self.btn_archive.clicked.connect(self._open_archive)
        grid.addWidget(self.btn_archive, 0, 1)
        
        # 3. Doctors (Alt+D)
        self.btn_doctors = QPushButton("&Doctors")
        self.btn_doctors.setProperty("class", "clinicalActionBtn")
        self.btn_doctors.setToolTip("Manage Clinical Doctors (Alt+D)")
        self.btn_doctors.setCursor(Qt.PointingHandCursor)
        self.btn_doctors.setFixedHeight(50)
        self._set_button_icon(self.btn_doctors, "doctor.svg")
        self.btn_doctors.clicked.connect(self._open_doctors)
        grid.addWidget(self.btn_doctors, 1, 0)
        
        # 4. Referrers (Alt+R)
        self.btn_referrers = QPushButton("&Referrers")
        self.btn_referrers.setProperty("class", "clinicalActionBtn")
        self.btn_referrers.setToolTip("Manage Referring Physicians (Alt+R)")
        self.btn_referrers.setCursor(Qt.PointingHandCursor)
        self.btn_referrers.setFixedHeight(50)
        self._set_button_icon(self.btn_referrers, "referrer.svg")
        self.btn_referrers.clicked.connect(self._open_referrers)
        grid.addWidget(self.btn_referrers, 1, 1)
        
        right_col.addLayout(grid)
        
        # 5. Templates (Alt+T) Full Width Button
        self.btn_templates = QPushButton("&Templates")
        self.btn_templates.setProperty("class", "clinicalActionWideBtn")
        self.btn_templates.setToolTip("Manage Examination Report Templates (Alt+T)")
        self.btn_templates.setCursor(Qt.PointingHandCursor)
        self.btn_templates.setFixedHeight(44)
        self._set_button_icon(self.btn_templates, "template.svg")
        self.btn_templates.clicked.connect(self._open_templates)
        right_col.addWidget(self.btn_templates)
        
        workspace_layout.addLayout(right_col, stretch=30)
        
        container_layout.addLayout(workspace_layout)

    def _create_viewport_card(self, filename: str, modality: str) -> QFrame:
        """Constructs an endoscopy preview card with border glow and click-to-zoom."""
        frame = QFrame()
        frame.setProperty("class", "viewportFrame")
        frame.setCursor(Qt.PointingHandCursor)
        frame.setFixedSize(126, 126)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        # Image Display
        img_lbl = QLabel()
        img_lbl.setAlignment(Qt.AlignCenter)
        img_path = os.path.join(self._assets_dir, filename)
        if os.path.exists(img_path):
            pix = QPixmap(img_path).scaled(118, 96, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            img_lbl.setPixmap(pix)
        else:
            img_lbl.setText("FEED")
            img_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
        layout.addWidget(img_lbl)
        
        # Modality Badge
        badge = QLabel(modality)
        badge.setProperty("class", "modalityBadge")
        badge.setAlignment(Qt.AlignCenter)
        layout.addWidget(badge)
        
        # Click handler to open live capture
        frame.mousePressEvent = lambda e: self._open_capture_window()
        return frame

    def _set_button_icon(self, button: QPushButton, icon_filename: str):
        """Attaches a clean SVG icon to the button if present."""
        icon_path = os.path.join(self._assets_dir, icon_filename)
        if os.path.exists(icon_path):
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(18, 18))

    # --- Window Dragging Logic (Frameless Window) ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragging = True
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._is_dragging and (event.buttons() & Qt.LeftButton):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._is_dragging = False
        event.accept()

    # --- Actions & Dialog Handlers ---
    def _open_about(self):
        dlg = AboutDialog(self)
        dlg.exec()

    def _confirm_exit(self):
        reply = QMessageBox.question(
            self, "Exit Endocare",
            "Are you sure you want to terminate Endocare?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.close()

    def _open_new_patient(self):
        from app.ui.workstation_window import WorkstationWindow
        dlg = WorkstationWindow(initial_module="new_patient", parent=self)
        dlg.showMaximized()
        dlg.exec()

    def _open_archive(self):
        from app.ui.dialogs.archive_dialog import ArchiveDialog
        dlg = ArchiveDialog(parent=self)
        dlg.showMaximized()
        dlg.exec()

    def _open_doctors(self):
        from app.ui.workstation_window import WorkstationWindow
        dlg = WorkstationWindow(initial_module="doctors", parent=self)
        dlg.showMaximized()
        dlg.exec()

    def _open_referrers(self):
        from app.ui.workstation_window import WorkstationWindow
        dlg = WorkstationWindow(initial_module="referrers", parent=self)
        dlg.showMaximized()
        dlg.exec()

    def _open_templates(self):
        from app.ui.workstation_window import WorkstationWindow
        dlg = WorkstationWindow(initial_module="templates", parent=self)
        dlg.showMaximized()
        dlg.exec()

    def _open_capture_cards(self, mode="library"):
        dlg = CaptureCardDialog(mode=mode, parent=self)
        dlg.showMaximized()
        dlg.exec()

    def _open_capture_window(self):
        from app.ui.capture_window import CaptureWindow
        dlg = CaptureWindow(parent=self)
        screen = self.screen() or QApplication.primaryScreen()
        if screen:
            dlg.setGeometry(screen.availableGeometry())
        dlg.showMaximized()
        dlg.exec()
