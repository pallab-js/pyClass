from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QHBoxLayout,
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QCursor
from user import UserRole


class AssignmentItem(QFrame):
    """A widget that displays a single assignment in a list."""
    clicked = Signal(int)

    def __init__(self, assignment, parent=None):
        super().__init__(parent)
        self.setObjectName("AssignmentItem")
        self.setFrameShape(QFrame.StyledPanel)
        self.setCursor(QCursor(Qt.PointingHandCursor))

        self.assignment_id = assignment.id

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        title_label = QLabel(assignment.title)
        title_label.setStyleSheet("font-size: 14px; font-weight: 500;")
        
        due_date_str = f"Due {assignment.due_date.strftime('%b %d, %Y')}" if assignment.due_date else "No due date"
        due_date_label = QLabel(due_date_str)
        due_date_label.setStyleSheet("font-size: 13px; color: #9AA0A6;")

        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(due_date_label)

    def mousePressEvent(self, event):
        """Emits the clicked signal when the item is pressed."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.assignment_id)
        super().mousePressEvent(event)


class ClassworkView(QWidget):
    """The view for the 'Classwork' tab, showing assignments."""
    assignment_selected = Signal(int)
    create_assignment_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(20)

        self.create_button = QPushButton("Create Assignment")
        self.create_button.setObjectName("AccentButton")
        self.create_button.setFixedWidth(150)
        self.create_button.clicked.connect(self.create_assignment_requested.emit)
        main_layout.addWidget(self.create_button, alignment=Qt.AlignLeft)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        self.assignments_container = QWidget()
        self.assignments_layout = QVBoxLayout(self.assignments_container)
        self.assignments_layout.setAlignment(Qt.AlignTop)
        self.assignments_layout.setSpacing(10)

        scroll_area.setWidget(self.assignments_container)
        main_layout.addWidget(scroll_area)

    def set_user_role(self, role: UserRole):
        """Show or hide the create button based on user role."""
        self.create_button.setVisible(role == UserRole.teacher)

    @Slot(list)
    def display_assignments(self, assignments: list):
        """Clears and populates the view with assignment items."""
        while self.assignments_layout.count():
            child = self.assignments_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for asn in assignments:
            item = AssignmentItem(asn)
            item.clicked.connect(self.assignment_selected.emit)
            self.assignments_layout.addWidget(item)