from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut


class ReferrersDialog(QDialog):
    """Management workstation for referring physicians and external medical centers."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Endocare • Referring Physicians & Clinics")
        self.setWindowState(Qt.WindowFullScreen)
        self.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.setMinimumSize(800, 500)
        
        QShortcut(QKeySequence(Qt.Key_F11), self, self._toggle_fullscreen)
        self._init_ui()

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)
        
        # Header Banner with integrated window controls
        banner = QFrame()
        banner.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0F766E, stop:1 #094E48);
                border-radius: 8px;
                padding: 10px 16px;
            }
        """)
        b_l = QHBoxLayout(banner)
        b_l.setContentsMargins(4, 4, 4, 4)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        t_l = QLabel("🏥 Referring Physicians Directory")
        t_l.setStyleSheet("color: white; font-size: 17px; font-weight: 700;")
        s_l = QLabel("Manage outpatient referral centers, primary care clinics, and automated report dispatch.")
        s_l.setStyleSheet("color: #CCFBF1; font-size: 12px;")
        text_layout.addWidget(t_l)
        text_layout.addWidget(s_l)
        b_l.addLayout(text_layout)
        
        b_l.addStretch()
        layout.addWidget(banner)
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Referrer Name", "Practice / Hospital", "Phone", "Email / Direct Portal", "Auto-Fax/EHR"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        refs = [
            ("Dr. Arthur Morgan", "Metropolitan Family Practice", "+1 (555) 392-1092", "direct@metrofamily.org", "HL7 / FHIR"),
            ("Dr. Rebecca Vance", "Westside Internal Medicine", "+1 (555) 482-9011", "vance@westsideinternal.com", "Encrypted PDF"),
            ("Dr. Kenneth Lee", "St. Jude Community Health", "+1 (555) 718-4902", "klee@stjudehealth.net", "Epic CareLink"),
            ("Dr. Samantha Miller", "Oakridge Oncology Institute", "+1 (555) 902-1847", "s.miller@oakridgeonco.org", "Direct DICOM/HL7"),
        ]
        table.setRowCount(len(refs))
        for r, ref in enumerate(refs):
            for c, val in enumerate(ref):
                it = QTableWidgetItem(val)
                table.setItem(r, c, it)
        layout.addWidget(table, 1)
        
        btn_box = QHBoxLayout()
        add_btn = QPushButton("➕ Add Referrer")
        add_btn.setStyleSheet("background: #0F766E; color: white; border-radius: 6px; padding: 8px 16px; font-weight: 600;")
        add_btn.clicked.connect(lambda: QMessageBox.information(self, "Add Referrer", "Opening referring provider registration form..."))
        btn_box.addWidget(add_btn)
        
        btn_box.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("background: #0F172A; color: white; border-radius: 6px; padding: 8px 20px; font-weight: 600;")
        close_btn.clicked.connect(self.accept)
        btn_box.addWidget(close_btn)
        layout.addLayout(btn_box)
