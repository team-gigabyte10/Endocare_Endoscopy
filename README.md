# Endocare — Endoscopy Management System

A modern, commercial-grade medical endoscopy desktop application for Windows desktop computers in hospitals, diagnostic centers, and endoscopy clinics.

Built with **Python** using **PySide6 (Qt for Python)**.

---

## 🩺 System Overview

**Endocare** is designed specifically for clinical endoscopy suites, supporting high-throughput procedure intake, Olympus / Pentax / Fujifilm video grabber integration, historical patient study archives, physician credential rosters, referring clinic communication, and standardized diagnostic report templates.

---

## 🚀 How to Run the Desktop Application

### 1. Prerequisites
- Python 3.10+ installed on Windows
- PySide6 (`pip install PySide6`)

### 2. Launching the Desktop Application
Run the following command from the project root:

```bash
python main.py
```

The application will launch immediately as a native Windows desktop GUI application with custom clinical styling, smooth animations, and high-DPI scaling.

---

## 🖥️ User Interface & Requirements Mapping

### 1. Overall UI Style
- **Color Palette**: Professional medical blue and teal palette (`#0284C7` Cyan, `#0F766E` Teal, `#0B192C` Deep Navy, `#F1F5F9` Clinical Slate, `#FFFFFF` Crisp White, `#10B981` Emerald).
- **Layout**: Desktop-first layout optimized for **1366×768** (laptop standard) and **1920×1080** (Full HD workstation).
- **Visuals**: Clean rounded cards, soft ambient drop shadows, clear typographic hierarchy, subtle borders, and medical icons.

### 2. Header
- **Left**:
  - Endocare logo & endoscopic lens pulse emblem
  - Application Name: **Endocare**
  - Subtitle: **Endoscopy Management System**
- **Right**:
  - Live system date & time clock updated in real-time via `QTimer`
  - Active practitioner badge: **Dr. Sarah Jenkins** (Senior Gastroenterologist • Suite 1) with online pulse status
  - Settings gear button
  - Window controls: **Minimize**, **Maximize / Restore**, and **Close**
  - Draggable header bar for repositioning

### 3. Dashboard Banner & Controls
- **Welcome to Endocare**
- Subtitle: **Endoscopy Management System**
- Facility Quick Stats: **18 Procedures Today**, **3 Active Suites**, **4 Capture Cards Ready**.
- **Capture Card Library Dropdown**:
  - Prominently placed with camera icon
  - Includes all 5 required actions:
    1. **Capture Card Library**
    2. **Manage Capture Cards**
    3. **Add New Capture Card**
    4. **Edit Capture Card**
    5. **Delete Capture Card**

### 4. Primary Dashboard Cards (5 Functions)
1. **New Patient**: Register a new patient and initialize the clinical endoscopy intake workflow.
2. **Patients Archive**: View and manage patient records, past endoscopy reports, biopsy results, and DICOM PACS exports.
3. **Doctors**: Manage doctors, attending endoscopists, credentials, and specialty suite permissions.
4. **Referrers**: Manage referring physicians, outpatient clinics, and electronic report dispatch channels.
5. **Template**: Manage report templates, structured diagnostic findings, and clinical classifications (Paris, Forrest, Prague, LA Grade).

---

## 📁 Project Structure

```
Endocare_Endoscopy/
├── main.py                     # Native Desktop Application Entrypoint
├── Prompt.md                   # Project Requirements & Specifications
├── README.md                   # Documentation and usage guide
├── assets/                     # Crisp SVG Medical Icons & Logos
│   ├── logo.svg                # Endocare Brand Emblem
│   ├── camera.svg              # Capture Card Library Camera Icon
│   ├── patient.svg             # New Patient Icon
│   ├── archive.svg             # Patients Archive Icon
│   ├── doctor.svg              # Doctors Icon
│   ├── referrer.svg            # Referrers Icon
│   ├── template.svg            # Report Template Icon
│   ├── settings.svg            # Settings Gear Icon
│   └── user.svg                # Clinician Profile Avatar
├── app/                        # Python PySide6 Application Source
│   ├── styles/
│   │   ├── theme.py            # Theme definitions, colors, and QSS builder
│   │   └── theme.qss           # Production Qt Style Sheet
│   └── ui/
│       ├── main_window.py      # Primary Desktop Home Page Window
│       ├── components/
│       │   ├── header.py       # Header with Live Clock & Window Controls
│       │   ├── dashboard_card.py # Reusable Clinical Dashboard Card
│       │   └── capture_card_menu.py # Capture Card Library Dropdown Menu
│       └── dialogs/
│           ├── capture_card_dialog.py # Capture Card Hardware Manager Dialog
│           ├── new_patient_dialog.py  # Patient Registration & Intake Dialog
│           ├── archive_dialog.py      # Patient Records & Search Archive Dialog
│           ├── doctors_dialog.py      # Physician & Endoscopist Roster Dialog
│           ├── referrers_dialog.py    # Referring Physicians Directory Dialog
│           └── templates_dialog.py    # Structured Report Templates Dialog
├── index.html                  # Interactive UI Mockup (Browser Reference)
├── style.css                   # UI Mockup Stylesheet
└── app.js                      # UI Mockup Interactive Logic
```
