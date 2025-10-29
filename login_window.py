from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Qt, Signal


class LoginWindow(QWidget):
    # Signal emitting email and password for login attempt
    login_attempt = Signal(str, str)
    # Signal to request showing the signup view
    show_signup_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Main layout for centering the login card
        main_layout = QHBoxLayout(self)
        main_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Central card widget
        card_widget = QWidget()
        card_widget.setObjectName("LoginCard")
        card_widget.setFixedSize(360, 400)

        # --- Add Shadow Effect ---
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor("#10000000")
        card_widget.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card_widget)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(20)

        # --- Widgets inside the card ---
        title_label = QLabel("Welcome Back")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: 500;")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Log In")
        self.login_button.clicked.connect(self._on_login_clicked)

        self.go_to_signup_button = QPushButton("Don't have an account? Sign Up")
        self.go_to_signup_button.setObjectName("LinkButton")
        self.go_to_signup_button.clicked.connect(self.show_signup_requested.emit)

        # --- Layouting the card ---
        card_layout.addStretch()
        card_layout.addWidget(title_label)
        card_layout.addSpacing(20)
        card_layout.addWidget(self.email_input)
        card_layout.addWidget(self.password_input)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.login_button)
        card_layout.addWidget(self.go_to_signup_button)
        card_layout.addStretch()

        main_layout.addWidget(card_widget)
        main_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

    def _on_login_clicked(self):
        email = self.email_input.text()
        password = self.password_input.text()
        self.login_attempt.emit(email, password)