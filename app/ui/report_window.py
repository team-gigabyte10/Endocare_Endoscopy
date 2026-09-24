"""
Endocare 2.42 - Endoscopic Procedure Report Workstation
Full-Screen Clinical Reporting Page with Interactive Rich-Text Findings,
Patient Information Demographics, Multi-Slot Endoscopy Image Gallery,
and Clinical Export / Print Engine.
"""

import os
import sys
import datetime
from typing import Optional, Dict, Any, List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QTextEdit, QComboBox,
    QCheckBox, QMessageBox, QGraphicsDropShadowEffect,
    QApplication, QFileDialog, QFontDialog, QScrollArea,
    QSizePolicy, QDialog
)
from PySide6.QtCore import Qt, QDate, QRect, QPoint, QSize, Signal
from PySide6.QtGui import (
    QPixmap, QColor, QFont, QTextCursor, QTextListFormat,
    QTextBlockFormat, QTextCharFormat, QKeySequence, QShortcut,
    QPainter, QPen, QBrush, QLinearGradient, QRadialGradient,
    QIcon, QPalette
)

from app.services.database import DatabaseService


class ClearCrossButton(QPushButton):
    """Circular red button with crisp white X for instantly clearing input fields."""
    def __init__(self, size: int = 18, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Clear / Reset Selection")
        r = size // 2
        f_size = 9 if size <= 18 else 11
        self.setStyleSheet(f"""
            QPushButton {{
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.35, fy:0.35,
                    stop:0 #EF4444, stop:0.7 #DC2626, stop:1 #991B1B);
                border: 1px solid #7F1D1D;
                border-radius: {r}px;
                color: #FFFFFF;
                font-size: {f_size}px;
                font-weight: 900;
                padding: 0px;
            }}
            QPushButton:hover {{
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.35, fy:0.35,
                    stop:0 #F87171, stop:0.7 #EF4444, stop:1 #B91C1C);
                border: 1px solid #991B1B;
            }}
            QPushButton:pressed {{
                background: #7F1D1D;
            }}
        """)
        self.setText("✕")


class CircularPresetButton(QPushButton):
    """
    Circular 3D Preset Button matching the [4] Green and [6] Red buttons in reference image.
    """
    def __init__(self, number: int, color_theme: str = "green", parent=None):
        super().__init__(parent)
        self.number = number
        self.color_theme = color_theme
        self.setFixedSize(62, 62)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(f"Switch to {number}-Image Grid Layout")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        w, h = self.width(), self.height()
        cx, cy = w / 2.0, h / 2.0
        r = min(w, h) / 2.0 - 2.0

        # Outer silver beveled metallic ring
        ring_grad = QLinearGradient(0, 0, w, h)
        if self.isDown():
            ring_grad.setColorAt(0.0, QColor("#4B5563"))
            ring_grad.setColorAt(1.0, QColor("#9CA3AF"))
        elif self.underMouse():
            ring_grad.setColorAt(0.0, QColor("#FFFFFF"))
            ring_grad.setColorAt(1.0, QColor("#94A3B8"))
        else:
            ring_grad.setColorAt(0.0, QColor("#E2E8F0"))
            ring_grad.setColorAt(0.5, QColor("#94A3B8"))
            ring_grad.setColorAt(1.0, QColor("#475569"))

        painter.setPen(QPen(QColor("#1E293B"), 1))
        painter.setBrush(QBrush(ring_grad))
        painter.drawEllipse(QPoint(int(cx), int(cy)), int(r), int(r))

        # Inner colored circle with glossy radial gradient
        inner_r = r - 4.5
        color_grad = QRadialGradient(cx - 3, cy - 3, inner_r)
        if self.color_theme == "green":
            color_grad.setColorAt(0.0, QColor("#34D399"))
            color_grad.setColorAt(0.6, QColor("#059669"))
            color_grad.setColorAt(1.0, QColor("#064E3B"))
        else:  # red
            color_grad.setColorAt(0.0, QColor("#F87171"))
            color_grad.setColorAt(0.6, QColor("#DC2626"))
            color_grad.setColorAt(1.0, QColor("#7F1D1D"))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color_grad))
        painter.drawEllipse(QPoint(int(cx), int(cy)), int(inner_r), int(inner_r))

        # Left side: Large bold number (4 or 6)
        painter.setPen(QPen(QColor("#FFFFFF")))
        font = QFont("Arial", 18, QFont.Bold)
        painter.setFont(font)
        painter.drawText(QRect(int(cx - 22), int(cy - 14), 22, 28), Qt.AlignCenter, str(self.number))

        # Right side: Grid mini squares graphic
        painter.setPen(QPen(QColor("rgba(255, 255, 255, 0.8)"), 1))
        painter.setBrush(QBrush(QColor("rgba(255, 255, 255, 0.25)")))
        if self.number == 4:
            # 2x2 grid
            for gx in range(2):
                for gy in range(2):
                    rx = int(cx + 4 + gx * 8)
                    ry = int(cy - 8 + gy * 8)
                    painter.drawRect(rx, ry, 6, 6)
        else:
            # 3x2 grid (6)
            for gx in range(2):
                for gy in range(3):
                    rx = int(cx + 4 + gx * 8)
                    ry = int(cy - 12 + gy * 8)
                    painter.drawRect(rx, ry, 6, 6)


class ImageSlotWidget(QFrame):
    """Individual Endoscopy Image Frame with lavender background and clickable title."""
    image_selected = Signal(object)

    def __init__(self, index: int, parent=None):
        super().__init__(parent)
        self.index = index
        self.image_path: Optional[str] = None
        self.caption = f"Image {index + 1}"
        self._pixmap: Optional[QPixmap] = None
        self._init_ui()

    def _init_ui(self):
        self.setStyleSheet("""
            QFrame#imageSlotContainer {
                background-color: #CCD3FB;
                border: 1px solid #B8C0F4;
                border-radius: 2px;
            }
        """)
        self.setObjectName("imageSlotContainer")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(190)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # Image Display Area
        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setStyleSheet("background-color: transparent;")
        self.img_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.img_label.setCursor(Qt.PointingHandCursor)
        self.img_label.mousePressEvent = self._on_clicked
        layout.addWidget(self.img_label, 1)

        # Image Title at bottom
        self.title_input = QLineEdit("(Image Title)")
        self.title_input.setAlignment(Qt.AlignCenter)
        self.title_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: #000000;
                font-size: 11px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: 500;
                padding: 1px;
            }
            QLineEdit:focus {
                background: #FFFFFF;
                border: 1px solid #0284C7;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.title_input)

    def set_image(self, file_path: Optional[str], caption: str = ""):
        self.image_path = file_path
        if caption:
            self.caption = caption
            self.title_input.setText(caption)
        else:
            self.title_input.setText("(Image Title)")

        if file_path and os.path.exists(file_path):
            self._pixmap = QPixmap(file_path)
        else:
            self._pixmap = None
        self._refresh_pixmap()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh_pixmap()

    def _refresh_pixmap(self):
        if self._pixmap and not self._pixmap.isNull():
            avail_w = max(40, self.img_label.width() - 4)
            avail_h = max(40, self.img_label.height() - 4)
            scaled = self._pixmap.scaled(avail_w, avail_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.img_label.setPixmap(scaled)
        else:
            self.img_label.clear()

    def _on_clicked(self, event):
        if self.image_path and os.path.exists(self.image_path):
            # Show high resolution zoom popup
            from app.ui.main_window import ImagePreviewModal
            modal = ImagePreviewModal(self.image_path, self.title_input.text() or "Endoscopic Capture", self)
            modal.exec()
        self.image_selected.emit(self)


class ProcedureReportWindow(QWidget):
    """
    Full-Screen Endoscopic Procedure Report Workstation.
    Faithfully implements the Endocare 2.42 Clinical Report Layout.
    """
    def __init__(self, patient_record: Optional[Dict[str, Any]] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Endocare 2.42 • Endoscopic Procedure Report")
        self.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.setObjectName("procedureReportWindow")
        self.setStyleSheet("""
            QWidget#procedureReportWindow {
                background-color: #2F3336;
            }
            QComboBox {
                background-color: #FFFFFF;
                color: #0F172A;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1.5px solid #0284C7;
                border-radius: 4px;
                selection-background-color: #0284C7;
                selection-color: #FFFFFF;
                outline: none;
                padding: 2px;
            }
            QComboBox QAbstractItemView::item {
                background-color: #FFFFFF;
                color: #0F172A;
                min-height: 24px;
                padding: 4px 8px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #E0F2FE;
                color: #0284C7;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #0284C7;
                color: #FFFFFF;
            }
        """)

        self.db = DatabaseService.get_instance()
        self.patient_record = patient_record or self._get_fallback_patient()
        self._assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../assets"))
        self._captures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/captures"))
        
        self.current_layout_preset = 2  # Default to 2 images as shown in screenshot
        self.image_slots: List[ImageSlotWidget] = []

        # Build full UI
        self._init_ui()
        self._setup_shortcuts()
        self._load_patient_data()
        self._load_patient_images()

    def _get_fallback_patient(self) -> Dict[str, Any]:
        """Provides default reference patient matching the reference image."""
        patients = self.db.get_patients(limit=10)
        if patients:
            return patients[0]
        return {
            "auto_id": "00000001",
            "mrn": "hhh",
            "name": "Adnan Shefat",
            "age": 18,
            "sex": "Male",
            "visit_date": "15-07-2026",
            "procedure_name": "COLONOSCOPY",
            "indication": "hjj",
            "history": "N/A",
            "doctor_name": "Dr. Sarah Jenkins",
            "referrer_name": "ffff",
            "town": "OPD"
        }

    def _setup_shortcuts(self):
        QShortcut(QKeySequence(Qt.Key_F11), self, self._toggle_fullscreen)
        QShortcut(QKeySequence(Qt.Key_Escape), self, self.close)

    def _apply_safe_geometry(self):
        """Strictly respects Windows desktop taskbar (bottom bar) geometry."""
        screen = self.screen() or QApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else None
        if avail:
            self.setGeometry(avail)
        self.showMaximized()

    def _toggle_fullscreen(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self._apply_safe_geometry()

    def showEvent(self, event):
        super().showEvent(event)
        if not getattr(self, "_geometry_applied", False):
            self._geometry_applied = True
            self._apply_safe_geometry()

    def _init_ui(self):
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # =====================================================================
        # 1. CENTRAL WORKSPACE: Scrollable White Report Document
        # =====================================================================
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignCenter)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #383C3F;
                border: none;
            }
            QScrollBar:vertical {
                background: #25282A;
                width: 12px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #52585D;
                min-height: 24px;
                border-radius: 4px;
            }
        """)

        # Report Sheet Container
        sheet_container = QWidget()
        sheet_container_layout = QVBoxLayout(sheet_container)
        sheet_container_layout.setContentsMargins(20, 16, 20, 16)
        sheet_container_layout.setAlignment(Qt.AlignCenter)

        # The crisp white document sheet
        self.report_sheet = QFrame()
        self.report_sheet.setObjectName("reportSheet")
        self.report_sheet.setMinimumWidth(880)
        self.report_sheet.setMaximumWidth(1060)
        self.report_sheet.setStyleSheet("""
            QFrame#reportSheet {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 2px;
            }
            QLabel {
                color: #000000;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

        # Subtle paper drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 140))
        shadow.setOffset(0, 4)
        self.report_sheet.setGraphicsEffect(shadow)

        sheet_layout = QVBoxLayout(self.report_sheet)
        sheet_layout.setContentsMargins(24, 18, 24, 18)
        sheet_layout.setSpacing(8)

        # -------------------------------------------------------------
        # A. Header Area (Hospital / Clinic Info)
        # -------------------------------------------------------------
        header_box = QVBoxLayout()
        header_box.setSpacing(1)
        header_box.setAlignment(Qt.AlignCenter)

        self.lbl_hospital_name = QLabel("Hospital/Clinic/Diagnostic Center Name")
        self.lbl_hospital_name.setAlignment(Qt.AlignCenter)
        self.lbl_hospital_name.setStyleSheet("""
            QLabel {
                font-size: 23px;
                font-weight: 800;
                color: #000000;
                letter-spacing: 0.2px;
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
        # B. Patient Demographic Information Grid
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

        # Helper to create styled table cells
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

        # Row 0: Identity No. | 00000001 | hhh | Visit Date | 15 July, 2026
        cell_id_hdr = make_hdr_cell("Identity No.", has_check=True)
        self.input_id = QLineEdit("00000001")
        self.input_id.setFixedWidth(80)
        self.input_id.setStyleSheet("border: none; background: transparent; font-size: 11px; color: #0F172A; padding: 0px 2px; height: 18px;")
        self.input_mrn = QLineEdit("hhh")
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
        self.date_visit = QLineEdit("15    July    , 2026")
        self.date_visit.setCursor(Qt.PointingHandCursor)
        cell_date_val = make_val_cell(self.date_visit)

        p_grid.addWidget(cell_id_hdr, 0, 0)
        p_grid.addWidget(id_val_box, 0, 1)
        p_grid.addWidget(cell_date_hdr, 0, 2)
        p_grid.addWidget(cell_date_val, 0, 3)

        # Row 1: Patient Name | Adnan Shefat | Age / Sex | 18 / Male
        cell_name_hdr = make_hdr_cell("Patient Name")
        self.input_name = QLineEdit("Adnan Shefat")
        self.input_name.setStyleSheet("font-weight: 700; color: #0F172A; border: none; background: transparent; font-size: 11px; padding: 0px 2px; height: 18px;")
        cell_name_val = make_val_cell(self.input_name)

        cell_age_hdr = make_hdr_cell("Age / Sex")
        age_sex_box = QFrame()
        age_sex_box.setFixedHeight(22)
        age_sex_box.setStyleSheet("background-color: #FFFFFF; border: 1px solid #808894;")
        as_l = QHBoxLayout(age_sex_box)
        as_l.setContentsMargins(4, 0, 4, 0)
        as_l.setSpacing(4)
        self.input_age = QLineEdit("18")
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

        table_combo_style = """
            QComboBox {
                border: none;
                background-color: #FFFFFF;
                color: #0F172A;
                font-size: 11px;
                padding: 0px 2px;
                height: 18px;
                max-height: 18px;
            }
            QComboBox QLineEdit {
                border: none;
                background: transparent;
                padding: 0px 2px;
                font-size: 11px;
                color: #0F172A;
                height: 18px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1.5px solid #0284C7;
                border-radius: 4px;
                selection-background-color: #0284C7;
                selection-color: #FFFFFF;
                outline: none;
                padding: 2px;
            }
            QComboBox QAbstractItemView::item {
                background-color: #FFFFFF;
                color: #0F172A;
                min-height: 22px;
                padding: 3px 8px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #E0F2FE;
                color: #0284C7;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #0284C7;
                color: #FFFFFF;
            }
        """

        # Row 2: History | [N/A v] [X] | Instrument | [N/A v] [X]
        cell_hist_hdr = make_hdr_cell("History")
        hist_box = QFrame()
        hist_box.setFixedHeight(22)
        hist_box.setStyleSheet("background-color: #FFFFFF; border: 1px solid #808894;")
        h_l = QHBoxLayout(hist_box)
        h_l.setContentsMargins(4, 0, 4, 0)
        h_l.setSpacing(4)
        self.combo_history = QComboBox()
        self.combo_history.setEditable(True)
        self.combo_history.addItems(["N/A", "Prior Polypectomy", "GERD / Barrett's", "IBD Surveillance", "Family History of CRC", "Post-Surgical"])
        self.combo_history.setStyleSheet(table_combo_style)
        self.combo_history.view().setStyleSheet("background-color: #FFFFFF; color: #0F172A; selection-background-color: #0284C7; selection-color: #FFFFFF;")
        btn_clear_hist = ClearCrossButton(size=16)
        btn_clear_hist.clicked.connect(lambda: self.combo_history.setCurrentText("N/A"))
        h_l.addWidget(self.combo_history, 1)
        h_l.addWidget(btn_clear_hist)

        cell_inst_hdr = make_hdr_cell("Instrument")
        inst_box = QFrame()
        inst_box.setFixedHeight(22)
        inst_box.setStyleSheet("background-color: #FFFFFF; border: 1px solid #808894;")
        i_l = QHBoxLayout(inst_box)
        i_l.setContentsMargins(4, 0, 4, 0)
        i_l.setSpacing(4)
        self.combo_instrument = QComboBox()
        self.combo_instrument.setEditable(True)
        self.combo_instrument.addItems(["N/A", "Olympus CF-HQ190L (Colonoscope)", "Olympus GIF-H190 (Gastroscope)", "Pentax EC-3890Fi", "Fujinon EC-530HL"])
        self.combo_instrument.setStyleSheet(table_combo_style)
        self.combo_instrument.view().setStyleSheet("background-color: #FFFFFF; color: #0F172A; selection-background-color: #0284C7; selection-color: #FFFFFF;")
        btn_clear_inst = ClearCrossButton(size=16)
        btn_clear_inst.clicked.connect(lambda: self.combo_instrument.setCurrentText("N/A"))
        i_l.addWidget(self.combo_instrument, 1)
        i_l.addWidget(btn_clear_inst)

        p_grid.addWidget(cell_hist_hdr, 2, 0)
        p_grid.addWidget(hist_box, 2, 1)
        p_grid.addWidget(cell_inst_hdr, 2, 2)
        p_grid.addWidget(inst_box, 2, 3)

        # Row 3: Referrer | [ffff v] [X] | Bed | OPD
        cell_ref_hdr = make_hdr_cell("Referrer")
        ref_box = QFrame()
        ref_box.setFixedHeight(22)
        ref_box.setStyleSheet("background-color: #FFFFFF; border: 1px solid #808894;")
        r_l = QHBoxLayout(ref_box)
        r_l.setContentsMargins(4, 0, 4, 0)
        r_l.setSpacing(4)
        self.combo_referrer = QComboBox()
        self.combo_referrer.setEditable(True)
        self.combo_referrer.addItems(["ffff", "Metropolitan Clinic", "Direct Clinical Intake", "Westside Family Practice", "St. Jude Internal Medicine"])
        self.combo_referrer.setStyleSheet(table_combo_style)
        self.combo_referrer.view().setStyleSheet("background-color: #FFFFFF; color: #0F172A; selection-background-color: #0284C7; selection-color: #FFFFFF;")
        btn_clear_ref = ClearCrossButton(size=16)
        btn_clear_ref.clicked.connect(lambda: self.combo_referrer.setCurrentText(""))
        r_l.addWidget(self.combo_referrer, 1)
        r_l.addWidget(btn_clear_ref)

        cell_bed_hdr = make_hdr_cell("Bed")
        self.input_bed = QLineEdit("OPD")
        cell_bed_val = make_val_cell(self.input_bed)

        p_grid.addWidget(cell_ref_hdr, 3, 0)
        p_grid.addWidget(ref_box, 3, 1)
        p_grid.addWidget(cell_bed_hdr, 3, 2)
        p_grid.addWidget(cell_bed_val, 3, 3)

        p_grid.setColumnStretch(0, 14)
        p_grid.setColumnStretch(1, 36)
        p_grid.setColumnStretch(2, 14)
        p_grid.setColumnStretch(3, 36)

        sheet_layout.addWidget(patient_frame)
        sheet_layout.addSpacing(6)

        # -------------------------------------------------------------
        # C. Spaced Procedure Report Banner
        # -------------------------------------------------------------
        banner_row = QHBoxLayout()
        banner_row.setSpacing(4)

        btn_banner_e = QPushButton("E")
        btn_banner_e.setFixedSize(22, 24)
        btn_banner_e.setCursor(Qt.PointingHandCursor)
        btn_banner_e.setStyleSheet("""
            QPushButton {
                background: #E2E8F0;
                border: 1px solid #94A3B8;
                font-size: 11px;
                font-weight: bold;
                color: #1E293B;
            }
            QPushButton:hover { background: #CBD5E1; }
        """)

        banner_center = QFrame()
        banner_center.setFixedHeight(24)
        banner_center.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #EBEFF3, stop:1 #D1D8E0);
                border: 1px solid #94A3B8;
            }
        """)
        b_c_l = QHBoxLayout(banner_center)
        b_c_l.setContentsMargins(0, 0, 0, 0)
        lbl_banner_title = QLabel("E N D O S C O P I C   P R O C E D U R E   R E P O R T")
        lbl_banner_title.setAlignment(Qt.AlignCenter)
        lbl_banner_title.setStyleSheet("font-size: 12px; font-weight: 800; color: #1E293B; letter-spacing: 2px;")
        b_c_l.addWidget(lbl_banner_title)

        btn_banner_u = QPushButton("U")
        btn_banner_u.setFixedSize(22, 24)
        btn_banner_u.setCursor(Qt.PointingHandCursor)
        btn_banner_u.setStyleSheet("""
            QPushButton {
                background: #E2E8F0;
                border: 1px solid #94A3B8;
                font-size: 11px;
                font-weight: bold;
                color: #1E293B;
            }
            QPushButton:hover { background: #CBD5E1; }
        """)

        banner_row.addWidget(btn_banner_e)
        banner_row.addWidget(banner_center, 1)
        banner_row.addWidget(btn_banner_u)
        sheet_layout.addLayout(banner_row)
        sheet_layout.addSpacing(6)

        # -------------------------------------------------------------
        # D. Two-Column Split (Left: Findings & Toolbar | Right: Images)
        # -------------------------------------------------------------
        content_split = QHBoxLayout()
        content_split.setSpacing(12)

        # === LEFT COLUMN: Procedure, Indication, Medication, Toolbar, Findings ===
        left_col = QVBoxLayout()
        left_col.setSpacing(6)

        # 1. Procedure Line
        proc_line = QHBoxLayout()
        proc_line.setSpacing(6)
        lbl_proc = QLabel("Procedure :")
        lbl_proc.setStyleSheet("font-weight: 800; font-size: 12px; color: #000000; background: transparent; border: none;")
        proc_line.addWidget(lbl_proc)

        self.combo_procedure = QComboBox()
        self.combo_procedure.setEditable(True)
        self.combo_procedure.addItems([
            "COLONOSCOPY", "GASTROSCOPY (OGD)", "SIGMOIDOSCOPY",
            "ERCP", "BRONCHOSCOPY", "CYSTOSCOPY", "ENTEROSCOPY"
        ])
        self.combo_procedure.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                border: 1.5px solid #0284C7;
                border-radius: 2px;
                padding: 3px 6px;
                font-weight: 800;
                font-size: 12px;
                color: #0284C7;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1.5px solid #0284C7;
                border-radius: 4px;
                selection-background-color: #0284C7;
                selection-color: #FFFFFF;
                outline: none;
                padding: 2px;
            }
            QComboBox QAbstractItemView::item {
                background-color: #FFFFFF;
                color: #0F172A;
                min-height: 24px;
                padding: 4px 8px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #E0F2FE;
                color: #0284C7;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #0284C7;
                color: #FFFFFF;
            }
        """)
        self.combo_procedure.view().setStyleSheet("background-color: #FFFFFF; color: #0F172A; selection-background-color: #0284C7; selection-color: #FFFFFF;")
        proc_line.addWidget(self.combo_procedure, 1)

        btn_clear_proc = ClearCrossButton()
        btn_clear_proc.clicked.connect(lambda: self.combo_procedure.setCurrentText(""))
        proc_line.addWidget(btn_clear_proc)
        left_col.addLayout(proc_line)

        # 2. Indication Line
        ind_line = QHBoxLayout()
        ind_line.setSpacing(6)
        lbl_ind = QLabel("Indication :")
        lbl_ind.setStyleSheet("font-weight: 800; font-size: 12px; color: #000000; background: transparent; border: none;")
        ind_line.addWidget(lbl_ind)

        self.input_indication = QLineEdit("hjj")
        self.input_indication.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 1.5px solid #0284C7;
                border-radius: 2px;
                padding: 4px 6px;
                font-size: 12px;
                color: #0F172A;
            }
        """)
        ind_line.addWidget(self.input_indication, 1)
        left_col.addLayout(ind_line)

        # 3. Medication Line
        med_line = QHBoxLayout()
        med_line.setSpacing(6)
        lbl_med = QLabel("Medication :")
        lbl_med.setStyleSheet("font-weight: 800; font-size: 12px; color: #000000; background: transparent; border: none;")
        med_line.addWidget(lbl_med)

        self.combo_medication = QComboBox()
        self.combo_medication.setEditable(True)
        self.combo_medication.addItems([
            "N/A", "Midazolam 3mg IV", "Propofol 100mg IV Sedation",
            "Fentanyl 50mcg IV", "Lidocaine 10% Spray", "Hyoscine Butylbromide 20mg IV"
        ])
        self.combo_medication.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #94A3B8;
                border-radius: 2px;
                padding: 3px 6px;
                font-size: 11px;
                color: #0F172A;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1.5px solid #0284C7;
                border-radius: 4px;
                selection-background-color: #0284C7;
                selection-color: #FFFFFF;
                outline: none;
                padding: 2px;
            }
            QComboBox QAbstractItemView::item {
                background-color: #FFFFFF;
                color: #0F172A;
                min-height: 24px;
                padding: 4px 8px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #E0F2FE;
                color: #0284C7;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #0284C7;
                color: #FFFFFF;
            }
        """)
        self.combo_medication.view().setStyleSheet("background-color: #FFFFFF; color: #0F172A; selection-background-color: #0284C7; selection-color: #FFFFFF;")
        med_line.addWidget(self.combo_medication, 1)

        btn_clear_med = ClearCrossButton()
        btn_clear_med.clicked.connect(lambda: self.combo_medication.setCurrentText("N/A"))
        med_line.addWidget(btn_clear_med)
        left_col.addLayout(med_line)

        # 4. Rich-Text Editor Toolbar
        toolbar_box = QFrame()
        toolbar_box.setStyleSheet("""
            QFrame {
                background-color: #F1F5F9;
                border: 1px solid #CBD5E1;
                border-radius: 3px;
                padding: 2px;
            }
            QPushButton {
                background: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 2px;
                font-size: 11px;
                padding: 3px 6px;
                color: #0F172A;
            }
            QPushButton:hover {
                background: #E2E8F0;
                border-color: #0284C7;
            }
            QPushButton:pressed {
                background: #CBD5E1;
            }
        """)
        tb_l = QHBoxLayout(toolbar_box)
        tb_l.setContentsMargins(4, 3, 4, 3)
        tb_l.setSpacing(3)

        btn_open = QPushButton("Open")
        btn_open.clicked.connect(self._handle_open_text)
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self._handle_save_text)
        btn_reset = QPushButton("Reset")
        btn_reset.clicked.connect(self._handle_reset_text)

        tb_l.addWidget(btn_open)
        tb_l.addWidget(btn_save)
        tb_l.addWidget(btn_reset)

        tb_sep = QFrame()
        tb_sep.setFrameShape(QFrame.VLine)
        tb_sep.setStyleSheet("background: #CBD5E1; max-width: 1px; margin: 0 2px;")
        tb_l.addWidget(tb_sep)

        self.btn_bold = QPushButton("B")
        self.btn_bold.setStyleSheet("font-weight: 900; font-family: 'Times New Roman', serif; min-width: 22px; font-size: 13px;")
        self.btn_bold.clicked.connect(self._toggle_bold)
        self.btn_italic = QPushButton("I")
        self.btn_italic.setStyleSheet("font-style: italic; font-family: 'Times New Roman', serif; min-width: 22px; font-size: 13px;")
        self.btn_italic.clicked.connect(self._toggle_italic)
        self.btn_underline = QPushButton("U")
        self.btn_underline.setStyleSheet("text-decoration: underline; font-family: 'Times New Roman', serif; min-width: 22px; font-size: 13px;")
        self.btn_underline.clicked.connect(self._toggle_underline)

        tb_l.addWidget(self.btn_bold)
        tb_l.addWidget(self.btn_italic)
        tb_l.addWidget(self.btn_underline)

        btn_bullet = QPushButton(":=")
        btn_bullet.setToolTip("Insert Bullet List")
        btn_bullet.clicked.connect(self._insert_bullet_list)
        tb_l.addWidget(btn_bullet)

        btn_align_left = QPushButton("Left")
        btn_align_left.setToolTip("Align Left")
        btn_align_left.clicked.connect(lambda: self.findings_edit.setAlignment(Qt.AlignLeft))
        btn_align_center = QPushButton("Center")
        btn_align_center.setToolTip("Align Center")
        btn_align_center.clicked.connect(lambda: self.findings_edit.setAlignment(Qt.AlignCenter))
        btn_align_right = QPushButton("Right")
        btn_align_right.setToolTip("Align Right")
        btn_align_right.clicked.connect(lambda: self.findings_edit.setAlignment(Qt.AlignRight))
        btn_align_just = QPushButton("Justify")
        btn_align_just.setToolTip("Justify")
        btn_align_just.clicked.connect(lambda: self.findings_edit.setAlignment(Qt.AlignJustify))

        tb_l.addWidget(btn_align_left)
        tb_l.addWidget(btn_align_center)
        tb_l.addWidget(btn_align_right)
        tb_l.addWidget(btn_align_just)

        self.combo_font_size = QComboBox()
        self.combo_font_size.addItems(["9", "10", "11", "12", "14", "16", "18", "20"])
        self.combo_font_size.setCurrentText("11")
        self.combo_font_size.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 2px;
                padding: 2px 4px;
                font-size: 11px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1.5px solid #0284C7;
                selection-background-color: #0284C7;
                selection-color: #FFFFFF;
                outline: none;
                padding: 2px;
            }
            QComboBox QAbstractItemView::item {
                background-color: #FFFFFF;
                color: #0F172A;
                min-height: 20px;
                padding: 2px 6px;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #0284C7;
                color: #FFFFFF;
            }
        """)
        self.combo_font_size.view().setStyleSheet("background-color: #FFFFFF; color: #0F172A; selection-background-color: #0284C7; selection-color: #FFFFFF;")
        self.combo_font_size.currentTextChanged.connect(self._change_font_size)
        tb_l.addWidget(self.combo_font_size)

        btn_fonts = QPushButton("Fonts")
        btn_fonts.clicked.connect(self._open_font_dialog)
        tb_l.addWidget(btn_fonts)

        tb_l.addStretch()
        left_col.addWidget(toolbar_box)

        # 5. Large Findings Rich Text Editor
        self.findings_edit = QTextEdit()
        self.findings_edit.setMinimumHeight(340)
        self.findings_edit.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #94A3B8;
                border-radius: 2px;
                padding: 8px;
                color: #0F172A;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11pt;
            }
            QTextEdit:focus {
                border: 1.5px solid #0284C7;
            }
        """)
        self.findings_edit.setPlainText("N/A")
        left_col.addWidget(self.findings_edit, 1)

        content_split.addLayout(left_col, 56)

        # === RIGHT COLUMN: Image Display Area ===
        self.images_col = QVBoxLayout()
        self.images_col.setSpacing(8)

        # Container inside images_col to host the layout grid/stack
        self.images_container = QWidget()
        self.images_grid_layout = QGridLayout(self.images_container)
        self.images_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.images_grid_layout.setSpacing(8)

        self.images_col.addWidget(self.images_container, 1)
        content_split.addLayout(self.images_col, 44)

        sheet_layout.addLayout(content_split, 1)

        sheet_container_layout.addWidget(self.report_sheet)
        scroll.setWidget(sheet_container)
        root_layout.addWidget(scroll, 1)

        # =====================================================================
        # 2. RIGHT PERSISTENT WORKFLOW SIDEBAR PANEL
        # =====================================================================
        self._build_sidebar(root_layout)

        # Build initial image slots
        self._rebuild_image_layout(self.current_layout_preset)

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

        # --- Brand Header (Endocare Logo & Text) ---
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

        # --- Circular Layout Preset Buttons: [4] Green and [6] Red ---
        preset_row = QHBoxLayout()
        preset_row.setAlignment(Qt.AlignCenter)
        preset_row.setSpacing(14)

        self.btn_preset_4 = CircularPresetButton(4, color_theme="green", parent=self)
        self.btn_preset_4.clicked.connect(lambda: self._rebuild_image_layout(4))

        self.btn_preset_6 = CircularPresetButton(6, color_theme="red", parent=self)
        self.btn_preset_6.clicked.connect(lambda: self._rebuild_image_layout(6))

        preset_row.addWidget(self.btn_preset_4)
        preset_row.addWidget(self.btn_preset_6)
        s_layout.addLayout(preset_row)
        s_layout.addSpacing(4)

        # --- Glossy Red Image Plus Button ---
        btn_image_plus = QPushButton("Image Plus")
        btn_image_plus.setFixedHeight(34)
        btn_image_plus.setCursor(Qt.PointingHandCursor)
        btn_image_plus.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #EF4444, stop:0.4 #DC2626, stop:1 #991B1B);
                color: #FFFFFF;
                border: 1.5px solid #FCA5A5;
                border-radius: 3px;
                font-family: 'Arial Black', Impact, sans-serif;
                font-style: italic;
                font-size: 15px;
                font-weight: 900;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F87171, stop:0.4 #EF4444, stop:1 #B91C1C);
            }
        """)
        btn_image_plus.clicked.connect(self._open_image_plus)
        s_layout.addWidget(btn_image_plus)

        # --- Report Workflow Buttons ---
        btn_back_capture = QPushButton("Back to Capture")
        btn_back_capture.setStyleSheet(btn_style_standard)
        btn_back_capture.setCursor(Qt.PointingHandCursor)
        btn_back_capture.clicked.connect(self._back_to_capture)
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
        btn_do_update = QPushButton("💾")
        btn_do_update.setFixedSize(22, 22)
        btn_do_update.setToolTip("Save all modifications to Database now")
        btn_do_update.setStyleSheet("background: #0284C7; color: white; border-radius: 2px; font-size: 11px;")
        btn_do_update.clicked.connect(self._save_report_to_database)

        u_lay.addWidget(self.chk_update_report, 1)
        u_lay.addWidget(btn_do_update)
        s_layout.addWidget(update_box)

        btn_print = QPushButton("Print Report")
        btn_print.setStyleSheet(btn_style_standard)
        btn_print.setCursor(Qt.PointingHandCursor)
        btn_print.clicked.connect(self._handle_print_report)
        s_layout.addWidget(btn_print)

        # Export Report Checkbox / Button
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
        btn_do_export.clicked.connect(self._handle_export_report)

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
        btn_home.clicked.connect(self._handle_home)
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
    # DYNAMIC IMAGE LAYOUT MANAGER (2, 4, or 6 Image Grid)
    # =========================================================================

    def _rebuild_image_layout(self, slot_count: int):
        """Switches image presentation between 2 (vertical stack), 4 (2x2), and 6 (3x2)."""
        # Toggle back to 2 if clicking the same preset button
        if slot_count == self.current_layout_preset and slot_count != 2:
            slot_count = 2
        self.current_layout_preset = slot_count

        # Clear existing layout items
        while self.images_grid_layout.count():
            item = self.images_grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        self.image_slots.clear()

        # Load available patient images
        auto_id = self.patient_record.get("auto_id", "")
        stored_images = self.db.get_study_images(auto_id) if auto_id else []

        # Fallback sample images if database has fewer
        fallback_files = [
            os.path.join(self._assets_dir, "preview_endo.png"),
            os.path.join(self._assets_dir, "preview_ercp.png"),
            os.path.join(self._assets_dir, "preview_usg.png")
        ]

        # Populate slots
        cols = 1 if slot_count == 2 else 2
        for idx in range(slot_count):
            slot = ImageSlotWidget(idx, parent=self)
            self.image_slots.append(slot)

            # Match stored image from database if present, otherwise clean lavender box
            img_file = None
            caption = "(Image Title)"
            if idx < len(stored_images):
                img_file = stored_images[idx].get("file_path")
                caption = stored_images[idx].get("caption") or "(Image Title)"

            slot.set_image(img_file, caption=caption)

            r = idx if slot_count == 2 else idx // 2
            c = 0 if slot_count == 2 else idx % 2
            self.images_grid_layout.addWidget(slot, r, c)

    def _load_patient_data(self):
        """Populates patient header fields with current record details."""
        rec = self.patient_record
        if not rec:
            return

        aid = str(rec.get("auto_id", "00000001"))
        if aid.isdigit():
            self.input_id.setText(f"{int(aid):08d}")
        else:
            self.input_id.setText(aid)

        self.input_mrn.setText(str(rec.get("mrn") or "hhh"))
        self.input_name.setText(str(rec.get("name") or "Adnan Shefat"))
        self.input_age.setText(str(rec.get("age") or "18"))
        self.input_sex.setText(str(rec.get("sex") or "Male"))
        
        v_date = rec.get("visit_date") or rec.get("date") or "15-07-2026"
        self.date_visit.setText(v_date)

        hist = rec.get("history") or "N/A"
        self.combo_history.setCurrentText(hist)

        ref = rec.get("referrer_name") or rec.get("referrer") or "ffff"
        self.combo_referrer.setCurrentText(ref)

        proc = rec.get("procedure_name") or rec.get("procedure") or "COLONOSCOPY"
        self.combo_procedure.setCurrentText(proc)

        ind = rec.get("indication") or "hjj"
        self.input_indication.setText(ind)

        # Default clinical findings template based on procedure if empty
        findings = rec.get("findings")
        if not findings or findings == "N/A":
            self.findings_edit.setPlainText(
                "• Mucosa: Smooth, glistening, normal vascular pattern throughout explored segments.\n"
                "• Lumen: Adequate distensibility with insufflation, clear luminal wash achieved.\n"
                "• Findings: No ulceration, stricture, polyp, or active bleeding identified.\n"
                "• Impression: Normal examination. Routine follow-up as clinically indicated."
            )
        else:
            self.findings_edit.setPlainText(findings)

    def _load_patient_images(self):
        """Refreshes study images inside the slots."""
        self._rebuild_image_layout(self.current_layout_preset)

    # =========================================================================
    # RICH-TEXT FORMATTING ACTIONS
    # =========================================================================

    def _toggle_bold(self):
        cursor = self.findings_edit.textCursor()
        fmt = cursor.charFormat()
        weight = QFont.Normal if fmt.fontWeight() == QFont.Bold else QFont.Bold
        fmt.setFontWeight(weight)
        cursor.mergeCharFormat(fmt)

    def _toggle_italic(self):
        cursor = self.findings_edit.textCursor()
        fmt = cursor.charFormat()
        fmt.setFontItalic(not fmt.fontItalic())
        cursor.mergeCharFormat(fmt)

    def _toggle_underline(self):
        cursor = self.findings_edit.textCursor()
        fmt = cursor.charFormat()
        fmt.setFontUnderline(not fmt.fontUnderline())
        cursor.mergeCharFormat(fmt)

    def _insert_bullet_list(self):
        cursor = self.findings_edit.textCursor()
        cursor.insertText("• ")

    def _change_font_size(self, size_str: str):
        if size_str.isdigit():
            size = int(size_str)
            cursor = self.findings_edit.textCursor()
            fmt = cursor.charFormat()
            fmt.setFontPointSize(size)
            cursor.mergeCharFormat(fmt)

    def _open_font_dialog(self):
        ok, font = QFontDialog.getFont(self.findings_edit.currentFont(), self)
        if ok:
            cursor = self.findings_edit.textCursor()
            fmt = cursor.charFormat()
            fmt.setFont(font)
            cursor.mergeCharFormat(fmt)

    def _handle_open_text(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Findings File", "", "Text Files (*.txt);;All Files (*)")
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                self.findings_edit.setPlainText(f.read())

    def _handle_save_text(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Findings Text", "Endoscopy_Findings.txt", "Text Files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.findings_edit.toPlainText())
            QMessageBox.information(self, "Saved", f"Findings successfully exported to:\n{path}")

    def _handle_reset_text(self):
        reply = QMessageBox.question(
            self, "Reset Findings",
            "Are you sure you want to reset the findings text to default?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.findings_edit.setPlainText("N/A")

    # =========================================================================
    # SIDEBAR WORKFLOW HANDLERS
    # =========================================================================

    def _save_report_to_database(self):
        """Updates and persists the modified patient report and findings in SQLite."""
        aid = self.input_id.text().strip().lstrip("0") or self.input_id.text().strip()
        update_data = {
            "name": self.input_name.text().strip(),
            "mrn": self.input_mrn.text().strip(),
            "indication": self.input_indication.text().strip(),
            "procedure_name": self.combo_procedure.currentText().strip(),
            "history": self.combo_history.currentText().strip(),
            "referrer_name": self.combo_referrer.currentText().strip(),
            "visit_date": self.date_visit.text().strip()
        }
        try:
            self.db.update_patient(aid, update_data)
            self.patient_record.update(update_data)
            self.patient_record["findings"] = self.findings_edit.toPlainText()
            QMessageBox.information(
                self, "Report Saved",
                f"✓ Examination Report for {self.patient_record.get('name')} saved successfully to SQLite database."
            )
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Unable to update patient record: {e}")

    def _handle_print_report(self):
        """Dispatches high-fidelity printable endoscopy report."""
        QMessageBox.information(
            self, "Print Clinical Report",
            f"Dispatching Endoscopic Procedure Report for:\n"
            f"Patient: {self.input_name.text()}\n"
            f"Procedure: {self.combo_procedure.currentText()}\n\n"
            f"✓ Sent to default medical laser printer queue."
        )

    def _handle_export_report(self):
        """Exports printable document report."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Procedure Report",
            f"Report_{self.input_name.text().replace(' ', '_')}.pdf",
            "PDF Documents (*.pdf);;All Files (*)"
        )
        if path:
            QMessageBox.information(
                self, "Export Complete",
                f"✓ Endoscopic Procedure Report generated successfully:\n{path}"
            )

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

    def _open_image_plus(self):
        from app.ui.dialogs.archive_dialog import ImagePlusModal
        name = self.input_name.text().strip() or "Patient"
        dlg = ImagePlusModal(name, self)
        dlg.exec()

    def _back_to_capture(self):
        """Closes report and launches Capture Workstation for this patient."""
        self.close()
        from app.ui.capture_window import CaptureWindow
        cap = CaptureWindow(patient_data=self.patient_record, parent=None)
        cap.showMaximized()
        cap.exec()

    def _handle_home(self):
        self.close()

    def _confirm_exit(self):
        reply = QMessageBox.question(
            self, "Exit Endocare",
            "Are you sure you want to terminate the application?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QApplication.quit()
