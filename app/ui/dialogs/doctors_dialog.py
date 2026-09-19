from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox
)
from PySide6.QtCore import Qt


class DoctorsDialog(QDialog):
    """Management dialog for clinical endoscopy physicians and endoscopists."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Endocare • Endoscopy Physicians & Staff")
        self.resize(780, 480)
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        banner = QFrame()
        banner.setStyleSheet("background-color: #0F172A; border-radius: 8px; padding: 14px 18px;")
        b_l = QVBoxLayout(banner)
        t_l = QLabel("🩺 Clinical Endoscopists & Physician Roster")
        t_l.setStyleSheet("color: white; font-size: 16px; font-weight: 700;")
        s_l = QLabel("Manage physician credentials, procedure authorization, and active suite assignments.")
        s_l.setStyleSheet("color: #94A3B8; font-size: 12px;")
        b_l.addWidget(t_l)
        b_l.addWidget(s_l)
        layout.addWidget(banner)
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Physician Name", "Specialty", "License / NPI", "Procedures Completed", "Status"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        docs = [
            ("Dr. Sarah Jenkins, MD, FACG", "Gastroenterology / Advanced Endoscopy", "NPI-91823741", "1,248", "● Active"),
            ("Dr. Michael Chang, MD", "Diagnostic & Therapeutic EGD/Colonoscopy", "NPI-84729104", "892", "● Active"),
            ("Dr. Elena Rostova, MD, PhD", "Interventional Endoscopy & ERCP", "NPI-57291038", "1,640", "● In Procedure"),
            ("Dr. Marcus Thorne, MD", "Pulmonology / Bronchoscopy", "NPI-63820194", "415", "● On Call"),
        ]
        table.setRowCount(len(docs))
        for r, doc in enumerate(docs):
            for c, val in enumerate(doc):
                it = QTableWidgetItem(val)
                if c == 4:
                    it.setTextAlignment(Qt.AlignCenter)
                    it.setForeground(Qt.darkGreen if "Active" in val else Qt.blue)
                table.setItem(r, c, it)
        layout.addWidget(table)
        
        btn_box = QHBoxLayout()
        add_btn = QPushButton("➕ Add Physician")
        add_btn.setStyleSheet("background: #0284C7; color: white; border-radius: 6px; padding: 8px 16px; font-weight: 600;")
        add_btn.clicked.connect(lambda: QMessageBox.information(self, "Add Physician", "Opening physician credentialing form..."))
        btn_box.addWidget(add_btn)
        
        btn_box.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("background: #0F172A; color: white; border-radius: 6px; padding: 8px 20px;")
        close_btn.clicked.connect(self.accept)
        btn_box.addWidget(close_btn)
        layout.addLayout(btn_box)
