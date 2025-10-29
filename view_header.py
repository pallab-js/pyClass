from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal


class ViewHeader(QWidget):
    """A reusable header widget with a back button and a title."""
    back_requested = Signal()

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        self.back_button = QPushButton("← Back")
        self.back_button.setObjectName("LinkButton") # Reuse link style
        self.back_button.setFixedWidth(80)
        self.back_button.clicked.connect(self.back_requested.emit)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 28px; font-weight: 500;")

        layout.addWidget(self.back_button)
        layout.addWidget(self.title_label)
        layout.addStretch()

    def set_title(self, title: str):
        self.title_label.setText(title)