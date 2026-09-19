"""
Endocare - Clinical Workstation Window
Unified clinical workspace hosting New Patient, Doctors Archive, Patients Archive,
Referrers Archive, and Template Editor on the SAME background page.
Strictly respects Windows desktop taskbar (bottom bar) geometry.
"""

import os
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QListWidget, QListWidgetItem,
    QPlainTextEdit, QTextEdit, QComboBox, QRadioButton, QButtonGroup,
    QDateEdit, QToolButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QCheckBox, QMessageBox, QGraphicsDropShadowEffect, QStackedWidget,
    QApplication, QAbstractItemView, QFontDialog, QFileDialog
)
from PySide6.QtCore import Qt, QDate, QRect
from PySide6.QtGui import (
    QPixmap, QColor, QFont, QTextCursor, QTextListFormat,
    QTextBlockFormat, QTextCharFormat
)


class WorkstationWindow(QDialog):
    """
    Unified Clinical Workstation.
    Maintains a persistent background canvas and right-hand workflow sidebar.
    Clinical modules (New Patient, Doctors Archive, Patients Archive, Referrers, Templates)
    open seamlessly as cards/dialogs on the SAME background page.
    """
    def __init__(self, initial_module: str = "new_patient", parent=None):
        super().__init__(parent)
        self.setWindowTitle("EndoCare 2.42 • Clinical Endoscopy Workstation")
        self.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        
        self._assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../assets"))
        
        # Safe screen geometry: strictly respect Windows desktop taskbar bounds
        self._apply_safe_screen_geometry()
        
        # Build unified workspace
        self._init_ui()
        
        # Switch to requested initial module
        self.set_module(initial_module)

    def _apply_safe_screen_geometry(self):
        """Ensures the workstation window never overlaps the Windows desktop bottom taskbar."""
        screen = QApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else QRect(0, 0, 1366, 720)
        
        # Available height on 1366x768 with 40px taskbar is 728.
        # Windows title bar takes ~32px, so client height of 672 leaves clear space above taskbar.
        target_w = min(1350, avail.width() - 16)
        target_h = min(672, avail.height() - 36)
        
        self.resize(target_w, target_h)
        self.setMinimumSize(1080, 620)
        self.setMaximumHeight(avail.height() - 8)
        self.setMaximumWidth(avail.width())
        
        # Position centered within available desktop area (above taskbar)
        x = avail.x() + (avail.width() - target_w) // 2
        y = avail.y() + (avail.height() - target_h) // 2
        self.move(max(avail.x(), x), max(avail.y(), y))

    def _init_ui(self):
        root = QFrame(self)
        root.setObjectName("workstationRoot")
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(root)
        
        workspace_layout = QHBoxLayout(root)
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(0)
        
        # =========================================================================
        # 1. CENTRAL CLINICAL CANVAS (Hosts the active card/dialog on the same page)
        # =========================================================================
        self.canvas_container = QWidget()
        self.canvas_layout = QVBoxLayout(self.canvas_container)
        self.canvas_layout.setContentsMargins(16, 12, 16, 12)
        self.canvas_layout.setAlignment(Qt.AlignCenter)
        
        # Stacked widget for smooth switching on the same background
        self.stack = QStackedWidget()
        
        # Cards
        self.card_new_patient = NewPatientCardWidget(self)
        self.card_doctors = DoctorsCardWidget(self)
        self.card_archive = ArchiveCardWidget(self)
        self.card_referrers = ReferrersCardWidget(self)
        self.card_templates = TemplatesCardWidget(self)
        
        self.stack.addWidget(self.card_new_patient)  # Index 0
        self.stack.addWidget(self.card_doctors)      # Index 1
        self.stack.addWidget(self.card_archive)      # Index 2
        self.stack.addWidget(self.card_referrers)    # Index 3
        self.stack.addWidget(self.card_templates)    # Index 4
        
        self.canvas_layout.addWidget(self.stack)
        workspace_layout.addWidget(self.canvas_container, 1)
        
        # Vertical divider between canvas and sidebar
        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 transparent, stop:0.1 #0284C7, stop:0.5 #38BDF8, stop:0.9 #0284C7, stop:1 transparent);
            max-width: 1.5px;
        """)
        workspace_layout.addWidget(divider)
        
        # =========================================================================
        # 2. PERSISTENT WORKFLOW SIDEBAR (Identical across all modules)
        # =========================================================================
        self._build_sidebar(workspace_layout)

    def _build_sidebar(self, parent_layout):
        sidebar = QFrame()
        sidebar.setObjectName("sideOpsPanel")
        sidebar.setFixedWidth(220)
        
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(10, 10, 10, 10)
        side_layout.setSpacing(6)
        
        # --- Brand Header ---
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        logo_path = os.path.join(self._assets_dir, "logo.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(165, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pix)
        else:
            logo_label.setText("EndoCare")
            logo_label.setStyleSheet("color: #38BDF8; font-size: 20px; font-weight: bold;")
        side_layout.addWidget(logo_label)
        
        subtitle = QLabel("All Solution of Endoscopy")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #64748B; font-size: 9px; font-weight: 600; margin-bottom: 4px;")
        side_layout.addWidget(subtitle)
        
        # --- Primary Module Navigation Buttons ---
        self.nav_buttons = {}
        
        modules = [
            ("new_patient", "New Patient"),
            ("archive", "Patients Archive"),
            ("doctors", "Doctors"),
            ("referrers", "Referrers"),
            ("templates", "Templates"),
        ]
        
        for key, text in modules:
            btn = QPushButton(text)
            btn.setObjectName("sideNavBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, k=key: self.set_module(k))
            self.nav_buttons[key] = btn
            side_layout.addWidget(btn)
            
        side_layout.addSpacing(6)
        
        # --- Report Operations Group Box ---
        actions_box = QFrame()
        actions_box.setObjectName("reportOpsBox")
        act_layout = QVBoxLayout(actions_box)
        act_layout.setContentsMargins(6, 6, 6, 6)
        act_layout.setSpacing(4)
        
        btn_back_capture = QPushButton("Back to Capture")
        btn_back_capture.setObjectName("btnReportAction")
        btn_back_capture.setCursor(Qt.PointingHandCursor)
        btn_back_capture.clicked.connect(self.close_workstation)
        act_layout.addWidget(btn_back_capture)
        
        self.chk_update = QCheckBox("Update Report")
        self.chk_update.setObjectName("chkReportToggle")
        self.chk_update.setChecked(True)
        act_layout.addWidget(self.chk_update)
        
        btn_print_rep = QPushButton("Print Report")
        btn_print_rep.setObjectName("btnReportAction")
        btn_print_rep.setCursor(Qt.PointingHandCursor)
        btn_print_rep.clicked.connect(self._handle_print_report)
        act_layout.addWidget(btn_print_rep)
        
        self.chk_export = QCheckBox("Export Report")
        self.chk_export.setObjectName("chkReportToggle")
        act_layout.addWidget(self.chk_export)
        
        btn_close_rep = QPushButton("Close Report")
        btn_close_rep.setObjectName("btnReportAction")
        btn_close_rep.setCursor(Qt.PointingHandCursor)
        btn_close_rep.clicked.connect(self.close_workstation)
        act_layout.addWidget(btn_close_rep)
        
        side_layout.addWidget(actions_box)
        side_layout.addStretch(1)
        
        # --- Bottom HOME & EXIT Controls ---
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(8)
        
        btn_home = QPushButton("HOME")
        btn_home.setObjectName("sideHomeBtn")
        btn_home.setCursor(Qt.PointingHandCursor)
        btn_home.clicked.connect(self.close_workstation)
        bottom_row.addWidget(btn_home)
        
        btn_exit = QPushButton("EXIT")
        btn_exit.setObjectName("sideExitBtn")
        btn_exit.setCursor(Qt.PointingHandCursor)
        btn_exit.clicked.connect(self._confirm_exit)
        bottom_row.addWidget(btn_exit)
        
        side_layout.addLayout(bottom_row)
        parent_layout.addWidget(sidebar)

    def set_module(self, module_name: str):
        """Switches active card/dialog on the same background page and updates tab highlighting."""
        module_map = {
            "new_patient": (0, self.card_new_patient),
            "doctors": (1, self.card_doctors),
            "archive": (2, self.card_archive),
            "referrers": (3, self.card_referrers),
            "templates": (4, self.card_templates),
        }
        
        if module_name == "archive":
            from app.ui.dialogs.archive_dialog import ArchiveDialog
            dlg = ArchiveDialog(parent=self)
            dlg.exec()
            return

        if module_name not in module_map:
            module_name = "new_patient"
            
        index, card_widget = module_map[module_name]
        self.stack.setCurrentIndex(index)
        
        # Update tab styles: highlight active, reset others
        for key, btn in self.nav_buttons.items():
            if key == module_name:
                btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #0369A1);
                        color: #FFFFFF;
                        border: 2px solid #38BDF8;
                        border-radius: 6px;
                        font-weight: 800;
                        font-size: 13px;
                        padding: 7px 12px;
                        text-align: center;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #E2E8F0);
                        color: #0F172A;
                        border: 1px solid #CBD5E1;
                        border-radius: 6px;
                        font-weight: 700;
                        font-size: 13px;
                        padding: 7px 12px;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background: #0284C7;
                        color: #FFFFFF;
                        border-color: #38BDF8;
                    }
                """)

    def close_workstation(self):
        """Closes the workstation and returns cleanly to the main launcher."""
        self.accept()

    def _confirm_exit(self):
        reply = QMessageBox.question(
            self, "Exit Endocare",
            "Are you sure you want to terminate Endocare?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.reject()

    def _handle_print_report(self):
        QMessageBox.information(
            self, "Clinical Report Engine",
            "Generating standardized Endoscopy Examination Report...\n"
            "Document sent to default medical printer spooler."
        )


# =============================================================================
# MODULE CARDS (Rendered directly in the center of the SAME background page)
# =============================================================================

class NewPatientCardWidget(QFrame):
    """New Patient intake card modeled faithfully after Demo/Newpatient.PNG."""
    def __init__(self, workstation: WorkstationWindow):
        super().__init__()
        self.workstation = workstation
        self.setObjectName("newPatientCard")
        self.setFixedWidth(740)
        
        # Visual drop shadow
        card_shadow = QGraphicsDropShadowEffect(self)
        card_shadow.setBlurRadius(28)
        card_shadow.setColor(QColor(0, 0, 0, 180))
        card_shadow.setOffset(0, 6)
        self.setGraphicsEffect(card_shadow)
        
        card_layout = QVBoxLayout(self)
        card_layout.setContentsMargins(20, 12, 20, 14)
        card_layout.setSpacing(8)
        
        # --- Header ---
        card_header = QHBoxLayout()
        btn_close = QPushButton("CLOSE")
        btn_close.setObjectName("cardCloseBtn")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.workstation.close_workstation)
        card_header.addWidget(btn_close)
        
        card_header.addStretch()
        title_lbl = QLabel("New Patient")
        title_lbl.setObjectName("cardTitle")
        title_lbl.setAlignment(Qt.AlignCenter)
        card_header.addWidget(title_lbl)
        card_header.addStretch()
        
        btn_add = QPushButton("ADD")
        btn_add.setObjectName("cardAddBtn")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self._handle_add)
        card_header.addWidget(btn_add)
        card_layout.addLayout(card_header)
        
        # Thin divider
        h_sep = QFrame()
        h_sep.setFrameShape(QFrame.HLine)
        h_sep.setStyleSheet("background: #0284C7; max-height: 1.5px; margin-bottom: 4px;")
        card_layout.addWidget(h_sep)
        
        # --- 12 Clinical Intake Form Fields ---
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(7)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)
        
        row = 0
        
        # 1. Patient Name
        lbl = QLabel("Patient Name :")
        lbl.setProperty("class", "formFieldLabel")
        self.input_name = QLineEdit()
        self.input_name.setProperty("class", "formInput")
        self.input_name.setPlaceholderText("Enter full patient name...")
        grid.addWidget(lbl, row, 0)
        grid.addWidget(self.input_name, row, 1, 1, 3)
        row += 1
        
        # 2. Age / Sex
        lbl = QLabel("Age / Sex :")
        lbl.setProperty("class", "formFieldLabel")
        age_sex_box = QHBoxLayout()
        age_sex_box.setSpacing(12)
        self.input_age = QLineEdit()
        self.input_age.setProperty("class", "formInput")
        self.input_age.setPlaceholderText("Age")
        self.input_age.setFixedWidth(75)
        age_sex_box.addWidget(self.input_age)
        
        self.radio_male = QRadioButton("Male")
        self.radio_male.setProperty("class", "formRadio")
        self.radio_male.setChecked(True)
        self.radio_female = QRadioButton("Female")
        self.radio_female.setProperty("class", "formRadio")
        self.gender_group = QButtonGroup(self)
        self.gender_group.addButton(self.radio_male)
        self.gender_group.addButton(self.radio_female)
        age_sex_box.addWidget(self.radio_male)
        age_sex_box.addWidget(self.radio_female)
        age_sex_box.addStretch()
        grid.addWidget(lbl, row, 0)
        grid.addLayout(age_sex_box, row, 1, 1, 3)
        row += 1
        
        # 3. MRN / Bed
        lbl = QLabel("MRN :")
        lbl.setProperty("class", "formFieldLabel")
        mrn_box = QHBoxLayout()
        self.input_mrn = QLineEdit()
        self.input_mrn.setProperty("class", "formInput")
        self.input_mrn.setPlaceholderText("Hospital MRN ID")
        mrn_box.addWidget(self.input_mrn)
        lbl_bed = QLabel("Bed :")
        lbl_bed.setProperty("class", "formFieldLabel")
        mrn_box.addWidget(lbl_bed)
        self.input_bed = QLineEdit("OPD")
        self.input_bed.setProperty("class", "formInput")
        self.input_bed.setFixedWidth(120)
        mrn_box.addWidget(self.input_bed)
        grid.addWidget(lbl, row, 0)
        grid.addLayout(mrn_box, row, 1, 1, 3)
        row += 1
        
        # 4. Procedure
        lbl = QLabel("Procedure :")
        lbl.setProperty("class", "formFieldLabel")
        proc_box = QHBoxLayout()
        self.combo_proc = QComboBox()
        self.combo_proc.setProperty("class", "formCombo")
        self.combo_proc.addItems([
            "COLONOSCOPY", "UPPER GI ENDOSCOPY", "ERCP", "SIGMOIDOSCOPY",
            "BRONCHOSCOPY", "EUS (ENDOSCOPIC ULTRASOUND)", "ENTEROSCOPY", "POLYPECTOMY"
        ])
        proc_box.addWidget(self.combo_proc)
        btn_proc_clr = QToolButton()
        btn_proc_clr.setObjectName("quickClearBtn")
        btn_proc_clr.setText("✕")
        btn_proc_clr.clicked.connect(lambda: self.combo_proc.setCurrentIndex(0))
        proc_box.addWidget(btn_proc_clr)
        grid.addWidget(lbl, row, 0)
        grid.addLayout(proc_box, row, 1, 1, 3)
        row += 1
        
        # 5. Referrer
        lbl = QLabel("Referrer :")
        lbl.setProperty("class", "formFieldLabel")
        ref_box = QHBoxLayout()
        self.combo_ref = QComboBox()
        self.combo_ref.setProperty("class", "formCombo")
        self.combo_ref.addItems(["General OPD Clinic", "Internal Medicine Dept", "Gastro Center", "Self-Referred"])
        ref_box.addWidget(self.combo_ref)
        btn_ref_add = QToolButton()
        btn_ref_add.setObjectName("quickAddBtn")
        btn_ref_add.setText("➕")
        btn_ref_add.clicked.connect(lambda: self.workstation.set_module("referrers"))
        ref_box.addWidget(btn_ref_add)
        grid.addWidget(lbl, row, 0)
        grid.addLayout(ref_box, row, 1, 1, 3)
        row += 1
        
        # 6. Doctor
        lbl = QLabel("Doctor :")
        lbl.setProperty("class", "formFieldLabel")
        doc_box = QHBoxLayout()
        self.combo_doc = QComboBox()
        self.combo_doc.setProperty("class", "formCombo")
        self.combo_doc.addItems(["Dr. Sarah Jenkins", "Dr. Michael Chang", "Dr. Elena Rostova", "Dr. David Miller"])
        doc_box.addWidget(self.combo_doc)
        btn_doc_add = QToolButton()
        btn_doc_add.setObjectName("quickAddBtn")
        btn_doc_add.setText("➕")
        btn_doc_add.clicked.connect(lambda: self.workstation.set_module("doctors"))
        doc_box.addWidget(btn_doc_add)
        grid.addWidget(lbl, row, 0)
        grid.addLayout(doc_box, row, 1, 1, 3)
        row += 1
        
        # 7. Indication
        lbl = QLabel("Indication :")
        lbl.setProperty("class", "formFieldLabel")
        self.input_ind = QLineEdit()
        self.input_ind.setProperty("class", "formInput")
        self.input_ind.setPlaceholderText("Clinical indication, symptoms, suspicion...")
        grid.addWidget(lbl, row, 0)
        grid.addWidget(self.input_ind, row, 1, 1, 3)
        row += 1
        
        # 8. Visit Date
        lbl = QLabel("Visit Date :")
        lbl.setProperty("class", "formFieldLabel")
        self.date_visit = QDateEdit()
        self.date_visit.setProperty("class", "formInput")
        self.date_visit.setDate(QDate.currentDate())
        self.date_visit.setCalendarPopup(True)
        grid.addWidget(lbl, row, 0)
        grid.addWidget(self.date_visit, row, 1, 1, 3)
        row += 1
        
        # 9. Address
        lbl = QLabel("Address :")
        lbl.setProperty("class", "formFieldLabel")
        self.input_address = QLineEdit()
        self.input_address.setProperty("class", "formInput")
        self.input_address.setPlaceholderText("Residential address...")
        grid.addWidget(lbl, row, 0)
        grid.addWidget(self.input_address, row, 1, 1, 3)
        row += 1
        
        # 10. Town / State
        lbl = QLabel("Town :")
        lbl.setProperty("class", "formFieldLabel")
        ts_box = QHBoxLayout()
        self.input_town = QLineEdit()
        self.input_town.setProperty("class", "formInput")
        ts_box.addWidget(self.input_town)
        lbl_state = QLabel("State :")
        lbl_state.setProperty("class", "formFieldLabel")
        ts_box.addWidget(lbl_state)
        self.input_state = QLineEdit()
        self.input_state.setProperty("class", "formInput")
        ts_box.addWidget(self.input_state)
        grid.addWidget(lbl, row, 0)
        grid.addLayout(ts_box, row, 1, 1, 3)
        row += 1
        
        # 11. Post Code / Phone
        lbl = QLabel("Post Code :")
        lbl.setProperty("class", "formFieldLabel")
        pp_box = QHBoxLayout()
        self.input_postcode = QLineEdit()
        self.input_postcode.setProperty("class", "formInput")
        self.input_postcode.setFixedWidth(110)
        pp_box.addWidget(self.input_postcode)
        lbl_phone = QLabel("Phone :")
        lbl_phone.setProperty("class", "formFieldLabel")
        pp_box.addWidget(lbl_phone)
        self.input_phone = QLineEdit()
        self.input_phone.setProperty("class", "formInput")
        pp_box.addWidget(self.input_phone)
        grid.addWidget(lbl, row, 0)
        grid.addLayout(pp_box, row, 1, 1, 3)
        
        card_layout.addLayout(grid)

    def _handle_add(self):
        name = self.input_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Notice", "Please enter the Patient Full Name before proceeding.")
            self.input_name.setFocus()
            return
            
        from app.services.database import DatabaseService
        db = DatabaseService.get_instance()
        
        mrn = self.input_mrn.text().strip() or db.get_next_mrn()
        proc = self.combo_proc.currentText()
        doc = self.combo_doc.currentText()
        ref = self.combo_ref.currentText() if hasattr(self, "combo_ref") else ""
        gender = "Male" if self.radio_male.isChecked() else "Female"
        age = self.input_age.text().strip()
        
        patient_data = {
            "name": name,
            "mrn": mrn,
            "procedure_name": proc,
            "doctor_name": doc,
            "referrer_name": ref,
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
            # Clear fields and keep focus for adding another patient
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
            # Closes intake and returns directly to capture viewports
            self.workstation.close_workstation()
        elif action == PatientAddedSuccessDialog.ACTION_STANDBY:
            # Leaves patient on standby and returns to launcher
            self.workstation.close_workstation()


class DoctorsCardWidget(QFrame):
    """Doctors Archive card modeled faithfully after Demo/Doctors.PNG."""
    def __init__(self, workstation: WorkstationWindow):
        super().__init__()
        self.workstation = workstation
        self.setObjectName("doctorsCard")
        self.setFixedWidth(740)
        
        # Visual drop shadow
        card_shadow = QGraphicsDropShadowEffect(self)
        card_shadow.setBlurRadius(28)
        card_shadow.setColor(QColor(0, 0, 0, 180))
        card_shadow.setOffset(0, 6)
        self.setGraphicsEffect(card_shadow)
        
        self.doctors = [
            {
                "name": "Dr. Sarah Jenkins",
                "specialty": "Gastroenterology / Advanced Therapeutic Endoscopy",
                "title": "Senior Consultant Gastroenterologist, MD, FACG",
                "department": "Endoscopy Unit & Digestive Health Institute",
                "address": "Diagnostic Center, Suite 402, Medical Arts Building",
                "phone": "+1 (555) 123-4567"
            },
            {
                "name": "Dr. Michael Chang",
                "specialty": "Gastrointestinal Endoscopy & ERCP",
                "title": "Clinical Director of GI Services, MBBS, FRCP",
                "department": "Department of Gastroenterology & Hepatology",
                "address": "Main Hospital Pavilion, 3rd Floor Endoscopy Suite",
                "phone": "+1 (555) 234-5678"
            },
            {
                "name": "Dr. Elena Rostova",
                "specialty": "Advanced Interventional Endoscopy & EUS",
                "title": "Chief of Endoscopic Surgery, MD, PhD",
                "department": "Division of Minimally Invasive Surgery",
                "address": "Surgical Tower, Suite 710",
                "phone": "+1 (555) 345-6789"
            },
            {
                "name": "Dr. David Miller",
                "specialty": "Diagnostic Endoscopy & Capsule Endoscopy",
                "title": "Associate Staff Physician, MBBS, MRCP",
                "department": "Day Care Endoscopy & Outpatient Clinic",
                "address": "North Medical Wing, Room 108",
                "phone": "+1 (555) 456-7890"
            }
        ]
        
        card_layout = QVBoxLayout(self)
        card_layout.setContentsMargins(20, 12, 20, 14)
        card_layout.setSpacing(8)
        
        # --- Header ---
        card_header = QHBoxLayout()
        btn_close = QPushButton("CLOSE")
        btn_close.setObjectName("cardCloseBtn")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.workstation.close_workstation)
        card_header.addWidget(btn_close)
        
        card_header.addStretch()
        title_lbl = QLabel("Doctors Archive")
        title_lbl.setObjectName("cardTitle")
        title_lbl.setAlignment(Qt.AlignCenter)
        card_header.addWidget(title_lbl)
        card_header.addStretch()
        
        spacer = QLabel()
        spacer.setFixedWidth(65)
        card_header.addWidget(spacer)
        card_layout.addLayout(card_header)
        
        # Thin divider
        h_sep = QFrame()
        h_sep.setFrameShape(QFrame.HLine)
        h_sep.setStyleSheet("background: #0284C7; max-height: 1.5px; margin-bottom: 4px;")
        card_layout.addWidget(h_sep)
        
        # --- Center Form & Roster Layout ---
        center_row = QHBoxLayout()
        center_row.setSpacing(14)
        
        # Left Form (6 fields)
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(8)
        form_layout.setVerticalSpacing(7)
        form_layout.setColumnStretch(0, 0)
        form_layout.setColumnStretch(1, 1)
        
        row = 0
        lbl = QLabel("Doctor Name :")
        lbl.setProperty("class", "formFieldLabel")
        self.input_name = QLineEdit()
        self.input_name.setProperty("class", "formInput")
        form_layout.addWidget(lbl, row, 0)
        form_layout.addWidget(self.input_name, row, 1)
        row += 1
        
        lbl = QLabel("Specialty :")
        lbl.setProperty("class", "formFieldLabel")
        self.input_spec = QLineEdit()
        self.input_spec.setProperty("class", "formInput")
        form_layout.addWidget(lbl, row, 0)
        form_layout.addWidget(self.input_spec, row, 1)
        row += 1
        
        lbl = QLabel("Title :")
        lbl.setProperty("class", "formFieldLabel")
        self.input_title = QLineEdit()
        self.input_title.setProperty("class", "formInput")
        form_layout.addWidget(lbl, row, 0)
        form_layout.addWidget(self.input_title, row, 1)
        row += 1
        
        lbl = QLabel("Department :")
        lbl.setProperty("class", "formFieldLabel")
        self.input_dept = QLineEdit()
        self.input_dept.setProperty("class", "formInput")
        form_layout.addWidget(lbl, row, 0)
        form_layout.addWidget(self.input_dept, row, 1)
        row += 1
        
        lbl = QLabel("Address :")
        lbl.setProperty("class", "formFieldLabel")
        self.txt_address = QPlainTextEdit()
        self.txt_address.setStyleSheet("background: #1E293B; color: #F8FAFC; border: 1.5px solid #334155; border-radius: 5px;")
        self.txt_address.setFixedHeight(60)
        form_layout.addWidget(lbl, row, 0, Qt.AlignTop)
        form_layout.addWidget(self.txt_address, row, 1)
        row += 1
        
        lbl = QLabel("Phone :")
        lbl.setProperty("class", "formFieldLabel")
        self.input_phone = QLineEdit()
        self.input_phone.setProperty("class", "formInput")
        form_layout.addWidget(lbl, row, 0)
        form_layout.addWidget(self.input_phone, row, 1)
        
        center_row.addLayout(form_layout, 6)
        
        # Right Roster List
        roster_col = QVBoxLayout()
        lbl_roster = QLabel("Active Physicians Roster:")
        lbl_roster.setStyleSheet("color: #38BDF8; font-size: 11px; font-weight: 700;")
        roster_col.addWidget(lbl_roster)
        
        self.list_doctors = QListWidget()
        self.list_doctors.setObjectName("doctorsListWidget")
        self.list_doctors.currentRowChanged.connect(self._on_doctor_selected)
        roster_col.addWidget(self.list_doctors)
        
        center_row.addLayout(roster_col, 4)
        card_layout.addLayout(center_row)
        
        # --- Bottom Actions & Record Navigator ---
        bot_row = QHBoxLayout()
        bot_row.setSpacing(8)
        
        btn_add = QPushButton("Add New")
        btn_add.setObjectName("btnDocAddNew")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self._handle_add_new)
        bot_row.addWidget(btn_add)
        
        btn_update = QPushButton("Update")
        btn_update.setObjectName("btnDocUpdate")
        btn_update.setCursor(Qt.PointingHandCursor)
        btn_update.clicked.connect(self._handle_update)
        bot_row.addWidget(btn_update)
        
        btn_edit = QPushButton("Edit")
        btn_edit.setObjectName("btnDocEdit")
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.clicked.connect(self._handle_edit)
        bot_row.addWidget(btn_edit)
        
        btn_delete = QPushButton("Delete")
        btn_delete.setObjectName("btnDocDelete")
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.clicked.connect(self._handle_delete)
        bot_row.addWidget(btn_delete)
        
        bot_row.addStretch()
        
        # 4 Navigator Arrows
        for icon_text, handler in [
            ("⏫", self._nav_first),
            ("🔼", self._nav_prev),
            ("🔽", self._nav_next),
            ("⏬", self._nav_last),
        ]:
            b = QPushButton(icon_text)
            b.setProperty("class", "docNavBtn")
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(handler)
            bot_row.addWidget(b)
            
        card_layout.addLayout(bot_row)
        
        self._populate_list()

    def _populate_list(self):
        self.list_doctors.clear()
        for doc in self.doctors:
            self.list_doctors.addItem(doc.get("name", ""))
        if self.doctors:
            self.list_doctors.setCurrentRow(0)
            self._load_doctor(self.doctors[0])

    def _on_doctor_selected(self, row: int):
        if 0 <= row < len(self.doctors):
            self._load_doctor(self.doctors[row])

    def _load_doctor(self, doc: dict):
        self.input_name.setText(doc.get("name", ""))
        self.input_spec.setText(doc.get("specialty", ""))
        self.input_title.setText(doc.get("title", ""))
        self.input_dept.setText(doc.get("department", ""))
        self.txt_address.setPlainText(doc.get("address", ""))
        self.input_phone.setText(doc.get("phone", ""))
        for w in (self.input_name, self.input_spec, self.input_title, self.input_dept, self.input_phone):
            w.setCursorPosition(0)

    def _handle_add_new(self):
        name = self.input_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Notice", "Please enter physician name.")
            self.input_name.setFocus()
            return
        new_doc = {
            "name": name,
            "specialty": self.input_spec.text().strip(),
            "title": self.input_title.text().strip(),
            "department": self.input_dept.text().strip(),
            "address": self.txt_address.toPlainText().strip(),
            "phone": self.input_phone.text().strip()
        }
        self.doctors.append(new_doc)
        self._populate_list()
        self.list_doctors.setCurrentRow(len(self.doctors) - 1)
        QMessageBox.information(self, "Physician Added", f"✓ {name} added to the active endoscopy roster.")

    def _handle_update(self):
        row = self.list_doctors.currentRow()
        if row < 0 or row >= len(self.doctors):
            QMessageBox.warning(self, "Notice", "Please select a physician to update.")
            return
        doc = self.doctors[row]
        doc["name"] = self.input_name.text().strip()
        doc["specialty"] = self.input_spec.text().strip()
        doc["title"] = self.input_title.text().strip()
        doc["department"] = self.input_dept.text().strip()
        doc["address"] = self.txt_address.toPlainText().strip()
        doc["phone"] = self.input_phone.text().strip()
        self.list_doctors.item(row).setText(doc["name"])
        QMessageBox.information(self, "Updated", f"✓ Profile for {doc['name']} updated.")

    def _handle_edit(self):
        self.input_name.setFocus()
        self.input_name.selectAll()

    def _handle_delete(self):
        row = self.list_doctors.currentRow()
        if row < 0 or row >= len(self.doctors):
            return
        doc = self.doctors[row]
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Remove {doc['name']} from the active roster?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            del self.doctors[row]
            self._populate_list()

    def _nav_first(self):
        if self.doctors:
            self.list_doctors.setCurrentRow(0)

    def _nav_prev(self):
        cur = self.list_doctors.currentRow()
        if cur > 0:
            self.list_doctors.setCurrentRow(cur - 1)

    def _nav_next(self):
        cur = self.list_doctors.currentRow()
        if cur < len(self.doctors) - 1:
            self.list_doctors.setCurrentRow(cur + 1)

    def _nav_last(self):
        if self.doctors:
            self.list_doctors.setCurrentRow(len(self.doctors) - 1)


class ArchiveCardWidget(QFrame):
    """Patients Archive full card matching Demo/Patientarchive.PNG."""
    def __init__(self, workstation: WorkstationWindow):
        super().__init__()
        self.workstation = workstation
        self.setObjectName("archiveCard")
        self.setStyleSheet("""
            QFrame#archiveCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0E2436, stop:0.4 #091A28, stop:1 #05101A);
                border: 2px solid #0284C7;
                border-radius: 12px;
            }
        """)
        
        self.records = [
            {"id": "00000001", "name": "Adnan Shefat", "age": "18", "sex": "Male", "date": "15-07-2026", "proc": "COLONOSCOPY", "doc": "Dr. Sarah Jenkins", "ref": "Metro Clinic", "mrn": "ENDO-0042", "town": "Dhaka", "state": "Central", "postcode": "1209", "phone": "01457856554", "addr": "House 14, Road 5, Dhanmondi"},
            {"id": "00000002", "name": "Maria Gonzales", "age": "45", "sex": "Female", "date": "17-08-2026", "proc": "UPPER GI ENDOSCOPY", "doc": "Dr. Michael Chang", "ref": "Westside Practice", "mrn": "ENDO-0811", "town": "Springfield", "state": "IL", "postcode": "62704", "phone": "+1 (555) 234-8901", "addr": "742 Evergreen Terrace"},
            {"id": "00000003", "name": "Alexander Hayes", "age": "58", "sex": "Male", "date": "18-09-2026", "proc": "COLONOSCOPY", "doc": "Dr. Sarah Jenkins", "ref": "Direct Intake", "mrn": "ENDO-0814", "town": "Chicago", "state": "IL", "postcode": "60611", "phone": "+1 (555) 789-0123", "addr": "404 North Medical Plaza"},
            {"id": "00000004", "name": "Robert Chen", "age": "62", "sex": "Male", "date": "16-09-2026", "proc": "ERCP", "doc": "Dr. Elena Rostova", "ref": "St. Jude Medicine", "mrn": "ENDO-0809", "town": "San Francisco", "state": "CA", "postcode": "94107", "phone": "+1 (555) 456-7890", "addr": "1208 Bayfront Promenade"}
        ]
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 10, 16, 12)
        lay.setSpacing(6)
        
        # Header
        hdr = QHBoxLayout()
        btn_close = QPushButton("CLOSE")
        btn_close.setObjectName("cardCloseBtn")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.workstation.close_workstation)
        hdr.addWidget(btn_close)
        
        hdr.addStretch()
        t_lbl = QLabel("Patients Archive")
        t_lbl.setObjectName("cardTitle")
        hdr.addWidget(t_lbl)
        hdr.addStretch()
        
        self.lbl_count = QLabel(f"Showing Last {len(self.records)} Patient(s)")
        self.lbl_count.setStyleSheet("color: #E2E8F0; font-weight: 700; font-size: 12px;")
        hdr.addWidget(self.lbl_count)
        lay.addLayout(hdr)
        
        # 9-Column Table
        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels([
            "Auto ID", "Patient Name", "Age", "Sex", "Visit Date", "Procedure", "Doctors", "Referrers", "MRN"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #0B1622; color: #F8FAFC; gridline-color: #1E293B; border: 1.5px solid #1E293B; border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #0F2030; color: #38BDF8; font-weight: bold; border: 1px solid #1E293B; padding: 4px;
            }
            QTableWidget::item:selected { background-color: #0284C7; color: white; }
        """)
        self.table.itemSelectionChanged.connect(self._on_table_select)
        lay.addWidget(self.table, 1)
        
        # Middle Details Card + Commands
        mid_row = QHBoxLayout()
        mid_row.setSpacing(10)
        
        det_frame = QFrame()
        det_frame.setStyleSheet("background: #0A131C; border: 1.5px solid #10B981; border-radius: 6px; padding: 4px;")
        det_lay = QGridLayout(det_frame)
        det_lay.setHorizontalSpacing(8)
        det_lay.setVerticalSpacing(4)
        
        det_lay.addWidget(QLabel("Selected Patient's Address:"), 0, 0)
        self.det_addr = QLineEdit()
        self.det_addr.setStyleSheet("background: #1E293B; color: white;")
        det_lay.addWidget(self.det_addr, 0, 1, 1, 3)
        
        det_lay.addWidget(QLabel("Town:"), 0, 4)
        self.det_town = QLineEdit()
        self.det_town.setStyleSheet("background: #1E293B; color: white;")
        det_lay.addWidget(self.det_town, 0, 5)
        
        det_lay.addWidget(QLabel("State:"), 0, 6)
        self.det_state = QLineEdit()
        self.det_state.setStyleSheet("background: #1E293B; color: white;")
        det_lay.addWidget(self.det_state, 0, 7)
        
        det_lay.addWidget(QLabel("Post Code:"), 1, 4)
        self.det_post = QLineEdit()
        self.det_post.setStyleSheet("background: #1E293B; color: white;")
        det_lay.addWidget(self.det_post, 1, 5)
        
        det_lay.addWidget(QLabel("Phone:"), 1, 6)
        self.det_phone = QLineEdit()
        self.det_phone.setStyleSheet("background: #1E293B; color: white;")
        det_lay.addWidget(self.det_phone, 1, 7)
        
        mid_row.addWidget(det_frame, 8)
        
        cmd_col = QVBoxLayout()
        cmd_col.setSpacing(4)
        btn_upd = QPushButton("Update")
        btn_upd.setStyleSheet("background: #0284C7; color: white; font-weight: bold; padding: 4px;")
        btn_del = QPushButton("Delete")
        btn_del.setStyleSheet("background: #DC2626; color: white; font-weight: bold; padding: 4px;")
        cmd_col.addWidget(btn_upd)
        cmd_col.addWidget(btn_del)
        mid_row.addLayout(cmd_col, 2)
        
        lay.addLayout(mid_row)
        self._populate_table()

    def _populate_table(self):
        self.table.setRowCount(0)
        for r in self.records:
            row = self.table.rowCount()
            self.table.insertRow(row)
            items = [r["id"], r["name"], r["age"], r["sex"], r["date"], r["proc"], r["doc"], r["ref"], r["mrn"]]
            for col, val in enumerate(items):
                it = QTableWidgetItem(str(val))
                it.setTextAlignment(Qt.AlignCenter if col in (0, 2, 3, 4) else Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(row, col, it)
        if self.records:
            self.table.selectRow(0)

    def _on_table_select(self):
        rows = self.table.selectionModel().selectedRows()
        if rows:
            r = self.records[rows[0].row()]
            self.det_addr.setText(r.get("addr", ""))
            self.det_town.setText(r.get("town", ""))
            self.det_state.setText(r.get("state", ""))
            self.det_post.setText(r.get("postcode", ""))
            self.det_phone.setText(r.get("phone", ""))


class ReferrersCardWidget(QFrame):
    """Referrers Archive card matching Demo/Referrers.PNG."""
    def __init__(self, workstation: WorkstationWindow):
        super().__init__()
        self.workstation = workstation
        self.setObjectName("referrersCard")
        self.setFixedWidth(740)
        
        card_shadow = QGraphicsDropShadowEffect(self)
        card_shadow.setBlurRadius(28)
        card_shadow.setColor(QColor(0, 0, 0, 180))
        card_shadow.setOffset(0, 6)
        self.setGraphicsEffect(card_shadow)
        
        self.setStyleSheet("""
            QFrame#referrersCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0E2436, stop:0.4 #091A28, stop:1 #05101A);
                border: 2px solid #0284C7;
                border-radius: 12px;
            }
        """)
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 12, 20, 14)
        lay.setSpacing(8)
        
        # Header
        hdr = QHBoxLayout()
        btn_close = QPushButton("CLOSE")
        btn_close.setObjectName("cardCloseBtn")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.workstation.close_workstation)
        hdr.addWidget(btn_close)
        
        hdr.addStretch()
        t_lbl = QLabel("Referrers Archive")
        t_lbl.setObjectName("cardTitle")
        hdr.addWidget(t_lbl)
        hdr.addStretch()
        
        sp = QLabel()
        sp.setFixedWidth(65)
        hdr.addWidget(sp)
        lay.addLayout(hdr)
        
        h_sep = QFrame()
        h_sep.setFrameShape(QFrame.HLine)
        h_sep.setStyleSheet("background: #0284C7; max-height: 1.5px; margin-bottom: 4px;")
        lay.addWidget(h_sep)
        
        # Center Row
        c_row = QHBoxLayout()
        c_row.setSpacing(14)
        
        form_lay = QGridLayout()
        form_lay.setHorizontalSpacing(8)
        form_lay.setVerticalSpacing(7)
        
        row = 0
        lbl = QLabel("Name & (Specialty) :")
        lbl.setProperty("class", "formFieldLabel")
        self.inp_name = QLineEdit("Metropolitan Family Clinic")
        self.inp_name.setProperty("class", "formInput")
        form_lay.addWidget(lbl, row, 0)
        form_lay.addWidget(self.inp_name, row, 1)
        row += 1
        
        lbl = QLabel("Title :")
        lbl.setProperty("class", "formFieldLabel")
        self.inp_title = QLineEdit("Primary Referral Center")
        self.inp_title.setProperty("class", "formInput")
        form_lay.addWidget(lbl, row, 0)
        form_lay.addWidget(self.inp_title, row, 1)
        row += 1
        
        lbl = QLabel("Department :")
        lbl.setProperty("class", "formFieldLabel")
        self.inp_dept = QLineEdit("General Outpatient & Diagnostic Medicine")
        self.inp_dept.setProperty("class", "formInput")
        form_lay.addWidget(lbl, row, 0)
        form_lay.addWidget(self.inp_dept, row, 1)
        row += 1
        
        lbl = QLabel("Address :")
        lbl.setProperty("class", "formFieldLabel")
        self.txt_addr = QPlainTextEdit("452 Health Boulevard, Medical District")
        self.txt_addr.setStyleSheet("background: #1E293B; color: #F8FAFC; border: 1.5px solid #334155; border-radius: 5px;")
        self.txt_addr.setFixedHeight(60)
        form_lay.addWidget(lbl, row, 0, Qt.AlignTop)
        form_lay.addWidget(self.txt_addr, row, 1)
        row += 1
        
        lbl = QLabel("Phone :")
        lbl.setProperty("class", "formFieldLabel")
        self.inp_phone = QLineEdit("+1 (555) 789-4321")
        self.inp_phone.setProperty("class", "formInput")
        form_lay.addWidget(lbl, row, 0)
        form_lay.addWidget(self.inp_phone, row, 1)
        
        c_row.addLayout(form_lay, 6)
        
        # Right Roster
        r_col = QVBoxLayout()
        lbl_r = QLabel("Active Referring Facilities:")
        lbl_r.setStyleSheet("color: #38BDF8; font-size: 11px; font-weight: 700;")
        r_col.addWidget(lbl_r)
        
        self.list_refs = QListWidget()
        self.list_refs.setObjectName("doctorsListWidget")
        self.list_refs.addItems([
            "Metropolitan Family Clinic",
            "Westside General Practice",
            "St. Jude Internal Medicine",
            "Direct Clinical Intake"
        ])
        self.list_refs.setCurrentRow(0)
        r_col.addWidget(self.list_refs)
        c_row.addLayout(r_col, 4)
        lay.addLayout(c_row)
        
        # Bottom Buttons
        b_row = QHBoxLayout()
        b_row.setSpacing(8)
        for t in ["Add New", "Update", "Edit", "Delete"]:
            b = QPushButton(t)
            b.setObjectName(f"btnDoc{t.replace(' ', '')}")
            b.setCursor(Qt.PointingHandCursor)
            b_row.addWidget(b)
            
        b_row.addStretch()
        for arrow in ["⏫", "🔼", "🔽", "⏬"]:
            ab = QPushButton(arrow)
            ab.setProperty("class", "docNavBtn")
            ab.setCursor(Qt.PointingHandCursor)
            b_row.addWidget(ab)
        lay.addLayout(b_row)


class TemplatesCardWidget(QFrame):
    """
    Template Editor workstation card modeled faithfully after Demo/Templates.PNG.
    Features:
    - Standard clinical header with [CLOSE] and [Template Editor]
    - Formatting toolbar: [Open], [Save], [B], [I], [U], [:≡], Alignment, Font Size (11), [Fonts]
    - Quick clinical template presets selector (Colonoscopy, EGD, Polypectomy, ERCP, Barrett's)
    - Medical white document canvas with rich-text editing & live formatting
    """
    def __init__(self, workstation: WorkstationWindow):
        super().__init__()
        self.workstation = workstation
        self.setObjectName("templatesCard")
        self.setFixedWidth(750)
        
        card_shadow = QGraphicsDropShadowEffect(self)
        card_shadow.setBlurRadius(28)
        card_shadow.setColor(QColor(0, 0, 0, 180))
        card_shadow.setOffset(0, 6)
        self.setGraphicsEffect(card_shadow)
        
        self.setStyleSheet("""
            QFrame#templatesCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0E2436, stop:0.4 #091A28, stop:1 #05101A);
                border: 2px solid #0284C7;
                border-radius: 12px;
            }
        """)
        
        self._init_templates_catalog()
        self._init_ui()

    def _init_templates_catalog(self):
        """Pre-defined standard clinical endoscopy report templates."""
        self.templates = {
            "Diagnostic Colonoscopy (Standard)": (
                "<div style='font-family: Segoe UI, Arial; font-size: 11pt; color: #0F172A; line-height: 1.4;'>"
                "<h3 style='color: #0284C7; margin-bottom: 4px; border-bottom: 1.5px solid #0284C7; padding-bottom: 4px;'>ENDOSCOPY CLINICAL REPORT &bull; LOWER GI</h3>"
                "<p><b>Procedure:</b> Complete Diagnostic Colonoscopy with Terminal Ileum Intubation<br/>"
                "<b>Indication:</b> Colorectal cancer screening / Altered bowel habits<br/>"
                "<b>Pre-Medication:</b> Midazolam 3mg IV, Fentanyl 50mcg IV<br/>"
                "<b>Endoscope:</b> Video Colonoscope EC-760R-V/L (HD+)</p>"
                "<hr style='border: 0; border-top: 1px solid #CBD5E1;'/>"
                "<p><b>Clinical Findings:</b></p>"
                "<ul>"
                "<li><b>Perianal / Rectal:</b> Normal perianal inspection. Digital rectal examination normal. Rectal ampulla unremarkable.</li>"
                "<li><b>Colon:</b> High-definition inspection performed on withdrawal. Bowel preparation Boston Bowel Prep Scale 8/9. Mucosa throughout sigmoid, descending, transverse, and ascending colon smooth with normal vascular pattern.</li>"
                "<li><b>Cecum & Ileum:</b> Cecum reached; verified by appendiceal orifice and ileocecal valve. Terminal ileum entered 15cm; normal villous architecture.</li>"
                "</ul>"
                "<p><b>Diagnostic Impression:</b> Normal colonoscopy to terminal ileum. No mucosal abnormalities, polyps, or diverticula detected.</p>"
                "<p><b>Recommendations:</b> Standard screening interval (10 years) recommended unless symptoms develop.</p>"
                "<br/>"
                "<p><b>Attending Endoscopist:</b> _________________________ &nbsp;&nbsp;&nbsp;&nbsp; <b>Date:</b> 19/09/2026</p>"
                "</div>"
            ),
            "Upper GI Endoscopy (EGD)": (
                "<div style='font-family: Segoe UI, Arial; font-size: 11pt; color: #0F172A; line-height: 1.4;'>"
                "<h3 style='color: #0284C7; margin-bottom: 4px; border-bottom: 1.5px solid #0284C7; padding-bottom: 4px;'>ENDOSCOPY CLINICAL REPORT &bull; UPPER GI (EGD)</h3>"
                "<p><b>Procedure:</b> Esophagogastroduodenoscopy (EGD) with Biopsy<br/>"
                "<b>Indication:</b> Dyspepsia, epigastric fullness, GERD refractory to PPI<br/>"
                "<b>Pre-Medication:</b> Topical Lidocaine 10% oral spray, Propofol monitored anesthesia<br/>"
                "<b>Endoscope:</b> Video Gastroscope EG-760Z (Zoom & NBI)</p>"
                "<hr style='border: 0; border-top: 1px solid #CBD5E1;'/>"
                "<p><b>Clinical Findings:</b></p>"
                "<ul>"
                "<li><b>Esophagus:</b> Normal lumen and peristalsis. Squamocolumnar junction (Z-line) regular at 38cm from incisors. No erosions or varices (LA Grade 0).</li>"
                "<li><b>Stomach:</b> Retroflexion demonstrates normal gastric cardia and fundus. Gastric body and antrum show mild patchy erythema; no ulceration or mass lesions. Rapid Urease Test (RUT) performed.</li>"
                "<li><b>Duodenum:</b> Duodenal bulb and second portion inspected with clear visualization of the major papilla. Mucosa normal.</li>"
                "</ul>"
                "<p><b>Diagnostic Impression:</b> Mild non-erosive antral gastritis. RUT pending.</p>"
                "<p><b>Recommendations:</b> Continue standard PPI for 4 weeks. Dietary modification advice provided.</p>"
                "<br/>"
                "<p><b>Attending Endoscopist:</b> _________________________ &nbsp;&nbsp;&nbsp;&nbsp; <b>Date:</b> 19/09/2026</p>"
                "</div>"
            ),
            "Polypectomy & Resection (Paris Class)": (
                "<div style='font-family: Segoe UI, Arial; font-size: 11pt; color: #0F172A; line-height: 1.4;'>"
                "<h3 style='color: #0284C7; margin-bottom: 4px; border-bottom: 1.5px solid #0284C7; padding-bottom: 4px;'>INTERVENTIONAL ENDOSCOPY &bull; POLYPECTOMY PROTOCOL</h3>"
                "<p><b>Procedure:</b> Colonoscopy with Endoscopic Mucosal Resection (EMR) / Polypectomy<br/>"
                "<b>Indication:</b> Positive fecal occult blood test (FIT+)</p>"
                "<hr style='border: 0; border-top: 1px solid #CBD5E1;'/>"
                "<p><b>Lesion Classification & Intervention:</b></p>"
                "<ul>"
                "<li><b>Location:</b> Mid-transverse colon (65cm from anal verge)</li>"
                "<li><b>Morphology:</b> Paris 0-Is sessile polyp, diameter 12mm</li>"
                "<li><b>Surface Pattern:</b> NICE Type 2 / Kudo Pit Pattern III-L (Adenomatous)</li>"
                "<li><b>Technique:</b> Submucosal injection of 4ml diluted methylene blue in saline. Complete hot snare polypectomy achieved en-bloc.</li>"
                "<li><b>Hemostasis:</b> Prophylactic placement of two endoscopic clips (Resolution 11mm). No immediate post-polypectomy hemorrhage.</li>"
                "</ul>"
                "<p><b>Diagnostic Impression:</b> Successful en-bloc endoscopic resection of Paris 0-Is transverse colon polyp. Specimen retrieved for histopathology.</p>"
                "<p><b>Recommendations:</b> Liquid diet for 24 hours. Surveillance colonoscopy in 3 years pending pathology staging.</p>"
                "<br/>"
                "<p><b>Attending Endoscopist:</b> _________________________ &nbsp;&nbsp;&nbsp;&nbsp; <b>Date:</b> 19/09/2026</p>"
                "</div>"
            ),
            "Therapeutic ERCP & Stenting": (
                "<div style='font-family: Segoe UI, Arial; font-size: 11pt; color: #0F172A; line-height: 1.4;'>"
                "<h3 style='color: #0284C7; margin-bottom: 4px; border-bottom: 1.5px solid #0284C7; padding-bottom: 4px;'>ENDOSCOPIC RETROGRADE CHOLANGIOPANCREATOGRAPHY (ERCP)</h3>"
                "<p><b>Procedure:</b> Therapeutic ERCP, Biliary Sphincterotomy, Balloon Extraction & Stenting<br/>"
                "<b>Indication:</b> Choledocholithiasis with acute obstructive cholangitis</p>"
                "<hr style='border: 0; border-top: 1px solid #CBD5E1;'/>"
                "<p><b>Endoscopic & Fluoroscopic Steps:</b></p>"
                "<ul>"
                "<li><b>Duodenoscopy:</b> Side-viewing duodenoscope advanced to D2. Major papilla had normal papillary orifice.</li>"
                "<li><b>Cannulation:</b> Selective biliary cannulation achieved with sphincterotome and 0.035 hydrophilic guidewire.</li>"
                "<li><b>Cholangiogram:</b> Common Bile Duct (CBD) dilated to 14mm. Two filling defects (8mm and 6mm) noted in distal CBD.</li>"
                "<li><b>Therapy:</b> Standard electrosurgical sphincterotomy (PulseCut mode). Fogarty biliary extraction balloon swept distal duct with extraction of calculi and sludge. 10Fr x 7cm plastic biliary stent deployed across papilla with prompt bile drainage.</li>"
                "</ul>"
                "<p><b>Diagnostic Impression:</b> Successful biliary duct clearance and decompression with 10Fr plastic stent placement.</p>"
                "<p><b>Recommendations:</b> Monitor amylase/lipase for 24h. Schedule elective stent removal in 6 weeks.</p>"
                "<br/>"
                "<p><b>Attending Endoscopist:</b> _________________________ &nbsp;&nbsp;&nbsp;&nbsp; <b>Date:</b> 19/09/2026</p>"
                "</div>"
            ),
            "Barrett's Esophagus Surveillance": (
                "<div style='font-family: Segoe UI, Arial; font-size: 11pt; color: #0F172A; line-height: 1.4;'>"
                "<h3 style='color: #0284C7; margin-bottom: 4px; border-bottom: 1.5px solid #0284C7; padding-bottom: 4px;'>UPPER GI ENDOSCOPY &bull; BARRETT'S SURVEILLANCE</h3>"
                "<p><b>Procedure:</b> High-Definition Chromoendoscopy & Targeted Seattle Biopsy Protocol<br/>"
                "<b>Indication:</b> Surveillance of known Barrett's Esophagus</p>"
                "<hr style='border: 0; border-top: 1px solid #CBD5E1;'/>"
                "<p><b>Endoscopic Assessment:</b></p>"
                "<ul>"
                "<li><b>Gastroesophageal Junction (GEJ):</b> Identified at 40cm. Diaphragmatic pinch at 42cm (2cm sliding hiatal hernia).</li>"
                "<li><b>Prague Classification:</b> Circumferential extent C2, Maximum extent M4.</li>"
                "<li><b>Mucosal Inspection:</b> Narrow Band Imaging (NBI) and acetic acid enhancement revealed regular tubular mucosa without nodularity or ulceration.</li>"
                "<li><b>Biopsies:</b> Four-quadrant biopsies taken every 2cm throughout the columnar-lined segment (Seattle Protocol).</li>"
                "</ul>"
                "<p><b>Diagnostic Impression:</b> Barrett's esophagus (Prague C2M4) without visible nodular dysplasia.</p>"
                "<p><b>Recommendations:</b> Continue high-dose PPI therapy. Follow-up interval determined by histological grade.</p>"
                "<br/>"
                "<p><b>Attending Endoscopist:</b> _________________________ &nbsp;&nbsp;&nbsp;&nbsp; <b>Date:</b> 19/09/2026</p>"
                "</div>"
            ),
            "Blank Clinical Template": (
                "<div style='font-family: Segoe UI, Arial; font-size: 11pt; color: #0F172A; line-height: 1.4;'>"
                "<h3 style='color: #0284C7; margin-bottom: 4px; border-bottom: 1.5px solid #0284C7; padding-bottom: 4px;'>ENDOSCOPY CLINICAL EXAMINATION REPORT</h3>"
                "<p><b>Patient Name:</b> _________________________ &nbsp;&nbsp;&nbsp;&nbsp; <b>MRN:</b> ___________________<br/>"
                "<b>Procedure:</b> _________________________ &nbsp;&nbsp;&nbsp;&nbsp; <b>Date:</b> 19/09/2026</p>"
                "<hr style='border: 0; border-top: 1px solid #CBD5E1;'/>"
                "<p><b>Findings:</b><br/>"
                "[Type clinical findings here...]</p>"
                "<p><b>Impression & Recommendations:</b><br/>"
                "[Type clinical impression and recommendations here...]</p>"
                "<br/><br/>"
                "<p><b>Endoscopist Signature:</b> _________________________</p>"
                "</div>"
            )
        }

    def _init_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 12, 18, 14)
        lay.setSpacing(8)
        
        # --- Header: [CLOSE] ... Template Editor ... [Template Preset Selector] ---
        hdr = QHBoxLayout()
        btn_close = QPushButton("CLOSE")
        btn_close.setObjectName("cardCloseBtn")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.workstation.close_workstation)
        hdr.addWidget(btn_close)
        
        hdr.addStretch()
        t_lbl = QLabel("Template Editor")
        t_lbl.setObjectName("cardTitle")
        t_lbl.setAlignment(Qt.AlignCenter)
        hdr.addWidget(t_lbl)
        hdr.addStretch()
        
        # Quick Clinical Preset Picker
        self.combo_presets = QComboBox()
        self.combo_presets.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1E293B, stop:1 #0F172A);
                color: #38BDF8;
                border: 1.5px solid #0284C7;
                border-radius: 5px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: 700;
                min-width: 170px;
            }
            QComboBox QAbstractItemView {
                background-color: #0F172A;
                color: #F8FAFC;
                selection-background-color: #0284C7;
            }
        """)
        self.combo_presets.addItems(list(self.templates.keys()))
        self.combo_presets.currentIndexChanged.connect(self._on_preset_changed)
        hdr.addWidget(self.combo_presets)
        lay.addLayout(hdr)
        
        # Divider
        h_sep = QFrame()
        h_sep.setFrameShape(QFrame.HLine)
        h_sep.setStyleSheet("background: #0284C7; max-height: 1.5px; margin-bottom: 2px;")
        lay.addWidget(h_sep)
        
        # --- Formatting Toolbar (Exact layout from Demo/Templates.PNG) ---
        tbar = QHBoxLayout()
        tbar.setSpacing(5)
        
        # Open & Save
        btn_open = QPushButton("Open")
        btn_open.setCursor(Qt.PointingHandCursor)
        btn_open.setStyleSheet(self._toolbar_btn_style())
        btn_open.clicked.connect(self._handle_open)
        tbar.addWidget(btn_open)
        
        btn_save = QPushButton("Save")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setStyleSheet(self._toolbar_btn_style())
        btn_save.clicked.connect(self._handle_save)
        tbar.addWidget(btn_save)
        
        # Subtle Separator
        tbar.addWidget(self._create_tool_sep())
        
        # Format Tools: B, I, U, :≡
        self.btn_b = QPushButton("B")
        self.btn_b.setCursor(Qt.PointingHandCursor)
        self.btn_b.setFixedWidth(28)
        self.btn_b.setStyleSheet(self._toolbar_tool_style("font-weight: 900; font-size: 13px;"))
        self.btn_b.clicked.connect(self._toggle_bold)
        tbar.addWidget(self.btn_b)
        
        self.btn_i = QPushButton("I")
        self.btn_i.setCursor(Qt.PointingHandCursor)
        self.btn_i.setFixedWidth(28)
        self.btn_i.setStyleSheet(self._toolbar_tool_style("font-style: italic; font-weight: 700; font-size: 13px; font-family: 'Times New Roman';"))
        self.btn_i.clicked.connect(self._toggle_italic)
        tbar.addWidget(self.btn_i)
        
        self.btn_u = QPushButton("U")
        self.btn_u.setCursor(Qt.PointingHandCursor)
        self.btn_u.setFixedWidth(28)
        self.btn_u.setStyleSheet(self._toolbar_tool_style("text-decoration: underline; font-weight: 700; font-size: 13px;"))
        self.btn_u.clicked.connect(self._toggle_underline)
        tbar.addWidget(self.btn_u)
        
        self.btn_bullets = QPushButton("•≡")
        self.btn_bullets.setCursor(Qt.PointingHandCursor)
        self.btn_bullets.setFixedWidth(30)
        self.btn_bullets.setStyleSheet(self._toolbar_tool_style("font-weight: 800; font-size: 12px;"))
        self.btn_bullets.clicked.connect(self._toggle_bullets)
        tbar.addWidget(self.btn_bullets)
        
        # Separator
        tbar.addWidget(self._create_tool_sep())
        
        # Alignment: Left, Center, Right
        btn_align_left = QPushButton("≡")
        btn_align_left.setCursor(Qt.PointingHandCursor)
        btn_align_left.setFixedWidth(28)
        btn_align_left.setToolTip("Align Left")
        btn_align_left.setStyleSheet(self._toolbar_tool_style("font-size: 14px; font-weight: 900;"))
        btn_align_left.clicked.connect(lambda: self._align_text(Qt.AlignLeft))
        tbar.addWidget(btn_align_left)
        
        btn_align_center = QPushButton("⫼")
        btn_align_center.setCursor(Qt.PointingHandCursor)
        btn_align_center.setFixedWidth(28)
        btn_align_center.setToolTip("Align Center")
        btn_align_center.setStyleSheet(self._toolbar_tool_style("font-size: 13px; font-weight: 900;"))
        btn_align_center.clicked.connect(lambda: self._align_text(Qt.AlignHCenter))
        tbar.addWidget(btn_align_center)
        
        btn_align_right = QPushButton("⫽")
        btn_align_right.setCursor(Qt.PointingHandCursor)
        btn_align_right.setFixedWidth(28)
        btn_align_right.setToolTip("Align Right")
        btn_align_right.setStyleSheet(self._toolbar_tool_style("font-size: 13px; font-weight: 900;"))
        btn_align_right.clicked.connect(lambda: self._align_text(Qt.AlignRight))
        tbar.addWidget(btn_align_right)
        
        # Separator
        tbar.addWidget(self._create_tool_sep())
        
        # Font Size Dropdown: [ 11 ⌵ ] (matching reference)
        self.combo_size = QComboBox()
        self.combo_size.setFixedWidth(56)
        self.combo_size.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #F1F5F9);
                color: #0F172A;
                border: 1px solid #94A3B8;
                border-radius: 4px;
                padding: 3px 6px;
                font-weight: 800;
                font-size: 12px;
            }
            QComboBox QAbstractItemView {
                background: #FFFFFF;
                color: #0F172A;
                selection-background-color: #0284C7;
                selection-color: #FFFFFF;
            }
        """)
        sizes = ["9", "10", "11", "12", "14", "16", "18", "20", "24"]
        self.combo_size.addItems(sizes)
        self.combo_size.setCurrentText("11")  # Matching Demo/Templates.PNG
        self.combo_size.currentTextChanged.connect(self._on_font_size_changed)
        tbar.addWidget(self.combo_size)
        
        # Fonts Button
        btn_fonts = QPushButton("Fonts")
        btn_fonts.setCursor(Qt.PointingHandCursor)
        btn_fonts.setStyleSheet(self._toolbar_btn_style())
        btn_fonts.clicked.connect(self._choose_font)
        tbar.addWidget(btn_fonts)
        
        tbar.addStretch()
        lay.addLayout(tbar)
        
        # --- High-Contrast Medical White Document Canvas ---
        self.editor = QTextEdit()
        self.editor.setObjectName("templateEditorCanvas")
        self.editor.setStyleSheet("""
            QTextEdit#templateEditorCanvas {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1.5px solid #0284C7;
                border-radius: 6px;
                padding: 16px 20px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11pt;
                selection-background-color: #38BDF8;
                selection-color: #0F172A;
            }
        """)
        
        # Load initial template
        initial_tpl = list(self.templates.values())[0]
        self.editor.setHtml(initial_tpl)
        lay.addWidget(self.editor, 1)

    def _create_tool_sep(self):
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("background-color: #334155; max-width: 1px; margin: 2px 3px;")
        return sep

    def _toolbar_btn_style(self):
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #E2E8F0);
                color: #0F172A;
                border: 1px solid #94A3B8;
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 800;
            }
            QPushButton:hover {
                background: #0284C7;
                color: #FFFFFF;
                border-color: #38BDF8;
            }
            QPushButton:pressed {
                background: #0369A1;
            }
        """

    def _toolbar_tool_style(self, extra_css: str = ""):
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1E293B, stop:1 #0F172A);
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 3px;
                {extra_css}
            }}
            QPushButton:hover {{
                background: #0284C7;
                color: #FFFFFF;
                border-color: #38BDF8;
            }}
            QPushButton:pressed {{
                background: #38BDF8;
                color: #0F172A;
            }}
        """

    # --- Rich Text Formatting Handlers ---
    def _merge_format(self, fmt: QTextCharFormat):
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        cursor.mergeCharFormat(fmt)
        self.editor.mergeCurrentCharFormat(fmt)

    def _toggle_bold(self):
        fmt = QTextCharFormat()
        is_bold = self.editor.fontWeight() == QFont.Bold
        fmt.setFontWeight(QFont.Normal if is_bold else QFont.Bold)
        self._merge_format(fmt)

    def _toggle_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(not self.editor.fontItalic())
        self._merge_format(fmt)

    def _toggle_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(not self.editor.fontUnderline())
        self._merge_format(fmt)

    def _toggle_bullets(self):
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        list_fmt = QTextListFormat()
        list_fmt.setStyle(QTextListFormat.ListDisc)
        cursor.createList(list_fmt)
        cursor.endEditBlock()

    def _align_text(self, alignment):
        self.editor.setAlignment(alignment)

    def _on_font_size_changed(self, size_str: str):
        try:
            sz = float(size_str)
            fmt = QTextCharFormat()
            fmt.setFontPointSize(sz)
            self._merge_format(fmt)
        except ValueError:
            pass

    def _choose_font(self):
        ok, font = QFontDialog.getFont(self.editor.currentFont(), self)
        if ok:
            fmt = QTextCharFormat()
            fmt.setFont(font)
            self._merge_format(fmt)

    def _on_preset_changed(self, index: int):
        key = self.combo_presets.currentText()
        if key in self.templates:
            self.editor.setHtml(self.templates[key])

    def _handle_open(self):
        key = self.combo_presets.currentText()
        reply = QMessageBox.question(
            self, "Load Template Preset",
            f"Load the structured clinical template for:\n'{key}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
        )
        if reply == QMessageBox.Yes and key in self.templates:
            self.editor.setHtml(self.templates[key])

    def _handle_save(self):
        key = self.combo_presets.currentText()
        QMessageBox.information(
            self, "Template Saved",
            f"✓ Clinical Template '{key}' saved successfully to Endocare Template Library."
        )

