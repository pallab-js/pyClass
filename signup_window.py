from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QComboBox,
    QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Qt, Signal

from user import UserRole


class SignupWindow(QWidget):
    # Signal emitting user details for signup attempt
    signup_attempt = Signal(str, str, str, str)
    # Signal to request switching back to the login view
    show_login_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QHBoxLayout(self)
        main_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        card_widget = QWidget()
        card_widget.setObjectName("LoginCard") # Re-use the same style
        card_widget.setFixedSize(360, 500)

        # --- Add Shadow Effect ---
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor("#10000000")
        card_widget.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card_widget)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(15)

        # --- Widgets inside the card ---
        title_label = QLabel("Create Account")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: 500;")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        self.role_combo = QComboBox()
        # Populate with roles from the UserRole enum
        for role in UserRole:
            self.role_combo.addItem(role.name.capitalize(), role.value)

        self.signup_button = QPushButton("Sign Up")
        self.signup_button.clicked.connect(self._on_signup_clicked)

        self.back_to_login_button = QPushButton("Already have an account? Log In")
        self.back_to_login_button.setObjectName("LinkButton") # For specific styling
        self.back_to_login_button.clicked.connect(self.show_login_requested.emit)

        # --- Layouting the card ---
        card_layout.addStretch(1)
        card_layout.addWidget(title_label)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.email_input)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(self.confirm_password_input)
        card_layout.addWidget(self.role_combo)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.signup_button)
        card_layout.addWidget(self.back_to_login_button)
        card_layout.addStretch(1)

        main_layout.addWidget(card_widget)
        main_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

    def _on_signup_clicked(self):
        email = self.email_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        role = self.role_combo.currentData() # Get the enum value
        self.signup_attempt.emit(email, password, confirm_password, role)