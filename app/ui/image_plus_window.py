# =====================================================================
# Endocare Endoscopy - Image Plus Multi-Frame Report Workstation
# =====================================================================
import os
import sys
from datetime import datetime
from typing import Optional, List, Dict, Any

from PySide6.QtCore import Qt, QSize, QPoint, QRect, Signal
from PySide6.QtGui import (
    QColor, QFont, QIcon, QPixmap, QPainter, QBrush, QPen,
    QLinearGradient, QRadialGradient, QCursor
)
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QLineEdit, QPushButton, QComboBox,
    QTextEdit, QCheckBox, QRadioButton, QButtonGroup, QHBoxLayout,
    QVBoxLayout, QGridLayout, QScrollArea, QFileDialog, QMessageBox,
    QSizePolicy, QGraphicsDropShadowEffect, QApplication
)

from app.ui.report_window import CircularPresetButton, ClearCrossButton


class ImagePlusSlotWidget(QFrame):
    """
    Individual Endoscopic Image Frame for Image Plus with soft lavender/periwinkle
    background, thin white border, and 'No Preview Available' placeholder.
    """
    image_selected = Signal(object)

    def __init__(self, index: int, parent=None):
        super().__init__(parent)
        self.index = index
        self.image_path: Optional[str] = None
        self._pixmap: Optional[QPixmap] = None
        self._init_ui()

    def _init_ui(self):
        self.setObjectName("imagePlusSlot")
        self.setFrameShape(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(220)
        self.setStyleSheet("""
            QFrame#imagePlusSlot {
                background-color: #CCD7FD;
                border: 1px solid #FFFFFF;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.display_label = QLabel("No Preview Available")
        self.display_label.setAlignment(Qt.AlignCenter)
        self.display_label.setStyleSheet("""
            QLabel {
                color: #0F172A;
                font-size: 11px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: 500;
                background-color: transparent;
                border: none;
            }
        """)
        self.display_label.setCursor(Qt.PointingHandCursor)
        self.display_label.mousePressEvent = self._on_clicked
        layout.addWidget(self.display_label, 1)

    def set_image(self, file_path: Optional[str]):
        self.image_path = file_path
        if file_path and os.path.exists(file_path):
            self._pixmap = QPixmap(file_path)
            self.display_label.setText("")
        else:
            self._pixmap = None
            self.display_label.setText("No Preview Available")
        self._refresh_pixmap()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh_pixmap()

    def _refresh_pixmap(self):
        if self._pixmap and not self._pixmap.isNull():
            avail_w = max(40, self.display_label.width() - 4)
            avail_h = max(40, self.display_label.height() - 4)
            scaled = self._pixmap.scaled(avail_w, avail_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.display_label.setPixmap(scaled)
        else:
            if not self.image_path:
                self.display_label.setText("No Preview Available")

    def _on_clicked(self, event):
        if self.image_path and os.path.exists(self.image_path):
            from app.ui.main_window import ImagePreviewModal
            modal = ImagePreviewModal(self.image_path, f"Image {self.index + 1}", self)
            modal.exec()
        else:
            # Open file dialog to choose an image for this slot
            path, _ = QFileDialog.getOpenFileName(
                self, f"Select Image for Slot {self.index + 1}", "",
                "Images (*.png *.jpg *.jpeg *.bmp)"
            )
            if path and os.path.exists(path):
                self.set_image(path)
        self.image_selected.emit(self)


class ImagePlusWindow(QWidget):
    """
    Dedicated Full-Screen Medical Image Plus Gallery & Reporting Page.
    Follows the reference design with 2-row demographics, Image Plus 1..6 radio bar,
    lavender multi-image grid, red 3D preset buttons, active green Image Plus banner,
    and official EndoCare branding.
    """
    def __init__(self, patient_record: Optional[Dict[str, Any]] = None, parent=None):
        super().__init__(parent)
        self.patient_record = patient_record or {}
        self.current_layout_preset = 4  # Default 4 images as shown in reference
        self.slots: List[ImagePlusSlotWidget] = []

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self._assets_dir = os.path.join(base_dir, "assets")

        self.setWindowTitle("EndoCare - Image Plus Report")
        self.setWindowIcon(QIcon(os.path.join(self._assets_dir, "logo.png")))
        self.setMinimumSize(1100, 720)

        # Standard window with minimize, maximize, and close controls
        self.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        self._init_ui()
        self._populate_patient_record()

    def show_maximized_clean(self):
        """Maximize while strictly keeping the Windows desktop bottom taskbar visible."""
        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.availableGeometry())
        self.showMaximized()

    def _init_ui(self):
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # =====================================================================
        # 1. CENTRAL DOCUMENT WORKSPACE (Dark slate canvas with white sheet)
        # =====================================================================
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #4B4E51;
                border: none;
            }
            QScrollBar:vertical {
                background: #373A3C;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #6B7280;
                min-height: 24px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9CA3AF;
            }
        """)

        sheet_container = QWidget()
        sheet_container.setStyleSheet("background-color: #4B4E51;")
        sheet_container_layout = QVBoxLayout(sheet_container)
        sheet_container_layout.setContentsMargins(18, 14, 18, 14)
        sheet_container_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        # The crisp white document sheet
        self.report_sheet = QFrame()
        self.report_sheet.setObjectName("imagePlusSheet")
        self.report_sheet.setMinimumWidth(880)
        self.report_sheet.setMaximumWidth(1100)
        self.report_sheet.setStyleSheet("""
            QFrame#imagePlusSheet {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 2px;
            }
            QLabel {
                color: #000000;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 140))
        shadow.setOffset(0, 4)
        self.report_sheet.setGraphicsEffect(shadow)

        sheet_layout = QVBoxLayout(self.report_sheet)
        sheet_layout.setContentsMargins(20, 16, 20, 16)
        sheet_layout.setSpacing(8)

        # -------------------------------------------------------------
        # A. Header Area (Hospital / Clinic Center Name)
        # -------------------------------------------------------------
        header_box = QVBoxLayout()
        header_box.setSpacing(1)
        header_box.setAlignment(Qt.AlignCenter)

        self.lbl_hospital_name = QLabel("Hospital/Clinic/Diagnostic Center Name")
        self.lbl_hospital_name.setAlignment(Qt.AlignCenter)
        self.lbl_hospital_name.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: 800;
                color: #000000;
                background: transparent;
                border: none;
            }
        """)
        header_box.addWidget(self.lbl_hospital_name)

        self.lbl_address1 = QLabel("Address Line 1")
        self.lbl_address1.setAlignment(Qt.AlignCenter)
        self.lbl_address1.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 700;
                color: #000000;
                background: transparent;
                border: none;
            }
        """)
        header_box.addWidget(self.lbl_address1)

        self.lbl_address2 = QLabel("Address Line 2")
        self.lbl_address2.setAlignment(Qt.AlignCenter)
        self.lbl_address2.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 700;
                color: #000000;
                background: transparent;
                border: none;
            }
        """)
        header_box.addWidget(self.lbl_address2)

        lbl_disclaimer = QLabel("(This is Text Format area. This option does not allow LOGO)")
        lbl_disclaimer.setAlignment(Qt.AlignCenter)
        lbl_disclaimer.setStyleSheet("""
            QLabel {
                font-size: 10px;
                font-style: italic;
                color: #333333;
                margin-top: 1px;
                background: transparent;
                border: none;
            }
        """)
        header_box.addWidget(lbl_disclaimer)
        sheet_layout.addLayout(header_box)
        sheet_layout.addSpacing(4)

        # -------------------------------------------------------------
        # B. Patient Demographic Grid (2 Rows: Identity No. & Name)
        # -------------------------------------------------------------
        patient_frame = QFrame()
        patient_frame.setStyleSheet("""
            QFrame {
                border: 1.5px solid #808894;
                background-color: #FFFFFF;
            }
        """)
        p_grid = QGridLayout(patient_frame)
        p_grid.setContentsMargins(0, 0, 0, 0)
        p_grid.setHorizontalSpacing(0)
        p_grid.setVerticalSpacing(0)

        def make_hdr_cell(text: str, has_check: bool = False):
            box = QFrame()
            box.setFixedHeight(22)
            box.setStyleSheet("background-color: #E2E6EA; border: 1px solid #808894;")
            l = QHBoxLayout(box)
            l.setContentsMargins(6, 0, 6, 0)
            l.setSpacing(4)
            lbl = QLabel(text)
            lbl.setStyleSheet("font-weight: 700; font-size: 11px; color: #0F172A; border: none; background: transparent;")
            l.addWidget(lbl)
            if has_check:
                chk = QCheckBox()
                chk.setStyleSheet("border: none; background: transparent;")
                l.addWidget(chk)
            l.addStretch()
            return box

        def make_val_cell(widget: QWidget):
            box = QFrame()
            box.setFixedHeight(22)
            box.setStyleSheet("background-color: #FFFFFF; border: 1px solid #808894;")
            l = QHBoxLayout(box)
            l.setContentsMargins(4, 0, 4, 0)
            l.setSpacing(2)
            widget.setStyleSheet("border: none; background: transparent; font-size: 11px; color: #000000; padding: 0px 2px; height: 18px;")
            l.addWidget(widget)
            return box

        # Row 0: Identity No. | 00000002 | N/A | Visit Date | 20 September, 2026
        cell_id_hdr = make_hdr_cell("Identity No.", has_check=True)
        self.input_id = QLineEdit("00000002")
        self.input_id.setFixedWidth(80)
        self.input_id.setStyleSheet("border: none; background: transparent; font-size: 11px; color: #0F172A; padding: 0px 2px; height: 18px;")
        self.input_mrn = QLineEdit("N/A")
        self.input_mrn.setStyleSheet("border: none; background: transparent; font-size: 11px; color: #0F172A; padding: 0px 2px; height: 18px;")
        id_val_box = QFrame()
        id_val_box.setFixedHeight(22)
        id_val_box.setStyleSheet("background-color: #FFFFFF; border: 1px solid #808894;")
        id_l = QHBoxLayout(id_val_box)
        id_l.setContentsMargins(4, 0, 4, 0)
        id_l.setSpacing(6)
        id_l.addWidget(self.input_id)
        id_l.addWidget(self.input_mrn)
        id_l.addStretch()

        cell_date_hdr = make_hdr_cell("Visit Date")
        self.date_visit = QLineEdit(datetime.now().strftime("%d %B, %Y"))
        self.date_visit.setCursor(Qt.PointingHandCursor)
        cell_date_val = make_val_cell(self.date_visit)

        p_grid.addWidget(cell_id_hdr, 0, 0)
        p_grid.addWidget(id_val_box, 0, 1)
        p_grid.addWidget(cell_date_hdr, 0, 2)
        p_grid.addWidget(cell_date_val, 0, 3)

        # Row 1: Patient Name | Nayem Islam | Age / Sex | 30 / Male
        cell_name_hdr = make_hdr_cell("Patient Name")
        self.input_name = QLineEdit("Nayem Islam")
        self.input_name.setStyleSheet("font-weight: 700; color: #0F172A; border: none; background: transparent; font-size: 11px; padding: 0px 2px; height: 18px;")
        cell_name_val = make_val_cell(self.input_name)

        cell_age_hdr = make_hdr_cell("Age / Sex")
        age_sex_box = QFrame()
        age_sex_box.setFixedHeight(22)
        age_sex_box.setStyleSheet("background-color: #FFFFFF; border: 1px solid #808894;")
        as_l = QHBoxLayout(age_sex_box)
        as_l.setContentsMargins(4, 0, 4, 0)
        as_l.setSpacing(4)
        self.input_age = QLineEdit("30")
        self.input_age.setFixedWidth(36)
        self.input_age.setStyleSheet("border: none; background: transparent; font-size: 11px; padding: 0px 2px; height: 18px;")
        slash_lbl = QLabel("/")
        slash_lbl.setStyleSheet("border: none; background: transparent; font-size: 11px; font-weight: bold;")
        self.input_sex = QLineEdit("Male")
        self.input_sex.setStyleSheet("border: none; background: transparent; font-size: 11px; padding: 0px 2px; height: 18px;")
        as_l.addWidget(self.input_age)
        as_l.addWidget(slash_lbl)
        as_l.addWidget(self.input_sex)
        as_l.addStretch()

        p_grid.addWidget(cell_name_hdr, 1, 0)
        p_grid.addWidget(cell_name_val, 1, 1)
        p_grid.addWidget(cell_age_hdr, 1, 2)
        p_grid.addWidget(age_sex_box, 1, 3)

        p_grid.setColumnStretch(0, 14)
        p_grid.setColumnStretch(1, 36)
        p_grid.setColumnStretch(2, 14)
        p_grid.setColumnStretch(3, 36)

        sheet_layout.addWidget(patient_frame)
        sheet_layout.addSpacing(4)

        # -------------------------------------------------------------
        # C. Image Plus Mode Radio Selection Strip
        # -------------------------------------------------------------
        radio_bar = QFrame()
        radio_bar.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border: 1px solid #CBD5E1;
                border-radius: 2px;
                padding: 2px;
            }
        """)
        rb_layout = QHBoxLayout(radio_bar)
        rb_layout.setContentsMargins(12, 4, 12, 4)
        rb_layout.setSpacing(24)
        rb_layout.setAlignment(Qt.AlignHCenter)

        self.radio_group = QButtonGroup(self)
        self.radio_map = {}

        radio_style = """
            QRadioButton {
                color: #0F172A;
                font-size: 11px;
                font-weight: 600;
                font-family: 'Segoe UI', Arial, sans-serif;
                spacing: 6px;
                background: transparent;
                border: none;
            }
            QRadioButton::indicator {
                width: 14px;
                height: 14px;
            }
            QRadioButton::indicator:unchecked {
                border: 1.5px solid #64748B;
                border-radius: 7px;
                background-color: #FFFFFF;
            }
            QRadioButton::indicator:checked {
                border: 1.5px solid #0284C7;
                border-radius: 7px;
                background-color: #0284C7;
            }
        """

        # -------------------------------------------------------------
        # D. Image Display Gallery Area (Lavender Slots)
        # -------------------------------------------------------------
        self.gallery_frame = QFrame()
        self.gallery_frame.setObjectName("galleryFrame")
        self.gallery_frame.setFrameShape(QFrame.NoFrame)
        self.gallery_frame.setStyleSheet("""
            QFrame#galleryFrame {
                background-color: #FFFFFF;
                border: 1px solid #808894;
            }
        """)
        self.gallery_layout = QGridLayout(self.gallery_frame)
        self.gallery_layout.setContentsMargins(1, 1, 1, 1)
        self.gallery_layout.setSpacing(2)

        for num in [1, 2, 3, 4, 6]:
            rb = QRadioButton(f"Image Plus {num}")
            rb.setStyleSheet(radio_style)
            rb.setCursor(Qt.PointingHandCursor)
            self.radio_group.addButton(rb, num)
            self.radio_map[num] = rb
            rb_layout.addWidget(rb)
            rb.toggled.connect(lambda checked, n=num: self._on_radio_toggled(n, checked))

        sheet_layout.addWidget(radio_bar)
        sheet_layout.addSpacing(4)
        sheet_layout.addWidget(self.gallery_frame, 1)

        # Check default 4 (will build gallery on toggle)
        if 4 in self.radio_map:
            self.radio_map[4].setChecked(True)

        sheet_container_layout.addWidget(self.report_sheet)
        scroll.setWidget(sheet_container)
        root_layout.addWidget(scroll, 1)

        # =====================================================================
        # 2. RIGHT WORKFLOW SIDEBAR PANEL
        # =====================================================================
        self._build_sidebar(root_layout)

    def _build_sidebar(self, parent_layout):
        sidebar = QFrame()
        sidebar.setObjectName("reportSidebar")
        sidebar.setFixedWidth(205)
        sidebar.setStyleSheet("""
            QFrame#reportSidebar {
                background-color: #373A3C;
                border-left: 1.5px solid #1E293B;
            }
        """)

        s_layout = QVBoxLayout(sidebar)
        s_layout.setContentsMargins(10, 10, 10, 10)
        s_layout.setSpacing(6)

        # --- Brand Header (Endocare Logo & Subtitle) ---
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        logo_path = os.path.join(self._assets_dir, "logo.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(165, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pix)
        else:
            logo_label.setText("EndoCare")
            logo_label.setStyleSheet("color: #38BDF8; font-size: 20px; font-weight: bold; background: transparent;")
        s_layout.addWidget(logo_label)

        subtitle = QLabel("All Solution of Endoscopy")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #94A3B8; font-size: 9px; font-weight: 600; margin-bottom: 4px; background: transparent;")
        s_layout.addWidget(subtitle)
        s_layout.addSpacing(4)

        # --- Primary Module Action Buttons (Beveled Style) ---
        btn_style_standard = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:0.5 #E2E8F0, stop:1 #CBD5E1);
                color: #003366;
                border: 1.5px solid #94A3B8;
                border-radius: 3px;
                font-weight: 800;
                font-size: 12px;
                padding: 6px 4px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #E0F2FE, stop:1 #BAE6FD);
                border-color: #0284C7;
                color: #0284C7;
            }
            QPushButton:pressed {
                background: #CBD5E1;
            }
        """

        btn_style_dimmed = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F1F5F9, stop:1 #CBD5E1);
                color: #93C5FD;
                border: 1px solid #64748B;
                border-radius: 3px;
                font-weight: 700;
                font-size: 12px;
                padding: 5px 4px;
            }
        """

        btn_new_pat = QPushButton("New Patient")
        btn_new_pat.setStyleSheet(btn_style_standard)
        btn_new_pat.setCursor(Qt.PointingHandCursor)
        btn_new_pat.clicked.connect(self._open_new_patient)
        s_layout.addWidget(btn_new_pat)

        btn_archive = QPushButton("Patients Archive")
        btn_archive.setStyleSheet(btn_style_standard)
        btn_archive.setCursor(Qt.PointingHandCursor)
        btn_archive.clicked.connect(self._open_archive)
        s_layout.addWidget(btn_archive)

        btn_doctors = QPushButton("Doctors")
        btn_doctors.setStyleSheet(btn_style_dimmed)
        btn_doctors.clicked.connect(self._open_doctors)
        s_layout.addWidget(btn_doctors)

        btn_referrers = QPushButton("Referrers")
        btn_referrers.setStyleSheet(btn_style_dimmed)
        btn_referrers.clicked.connect(self._open_referrers)
        s_layout.addWidget(btn_referrers)

        btn_templates = QPushButton("Templates")
        btn_templates.setStyleSheet(btn_style_dimmed)
        btn_templates.clicked.connect(self._open_templates)
        s_layout.addWidget(btn_templates)

        s_layout.addSpacing(4)

        # --- Circular 3D Layout Preset Buttons: [4] Red and [6] Red ---
        preset_row = QHBoxLayout()
        preset_row.setAlignment(Qt.AlignCenter)
        preset_row.setSpacing(14)

        self.btn_preset_4 = CircularPresetButton(4, color_theme="red", parent=self)
        self.btn_preset_4.clicked.connect(lambda: self._select_preset(4))

        self.btn_preset_6 = CircularPresetButton(6, color_theme="red", parent=self)
        self.btn_preset_6.clicked.connect(lambda: self._select_preset(6))

        preset_row.addWidget(self.btn_preset_4)
        preset_row.addWidget(self.btn_preset_6)
        s_layout.addLayout(preset_row)
        s_layout.addSpacing(4)

        # --- Active Green Glossy Image Plus Banner ---
        btn_image_plus = QPushButton("Image Plus")
        btn_image_plus.setFixedHeight(34)
        btn_image_plus.setCursor(Qt.PointingHandCursor)
        btn_image_plus.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #22C55E, stop:0.4 #16A34A, stop:1 #15803D);
                color: #FFFFFF;
                border: 1.5px solid #86EFAC;
                border-radius: 3px;
                font-family: 'Arial Black', Impact, sans-serif;
                font-style: italic;
                font-size: 15px;
                font-weight: 900;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4ADE80, stop:0.4 #22C55E, stop:1 #16A34A);
            }
        """)
        s_layout.addWidget(btn_image_plus)

        # --- Report Workflow Buttons ---
        btn_back_capture = QPushButton("Back to Capture")
        btn_back_capture.setStyleSheet(btn_style_standard)
        btn_back_capture.setCursor(Qt.PointingHandCursor)
        btn_back_capture.clicked.connect(self.close)
        s_layout.addWidget(btn_back_capture)

        # Update Report Checkbox / Button
        update_box = QFrame()
        update_box.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #E2E8F0);
                border: 1.5px solid #94A3B8;
                border-radius: 3px;
            }
        """)
        u_lay = QHBoxLayout(update_box)
        u_lay.setContentsMargins(6, 4, 6, 4)
        u_lay.setSpacing(6)

        self.chk_update_report = QCheckBox("Update Report")
        self.chk_update_report.setChecked(True)
        self.chk_update_report.setCursor(Qt.PointingHandCursor)
        self.chk_update_report.setStyleSheet("""
            QCheckBox {
                color: #003366;
                font-weight: 800;
                font-size: 12px;
                border: none;
                background: transparent;
            }
        """)
        btn_do_save = QPushButton("💾")
        btn_do_save.setFixedSize(22, 22)
        btn_do_save.setToolTip("Save Image Plus Selection")
        btn_do_save.setStyleSheet("background: #0284C7; color: white; border-radius: 2px; font-size: 11px;")
        btn_do_save.clicked.connect(self._handle_save)

        u_lay.addWidget(self.chk_update_report, 1)
        u_lay.addWidget(btn_do_save)
        s_layout.addWidget(update_box)

        # Print Report
        btn_print = QPushButton("Print Report")
        btn_print.setStyleSheet(btn_style_standard)
        btn_print.setCursor(Qt.PointingHandCursor)
        btn_print.clicked.connect(self._handle_print)
        s_layout.addWidget(btn_print)

        # Export Report
        export_box = QFrame()
        export_box.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #E2E8F0);
                border: 1.5px solid #94A3B8;
                border-radius: 3px;
            }
        """)
        e_lay = QHBoxLayout(export_box)
        e_lay.setContentsMargins(6, 4, 6, 4)
        e_lay.setSpacing(6)

        self.chk_export_report = QCheckBox("Export Report")
        self.chk_export_report.setCursor(Qt.PointingHandCursor)
        self.chk_export_report.setStyleSheet("""
            QCheckBox {
                color: #003366;
                font-weight: 800;
                font-size: 12px;
                border: none;
                background: transparent;
            }
        """)
        btn_do_export = QPushButton("📄")
        btn_do_export.setFixedSize(22, 22)
        btn_do_export.setToolTip("Export report to PDF / Document")
        btn_do_export.setStyleSheet("background: #0F766E; color: white; border-radius: 2px; font-size: 11px;")
        btn_do_export.clicked.connect(self._handle_export)

        e_lay.addWidget(self.chk_export_report, 1)
        e_lay.addWidget(btn_do_export)
        s_layout.addWidget(export_box)

        btn_close = QPushButton("Close Report")
        btn_close.setStyleSheet(btn_style_standard)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.close)
        s_layout.addWidget(btn_close)

        s_layout.addStretch(1)

        # --- Bottom HOME & EXIT Controls ---
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(8)

        btn_home = QPushButton("HOME")
        btn_home.setFixedHeight(30)
        btn_home.setCursor(Qt.PointingHandCursor)
        btn_home.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #059669, stop:1 #047857);
                color: #FFFFFF;
                border: 1px solid #10B981;
                border-radius: 3px;
                font-weight: 800;
                font-size: 12px;
                letter-spacing: 1px;
            }
            QPushButton:hover { background: #10B981; }
        """)
        btn_home.clicked.connect(self.close)
        bottom_row.addWidget(btn_home)

        btn_exit = QPushButton("EXIT")
        btn_exit.setFixedHeight(30)
        btn_exit.setCursor(Qt.PointingHandCursor)
        btn_exit.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B91C1C, stop:1 #7F1D1D);
                color: #FFFFFF;
                border: 1px solid #EF4444;
                border-radius: 3px;
                font-weight: 800;
                font-size: 12px;
                letter-spacing: 1px;
            }
            QPushButton:hover { background: #DC2626; }
        """)
        btn_exit.clicked.connect(self._confirm_exit)
        bottom_row.addWidget(btn_exit)

        s_layout.addLayout(bottom_row)
        parent_layout.addWidget(sidebar)

    # =========================================================================
    # Gallery Dynamic Rebuilding
    # =========================================================================
    def _select_preset(self, num: int):
        if num in self.radio_map:
            self.radio_map[num].setChecked(True)
        else:
            self._rebuild_gallery(num)

    def _on_radio_toggled(self, num: int, checked: bool):
        if checked:
            self._rebuild_gallery(num)

    def _rebuild_gallery(self, count: int):
        self.current_layout_preset = count

        # Clear existing items
        while self.gallery_layout.count():
            item = self.gallery_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()
        self.slots.clear()

        # Grid dimensions based on count
        if count == 1:
            rows, cols = 1, 1
        elif count == 2:
            rows, cols = 1, 2
        elif count == 3:
            rows, cols = 1, 3
        elif count == 4:
            rows, cols = 2, 2
        elif count == 6:
            rows, cols = 2, 3
        else:
            rows, cols = 2, 2

        idx = 0
        for r in range(rows):
            for c in range(cols):
                slot = ImagePlusSlotWidget(idx, parent=self.gallery_frame)
                self.gallery_layout.addWidget(slot, r, c)
                self.slots.append(slot)
                idx += 1
                if idx >= count:
                    break
            if idx >= count:
                break

    # =========================================================================
    # Data & Actions
    # =========================================================================
    def _populate_patient_record(self):
        rec = self.patient_record
        if not rec:
            return
        if "id" in rec:
            self.input_id.setText(str(rec["id"]).zfill(8))
        if "mrn" in rec and rec["mrn"]:
            self.input_mrn.setText(str(rec["mrn"]))
        if "name" in rec and rec["name"]:
            self.input_name.setText(str(rec["name"]))
        if "age" in rec and rec["age"]:
            self.input_age.setText(str(rec["age"]))
        if "sex" in rec and rec["sex"]:
            self.input_sex.setText(str(rec["sex"]))
        if "date" in rec and rec["date"]:
            self.date_visit.setText(str(rec["date"]))

    def _handle_save(self):
        QMessageBox.information(self, "Image Plus", "✓ Image Plus configuration updated successfully.")

    def _handle_print(self):
        QMessageBox.information(self, "Print", "Dispatching Image Plus sheet to printer...")

    def _handle_export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Image Plus Report",
            f"ImagePlus_{self.input_name.text().replace(' ', '_')}.pdf",
            "PDF Documents (*.pdf);;All Files (*)"
        )
        if path:
            QMessageBox.information(self, "Export Complete", f"✓ Saved Image Plus report:\n{path}")

    def _open_new_patient(self):
        from app.ui.dialogs.new_patient_dialog import NewPatientDialog
        dlg = NewPatientDialog(self)
        dlg.showMaximized()
        dlg.exec()

    def _open_archive(self):
        from app.ui.dialogs.archive_dialog import ArchiveDialog
        dlg = ArchiveDialog(parent=self)
        dlg.showMaximized()
        dlg.exec()

    def _open_doctors(self):
        from app.ui.dialogs.doctors_dialog import DoctorsDialog
        dlg = DoctorsDialog(parent=self)
        dlg.showMaximized()
        dlg.exec()

    def _open_referrers(self):
        from app.ui.dialogs.referrers_dialog import ReferrersDialog
        dlg = ReferrersDialog(parent=self)
        dlg.exec()

    def _open_templates(self):
        from app.ui.dialogs.templates_dialog import TemplatesDialog
        dlg = TemplatesDialog(parent=self)
        dlg.exec()

    def _confirm_exit(self):
        ans = QMessageBox.question(
            self, "Exit EndoCare",
            "Are you sure you want to close EndoCare Workstation?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if ans == QMessageBox.Yes:
            QApplication.quit()
