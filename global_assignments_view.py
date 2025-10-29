from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QScrollArea,
    QFrame,
    QHBoxLayout,
)
from PySide6.QtCore import Qt, Slot


class GlobalAssignmentItem(QFrame):
    """A widget that displays a single assignment with its class name."""
    def __init__(self, assignment, parent=None):
        super().__init__(parent)
        self.setObjectName("AssignmentItem") # Reuse style
        self.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout(self)
        
        title_label = QLabel(assignment.title)
        title_label.setStyleSheet("font-size: 14px; font-weight: 500;")

        class_name_label = QLabel(assignment.classroom.name)
        class_name_label.setStyleSheet("font-size: 12px; color: #8AB4F8;")

        due_date_str = f"Due {assignment.due_date.strftime('%b %d, %Y')}" if assignment.due_date else "No due date"
        due_date_label = QLabel(due_date_str)
        due_date_label.setStyleSheet("font-size: 13px; color: #9AA0A6;")

        top_layout = QHBoxLayout()
        top_layout.addWidget(title_label)
        top_layout.addStretch()
        top_layout.addWidget(due_date_label)

        layout.addLayout(top_layout)
        layout.addWidget(class_name_label)


class GlobalAssignmentsView(QWidget):
    """A view showing all assignments for a user across all classes."""
    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)

        title = QLabel("All Assignments")
        title.setStyleSheet("font-size: 28px; font-weight: 500;")
        main_layout.addWidget(title)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        container = QWidget()
        self.assignments_layout = QVBoxLayout(container)
        self.assignments_layout.setAlignment(Qt.AlignTop)
        self.assignments_layout.setSpacing(10)

        scroll_area.setWidget(container)
        main_layout.addWidget(scroll_area)

    @Slot(list)
    def display_assignments(self, assignments: list):
        """Clears and populates the view with assignment items."""
        while self.assignments_layout.count():
            child = self.assignments_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for asn in assignments:
            item = GlobalAssignmentItem(asn)
            self.assignments_layout.addWidget(item)