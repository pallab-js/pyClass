from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QFrame,
)
from PySide6.QtCore import Qt, Signal, Slot
from submission import Submission


class SubmissionPanel(QFrame):
    """A panel for students to manage their assignment submission."""
    submit_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LoginCard")  # Reuse card style
        self.setFixedWidth(300)

        self.current_submission = None

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        title_label = QLabel("Your Work")
        title_label.setStyleSheet("font-size: 16px; font-weight: 500;")
        self.status_label = QLabel("Assigned")
        self.status_label.setStyleSheet("font-size: 13px; color: #9AA0A6;")
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.status_label)
        layout.addLayout(title_layout)

        self.file_label = QLabel("No file attached.")
        self.file_label.setStyleSheet("font-size: 13px; padding: 10px; background-color: #303134; border-radius: 4px;")
        layout.addWidget(self.file_label)

        self.add_file_button = QPushButton("Add File")
        self.add_file_button.clicked.connect(self.open_file_dialog)

        self.turn_in_button = QPushButton("Turn In")
        self.turn_in_button.setObjectName("AccentButton")
        self.turn_in_button.clicked.connect(self.turn_in)

        layout.addWidget(self.add_file_button)
        layout.addWidget(self.turn_in_button)
        layout.addStretch()

    def open_file_dialog(self):
        """Opens a file dialog to select a file for submission."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Submit")
        if file_path:
            # In a real app, you'd handle file uploads. Here, we just store the path.
            self.file_label.setText(file_path.split('/')[-1])
            self.file_label.setToolTip(file_path)

    def turn_in(self):
        """Emits the signal to submit the work."""
        file_path = self.file_label.toolTip()
        if file_path:
            self.submit_requested.emit(file_path)

    @Slot(Submission)
    def update_submission_status(self, submission):
        """Updates the UI based on the current submission status."""
        self.current_submission = submission
        if submission and submission.content:
            self.status_label.setText("Turned In")
            self.file_label.setText(submission.content.split('/')[-1])
            self.file_label.setToolTip(submission.content)
            self.add_file_button.setText("Change File")
            self.turn_in_button.setText("Resubmit")
        else:
            self.status_label.setText("Assigned")
            self.file_label.setText("No file attached.")
            self.file_label.setToolTip("")
            self.add_file_button.setText("Add File")
            self.turn_in_button.setText("Turn In")