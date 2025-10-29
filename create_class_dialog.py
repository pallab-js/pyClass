from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QDialogButtonBox,
    QMessageBox,
)
from PySide6.QtCore import Signal


class CreateClassDialog(QDialog):
    """A dialog for creating a new class."""

    # Signal emits class name and section
    create_requested = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Class")
        self.setFixedSize(350, 200)

        layout = QVBoxLayout(self)

        title_label = QLabel("Create a new class")
        title_label.setStyleSheet("font-size: 16px; font-weight: 500;")
        layout.addWidget(title_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Class name (required)")
        layout.addWidget(self.name_input)

        self.section_input = QLineEdit()
        self.section_input.setPlaceholderText("Section (optional)")
        layout.addWidget(self.section_input)

        # Standard dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept(self):
        """Overrides the default accept to emit a signal before closing."""
        name = self.name_input.text().strip()
        section = self.section_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Class name is required.")
            return
        
        if len(name) > 100:
            QMessageBox.warning(self, "Validation Error", "Class name must be 100 characters or less.")
            return
            
        if len(section) > 50:
            QMessageBox.warning(self, "Validation Error", "Section must be 50 characters or less.")
            return
        
        self.create_requested.emit(name, section)
        super().accept()