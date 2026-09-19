from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox
)
from PySide6.QtCore import Qt


class TemplatesDialog(QDialog):
    """Management dialog for standardized endoscopy clinical report templates."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Endocare • Endoscopy Report Templates")
        self.resize(800, 500)
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        banner = QFrame()
        banner.setStyleSheet("background-color: #0369A1; border-radius: 8px; padding: 14px 18px;")
        b_l = QVBoxLayout(banner)
        t_l = QLabel("📄 Structured Report Templates")
        t_l.setStyleSheet("color: white; font-size: 16px; font-weight: 700;")
        s_l = QLabel("Standardized clinical report templates, endoscopic classifications (Paris, Forrest, Prague, LA Grade).")
        s_l.setStyleSheet("color: #E0F2FE; font-size: 12px;")
        b_l.addWidget(t_l)
        b_l.addWidget(s_l)
        layout.addWidget(banner)
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Template Code", "Procedure / Title", "Clinical Classification", "Macro Fields", "Status"])
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        tpls = [
            ("TPL-EGD-01", "Normal Upper GI Gastroscopy", "Standard Negative Study", "12 structured tags", "Active Default"),
            ("TPL-EGD-02", "Peptic Ulcer Bleeding Protocol", "Forrest Classification (Ia, Ib, IIa-c, III)", "Hemostasis clip / epi", "Active"),
            ("TPL-COL-01", "Screening Colonoscopy & Polypectomy", "Paris Classification / Nice Class", "Cold snare / hot biopsy", "Active Default"),
            ("TPL-COL-02", "Inflammatory Bowel Disease (IBD)", "Mayo Endoscopic Score / SES-CD", "Segmental mucosal scoring", "Active"),
            ("TPL-ERCP-01", "Biliary Sphincterotomy & Stenting", "Cotton-Leung / ASGE Guidelines", "Fluoroscopy frames / wire", "Active"),
            ("TPL-BAR-01", "Barrett's Esophagus Surveillance", "Prague C&M Criteria + Seattle protocol", "Quadrantic biopsy tags", "Active"),
        ]
        table.setRowCount(len(tpls))
        for r, tpl in enumerate(tpls):
            for c, val in enumerate(tpl):
                it = QTableWidgetItem(val)
                if c == 4:
                    it.setTextAlignment(Qt.AlignCenter)
                    it.setForeground(Qt.darkGreen)
                table.setItem(r, c, it)
        layout.addWidget(table)
        
        btn_box = QHBoxLayout()
        add_btn = QPushButton("➕ Create Template")
        add_btn.setStyleSheet("background: #0284C7; color: white; border-radius: 6px; padding: 8px 16px; font-weight: 600;")
        add_btn.clicked.connect(lambda: QMessageBox.information(self, "Create Template", "Opening structured report template builder..."))
        btn_box.addWidget(add_btn)
        
        btn_box.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("background: #0F172A; color: white; border-radius: 6px; padding: 8px 20px;")
        close_btn.clicked.connect(self.accept)
        btn_box.addWidget(close_btn)
        layout.addLayout(btn_box)
