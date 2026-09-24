"""
Theme definition and stylesheet generator for Endocare Endoscopy Management System.
Medical Blue / Teal Palette adhering to commercial Windows healthcare desktop aesthetics.
"""

class Colors:
    # Primary Medical Blue / Teal Palette
    PRIMARY = "#0284C7"         # Medical Cyan / Sky Blue
    PRIMARY_DARK = "#0369A1"    # Darker blue on press
    PRIMARY_LIGHT = "#E0F2FE"   # Tinted light blue
    PRIMARY_GLOW = "#38BDF8"    # Active focus ring
    
    SECONDARY = "#0F766E"       # Clinical Teal
    SECONDARY_LIGHT = "#CCFBF1" # Light Teal background
    
    # Dark Contrast & Text
    NAVY_DARK = "#0B192C"       # Deep Header / Titlebar Navy
    NAVY_SURFACE = "#1E293B"    # Slate Navy
    TEXT_MAIN = "#0F172A"       # Primary Dark Text (Slate 900)
    TEXT_MUTED = "#475569"      # Secondary Muted Text (Slate 600)
    TEXT_LIGHT = "#94A3B8"      # Light Meta Text (Slate 400)
    TEXT_WHITE = "#FFFFFF"      # High contrast white
    
    # Backgrounds & Cards
    BG_WINDOW = "#F1F5F9"       # Main Clinical Light Slate (Slate 100)
    BG_CANVAS = "#F8FAFC"       # Card background (Slate 50)
    BG_CARD = "#FFFFFF"         # Crisp White Card
    BG_CARD_HOVER = "#F0F9FF"   # Subtle light blue hover
    BORDER_LIGHT = "#CBD5E1"    # Subtle border (Slate 300)
    BORDER_CARD = "#E2E8F0"     # Card border (Slate 200)
    BORDER_HOVER = "#0284C7"    # Highlight border
    
    # Clinical Status Colors
    STATUS_ACTIVE = "#10B981"   # Emerald Green (Online / In-Use)
    STATUS_STANDBY = "#0284C7"  # Medical Blue (Ready)
    STATUS_URGENT = "#EF4444"   # Crimson Alert
    STATUS_WARNING = "#F59E0B"  # Amber in progress
    STATUS_SCHEDULED = "#6366F1"# Indigo scheduled


def get_stylesheet() -> str:
    """Returns the full QSS stylesheet for the application."""
    return f"""
    /* Global Base */
    QMainWindow, QWidget#centralWidget {{
        background-color: {Colors.BG_WINDOW};
        font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
        color: {Colors.TEXT_MAIN};
    }}
    
    /* Header Bar */
    QFrame#headerBar {{
        background-color: {Colors.NAVY_DARK};
        border-bottom: 2px solid #0369A1;
        min-height: 64px;
        max-height: 64px;
    }}
    
    QLabel#appTitle {{
        color: #FFFFFF;
        font-size: 20px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }}
    
    QLabel#appSubtitle {{
        color: #7DD3FC;
        font-size: 11px;
        font-weight: 500;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }}
    
    QLabel#headerClock {{
        color: #E2E8F0;
        font-size: 12px;
        font-weight: 500;
        background-color: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 6px;
        padding: 5px 12px;
    }}
    
    QFrame#userBadge {{
        background-color: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 6px;
        padding: 3px 10px;
    }}
    
    QLabel#userName {{
        color: #FFFFFF;
        font-size: 12px;
        font-weight: 600;
    }}
    
    QLabel#userRole {{
        color: #93C5FD;
        font-size: 10px;
    }}
    
    /* Header Action & Window Controls */
    QToolButton#headerButton {{
        background-color: transparent;
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 6px;
        padding: 5px;
        color: #E2E8F0;
    }}
    
    QToolButton#headerButton:hover {{
        background-color: rgba(255, 255, 255, 0.18);
        border-color: rgba(255, 255, 255, 0.35);
    }}
    
    QToolButton#winCloseBtn {{
        background-color: transparent;
        border: none;
        border-radius: 4px;
        padding: 6px 12px;
        color: #CBD5E1;
        font-size: 13px;
        font-weight: bold;
    }}
    
    QToolButton#winCloseBtn:hover {{
        background-color: #DC2626;
        color: #FFFFFF;
    }}
    
    QToolButton#winControlBtn {{
        background-color: transparent;
        border: none;
        border-radius: 4px;
        padding: 6px 10px;
        color: #CBD5E1;
        font-size: 12px;
    }}
    
    QToolButton#winControlBtn:hover {{
        background-color: rgba(255, 255, 255, 0.12);
        color: #FFFFFF;
    }}
    
    /* Welcome Banner */
    QFrame#welcomeBanner {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFFFFF, stop:1 #F0F9FF);
        border: 1px solid {Colors.BORDER_CARD};
        border-radius: 12px;
        padding: 18px 24px;
    }}
    
    QLabel#welcomeTitle {{
        font-size: 26px;
        font-weight: 700;
        color: {Colors.TEXT_MAIN};
        margin-bottom: 2px;
    }}
    
    QLabel#welcomeSubtitle {{
        font-size: 14px;
        font-weight: 400;
        color: {Colors.TEXT_MUTED};
    }}
    
    /* Facility Quick Stat Badges */
    QFrame#statBadge {{
        background-color: #FFFFFF;
        border: 1px solid {Colors.BORDER_CARD};
        border-radius: 8px;
        padding: 6px 14px;
    }}
    
    QLabel#statVal {{
        font-size: 16px;
        font-weight: 700;
        color: {Colors.PRIMARY_DARK};
    }}
    
    QLabel#statLbl {{
        font-size: 10px;
        font-weight: 600;
        color: {Colors.TEXT_MUTED};
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* Capture Card Library Dropdown Button */
    QPushButton#captureCardDropdownBtn {{
        background-color: #FFFFFF;
        color: {Colors.NAVY_DARK};
        font-size: 13px;
        font-weight: 600;
        border: 1.5px solid #0284C7;
        border-radius: 8px;
        padding: 8px 18px;
        text-align: left;
    }}
    
    QPushButton#captureCardDropdownBtn:hover {{
        background-color: #F0F9FF;
        border-color: #0369A1;
    }}
    
    QPushButton#captureCardDropdownBtn:pressed {{
        background-color: #E0F2FE;
    }}
    
    /* Dropdown Menus */
    QMenu {{
        background-color: #FFFFFF;
        border: 1px solid {Colors.BORDER_LIGHT};
        border-radius: 8px;
        padding: 6px;
        font-size: 13px;
    }}
    
    QMenu::item {{
        padding: 8px 24px 8px 12px;
        border-radius: 5px;
        color: {Colors.TEXT_MAIN};
        font-weight: 500;
    }}
    
    QMenu::item:selected {{
        background-color: #F0F9FF;
        color: {Colors.PRIMARY_DARK};
    }}
    
    QMenu::separator {{
        height: 1px;
        background: {Colors.BORDER_CARD};
        margin: 4px 6px;
    }}
    
    /* Dashboard Cards */
    QFrame#dashboardCard {{
        background-color: #FFFFFF;
        border: 1.5px solid {Colors.BORDER_CARD};
        border-radius: 12px;
        padding: 20px;
    }}
    
    QFrame#dashboardCard:hover {{
        background-color: #F8FAFC;
        border-color: {Colors.PRIMARY};
    }}
    
    QLabel#cardTitle {{
        font-size: 18px;
        font-weight: 700;
        color: {Colors.TEXT_MAIN};
    }}
    
    QLabel#cardSubtitle {{
        font-size: 13px;
        color: {Colors.TEXT_MUTED};
        font-weight: 400;
    }}
    
    QFrame#cardIconContainer {{
        background-color: #E0F2FE;
        border-radius: 12px;
        min-width: 52px;
        max-width: 52px;
        min-height: 52px;
        max-height: 52px;
    }}
    
    /* Common Buttons */
    QPushButton.primaryButton {{
        background-color: {Colors.PRIMARY};
        color: #FFFFFF;
        font-size: 13px;
        font-weight: 600;
        border-radius: 8px;
        padding: 9px 20px;
        border: none;
    }}
    
    QPushButton.primaryButton:hover {{
        background-color: {Colors.PRIMARY_DARK};
    }}
    
    QPushButton.secondaryButton {{
        background-color: #FFFFFF;
        color: {Colors.TEXT_MAIN};
        font-size: 13px;
        font-weight: 600;
        border: 1px solid {Colors.BORDER_LIGHT};
        border-radius: 8px;
        padding: 8px 18px;
    }}
    
    QPushButton.secondaryButton:hover {{
        background-color: #F1F5F9;
        border-color: {Colors.BORDER_HOVER};
    }}
    
    /* Form Inputs */
    QLineEdit, QComboBox, QSpinBox, QDateEdit {{
        background-color: #FFFFFF;
        border: 1.5px solid {Colors.BORDER_LIGHT};
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        color: {Colors.TEXT_MAIN};
    }}
    
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus {{
        border-color: {Colors.PRIMARY};
        background-color: #FAFCFE;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: #FFFFFF;
        color: {Colors.TEXT_MAIN};
        border: 1.5px solid {Colors.PRIMARY};
        border-radius: 6px;
        selection-background-color: {Colors.PRIMARY};
        selection-color: #FFFFFF;
        outline: none;
        padding: 4px;
    }}
    
    QComboBox QAbstractItemView::item {{
        min-height: 26px;
        padding: 4px 10px;
        color: {Colors.TEXT_MAIN};
        background-color: #FFFFFF;
        border-radius: 4px;
    }}
    
    QComboBox QAbstractItemView::item:hover {{
        background-color: {Colors.PRIMARY_LIGHT};
        color: {Colors.PRIMARY};
    }}
    
    QComboBox QAbstractItemView::item:selected {{
        background-color: {Colors.PRIMARY};
        color: #FFFFFF;
    }}
    
    /* Tables */
    QTableWidget {{
        background-color: #FFFFFF;
        border: 1px solid {Colors.BORDER_CARD};
        border-radius: 8px;
        gridline-color: #F1F5F9;
        font-size: 13px;
    }}
    
    QHeaderView::section {{
        background-color: #F8FAFC;
        color: {Colors.TEXT_MUTED};
        font-weight: 600;
        font-size: 12px;
        border: none;
        border-bottom: 1px solid {Colors.BORDER_LIGHT};
        padding: 8px;
    }}
    
    /* Dialog Windows */
    QDialog {{
        background-color: {Colors.BG_WINDOW};
    }}
    
    /* Status Footer Bar */
    QFrame#statusBar {{
        background-color: #FFFFFF;
        border-top: 1px solid {Colors.BORDER_CARD};
        min-height: 32px;
        max-height: 32px;
        padding: 0 16px;
    }}
    
    QLabel#statusText {{
        color: {Colors.TEXT_MUTED};
        font-size: 11px;
    }}
    
    /* ==========================================================================
       MODERN MEDICAL LAUNCHER WINDOW STYLES
       ========================================================================== */
       
    QFrame#launcherCentralContainer {{
        background: qradialgradient(cx:0.5, cy:0.4, radius:0.85, fx:0.5, fy:0.35, 
            stop:0 #0E2E42, stop:0.35 #091F2D, stop:0.75 #05141E, stop:1 #02090F);
        border: 2px solid #0284C7;
        border-radius: 14px;
    }}
    
    /* Corner Pill Buttons */
    QPushButton#aboutCornerBtn {{
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.55, fx:0.5, fy:0.5, stop:0 #0F2D4A, stop:1 #061828);
        color: #38BDF8;
        border: 2px solid #0284C7;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 1.5px;
        padding: 0px;
    }}
    
    QPushButton#aboutCornerBtn:hover {{
        background: #0284C7;
        color: #FFFFFF;
        border-color: #7DD3FC;
    }}
    
    QPushButton#aboutCornerBtn:pressed {{
        background: #0369A1;
    }}
    
    QPushButton#exitCornerBtn {{
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.55, fx:0.5, fy:0.5, stop:0 #500E0E, stop:1 #220505);
        color: #F87171;
        border: 2px solid #DC2626;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 1.5px;
        padding: 0px;
    }}
    
    QPushButton#exitCornerBtn:hover {{
        background: #DC2626;
        color: #FFFFFF;
        border-color: #FCA5A5;
    }}
    
    QPushButton#exitCornerBtn:pressed {{
        background: #991B1B;
    }}
    
    /* Top Header Text Elements */
    QLabel#heroAppSubtitle {{
        color: #94A3B8;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
    }}
    
    QLabel#heroAppTitle {{
        color: #FFFFFF;
        font-size: 56px;
        font-weight: 900;
        letter-spacing: 10px;
    }}
    
    QLabel#heroVerTag {{
        color: #38BDF8;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 1px;
    }}
    
    QLabel#devCreditText {{
        color: #64748B;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }}
    
    QLabel#trialBadge,
    QLabel#editionBadge {{
        color: #10B981;
        background-color: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 6px;
        padding: 3px 12px;
        font-size: 12px;
        font-weight: 700;
        font-style: italic;
        letter-spacing: 0.6px;
    }}
    
    /* Medical Viewport Panels */
    QFrame.viewportFrame {{
        background-color: #030712;
        border: 1.5px solid #1E293B;
        border-radius: 8px;
    }}
    
    QFrame.viewportFrame:hover {{
        border: 1.5px solid #0284C7;
    }}
    
    QLabel.modalityBadge {{
        background-color: rgba(15, 23, 42, 0.85);
        color: #38BDF8;
        font-size: 9px;
        font-weight: 700;
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 4px;
        padding: 2px 5px;
    }}
    
    /* Capture Card Selector */
    QLabel#captureCardLabel {{
        color: #E2E8F0;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }}
    
    QComboBox#captureCardCombo {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1E293B, stop:1 #0F172A);
        color: #F8FAFC;
        border: 1.5px solid #0284C7;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 12px;
        font-weight: 600;
        min-height: 24px;
    }}
    
    QComboBox#captureCardCombo:hover {{
        border-color: #38BDF8;
        background-color: #1E293B;
    }}
    
    QComboBox#captureCardCombo::drop-down {{
        border: none;
        width: 24px;
    }}
    
    QComboBox#captureCardCombo QAbstractItemView {{
        background-color: #0F172A;
        color: #F8FAFC;
        border: 1px solid #0284C7;
        selection-background-color: #0284C7;
        selection-color: #FFFFFF;
        padding: 4px;
    }}
    
    /* Clinical Action Buttons */
    QPushButton.clinicalActionBtn {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #F1F5F9);
        color: #0F172A;
        border: 1.5px solid #94A3B8;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.3px;
        padding: 10px 14px;
        text-align: center;
    }}
    
    QPushButton.clinicalActionBtn:hover {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0284C7, stop:1 #0369A1);
        color: #FFFFFF;
        border-color: #38BDF8;
    }}
    
    QPushButton.clinicalActionBtn:pressed {{
        background: #0284C7;
        color: #FFFFFF;
    }}
    
    /* Templates Full-Width Button */
    QPushButton.clinicalActionWideBtn {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #F1F5F9);
        color: #0F172A;
        border: 1.5px solid #94A3B8;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.5px;
        padding: 9px 14px;
        text-align: center;
    }}
    
    QPushButton.clinicalActionWideBtn:hover {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0F766E, stop:1 #0D9488);
        color: #FFFFFF;
        border-color: #2DD4BF;
    }}
    
    QPushButton.clinicalActionWideBtn:pressed {{
        background: #0F766E;
        color: #FFFFFF;
    }}
    
    /* ==========================================================================
       DOCTORS WORKSTATION & UNIFIED WORKSTATION STYLES
       ========================================================================== */
    
    QFrame#workstationRoot, QFrame#doctorsWorkstationRoot, QFrame#newPatientWorkstationRoot {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #070E16, stop:0.5 #0B1622, stop:1 #050A10);
    }}
    
    QFrame#newPatientCard {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0E2436, stop:0.4 #091A28, stop:1 #05101A);
        border: 2px solid #0284C7;
        border-radius: 12px;
    }}
    
    /* Card Header Buttons */
    QPushButton#cardCloseBtn {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #DC2626, stop:1 #991B1B);
        color: #FFFFFF;
        border: 1px solid #F87171;
        border-radius: 5px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1px;
        padding: 5px 14px;
    }}
    QPushButton#cardCloseBtn:hover {{
        background: #EF4444;
        border-color: #FCA5A5;
    }}
    
    QPushButton#cardAddBtn {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #10B981, stop:1 #047857);
        color: #FFFFFF;
        border: 1px solid #34D399;
        border-radius: 5px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1px;
        padding: 5px 16px;
    }}
    QPushButton#cardAddBtn:hover {{
        background: #059669;
        border-color: #6EE7B7;
    }}
    
    QLabel#cardTitle {{
        color: #F8FAFC;
        font-size: 20px;
        font-weight: 800;
        letter-spacing: 1px;
    }}
    
    /* Form Inputs */
    QLabel.formFieldLabel {{
        color: #E2E8F0;
        font-size: 13px;
        font-weight: 700;
    }}
    
    QLineEdit.formInput, QDateEdit.formInput {{
        background-color: #1E293B;
        color: #F8FAFC;
        border: 1.5px solid #334155;
        border-radius: 5px;
        padding: 6px 10px;
        font-size: 13px;
        font-weight: 600;
    }}
    QLineEdit.formInput:focus, QDateEdit.formInput:focus {{
        border-color: #38BDF8;
        background-color: #1E2E42;
    }}
    
    QComboBox.formCombo {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1E293B, stop:1 #0F172A);
        color: #F8FAFC;
        border: 1.5px solid #334155;
        border-radius: 5px;
        padding: 5px 10px;
        font-size: 13px;
        font-weight: 600;
    }}
    QComboBox.formCombo:focus {{
        border-color: #38BDF8;
    }}
    QComboBox.formCombo QAbstractItemView {{
        background-color: #0F172A;
        color: #F8FAFC;
        border: 1px solid #0284C7;
        selection-background-color: #0284C7;
        selection-color: #FFFFFF;
        padding: 4px;
    }}
    
    QRadioButton.formRadio {{
        color: #E2E8F0;
        font-size: 13px;
        font-weight: 600;
        spacing: 6px;
    }}
    QRadioButton.formRadio::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 8px;
        border: 1.5px solid #64748B;
        background: #1E293B;
    }}
    QRadioButton.formRadio::indicator:checked {{
        border-color: #38BDF8;
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.45, fx:0.5, fy:0.5, stop:0 #38BDF8, stop:0.6 #0284C7, stop:1 #1E293B);
    }}
    
    /* Quick Action Buttons on Form */
    QToolButton#quickClearBtn {{
        background-color: #7F1D1D;
        color: #FCA5A5;
        border: 1px solid #DC2626;
        border-radius: 4px;
        font-weight: 900;
        font-size: 12px;
        padding: 4px 8px;
    }}
    QToolButton#quickClearBtn:hover {{
        background-color: #DC2626;
        color: #FFFFFF;
    }}
    
    QToolButton#quickAddBtn {{
        background-color: #03446A;
        color: #38BDF8;
        border: 1px solid #0284C7;
        border-radius: 4px;
        font-weight: 900;
        font-size: 13px;
        padding: 4px 8px;
    }}
    QToolButton#quickAddBtn:hover {{
        background-color: #0284C7;
        color: #FFFFFF;
    }}
    
    /* Persistent Right Sidebar */
    QFrame#workspaceSidebar {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0C1724, stop:0.5 #08111A, stop:1 #040A10);
        border-left: 2px solid #1E293B;
    }}
    
    QPushButton.sideNavBtn {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #F1F5F9);
        color: #0F172A;
        border: 1.5px solid #94A3B8;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.3px;
        padding: 10px 12px;
        text-align: center;
    }}
    QPushButton.sideNavBtn:hover {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0284C7, stop:1 #0369A1);
        color: #FFFFFF;
        border-color: #38BDF8;
    }}
    
    QPushButton.sideNavActiveBtn {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0284C7, stop:1 #0369A1);
        color: #FFFFFF;
        border: 2px solid #38BDF8;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 0.4px;
        padding: 10px 12px;
        text-align: center;
    }}
    
    QPushButton.sideActionBtn {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1E293B, stop:1 #0F172A);
        color: #E2E8F0;
        border: 1px solid #334155;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
        padding: 8px 12px;
    }}
    QPushButton.sideActionBtn:hover {{
        background: #334155;
        color: #FFFFFF;
        border-color: #64748B;
    }}
    
    QCheckBox.sideCheckBox {{
        color: #CBD5E1;
        font-size: 12px;
        font-weight: 600;
        spacing: 8px;
    }}
    QCheckBox.sideCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 3px;
        border: 1.5px solid #64748B;
        background: #1E293B;
    }}
    QCheckBox.sideCheckBox::indicator:checked {{
        background-color: #0284C7;
        border-color: #38BDF8;
    }}
    
    QPushButton#sideHomeBtn {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #10B981, stop:1 #047857);
        color: #FFFFFF;
        border: 1.5px solid #34D399;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 1px;
        padding: 9px 16px;
    }}
    QPushButton#sideHomeBtn:hover {{
        background: #059669;
        border-color: #6EE7B7;
    }}
    
    QPushButton#sideExitBtn {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #DC2626, stop:1 #991B1B);
        color: #FFFFFF;
        border: 1.5px solid #F87171;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 1px;
        padding: 9px 16px;
    }}
    QPushButton#sideExitBtn:hover {{
        background: #EF4444;
        border-color: #FCA5A5;
    }}
    
    /* ==========================================================================
       PATIENTS ARCHIVE WORKSTATION STYLES (MATCHING Demo/Patientarchive.PNG)
       ========================================================================== */
       
    QFrame#archiveWorkstationRoot {{
        background: #374151;
    }}
    
    QFrame#archiveWorkstationCard {{
        background: #2D3748;
        border: 1.5px solid #4B5563;
        border-radius: 8px;
    }}
    
    /* Top Jade/Teal Banner Header */
    QFrame#archiveHeaderBar {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3D7363, stop:0.5 #2D584C, stop:1 #1F3D35);
        border: 1px solid #1B4036;
        border-radius: 4px;
        padding: 4px 8px;
    }}
    
    QLabel#archiveHeaderTitle {{
        color: #D1E7DD;
        font-size: 22px;
        font-weight: 900;
        letter-spacing: 1px;
    }}
    
    QLabel#archiveCounterBadge {{
        color: #FFFFFF;
        font-size: 12px;
        font-weight: 700;
        background: transparent;
        border: none;
        padding: 2px 6px;
    }}
    
    /* Upper Archive Table (9 Columns: Black Header, White/Silver Canvas) */
    QTableWidget#archiveTable {{
        background-color: #ECEEF1;
        border: 1.5px solid #94A3B8;
        border-radius: 4px;
        gridline-color: #CBD5E1;
        color: #0F172A;
        font-size: 12px;
        selection-background-color: #000000;
        selection-color: #FFFFFF;
    }}
    
    QTableWidget#archiveTable::item {{
        padding: 4px 6px;
        border-bottom: 1px solid #E2E8F0;
        color: #0F172A;
    }}
    
    QTableWidget#archiveTable::item:selected {{
        background-color: #000000;
        color: #FFFFFF;
        font-weight: 700;
    }}
    
    QHeaderView::section#archiveTableHeader {{
        background-color: #000000;
        color: #FFFFFF;
        font-weight: 800;
        font-size: 12px;
        padding: 5px 6px;
        border: 1px solid #334155;
    }}
    
    /* Green-Bordered Details & Search Sub-Cards */
    QFrame#selectedPatientDetailsBox, QFrame#search12Box {{
        background-color: #E5E7EB;
        border: 2px solid #22C55E;
        border-radius: 6px;
        padding: 6px 10px;
    }}
    
    QLabel.archiveFieldLabel {{
        color: #111827;
        font-size: 11px;
        font-weight: 700;
    }}
    
    QLineEdit.archiveInput, QPlainTextEdit.archiveInput, QComboBox.archiveCombo, QDateEdit.archiveDate {{
        background-color: #FFFFFF;
        color: #000000;
        border: 1px solid #94A3B8;
        border-radius: 3px;
        padding: 3px 6px;
        font-size: 11px;
        font-weight: 600;
    }}
    QLineEdit.archiveInput:focus, QPlainTextEdit.archiveInput:focus, QComboBox.archiveCombo:focus, QDateEdit.archiveDate:focus {{
        border-color: #0284C7;
        background-color: #FFFFFF;
    }}
    
    QComboBox.archiveCombo QAbstractItemView {{
        background-color: #FFFFFF;
        color: #000000;
        border: 1px solid #94A3B8;
        selection-background-color: #0284C7;
        selection-color: #FFFFFF;
        padding: 3px;
    }}
    
    /* Update & Delete Buttons in Address Box */
    QPushButton#btnArchiveUpdate {{
        background: #FFFFFF;
        color: #0000CD;
        border: 1px solid #94A3B8;
        border-radius: 3px;
        font-size: 12px;
        font-weight: 800;
        text-decoration: underline;
        padding: 4px 14px;
    }}
    QPushButton#btnArchiveUpdate:hover {{
        background: #EFF6FF;
        border-color: #0000CD;
    }}
    
    QPushButton#btnArchiveDelete {{
        background: #FFFFFF;
        color: #DC2626;
        border: 1px solid #94A3B8;
        border-radius: 3px;
        font-size: 12px;
        font-weight: 800;
        text-decoration: underline;
        padding: 4px 14px;
    }}
    QPushButton#btnArchiveDelete:hover {{
        background: #FEF2F2;
        border-color: #DC2626;
    }}
    
    /* Archive Right Command Buttons (New Patient, Capture, Show Report, Image Plus) */
    QPushButton.archiveSideActionBtn {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #DDE2E8);
        color: #0F172A;
        border: 1px solid #64748B;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
        padding: 5px 10px;
        min-width: 115px;
    }}
    QPushButton.archiveSideActionBtn:hover {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F1F5F9, stop:1 #CBD5E1);
        border-color: #334155;
    }}
    QPushButton.archiveSideActionBtn:pressed {{
        background: #CBD5E1;
    }}
    
    /* 12 Criteria Checkboxes & Controls */
    QCheckBox.archiveCriteriaCheck {{
        color: #0000CD;
        font-size: 11px;
        font-weight: 800;
        spacing: 5px;
    }}
    QCheckBox.archiveCriteriaCheck::indicator {{
        width: 13px;
        height: 13px;
        border-radius: 2px;
        border: 1px solid #64748B;
        background: #FFFFFF;
    }}
    QCheckBox.archiveCriteriaCheck::indicator:checked {{
        background-color: #0000CD;
        border-color: #0000CD;
    }}
    
    QRadioButton.archiveRadio {{
        color: #111827;
        font-size: 11px;
        font-weight: 600;
        spacing: 4px;
    }}
    QRadioButton.archiveRadio::indicator {{
        width: 13px;
        height: 13px;
        border-radius: 6px;
        border: 1px solid #64748B;
        background: #FFFFFF;
    }}
    QRadioButton.archiveRadio::indicator:checked {{
        border-color: #0000CD;
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.4, fx:0.5, fy:0.5, stop:0 #0000CD, stop:1 #FFFFFF);
    }}
    
    QLabel.archiveB2wnLabel {{
        color: #0000CD;
        font-weight: 800;
        font-size: 11px;
    }}
    
    QLabel#search12HeaderTitle {{
        color: #155E50;
        font-size: 13px;
        font-weight: 800;
    }}
    
    QPushButton#btnArchiveSearch {{
        background: #FFFFFF;
        color: #15803D;
        border: 2px solid #22C55E;
        border-radius: 4px;
        font-size: 13px;
        font-weight: 900;
        letter-spacing: 1px;
        padding: 3px 20px;
    }}
    QPushButton#btnArchiveSearch:hover {{
        background: #22C55E;
        color: #FFFFFF;
    }}
    
    /* ==========================================================================

       DOCTORS ARCHIVE WORKSTATION STYLES
       ========================================================================== */
       
    QFrame#doctorsWorkstationRoot {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #070E16, stop:0.5 #0B1622, stop:1 #050A10);
    }}
    
    QFrame#doctorsCard {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0E2436, stop:0.4 #091A28, stop:1 #05101A);
        border: 2px solid #0284C7;
        border-radius: 12px;
    }}
    
    /* Doctors Directory List */
    QListWidget#doctorsListWidget {{
        background-color: #0A131C;
        border: 1.5px solid #1E293B;
        border-radius: 6px;
        color: #F8FAFC;
        font-size: 13px;
        padding: 4px;
    }}
    
    QListWidget#doctorsListWidget::item {{
        padding: 8px 10px;
        border-radius: 4px;
        margin-bottom: 2px;
    }}
    
    QListWidget#doctorsListWidget::item:hover {{
        background-color: #1E293B;
        color: #38BDF8;
    }}
    
    QListWidget#doctorsListWidget::item:selected {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #0369A1);
        color: #FFFFFF;
        font-weight: 700;
        border-left: 3px solid #38BDF8;
    }}
    
    /* Doctors Action Buttons */
    QPushButton#btnDocAddNew {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #F1F5F9);
        color: #0F172A;
        border: 1.5px solid #94A3B8;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 800;
        padding: 7px 14px;
    }}
    QPushButton#btnDocAddNew:hover {{
        background: #0284C7;
        color: #FFFFFF;
        border-color: #38BDF8;
    }}
    
    QPushButton#btnDocUpdate {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #E0F2FE);
        color: #0369A1;
        border: 1.5px solid #0284C7;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 800;
        padding: 7px 14px;
    }}
    QPushButton#btnDocUpdate:hover {{
        background: #0284C7;
        color: #FFFFFF;
    }}
    
    QPushButton#btnDocEdit {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #F1F5F9);
        color: #0F172A;
        border: 1.5px solid #94A3B8;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 800;
        padding: 7px 14px;
    }}
    QPushButton#btnDocEdit:hover {{
        background: #334155;
        color: #FFFFFF;
    }}
    
    QPushButton#btnDocDelete {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #FEE2E2);
        color: #DC2626;
        border: 1.5px solid #DC2626;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 800;
        padding: 7px 14px;
    }}
    QPushButton#btnDocDelete:hover {{
        background: #DC2626;
        color: #FFFFFF;
    }}
    
    /* Navigation Arrows */
    QPushButton.docNavBtn {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1E293B, stop:1 #0F172A);
        color: #10B981;
        border: 1.5px solid #10B981;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 900;
        padding: 4px 10px;
        min-width: 32px;
    }}
    QPushButton.docNavBtn:hover {{
        background: #10B981;
        color: #FFFFFF;
    }}
    
    /* Sidebar Report Operations Box & Secondary Actions */
    QFrame#reportOpsBox {{
        background: #08121C;
        border: 1.5px solid #1E293B;
        border-radius: 8px;
        padding: 6px;
    }}
    
    QPushButton.sideActionBtn, QPushButton#btnReportAction {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1E293B, stop:1 #0F172A);
        color: #E2E8F0;
        border: 1px solid #334155;
        border-radius: 5px;
        font-size: 11px;
        font-weight: 700;
        padding: 6px 10px;
        text-align: center;
    }}
    QPushButton.sideActionBtn:hover, QPushButton#btnReportAction:hover {{
        background: #0284C7;
        color: #FFFFFF;
        border-color: #38BDF8;
    }}
    
    QCheckBox.sideCheckBox, QCheckBox#chkReportToggle {{
        color: #94A3B8;
        font-size: 11px;
        font-weight: 600;
        spacing: 6px;
        padding: 2px 4px;
    }}
    QCheckBox.sideCheckBox:checked, QCheckBox#chkReportToggle:checked {{
        color: #38BDF8;
    }}
    """
