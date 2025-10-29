from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QDateTimeEdit,
    QSpinBox,
    QDialogButtonBox,
    QFormLayout,
    QMessageBox,
)
from PySide6.QtCore import Signal, QDateTime


class CreateAssignmentDialog(QDialog):
    """A dialog for creating a new assignment."""

    # Emits title, instructions, due_date, points
    create_requested = Signal(str, str, object, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Assignment")
        self.setMinimumWidth(450)

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.title_input = QLineEdit()
        self.instructions_input = QTextEdit()
        self.instructions_input.setFixedHeight(100)
        self.points_input = QSpinBox()
        self.points_input.setRange(0, 1000)
        self.points_input.setValue(100)
        self.due_date_input = QDateTimeEdit(QDateTime.currentDateTime().addDays(7))
        self.due_date_input.setCalendarPopup(True)

        form_layout.addRow("Title:", self.title_input)
        form_layout.addRow("Instructions (optional):", self.instructions_input)
        form_layout.addRow("Points:", self.points_input)
        form_layout.addRow("Due Date:", self.due_date_input)

        main_layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def accept(self):
        """Overrides the default accept to emit a signal before closing."""
        title = self.title_input.text().strip()
        instructions = self.instructions_input.toPlainText().strip()
        points = self.points_input.value()
        due_date = self.due_date_input.dateTime().toPython()
        
        if not title:
            QMessageBox.warning(self, "Validation Error", "Assignment title is required.")
            return
        
        if len(title) > 200:
            QMessageBox.warning(self, "Validation Error", "Assignment title must be 200 characters or less.")
            return
            
        if len(instructions) > 2000:
            QMessageBox.warning(self, "Validation Error", "Instructions must be 2000 characters or less.")
            return
        
        if points < 0 or points > 10000:
            QMessageBox.warning(self, "Validation Error", "Points must be between 0 and 10,000.")
            return
        
        self.create_requested.emit(title, instructions, due_date, points)
        super().accept()