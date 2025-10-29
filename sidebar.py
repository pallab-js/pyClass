from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, Qt, Signal


class Sidebar(QWidget):
    """The main navigation sidebar for the application."""

    # Signal that emits the name of the view to navigate to.
    navigation_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(240)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignTop)

        self.nav_buttons = {}

        # Navigation items from project plan
        nav_items = {
            "Classes": "",
            "Calendar": "",
            "Assignments": "",
            "Settings": "",
        }

        for text, icon in nav_items.items():
            button = self._create_nav_button(text, str(icon))
            # Use a lambda to pass the button's text when its clicked signal is emitted
            button.clicked.connect(lambda checked, name=text: self.on_button_clicked(checked, name))
            layout.addWidget(button)
            self.nav_buttons[text] = button

    def _create_nav_button(self, text: str, icon_path: str) -> QPushButton:
        """Factory method to create a consistent navigation button."""
        button = QPushButton(f"  {text}")
        if icon_path:
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(20, 20))
        button.setCheckable(True)
        button.setAutoExclusive(True)
        button.setObjectName("SidebarButton")
        return button

    def on_button_clicked(self, checked: bool, name: str):
        if checked:
            self.navigation_requested.emit(name)