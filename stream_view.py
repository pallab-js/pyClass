from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QScrollArea,
    QFrame,
    QHBoxLayout,
    QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Qt, Signal, Slot
from user import UserRole


class AnnouncementCard(QFrame):
    """A card that displays a single announcement."""
    def __init__(self, announcement, parent=None):
        super().__init__(parent)
        self.setObjectName("AnnouncementCard")
        self.setFrameShape(QFrame.StyledPanel)

        # --- Add Shadow Effect ---
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor("#10000000")
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        author_text = f"{announcement.author.email} • {announcement.timestamp.strftime('%b %d, %Y')}"
        author_label = QLabel(author_text)
        author_label.setStyleSheet("font-size: 13px; color: #9AA0A6;")

        content_label = QLabel(announcement.content)
        content_label.setWordWrap(True)
        content_label.setStyleSheet("font-size: 14px;")

        layout.addWidget(author_label)
        layout.addWidget(content_label)


class StreamView(QWidget):
    """The view for the 'Stream' tab, showing announcements."""
    post_announcement_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)

        # --- Class Code Box (for teachers) ---
        self.class_code_box = QFrame()
        self.class_code_box.setObjectName("PostBox") # Reuse style
        self.class_code_box.setFrameShape(QFrame.StyledPanel)
        class_code_layout = QHBoxLayout(self.class_code_box)
        class_code_label = QLabel("Class code")
        class_code_label.setStyleSheet("font-size: 14px;")
        self.class_code_value = QLabel("xxxxxxx")
        self.class_code_value.setStyleSheet("font-size: 16px; font-weight: 500;")
        self.class_code_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        class_code_layout.addWidget(class_code_label)
        class_code_layout.addStretch()
        class_code_layout.addWidget(self.class_code_value)
        main_layout.addWidget(self.class_code_box)
        self.class_code_box.hide() # Hidden by default


        # --- Post Announcement Box ---
        self.post_box = QFrame()
        self.post_box.setObjectName("PostBox")
        self.post_box.setFrameShape(QFrame.StyledPanel)

        # --- Add Shadow Effect ---
        post_box_shadow = QGraphicsDropShadowEffect(self)
        post_box_shadow.setBlurRadius(20)
        post_box_shadow.setXOffset(0)
        post_box_shadow.setYOffset(4)
        post_box_shadow.setColor("#10000000")
        self.post_box.setGraphicsEffect(post_box_shadow)

        post_layout = QVBoxLayout(self.post_box)

        self.post_input = QTextEdit()
        self.post_input.setPlaceholderText("Announce something to your class")
        self.post_input.setFixedHeight(80)

        self.post_button = QPushButton("Post")
        self.post_button.setFixedWidth(100)
        self.post_button.clicked.connect(self._on_post_clicked)

        post_layout.addWidget(self.post_input)
        post_layout.addWidget(self.post_button, alignment=Qt.AlignRight)
        main_layout.addWidget(self.post_box)

        # --- Announcements List ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        self.announcements_container = QWidget()
        self.announcements_layout = QVBoxLayout(self.announcements_container)
        self.announcements_layout.setAlignment(Qt.AlignTop)
        self.announcements_layout.setSpacing(15)

        scroll_area.setWidget(self.announcements_container)
        main_layout.addWidget(scroll_area)

    def set_user_role(self, role: UserRole):
        """Show or hide the post box based on user role."""
        is_teacher = (role == UserRole.teacher)
        self.post_box.setVisible(is_teacher)
        self.class_code_box.setVisible(is_teacher)

    def display_class_code(self, code: str):
        self.class_code_value.setText(code)

    @Slot(list)
    def display_announcements(self, announcements: list):
        """Clears and populates the view with announcement cards."""
        # Clear existing announcements
        while self.announcements_layout.count():
            child = self.announcements_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for ann in announcements:
            self.add_announcement_card(ann)

    @Slot(object)
    def add_announcement_card(self, announcement):
        """Adds a single announcement card to the top of the list."""
        card = AnnouncementCard(announcement)
        self.announcements_layout.insertWidget(0, card)

    def _on_post_clicked(self):
        content = self.post_input.toPlainText()
        if content:
            self.post_announcement_requested.emit(content)
            self.post_input.clear()