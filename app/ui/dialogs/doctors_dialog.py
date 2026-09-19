import os

from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QListWidget, QListWidgetItem,
    QPlainTextEdit, QCheckBox, QMessageBox, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QColor



class DoctorsDialog(QDialog):
    """
    Doctors Archive Workstation.
    Full clinical workspace modeled after the PANORAMA reference design,
    featuring the two-column Doctors Archive card and the persistent right workflow sidebar.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Endocare • Clinical Endoscopists & Doctors Archive")
        self.resize(1366, 730)
        self.setMinimumSize(1100, 680)
        
        self.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self._assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../assets"))
        
        self._init_data()
        self._init_ui()

    def _init_data(self):
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
                "specialty": "Therapeutic Colonoscopy & ERCP Interventions",
                "title": "Associate Professor & Attending Endoscopist, MD",
                "department": "Interventional Endoscopy Suite 1",
                "address": "Metropolitan Hospital, Tower B, Level 3",
                "phone": "+1 (555) 234-5678"
            },
            {
                "name": "Dr. Elena Rostova",
                "specialty": "Diagnostic & Therapeutic Upper/Lower GI Endoscopy",
                "title": "Consultant Gastroenterologist, MD, PhD",
                "department": "Department of Digestive Diseases",
                "address": "Clinical Pavillion 2, Ambulatory Surgery Center",
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

    def _init_ui(self):
        root = QFrame(self)
        root.setObjectName("doctorsWorkstationRoot")
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(root)
        
        workspace_layout = QHBoxLayout(root)
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(0)
        
        # =========================================================================
        # 1. CENTER CLINICAL CANVAS (Holds the centered Doctors Archive Card)
        # =========================================================================
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(40, 20, 40, 20)
        canvas_layout.setAlignment(Qt.AlignCenter)
        
        # Elevated Doctors Card
        card = QFrame()
        card.setObjectName("doctorsCard")
        card.setFixedWidth(760)
        
        card_shadow = QGraphicsDropShadowEffect(self)
        card_shadow.setBlurRadius(32)
        card_shadow.setColor(QColor(0, 0, 0, 200))
        card_shadow.setOffset(0, 8)
        card.setGraphicsEffect(card_shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 16, 22, 18)
        card_layout.setSpacing(12)
        
        # --- Card Header: [CLOSE] ... Doctors Archive ---
        card_header = QHBoxLayout()
        card_header.setContentsMargins(0, 0, 0, 2)
        
        btn_close = QPushButton("CLOSE")
        btn_close.setObjectName("cardCloseBtn")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.reject)
        card_header.addWidget(btn_close)
        
        card_header.addStretch()
        
        title_lbl = QLabel("Doctors Archive")
        title_lbl.setObjectName("cardTitle")
        title_lbl.setAlignment(Qt.AlignCenter)
        card_header.addWidget(title_lbl)
        
        card_header.addStretch()
        # Invisible spacer matching close button width for symmetrical centering
        spacer = QLabel()
        spacer.setFixedWidth(70)
        card_header.addWidget(spacer)
        
        card_layout.addLayout(card_header)
        
        # Header separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 transparent, stop:0.2 #0284C7, stop:0.5 #38BDF8, stop:0.8 #0284C7, stop:1 transparent);
            max-height: 1.5px;
            margin-bottom: 4px;
        """)
        card_layout.addWidget(sep)
        
        # --- Card Body: Left Details Form & Right Directory List ---
        body_layout = QHBoxLayout()
        body_layout.setSpacing(16)
        
        # === Left Form (6 Fields) ===
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(10)
        form_layout.setVerticalSpacing(10)
        
        # 1. Doctor Name
        lbl_name = QLabel("Doctor Name :")
        lbl_name.setProperty("class", "formFieldLabel")
        self.input_name = QLineEdit()
        self.input_name.setProperty("class", "formInput")
        self.input_name.setPlaceholderText("Enter physician name...")
        form_layout.addWidget(lbl_name, 0, 0)
        form_layout.addWidget(self.input_name, 0, 1)
        
        # 2. Specialty
        lbl_spec = QLabel("Specialty :")
        lbl_spec.setProperty("class", "formFieldLabel")
        self.input_spec = QLineEdit()
        self.input_spec.setProperty("class", "formInput")
        self.input_spec.setPlaceholderText("e.g., Gastroenterology & Advanced Endoscopy")
        form_layout.addWidget(lbl_spec, 1, 0)
        form_layout.addWidget(self.input_spec, 1, 1)
        
        # 3. Title
        lbl_title_field = QLabel("Title :")
        lbl_title_field.setProperty("class", "formFieldLabel")
        self.input_title = QLineEdit()
        self.input_title.setProperty("class", "formInput")
        self.input_title.setPlaceholderText("e.g., Senior Consultant, MD, FACG")
        form_layout.addWidget(lbl_title_field, 2, 0)
        form_layout.addWidget(self.input_title, 2, 1)
        
        # 4. Department
        lbl_dept = QLabel("Department :")
        lbl_dept.setProperty("class", "formFieldLabel")
        self.input_dept = QLineEdit()
        self.input_dept.setProperty("class", "formInput")
        self.input_dept.setPlaceholderText("e.g., Endoscopy Suite & Digestive Health")
        form_layout.addWidget(lbl_dept, 3, 0)
        form_layout.addWidget(self.input_dept, 3, 1)
        
        # 5. Address
        lbl_addr = QLabel("Address :")
        lbl_addr.setProperty("class", "formFieldLabel")
        self.txt_address = QPlainTextEdit()
        self.txt_address.setFixedHeight(48)
        self.txt_address.setStyleSheet("background-color: #1E293B; color: #F8FAFC; border: 1.5px solid #334155; border-radius: 5px; font-size: 12px;")
        self.txt_address.setPlaceholderText("Clinic or chamber location...")
        form_layout.addWidget(lbl_addr, 4, 0, Qt.AlignTop)
        form_layout.addWidget(self.txt_address, 4, 1)
        
        # 6. Phone
        lbl_phone = QLabel("Phone :")
        lbl_phone.setProperty("class", "formFieldLabel")
        self.input_phone = QLineEdit()
        self.input_phone.setProperty("class", "formInput")
        self.input_phone.setPlaceholderText("+1 (555) 000-0000")
        form_layout.addWidget(lbl_phone, 5, 0)
        form_layout.addWidget(self.input_phone, 5, 1)
        
        body_layout.addLayout(form_layout, stretch=6)
        
        # === Right Directory List ===
        list_container = QVBoxLayout()
        list_container.setSpacing(4)
        lbl_list_header = QLabel("Active Physicians Roster:")
        lbl_list_header.setStyleSheet("color: #38BDF8; font-size: 11px; font-weight: 700;")
        list_container.addWidget(lbl_list_header)
        
        self.list_doctors = QListWidget()
        self.list_doctors.setObjectName("doctorsListWidget")
        self.list_doctors.currentRowChanged.connect(self._on_doctor_selected)
        list_container.addWidget(self.list_doctors)
        
        body_layout.addLayout(list_container, stretch=4)
        card_layout.addLayout(body_layout)
        
        # --- Card Footer: Action Buttons & Navigation Arrows ---
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 8, 0, 0)
        footer_layout.setSpacing(8)
        
        # Left CRUD Buttons
        self.btn_add_new = QPushButton("Add New")
        self.btn_add_new.setObjectName("btnDocAddNew")
        self.btn_add_new.setShortcut("Alt+A")
        self.btn_add_new.setToolTip("Add New Physician (Alt+A)")
        self.btn_add_new.setCursor(Qt.PointingHandCursor)
        self.btn_add_new.clicked.connect(self._handle_add_new)
        footer_layout.addWidget(self.btn_add_new)
        
        self.btn_update = QPushButton("Update")
        self.btn_update.setObjectName("btnDocUpdate")
        self.btn_update.setShortcut("Alt+U")
        self.btn_update.setToolTip("Update Physician Profile (Alt+U)")
        self.btn_update.setCursor(Qt.PointingHandCursor)
        self.btn_update.clicked.connect(self._handle_update)
        footer_layout.addWidget(self.btn_update)
        
        self.btn_edit = QPushButton("Edit")
        self.btn_edit.setObjectName("btnDocEdit")
        self.btn_edit.setShortcut("Alt+E")
        self.btn_edit.setToolTip("Edit Profile (Alt+E)")
        self.btn_edit.setCursor(Qt.PointingHandCursor)
        self.btn_edit.clicked.connect(lambda: self.input_name.setFocus())
        footer_layout.addWidget(self.btn_edit)
        
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setObjectName("btnDocDelete")
        self.btn_delete.setShortcut("Alt+D")
        self.btn_delete.setToolTip("Delete Physician Profile (Alt+D)")
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.clicked.connect(self._handle_delete)
        footer_layout.addWidget(self.btn_delete)
        
        footer_layout.addStretch()
        
        # Right Record Navigator Arrows
        btn_first = QPushButton("⏫")
        btn_first.setProperty("class", "docNavBtn")
        btn_first.setToolTip("Jump to First Physician")
        btn_first.setCursor(Qt.PointingHandCursor)
        btn_first.clicked.connect(self._nav_first)
        footer_layout.addWidget(btn_first)
        
        btn_prev = QPushButton("🔼")
        btn_prev.setProperty("class", "docNavBtn")
        btn_prev.setToolTip("Previous Physician")
        btn_prev.setCursor(Qt.PointingHandCursor)
        btn_prev.clicked.connect(self._nav_prev)
        footer_layout.addWidget(btn_prev)
        
        btn_next = QPushButton("🔽")
        btn_next.setProperty("class", "docNavBtn")
        btn_next.setToolTip("Next Physician")
        btn_next.setCursor(Qt.PointingHandCursor)
        btn_next.clicked.connect(self._nav_next)
        footer_layout.addWidget(btn_next)
        
        btn_last = QPushButton("⏬")
        btn_last.setProperty("class", "docNavBtn")
        btn_last.setToolTip("Jump to Last Physician")
        btn_last.setCursor(Qt.PointingHandCursor)
        btn_last.clicked.connect(self._nav_last)
        footer_layout.addWidget(btn_last)
        
        card_layout.addLayout(footer_layout)
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
        
        # Divider
        s_line = QFrame()
        s_line.setFrameShape(QFrame.HLine)
        s_line.setStyleSheet("background-color: #1E293B; max-height: 1px; margin-bottom: 4px;")
        side_layout.addWidget(s_line)
        
        # Primary Clinical Navigation Buttons
        btn_nav_patient = QPushButton("New Patient")
        btn_nav_patient.setProperty("class", "sideNavBtn")
        btn_nav_patient.setCursor(Qt.PointingHandCursor)
        btn_nav_patient.clicked.connect(self._open_new_patient)
        side_layout.addWidget(btn_nav_patient)
        
        btn_nav_archive = QPushButton("Patients Archive")
        btn_nav_archive.setProperty("class", "sideNavBtn")
        btn_nav_archive.setCursor(Qt.PointingHandCursor)
        btn_nav_archive.clicked.connect(self._open_archive)
        side_layout.addWidget(btn_nav_archive)
        
        btn_nav_doctors = QPushButton("Doctors")
        btn_nav_doctors.setProperty("class", "sideNavActiveBtn")  # Highlighted active tab
        btn_nav_doctors.setCursor(Qt.PointingHandCursor)
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
        
        # Report & Workflow Actions Group
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
        btn_capture.clicked.connect(lambda: QMessageBox.information(self, "Live Stream", "Returning to USB2 Live Endoscopy Viewport..."))
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
        
        # Bottom HOME & EXIT Controls
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
        
        # Initial Population of List
        self._populate_list()

    def _populate_list(self):
        self.list_doctors.clear()
        for doc in self.doctors:
            self.list_doctors.addItem(doc.get("name", ""))
        if self.doctors:
            self.list_doctors.setCurrentRow(0)
            self._load_doctor_details(self.doctors[0])

    def _on_doctor_selected(self, row: int):
        if 0 <= row < len(self.doctors):
            self._load_doctor_details(self.doctors[row])

    def _load_doctor_details(self, doc: dict):
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
            QMessageBox.warning(self, "Notice", "Please select a physician from the roster to update.")
            return
            
        doc = self.doctors[row]
        doc["name"] = self.input_name.text().strip()
        doc["specialty"] = self.input_spec.text().strip()
        doc["title"] = self.input_title.text().strip()
        doc["department"] = self.input_dept.text().strip()
        doc["address"] = self.txt_address.toPlainText().strip()
        doc["phone"] = self.input_phone.text().strip()
        
        # Update list item text
        self.list_doctors.item(row).setText(doc["name"])
        QMessageBox.information(self, "Profile Updated", f"✓ Physician profile for {doc['name']} updated successfully.")

    def _handle_delete(self):
        row = self.list_doctors.currentRow()
        if row < 0 or row >= len(self.doctors):
            QMessageBox.warning(self, "Notice", "Please select a physician to delete.")
            return
            
        doc = self.doctors[row]
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to remove {doc['name']} from the clinical roster?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            del self.doctors[row]
            self._populate_list()

    # --- Navigation Helpers ---
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

    # --- Sidebar Navigation Handlers ---
    def _open_new_patient(self):
        from app.ui.dialogs.new_patient_dialog import NewPatientDialog
        dlg = NewPatientDialog(self)
        dlg.exec()

    def _open_archive(self):
        from app.ui.dialogs.archive_dialog import ArchiveDialog
        dlg = ArchiveDialog(self)
        dlg.exec()

    def _open_referrers(self):
        from app.ui.dialogs.referrers_dialog import ReferrersDialog
        dlg = ReferrersDialog(self)
        dlg.exec()

    def _open_templates(self):
        from app.ui.dialogs.templates_dialog import TemplatesDialog
        dlg = TemplatesDialog(self)
        dlg.exec()

    def _confirm_exit(self):
        reply = QMessageBox.question(
            self, "Exit Endocare",
            "Are you sure you want to terminate Endocare?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.reject()
