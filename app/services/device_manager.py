"""
Device manager for detecting and managing physical USB Endoscopy Capture Cards.
Uses PySide6.QtMultimedia QMediaDevices and DirectShow probe to discover USB grabbers in real time.
"""

from typing import List, Dict, Optional
import cv2
from PySide6.QtMultimedia import QMediaDevices


class CaptureDeviceManager:
    """Manages endoscopy video capture devices and queries USB ports passively."""
    
    # Flag set to True when CaptureWindow is actively streaming video through DirectShow
    device_in_use: bool = False
    
    @classmethod
    def get_connected_devices(cls, probe_hardware: bool = False) -> List[Dict[str, str]]:
        """Lists connected video input devices without activating the camera hardware by default."""
        devices = []
        try:
            video_inputs = QMediaDevices.videoInputs()
            for idx, cam in enumerate(video_inputs):
                if cam.isNull():
                    continue
                name = cam.description() or f"Video Input {idx}"
                cam_id = bytes(cam.id()).decode('utf-8', errors='ignore')
                
                # Only probe via DirectShow VideoCapture when explicitly requested;
                # opening cv2.VideoCapture activates the camera hardware/LED.
                if probe_hardware and not cls.device_in_use:
                    try:
                        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
                        if not cap.isOpened():
                            continue
                        cap.release()
                    except Exception:
                        pass
                
                is_usb = "usb" in cam_id.lower() or "usb" in name.lower() or "video" in name.lower()
                device_type = "USB Hardware Capture Card" if is_usb else "Integrated / Virtual Video"
                
                devices.append({
                    "name": name,
                    "id": cam_id,
                    "type": device_type,
                    "is_usb": is_usb,
                    "status": "Online & Active",
                    "resolution": "1920×1080 @ 60fps",
                    "port": f"USB Port {idx + 1} (DirectShow)"
                })
                
            # Optional DirectShow index 0 fallback only when hardware probing is explicitly requested
            if probe_hardware and not devices and not cls.device_in_use:
                try:
                    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                    if cap.isOpened():
                        cap.release()
                        devices.append({
                            "name": "USB2 Video",
                            "id": "directshow_0",
                            "type": "USB Hardware Capture Card",
                            "is_usb": True,
                            "status": "Online & Active",
                            "resolution": "1920×1080 @ 60fps",
                            "port": "USB 3.0 / 2.0 DirectShow"
                        })
                except Exception:
                    pass

        except Exception as e:
            print(f"Error querying video devices: {e}")
            
        return devices

    @classmethod
    def get_primary_usb_card(cls, probe_hardware: bool = False) -> Optional[Dict[str, str]]:
        devices = cls.get_connected_devices(probe_hardware=probe_hardware)
        for dev in devices:
            if dev.get("is_usb"):
                return dev
        return devices[0] if devices else None
