"""
Endocare Core Utilities - Path & Storage Virtualization
Handles seamless asset loading and persistent user data directory resolution
both in standard Python development and inside compiled PyInstaller / Inno Setup environments.
"""

import os
import sys
import shutil


def is_frozen() -> bool:
    """Check if the application is running inside a PyInstaller frozen bundle."""
    return getattr(sys, "frozen", False)


def get_base_dir() -> str:
    """
    Returns the root directory where the application code/bundle resides.
    In frozen mode: sys._MEIPASS or directory of sys.executable.
    In development mode: Project root directory (Endocare_Endoscopy).
    """
    if is_frozen():
        # PyInstaller temp unpack or dist folder
        return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.executable)))
    else:
        # Development mode: two levels up from app/core/
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


def get_asset_path(filename: str = "") -> str:
    """
    Returns the absolute path to an asset or the assets directory.
    Works reliably both in development and inside PyInstaller frozen binaries.
    """
    base = get_base_dir()
    assets_dir = os.path.join(base, "assets")
    
    # Fallback check if assets is alongside executable in onedir mode
    if not os.path.exists(assets_dir) and is_frozen():
        alt_assets = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), "assets")
        if os.path.exists(alt_assets):
            assets_dir = alt_assets

    if filename:
        return os.path.join(assets_dir, filename)
    return assets_dir


def get_data_dir() -> str:
    """
    Returns the persistent storage directory for user databases, settings, and captures.
    
    In Frozen/Installed mode:
      Uses %LOCALAPPDATA%\\Endocare (e.g. C:\\Users\\<user>\\AppData\\Local\\Endocare)
      This guarantees write permissions even when installed in C:\\Program Files\\Endocare.
      Automatically initializes the database from seed if not already present.
      
    In Development mode:
      Uses the project's local 'data' folder for seamless git development.
    """
    if is_frozen():
        local_app_data = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        data_dir = os.path.join(local_app_data, "Endocare", "data")
    else:
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))

    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_db_path() -> str:
    """
    Returns the absolute path to the SQLite database (endocare.db).
    In frozen mode, if the database doesn't exist yet in %LOCALAPPDATA%,
    it seeds it from the bundled baseline database if available.
    """
    data_dir = get_data_dir()
    target_db = os.path.join(data_dir, "endocare.db")
    
    # If database does not exist in local app data, check for seed DB bundled with app
    if is_frozen() and not os.path.exists(target_db):
        bundled_seed = os.path.join(get_base_dir(), "data", "endocare.db")
        if not os.path.exists(bundled_seed):
            bundled_seed = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), "data", "endocare.db")
            
        if os.path.exists(bundled_seed):
            try:
                shutil.copy2(bundled_seed, target_db)
            except Exception as e:
                print(f"[Endocare] Could not copy seed database: {e}")
                
    return target_db


def get_captures_dir() -> str:
    """Returns the persistent folder for endoscopic photos and procedure recordings."""
    captures_dir = os.path.join(get_data_dir(), "captures")
    os.makedirs(captures_dir, exist_ok=True)
    return captures_dir
