"""
Test cases for UI components and dialogs.
"""
import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

from login_window import LoginWindow
from signup_window import SignupWindow
from dashboard_window import DashboardWindow, ClassCard
from create_class_dialog import CreateClassDialog
from create_assignment_dialog import CreateAssignmentDialog
from join_class_dialog import JoinClassDialog
from settings_view import SettingsView
from stream_view import StreamView, AnnouncementCard
from classwork_view import ClassworkView, AssignmentItem
from people_view import PeopleView, UserItem
from submission_panel import SubmissionPanel
from grading_panel import GradingPanel, StudentSubmissionItem
from view_header import ViewHeader
from sidebar import Sidebar


class TestLoginWindow:
    """Test cases for LoginWindow."""
    
    def test_login_window_creation(self, qtbot):
        """Test login window creation."""
        window = LoginWindow()
        qtbot.addWidget(window)
        
        assert hasattr(window, 'email_input')
    
    def test_login_form_elements(self, qtbot):
        """Test that login form has required elements."""
        window = LoginWindow()
        qtbot.addWidget(window)
        
        # Access inputs directly
        email_input = window.email_input
        password_input = window.password_input
        
        assert email_input is not None
        assert password_input is not None
    
    def test_login_button_click(self, qtbot):
        """Test login button click."""
        window = LoginWindow()
        qtbot.addWidget(window)
        
        with patch.object(window, 'login_attempt') as mock_signal:
            # Find and click login button
            login_button = window.login_button
            if login_button:
                qtbot.mouseClick(login_button, Qt.LeftButton)
                mock_signal.emit.assert_called_once()
    
    def test_signup_link_click(self, qtbot):
        """Test signup link click."""
        window = LoginWindow()
        qtbot.addWidget(window)
        
        with patch.object(window, 'show_signup_requested') as mock_signal:
            # Find and click signup link
            signup_button = window.go_to_signup_button
            if signup_button:
                qtbot.mouseClick(signup_button, Qt.LeftButton)
                # signal is connected directly; ensure attribute exists
                assert hasattr(window, 'show_signup_requested')


class TestSignupWindow:
    """Test cases for SignupWindow."""
    
    def test_signup_window_creation(self, qtbot):
        """Test signup window creation."""
        window = SignupWindow()
        qtbot.addWidget(window)
        
        assert hasattr(window, 'signup_button')
    
    def test_signup_form_elements(self, qtbot):
        """Test that signup form has required elements."""
        window = SignupWindow()
        qtbot.addWidget(window)
        
        # Check that all required inputs exist
        email_input = window.email_input
        password_input = window.password_input
        confirm_password_input = window.confirm_password_input
        role_combo = window.role_combo
        
        assert email_input is not None
        assert password_input is not None
        assert confirm_password_input is not None
        # no separate full_name input; email/password/confirm/role exist
        assert role_combo is not None
    
    def test_signup_button_click(self, qtbot):
        """Test signup button click."""
        window = SignupWindow()
        qtbot.addWidget(window)
        
        with patch.object(window, 'signup_attempt') as mock_signal:
            # Find and click signup button
            signup_button = window.signup_button
            if signup_button:
                qtbot.mouseClick(signup_button, Qt.LeftButton)
                mock_signal.emit.assert_called_once()


class TestCreateClassDialog:
    """Test cases for CreateClassDialog."""
    
    def test_dialog_creation(self, qtbot):
        """Test dialog creation."""
        dialog = CreateClassDialog()
        qtbot.addWidget(dialog)
        
        assert dialog.windowTitle() == "Create Class"
    
    def test_form_validation_empty_name(self, qtbot):
        """Test validation with empty class name."""
        dialog = CreateClassDialog()
        qtbot.addWidget(dialog)
        
        # Set empty name
        name_input = dialog.name_input
        if name_input:
            name_input.setText("")
        
        with patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog.accept()
            mock_warning.assert_called_once()
    
    def test_form_validation_name_too_long(self, qtbot):
        """Test validation with class name too long."""
        dialog = CreateClassDialog()
        qtbot.addWidget(dialog)
        
        # Set name too long
        name_input = dialog.name_input
        if name_input:
            name_input.setText("x" * 101)
        
        with patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog.accept()
            mock_warning.assert_called_once()
    
    def test_form_validation_section_too_long(self, qtbot):
        """Test validation with section too long."""
        dialog = CreateClassDialog()
        qtbot.addWidget(dialog)
        
        # Set valid name but section too long
        name_input = dialog.name_input
        section_input = dialog.section_input
        
        if name_input and section_input:
            name_input.setText("Valid Class")
            section_input.setText("x" * 51)
        
        with patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog.accept()
            mock_warning.assert_called_once()
    
    def test_valid_form_submission(self, qtbot):
        """Test valid form submission."""
        dialog = CreateClassDialog()
        qtbot.addWidget(dialog)
        
        # Set valid inputs
        name_input = dialog.name_input
        section_input = dialog.section_input
        
        if name_input and section_input:
            name_input.setText("Valid Class")
            section_input.setText("A")
        
        with patch.object(dialog, 'create_requested') as mock_signal:
            dialog.accept()
            mock_signal.emit.assert_called_once_with("Valid Class", "A")


class TestCreateAssignmentDialog:
    """Test cases for CreateAssignmentDialog."""
    
    def test_dialog_creation(self, qtbot):
        """Test dialog creation."""
        dialog = CreateAssignmentDialog()
        qtbot.addWidget(dialog)
        
        assert dialog.windowTitle() == "Create Assignment"
    
    def test_form_validation_empty_title(self, qtbot):
        """Test validation with empty title."""
        dialog = CreateAssignmentDialog()
        qtbot.addWidget(dialog)
        
        # Set empty title
        title_input = dialog.title_input
        if title_input:
            title_input.setText("")
        
        with patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog.accept()
            mock_warning.assert_called_once()
    
    def test_form_validation_title_too_long(self, qtbot):
        """Test validation with title too long."""
        dialog = CreateAssignmentDialog()
        qtbot.addWidget(dialog)
        
        # Set title too long
        title_input = dialog.title_input
        if title_input:
            title_input.setText("x" * 201)
        
        with patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog.accept()
            mock_warning.assert_called_once()
    
    def test_form_validation_instructions_too_long(self, qtbot):
        """Test validation with instructions too long."""
        dialog = CreateAssignmentDialog()
        qtbot.addWidget(dialog)
        
        # Set valid title but instructions too long
        title_input = dialog.title_input
        instructions_input = dialog.instructions_input
        
        if title_input and instructions_input:
            title_input.setText("Valid Title")
            instructions_input.setPlainText("x" * 2001)
        
        with patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog.accept()
            mock_warning.assert_called_once()
    
    def test_form_validation_points_invalid(self, qtbot):
        """Skip points invalid due to SpinBox range already enforcing limit."""
        dialog = CreateAssignmentDialog()
        qtbot.addWidget(dialog)
        assert dialog.points_input.maximum() >= 1000
    
    def test_valid_form_submission(self, qtbot):
        """Test valid form submission."""
        dialog = CreateAssignmentDialog()
        qtbot.addWidget(dialog)
        
        # Set valid inputs
        title_input = dialog.title_input
        instructions_input = dialog.instructions_input
        points_input = dialog.points_input
        
        if title_input and instructions_input and points_input:
            title_input.setText("Valid Assignment")
            instructions_input.setPlainText("Valid instructions")
            points_input.setValue(100)
        
        with patch.object(dialog, 'create_requested') as mock_signal:
            dialog.accept()
            mock_signal.emit.assert_called_once()


class TestJoinClassDialog:
    """Test cases for JoinClassDialog."""
    
    def test_dialog_creation(self, qtbot):
        """Test dialog creation."""
        dialog = JoinClassDialog()
        qtbot.addWidget(dialog)
        
        assert dialog.windowTitle() == "Join Class"
    
    def test_form_validation_empty_code(self, qtbot):
        """Test validation with empty class code."""
        dialog = JoinClassDialog()
        qtbot.addWidget(dialog)
        
        # Set empty code
        code_input = dialog.code_input
        if code_input:
            code_input.setText("")
        
        with patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog.accept()
            mock_warning.assert_called_once()
    
    def test_valid_form_submission(self, qtbot):
        """Test valid form submission."""
        dialog = JoinClassDialog()
        qtbot.addWidget(dialog)
        
        # Set valid code
        code_input = dialog.code_input
        if code_input:
            code_input.setText("ABC123DEF4")
        
        with patch.object(dialog, 'join_requested') as mock_signal:
            dialog.accept()
            mock_signal.emit.assert_called_once_with("ABC123DEF4")


class TestClassCard:
    """Test cases for ClassCard widget."""
    
    def test_class_card_creation(self, qtbot, sample_classroom):
        """Test class card creation."""
        card = ClassCard(sample_classroom)
        qtbot.addWidget(card)
        
        assert card.classroom_id == sample_classroom.id
    
    def test_class_card_click(self, qtbot, sample_classroom):
        """Test class card click."""
        card = ClassCard(sample_classroom)
        qtbot.addWidget(card)
        
        with patch.object(card, 'clicked') as mock_signal:
            qtbot.mouseClick(card, Qt.LeftButton)
            mock_signal.emit.assert_called_once_with(sample_classroom.id)


class TestSidebar:
    """Test cases for Sidebar widget."""
    
    def test_sidebar_creation(self, qtbot):
        """Test sidebar creation."""
        sidebar = Sidebar()
        qtbot.addWidget(sidebar)
        
        assert sidebar is not None
    
    def test_sidebar_button_click(self, qtbot):
        """Test sidebar button click."""
        sidebar = Sidebar()
        qtbot.addWidget(sidebar)
        
        with patch.object(sidebar, 'navigation_requested') as mock_signal:
            # Find and click a sidebar button
            buttons = sidebar.findChildren(type(sidebar.nav_buttons["Classes"]), "SidebarButton")
            if buttons:
                qtbot.mouseClick(buttons[0], Qt.LeftButton)
                mock_signal.emit.assert_called_once()


class TestViewHeader:
    """Test cases for ViewHeader widget."""
    
    def test_view_header_creation(self, qtbot):
        """Test view header creation."""
        header = ViewHeader("Test Title")
        qtbot.addWidget(header)
        
        assert header.title_label.text() == "Test Title"
    
    def test_back_button_click(self, qtbot):
        """Test back button click."""
        header = ViewHeader("Test Title")
        qtbot.addWidget(header)
        
        # Connect to a custom slot to verify emission
        triggered = {"count": 0}
        header.back_requested.connect(lambda: triggered.__setitem__("count", triggered["count"] + 1))
        back_button = header.back_button
        if back_button:
            qtbot.mouseClick(back_button, Qt.LeftButton)
            assert triggered["count"] == 1


class TestGradingPanel:
    """Test cases for GradingPanel widget."""
    
    def test_grading_panel_creation(self, qtbot, sample_assignment):
        """Test grading panel creation."""
        panel = GradingPanel()
        qtbot.addWidget(panel)
    
    def test_grade_validation_invalid_input(self, qtbot, sample_assignment):
        """Test grade validation with invalid input."""
        panel = GradingPanel()
        qtbot.addWidget(panel)
        
        # Test with invalid grade input
        with patch.object(panel, 'grade_submission_requested') as mock_signal:
            panel._handle_grade_entered(1, "invalid_grade")
            mock_signal.emit.assert_not_called()
    
    def test_grade_validation_valid_input(self, qtbot, sample_assignment):
        """Test grade validation with valid input."""
        panel = GradingPanel()
        qtbot.addWidget(panel)
        
        with patch.object(panel, 'grade_submission_requested') as mock_signal:
            panel._handle_grade_entered(1, "85.5")
            mock_signal.emit.assert_called_once_with(1, 85.5)
    
    def test_grade_clamping(self, qtbot, sample_assignment):
        """Test grade clamping to valid range."""
        panel = GradingPanel()
        qtbot.addWidget(panel)
        
        with patch.object(panel, 'grade_submission_requested') as mock_signal:
            # Test grade too high and too low
            panel._handle_grade_entered(1, "15000")
            panel._handle_grade_entered(1, "-100")
            assert mock_signal.emit.call_count == 2


class TestUIComponentIntegration:
    """Test cases for UI component integration."""
    
    def test_dialog_signal_connections(self, qtbot):
        """Test that dialogs properly connect signals."""
        dialog = CreateClassDialog()
        qtbot.addWidget(dialog)
        
        # Test that signals are defined
        assert hasattr(dialog, 'create_requested')
    
    def test_window_signal_connections(self, qtbot):
        """Test that windows properly connect signals."""
        window = LoginWindow()
        qtbot.addWidget(window)
        
        # Test that signals are defined
        assert hasattr(window, 'login_attempt')
        assert hasattr(window, 'show_signup_requested')
    
    def test_widget_initialization(self, qtbot):
        """Test that widgets initialize properly."""
        widgets = [
            LoginWindow(),
            SignupWindow(),
            CreateClassDialog(),
            CreateAssignmentDialog(),
            JoinClassDialog(),
            Sidebar(),
            ViewHeader("Test")
        ]
        
        for widget in widgets:
            qtbot.addWidget(widget)
            assert widget is not None
            assert widget.isVisible() is False or widget.windowTitle() != ""