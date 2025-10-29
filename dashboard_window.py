from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QGraphicsDropShadowEffect,
    QSpacerItem,
)
from classroom import Classroom
from user import UserRole
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor


class ClassCard(QWidget):
    """A card representing a single class in the dashboard."""
    clicked = Signal(int)

    def __init__(self, classroom: Classroom, parent=None):
        super().__init__(parent)
        self.setFixedSize(280, 100)
        self.setObjectName("ClassCard")
        self.setCursor(QCursor(Qt.PointingHandCursor))

        # --- Add Shadow Effect ---
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor("#10000000") # Very transparent black
        self.setGraphicsEffect(shadow)
        # We need to set margins on the layout to make space for the shadow
        # This prevents the shadow from being clipped by the widget's boundaries.
        self.setContentsMargins(10, 10, 10, 10)

        self.classroom_id = classroom.id

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        name_label = QLabel(classroom.name)
        name_label.setObjectName("CardTitleLabel")
        name_label.setWordWrap(True)

        teacher_label = QLabel(classroom.teacher.email)
        teacher_label.setObjectName("CardSubtitleLabel")

        layout.addWidget(name_label)
        layout.addStretch()
        layout.addWidget(teacher_label)

    def mousePressEvent(self, event):
        """Emits the clicked signal when the card is pressed."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.classroom_id)
        super().mousePressEvent(event)


class DashboardWindow(QWidget):
    """The main dashboard view showing a grid of classes."""
    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(20)

        # --- Header Layout ---
        header_layout = QHBoxLayout()
        title = QLabel("Classes")
        title.setStyleSheet("font-size: 28px; font-weight: 500;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.join_class_button = QPushButton("Join Class")
        self.join_class_button.hide()
        header_layout.addWidget(self.join_class_button)

        self.create_class_button = QPushButton("Create Class")
        self.create_class_button.setObjectName("AccentButton") # For special styling
        self.create_class_button.hide() # Hidden by default
        header_layout.addWidget(self.create_class_button)


        main_layout.addLayout(header_layout)
        # --- End Header ---

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        content_widget = QWidget()
        self.grid_layout = QGridLayout(content_widget)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def set_user_role(self, role: UserRole):
        """Shows or hides UI elements based on the user's role."""
        self.create_class_button.setVisible(role == UserRole.teacher)
        self.join_class_button.setVisible(role == UserRole.student)

    def clear_classes(self):
        """Removes all class cards from the grid layout."""
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()