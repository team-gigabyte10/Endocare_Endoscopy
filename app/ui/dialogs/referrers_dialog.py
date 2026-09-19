from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox
)
from PySide6.QtCore import Qt


class ReferrersDialog(QDialog):
    """Management dialog for referring physicians and external medical centers."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Endocare • Referring Physicians & Clinics")
        self.resize(780, 480)
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        banner = QFrame()
        banner.setStyleSheet("background-color: #0F766E; border-radius: 8px; padding: 14px 18px;")
        b_l = QVBoxLayout(banner)
        t_l = QLabel("🏥 Referring Physicians Directory")
        t_l.setStyleSheet("color: white; font-size: 16px; font-weight: 700;")
        s_l = QLabel("Manage outpatient referral centers, primary care clinics, and automated report dispatch.")
        s_l.setStyleSheet("color: #CCFBF1; font-size: 12px;")
        b_l.addWidget(t_l)
        b_l.addWidget(s_l)
        layout.addWidget(banner)
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Referrer Name", "Practice / Hospital", "Phone", "Email / Direct Portal", "Auto-Fax/EHR"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
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
        layout.addWidget(table)
        
        btn_box = QHBoxLayout()
        add_btn = QPushButton("➕ Add Referrer")
        add_btn.setStyleSheet("background: #0F766E; color: white; border-radius: 6px; padding: 8px 16px; font-weight: 600;")
        add_btn.clicked.connect(lambda: QMessageBox.information(self, "Add Referrer", "Opening referring provider registration form..."))
        btn_box.addWidget(add_btn)
        
        btn_box.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("background: #0F172A; color: white; border-radius: 6px; padding: 8px 20px;")
        close_btn.clicked.connect(self.accept)
        btn_box.addWidget(close_btn)
        layout.addLayout(btn_box)
