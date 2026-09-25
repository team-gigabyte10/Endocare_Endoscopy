# -*- mode: python ; coding: utf-8 -*-
"""
Endocare Endoscopy Management System
PyInstaller Specification for Windows Desktop Executable Distribution
"""

import sys
import os

block_cipher = None

# Paths
project_dir = os.path.abspath(SPECPATH)
assets_dir = os.path.join(project_dir, 'assets')
data_db = os.path.join(project_dir, 'data', 'endocare.db')

datas = [
    (assets_dir, 'assets'),
]

# If initial seed database exists, package it as template
if os.path.exists(data_db):
    datas.append((data_db, 'data'))

# Exclude unnecessary heavy scientific packages installed globally in Python
excludes = [
    'tensorflow',
    'tensorboard',
    'tensorboard_data_server',
    'keras',
    'torch',
    'scipy',
    'matplotlib',
    'onnxruntime',
    'fastapi',
    'uvicorn',
    'starlette',
    'websockets',
    'pytest',
    'jinja2',
    'h5py',
    'grpc',
    'absl',
    'lxml',
    'pydantic',
    'rich',
]

hiddenimports = [
    'sqlite3',
    'cv2',
    'numpy',
    'PIL',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'app.core',
    'app.core.paths',
    'app.services',
    'app.services.database',
    'app.services.device_manager',
    'app.styles',
    'app.styles.theme',
    'app.ui',
    'app.ui.main_window',
    'app.ui.workstation_window',
    'app.ui.capture_window',
    'app.ui.report_window',
    'app.ui.image_plus_window',
    'app.ui.components.header',
    'app.ui.components.dashboard_card',
    'app.ui.components.capture_card_menu',
    'app.ui.dialogs.about_dialog',
    'app.ui.dialogs.archive_dialog',
    'app.ui.dialogs.capture_card_dialog',
    'app.ui.dialogs.doctors_dialog',
    'app.ui.dialogs.new_patient_dialog',
    'app.ui.dialogs.referrers_dialog',
    'app.ui.dialogs.templates_dialog',
]

a = Analysis(
    ['main.py'],
    pathex=[project_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Endocare',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(assets_dir, 'logo.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Endocare',
)
