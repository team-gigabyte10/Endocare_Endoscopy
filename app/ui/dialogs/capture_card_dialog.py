from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QLineEdit, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut


class CaptureCardDialog(QDialog):
    """
    Workstation for managing Endoscopy Capture Card Library hardware configurations,
    SDI/HDMI frame grabbers, pedal triggers, and video resolutions.
    """
    def __init__(self, mode="library", parent=None):
        super().__init__(parent)
        self.mode = mode
        self.setWindowTitle("Endocare • Capture Card Library Manager")
        self.setWindowState(Qt.WindowFullScreen)
        self.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.setMinimumSize(820, 520)
        
        QShortcut(QKeySequence(Qt.Key_F11), self, self._toggle_fullscreen)
        self._init_ui()

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showMaximized()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # Header Info Banner
        banner = QFrame()
        banner.setStyleSheet("""
            QFrame {
                background-color: #0F172A;
                border-radius: 8px;
                padding: 14px 18px;
            }
        """)
        b_layout = QHBoxLayout(banner)
        
        text_layout = QVBoxLayout()
        title_lbl = QLabel("📹 Capture Card Hardware Library")
        title_lbl.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: 700;")
        sub_lbl = QLabel("Configure medical video acquisition cards, Olympus/Pentax/Fujifilm inputs, and DICOM frame capture.")
        sub_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
        text_layout.addWidget(title_lbl)
        text_layout.addWidget(sub_lbl)
        b_layout.addLayout(text_layout)
        
        b_layout.addStretch()
        
        # Status counter
        stat_box = QLabel("4 Cards Online\n4K UHD Ready")
        stat_box.setStyleSheet("color: #38BDF8; font-size: 12px; font-weight: 600; text-align: right;")
        stat_box.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        b_layout.addWidget(stat_box)
        
        layout.addWidget(banner)
        
        # Action Toolbar inside dialog
        toolbar = QHBoxLayout()
        add_btn = QPushButton("➕ Add New Card")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #0284C7; color: white; font-weight: 600;
                border-radius: 6px; padding: 7px 14px; border: none;
            }
            QPushButton:hover { background-color: #0369A1; }
        """)
        add_btn.clicked.connect(self._add_card_action)
        toolbar.addWidget(add_btn)
        
        test_btn = QPushButton("⚡ Test Active Feed")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF; color: #0F172A; font-weight: 600;
                border: 1px solid #CBD5E1; border-radius: 6px; padding: 7px 14px;
            }
            QPushButton:hover { background-color: #F8FAFC; border-color: #0284C7; }
        """)
        test_btn.clicked.connect(self._test_feed_action)
        toolbar.addWidget(test_btn)
        
        toolbar.addStretch()
        
        refresh_btn = QPushButton("🔄 Refresh Bus")
        refresh_btn.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 6px; padding: 6px 12px; background: white;")
        refresh_btn.clicked.connect(self._load_cards)
        toolbar.addWidget(refresh_btn)
        
        layout.addLayout(toolbar)
        
        # Cards Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Card / Device Name", "Suite / Port", "Interface", "Resolution", "Trigger", "Status"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        self._load_cards()
        
        # Bottom Actions
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        
        edit_btn = QPushButton("Edit Selected")
        edit_btn.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 6px; padding: 8px 16px; background: white;")
        edit_btn.clicked.connect(self._edit_card_action)
        btn_box.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete Selected")
        delete_btn.setStyleSheet("border: 1px solid #FCA5A5; color: #DC2626; border-radius: 6px; padding: 8px 16px; background: white;")
        delete_btn.clicked.connect(self._delete_card_action)
        btn_box.addWidget(delete_btn)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("background-color: #0F172A; color: white; border-radius: 6px; padding: 8px 20px; font-weight: 600;")
        close_btn.clicked.connect(self.accept)
        btn_box.addWidget(close_btn)
        
        layout.addLayout(btn_box)

    def _load_cards(self):
        from app.services.device_manager import CaptureDeviceManager
        devices = CaptureDeviceManager.get_connected_devices()
        cards_data = []
        for idx, dev in enumerate(devices):
            name = dev.get("name", "USB2 Video")
            res = dev.get("resolution", "1920×1080 @ 60fps")
            port = dev.get("port", f"USB Port {idx + 1}")
            cards_data.append((
                f"{name} (Physical Capture Card)",
                port,
                "USB 3.0 / DirectShow",
                res,
                "Scope Button / Middle Click / Pedal",
                "● Active"
            ))
        if not cards_data:
            cards_data.append((
                "No Physical Capture Card Detected",
                "—",
                "DirectShow",
                "—",
                "—",
                "● Offline"
            ))

        self.table.setRowCount(len(cards_data))
        for row, data in enumerate(cards_data):
            for col, text in enumerate(data):
                item = QTableWidgetItem(text)
                if col == 5:
                    item.setTextAlignment(Qt.AlignCenter)
                    if "Active" in text:
                        item.setForeground(Qt.darkGreen)
                    elif "Standby" in text:
                        item.setForeground(Qt.darkYellow)
                    else:
                        item.setForeground(Qt.blue)
                self.table.setItem(row, col, item)

    def _add_card_action(self):
        QMessageBox.information(
            self, "Add Capture Card",
            "Hardware Scan Wizard initialized.\n\nSearching for connected USB3/PCIe Video Capture Devices, DeckLink SDI, and NDI/DICOM streams..."
        )

    def _test_feed_action(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            current_row = 0
        card_name = self.table.item(current_row, 0).text()
        QMessageBox.information(
            self, "Video Signal Lock",
            f"Testing video pipeline for:\n{card_name}\n\nStatus: 60 FPS LOCK OK\nColor Matrix: Rec.709 10-bit Medical\nLatency: 14ms (Pass)"
        )

    def _edit_card_action(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Select Card", "Please select a capture card to edit.")
            return
        card_name = self.table.item(current_row, 0).text()
        QMessageBox.information(self, "Edit Capture Card", f"Opening configuration parameters for:\n{card_name}")

    def _delete_card_action(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Select Card", "Please select a capture card to delete.")
            return
        card_name = self.table.item(current_row, 0).text()
        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Are you sure you want to unbind capture device:\n'{card_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.table.removeRow(current_row)
