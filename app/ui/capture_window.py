"""
Endocare - Clinical Endoscopy Capture Workstation
Clinical High-Definition Live Capture and Diagnostic Workstation.

Features:
- Real-time DirectShow hardware video grabber (USB2 Video capture card) with background thread
- Seamless fallback to high-definition standby HUD or clinical tissue simulation
- Instant capture saving to database and disk with shutter flash animation
- Captured Images Tray on the left with frame selection, delete icon, and zoom preview
- Live Reporting side pane with full rich text toolbar, font sizing, and endoscopy templates popup
- Bottom adjustment bar with S-Video / Composite selector, 17-standard Video Type dropdown,
  Resolution selector, real-time Brightness, Contrast, Hue, Saturation sliders, and Reset Color
- Keyboard shortcuts: Space/Enter/F2 for Capture, F11 for Full Screen Preview, F9 for Vessel+, F8 for Vision X
"""

import os
import sys
import subprocess
import time
import math
import datetime
from typing import Optional, Dict, Any, List

import cv2
import numpy as np

from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QFrame, QCheckBox, QComboBox, QSlider, QScrollArea,
    QTextEdit, QToolButton, QMessageBox, QFileDialog, QApplication,
    QSizePolicy, QMenu, QScrollBar
)
from PySide6.QtCore import Qt, QTimer, QTime, QRect, QPoint, QSize, Signal, QThread, QEvent
from PySide6.QtGui import (
    QImage, QPixmap, QColor, QFont, QPainter, QPen, QBrush,
    QRadialGradient, QLinearGradient, QTextListFormat, QKeySequence,
    QShortcut, QIcon, QPolygon
)

from app.services.database import DatabaseService
from app.core.paths import get_asset_path, get_captures_dir
from app.services.device_manager import CaptureDeviceManager


class HomeButton(QPushButton):
    """
    Custom 3D Metallic Circular Home Button.
    Faithfully renders the metallic beveled circular button with crisp white house icon
    from Demo/Screenshot 2026-09-20 003705.png.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(44, 44)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Return to Main Launcher (Close)")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        w = self.width()
        h = self.height()
        r = min(w, h) / 2.0 - 2.0
        cx = w / 2.0
        cy = h / 2.0

        # Outer silver beveled ring
        grad_ring = QLinearGradient(0, 0, w, h)
        if self.isDown():
            grad_ring.setColorAt(0.0, QColor("#505050"))
            grad_ring.setColorAt(1.0, QColor("#909090"))
        elif self.underMouse():
            grad_ring.setColorAt(0.0, QColor("#FFFFFF"))
            grad_ring.setColorAt(1.0, QColor("#708090"))
        else:
            grad_ring.setColorAt(0.0, QColor("#D0D0D0"))
            grad_ring.setColorAt(1.0, QColor("#606060"))

        painter.setPen(QPen(QColor("#202020"), 1))
        painter.setBrush(QBrush(grad_ring))
        painter.drawEllipse(QPoint(int(cx), int(cy)), int(r), int(r))

        # Inner dark gradient circle
        inner_r = r - 3.5
        grad_inner = QRadialGradient(cx - 2, cy - 2, inner_r)
        if self.isDown():
            grad_inner.setColorAt(0.0, QColor("#111111"))
            grad_inner.setColorAt(1.0, QColor("#000000"))
        elif self.underMouse():
            grad_inner.setColorAt(0.0, QColor("#334455"))
            grad_inner.setColorAt(1.0, QColor("#101824"))
        else:
            grad_inner.setColorAt(0.0, QColor("#444444"))
            grad_inner.setColorAt(0.8, QColor("#222222"))
            grad_inner.setColorAt(1.0, QColor("#151515"))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(grad_inner))
        painter.drawEllipse(QPoint(int(cx), int(cy)), int(inner_r), int(inner_r))

        # House Icon
        painter.setPen(QPen(QColor("#FFFFFF"), 2.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.NoBrush)

        # Roof triangle
        roof = QPolygon([
            QPoint(int(cx), int(cy - 9)),
            QPoint(int(cx - 10), int(cy + 1)),
            QPoint(int(cx + 10), int(cy + 1))
        ])
        painter.drawPolyline(roof)

        # Chimney
        painter.drawLine(int(cx + 6), int(cy - 5), int(cx + 6), int(cy - 8))

        # House walls
        painter.drawLine(int(cx - 7), int(cy + 1), int(cx - 7), int(cy + 10))
        painter.drawLine(int(cx + 7), int(cy + 1), int(cx + 7), int(cy + 10))
        painter.drawLine(int(cx - 7), int(cy + 10), int(cx + 7), int(cy + 10))

        # Door
        painter.drawLine(int(cx - 2), int(cy + 10), int(cx - 2), int(cy + 5))
        painter.drawLine(int(cx - 2), int(cy + 5), int(cx + 2), int(cy + 5))
        painter.drawLine(int(cx + 2), int(cy + 5), int(cx + 2), int(cy + 10))


class VideoCaptureThread(QThread):
    """
    Background worker thread polling DirectShow video frames at up to 60 FPS.
    Prevents any UI stutter and cleanly handles connect/disconnect.
    """
    frame_ready = Signal(np.ndarray)

    def __init__(self, device_index=0, parent=None):
        super().__init__(parent)
        self.device_index = device_index
        self._running = False
        self._cap = None

    def run(self):
        self._running = True
        try:
            self._cap = cv2.VideoCapture(self.device_index, cv2.CAP_DSHOW)
            if self._cap.isOpened():
                self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                self._cap.set(cv2.CAP_PROP_FPS, 60)
        except Exception as e:
            print(f"Error opening DirectShow device {self.device_index}: {e}")

        while self._running:
            if self._cap and self._cap.isOpened():
                ret, frame = self._cap.read()
                if ret and frame is not None:
                    self.frame_ready.emit(frame)
                else:
                    self.msleep(30)
            else:
                self.msleep(50)

        if self._cap:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None

    def stop(self):
        self._running = False
        self.wait(400)


class LiveVideoViewport(QLabel):
    """
    High-performance live endoscopic viewport.
    Renders live DirectShow grabber frames from the physical USB2 Video card,
    with authentic fallback to clinical standby HUD or clinical tissue simulation.
    """
    frame_captured = Signal(QImage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("liveViewport")
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(480, 320)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("background-color: #000000; border: none;")

        self._assets_dir = get_asset_path()
        
        # Color adjustment parameters (0 to 100, default 50)
        self.brightness = 50
        self.contrast = 50
        self.hue = 50
        self.saturation = 50

        # Filter states
        self.filter_vessel_plus = False   # (F9) Vessel+ NBI cyan/green boost
        self.filter_vision_x = False      # (F8) Vision X contrast/sharpness
        self.filter_crop_onthefly = False  # OnTheFly cropping (unchecked default)
        self.filter_invert_gray = False    # GrayScale-Pixels Inverter (unchecked default)

        # Hardware feed state
        self._sim_tick = 0
        self._is_recording = False
        self._record_writer = None
        self._record_path = None
        self._record_w = 1280
        self._record_h = 720
        self._frames_written = 0
        self._patient_info = {}

        # Last received camera frame
        self._latest_cv_frame = None

        # Flash animation on capture
        self._flash_opacity = 0.0
        self._flash_timer = QTimer(self)
        self._flash_timer.timeout.connect(self._decay_flash)

        # Hardware capture thread
        self._cap_thread = VideoCaptureThread(device_index=0, parent=self)
        self._cap_thread.frame_ready.connect(self._on_new_camera_frame)
        self._cap_thread.start()

        # 30-40 FPS Render loop
        self._render_timer = QTimer(self)
        self._render_timer.timeout.connect(self._on_tick)
        self._render_timer.start(33)

    def _on_new_camera_frame(self, frame: np.ndarray):
        self._latest_cv_frame = frame
        if self._is_recording and self._record_writer is not None:
            try:
                rec_frame = frame.copy()
                if self.filter_crop_onthefly:
                    ch_h, ch_w = rec_frame.shape[:2]
                    cy = int(ch_h * 0.04)
                    cx = int(ch_w * 0.04)
                    if cy > 0 and cx > 0:
                        rec_frame = rec_frame[cy:ch_h - cy, cx:ch_w - cx]
                if self.filter_invert_gray:
                    gray = cv2.cvtColor(rec_frame, cv2.COLOR_BGR2GRAY)
                    inv = cv2.bitwise_not(gray)
                    rec_frame = cv2.cvtColor(inv, cv2.COLOR_GRAY2BGR)

                if self.brightness != 50 or self.contrast != 50:
                    alpha = self.contrast / 50.0
                    beta = (self.brightness - 50) * 2.0
                    rec_frame = np.clip(alpha * rec_frame.astype(np.float32) + beta, 0, 255).astype(np.uint8)

                if rec_frame.shape[1] != self._record_w or rec_frame.shape[0] != self._record_h:
                    rec_frame = cv2.resize(rec_frame, (self._record_w, self._record_h))

                self._record_writer.write(rec_frame)
                self._frames_written += 1
            except Exception:
                pass

    def closeEvent(self, event):
        self.stop_camera()
        super().closeEvent(event)

    def stop_camera(self):
        if hasattr(self, '_render_timer') and self._render_timer.isActive():
            self._render_timer.stop()
        if hasattr(self, '_flash_timer') and self._flash_timer.isActive():
            self._flash_timer.stop()
        if hasattr(self, '_cap_thread') and self._cap_thread:
            self._cap_thread.stop()
            self._cap_thread.wait(1000)
        if self._record_writer:
            try:
                self._record_writer.release()
            except Exception:
                pass
            self._record_writer = None

    def set_patient_info(self, info: dict):
        self._patient_info = info
        self.update()

    def set_adjustments(self, brightness: int, contrast: int, hue: int, saturation: int):
        self.brightness = brightness
        self.contrast = contrast
        self.hue = hue
        self.saturation = saturation
        self.update()

    def set_filters(self, vessel_plus: bool, vision_x: bool, crop: bool, invert_gray: bool):
        self.filter_vessel_plus = vessel_plus
        self.filter_vision_x = vision_x
        self.filter_crop_onthefly = crop
        self.filter_invert_gray = invert_gray
        self.update()

    def trigger_capture_flash(self):
        self._flash_opacity = 0.90
        if not self._flash_timer.isActive():
            self._flash_timer.start(25)
        self.update()

    def _decay_flash(self):
        self._flash_opacity -= 0.14
        if self._flash_opacity <= 0.0:
            self._flash_opacity = 0.0
            self._flash_timer.stop()
        self.update()

    def _on_tick(self):
        self._sim_tick += 1
        if self._is_recording and self._record_writer is not None and self._latest_cv_frame is None:
            try:
                qimg = self.grab_current_frame()
                if not qimg.isNull():
                    if qimg.format() not in (QImage.Format_RGB32, QImage.Format_ARGB32):
                        qimg = qimg.convertToFormat(QImage.Format_RGB32)
                    arr = np.frombuffer(qimg.bits(), dtype=np.uint8).reshape((qimg.height(), qimg.width(), 4))
                    bgr_frame = cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)
                    if bgr_frame.shape[1] != self._record_w or bgr_frame.shape[0] != self._record_h:
                        bgr_frame = cv2.resize(bgr_frame, (self._record_w, self._record_h))
                    self._record_writer.write(bgr_frame)
                    self._frames_written += 1
            except Exception:
                pass
        self.update()

    def start_recording(self, output_path: str):
        self._record_path = output_path
        self._frames_written = 0

        # Match camera dimensions if available, or default to 1280x720 HD
        if self._latest_cv_frame is not None:
            h, w = self._latest_cv_frame.shape[:2]
        else:
            w, h = 1280, 720
        self._record_w = w
        self._record_h = h

        # Universally supported MJPG for .avi on Windows, or mp4v for .mp4
        if output_path.lower().endswith(".mp4"):
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        else:
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')

        self._record_writer = cv2.VideoWriter(output_path, fourcc, 30.0, (w, h))
        self._is_recording = True

    def stop_recording(self) -> Optional[str]:
        self._is_recording = False
        if self._record_writer:
            if getattr(self, '_frames_written', 0) == 0:
                try:
                    qimg = self.grab_current_frame()
                    if not qimg.isNull():
                        if qimg.format() not in (QImage.Format_RGB32, QImage.Format_ARGB32):
                            qimg = qimg.convertToFormat(QImage.Format_RGB32)
                        arr = np.frombuffer(qimg.bits(), dtype=np.uint8).reshape((qimg.height(), qimg.width(), 4))
                        bgr_frame = cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)
                        if bgr_frame.shape[1] != self._record_w or bgr_frame.shape[0] != self._record_h:
                            bgr_frame = cv2.resize(bgr_frame, (self._record_w, self._record_h))
                        for _ in range(15):
                            self._record_writer.write(bgr_frame)
                except Exception:
                    pass
            try:
                self._record_writer.release()
            except Exception:
                pass
            self._record_writer = None
        return self._record_path

    def is_hardware_signal_active(self) -> bool:
        return self._latest_cv_frame is not None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        w = self.width()
        h = self.height()

        # 1. Base Black Video Screen
        painter.fillRect(0, 0, w, h, QColor("#000000"))

        has_active_signal = self.is_hardware_signal_active()

        # 2. Render Live Feed or Standby HUD
        if has_active_signal and self._latest_cv_frame is not None:
            frame = self._latest_cv_frame.copy()

            # Apply OnTheFly Image Cropping (4% perimeter crop to remove camera borders)
            if self.filter_crop_onthefly:
                ch_h, ch_w = frame.shape[:2]
                crop_y = int(ch_h * 0.04)
                crop_x = int(ch_w * 0.04)
                if crop_y > 0 and crop_x > 0:
                    frame = frame[crop_y:ch_h - crop_y, crop_x:ch_w - crop_x]

            # Apply GrayScale-Pixels Inverter
            if self.filter_invert_gray:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                inv = cv2.bitwise_not(gray)
                rgb_frame = cv2.cvtColor(inv, cv2.COLOR_GRAY2RGB)
            else:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            fh, fw, ch = rgb_frame.shape
            bytes_per_line = ch * fw
            qimg = QImage(rgb_frame.data, fw, fh, bytes_per_line, QImage.Format_RGB888)
            pix = QPixmap.fromImage(qimg)
            scaled = pix.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            ox = (w - scaled.width()) // 2
            oy = (h - scaled.height()) // 2
            painter.drawPixmap(ox, oy, scaled)
        else:
            # Standby mode when no camera frame is received - Clean medical HUD, never dummy images
            painter.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
            painter.setPen(QColor("#64748B"))
            painter.drawText(QRect(0, h // 2 - 25, w, 30), Qt.AlignCenter, "STANDBY • NO VIDEO SIGNAL")
            painter.setFont(QFont("Segoe UI", 9))
            painter.setPen(QColor("#475569"))
            painter.drawText(QRect(0, h // 2 + 10, w, 20), Qt.AlignCenter, "DirectShow USB2 Capture Device Ready")

        # 3. Filters & Real-time Color Adjustments
        if self.filter_vessel_plus:
            painter.fillRect(0, 0, w, h, QColor(0, 200, 140, 55))

        if self.filter_vision_x:
            painter.fillRect(0, 0, w, h, QColor(20, 170, 245, 45))

        # Brightness / Contrast color grading
        b_delta = self.brightness - 50
        if b_delta > 0:
            painter.fillRect(0, 0, w, h, QColor(255, 255, 255, int(b_delta * 2.0)))
        elif b_delta < 0:
            painter.fillRect(0, 0, w, h, QColor(0, 0, 0, int(abs(b_delta) * 2.4)))

        s_delta = self.saturation - 50
        if s_delta > 0:
            painter.fillRect(0, 0, w, h, QColor(255, 120, 120, int(s_delta * 0.45)))
        elif s_delta < 0:
            painter.fillRect(0, 0, w, h, QColor(128, 128, 128, int(abs(s_delta) * 0.9)))

        # 4. Authentic Green Tracking Markers from Screenshot 003705.png
        # Marker 1 (upper-left region)
        marker1_y = int(h * 0.20)
        painter.fillRect(int(w * 0.048), marker1_y, 4, 4, QColor("#00FF66"))

        # Marker 2 (mid-lower region)
        marker2_y = int(h * 0.62)
        painter.fillRect(int(w * 0.27), marker2_y, 4, 4, QColor("#00FF66"))

        # 5. Top Left & Top Right Live HUD
        # Top-left HUD: Patient ID, Name, Date, Time
        painter.setFont(QFont("Segoe UI", 9, QFont.DemiBold))
        painter.setPen(QColor("#E2E8F0"))
        curr_time = QTime.currentTime().toString("HH:mm:ss")
        curr_date = datetime.date.today().strftime("%d-%b-%Y")
        patient_id = self._patient_info.get('auto_id', '9')
        if str(patient_id).startswith("0000000"):
            patient_id = str(patient_id).replace("0000000", "")
        patient_name = self._patient_info.get('name', 'Nayem Islam')
        patient_str = f"ID: {patient_id}  |  {patient_name}  |  {curr_date} {curr_time}"
        painter.drawText(16, 24, patient_str)

        # Top-right HUD: Video status
        if self._is_recording:
            if (self._sim_tick // 15) % 2 == 0:
                painter.setPen(QColor("#EF4444"))
                painter.setBrush(QBrush(QColor("#EF4444")))
                painter.drawEllipse(w - 110, 14, 10, 10)
                painter.drawText(w - 95, 24, "REC ● LIVE")
        else:
            painter.setPen(QColor("#38BDF8"))
            status_text = "USB2 LIVE 60 FPS" if self.is_hardware_signal_active() else "DIRECTSHOW STANDBY"
            painter.drawText(w - 150, 24, status_text)

        # 7. Shutter Flash Effect on Capture
        if self._flash_opacity > 0.0:
            alpha = int(self._flash_opacity * 255)
            painter.fillRect(0, 0, w, h, QColor(255, 255, 255, alpha))

    def grab_current_frame(self) -> QImage:
        """Captures the current viewport display as a clean, high-resolution QImage."""
        if self._latest_cv_frame is not None:
            frame = self._latest_cv_frame.copy()
            if self.filter_crop_onthefly:
                ch_h, ch_w = frame.shape[:2]
                crop_y = int(ch_h * 0.04)
                crop_x = int(ch_w * 0.04)
                if crop_y > 0 and crop_x > 0:
                    frame = frame[crop_y:ch_h - crop_y, crop_x:ch_w - crop_x]
            if self.filter_invert_gray:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                inv = cv2.bitwise_not(gray)
                rgb_frame = cv2.cvtColor(inv, cv2.COLOR_GRAY2RGB)
            else:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if self.brightness != 50 or self.contrast != 50:
                alpha = self.contrast / 50.0
                beta = (self.brightness - 50) * 2.0
                rgb_frame = np.clip(alpha * rgb_frame.astype(np.float32) + beta, 0, 255).astype(np.uint8)

            fh, fw, ch = rgb_frame.shape
            bytes_per_line = ch * fw
            qimg = QImage(rgb_frame.data, fw, fh, bytes_per_line, QImage.Format_RGB888)
            return qimg.copy()

        old_flash = self._flash_opacity
        self._flash_opacity = 0.0
        pix = self.grab()
        self._flash_opacity = old_flash
        return pix.toImage()


class CaptureWindow(QDialog):
    """
    Endocare 2.42 Live Capture Workstation.
    Clinical High-Definition Live Capture, Image Management, and Reporting Workstation.
    """
    def __init__(self, patient_data: Optional[Dict[str, Any]] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Endocare 2.42 • Live Capture Workstation")
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        
        # State for dragging & window geometry restoration
        self._drag_pos = QPoint()
        self._is_dragging = False
        self._normal_geometry = None
        
        # Load patient
        self.db = DatabaseService.get_instance()
        self.patient_data = patient_data or self._get_fallback_patient()
        
        self._assets_dir = get_asset_path()
        self._captures_dir = get_captures_dir()
        
        self.captured_images: List[Dict[str, Any]] = []
        self._selected_card_widget = None
        self._auto_capture_timer = QTimer(self)
        self._auto_capture_timer.timeout.connect(self._handle_auto_capture)

        self._apply_screen_geometry()
        self._init_ui()
        self._setup_shortcuts()
        self._load_patient_thumbnails()

    def _get_fallback_patient(self) -> Dict[str, Any]:
        """Returns the canonical patient from reference screenshot (Nayem Islam, ID 9)."""
        patients = self.db.get_patients(limit=15)
        for p in patients:
            if "nayem" in p.get("name", "").lower():
                return p
        return {
            "auto_id": "9",
            "name": "Nayem Islam",
            "mrn": "ENDO-0042",
            "age": 24,
            "sex": "Male",
            "proc": "UPPER GI ENDOSCOPY",
            "doctor": "Dr. Sarah Jenkins"
        }

    def _apply_screen_geometry(self):
        screen = QApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else None
        if avail:
            self.setGeometry(avail)
        self.showMaximized()

    def showEvent(self, event):
        super().showEvent(event)
        if not getattr(self, '_initial_show_done', False):
            self._initial_show_done = True
            screen = self.screen() or QApplication.primaryScreen()
            avail = screen.availableGeometry() if screen else None
            if avail:
                self.setGeometry(avail)
            self.showMaximized()
            if hasattr(self, 'btn_win_max'):
                self.btn_win_max.setText("🗗")
                self.btn_win_max.setToolTip("Restore Down")

    def closeEvent(self, event):
        if hasattr(self, 'viewport'):
            self.viewport.stop_camera()
        super().closeEvent(event)

    def reject(self):
        if hasattr(self, 'viewport'):
            self.viewport.stop_camera()
        super().reject()

    def changeEvent(self, event):
        """Keep Full Screen / Restore button icon and tooltip synchronized with window state."""
        if event.type() == QEvent.WindowStateChange:
            if hasattr(self, 'btn_win_max'):
                if self.isFullScreen():
                    self.btn_win_max.setText("🗗")
                    self.btn_win_max.setToolTip("Restore Down")
                else:
                    self.btn_win_max.setText("🗖")
                    self.btn_win_max.setToolTip("Full Screen")
        super().changeEvent(event)

    def mousePressEvent(self, event):
        """Enable dragging the frameless window when in restored/normal mode."""
        if not self.isFullScreen() and event.button() == Qt.LeftButton:
            if hasattr(self, 'title_bar') and event.position().y() <= self.title_bar.height():
                self._is_dragging = True
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Move the window while dragging title bar."""
        if self._is_dragging and (event.buttons() & Qt.LeftButton):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._is_dragging = False
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Double clicking title bar toggles between Full Screen and Restored."""
        if hasattr(self, 'title_bar') and event.position().y() <= self.title_bar.height():
            if event.button() == Qt.LeftButton:
                self._toggle_fullscreen()
                event.accept()
                return
        super().mouseDoubleClickEvent(event)

    def _setup_shortcuts(self):
        QShortcut(QKeySequence(Qt.Key_Space), self, self._handle_capture_image)
        QShortcut(QKeySequence(Qt.Key_Return), self, self._handle_capture_image)
        QShortcut(QKeySequence(Qt.Key_F2), self, self._handle_capture_image)
        QShortcut(QKeySequence(Qt.Key_F11), self, self._toggle_fullscreen)
        QShortcut(QKeySequence(Qt.Key_F9), self, self._toggle_vessel_plus)
        QShortcut(QKeySequence(Qt.Key_F8), self, self._toggle_vision_x)

    def _init_ui(self):
        self.setObjectName("endocareCaptureRoot")
        check_icon_path = os.path.abspath(os.path.join(self._assets_dir, "checkbox_check.png")).replace("\\", "/")
        self.setStyleSheet(f"""
            QDialog#endocareCaptureRoot {{
                background-color: #262626;
                color: #FFFFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QLabel {{
                color: #FFFFFF;
            }}
            QCheckBox {{
                color: #FFFFFF;
                font-size: 11px;
                font-weight: bold;
                spacing: 6px;
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border: 1px solid #000000;
                background: #FFFFFF;
                border-radius: 2px;
            }}
            QCheckBox::indicator:hover {{
                border: 1px solid #38BDF8;
            }}
            QCheckBox::indicator:checked {{
                background: #FFFFFF;
                border: 1px solid #000000;
                image: url("{check_icon_path}");
            }}
            QComboBox {{
                background: #FFFFFF;
                color: #000000;
                border: 1px solid #71717A;
                font-size: 11px;
                font-weight: bold;
                padding: 1px 3px;
            }}
            QComboBox QAbstractItemView {{
                background: #FFFFFF;
                color: #000000;
                selection-background-color: #0284C7;
                selection-color: #FFFFFF;
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 2)
        main_layout.setSpacing(2)

        # 0. SLEEK CUSTOM TITLE BAR (Minimize, Full Screen/Restore, Close)
        self._build_title_bar(main_layout)

        # Clinical Workspace Body Container with side padding
        body_widget = QWidget()
        body_layout = QVBoxLayout(body_widget)
        body_layout.setContentsMargins(4, 0, 4, 0)
        body_layout.setSpacing(2)

        # 1. TOP CONTROL BAR
        self._build_top_control_bar(body_layout)

        # 2. PATIENT CONTEXT SUB-BAR
        self._build_patient_subbar(body_layout)

        # 3. CENTER SPLITTER (Tray | Live Viewport | Live Reporting)
        self._build_workspace_center(body_layout)

        # 4. BOTTOM VIDEO & COLOR ADJUSTMENT BAR
        self._build_bottom_adjustment_bar(body_layout)

        main_layout.addWidget(body_widget, 1)
        self._sync_filters()

    def _build_title_bar(self, parent_layout: QVBoxLayout):
        """
        Sleek clinical title bar containing window title, live patient status,
        and window controls: Minimize (—), Full Screen/Restore (🗖/🗗), Close (✕).
        """
        self.title_bar = QFrame()
        self.title_bar.setObjectName("captureTitleBar")
        self.title_bar.setFixedHeight(34)
        self.title_bar.setStyleSheet("""
            QFrame#captureTitleBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #25282C, stop:1 #16181B);
                border-bottom: 1px solid #33383F;
            }
            QLabel {
                color: #CBD5E1;
            }
            QPushButton[class="winCtrlBtn"] {
                background: transparent;
                color: #CBD5E1;
                border: none;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                font-weight: 600;
                padding: 0px;
            }
            QPushButton[class="winCtrlBtn"]:hover {
                background-color: rgba(255, 255, 255, 0.15);
                color: #FFFFFF;
            }
            QPushButton[class="winCtrlBtn"]:pressed {
                background-color: rgba(255, 255, 255, 0.25);
            }
            QPushButton#winCtrlClose {
                background: transparent;
                color: #CBD5E1;
                border: none;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton#winCtrlClose:hover {
                background-color: #E81123;
                color: #FFFFFF;
            }
            QPushButton#winCtrlClose:pressed {
                background-color: #C42B1C;
                color: #FFFFFF;
            }
        """)

        title_lay = QHBoxLayout(self.title_bar)
        title_lay.setContentsMargins(10, 0, 0, 0)
        title_lay.setSpacing(8)

        # Brand Logo / Icon
        logo_icon = QLabel()
        logo_path = os.path.join(self._assets_dir, "logo.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(18, 18, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_icon.setPixmap(pix)
        title_lay.addWidget(logo_icon)

        # App & Window Title
        lbl_title = QLabel("Endocare 2.42  •  Live Capture Workstation")
        lbl_title.setStyleSheet("color: #F1F5F9; font-size: 12px; font-weight: 700; letter-spacing: 0.5px;")
        title_lay.addWidget(lbl_title)

        # Patient Info Tag
        pat_name = self.patient_data.get("name", "Nayem Islam")
        pat_id = str(self.patient_data.get("auto_id", "9")).replace("0000000", "")
        self.lbl_title_status = QLabel(f"● LIVE  [{pat_id}] {pat_name}")
        self.lbl_title_status.setStyleSheet(
            "color: #10B981; font-size: 11px; font-weight: 600; padding: 2px 8px; "
            "background: rgba(16, 185, 129, 0.12); border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.3);"
        )
        title_lay.addWidget(self.lbl_title_status)

        # Stretch to fill the middle draggable space
        title_lay.addStretch()

        # Window Controls: Minimize (—), Full Screen/Restore (🗖/🗗), Close (✕)
        ctrl_box = QHBoxLayout()
        ctrl_box.setSpacing(0)
        ctrl_box.setContentsMargins(0, 0, 0, 0)

        # 1. Minimize (—)
        self.btn_win_min = QPushButton("—")
        self.btn_win_min.setProperty("class", "winCtrlBtn")
        self.btn_win_min.setFixedSize(46, 33)
        self.btn_win_min.setToolTip("Minimize")
        self.btn_win_min.setCursor(Qt.PointingHandCursor)
        self.btn_win_min.clicked.connect(self.showMinimized)
        ctrl_box.addWidget(self.btn_win_min)

        # 2. Full Screen / Restore (🗖 / 🗗)
        is_fs = self.isFullScreen()
        self.btn_win_max = QPushButton("🗗" if is_fs else "🗖")
        self.btn_win_max.setProperty("class", "winCtrlBtn")
        self.btn_win_max.setFixedSize(46, 33)
        self.btn_win_max.setToolTip("Restore Down" if is_fs else "Full Screen")
        self.btn_win_max.setCursor(Qt.PointingHandCursor)
        self.btn_win_max.clicked.connect(self._toggle_fullscreen)
        ctrl_box.addWidget(self.btn_win_max)

        # 3. Close (✕)
        self.btn_win_close = QPushButton("✕")
        self.btn_win_close.setObjectName("winCtrlClose")
        self.btn_win_close.setFixedSize(48, 33)
        self.btn_win_close.setToolTip("Close (✕)")
        self.btn_win_close.setCursor(Qt.PointingHandCursor)
        self.btn_win_close.clicked.connect(self.close)
        ctrl_box.addWidget(self.btn_win_close)

        title_lay.addLayout(ctrl_box)
        parent_layout.addWidget(self.title_bar)

    def _build_top_control_bar(self, parent_layout: QVBoxLayout):
        top_bar = QFrame()
        top_bar.setObjectName("topControlBar")
        top_bar.setFixedHeight(66)
        top_bar.setStyleSheet("""
            QFrame#topControlBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4E4E4E, stop:0.06 #323232, stop:0.5 #202020, stop:0.95 #121212, stop:1 #080808);
                border-top: 1px solid #707070;
                border-bottom: 1px solid #141414;
                border-left: 1px solid #404040;
                border-right: 1px solid #404040;
            }
        """)
        top_lay = QHBoxLayout(top_bar)
        top_lay.setContentsMargins(8, 4, 8, 4)
        top_lay.setSpacing(10)

        # === Group A: 3 Checkboxes ===
        chk_box = QVBoxLayout()
        chk_box.setSpacing(2)
        chk_box.setAlignment(Qt.AlignVCenter)
        self.chk_crop = QCheckBox("OnTheFly Image Cropping")
        self.chk_crop.setChecked(False)
        self.chk_crop.toggled.connect(self._sync_filters)

        self.chk_invert = QCheckBox("GrayScale-Pixels Inverter")
        self.chk_invert.setChecked(False)
        self.chk_invert.toggled.connect(self._sync_filters)

        self.chk_auto_capture = QCheckBox("Automatic Image Capture")
        self.chk_auto_capture.setChecked(False)
        self.chk_auto_capture.toggled.connect(self._toggle_auto_capture)

        chk_box.addWidget(self.chk_crop)
        chk_box.addWidget(self.chk_invert)
        chk_box.addWidget(self.chk_auto_capture)
        top_lay.addLayout(chk_box)

        top_lay.addWidget(self._create_etched_sep())

        # === Group B: Mode Buttons (F9) Vessel + & (F8) Vision X ===
        vessel_box = QVBoxLayout()
        vessel_box.setSpacing(3)
        vessel_box.setAlignment(Qt.AlignVCenter)

        btn_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #D2D2D2);
                color: #000000;
                font-size: 11px;
                font-weight: 800;
                border: 1px solid #333333;
                border-radius: 3px;
                padding: 3px 8px;
            }
            QPushButton:hover {
                background: #FFFFFF;
            }
            QPushButton:pressed, QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #C5D8E8, stop:1 #9BBFD8);
                border: 1px solid #0369A1;
            }
        """

        self.btn_vessel = QPushButton("(F9) Vessel +")
        self.btn_vessel.setCheckable(True)
        self.btn_vessel.setFixedSize(94, 25)
        self.btn_vessel.setStyleSheet(btn_style)
        self.btn_vessel.setCursor(Qt.PointingHandCursor)
        self.btn_vessel.clicked.connect(self._toggle_vessel_plus)

        self.btn_vision = QPushButton("(F8) Vision X")
        self.btn_vision.setCheckable(True)
        self.btn_vision.setFixedSize(94, 25)
        self.btn_vision.setStyleSheet(btn_style)
        self.btn_vision.setCursor(Qt.PointingHandCursor)
        self.btn_vision.clicked.connect(self._toggle_vision_x)

        vessel_box.addWidget(self.btn_vessel)
        vessel_box.addWidget(self.btn_vision)
        top_lay.addLayout(vessel_box)

        top_lay.addWidget(self._create_etched_sep())

        # === Group C: Video Operations & Card Status ===
        vid_col = QVBoxLayout()
        vid_col.setSpacing(2)
        vid_col.setAlignment(Qt.AlignVCenter)

        vid_row = QHBoxLayout()
        vid_row.setSpacing(4)

        # Open Video (White button, Bold Green Text)
        self.btn_open_vid = QPushButton("Open Video")
        self.btn_open_vid.setFixedSize(84, 26)
        self.btn_open_vid.setCursor(Qt.PointingHandCursor)
        self.btn_open_vid.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #D2D2D2);
                color: #008000;
                font-size: 11px;
                font-weight: 800;
                border: 1px solid #333333;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #FFFFFF;
            }
        """)
        self.btn_open_vid.clicked.connect(self._handle_open_video)
        vid_row.addWidget(self.btn_open_vid)

        # Close Video (Light Grey Button, Disabled Text)
        self.btn_close_vid = QPushButton("Close Video")
        self.btn_close_vid.setFixedSize(82, 26)
        self.btn_close_vid.setCursor(Qt.PointingHandCursor)
        self.btn_close_vid.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F0F0F0, stop:1 #D8D8D8);
                color: #8C8C8C;
                font-size: 11px;
                font-weight: 700;
                border: 1px solid #444444;
                border-radius: 3px;
            }
            QPushButton:hover {
                color: #555555;
            }
        """)
        self.btn_close_vid.clicked.connect(self._handle_close_video)
        vid_row.addWidget(self.btn_close_vid)

        # Record Video with 3D Red Sphere Icon & Bold Red Text
        self.btn_rec_vid = QPushButton(" Record Video")
        self.btn_rec_vid.setIcon(self._create_red_sphere_icon())
        self.btn_rec_vid.setIconSize(QSize(14, 14))
        self.btn_rec_vid.setFixedSize(112, 26)
        self.btn_rec_vid.setCursor(Qt.PointingHandCursor)
        self.btn_rec_vid.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #D2D2D2);
                color: #CC0000;
                font-size: 11px;
                font-weight: 800;
                border: 1px solid #333333;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #FFF0F0;
            }
        """)
        self.btn_rec_vid.clicked.connect(self._toggle_recording)
        vid_row.addWidget(self.btn_rec_vid)

        vid_col.addLayout(vid_row)

        primary_card = CaptureDeviceManager.get_primary_usb_card()
        card_name = primary_card.get("name", "USB2 Video")
        self.lbl_card_status = QLabel(f"Capture Card: {card_name}")
        self.lbl_card_status.setAlignment(Qt.AlignCenter)
        self.lbl_card_status.setStyleSheet("color: #FFFFFF; font-size: 11px; font-weight: 700; margin-top: 1px;")
        vid_col.addWidget(self.lbl_card_status)
        top_lay.addLayout(vid_col)

        top_lay.addWidget(self._create_etched_sep())

        # === Group D: GIANT [Capture Image] BUTTON ===
        self.btn_capture = QPushButton("Capture\nImage")
        self.btn_capture.setFixedSize(88, 52)
        self.btn_capture.setCursor(Qt.PointingHandCursor)
        self.btn_capture.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:0.5 #E8E8E8, stop:1 #D0D0D0);
                color: #002060;
                font-size: 14px;
                font-weight: 900;
                border: 1.5px solid #222222;
                border-radius: 3px;
                line-height: 1.1;
            }
            QPushButton:hover {
                background: #FFFFFF;
                color: #003399;
                border-color: #000000;
            }
            QPushButton:pressed {
                background: #B8D0E8;
            }
        """)
        self.btn_capture.clicked.connect(self._handle_capture_image)
        top_lay.addWidget(self.btn_capture)

        top_lay.addWidget(self._create_etched_sep())

        # === Group E: Workflow Navigation Buttons (Write Report, Archive, New Patient) ===
        nav_lay = QHBoxLayout()
        nav_lay.setSpacing(6)

        sub_btn_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #D2D2D2);
                color: #000000;
                font-size: 11px;
                font-weight: 800;
                border: 1px solid #333333;
                border-radius: 3px;
                text-align: center;
            }
            QPushButton:hover {
                background: #FFFFFF;
            }
            QPushButton:pressed {
                background: #C8C8C8;
            }
        """

        self.btn_write_report = QPushButton("Write\nReport")
        self.btn_write_report.setFixedSize(62, 50)
        self.btn_write_report.setStyleSheet(sub_btn_style)
        self.btn_write_report.setCursor(Qt.PointingHandCursor)
        self.btn_write_report.clicked.connect(self._toggle_live_reporting)
        nav_lay.addWidget(self.btn_write_report)

        self.btn_archive = QPushButton("Patients\nArchive")
        self.btn_archive.setFixedSize(68, 50)
        self.btn_archive.setStyleSheet(sub_btn_style)
        self.btn_archive.setCursor(Qt.PointingHandCursor)
        self.btn_archive.clicked.connect(self._open_archive)
        nav_lay.addWidget(self.btn_archive)

        self.btn_new_pat = QPushButton("New\nPatient")
        self.btn_new_pat.setFixedSize(62, 50)
        self.btn_new_pat.setStyleSheet(sub_btn_style)
        self.btn_new_pat.setCursor(Qt.PointingHandCursor)
        self.btn_new_pat.clicked.connect(self._open_new_patient)
        nav_lay.addWidget(self.btn_new_pat)

        top_lay.addLayout(nav_lay)

        top_lay.addStretch()

        # === Group F: Circular 3D Metallic HOME Button ===
        btn_home = HomeButton(self)
        btn_home.clicked.connect(self.close)
        top_lay.addWidget(btn_home)

        parent_layout.addWidget(top_bar)

    def _create_red_sphere_icon(self) -> QIcon:
        """Generates a 3D red sphere icon for Record button."""
        pix = QPixmap(16, 16)
        pix.fill(Qt.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.Antialiasing, True)
        grad = QRadialGradient(5, 5, 7)
        grad.setColorAt(0.0, QColor("#FF6666"))
        grad.setColorAt(0.4, QColor("#EE0000"))
        grad.setColorAt(1.0, QColor("#880000"))
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor("#550000"), 1))
        painter.drawEllipse(1, 1, 13, 13)
        painter.end()
        return QIcon(pix)

    def _build_patient_subbar(self, parent_layout: QVBoxLayout):
        subbar = QFrame()
        subbar.setFixedHeight(44)
        subbar.setStyleSheet("background: #2B2B2B; border: none; margin: 0px 2px;")
        sub_lay = QHBoxLayout(subbar)
        sub_lay.setContentsMargins(4, 2, 4, 2)
        sub_lay.setSpacing(10)

        # 1. Patient Auto ID Box (Matching large silver "9" box in screenshot)
        auto_id_val = str(self.patient_data.get("auto_id", "9"))
        if auto_id_val.startswith("0000000"):
            auto_id_val = auto_id_val.replace("0000000", "")
        self.lbl_id_badge = QLabel(auto_id_val or "9")
        self.lbl_id_badge.setFixedSize(48, 38)
        self.lbl_id_badge.setAlignment(Qt.AlignCenter)
        self.lbl_id_badge.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #D2D2D2);
            color: #000000;
            font-size: 24px;
            font-weight: 900;
            border: 1.5px solid #444444;
            border-radius: 2px;
        """)
        sub_lay.addWidget(self.lbl_id_badge)

        # 2. Patient Name Title with elegant serif font & underline
        sub_lay.addStretch(1)
        name_str = self.patient_data.get("name", "Nayem Islam")
        self.lbl_patient_title = QLabel(name_str)
        self.lbl_patient_title.setAlignment(Qt.AlignCenter)
        self.lbl_patient_title.setStyleSheet("""
            color: #FFFFFF;
            font-size: 26px;
            font-family: 'Times New Roman', 'Georgia', serif;
            font-weight: 500;
            text-decoration: underline;
        """)
        sub_lay.addWidget(self.lbl_patient_title)
        sub_lay.addStretch(1)

        # 3. Live Reporting Button
        self.btn_live_reporting = QPushButton("Live Reporting")
        self.btn_live_reporting.setFixedHeight(30)
        self.btn_live_reporting.setCursor(Qt.PointingHandCursor)
        self.btn_live_reporting.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #D2D2D2);
                color: #000000;
                font-weight: 700;
                font-size: 12px;
                border: 1px solid #444444;
                border-radius: 2px;
                padding: 3px 12px;
            }
            QPushButton:hover {
                background: #FFFFFF;
            }
        """)
        self.btn_live_reporting.clicked.connect(self._toggle_live_reporting)
        sub_lay.addWidget(self.btn_live_reporting)

        parent_layout.addWidget(subbar)

    def _build_workspace_center(self, parent_layout: QVBoxLayout):
        center_frame = QFrame()
        center_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        center_lay = QHBoxLayout(center_frame)
        center_lay.setContentsMargins(2, 0, 2, 0)
        center_lay.setSpacing(4)

        # === A. LEFT COLUMN: Captured Images Tray ===
        tray_frame = QFrame()
        tray_frame.setFixedWidth(130)
        tray_frame.setObjectName("imagesTrayFrame")
        tray_frame.setStyleSheet("""
            QFrame#imagesTrayFrame {
                background: #737984;
                border: 1px solid #404040;
            }
        """)
        tray_lay = QVBoxLayout(tray_frame)
        tray_lay.setContentsMargins(2, 2, 2, 2)
        tray_lay.setSpacing(2)

        # Tray Title Header Bar
        lbl_tray_title = QLabel("Captured Images Tray")
        lbl_tray_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lbl_tray_title.setStyleSheet("""
            background: #9AA0A6;
            color: #202124;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 4px;
            border-bottom: 1px solid #606060;
        """)
        tray_lay.addWidget(lbl_tray_title)

        # Scroll area for captured thumbnails
        self.tray_scroll = QScrollArea()
        self.tray_scroll.setWidgetResizable(True)
        self.tray_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tray_scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #C0C0C0;
                width: 14px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #808080;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 12px;
                background: #A0A0A0;
            }
        """)
        self.tray_container = QWidget()
        self.tray_layout = QVBoxLayout(self.tray_container)
        self.tray_layout.setContentsMargins(2, 2, 2, 2)
        self.tray_layout.setSpacing(6)
        self.tray_layout.setAlignment(Qt.AlignTop)
        self.tray_scroll.setWidget(self.tray_container)
        tray_lay.addWidget(self.tray_scroll, 1)

        center_lay.addWidget(tray_frame)

        # === B. CENTER COLUMN: Live Video Viewport Container ===
        vp_container = QFrame()
        vp_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        vp_lay = QVBoxLayout(vp_container)
        vp_lay.setContentsMargins(0, 0, 0, 0)
        vp_lay.setSpacing(0)

        # Viewport Header Bar (Soft baby blue with navy text)
        vp_header = QLabel('Live (Press "F11" Button for Full Screen Preview On/Off)')
        vp_header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        vp_header.setFixedHeight(22)
        vp_header.setStyleSheet("""
            background: #A6C6E2;
            color: #1A3050;
            font-size: 11px;
            font-weight: bold;
            padding-left: 8px;
            border-bottom: 1px solid #7FAAD0;
        """)
        vp_lay.addWidget(vp_header)

        # Live Viewport Widget
        self.viewport = LiveVideoViewport(self)
        self.viewport.set_patient_info(self.patient_data)
        
        self.viewport.setContextMenuPolicy(Qt.CustomContextMenu)
        self.viewport.customContextMenuRequested.connect(self._show_viewport_menu)

        vp_lay.addWidget(self.viewport, 1)

        # Authentic bottom horizontal scrollbar under video viewport
        self.video_scrollbar = QScrollBar(Qt.Horizontal)
        self.video_scrollbar.setFixedHeight(12)
        self.video_scrollbar.setStyleSheet("""
            QScrollBar:horizontal {
                background: #C0C0C0;
                height: 12px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #808080;
                min-width: 30px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 12px;
                background: #A0A0A0;
            }
        """)
        vp_lay.addWidget(self.video_scrollbar)

        center_lay.addWidget(vp_container, 1)

        # === C. RIGHT COLUMN: Live Reporting Panel ===
        # Hidden by default
        self.reporting_panel = QFrame()
        self.reporting_panel.setFixedWidth(460)
        self.reporting_panel.setVisible(False)
        self.reporting_panel.setObjectName("reportingPanel")
        self.reporting_panel.setStyleSheet("""
            QFrame#reportingPanel {
                background: #505050;
                border: 1px solid #333333;
            }
        """)
        rep_lay = QVBoxLayout(self.reporting_panel)
        rep_lay.setContentsMargins(4, 4, 4, 4)
        rep_lay.setSpacing(3)

        # Toolbar row matching Demo/Screenshot 2026-09-20 003705.png:
        tool_row = QHBoxLayout()
        tool_row.setSpacing(2)

        tb_style = """
            QToolButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #D2D2D2);
                color: #000000;
                font-weight: 900;
                border: 1px solid #555555;
                border-radius: 2px;
                width: 22px;
                height: 22px;
            }
            QToolButton:hover {
                background: #FFFFFF;
            }
            QToolButton:pressed {
                background: #A0C0E0;
            }
        """

        btn_b = QToolButton()
        btn_b.setText("B")
        btn_b.setStyleSheet(tb_style)
        btn_b.clicked.connect(lambda: self.report_editor.setFontWeight(QFont.Bold if self.report_editor.fontWeight() != QFont.Bold else QFont.Normal))
        tool_row.addWidget(btn_b)

        btn_i = QToolButton()
        btn_i.setText("I")
        btn_i.setStyleSheet(tb_style.replace("font-weight: 900;", "font-weight: 900; font-style: italic;"))
        btn_i.clicked.connect(lambda: self.report_editor.setFontItalic(not self.report_editor.fontItalic()))
        tool_row.addWidget(btn_i)

        btn_u = QToolButton()
        btn_u.setText("U")
        btn_u.setStyleSheet(tb_style.replace("font-weight: 900;", "font-weight: 900; text-decoration: underline;"))
        btn_u.clicked.connect(lambda: self.report_editor.setFontUnderline(not self.report_editor.fontUnderline()))
        tool_row.addWidget(btn_u)

        btn_bullet = QToolButton()
        btn_bullet.setText("⁝≡")
        btn_bullet.setToolTip("Bulleted List")
        btn_bullet.setStyleSheet(tb_style)
        btn_bullet.clicked.connect(self._insert_bullet_list)
        tool_row.addWidget(btn_bullet)

        btn_left = QToolButton()
        btn_left.setText("≡")
        btn_left.setToolTip("Align Left")
        btn_left.setStyleSheet(tb_style)
        btn_left.clicked.connect(lambda: self.report_editor.setAlignment(Qt.AlignLeft))
        tool_row.addWidget(btn_left)

        btn_center = QToolButton()
        btn_center.setText("≚")
        btn_center.setToolTip("Align Center")
        btn_center.setStyleSheet(tb_style)
        btn_center.clicked.connect(lambda: self.report_editor.setAlignment(Qt.AlignCenter))
        tool_row.addWidget(btn_center)

        btn_right = QToolButton()
        btn_right.setText("≣")
        btn_right.setToolTip("Align Right")
        btn_right.setStyleSheet(tb_style)
        btn_right.clicked.connect(lambda: self.report_editor.setAlignment(Qt.AlignRight))
        tool_row.addWidget(btn_right)

        self.combo_font_sz = QComboBox()
        self.combo_font_sz.addItems(["9", "10", "11", "12", "14", "16", "18"])
        self.combo_font_sz.setCurrentText("11")
        self.combo_font_sz.setFixedWidth(46)
        self.combo_font_sz.setFixedHeight(24)
        self.combo_font_sz.currentTextChanged.connect(lambda sz: self.report_editor.setFontPointSize(float(sz)))
        tool_row.addWidget(self.combo_font_sz)

        btn_show_tmpl = QPushButton("Show Templates List")
        btn_show_tmpl.setFixedHeight(24)
        btn_show_tmpl.setCursor(Qt.PointingHandCursor)
        btn_show_tmpl.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #D2D2D2);
                color: #000000;
                font-size: 11px;
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 2px;
                padding: 2px 8px;
            }
            QPushButton:hover {
                background: #FFFFFF;
            }
        """)
        btn_show_tmpl.clicked.connect(self._show_templates_popup)
        tool_row.addWidget(btn_show_tmpl)

        rep_lay.addLayout(tool_row)

        # Main Rich Text Live Report Area
        # Matches Demo/Screenshot 2026-09-20 003705.png (pure white canvas with "N/A")
        self.report_editor = QTextEdit()
        self.report_editor.setStyleSheet("""
            QTextEdit {
                background: #FFFFFF;
                color: #000000;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11pt;
                border: 1px solid #333333;
                padding: 6px;
            }
        """)
        self.report_editor.setPlainText("N/A\n")
        rep_lay.addWidget(self.report_editor, 1)

        center_lay.addWidget(self.reporting_panel)

        parent_layout.addWidget(center_frame, 1)

    def _build_bottom_adjustment_bar(self, parent_layout: QVBoxLayout):
        bot_bar = QFrame()
        bot_bar.setObjectName("botAdjustmentBar")
        bot_bar.setFixedHeight(64)
        bot_bar.setStyleSheet("""
            QFrame#botAdjustmentBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4E4E4E, stop:0.06 #323232, stop:0.5 #202020, stop:0.95 #121212, stop:1 #080808);
                border-top: 1px solid #707070;
                border-bottom: 1px solid #141414;
                border-left: 1px solid #404040;
                border-right: 1px solid #404040;
            }
        """)
        bot_lay = QHBoxLayout(bot_bar)
        bot_lay.setContentsMargins(8, 4, 8, 4)
        bot_lay.setSpacing(10)

        # 1. Port Input Selector Button (S-Video Port In as shown in screenshot)
        self.btn_port_in = QPushButton("S-Video\nPort In")
        self.btn_port_in.setFixedSize(84, 50)
        self.btn_port_in.setCursor(Qt.PointingHandCursor)
        self.btn_port_in.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #444444, stop:1 #222222);
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 800;
                border: 1.5px solid #666666;
                border-radius: 2px;
            }
            QPushButton:hover {
                background: #555555;
            }
            QPushButton:pressed {
                background: #111111;
            }
        """)
        self.btn_port_in.clicked.connect(self._toggle_port_input)
        bot_lay.addWidget(self.btn_port_in)

        bot_lay.addWidget(self._create_etched_sep())

        # 2. Video Type & Resolution Selectors
        vt_col = QVBoxLayout()
        vt_col.setSpacing(3)
        vt_col.setAlignment(Qt.AlignVCenter)
        
        # Row 1: Video Type (with all 17 standards from Demo/Screenshot 2026-09-20 003705.png)
        r1 = QHBoxLayout()
        lbl_vt = QLabel("Video Type")
        lbl_vt.setFixedWidth(70)
        lbl_vt.setStyleSheet("font-size: 11px; font-weight: bold; color: #FFFFFF;")
        self.combo_video_type = QComboBox()
        self.combo_video_type.setFixedWidth(160)
        self.combo_video_type.setFixedHeight(22)
        video_types = [
            "NTSC (M) Standard, 7.5 IRE Black",
            "NTSC (M) Standard, 0 IRE Black Jpn",
            "NTSC 433",
            "PAL (B) Standard [Default]",
            "PAL (D) Standard",
            "PAL (H) Standard",
            "PAL (I) Standard",
            "PAL (M) Standard",
            "PAL (N) Standard",
            "SECAM (B) Standard",
            "SECAM (D) Standard",
            "SECAM (G) Standard",
            "SECAM (H) Standard",
            "SECAM (K) Standard",
            "SECAM (K1) Standard",
            "SECAM (L) Standard",
            "SECAM (L1) Standard"
        ]
        self.combo_video_type.addItems(video_types)
        self.combo_video_type.setCurrentText("SECAM (B) Standard")
        r1.addWidget(lbl_vt)
        r1.addWidget(self.combo_video_type)
        vt_col.addLayout(r1)

        # Row 2: Resolution (with 1920x1080x24,15 as shown in screenshot)
        r2 = QHBoxLayout()
        lbl_res = QLabel("Resolution")
        lbl_res.setFixedWidth(70)
        lbl_res.setStyleSheet("font-size: 11px; font-weight: bold; color: #FFFFFF;")
        self.combo_res = QComboBox()
        self.combo_res.setFixedWidth(160)
        self.combo_res.setFixedHeight(22)
        self.combo_res.addItems([
            "1920x1080x24,15",
            "1280x720x30",
            "720x576x25",
            "640x480x30"
        ])
        self.combo_res.setCurrentText("1920x1080x24,15")
        r2.addWidget(lbl_res)
        r2.addWidget(self.combo_res)
        vt_col.addLayout(r2)

        bot_lay.addLayout(vt_col)

        bot_lay.addWidget(self._create_etched_sep())

        # 3. 2x2 Grid of Sliders: Brightness & Hue, Contrast & Saturation
        slider_grid = QGridLayout()
        slider_grid.setHorizontalSpacing(10)
        slider_grid.setVerticalSpacing(2)

        # Brightness
        slider_grid.addWidget(self._create_slider_label("Brightness"), 0, 0)
        self.slider_bright, self.lbl_bright_val = self._create_stepped_slider("bright")
        slider_grid.addLayout(self.slider_bright, 0, 1)

        # Hue
        slider_grid.addWidget(self._create_slider_label("Hue"), 0, 2)
        self.slider_hue, self.lbl_hue_val = self._create_stepped_slider("hue")
        slider_grid.addLayout(self.slider_hue, 0, 3)

        # Contrast
        slider_grid.addWidget(self._create_slider_label("Contrast"), 1, 0)
        self.slider_contrast, self.lbl_contrast_val = self._create_stepped_slider("contrast")
        slider_grid.addLayout(self.slider_contrast, 1, 1)

        # Saturation
        slider_grid.addWidget(self._create_slider_label("Saturation"), 1, 2)
        self.slider_sat, self.lbl_sat_val = self._create_stepped_slider("sat")
        slider_grid.addLayout(self.slider_sat, 1, 3)

        bot_lay.addLayout(slider_grid)

        bot_lay.addWidget(self._create_etched_sep())

        # 4. Reset Color Button (Silver button with Bold Navy Text)
        btn_reset_color = QPushButton("Reset Color")
        btn_reset_color.setFixedSize(86, 48)
        btn_reset_color.setCursor(Qt.PointingHandCursor)
        btn_reset_color.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #D2D2D2);
                color: #002060;
                font-weight: 800;
                font-size: 12px;
                border: 1px solid #444444;
                border-radius: 2px;
            }
            QPushButton:hover {
                background: #FFFFFF;
                color: #003399;
            }
            QPushButton:pressed {
                background: #B8D0E8;
            }
        """)
        btn_reset_color.clicked.connect(self._reset_colors)
        bot_lay.addWidget(btn_reset_color)

        parent_layout.addWidget(bot_bar)

    def _create_slider_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #FFFFFF;")
        lbl.setFixedWidth(64)
        return lbl

    def _create_stepped_slider(self, key: str):
        layout = QHBoxLayout()
        layout.setSpacing(2)

        btn_dec = QToolButton()
        btn_dec.setText("<")
        btn_dec.setFixedSize(16, 20)
        btn_dec.setStyleSheet("""
            QToolButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #D0D0D0);
                color: #000000;
                font-weight: bold;
                font-size: 10px;
                border: 1px solid #444444;
                border-radius: 1px;
            }
            QToolButton:hover {
                background: #FFFFFF;
            }
        """)

        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(50)
        slider.setFixedWidth(96)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 12px;
                background: #FFFFFF;
                border: 1px solid #555555;
            }
            QSlider::sub-page:horizontal {
                background: #FFFFFF;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #DCDCDC, stop:1 #A0A0A0);
                border: 1px solid #404040;
                width: 14px;
                margin-top: -1px;
                margin-bottom: -1px;
            }
        """)

        btn_inc = QToolButton()
        btn_inc.setText(">")
        btn_inc.setFixedSize(16, 20)
        btn_inc.setStyleSheet(btn_dec.styleSheet())

        val_box = QLabel("50")
        val_box.setFixedSize(30, 20)
        val_box.setAlignment(Qt.AlignCenter)
        val_box.setStyleSheet("background: #111111; color: #FFFFFF; font-size: 11px; font-weight: bold; border: 1px solid #555555;")

        btn_dec.clicked.connect(lambda: slider.setValue(max(0, slider.value() - 2)))
        btn_inc.clicked.connect(lambda: slider.setValue(min(100, slider.value() + 2)))

        def on_change(v):
            val_box.setText(str(v))
            self._sync_adjustments()

        slider.valueChanged.connect(on_change)
        setattr(self, f"_slider_widget_{key}", slider)

        layout.addWidget(btn_dec)
        layout.addWidget(slider)
        layout.addWidget(btn_inc)
        layout.addWidget(val_box)
        return layout, val_box

    def _create_etched_sep(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("""
            border-left: 1px solid #141414;
            border-right: 1px solid #5A5A5A;
            max-width: 2px;
            margin-top: 4px;
            margin-bottom: 4px;
        """)
        return sep

    def _show_viewport_menu(self, pos):
        menu = QMenu(self)
        action_fs = menu.addAction("Toggle Full Screen Preview (F11)")
        action_fs.triggered.connect(self._toggle_fullscreen)
        menu.exec(self.viewport.mapToGlobal(pos))

    # =========================================================================
    # ACTIONS & WORKFLOW LOGIC
    # =========================================================================

    def _sync_adjustments(self):
        b = getattr(self, "_slider_widget_bright").value()
        c = getattr(self, "_slider_widget_contrast").value()
        h = getattr(self, "_slider_widget_hue").value()
        s = getattr(self, "_slider_widget_sat").value()
        self.viewport.set_adjustments(b, c, h, s)

    def _sync_filters(self):
        self.viewport.set_filters(
            vessel_plus=self.btn_vessel.isChecked(),
            vision_x=self.btn_vision.isChecked(),
            crop=self.chk_crop.isChecked(),
            invert_gray=self.chk_invert.isChecked()
        )

    def _toggle_vessel_plus(self):
        if self.sender() != self.btn_vessel:
            self.btn_vessel.setChecked(not self.btn_vessel.isChecked())
        self._sync_filters()

    def _toggle_vision_x(self):
        if self.sender() != self.btn_vision:
            self.btn_vision.setChecked(not self.btn_vision.isChecked())
        self._sync_filters()

    def _reset_colors(self):
        getattr(self, "_slider_widget_bright").setValue(50)
        getattr(self, "_slider_widget_contrast").setValue(50)
        getattr(self, "_slider_widget_hue").setValue(50)
        getattr(self, "_slider_widget_sat").setValue(50)
        self.viewport.set_adjustments(50, 50, 50, 50)

    def _toggle_port_input(self):
        cur = self.btn_port_in.text()
        if "S-Video" in cur:
            self.btn_port_in.setText("Composite\nPort In")
        elif "Composite" in cur:
            self.btn_port_in.setText("HDMI\nPort In")
        else:
            self.btn_port_in.setText("S-Video\nPort In")

    def _toggle_live_reporting(self):
        is_visible = self.reporting_panel.isVisible()
        self.reporting_panel.setVisible(not is_visible)

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            if hasattr(self, '_normal_geometry') and self._normal_geometry:
                self.setGeometry(self._normal_geometry)
            else:
                screen = QApplication.primaryScreen()
                if screen:
                    avail = screen.availableGeometry()
                    w = min(1366, int(avail.width() * 0.92))
                    h = min(768, int(avail.height() * 0.92))
                    x = avail.x() + (avail.width() - w) // 2
                    y = avail.y() + (avail.height() - h) // 2
                    self.setGeometry(x, y, w, h)
            if hasattr(self, 'btn_win_max'):
                self.btn_win_max.setText("🗖")
                self.btn_win_max.setToolTip("Full Screen")
        else:
            self._normal_geometry = self.geometry()
            screen = self.screen() or QApplication.primaryScreen()
            avail = screen.availableGeometry() if screen else None
            if avail:
                self.setGeometry(avail)
            self.showMaximized()
            if hasattr(self, 'btn_win_max'):
                self.btn_win_max.setText("🗗")
                self.btn_win_max.setToolTip("Restore Down")

    def _toggle_auto_capture(self, checked: bool):
        if checked:
            self._auto_capture_timer.start(5000)
        else:
            self._auto_capture_timer.stop()

    def _handle_auto_capture(self):
        if self.chk_auto_capture.isChecked():
            self._handle_capture_image()

    def _toggle_recording(self):
        if not self.viewport._is_recording:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            auto_id = str(self.patient_data.get("auto_id", "9"))
            rec_path = os.path.join(self._captures_dir, f"video_{auto_id}_{timestamp}.avi")
            self.viewport.start_recording(rec_path)
            self.btn_rec_vid.setText("⏹ Stop Rec")
            self.btn_rec_vid.setStyleSheet("""
                QPushButton {
                    background: #DC2626;
                    color: #FFFFFF;
                    font-size: 11px;
                    font-weight: 800;
                    border: 1px solid #7F1D1D;
                    border-radius: 3px;
                }
            """)
        else:
            saved_path = self.viewport.stop_recording()
            self.btn_rec_vid.setText(" Record Video")
            self.btn_rec_vid.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #D2D2D2);
                    color: #CC0000;
                    font-size: 11px;
                    font-weight: 800;
                    border: 1px solid #333333;
                    border-radius: 3px;
                }
            """)
            if saved_path:
                norm_path = os.path.normpath(saved_path)
                try:
                    if os.path.exists(norm_path):
                        subprocess.Popen(f'explorer /select,"{norm_path}"')
                    else:
                        folder = os.path.dirname(norm_path)
                        if os.path.exists(folder):
                            subprocess.Popen(f'explorer "{folder}"')
                except Exception:
                    try:
                        folder = os.path.dirname(norm_path)
                        os.startfile(folder)
                    except Exception:
                        pass

    def _handle_open_video(self):
        if not self.viewport._cap_thread.isRunning():
            self.viewport._cap_thread.start()
        self.btn_open_vid.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #D0F0D0, stop:1 #A0E0A0);
                color: #006000;
                font-size: 11px;
                font-weight: 800;
                border: 1px solid #008000;
                border-radius: 3px;
            }
        """)
        self.btn_close_vid.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #D2D2D2);
                color: #000000;
                font-size: 11px;
                font-weight: 800;
                border: 1px solid #333333;
                border-radius: 3px;
            }
        """)

    def _handle_close_video(self):
        self.viewport.stop_camera()
        self.btn_open_vid.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #D2D2D2);
                color: #008000;
                font-size: 11px;
                font-weight: 800;
                border: 1px solid #333333;
                border-radius: 3px;
            }
        """)
        self.btn_close_vid.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F0F0F0, stop:1 #D8D8D8);
                color: #8C8C8C;
                font-size: 11px;
                font-weight: 700;
                border: 1px solid #444444;
                border-radius: 3px;
            }
        """)

    def _handle_capture_image(self):
        """Captures frame from live viewport, saves to disk and database, and displays in tray."""
        frame_img = self.viewport.grab_current_frame()
        self.viewport.trigger_capture_flash()

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        auto_id = str(self.patient_data.get("auto_id", "9"))
        filename = f"capture_{auto_id}_{timestamp}.png"
        filepath = os.path.join(self._captures_dir, filename)

        frame_img.save(filepath, "PNG")

        frame_idx = len(self.captured_images) + 1
        db_id = self.db.save_study_image(
            patient_auto_id=auto_id,
            file_path=filepath,
            frame_number=frame_idx,
            caption=f"Frame {frame_idx} • {self.patient_data.get('proc', 'Endoscopy')}"
        )

        record = {
            "id": db_id,
            "path": filepath,
            "image": frame_img,
            "frame": frame_idx
        }
        self.captured_images.append(record)
        self._add_thumbnail_to_tray(record, highlight=True)

    def _clear_tray(self):
        """Clears all thumbnail cards from the tray."""
        self.captured_images.clear()
        self._selected_card_widget = None
        while self.tray_layout.count():
            item = self.tray_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _load_patient_thumbnails(self):
        """Loads captured study images for the active patient from the database and disk."""
        self._clear_tray()
        auto_id = str(self.patient_data.get("auto_id", "9"))
        saved_imgs = self.db.get_study_images(auto_id)
        
        for item in saved_imgs:
            fp = item.get("file_path", "")
            if fp and os.path.exists(fp):
                # Never load dummy/preview/reference images into the tray
                fn = os.path.basename(fp).lower()
                caption = str(item.get("caption", "")).lower()
                norm_fp = fp.replace("\\", "/").lower()
                if "preview_" in fn or "ref_tray_frame" in fn or "standard reference view" in caption or "trial edition" in caption:
                    continue
                if "assets/" in norm_fp or "assets\\" in fp.lower():
                    continue

                img = QImage(fp)
                if not img.isNull():
                    record = {
                        "id": item.get("id"),
                        "path": fp,
                        "image": img,
                        "frame": item.get("frame_number", len(self.captured_images) + 1)
                    }
                    self.captured_images.append(record)
                    self._add_thumbnail_to_tray(record, highlight=(len(self.captured_images) == len(saved_imgs)))

    def _add_thumbnail_to_tray(self, record: dict, highlight: bool = False):
        card = QFrame()
        card.setFixedSize(118, 84)
        card.setCursor(Qt.PointingHandCursor)

        border_css = "border: 3px solid #00C800;" if highlight else "border: 2px solid #111111;"
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #000000;
                {border_css}
            }}
        """)

        clay = QVBoxLayout(card)
        clay.setContentsMargins(0, 0, 0, 0)
        clay.setSpacing(0)

        img_lbl = QLabel(card)
        img_lbl.setAlignment(Qt.AlignCenter)
        pix = QPixmap.fromImage(record["image"]).scaled(112, 78, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        img_lbl.setPixmap(pix)
        clay.addWidget(img_lbl)

        # Image Remove Icon Button at Top-Right
        btn_remove = QPushButton("✕", card)
        btn_remove.setObjectName("thumbDeleteBtn")
        btn_remove.setToolTip(f"Remove Frame #{record.get('frame', '')}")
        btn_remove.setFixedSize(20, 20)
        btn_remove.move(card.width() - 24, 4)
        btn_remove.setCursor(Qt.PointingHandCursor)
        btn_remove.setStyleSheet("""
            QPushButton#thumbDeleteBtn {
                background-color: rgba(220, 38, 38, 0.85);
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.8);
                border-radius: 10px;
                font-size: 11px;
                font-weight: 900;
                padding: 0px;
                margin: 0px;
            }
            QPushButton#thumbDeleteBtn:hover {
                background-color: #EF4444;
                border: 1px solid #FFFFFF;
            }
            QPushButton#thumbDeleteBtn:pressed {
                background-color: #991B1B;
            }
        """)
        btn_remove.clicked.connect(lambda checked=False, r=record, c=card: self._handle_delete_thumbnail(r, c))

        def on_card_click(event):
            if btn_remove.geometry().contains(event.pos()):
                return
            self._on_thumbnail_clicked(record, card)

        card.mousePressEvent = on_card_click
        
        card.setContextMenuPolicy(Qt.CustomContextMenu)
        card.customContextMenuRequested.connect(lambda pos, r=record, c=card: self._show_thumbnail_menu(pos, r, c))

        self.tray_layout.addWidget(card)
        if highlight:
            self._selected_card_widget = card

        QTimer.singleShot(50, lambda: self.tray_scroll.verticalScrollBar().setValue(self.tray_scroll.verticalScrollBar().maximum()))

    def _handle_delete_thumbnail(self, record: dict, card_widget: QFrame):
        """Removes a captured frame from the tray, database, and filesystem."""
        frame_num = record.get("frame", "")
        reply = QMessageBox.question(
            self,
            "Remove Captured Image",
            f"Are you sure you want to remove Frame #{frame_num}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        # 1. Delete from database if record has an ID
        if record.get("id"):
            try:
                self.db.delete_study_image(record["id"])
            except Exception as e:
                print(f"[Warning] Failed to delete image from DB: {e}")

        # 2. Delete file from captures dir if it exists
        file_path = record.get("path")
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"[Warning] Failed to remove image file: {e}")

        # 3. Remove record from internal list
        if record in self.captured_images:
            self.captured_images.remove(record)

        # 4. Remove widget from tray UI
        if self._selected_card_widget == card_widget:
            self._selected_card_widget = None

        self.tray_layout.removeWidget(card_widget)
        card_widget.deleteLater()

    def _on_thumbnail_clicked(self, record: dict, card_widget: QFrame):
        self._select_thumbnail(record, card_widget)
        self._zoom_image(record["path"], record["frame"])

    def _select_thumbnail(self, record: dict, card_widget: Optional[QFrame] = None):
        if self._selected_card_widget and self._selected_card_widget != card_widget:
            self._selected_card_widget.setStyleSheet("QFrame { background-color: #000000; border: 2px solid #111111; }")
        if card_widget:
            card_widget.setStyleSheet("QFrame { background-color: #000000; border: 3px solid #00C800; }")
            self._selected_card_widget = card_widget

    def _show_thumbnail_menu(self, pos, record: dict, card_widget: QFrame):
        menu = QMenu(self)
        act_zoom = menu.addAction("🔍 Zoom Preview")
        act_export = menu.addAction("💾 Export Image")
        menu.addSeparator()
        act_del = menu.addAction("🗑 Delete Image")
        act_zoom.triggered.connect(lambda: self._zoom_image(record["path"], record.get("frame", 1)))
        act_export.triggered.connect(lambda: self._export_image(record["path"]))
        act_del.triggered.connect(lambda: self._handle_delete_thumbnail(record, card_widget))
        menu.exec(card_widget.mapToGlobal(pos))

    def _export_image(self, src_path: str):
        target, _ = QFileDialog.getSaveFileName(self, "Export Endoscopy Image", "Endoscopy_Capture.png", "PNG Image (*.png);;JPEG (*.jpg)")
        if target:
            try:
                import shutil
                shutil.copy2(src_path, target)
                QMessageBox.information(self, "Export Success", f"✓ Captured image exported to:\n{target}")
            except Exception as e:
                QMessageBox.warning(self, "Export Failed", str(e))

    def _zoom_image(self, file_path: str, frame_num: int):
        from app.ui.main_window import ImagePreviewModal
        dlg = ImagePreviewModal(file_path, f"Captured Frame #{frame_num} Review", self)
        dlg.exec()

    def _insert_bullet_list(self):
        cursor = self.report_editor.textCursor()
        cursor.insertList(QTextListFormat.ListDisc)

    def _show_templates_popup(self):
        procs = self.db.get_procedures()
        items = [f"{p.get('name', '')} ({p.get('code', '')})" for p in procs]
        if not items:
            items = ["UPPER GI ENDOSCOPY", "COLONOSCOPY", "ERCP / FLUOROSCOPY", "BRONCHOSCOPY"]
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Insert Report Template")
        msg.setText("Select an Endoscopy Standard Template to insert into live findings:")
        combo = QComboBox(msg)
        combo.addItems(items)
        msg.layout().addWidget(combo)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        if msg.exec() == QMessageBox.Ok:
            sel_name = combo.currentText().split(" (")[0]
            for p in procs:
                if p.get("name") == sel_name:
                    findings = p.get("default_findings", "")
                    self.report_editor.append(f"\n--- {sel_name} Standard Template ---\n{findings}\n")
                    break

    def _open_archive(self):
        from app.ui.dialogs.archive_dialog import ArchiveDialog
        dlg = ArchiveDialog(parent=self)
        dlg.showMaximized()
        dlg.exec()

    def _open_new_patient(self):
        from app.ui.dialogs.new_patient_dialog import NewPatientDialog
        dlg = NewPatientDialog(parent=self)
        dlg.showMaximized()
        if dlg.exec() == QDialog.Accepted:
            latest = self.db.get_patients(limit=1)
            if latest:
                p = latest[0]
                self.patient_data = p
                self.lbl_id_badge.setText(str(p.get("auto_id", "9")).replace("0000000", ""))
                self.lbl_patient_title.setText(p.get("name", "Nayem Islam"))
                if hasattr(self, 'lbl_title_status'):
                    pat_id = str(p.get("auto_id", "9")).replace("0000000", "")
                    self.lbl_title_status.setText(f"● LIVE  [{pat_id}] {p.get('name', 'Nayem Islam')}")
                self.viewport.set_patient_info(self.patient_data)
                self._load_patient_thumbnails()
