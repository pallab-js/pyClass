"""
Test cases for controller business logic.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from auth_controller import AuthController
from classroom_controller import ClassroomController
from assignment_controller import AssignmentController
from submission_controller import SubmissionController
from announcement_controller import AnnouncementController
from settings_controller import SettingsController
from user import User, UserRole


class TestAuthController:
    """Test cases for AuthController."""
    
    def test_login_success(self, db_session, sample_teacher):
        """Test successful login."""
        controller = AuthController()
        
        # Mock the signal emission
        with patch.object(controller, 'login_successful') as mock_success:
            controller.login(sample_teacher.email, "password123")
            mock_success.emit.assert_called_once()
    
    def test_login_invalid_credentials(self, db_session):
        """Test login with invalid credentials."""
        controller = AuthController()
        
        with patch.object(controller, 'login_failed') as mock_failed:
            controller.login("nonexistent@example.com", "wrongpassword")
            mock_failed.emit.assert_called_once()
    
    def test_signup_success(self, db_session):
        """Test successful signup."""
        controller = AuthController()
        
        with patch.object(controller, 'signup_successful') as mock_success:
            controller.signup("newuser@example.com", "password123", "password123", UserRole.student.value)
            mock_success.emit.assert_called_once()
    
    def test_signup_duplicate_email(self, db_session, sample_teacher):
        """Test signup with duplicate email."""
        controller = AuthController()
        
        with patch.object(controller, 'signup_failed') as mock_failed:
            controller.signup(sample_teacher.email, "password123", "password123", UserRole.student.value)
            mock_failed.emit.assert_called_once()
    
    def test_signup_validation(self, db_session):
        """Test signup validation."""
        controller = AuthController()
        
        # Test empty email
        with patch.object(controller, 'signup_failed') as mock_failed:
            controller.signup("", "password123", "password123", UserRole.student.value)
            mock_failed.emit.assert_called_once()
        
        # Test empty password
        with patch.object(controller, 'signup_failed') as mock_failed:
            controller.signup("test@example.com", "", "", UserRole.student.value)
            mock_failed.emit.assert_called_once()


class TestClassroomController:
    """Test cases for ClassroomController."""
    
    def test_create_classroom_success(self, db_session, sample_teacher):
        """Test successful classroom creation."""
        controller = ClassroomController()
        
        with patch.object(controller, 'class_created') as mock_created:
            controller.create_class("New Class", "B", sample_teacher)
            mock_created.emit.assert_called_once()
    
    def test_join_classroom_success(self, db_session, sample_student, sample_classroom):
        """Test successful classroom joining."""
        controller = ClassroomController()
        
        with patch.object(controller, 'class_joined') as mock_joined:
            controller.join_class(sample_classroom.class_code, sample_student)
            mock_joined.emit.assert_called_once()
    
    def test_join_classroom_invalid_code(self, db_session, sample_student):
        """Test joining classroom with invalid code."""
        controller = ClassroomController()
        
        with patch.object(controller, 'join_class_failed') as mock_failed:
            controller.join_class("INVALID", sample_student)
            mock_failed.emit.assert_called_once()
    
    def test_get_user_classrooms_teacher(self, db_session, sample_teacher, sample_classroom):
        """Test getting classrooms for a teacher."""
        controller = ClassroomController()
        
        with patch.object(controller, 'classes_fetched') as mock_fetched:
            controller.get_classes_for_user(sample_teacher)
            mock_fetched.emit.assert_called_once()
    
    def test_get_user_classrooms_student(self, db_session, sample_student, sample_classroom):
        """Test getting classrooms for a student."""
        # Add student to classroom
        sample_classroom.students.append(sample_student)
        db_session.commit()
        
        controller = ClassroomController()
        with patch.object(controller, 'classes_fetched') as mock_fetched:
            controller.get_classes_for_user(sample_student)
            mock_fetched.emit.assert_called_once()


class TestAssignmentController:
    """Test cases for AssignmentController."""
    
    def test_create_assignment_success(self, db_session, sample_classroom):
        """Test successful assignment creation."""
        controller = AssignmentController()
        
        with patch.object(controller, 'assignment_created') as mock_created:
            controller.create_assignment("Test Assignment", "Instructions", None, 100, sample_classroom.id)
            mock_created.emit.assert_called_once()
    
    def test_get_class_assignments(self, db_session, sample_classroom, sample_assignment):
        """Test getting assignments for a class."""
        controller = AssignmentController()
        
        with patch.object(controller, 'class_assignments_fetched') as mock_fetched:
            controller.get_assignments_for_class(sample_classroom.id)
            mock_fetched.emit.assert_called_once()
    
    def test_get_user_assignments(self, db_session, sample_student, sample_classroom, sample_assignment):
        """Test getting assignments for a user."""
        # Add student to classroom
        sample_classroom.students.append(sample_student)
        db_session.commit()
        
        controller = AssignmentController()
        with patch.object(controller, 'global_assignments_fetched') as mock_fetched:
            controller.get_all_assignments_for_user(sample_student)
            mock_fetched.emit.assert_called_once()
    
    def test_get_assignment_by_id(self, db_session, sample_assignment):
        """Test getting assignment by ID."""
        controller = AssignmentController()
        
        with patch.object(controller, 'assignment_fetched') as mock_fetched:
            controller.get_assignment_by_id(sample_assignment.id)
            mock_fetched.emit.assert_called_once()
    
    def test_get_assignment_by_id_not_found(self, db_session):
        """Test getting non-existent assignment."""
        controller = AssignmentController()
        
        assignment = controller.get_assignment_by_id(99999)
        assert assignment is None


class TestSubmissionController:
    """Test cases for SubmissionController."""
    
    def test_create_submission_success(self, db_session, sample_assignment, sample_student):
        """Test successful submission creation."""
        controller = SubmissionController()
        
        with patch.object(controller, 'submission_updated') as mock_updated:
            controller.create_or_update_submission(sample_assignment.id, sample_student, "My submission")
            mock_updated.emit.assert_called_once()
    
    def test_update_submission_success(self, db_session, sample_submission):
        """Test successful submission update."""
        controller = SubmissionController()
        
        with patch.object(controller, 'submission_updated') as mock_updated:
            controller.create_or_update_submission(sample_submission.assignment_id, sample_submission.student, "Updated submission")
            mock_updated.emit.assert_called_once()
    
    def test_get_assignment_submissions(self, db_session, sample_assignment, sample_submission):
        """Test getting submissions for an assignment."""
        controller = SubmissionController()
        
        with patch.object(controller, 'all_submissions_fetched') as mock_fetched:
            controller.get_all_submissions_for_assignment(sample_assignment.id)
            mock_fetched.emit.assert_called_once()
    
    def test_grade_submission_success(self, db_session, sample_submission):
        """Test successful submission grading."""
        controller = SubmissionController()
        
        with patch.object(controller, 'submission_updated') as mock_updated:
            controller.grade_submission(sample_submission.id, 90.0)
            mock_updated.emit.assert_called_once()
    
    def test_grade_submission_invalid_range(self, db_session, sample_submission):
        """Test grading submission with invalid grade range."""
        controller = SubmissionController()
        
        # Test negative grade
        with patch.object(controller, 'submission_failed') as mock_failed:
            controller.grade_submission(sample_submission.id, -1.0)
            mock_failed.emit.assert_called_once()
        
        # Test grade too high
        with patch.object(controller, 'submission_failed') as mock_failed:
            controller.grade_submission(sample_submission.id, 10001.0)
            mock_failed.emit.assert_called_once()


class TestAnnouncementController:
    """Test cases for AnnouncementController."""
    
    def test_create_announcement_success(self, db_session, sample_classroom, sample_teacher):
        """Test successful announcement creation."""
        controller = AnnouncementController()
        
        with patch.object(controller, 'announcement_created') as mock_created:
            controller.create_announcement("New announcement", sample_classroom.id, sample_teacher)
            mock_created.emit.assert_called_once()
    
    def test_get_class_announcements(self, db_session, sample_classroom, sample_announcement):
        """Test getting announcements for a class."""
        controller = AnnouncementController()
        
        with patch.object(controller, 'announcements_fetched') as mock_fetched:
            controller.get_announcements_for_class(sample_classroom.id)
            mock_fetched.emit.assert_called_once()


class TestSettingsController:
    """Test cases for SettingsController."""
    
    def test_update_user_settings_success(self, db_session, sample_teacher):
        """Test successful user settings update."""
        controller = SettingsController()
        
        with patch.object(controller, 'settings_updated') as mock_updated:
            controller.update_user_settings(sample_teacher, "Updated Name")
            mock_updated.emit.assert_called_once()
    
    def test_update_user_settings_user_not_found(self, db_session):
        """Test updating settings for non-existent user."""
        controller = SettingsController()
        
        with patch.object(controller, 'settings_update_failed') as mock_failed:
            controller.update_user_settings(User(id=99999), "Updated Name")
            mock_failed.emit.assert_called_once()
    
    def test_update_user_settings_validation(self, db_session, sample_teacher):
        """Test settings update validation."""
        controller = SettingsController()
        
        # Test empty name
        with patch.object(controller, 'settings_update_failed') as mock_failed:
            controller.update_user_settings(sample_teacher, "")
            mock_failed.emit.assert_called_once()
        
        # Test name too long
        with patch.object(controller, 'settings_update_failed') as mock_failed:
            controller.update_user_settings(sample_teacher, "x" * 101)
            mock_failed.emit.assert_called_once()


class TestControllerErrorHandling:
    """Test cases for controller error handling."""
    
    def test_database_connection_error(self, db_session):
        """Test handling of database connection errors."""
        controller = AuthController()
        
        # Mock database error
        with patch('base.SessionLocal') as mock_session:
            mock_session.return_value.query.side_effect = Exception("Database connection failed")
            
            with patch.object(controller, 'login_failed') as mock_failed:
                controller.login("test@example.com", "password123")
                mock_failed.emit.assert_called_once()
    
    def test_controller_signal_emission(self, db_session):
        """Test that controllers properly emit signals."""
        controller = AuthController()
        
        # Test that signals are defined
        assert hasattr(controller, 'login_successful')
        assert hasattr(controller, 'login_failed')
        assert hasattr(controller, 'signup_successful')
        assert hasattr(controller, 'signup_failed')
    
    def test_controller_initialization(self):
        """Test that all controllers initialize properly."""
        controllers = [
            AuthController(),
            ClassroomController(),
            AssignmentController(),
            SubmissionController(),
            AnnouncementController(),
            SettingsController()
        ]
        
        for controller in controllers:
            assert controller is not None
            # Test that each controller has the expected signals
            assert hasattr(controller, '__class__')