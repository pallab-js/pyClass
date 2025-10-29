import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
    QToolBar,
    QPushButton,
    QWidget,
    QSpacerItem,
    QSizePolicy,
    QHBoxLayout,
    QMessageBox,
    QLabel,
)
from PySide6.QtCore import Slot

from login_window import LoginWindow
from signup_window import SignupWindow
from dashboard_window import DashboardWindow, ClassCard
from class_window import ClassWindow
from join_class_dialog import JoinClassDialog
from assignment_window import AssignmentWindow
from settings_view import SettingsView
from global_assignments_view import GlobalAssignmentsView
from create_class_dialog import CreateClassDialog
from create_assignment_dialog import CreateAssignmentDialog
from placeholder_views import PlaceholderView
from sidebar import Sidebar
from theme import ThemeManager
from auth_controller import AuthController
from classroom_controller import ClassroomController
from announcement_controller import AnnouncementController
from assignment_controller import AssignmentController
from settings_controller import SettingsController
from submission_controller import SubmissionController
from people_controller import PeopleController
from base import Base, engine, SessionLocal
from classroom import Classroom
from user import User, UserRole
from assignment import Assignment
from submission import Submission


class MainLayout(QWidget):
    """A widget that combines the Sidebar and the main content area (QStackedWidget)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.content_stack = QStackedWidget()

        layout.addWidget(self.sidebar)
        layout.addWidget(self.content_stack)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("pyClass")
        self.setGeometry(100, 100, 1280, 720)

        self.current_user = None

        self.theme_manager = ThemeManager(QApplication.instance())
        
        # Instantiate the controller
        self.auth_controller = AuthController()
        self.classroom_controller = ClassroomController()
        self.announcement_controller = AnnouncementController()
        self.assignment_controller = AssignmentController()
        self.people_controller = PeopleController()
        self.settings_controller = SettingsController()
        self.submission_controller = SubmissionController()

        # The main layout will contain the sidebar and the content stack
        self.main_layout = MainLayout()

        # --- Pre-Login Views ---
        self.pre_login_stack = QStackedWidget()
        self.login_view = LoginWindow()
        self.signup_view = SignupWindow()
        self.pre_login_stack.addWidget(self.login_view)
        self.pre_login_stack.addWidget(self.signup_view)

        # --- Post-Login Views ---
        self.dashboard_view = DashboardWindow()
        self.class_view = ClassWindow()
        self.assignment_view = AssignmentWindow()
        self.global_assignments_view = GlobalAssignmentsView()
        self.settings_view = SettingsView()

        # --- Main View Stack ---
        # This stack switches between the pre-login and post-login states
        self.view_stack = QStackedWidget()
        self.view_stack.addWidget(self.pre_login_stack)
        self.view_stack.addWidget(self.main_layout)
        self.setCentralWidget(self.view_stack)

        # --- Connect signals and slots ---
        self.login_view.login_attempt.connect(self.auth_controller.login)
        self.login_view.show_signup_requested.connect(lambda: self.pre_login_stack.setCurrentWidget(self.signup_view))
        self.signup_view.signup_attempt.connect(self.auth_controller.signup)
        self.signup_view.show_login_requested.connect(lambda: self.pre_login_stack.setCurrentWidget(self.login_view))
        self.auth_controller.login_successful.connect(self.on_login_successful)
        self.auth_controller.login_failed.connect(self.on_login_failed)
        self.auth_controller.signup_successful.connect(self.on_signup_successful)
        self.auth_controller.signup_failed.connect(self.on_signup_failed)
        self.classroom_controller.class_created.connect(self.on_class_created)
        self.classroom_controller.class_joined.connect(self.on_class_joined)
        self.classroom_controller.join_class_failed.connect(self.on_join_class_failed)        
        self.assignment_controller.class_assignments_fetched.connect(self.class_view.classwork_tab.display_assignments)
        self.assignment_controller.assignment_created.connect(lambda: self.assignment_controller.get_assignments_for_class(self.class_view.current_class_id))
        self.submission_controller.submission_fetched.connect(self.assignment_view.submission_panel.update_submission_status)
        self.submission_controller.submission_updated.connect(self.assignment_view.submission_panel.update_submission_status)
        self.submission_controller.all_submissions_fetched.connect(self.on_all_submissions_fetched)
        self.announcement_controller.announcements_fetched.connect(self.class_view.stream_tab.display_announcements)
        self.announcement_controller.announcement_created.connect(self.class_view.stream_tab.add_announcement_card)
        self.dashboard_view.create_class_button.clicked.connect(self.open_create_class_dialog)
        self.settings_view.save_requested.connect(self.save_settings)
        self.settings_controller.settings_updated.connect(self.on_settings_updated)
        self.dashboard_view.join_class_button.clicked.connect(self.open_join_class_dialog)
        self.main_layout.sidebar.navigation_requested.connect(self.navigate)
        self.assignment_view.submission_panel.submit_requested.connect(self.submit_work)
        self.assignment_view.grade_assignment_requested.connect(self.submission_controller.grade_submission)
        self.assignment_view.header.back_requested.connect(lambda: self.main_layout.content_stack.setCurrentWidget(self.class_view))
        self.class_view.header.back_requested.connect(lambda: self.main_layout.content_stack.setCurrentWidget(self.dashboard_view))
        self.class_view.stream_tab.post_announcement_requested.connect(self.post_announcement)
        self.class_view.classwork_tab.assignment_selected.connect(self.navigate_to_assignment)
        self.class_view.classwork_tab.create_assignment_requested.connect(self.open_create_assignment_dialog)

        self.classroom_controller.classes_fetched.connect(self.on_classes_fetched)
        self.assignment_controller.global_assignments_fetched.connect(self.global_assignments_view.display_assignments)
        
        # Controller signals for single-item fetches
        self.classroom_controller.class_fetched.connect(self.on_class_fetched)
        self.assignment_controller.assignment_fetched.connect(self.on_assignment_fetched)
        self._create_top_bar()

    def _create_top_bar(self):
        top_bar = QToolBar("TopBar")
        top_bar.setMovable(False)
        self.addToolBar(top_bar)
        self.top_bar = top_bar # Store the reference
        self.top_bar.hide() # Hide until user is logged in

        self.profile_label = QLabel()
        self.top_bar.addWidget(self.profile_label)

        # Spacer to push items to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.top_bar.addWidget(spacer)

    @Slot(str)
    def on_login_failed(self, reason: str):
        """Shows an error message box on login failure."""
        QMessageBox.warning(self, "Login Failed", reason)

    @Slot()
    def on_signup_successful(self):
        """Shows a success message and switches to the login view."""
        QMessageBox.information(self, "Signup Successful", "Your account has been created. Please log in.")
        self.pre_login_stack.setCurrentWidget(self.login_view)

    @Slot(str)
    def on_signup_failed(self, reason: str):
        """Shows an error message box on signup failure."""
        QMessageBox.warning(self, "Signup Failed", reason)

    def open_create_class_dialog(self):
        """Opens the dialog to create a new class."""
        dialog = CreateClassDialog(self)
        # Connect the dialog's signal to the controller's slot
        dialog.create_requested.connect(
            lambda name, section: self.classroom_controller.create_class(name, section, self.current_user))
        dialog.exec()

    def open_join_class_dialog(self):
        """Opens the dialog to join a class."""
        dialog = JoinClassDialog(self)
        dialog.join_requested.connect(
            lambda code: self.classroom_controller.join_class(code, self.current_user)
        )
        dialog.exec()

    @Slot(str)
    def open_create_assignment_dialog(self):
        """Opens the dialog to create a new assignment."""
        dialog = CreateAssignmentDialog(self)
        dialog.create_requested.connect(
            lambda title, instructions, due_date, points: self.assignment_controller.create_assignment(
                title, instructions, due_date, points, self.class_view.current_class_id
            )
        )
        dialog.exec()

    def on_join_class_failed(self, reason: str):
        """Shows an error message box on join class failure."""
        QMessageBox.warning(self, "Join Failed", reason)

    @Slot(str)
    def post_announcement(self, content: str):
        """Handles the request to post a new announcement."""
        if self.class_view.current_classroom:
            self.announcement_controller.create_announcement(
                content, self.class_view.current_classroom.id, self.current_user)

    @Slot(str)
    def submit_work(self, content: str):
        """Handles the request to submit work for an assignment."""
        assignment = self.assignment_view.current_assignment
        if assignment:
            self.submission_controller.create_or_update_submission(
                assignment.id, self.current_user, content)

    @Slot(str)
    def save_settings(self, full_name: str):
        """Handles the request to save user settings."""
        self.settings_controller.update_user_settings(self.current_user, full_name)

    @Slot(User)
    def on_settings_updated(self, updated_user: User):
        self.current_user = updated_user
        QMessageBox.information(self, "Success", "Your settings have been updated.")

    @Slot(User)
    def on_login_successful(self, user: User):
        """Switches to the dashboard view on successful login."""
        self.current_user = user
        print(f"Login successful for {user.email} ({user.role.value})")

        # Update UI elements
        self.profile_label.setText(f"Welcome, {self.current_user.email}")
        self.top_bar.show()

        # Show role-specific UI elements
        self.dashboard_view.set_user_role(self.current_user.role)

        # --- Create and map the main application views ---
        self.content_views = {
            "Classes": self.dashboard_view,
            "AssignmentView": self.assignment_view, # A view not directly in the sidebar
            "ClassView": self.class_view, # A view not directly in the sidebar
            "Calendar": PlaceholderView("Calendar"), # Still a placeholder
            "Assignments": self.global_assignments_view,
            "Settings": self.settings_view,
        }


        # Add post-login views to the content stack inside MainLayout
        for view in self.content_views.values():
            self.main_layout.content_stack.addWidget(view)

        # Request the classes for the current user
        self.classroom_controller.get_classes_for_user(self.current_user)

        # Set the initial view to Classes/Dashboard
        self.main_layout.sidebar.nav_buttons["Classes"].setChecked(True)
        self.navigate("Classes")

        # Switch the main view from Login to the MainLayout (Sidebar + Content)
        self.view_stack.setCurrentWidget(self.main_layout)

    @Slot(list)
    def on_classes_fetched(self, classes: list):
        """Populates the dashboard with the fetched classes."""
        self.dashboard_view.clear_classes()
        for classroom in classes:
            self._add_class_card_to_dashboard(classroom)

    @Slot(str)
    def navigate(self, view_name: str):
        """Switches the view in the main content area."""
        if view_name in self.content_views:
            # If navigating to global assignments, fetch the data
            if view_name == "Assignments":
                self.assignment_controller.get_all_assignments_for_user(self.current_user)
            # If navigating to settings, load the user's data
            if view_name == "Settings":
                self.settings_view.load_user_data(self.current_user)
            self.main_layout.content_stack.setCurrentWidget(self.content_views[view_name])

    @Slot(int)
    def navigate_to_class(self, classroom_id: int):
        """Requests the controller to fetch a specific class and then navigates."""
        self.classroom_controller.get_class_by_id(classroom_id)

    @Slot(Classroom)
    def on_class_fetched(self, classroom: Classroom):
        """Callback for when a single class is fetched, to populate the class view."""
        if classroom:
            self.class_view.load_class(classroom)
            self.class_view.stream_tab.set_user_role(self.current_user.role)
            self.class_view.classwork_tab.set_user_role(self.current_user.role)
            self.main_layout.content_stack.setCurrentWidget(self.class_view)
            # Fetch related data
            self.announcement_controller.get_announcements_for_class(classroom.id)
            self.assignment_controller.get_assignments_for_class(classroom.id)
            # The classroom object already has teacher and students loaded.
            self.class_view.people_tab.display_people(classroom.teacher, classroom.students)

    @Slot(int)
    def navigate_to_assignment(self, assignment_id: int):
        """Requests the controller to fetch a specific assignment and then navigates."""
        self.assignment_controller.get_assignment_by_id(assignment_id)

    @Slot(Assignment)
    def on_assignment_fetched(self, assignment: Assignment):
        """Callback for when a single assignment is fetched, to populate the assignment view."""
        if assignment:
            self.assignment_view.load_assignment(assignment, self.current_user)
            self.main_layout.content_stack.setCurrentWidget(self.assignment_view)
            if self.current_user.role.value == 'student':
                self.submission_controller.get_submission(assignment.id, self.current_user.id)
            else: # Teacher
                self.submission_controller.get_all_submissions_for_assignment(assignment.id)

    @Slot(list)
    def on_all_submissions_fetched(self, submissions: list):
        """Provides the grading panel with the data it needs."""
        current_classroom = self.class_view.current_classroom
        if current_classroom:
            # The classroom object already has students loaded from when we navigated to it.
            self.assignment_view.grading_panel.display_submissions(current_classroom.students, submissions)

    def _add_class_card_to_dashboard(self, classroom: Classroom):
        """Adds a new class card to the dashboard when a class is created."""
        card = ClassCard(classroom)
        card.clicked.connect(self.navigate_to_class)
        count = self.dashboard_view.grid_layout.count()
        self.dashboard_view.grid_layout.addWidget(card, count // 3, count % 3)

    @Slot(Classroom)
    def on_class_created(self, new_class):
        self._add_class_card_to_dashboard(new_class)
        QMessageBox.information(
            self,
            "Class Created Successfully",
            f"The class '{new_class.name}' has been created.\n\n"
            f"Share this code with your students to join: {new_class.class_code}"
        )

    @Slot(Classroom)
    def on_class_joined(self, new_class):
        self._add_class_card_to_dashboard(new_class)
        QMessageBox.information(
            self,
            "Class Joined",
            f"You have successfully joined '{new_class.name}'."
        )

def setup_database():
    """Creates database tables and a dummy user for testing."""
    from classroom import student_classroom_association
    # Import all models here so Base knows about them
    from submission import Submission
    from assignment import Assignment
    from announcement import Announcement

    Base.metadata.create_all(bind=engine)
    
    # Optional: Create a dummy user for easy testing
    from base import SessionLocal
    db = SessionLocal()
    if not db.query(User).filter(User.email == "teacher@example.com").first():
        print("Creating dummy teacher user...")
        teacher = User(email="teacher@example.com", role="teacher")
        teacher.set_password("password")
        db.add(teacher)
        db.commit()
    if not db.query(User).filter(User.email == "student@example.com").first():
        print("Creating dummy student user...")
        student = User(email="student@example.com", role=UserRole.student)
        student.set_password("password")
        db.add(student)
        db.commit()
    db.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    setup_database()

    window = MainWindow()
    window.show()
    sys.exit(app.exec())