from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QFrame,
)
from PySide6.QtCore import Qt, Signal, Slot
from user import User


class SettingsView(QWidget):
    """A view for displaying and editing user settings."""
    save_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setAlignment(Qt.AlignTop)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 28px; font-weight: 500;")
        main_layout.addWidget(title)

        # --- Profile Form ---
        form_frame = QFrame()
        form_frame.setContentsMargins(0, 20, 0, 0)
        form_layout = QFormLayout(form_frame)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setRowWrapPolicy(QFormLayout.WrapAllRows)

        self.full_name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.email_input.setReadOnly(True) # Email is not editable

        form_layout.addRow("Full Name:", self.full_name_input)
        form_layout.addRow("Email:", self.email_input)

        main_layout.addWidget(form_frame)

        self.save_button = QPushButton("Save Changes")
        self.save_button.setObjectName("AccentButton")
        self.save_button.setFixedWidth(150)
        self.save_button.clicked.connect(self._on_save)
        main_layout.addWidget(self.save_button)

    @Slot(User)
    def load_user_data(self, user: User):
        """Populates the form with the user's current data."""
        self.full_name_input.setText(user.full_name or "")
        self.email_input.setText(user.email)

    def _on_save(self):
        """Emits the signal to save the updated settings."""
        self.save_requested.emit(self.full_name_input.text())