import os
import random
from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QComboBox, QDateEdit, QPushButton, QRadioButton,
    QButtonGroup, QFrame, QToolButton, QCheckBox, QMessageBox,
    QGraphicsDropShadowEffect, QSizePolicy, QApplication
)
from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtGui import QIcon, QPixmap, QColor, QKeySequence, QShortcut

from app.ui.dialogs.archive_dialog import ArchiveDialog
from app.ui.dialogs.doctors_dialog import DoctorsDialog
from app.ui.dialogs.referrers_dialog import ReferrersDialog
from app.ui.dialogs.templates_dialog import TemplatesDialog
from app.core.paths import get_asset_path


class NewPatientDialog(QDialog):
    """
    New Patient Clinical Intake Workstation.
    Full clinical workspace layout for Endocare,
    featuring the centered New Patient card and the persistent right-hand workflow sidebar.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowState(Qt.WindowFullScreen)
        self.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.setMinimumSize(1080, 600)
        
        QShortcut(QKeySequence(Qt.Key_F11), self, self._toggle_fullscreen)
        
        self._assets_dir = get_asset_path()
        self._init_ui()

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showMaximized()

    def _init_ui(self):
        root = QFrame(self)
        root.setObjectName("newPatientWorkstationRoot")
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(root)
        
        workspace_layout = QHBoxLayout(root)
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(0)
        
        # =========================================================================
        # 1. CENTER CLINICAL CANVAS (Holds the centered New Patient Card)
        # =========================================================================
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(40, 20, 40, 20)
        canvas_layout.setAlignment(Qt.AlignCenter)
        
        # Elevated New Patient Card
        card = QFrame()
        card.setObjectName("newPatientCard")
        card.setFixedWidth(640)
        
        # Drop shadow effect
        card_shadow = QGraphicsDropShadowEffect(self)
        card_shadow.setBlurRadius(32)
        card_shadow.setColor(QColor(0, 0, 0, 200))
        card_shadow.setOffset(0, 8)
        card.setGraphicsEffect(card_shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 16, 24, 20)
        card_layout.setSpacing(12)
        
        # --- Card Header: [CLOSE] ... New Patient ... [ADD] ---
        card_header = QHBoxLayout()
        card_header.setContentsMargins(0, 0, 0, 4)
        
        self.btn_card_close = QPushButton("CLOSE")
        self.btn_card_close.setObjectName("cardCloseBtn")
        self.btn_card_close.setCursor(Qt.PointingHandCursor)
        self.btn_card_close.clicked.connect(self.reject)
        card_header.addWidget(self.btn_card_close)
        
        card_header.addStretch()
        
        card_title = QLabel("New Patient")
        card_title.setObjectName("cardTitle")
        card_title.setAlignment(Qt.AlignCenter)
        card_header.addWidget(card_title)
        
        card_header.addStretch()
        
        self.btn_card_add = QPushButton("ADD")
        self.btn_card_add.setObjectName("cardAddBtn")
        self.btn_card_add.setCursor(Qt.PointingHandCursor)
        self.btn_card_add.clicked.connect(self._handle_add_patient)
        card_header.addWidget(self.btn_card_add)
        
        card_layout.addLayout(card_header)
        
        # Header accent separator
        h_sep = QFrame()
        h_sep.setFrameShape(QFrame.HLine)
        h_sep.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 transparent, stop:0.2 #0284C7, stop:0.5 #38BDF8, stop:0.8 #0284C7, stop:1 transparent);
            max-height: 1.5px;
            margin-bottom: 6px;
        """)
        card_layout.addWidget(h_sep)
        
        # --- Form Grid (Exact 12 rows from reference) ---
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)
        
        row = 0
        
        # 1. Patient Name
        lbl_name = QLabel("Patient Name :")
        lbl_name.setProperty("class", "formFieldLabel")
        self.input_name = QLineEdit()
        self.input_name.setProperty("class", "formInput")
        self.input_name.setPlaceholderText("Enter full patient name...")
        grid.addWidget(lbl_name, row, 0)
        grid.addWidget(self.input_name, row, 1, 1, 3)
        row += 1
        
        # 2. Age / Sex
        lbl_age_sex = QLabel("Age / Sex :")
        lbl_age_sex.setProperty("class", "formFieldLabel")
        
        age_sex_layout = QHBoxLayout()
        age_sex_layout.setSpacing(14)
        
        self.input_age = QLineEdit()
        self.input_age.setProperty("class", "formInput")
        self.input_age.setPlaceholderText("Age")
        self.input_age.setFixedWidth(80)
        age_sex_layout.addWidget(self.input_age)
        
        # Radio buttons for Gender
        self.radio_male = QRadioButton("Male")
        self.radio_male.setProperty("class", "formRadio")
        self.radio_male.setChecked(True)
        self.radio_female = QRadioButton("Female")
        self.radio_female.setProperty("class", "formRadio")
        
        self.gender_group = QButtonGroup(self)
        self.gender_group.addButton(self.radio_male)
        self.gender_group.addButton(self.radio_female)
        
        age_sex_layout.addWidget(self.radio_male)
        age_sex_layout.addWidget(self.radio_female)
        age_sex_layout.addStretch()
        
        grid.addWidget(lbl_age_sex, row, 0)
        grid.addLayout(age_sex_layout, row, 1, 1, 3)
        row += 1
        
        # 3. MRN & Bed
        lbl_mrn = QLabel("MRN :")
        lbl_mrn.setProperty("class", "formFieldLabel")
        self.input_mrn = QLineEdit()
        self.input_mrn.setProperty("class", "formInput")
        self.input_mrn.setText(f"ENDO-{datetime.now().strftime('%Y')}-{random.randint(1000, 9999)}")
        
        lbl_bed = QLabel("Bed :")
        lbl_bed.setProperty("class", "formFieldLabel")
        self.input_bed = QLineEdit()
        self.input_bed.setProperty("class", "formInput")
        self.input_bed.setText("OPD")
        
        mrn_bed_layout = QHBoxLayout()
        mrn_bed_layout.setSpacing(12)
        mrn_bed_layout.addWidget(self.input_mrn, stretch=2)
        mrn_bed_layout.addWidget(lbl_bed)
        mrn_bed_layout.addWidget(self.input_bed, stretch=2)
        
        grid.addWidget(lbl_mrn, row, 0)
        grid.addLayout(mrn_bed_layout, row, 1, 1, 3)
        row += 1
        
        # 4. Procedure + [X]
        lbl_proc = QLabel("Procedure :")
        lbl_proc.setProperty("class", "formFieldLabel")
        
        proc_layout = QHBoxLayout()
        proc_layout.setSpacing(6)
        
        self.combo_proc = QComboBox()
        self.combo_proc.setProperty("class", "formCombo")
        self.combo_proc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.combo_proc.addItems([
            "COLONOSCOPY",
            "UPPER GI ENDOSCOPY (EGD / GASTROSCOPY)",
            "ENDOSCOPIC RETROGRADE CHOLANGIOPANCREATOGRAPHY (ERCP)",
            "FLEXIBLE SIGMOIDOSCOPY",
            "DIAGNOSTIC BRONCHOSCOPY",
            "ENDOSCOPIC ULTRASOUND (EUS)",
            "POLYPECTOMY & MUCOSAL RESECTION (EMR)"
        ])
        
        btn_clear_proc = QToolButton()
        btn_clear_proc.setObjectName("quickClearBtn")
        btn_clear_proc.setText("✕")
        btn_clear_proc.setToolTip("Clear Procedure Selection")
        btn_clear_proc.setCursor(Qt.PointingHandCursor)
        btn_clear_proc.clicked.connect(lambda: self.combo_proc.setCurrentIndex(0))
        
        proc_layout.addWidget(self.combo_proc)
        proc_layout.addWidget(btn_clear_proc)
        
        grid.addWidget(lbl_proc, row, 0)
        grid.addLayout(proc_layout, row, 1, 1, 3)
        row += 1
        
        # 5. Referrer + [+]
        lbl_ref = QLabel("Referrer :")
        lbl_ref.setProperty("class", "formFieldLabel")
        
        ref_layout = QHBoxLayout()
        ref_layout.setSpacing(6)
        
        self.combo_ref = QComboBox()
        self.combo_ref.setProperty("class", "formCombo")
        self.combo_ref.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.combo_ref.addItems([
            "Direct Clinical Intake / Self Referral",
            "Dr. Arthur Morgan (Metropolitan GI Clinic)",
            "Dr. Rebecca Vance (Westside Family Practice)",
            "Dr. Kenneth Lee (St. Jude Internal Medicine)",
            "Emergency Department Referral"
        ])
        
        btn_add_ref = QToolButton()
        btn_add_ref.setObjectName("quickAddBtn")
        btn_add_ref.setText("＋")
        btn_add_ref.setToolTip("Manage / Add New Referrer")
        btn_add_ref.setCursor(Qt.PointingHandCursor)
        btn_add_ref.clicked.connect(self._open_referrers)
        
        ref_layout.addWidget(self.combo_ref)
        ref_layout.addWidget(btn_add_ref)
        
        grid.addWidget(lbl_ref, row, 0)
        grid.addLayout(ref_layout, row, 1, 1, 3)
        row += 1
        
        # 6. Doctor + [+]
        lbl_doc = QLabel("Doctor :")
        lbl_doc.setProperty("class", "formFieldLabel")
        
        doc_layout = QHBoxLayout()
        doc_layout.setSpacing(6)
        
        self.combo_doc = QComboBox()
        self.combo_doc.setProperty("class", "formCombo")
        self.combo_doc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.combo_doc.addItems([
            "Dr. Sarah Jenkins (Senior Consultant Gastroenterologist)",
            "Dr. Michael Chang (Advanced Interventional Endoscopist)",
            "Dr. Elena Rostova (Consultant Gastroenterologist)",
            "Dr. David Miller (Associate Endoscopist)"
        ])
        
        btn_add_doc = QToolButton()
        btn_add_doc.setObjectName("quickAddBtn")
        btn_add_doc.setText("＋")
        btn_add_doc.setToolTip("Manage / Add New Doctor")
        btn_add_doc.setCursor(Qt.PointingHandCursor)
        btn_add_doc.clicked.connect(self._open_doctors)
        
        doc_layout.addWidget(self.combo_doc)
        doc_layout.addWidget(btn_add_doc)
        
        grid.addWidget(lbl_doc, row, 0)
        grid.addLayout(doc_layout, row, 1, 1, 3)
        row += 1
        
        # 7. Indication
        lbl_ind = QLabel("Indication :")
        lbl_ind.setProperty("class", "formFieldLabel")
        self.input_ind = QLineEdit()
        self.input_ind.setProperty("class", "formInput")
        self.input_ind.setPlaceholderText("e.g., Routine CRC screening, rectal bleeding, polyp follow-up...")
        grid.addWidget(lbl_ind, row, 0)
        grid.addWidget(self.input_ind, row, 1, 1, 3)
        row += 1
        
        # Separator Line before Demographics
        sep_mid = QFrame()
        sep_mid.setFrameShape(QFrame.HLine)
        sep_mid.setStyleSheet("background-color: #1E293B; max-height: 1px; margin: 4px 0;")
        grid.addWidget(sep_mid, row, 0, 1, 4)
        row += 1
        
        # 8. Visit Date
        lbl_date = QLabel("Visit Date :")
        lbl_date.setProperty("class", "formFieldLabel")
        self.input_date = QDateEdit()
        self.input_date.setProperty("class", "formInput")
        self.input_date.setCalendarPopup(True)
        self.input_date.setDisplayFormat("dddd , d MMMM, yyyy")
        self.input_date.setDate(QDate.currentDate())
        grid.addWidget(lbl_date, row, 0)
        grid.addWidget(self.input_date, row, 1, 1, 3)
        row += 1
        
        # 9. Address
        lbl_addr = QLabel("Address :")
        lbl_addr.setProperty("class", "formFieldLabel")
        self.input_addr = QLineEdit()
        self.input_addr.setProperty("class", "formInput")
        self.input_addr.setPlaceholderText("Street Address / Clinic ward...")
        grid.addWidget(lbl_addr, row, 0)
        grid.addWidget(self.input_addr, row, 1, 1, 3)
        row += 1
        
        # 10. Town & State
        lbl_town = QLabel("Town :")
        lbl_town.setProperty("class", "formFieldLabel")
        self.input_town = QLineEdit()
        self.input_town.setProperty("class", "formInput")
        
        lbl_state = QLabel("State :")
        lbl_state.setProperty("class", "formFieldLabel")
        self.input_state = QLineEdit()
        self.input_state.setProperty("class", "formInput")
        
        town_state_layout = QHBoxLayout()
        town_state_layout.setSpacing(12)
        town_state_layout.addWidget(self.input_town, stretch=2)
        town_state_layout.addWidget(lbl_state)
        town_state_layout.addWidget(self.input_state, stretch=2)
        
        grid.addWidget(lbl_town, row, 0)
        grid.addLayout(town_state_layout, row, 1, 1, 3)
        row += 1
        
        # 11. Post Code & Phone
        lbl_post = QLabel("Post Code :")
        lbl_post.setProperty("class", "formFieldLabel")
        self.input_post = QLineEdit()
        self.input_post.setProperty("class", "formInput")
        
        lbl_phone = QLabel("Phone :")
        lbl_phone.setProperty("class", "formFieldLabel")
        self.input_phone = QLineEdit()
        self.input_phone.setProperty("class", "formInput")
        self.input_phone.setPlaceholderText("+1 (555) 000-0000")
        
        post_phone_layout = QHBoxLayout()
        post_phone_layout.setSpacing(12)
        post_phone_layout.addWidget(self.input_post, stretch=2)
        post_phone_layout.addWidget(lbl_phone)
        post_phone_layout.addWidget(self.input_phone, stretch=2)
        
        grid.addWidget(lbl_post, row, 0)
        grid.addLayout(post_phone_layout, row, 1, 1, 3)
        row += 1
        
        card_layout.addLayout(grid)
        canvas_layout.addWidget(card)
        
        workspace_layout.addWidget(canvas_container, stretch=1)
        
        # =========================================================================
        # 2. PERSISTENT RIGHT SIDEBAR (Matching reference layout)
        # =========================================================================
        sidebar = QFrame()
        sidebar.setObjectName("workspaceSidebar")
        sidebar.setFixedWidth(230)
        
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(14, 16, 14, 16)
        side_layout.setSpacing(10)
        
        # Top Logo Banner
        logo_lbl = QLabel()
        logo_lbl.setAlignment(Qt.AlignCenter)
        logo_path = os.path.join(self._assets_dir, "logo.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(190, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_lbl.setPixmap(pix)
        else:
            logo_lbl.setText("ENDOCARE")
            logo_lbl.setStyleSheet("color: #38BDF8; font-size: 20px; font-weight: bold;")
        side_layout.addWidget(logo_lbl)
        
        # Glowing Divider
        s_line = QFrame()
        s_line.setFrameShape(QFrame.HLine)
        s_line.setStyleSheet("background-color: #1E293B; max-height: 1px; margin-bottom: 4px;")
        side_layout.addWidget(s_line)
        
        # --- Primary Clinical Navigation Buttons ---
        btn_nav_patient = QPushButton("New Patient")
        btn_nav_patient.setProperty("class", "sideNavActiveBtn")  # Highlighted active
        btn_nav_patient.setCursor(Qt.PointingHandCursor)
        side_layout.addWidget(btn_nav_patient)
        
        btn_nav_archive = QPushButton("Patients Archive")
        btn_nav_archive.setProperty("class", "sideNavBtn")
        btn_nav_archive.setCursor(Qt.PointingHandCursor)
        btn_nav_archive.clicked.connect(self._open_archive)
        side_layout.addWidget(btn_nav_archive)
        
        btn_nav_doctors = QPushButton("Doctors")
        btn_nav_doctors.setProperty("class", "sideNavBtn")
        btn_nav_doctors.setCursor(Qt.PointingHandCursor)
        btn_nav_doctors.clicked.connect(self._open_doctors)
        side_layout.addWidget(btn_nav_doctors)
        
        btn_nav_referrers = QPushButton("Referrers")
        btn_nav_referrers.setProperty("class", "sideNavBtn")
        btn_nav_referrers.setCursor(Qt.PointingHandCursor)
        btn_nav_referrers.clicked.connect(self._open_referrers)
        side_layout.addWidget(btn_nav_referrers)
        
        btn_nav_templates = QPushButton("Templates")
        btn_nav_templates.setProperty("class", "sideNavBtn")
        btn_nav_templates.setCursor(Qt.PointingHandCursor)
        btn_nav_templates.clicked.connect(self._open_templates)
        side_layout.addWidget(btn_nav_templates)
        
        side_layout.addStretch()
        
        # --- Report & Workflow Actions Group ---
        actions_box = QFrame()
        actions_box.setStyleSheet("""
            QFrame {
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid #1E293B;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        act_layout = QVBoxLayout(actions_box)
        act_layout.setContentsMargins(6, 6, 6, 6)
        act_layout.setSpacing(8)
        
        btn_capture = QPushButton("Back to Capture")
        btn_capture.setProperty("class", "sideActionBtn")
        btn_capture.setCursor(Qt.PointingHandCursor)
        btn_capture.clicked.connect(self._handle_back_to_capture)
        act_layout.addWidget(btn_capture)
        
        self.chk_update_report = QCheckBox("Update Report")
        self.chk_update_report.setProperty("class", "sideCheckBox")
        self.chk_update_report.setChecked(True)
        act_layout.addWidget(self.chk_update_report)
        
        btn_print = QPushButton("Print Report")
        btn_print.setProperty("class", "sideActionBtn")
        btn_print.setCursor(Qt.PointingHandCursor)
        btn_print.clicked.connect(lambda: QMessageBox.information(self, "Print", "Preparing Clinical Diagnostic Report for print..."))
        act_layout.addWidget(btn_print)
        
        self.chk_export_report = QCheckBox("Export Report")
        self.chk_export_report.setProperty("class", "sideCheckBox")
        act_layout.addWidget(self.chk_export_report)
        
        btn_close_rep = QPushButton("Close Report")
        btn_close_rep.setProperty("class", "sideActionBtn")
        btn_close_rep.setCursor(Qt.PointingHandCursor)
        btn_close_rep.clicked.connect(self.accept)
        act_layout.addWidget(btn_close_rep)
        
        side_layout.addWidget(actions_box)
        
        side_layout.addSpacing(6)
        
        # --- Bottom HOME & EXIT Controls ---
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(10)
        
        btn_home = QPushButton("HOME")
        btn_home.setObjectName("sideHomeBtn")
        btn_home.setCursor(Qt.PointingHandCursor)
        btn_home.clicked.connect(self.accept)  # Returns to main launcher
        bottom_row.addWidget(btn_home)
        
        btn_exit = QPushButton("EXIT")
        btn_exit.setObjectName("sideExitBtn")
        btn_exit.setCursor(Qt.PointingHandCursor)
        btn_exit.clicked.connect(self._confirm_exit)
        bottom_row.addWidget(btn_exit)
        
        side_layout.addLayout(bottom_row)
        
        workspace_layout.addWidget(sidebar)

    # --- Actions & Dialog Handlers ---
    def _handle_add_patient(self):
        name = self.input_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Notice", "Please enter the Patient Full Name before proceeding.")
            self.input_name.setFocus()
            return
            
        from app.services.database import DatabaseService
        db = DatabaseService.get_instance()
        
        mrn = self.input_mrn.text().strip() or db.get_next_mrn()
        procedure = self.combo_proc.currentText()
        doctor = self.combo_doc.currentText()
        referrer = self.combo_ref.currentText() if hasattr(self, "combo_ref") else ""
        gender = "Male" if self.radio_male.isChecked() else "Female"
        age = self.input_age.text().strip()
        
        patient_data = {
            "name": name,
            "mrn": mrn,
            "procedure_name": procedure,
            "doctor_name": doctor,
            "referrer_name": referrer,
            "sex": gender,
            "age": int(age) if age.isdigit() else 0,
            "indication": self.input_ind.text().strip(),
            "visit_date": self.date_visit.date().toString("dd-MM-yyyy"),
            "address": self.input_address.text().strip(),
            "town": self.input_town.text().strip(),
            "state": self.input_state.text().strip(),
            "postcode": self.input_postcode.text().strip(),
            "phone": self.input_phone.text().strip()
        }
        
        auto_id = db.add_patient(patient_data)
        patient_data["auto_id"] = auto_id
        
        from app.ui.dialogs.patient_success_dialog import PatientAddedSuccessDialog
        dialog = PatientAddedSuccessDialog(patient_data, parent=self)
        dialog.exec()
        
        action = dialog.selected_action
        if action == PatientAddedSuccessDialog.ACTION_ADD_NEW:
            self.input_name.clear()
            self.input_mrn.clear()
            self.input_age.clear()
            self.input_ind.clear()
            self.input_address.clear()
            self.input_town.clear()
            self.input_state.clear()
            self.input_postcode.clear()
            self.input_phone.clear()
            self.input_name.setFocus()
        elif action == PatientAddedSuccessDialog.ACTION_CAPTURE:
            parent_w = self.parent()
            self.accept()
            from app.ui.capture_window import CaptureWindow
            dlg = CaptureWindow(patient_data=patient_data, parent=parent_w)
            dlg.showMaximized()
            dlg.exec()
        elif action == PatientAddedSuccessDialog.ACTION_STANDBY:
            self.accept()

    def _handle_back_to_capture(self):
        parent_w = self.parent()
        self.accept()
        from app.ui.capture_window import CaptureWindow
        dlg = CaptureWindow(parent=parent_w)
        dlg.showMaximized()
        dlg.exec()

    def _open_doctors(self):
        dlg = DoctorsDialog(self)
        dlg.showMaximized()
        dlg.exec()

    def _open_referrers(self):
        dlg = ReferrersDialog(self)
        dlg.showMaximized()
        dlg.exec()

    def _open_archive(self):
        dlg = ArchiveDialog(self)
        dlg.showMaximized()
        dlg.exec()

    def _open_templates(self):
        dlg = TemplatesDialog(self)
        dlg.showMaximized()
        dlg.exec()

    def _confirm_exit(self):
        reply = QMessageBox.question(
            self, "Exit Endocare",
            "Are you sure you want to terminate Endocare?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.reject()
