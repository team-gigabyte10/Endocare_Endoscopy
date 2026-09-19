"""
Endocare - Patient Added Success Dialog
Modal confirmation dialog shown after a new patient is registered,
featuring patient details and 3 clinical workflow actions:
1. [ Add New ] - Clear form and register another patient
2. [ Capture ] - Proceed immediately to endoscopy image capture
3. [ Stand by ] - Queue patient on standby and return to launcher
"""

from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont


class PatientAddedSuccessDialog(QDialog):
    """Clinical success modal presenting registration summary and 3 workflow paths."""
    
    ACTION_ADD_NEW = "add_new"
    ACTION_CAPTURE = "capture"
    ACTION_STANDBY = "standby"
    
    def __init__(self, patient_data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Patient Intake Confirmation • Endocare")
        self.setFixedSize(580, 350)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        self.patient_data = patient_data
        self.selected_action = self.ACTION_ADD_NEW
        
        self._init_ui()

    def _init_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(10, 10, 10, 10)
        
        container = QFrame(self)
        container.setObjectName("successDialogContainer")
        container.setStyleSheet("""
            QFrame#successDialogContainer {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0F1D2C, stop:0.6 #09131D, stop:1 #050B11);
                border: 2px solid #10B981;
                border-radius: 12px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setColor(QColor(0, 0, 0, 220))
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)
        
        # --- Top Header: Checkmark Icon & Title ---
        header_row = QHBoxLayout()
        header_row.setSpacing(14)
        
        badge = QLabel("✓")
        badge.setFixedSize(44, 44)
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet("""
            background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 #10B981, stop:1 #047857);
            color: #FFFFFF;
            font-size: 22px;
            font-weight: 900;
            border-radius: 22px;
            border: 2px solid #34D399;
        """)
        header_row.addWidget(badge)
        
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        
        title = QLabel("Patient Registered Successfully")
        title.setStyleSheet("color: #F8FAFC; font-size: 17px; font-weight: 800; letter-spacing: 0.5px;")
        title_col.addWidget(title)
        
        subtitle = QLabel("Clinical intake profile saved to active endoscopy database.")
        subtitle.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 500;")
        title_col.addWidget(subtitle)
        
        header_row.addLayout(title_col)
        header_row.addStretch()
        layout.addLayout(header_row)
        
        # Subtle divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background: #1E293B; max-height: 1px;")
        layout.addWidget(divider)
        
        # Patient Field Values
        name = self.patient_data.get("name", "N/A")
        mrn = self.patient_data.get("mrn", "N/A")
        proc = self.patient_data.get("procedure", "COLONOSCOPY")
        doc = self.patient_data.get("doctor", "N/A")
        age = self.patient_data.get("age", "")
        gender = self.patient_data.get("gender", "")
        age_gender = f"{gender}, {age} yrs" if age else gender

        # --- Patient Details Summary Box ---
        summary_card = QFrame()
        summary_card.setObjectName("successSummaryCard")
        summary_card.setStyleSheet("""
            QFrame#successSummaryCard {
                background-color: #0A141F;
                border: 1.5px solid #1E2E40;
                border-radius: 8px;
                padding: 12px 18px;
            }
            QLabel {
                border: none;
                background: transparent;
            }
        """)
        
        sum_layout = QHBoxLayout(summary_card)
        sum_layout.setContentsMargins(14, 10, 14, 10)
        sum_layout.setSpacing(24)
        
        # Left Column
        left_col = QGridLayout()
        left_col.setHorizontalSpacing(10)
        left_col.setVerticalSpacing(8)
        
        left_col.addWidget(self._make_field_label("Patient:"), 0, 0)
        lbl_name = QLabel(name)
        lbl_name.setStyleSheet("color: #38BDF8; font-size: 14px; font-weight: 800; border: none; background: transparent;")
        left_col.addWidget(lbl_name, 0, 1)
        
        left_col.addWidget(self._make_field_label("MRN ID:"), 1, 0)
        lbl_mrn = QLabel(mrn)
        lbl_mrn.setStyleSheet("color: #E2E8F0; font-size: 12px; font-weight: 700; border: none; background: transparent;")
        left_col.addWidget(lbl_mrn, 1, 1)
        
        left_col.addWidget(self._make_field_label("Age / Sex:"), 2, 0)
        lbl_as = QLabel(age_gender)
        lbl_as.setStyleSheet("color: #CBD5E1; font-size: 12px; font-weight: 600; border: none; background: transparent;")
        left_col.addWidget(lbl_as, 2, 1)
        
        sum_layout.addLayout(left_col, 5)
        
        # Vertical Separator
        v_sep = QFrame()
        v_sep.setFrameShape(QFrame.VLine)
        v_sep.setStyleSheet("background-color: #1E2E40; max-width: 1px;")
        sum_layout.addWidget(v_sep)
        
        # Right Column
        right_col = QGridLayout()
        right_col.setHorizontalSpacing(10)
        right_col.setVerticalSpacing(8)
        
        right_col.addWidget(self._make_field_label("Procedure:"), 0, 0)
        lbl_proc = QLabel(proc)
        lbl_proc.setStyleSheet("color: #F8FAFC; font-size: 13px; font-weight: 800; border: none; background: transparent;")
        right_col.addWidget(lbl_proc, 0, 1)
        
        right_col.addWidget(self._make_field_label("Attending:"), 1, 0)
        lbl_doc = QLabel(doc)
        lbl_doc.setStyleSheet("color: #CBD5E1; font-size: 12px; font-weight: 600; border: none; background: transparent;")
        right_col.addWidget(lbl_doc, 1, 1)
        
        right_col.addWidget(self._make_field_label("Status:"), 2, 0)
        lbl_status = QLabel("● Ready for Study")
        lbl_status.setStyleSheet("color: #10B981; font-size: 12px; font-weight: 800; border: none; background: transparent;")
        right_col.addWidget(lbl_status, 2, 1)
        
        sum_layout.addLayout(right_col, 5)
        
        layout.addWidget(summary_card)
        layout.addStretch(1)
        
        # --- Bottom 3 Clinical Action Buttons ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        # 1. [ Add New ]
        btn_add_new = QPushButton("Add New")
        btn_add_new.setCursor(Qt.PointingHandCursor)
        btn_add_new.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1E293B, stop:1 #0F172A);
                color: #38BDF8;
                border: 1.5px solid #0284C7;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 800;
                padding: 10px 18px;
            }
            QPushButton:hover {
                background: #0284C7;
                color: #FFFFFF;
                border-color: #38BDF8;
            }
        """)
        btn_add_new.clicked.connect(lambda: self._choose_action(self.ACTION_ADD_NEW))
        btn_layout.addWidget(btn_add_new)
        
        # 2. [ Capture ] (Primary glowing green)
        btn_capture = QPushButton("Capture")
        btn_capture.setCursor(Qt.PointingHandCursor)
        btn_capture.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #10B981, stop:1 #047857);
                color: #FFFFFF;
                border: 1.5px solid #34D399;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 900;
                letter-spacing: 0.5px;
                padding: 10px 22px;
            }
            QPushButton:hover {
                background: #059669;
                border-color: #6EE7B7;
            }
        """)
        btn_capture.clicked.connect(lambda: self._choose_action(self.ACTION_CAPTURE))
        btn_layout.addWidget(btn_capture)
        
        # 3. [ Stand by ]
        btn_standby = QPushButton("Stand by")
        btn_standby.setCursor(Qt.PointingHandCursor)
        btn_standby.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1E293B, stop:1 #0F172A);
                color: #FBBF24;
                border: 1.5px solid #D97706;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 800;
                padding: 10px 18px;
            }
            QPushButton:hover {
                background: #D97706;
                color: #FFFFFF;
                border-color: #FCD34D;
            }
        """)
        btn_standby.clicked.connect(lambda: self._choose_action(self.ACTION_STANDBY))
        btn_layout.addWidget(btn_standby)
        
        layout.addLayout(btn_layout)
        outer_layout.addWidget(container)

    def _make_field_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 700;")
        return lbl

    def _choose_action(self, action: str):
        self.selected_action = action
        self.accept()
