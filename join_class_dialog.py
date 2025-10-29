from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QDialogButtonBox,
)
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMessageBox


class JoinClassDialog(QDialog):
    """A dialog for joining a class with a code."""

    # Signal emits the class code
    join_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Join Class")
        self.setFixedSize(350, 150)

        layout = QVBoxLayout(self)

        title_label = QLabel("Enter the class code to join")
        title_label.setStyleSheet("font-size: 16px; font-weight: 500;")
        layout.addWidget(title_label)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Class code")
        layout.addWidget(self.code_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept(self):
        code = self.code_input.text().strip()
        if not code:
            QMessageBox.warning(self, "Validation Error", "Class code is required.")
            return
        self.join_requested.emit(code)
        super().accept()