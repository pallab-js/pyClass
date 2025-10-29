from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout
from PySide6.QtCore import Slot, Qt


class UserItem(QFrame):
    """A reusable widget to display a user in a list."""
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.setObjectName("LoginCard")  # Reuse a card style with a border
        self.setStyleSheet("border-radius: 4px; padding: 8px;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(f"  {user.email}")
        label.setStyleSheet("font-size: 14px; border: none;")
        layout.addWidget(label)


class PeopleView(QWidget):
    """The view for the 'People' tab, showing teacher and students."""

    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setAlignment(Qt.AlignTop)

        # --- Teacher Section ---
        teacher_title = QLabel("Teacher")
        teacher_title.setStyleSheet("font-size: 20px; color: #AAAAAA; padding-bottom: 8px; border-bottom: 1px solid #444444;")
        main_layout.addWidget(teacher_title)

        self.teacher_layout = QVBoxLayout()
        self.teacher_layout.setSpacing(10)
        main_layout.addLayout(self.teacher_layout)

        # --- Students Section ---
        students_title = QLabel("Classmates")
        students_title.setStyleSheet("font-size: 20px; color: #AAAAAA; padding-bottom: 8px; border-bottom: 1px solid #444444;")
        main_layout.addWidget(students_title)

        self.students_layout = QVBoxLayout()
        self.students_layout.setSpacing(10)
        main_layout.addLayout(self.students_layout)

    def _clear_layout(self, layout):
        """Removes all widgets from a given layout."""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    @Slot(object, list)
    def display_people(self, teacher, students: list):
        """Clears and populates the view with the teacher and students."""
        self._clear_layout(self.teacher_layout)
        self._clear_layout(self.students_layout)

        if teacher:
            self.teacher_layout.addWidget(UserItem(teacher))

        for student in sorted(students, key=lambda s: s.email):
            self.students_layout.addWidget(UserItem(student))

    def clear_view(self):
        """Clears all content from the view."""
        self._clear_layout(self.teacher_layout)
        self._clear_layout(self.students_layout)