from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt


class PlaceholderView(QWidget):
    """A simple placeholder view with a title."""
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel(f"{title} View")
        label.setStyleSheet("font-size: 28px; font-weight: 500; color: #9AA0A6;")

        layout.addWidget(label)