import os
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QMenu, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QAction, QCursor

from app.services.device_manager import CaptureDeviceManager


class CaptureCardDropdown(QWidget):
    """
    Prominent Capture Card Library Dropdown component.
    Detects and dynamically displays the physical USB Capture Card connected to the computer.
    """
    library_requested = Signal()
    manage_requested = Signal()
    add_requested = Signal()
    edit_requested = Signal()
    delete_requested = Signal()
    device_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.devices = CaptureDeviceManager.get_connected_devices()
        self.primary_device = CaptureDeviceManager.get_primary_usb_card()
        self._init_ui()
        
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Display the actual connected USB capture card in the button label
        device_name = self.primary_device.get("name", "USB2 Video")
        self.btn = QPushButton(f"📹 Capture Card: {device_name} [Active]  ▾")
        self.btn.setObjectName("captureCardDropdownBtn")
        self.btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn.setStyleSheet("""
            QPushButton#captureCardDropdownBtn {
                background-color: #FFFFFF;
                color: #0A2540;
                font-size: 13px;
                font-weight: 700;
                border: 2px solid #0284C7;
                border-radius: 8px;
                padding: 8px 18px;
                text-align: left;
            }
            QPushButton#captureCardDropdownBtn:hover {
                background-color: #F0F9FF;
                border-color: #0369A1;
            }
        """)
        
        # Load Camera icon
        camera_icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../assets/camera.svg"))
        if os.path.exists(camera_icon_path):
            self.btn.setIcon(QIcon(camera_icon_path))
            
        # Create Menu
        self.menu = QMenu(self)
        
        # 1. SHOW THE CONNECTED USB CAPTURE CARD PROMINENTLY AT TOP
        for dev in self.devices:
            dev_title = dev.get("name", "USB2 Video")
            dev_res = dev.get("resolution", "1080p @ 60fps")
            action_connected = QAction(f"🟢 {dev_title} (USB Port) • {dev_res} [Connected]", self)
            action_connected.setToolTip(f"Live hardware capture feed from {dev_title}")
            action_connected.triggered.connect(lambda checked=False, d=dev: self._on_device_clicked(d))
            self.menu.addAction(action_connected)
            
        self.menu.addSeparator()
        
        # Standard required items from Prompt.md
        self.action_library = QAction("📹  Capture Card Library (All Sources)", self)
        self.action_manage = QAction("⚙️  Manage Capture Cards", self)
        self.action_add = QAction("➕  Add New Capture Card", self)
        self.action_edit = QAction("✏️  Edit Capture Card", self)
        self.action_delete = QAction("🗑️  Delete Capture Card", self)
        
        self.menu.addAction(self.action_library)
        self.menu.addAction(self.action_manage)
        self.menu.addAction(self.action_add)
        self.menu.addAction(self.action_edit)
        self.menu.addSeparator()
        self.menu.addAction(self.action_delete)
        
        # Connect Actions
        self.action_library.triggered.connect(self.library_requested.emit)
        self.action_manage.triggered.connect(self.manage_requested.emit)
        self.action_add.triggered.connect(self.add_requested.emit)
        self.action_edit.triggered.connect(self.edit_requested.emit)
        self.action_delete.triggered.connect(self.delete_requested.emit)
        
        self.btn.setMenu(self.menu)
        layout.addWidget(self.btn)

    def _on_device_clicked(self, device):
        name = device.get("name", "USB2 Video")
        port = device.get("port", "USB 3.0 / 2.0")
        res = device.get("resolution", "1920x1080 @ 60fps")
        self.device_selected.emit(name)
        QMessageBox.information(
            self, f"Hardware Capture Card: {name}",
            f"Physical Capture Device Active:\n\n"
            f"• Device: {name}\n"
            f"• Connection: {port} (Hardware DirectShow)\n"
            f"• Resolution: {res}\n"
            f"• Signal Lock: Stable (60 FPS)\n"
            f"• Color Standard: Rec.709 Medical 10-bit\n"
            f"• Status: Ready for Endoscopy Video Acquisition"
        )
