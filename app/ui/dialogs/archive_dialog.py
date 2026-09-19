import os
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QComboBox, QDateEdit, QPushButton, QRadioButton,
    QButtonGroup, QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QCheckBox, QMessageBox, QGraphicsDropShadowEffect, QPlainTextEdit,
    QAbstractItemView, QApplication
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QPixmap


class DiagnosticReportModal(QDialog):
    """Endoscopy Examination Diagnostic Report Viewer."""
    def __init__(self, record: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Diagnostic Report • {record.get('name', 'Patient')}")
        self.setFixedSize(700, 560)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        container = QFrame(self)
        container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0F1D2C, stop:1 #081018);
                border: 2px solid #0284C7;
                border-radius: 12px;
            }
            QLabel { color: #F8FAFC; }
        """)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(container)
        
        lay = QVBoxLayout(container)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)
        
        # Header
        top = QHBoxLayout()
        t_lbl = QLabel("ENDOSCOPY DIAGNOSTIC EXAMINATION REPORT")
        t_lbl.setStyleSheet("font-size: 16px; font-weight: 800; color: #38BDF8; letter-spacing: 0.5px;")
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #1E293B; color: #CBD5E1; border: 1px solid #334155; border-radius: 14px; font-weight: bold;
            }
            QPushButton:hover { background: #DC2626; color: white; border-color: #F87171; }
        """)
        close_btn.clicked.connect(self.accept)
        top.addWidget(t_lbl)
        top.addStretch()
        top.addWidget(close_btn)
        lay.addLayout(top)
        
        # Patient Details Grid
        grid = QGridLayout()
        grid.setSpacing(8)
        grid.addWidget(QLabel(f"<b>Patient:</b> {record.get('name')}"), 0, 0)
        grid.addWidget(QLabel(f"<b>MRN:</b> {record.get('mrn')}"), 0, 1)
        grid.addWidget(QLabel(f"<b>Age / Sex:</b> {record.get('age')} / {record.get('sex')}"), 1, 0)
        grid.addWidget(QLabel(f"<b>Visit Date:</b> {record.get('date')}"), 1, 1)
        grid.addWidget(QLabel(f"<b>Procedure:</b> {record.get('procedure')}"), 2, 0)
        grid.addWidget(QLabel(f"<b>Attending Endoscopist:</b> {record.get('doctor')}"), 2, 1)
        grid.addWidget(QLabel(f"<b>Referrer:</b> {record.get('referrer')}"), 3, 0, 1, 2)
        lay.addLayout(grid)
        
        # Findings Box
        f_box = QFrame()
        f_box.setStyleSheet("background: #0B1622; border: 1px solid #1E293B; border-radius: 6px; padding: 10px;")
        f_lay = QVBoxLayout(f_box)
        f_lay.setSpacing(6)
        f_title = QLabel("CLINICAL ENDOSCOPIC FINDINGS & IMPRESSION:")
        f_title.setStyleSheet("color: #10B981; font-weight: 700; font-size: 12px;")
        f_text = QLabel(
            f"• Scope advanced to cecum / terminal ileum without mucosal perforation.\n"
            f"• Primary Finding: {record.get('indication', 'Mucosal surveillance performed')}.\n"
            f"• Biopsy / Intervention: Target cold snare polypectomy performed with clear margins.\n"
            f"• Hemostasis: Complete. No immediate hemorrhage noted.\n"
            f"• Recommendation: Routine follow-up surveillance colonoscopy in 3 years."
        )
        f_text.setStyleSheet("color: #CBD5E1; font-size: 12px; line-height: 1.4;")
        f_lay.addWidget(f_title)
        f_lay.addWidget(f_text)
        lay.addWidget(f_box)
        
        # Bottom Print / Close
        b_lay = QHBoxLayout()
        b_lay.addStretch()
        p_btn = QPushButton("🖨 Print Official Report")
        p_btn.setStyleSheet("background: #0284C7; color: white; border-radius: 6px; padding: 8px 18px; font-weight: 700;")
        p_btn.clicked.connect(lambda: QMessageBox.information(self, "Print", "Dispatching report to hospital laser printer..."))
        b_lay.addWidget(p_btn)
        lay.addLayout(b_lay)


class ImagePlusModal(QDialog):
    """Multi-Frame Endoscopic Image Viewer / Gallery."""
    def __init__(self, patient_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Image Plus • {patient_name}")
        self.setFixedSize(760, 520)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        container = QFrame(self)
        container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0F1D2C, stop:1 #081018);
                border: 2px solid #0284C7;
                border-radius: 12px;
            }
            QLabel { color: #F8FAFC; }
        """)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(container)
        
        lay = QVBoxLayout(container)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(12)
        
        top = QHBoxLayout()
        t_lbl = QLabel(f"IMAGE PLUS • CAPTURED FRAMES [{patient_name}]")
        t_lbl.setStyleSheet("font-size: 15px; font-weight: 800; color: #38BDF8;")
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #1E293B; color: #CBD5E1; border: 1px solid #334155; border-radius: 14px; font-weight: bold;
            }
            QPushButton:hover { background: #DC2626; color: white; border-color: #F87171; }
        """)
        close_btn.clicked.connect(self.accept)
        top.addWidget(t_lbl)
        top.addStretch()
        top.addWidget(close_btn)
        lay.addLayout(top)
        
        # 3 Frame Preview Row
        f_row = QHBoxLayout()
        f_row.setSpacing(14)
        assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../assets"))
        
        for f_name, tag in [("preview_ercp.png", "Frame 1 • Retrograde Fluoro"), 
                            ("preview_endo.png", "Frame 2 • Cecal Polyp (NBI)"), 
                            ("preview_usg.png", "Frame 3 • Color Doppler")]:
            card = QFrame()
            card.setStyleSheet("background: #030712; border: 1.5px solid #1E293B; border-radius: 8px;")
            c_lay = QVBoxLayout(card)
            c_lay.setContentsMargins(6, 6, 6, 6)
            c_lay.setSpacing(4)
            
            img_lbl = QLabel()
            img_lbl.setAlignment(Qt.AlignCenter)
            p = os.path.join(assets_dir, f_name)
            if os.path.exists(p):
                pix = QPixmap(p).scaled(220, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                img_lbl.setPixmap(pix)
            c_lay.addWidget(img_lbl)
            
            tag_lbl = QLabel(tag)
            tag_lbl.setStyleSheet("color: #38BDF8; font-size: 11px; font-weight: 700;")
            tag_lbl.setAlignment(Qt.AlignCenter)
            c_lay.addWidget(tag_lbl)
            f_row.addWidget(card)
            
        lay.addLayout(f_row)
        
        info_lbl = QLabel("High-Definition 1080p60 USB2 Video Grabber Frames • DICOM C-STORE Compatible")
        info_lbl.setStyleSheet("color: #94A3B8; font-size: 11px;")
        info_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(info_lbl)


class ArchiveDialog(QDialog):
    """
    Patients Archive Workstation.
    Full clinical archive matching the PANORAMA reference design with:
    - Upper records table (9 columns)
    - Selected patient contact/address details card with Update and Delete
    - Command button column: New Patient, Capture, Show Report, Image Plus
    - Bottom multi-variable 12-criteria search engine with checkbox activation
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Endocare • Patients Archive & Study Records")
        # Safe desktop bounds: strictly respect Windows desktop taskbar
        screen = QApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else None
        target_w = min(1350, avail.width() - 16) if avail else 1350
        target_h = min(672, avail.height() - 36) if avail else 672
        self.resize(target_w, target_h)
        self.setMinimumSize(1080, 600)
        self.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        if avail:
            self.setMaximumHeight(avail.height() - 8)
            x = avail.x() + (avail.width() - target_w) // 2
            y = avail.y() + (avail.height() - target_h) // 2
            self.move(max(avail.x(), x), max(avail.y(), y))
        
        self._init_data()
        self._init_ui()

    def _init_data(self):
        # Sample realistic clinical database records
        self.records = [
            {
                "auto_id": "00000001", "name": "Adnan Shefat", "age": "18", "sex": "Male",
                "date": "15-07-2026", "procedure": "COLONOSCOPY", "doctor": "Dr. Sarah Jenkins",
                "referrer": "Metropolitan Clinic", "mrn": "ENDO-2026-0042",
                "address": "House 14, Road 5, Block B, Dhanmondi", "town": "Dhaka", "state": "Central",
                "postcode": "1209", "phone": "01457856554", "indication": "Chronic recurrent abdominal discomfort"
            },
            {
                "auto_id": "00000002", "name": "Maria Gonzales", "age": "45", "sex": "Female",
                "date": "17-08-2026", "procedure": "UPPER GI ENDOSCOPY", "doctor": "Dr. Michael Chang",
                "referrer": "Westside Family Practice", "mrn": "ENDO-2026-0811",
                "address": "742 Evergreen Terrace", "town": "Springfield", "state": "IL",
                "postcode": "62704", "phone": "+1 (555) 234-8901", "indication": "Grade B Reflux Esophagitis (LA Class)"
            },
            {
                "auto_id": "00000003", "name": "Alexander Hayes", "age": "58", "sex": "Male",
                "date": "18-09-2026", "procedure": "COLONOSCOPY", "doctor": "Dr. Sarah Jenkins",
                "referrer": "Direct Clinical Intake", "mrn": "ENDO-2026-0814",
                "address": "404 North Medical Plaza, Suite 300", "town": "Chicago", "state": "IL",
                "postcode": "60611", "phone": "+1 (555) 789-0123", "indication": "Tubular Adenoma (Paris 0-Is) resected"
            },
            {
                "auto_id": "00000004", "name": "Robert Chen", "age": "62", "sex": "Male",
                "date": "16-09-2026", "procedure": "ERCP", "doctor": "Dr. Elena Rostova",
                "referrer": "St. Jude Internal Medicine", "mrn": "ENDO-2026-0809",
                "address": "1208 Bayfront Promenade", "town": "San Francisco", "state": "CA",
                "postcode": "94107", "phone": "+1 (555) 456-7890", "indication": "Choledocholithiasis extracted, stent placed"
            },
            {
                "auto_id": "00000005", "name": "Emma Watson", "age": "34", "sex": "Female",
                "date": "15-09-2026", "procedure": "COLONOSCOPY", "doctor": "Dr. Sarah Jenkins",
                "referrer": "Emergency Department", "mrn": "ENDO-2026-0803",
                "address": "88 Crescent Boulevard", "town": "Boston", "state": "MA",
                "postcode": "02115", "phone": "+1 (555) 890-1234", "indication": "Normal terminal ileum & colon mucosa"
            },
            {
                "auto_id": "00000006", "name": "David Miller", "age": "50", "sex": "Male",
                "date": "14-09-2026", "procedure": "UPPER GI ENDOSCOPY", "doctor": "Dr. Michael Chang",
                "referrer": "Direct Clinical Intake", "mrn": "ENDO-2026-0798",
                "address": "15 Beacon Hill Lane", "town": "Seattle", "state": "WA",
                "postcode": "98101", "phone": "+1 (555) 345-6789", "indication": "Gastric Ulcer (Forrest III), Biopsy sent"
            }
        ]
        self._current_filtered = list(self.records)

    def _init_ui(self):
        root = QFrame(self)
        root.setObjectName("archiveWorkstationRoot")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(root)
        
        container_layout = QVBoxLayout(root)
        container_layout.setContentsMargins(20, 16, 20, 16)
        
        # Central Main Card
        card = QFrame()
        card.setObjectName("archiveWorkstationCard")
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 6)
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 10, 14, 12)
        card_layout.setSpacing(8)
        
        # =========================================================================
        # 1. HEADER: [CLOSE] ... Patients Archive ... Showing Last X Patient(s)
        # Top banner with jade/teal gradient matching Demo/Patientarchive.PNG
        # =========================================================================
        header_frame = QFrame()
        header_frame.setObjectName("archiveHeaderBar")
        header_row = QHBoxLayout(header_frame)
        header_row.setContentsMargins(8, 4, 10, 4)
        
        btn_close = QPushButton("CLOSE")
        btn_close.setObjectName("cardCloseBtn")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.reject)
        header_row.addWidget(btn_close)
        
        header_row.addStretch()
        
        title_lbl = QLabel("Patients Archive")
        title_lbl.setObjectName("archiveHeaderTitle")
        title_lbl.setAlignment(Qt.AlignCenter)
        header_row.addWidget(title_lbl)
        
        header_row.addStretch()
        
        self.lbl_counter = QLabel(f"Showing Last {len(self.records)} Patient(s)")
        self.lbl_counter.setObjectName("archiveCounterBadge")
        header_row.addWidget(self.lbl_counter)
        
        card_layout.addWidget(header_frame)
        
        # =========================================================================
        # 2. UPPER ARCHIVE TABLE (9 Columns matching reference image)
        # =========================================================================
        self.table = QTableWidget()
        self.table.setObjectName("archiveTable")
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Auto ID", "Patient Name", "Age", "Sex", "Visit Date", "Procedure", "Doctors", "Referrers", "MRN"
        ])
        self.table.horizontalHeader().setObjectName("archiveTableHeader")
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.setColumnWidth(0, 95)   # Auto ID
        self.table.setColumnWidth(1, 160)  # Patient Name
        self.table.setColumnWidth(2, 55)   # Age
        self.table.setColumnWidth(3, 65)   # Sex
        self.table.setColumnWidth(4, 95)   # Visit Date
        self.table.setColumnWidth(5, 170)  # Procedure
        self.table.setColumnWidth(6, 165)  # Doctors
        self.table.setColumnWidth(7, 165)  # Referrers
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.itemSelectionChanged.connect(self._on_table_row_selected)
        
        card_layout.addWidget(self.table, stretch=4)
        
        # =========================================================================
        # 3. MIDDLE SELECTED PATIENT DETAILS & ACTION BOX
        # =========================================================================
        middle_row = QHBoxLayout()
        middle_row.setSpacing(10)
        
        # Green-bordered details sub-card matching Demo/Patientarchive.PNG
        details_box = QFrame()
        details_box.setObjectName("selectedPatientDetailsBox")
        d_layout = QHBoxLayout(details_box)
        d_layout.setContentsMargins(10, 6, 10, 6)
        d_layout.setSpacing(10)
        
        # Left: Address label stacked vertically
        lbl_addr = QLabel("Selected\nPatient's\nAddress :")
        lbl_addr.setProperty("class", "archiveFieldLabel")
        lbl_addr.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        d_layout.addWidget(lbl_addr)
        
        self.txt_address = QLineEdit()
        self.txt_address.setProperty("class", "archiveInput")
        self.txt_address.setMinimumHeight(38)
        d_layout.addWidget(self.txt_address, stretch=3)
        
        # Middle-Right: 2-row grid with Town, State, Update / Post Code, Phone, Delete
        sub_grid = QGridLayout()
        sub_grid.setHorizontalSpacing(8)
        sub_grid.setVerticalSpacing(5)
        
        lbl_town = QLabel("Town :")
        lbl_town.setProperty("class", "archiveFieldLabel")
        self.input_town = QLineEdit()
        self.input_town.setProperty("class", "archiveInput")
        
        lbl_state = QLabel("State :")
        lbl_state.setProperty("class", "archiveFieldLabel")
        self.input_state = QLineEdit()
        self.input_state.setProperty("class", "archiveInput")
        
        btn_update = QPushButton("Update")
        btn_update.setObjectName("btnArchiveUpdate")
        btn_update.setCursor(Qt.PointingHandCursor)
        btn_update.clicked.connect(self._handle_update_patient)
        
        lbl_post = QLabel("Post Code :")
        lbl_post.setProperty("class", "archiveFieldLabel")
        self.input_post = QLineEdit()
        self.input_post.setProperty("class", "archiveInput")
        
        lbl_phone = QLabel("Phone :")
        lbl_phone.setProperty("class", "archiveFieldLabel")
        self.input_phone = QLineEdit()
        self.input_phone.setProperty("class", "archiveInput")
        
        btn_delete = QPushButton("Delete")
        btn_delete.setObjectName("btnArchiveDelete")
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.clicked.connect(self._handle_delete_patient)
        
        sub_grid.addWidget(lbl_town, 0, 0)
        sub_grid.addWidget(self.input_town, 0, 1)
        sub_grid.addWidget(lbl_state, 0, 2)
        sub_grid.addWidget(self.input_state, 0, 3)
        sub_grid.addWidget(btn_update, 0, 4)
        
        sub_grid.addWidget(lbl_post, 1, 0)
        sub_grid.addWidget(self.input_post, 1, 1)
        sub_grid.addWidget(lbl_phone, 1, 2)
        sub_grid.addWidget(self.input_phone, 1, 3)
        sub_grid.addWidget(btn_delete, 1, 4)
        
        d_layout.addLayout(sub_grid, stretch=4)
        middle_row.addWidget(details_box, stretch=1)
        
        # Far Right Action Buttons (Vertical Stack of 4)
        side_action_layout = QVBoxLayout()
        side_action_layout.setSpacing(4)
        
        btn_new_pat = QPushButton("New Patient")
        btn_new_pat.setProperty("class", "archiveSideActionBtn")
        btn_new_pat.setCursor(Qt.PointingHandCursor)
        btn_new_pat.clicked.connect(self._open_new_patient)
        
        btn_capture = QPushButton("Capture")
        btn_capture.setProperty("class", "archiveSideActionBtn")
        btn_capture.setCursor(Qt.PointingHandCursor)
        btn_capture.clicked.connect(lambda: QMessageBox.information(self, "Capture", "Returning to Endoscopic Grabber Live Viewport..."))
        
        btn_show_rep = QPushButton("Show Report")
        btn_show_rep.setProperty("class", "archiveSideActionBtn")
        btn_show_rep.setCursor(Qt.PointingHandCursor)
        btn_show_rep.clicked.connect(self._show_report_modal)
        
        btn_img_plus = QPushButton("Image Plus")
        btn_img_plus.setProperty("class", "archiveSideActionBtn")
        btn_img_plus.setCursor(Qt.PointingHandCursor)
        btn_img_plus.clicked.connect(self._show_image_plus_modal)
        
        side_action_layout.addWidget(btn_new_pat)
        side_action_layout.addWidget(btn_capture)
        side_action_layout.addWidget(btn_show_rep)
        side_action_layout.addWidget(btn_img_plus)
        middle_row.addLayout(side_action_layout)
        
        card_layout.addLayout(middle_row)
        
        # =========================================================================
        # 4. BOTTOM SEARCH: "Search Patients By 12 Criteria"
        # =========================================================================
        s_top = QHBoxLayout()
        s_top.setContentsMargins(4, 2, 4, 0)
        s_title = QLabel("Search Patients By 12 Criteria (you can select single to maximum criteria at a time for accurate search)")
        s_title.setObjectName("search12HeaderTitle")
        s_top.addWidget(s_title)
        s_top.addStretch()
        
        btn_search = QPushButton("SEARCH")
        btn_search.setObjectName("btnArchiveSearch")
        btn_search.setCursor(Qt.PointingHandCursor)
        btn_search.clicked.connect(self._handle_search)
        s_top.addWidget(btn_search)
        card_layout.addLayout(s_top)
        
        search_box = QFrame()
        search_box.setObjectName("search12Box")
        s_layout = QVBoxLayout(search_box)
        s_layout.setContentsMargins(10, 6, 10, 6)
        s_layout.setSpacing(4)
        
        # 3 Column Criteria Grid
        c_grid = QGridLayout()
        c_grid.setHorizontalSpacing(14)
        c_grid.setVerticalSpacing(4)
        
        def _make_b2wn():
            lbl = QLabel("- b2wn -")
            lbl.setProperty("class", "archiveB2wnLabel")
            return lbl
        
        # --- Column 1: A.ID, Age, Date, Sex ---
        self.chk_aid = QCheckBox("A. ID :")
        self.chk_aid.setProperty("class", "archiveCriteriaCheck")
        self.input_aid_min = QLineEdit("0")
        self.input_aid_min.setProperty("class", "archiveInput")
        self.input_aid_min.setFixedWidth(56)
        self.input_aid_max = QLineEdit("0")
        self.input_aid_max.setProperty("class", "archiveInput")
        self.input_aid_max.setFixedWidth(70)
        
        aid_lay = QHBoxLayout()
        aid_lay.addWidget(self.input_aid_min)
        aid_lay.addWidget(_make_b2wn())
        aid_lay.addWidget(self.input_aid_max)
        aid_lay.addStretch()
        c_grid.addWidget(self.chk_aid, 0, 0)
        c_grid.addLayout(aid_lay, 0, 1)
        
        self.chk_age = QCheckBox("Age :")
        self.chk_age.setProperty("class", "archiveCriteriaCheck")
        self.input_age_min = QLineEdit("0")
        self.input_age_min.setProperty("class", "archiveInput")
        self.input_age_min.setFixedWidth(56)
        self.input_age_max = QLineEdit("0")
        self.input_age_max.setProperty("class", "archiveInput")
        self.input_age_max.setFixedWidth(70)
        
        age_lay = QHBoxLayout()
        age_lay.addWidget(self.input_age_min)
        age_lay.addWidget(_make_b2wn())
        age_lay.addWidget(self.input_age_max)
        age_lay.addStretch()
        c_grid.addWidget(self.chk_age, 1, 0)
        c_grid.addLayout(age_lay, 1, 1)
        
        self.chk_date = QCheckBox("Date :")
        self.chk_date.setProperty("class", "archiveCriteriaCheck")
        self.input_date_min = QDateEdit()
        self.input_date_min.setProperty("class", "archiveDate")
        self.input_date_min.setCalendarPopup(True)
        self.input_date_min.setDisplayFormat("dd-MM-yyyy")
        self.input_date_min.setDate(QDate.currentDate().addDays(-1))
        
        self.input_date_max = QDateEdit()
        self.input_date_max.setProperty("class", "archiveDate")
        self.input_date_max.setCalendarPopup(True)
        self.input_date_max.setDisplayFormat("dd-MM-yyyy")
        self.input_date_max.setDate(QDate.currentDate())
        
        date_lay = QHBoxLayout()
        date_lay.addWidget(self.input_date_min)
        date_lay.addWidget(_make_b2wn())
        date_lay.addWidget(self.input_date_max)
        c_grid.addWidget(self.chk_date, 2, 0)
        c_grid.addLayout(date_lay, 2, 1)
        
        self.chk_sex = QCheckBox("Sex :")
        self.chk_sex.setProperty("class", "archiveCriteriaCheck")
        self.radio_s_male = QRadioButton("Male")
        self.radio_s_male.setProperty("class", "archiveRadio")
        self.radio_s_male.setChecked(True)
        self.radio_s_female = QRadioButton("Female")
        self.radio_s_female.setProperty("class", "archiveRadio")
        
        sex_group = QButtonGroup(self)
        sex_group.addButton(self.radio_s_male)
        sex_group.addButton(self.radio_s_female)
        
        sex_lay = QHBoxLayout()
        sex_lay.addWidget(self.radio_s_male)
        sex_lay.addWidget(self.radio_s_female)
        sex_lay.addStretch()
        c_grid.addWidget(self.chk_sex, 3, 0)
        c_grid.addLayout(sex_lay, 3, 1)
        
        # --- Column 2: MRN, Name, Indication, Report ---
        self.chk_mrn = QCheckBox("MRN :")
        self.chk_mrn.setProperty("class", "archiveCriteriaCheck")
        self.input_s_mrn = QLineEdit()
        self.input_s_mrn.setProperty("class", "archiveInput")
        c_grid.addWidget(self.chk_mrn, 0, 2)
        c_grid.addWidget(self.input_s_mrn, 0, 3)
        
        self.chk_name = QCheckBox("Name :")
        self.chk_name.setProperty("class", "archiveCriteriaCheck")
        self.input_s_name = QLineEdit()
        self.input_s_name.setProperty("class", "archiveInput")
        c_grid.addWidget(self.chk_name, 1, 2)
        c_grid.addWidget(self.input_s_name, 1, 3)
        
        self.chk_ind = QCheckBox("Indication :")
        self.chk_ind.setProperty("class", "archiveCriteriaCheck")
        self.input_s_ind = QLineEdit()
        self.input_s_ind.setProperty("class", "archiveInput")
        c_grid.addWidget(self.chk_ind, 2, 2)
        c_grid.addWidget(self.input_s_ind, 2, 3)
        
        self.chk_rep = QCheckBox("Report :")
        self.chk_rep.setProperty("class", "archiveCriteriaCheck")
        self.input_s_rep = QLineEdit()
        self.input_s_rep.setProperty("class", "archiveInput")
        c_grid.addWidget(self.chk_rep, 3, 2)
        c_grid.addWidget(self.input_s_rep, 3, 3)
        
        # --- Column 3: Procedure, History, Doctor, Referrer ---
        self.chk_proc = QCheckBox("Procedure :")
        self.chk_proc.setProperty("class", "archiveCriteriaCheck")
        self.combo_s_proc = QComboBox()
        self.combo_s_proc.setProperty("class", "archiveCombo")
        self.combo_s_proc.addItems(["COLONOSCOPY", "UPPER GI ENDOSCOPY", "ERCP", "SIGMOIDOSCOPY", "EUS"])
        c_grid.addWidget(self.chk_proc, 0, 4)
        c_grid.addWidget(self.combo_s_proc, 0, 5)
        
        self.chk_hist = QCheckBox("History :")
        self.chk_hist.setProperty("class", "archiveCriteriaCheck")
        self.combo_s_hist = QComboBox()
        self.combo_s_hist.setProperty("class", "archiveCombo")
        self.combo_s_hist.addItems(["All Histories", "Prior Polypectomy", "GERD / Barrett's", "Inflammatory Bowel Disease", "Post-Surgical"])
        c_grid.addWidget(self.chk_hist, 1, 4)
        c_grid.addWidget(self.combo_s_hist, 1, 5)
        
        self.chk_doc = QCheckBox("Doctor :")
        self.chk_doc.setProperty("class", "archiveCriteriaCheck")
        self.combo_s_doc = QComboBox()
        self.combo_s_doc.setProperty("class", "archiveCombo")
        self.combo_s_doc.addItems(["Dr. Sarah Jenkins", "Dr. Michael Chang", "Dr. Elena Rostova", "Dr. David Miller"])
        c_grid.addWidget(self.chk_doc, 2, 4)
        c_grid.addWidget(self.combo_s_doc, 2, 5)
        
        self.chk_ref = QCheckBox("Referrer :")
        self.chk_ref.setProperty("class", "archiveCriteriaCheck")
        self.combo_s_ref = QComboBox()
        self.combo_s_ref.setProperty("class", "archiveCombo")
        self.combo_s_ref.addItems(["Metropolitan Clinic", "Westside Family Practice", "Direct Clinical Intake", "St. Jude Internal Medicine"])
        c_grid.addWidget(self.chk_ref, 3, 4)
        c_grid.addWidget(self.combo_s_ref, 3, 5)
        
        s_layout.addLayout(c_grid)
        card_layout.addWidget(search_box)
        
        container_layout.addWidget(card)
        
        # Populate initial rows
        self._populate_table(self.records)

    def _populate_table(self, data_list):
        self.table.setRowCount(len(data_list))
        for r_idx, rec in enumerate(data_list):
            self.table.setItem(r_idx, 0, QTableWidgetItem(rec.get("auto_id", "")))
            self.table.setItem(r_idx, 1, QTableWidgetItem(rec.get("name", "")))
            self.table.setItem(r_idx, 2, QTableWidgetItem(rec.get("age", "")))
            self.table.setItem(r_idx, 3, QTableWidgetItem(rec.get("sex", "")))
            self.table.setItem(r_idx, 4, QTableWidgetItem(rec.get("date", "")))
            self.table.setItem(r_idx, 5, QTableWidgetItem(rec.get("procedure", "")))
            self.table.setItem(r_idx, 6, QTableWidgetItem(rec.get("doctor", "")))
            self.table.setItem(r_idx, 7, QTableWidgetItem(rec.get("referrer", "")))
            self.table.setItem(r_idx, 8, QTableWidgetItem(rec.get("mrn", "")))
        
        self.lbl_counter.setText(f"Showing Last {len(data_list)} Patient(s)")
        
        if data_list:
            self.table.selectRow(0)
            self._load_patient_details(data_list[0])
        else:
            self._clear_patient_details()

    def _on_table_row_selected(self):
        row = self.table.currentRow()
        if 0 <= row < len(self._current_filtered):
            self._load_patient_details(self._current_filtered[row])

    def _load_patient_details(self, rec):
        self.txt_address.setText(rec.get("address", ""))
        self.input_town.setText(rec.get("town", ""))
        self.input_state.setText(rec.get("state", ""))
        self.input_post.setText(rec.get("postcode", ""))
        self.input_phone.setText(rec.get("phone", ""))

    def _clear_patient_details(self):
        self.txt_address.clear()
        self.input_town.clear()
        self.input_state.clear()
        self.input_post.clear()
        self.input_phone.clear()

    def _handle_update_patient(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._current_filtered):
            QMessageBox.warning(self, "Notice", "Please select a patient from the archive table first.")
            return
            
        rec = self._current_filtered[row]
        rec["address"] = self.txt_address.text().strip()
        rec["town"] = self.input_town.text().strip()
        rec["state"] = self.input_state.text().strip()
        rec["postcode"] = self.input_post.text().strip()
        rec["phone"] = self.input_phone.text().strip()
        
        QMessageBox.information(
            self, "Patient Record Updated",
            f"✓ Contact & Address for {rec.get('name')} [{rec.get('mrn')}] updated successfully."
        )


    def _handle_delete_patient(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._current_filtered):
            QMessageBox.warning(self, "Notice", "Please select a patient to remove.")
            return
            
        rec = self._current_filtered[row]
        reply = QMessageBox.question(
            self, "Confirm Patient Deletion",
            f"Are you sure you want to archive / delete {rec.get('name')} [{rec.get('mrn')}]?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if rec in self.records:
                self.records.remove(rec)
            self._current_filtered.remove(rec)
            self._populate_table(self._current_filtered)

    def _handle_search(self):
        results = []
        for rec in self.records:
            match = True
            
            # 1. A. ID
            if self.chk_aid.isChecked():
                try:
                    aid = int(rec.get("auto_id", "0"))
                    min_aid = int(self.input_aid_min.text())
                    max_aid = int(self.input_aid_max.text())
                    if not (min_aid <= aid <= max_aid):
                        match = False
                except ValueError:
                    pass
                    
            # 2. Age
            if match and self.chk_age.isChecked():
                try:
                    age = int(rec.get("age", "0"))
                    min_age = int(self.input_age_min.text())
                    max_age = int(self.input_age_max.text())
                    if not (min_age <= age <= max_age):
                        match = False
                except ValueError:
                    pass
                    
            # 3. Sex
            if match and self.chk_sex.isChecked():
                chosen_sex = "Male" if self.radio_s_male.isChecked() else "Female"
                if rec.get("sex", "").lower() != chosen_sex.lower():
                    match = False
                    
            # 4. MRN
            if match and self.chk_mrn.isChecked():
                term = self.input_s_mrn.text().strip().lower()
                if term and term not in rec.get("mrn", "").lower():
                    match = False
                    
            # 5. Name
            if match and self.chk_name.isChecked():
                term = self.input_s_name.text().strip().lower()
                if term and term not in rec.get("name", "").lower():
                    match = False
                    
            # 6. Indication
            if match and self.chk_ind.isChecked():
                term = self.input_s_ind.text().strip().lower()
                if term and term not in rec.get("indication", "").lower():
                    match = False
                    
            # 7. Procedure
            if match and self.chk_proc.isChecked():
                proc = self.combo_s_proc.currentText().strip().lower()
                if proc not in rec.get("procedure", "").lower():
                    match = False
                    
            # 8. Doctor
            if match and self.chk_doc.isChecked():
                doc = self.combo_s_doc.currentText().strip().lower()
                if doc not in rec.get("doctor", "").lower():
                    match = False
                    
            # 9. Referrer
            if match and self.chk_ref.isChecked():
                ref = self.combo_s_ref.currentText().strip().lower()
                if ref not in rec.get("referrer", "").lower():
                    match = False
                    
            if match:
                results.append(rec)
                
        self._current_filtered = results
        self._populate_table(results)

    def _handle_reset(self):
        for chk in [self.chk_aid, self.chk_age, self.chk_date, self.chk_sex,
                    self.chk_mrn, self.chk_name, self.chk_ind, self.chk_rep,
                    self.chk_proc, self.chk_hist, self.chk_doc, self.chk_ref]:
            chk.setChecked(False)
        self._current_filtered = list(self.records)
        self._populate_table(self.records)

    def _open_new_patient(self):
        from app.ui.dialogs.new_patient_dialog import NewPatientDialog
        dlg = NewPatientDialog(self)
        dlg.exec()

    def _show_report_modal(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._current_filtered):
            QMessageBox.warning(self, "Notice", "Please select a patient from the table to view the report.")
            return
        rec = self._current_filtered[row]
        dlg = DiagnosticReportModal(rec, self)
        dlg.exec()

    def _show_image_plus_modal(self):
        row = self.table.currentRow()
        name = self._current_filtered[row].get("name", "Patient") if (0 <= row < len(self._current_filtered)) else "Patient"
        dlg = ImagePlusModal(name, self)
        dlg.exec()
