from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
    QHBoxLayout,
    QLineEdit,
)
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QDoubleValidator


class StudentSubmissionItem(QFrame):
    """A widget showing a single student's submission status and grade input."""
    # Emits submission_id, grade_text
    grade_entered = Signal(int, str)

    def __init__(self, student, submission, parent=None):
        super().__init__(parent)
        self.setObjectName("AssignmentItem") # Reuse style
        self.setFrameShape(QFrame.StyledPanel)

        self.submission = submission

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)

        student_label = QLabel(student.email)
        status_label = QLabel("Turned In" if submission else "Assigned")
        status_label.setStyleSheet("font-size: 13px; color: #9AA0A6;")

        self.grade_input = QLineEdit()
        self.grade_input.setPlaceholderText("Grade")
        self.grade_input.setFixedWidth(60)
        self.grade_input.setValidator(QDoubleValidator(0, 1000, 2)) # Allow float grades
        self.grade_input.editingFinished.connect(self._on_grade_entered)

        if submission and submission.grade is not None:
            self.grade_input.setText(str(submission.grade))

        layout.addWidget(student_label)
        layout.addStretch()
        layout.addWidget(status_label)
        layout.addWidget(self.grade_input)

    def _on_grade_entered(self):
        """Emits a signal when the teacher finishes editing a grade."""
        if self.submission: # Only emit if there is a submission to grade
            self.grade_entered.emit(self.submission.id, self.grade_input.text())


class GradingPanel(QFrame):
    """A panel for teachers to view and grade all submissions."""
    grade_submission_requested = Signal(int, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LoginCard") # Reuse card style
        self.setFixedWidth(300)

        layout = QVBoxLayout(self)
        title_label = QLabel("Student Work")
        title_label.setStyleSheet("font-size: 16px; font-weight: 500;")
        layout.addWidget(title_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        self.submissions_container = QWidget()
        self.submissions_layout = QVBoxLayout(self.submissions_container)
        self.submissions_layout.setAlignment(Qt.AlignTop)
        self.submissions_layout.setSpacing(5)

        scroll_area.setWidget(self.submissions_container)
        layout.addWidget(scroll_area)

    @Slot(list, list)
    def display_submissions(self, all_students: list, submissions: list):
        """Populates the panel with all students and their submission status."""
        # Clear existing items
        while self.submissions_layout.count():
            child = self.submissions_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        submissions_by_student_id = {s.student_id: s for s in submissions}

        for student in sorted(all_students, key=lambda s: s.email):
            submission = submissions_by_student_id.get(student.id)
            item = StudentSubmissionItem(student, submission)
            item.grade_entered.connect(self._handle_grade_entered)
            self.submissions_layout.addWidget(item)

    def _handle_grade_entered(self, submission_id: int, grade_text: str):
        """Converts grade text to float and emits the final signal."""
        if not grade_text.strip():
            return  # Empty grade, don't process
            
        try:
            grade = float(grade_text)
            # Clamp grade to valid range
            grade = max(0.0, min(10000.0, grade))
            self.grade_submission_requested.emit(submission_id, grade)
        except ValueError:
            # Reset the input to show error state
            for i in range(self.submissions_layout.count()):
                item = self.submissions_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if hasattr(widget, 'submission') and widget.submission and widget.submission.id == submission_id:
                        widget.grade_input.setText("")
                        widget.grade_input.setStyleSheet("border: 1px solid #E53E3E;")  # Red border for error
                        break