from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from submission_panel import SubmissionPanel
from grading_panel import GradingPanel
from view_header import ViewHeader


class AssignmentWindow(QWidget):
    """The main view for a single assignment, with instructions and submission panel."""

    grade_assignment_requested = Signal(int, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.header = ViewHeader()
        self.current_assignment = None
        self.current_user = None

        # Main horizontal layout for the split view
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(20)

        # --- Left Side: Instructions ---
        instructions_panel = QWidget()
        instructions_layout = QVBoxLayout(instructions_panel)
        instructions_layout.setAlignment(Qt.AlignTop)

        instructions_layout.addWidget(self.header)
        self.points_due_label = QLabel("100 points • Due Sep 15")
        self.points_due_label.setStyleSheet("font-size: 13px; color: #9AA0A6; padding-bottom: 10px; border-bottom: 1px solid #3c4043;")

        self.instructions_label = QLabel("Assignment instructions will appear here.")
        self.instructions_label.setWordWrap(True)
        self.instructions_label.setAlignment(Qt.AlignTop)

        instructions_layout.addWidget(self.points_due_label)
        instructions_layout.addSpacing(20)
        instructions_layout.addWidget(self.instructions_label)

        # --- Right Side: Submission Panel ---
        self.grading_panel = GradingPanel()
        self.submission_panel = SubmissionPanel()
        self.grading_panel.grade_submission_requested.connect(self.grade_assignment_requested.emit)
        self.header.back_requested.connect(self.go_back) # Placeholder connection

        main_layout.addWidget(instructions_panel, stretch=2)
        main_layout.addWidget(self.submission_panel, stretch=1)
        main_layout.addWidget(self.grading_panel, stretch=1)

    def load_assignment(self, assignment, user):
        """Loads the data for a specific assignment into the view."""
        self.current_assignment = assignment
        self.current_user = user
        self.header.set_title(assignment.title)
        due_date_str = f"Due {assignment.due_date.strftime('%b %d')}" if assignment.due_date else "No due date"
        self.points_due_label.setText(f"{assignment.points or 0} points • {due_date_str}")
        self.instructions_label.setText(assignment.instructions or "No instructions provided.")

        is_student = user.role.value == 'student'
        self.submission_panel.setVisible(is_student)
        self.grading_panel.setVisible(not is_student)
        if is_student:
            self.submission_panel.update_submission_status(None) # Reset panel

    def go_back(self):
        # This method is a placeholder. The actual navigation will be handled by MainWindow.
        print("Back button clicked in AssignmentWindow")