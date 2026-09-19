"""
Endocare - Templates Dialog
Workstation implementation modeled faithfully after Demo/Templates.PNG.
"""

from app.ui.workstation_window import WorkstationWindow


class TemplatesDialog(WorkstationWindow):
    """Management dialog for standardized endoscopy clinical report templates."""
    def __init__(self, parent=None):
        super().__init__(initial_module="templates", parent=parent)

