"""
Integration tests for end-to-end scenarios.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from main import MainWindow, setup_database
from auth_controller import AuthController
from classroom_controller import ClassroomController
from assignment_controller import AssignmentController
from submission_controller import SubmissionController
from announcement_controller import AnnouncementController
from user import User, UserRole
from classroom import Classroom
from assignment import Assignment
from submission import Submission
from announcement import Announcement


class TestAuthenticationFlow:
    """Test complete authentication flow."""
    
    def test_teacher_signup_and_login(self, db_session, qtbot):
        """Test teacher signup and login flow."""
        # Test signup
        auth_controller = AuthController()
        
        with patch.object(auth_controller, 'signup_successful') as mock_signup_success:
            auth_controller.signup("teacher@example.com", "password123", "password123", UserRole.teacher.value)
            mock_signup_success.emit.assert_called_once()
        
        # Test login
        with patch.object(auth_controller, 'login_successful') as mock_login_success:
            auth_controller.login("teacher@example.com", "password123")
            mock_login_success.emit.assert_called_once()
    
    def test_student_signup_and_login(self, db_session, qtbot):
        """Test student signup and login flow."""
        # Test signup
        auth_controller = AuthController()
        
        with patch.object(auth_controller, 'signup_successful') as mock_signup_success:
            auth_controller.signup("student@example.com", "password123", "password123", UserRole.student.value)
            mock_signup_success.emit.assert_called_once()
        
        # Test login
        with patch.object(auth_controller, 'login_successful') as mock_login_success:
            auth_controller.login("student@example.com", "password123")
            mock_login_success.emit.assert_called_once()


class TestClassroomManagementFlow:
    """Test complete classroom management flow."""
    
    def test_teacher_creates_classroom_and_student_joins(self, db_session, qtbot):
        """Test teacher creates classroom and student joins."""
        # Create teacher and student
        auth_controller = AuthController()
        
        # Teacher signup
        with patch.object(auth_controller, 'signup_successful'):
            auth_controller.signup("teacher@example.com", "password123", "password123", UserRole.teacher.value)
        
        # Student signup
        with patch.object(auth_controller, 'signup_successful'):
            auth_controller.signup("student@example.com", "password123", "password123", UserRole.student.value)
        
        # Get users
        teacher = db_session.query(User).filter_by(email="teacher@example.com").first()
        student = db_session.query(User).filter_by(email="student@example.com").first()
        
        # Teacher creates classroom
        classroom_controller = ClassroomController()
        
        with patch.object(classroom_controller, 'class_created') as mock_created:
            classroom_controller.create_class("Test Class", "A", teacher)
            mock_created.emit.assert_called_once()
        
        # Get created classroom
        classroom = db_session.query(Classroom).filter_by(teacher_id=teacher.id).first()
        
        # Student joins classroom
        with patch.object(classroom_controller, 'class_joined') as mock_joined:
            classroom_controller.join_class(classroom.class_code, student)
            mock_joined.emit.assert_called_once()
        
        # Verify student is in classroom
        db_session.refresh(classroom)
        assert any(s.id == student.id for s in classroom.students)


class TestAssignmentFlow:
    """Test complete assignment flow."""
    
    def test_teacher_creates_assignment_and_student_submits(self, db_session, qtbot):
        """Test teacher creates assignment and student submits."""
        # Setup: Create teacher, student, and classroom
        auth_controller = AuthController()
        classroom_controller = ClassroomController()
        
        # Create users
        with patch.object(auth_controller, 'signup_successful'):
            auth_controller.signup("teacher@example.com", "password123", "password123", UserRole.teacher.value)
            auth_controller.signup("student@example.com", "password123", "password123", UserRole.student.value)
        
        teacher = db_session.query(User).filter_by(email="teacher@example.com").first()
        student = db_session.query(User).filter_by(email="student@example.com").first()
        
        # Create classroom
        with patch.object(classroom_controller, 'class_created'):
            classroom_controller.create_class("Test Class", "A", teacher)
        
        classroom = db_session.query(Classroom).filter_by(teacher_id=teacher.id).first()
        
        # Add student to classroom
        classroom.students.append(student)
        db_session.commit()
        
        # Teacher creates assignment
        assignment_controller = AssignmentController()
        
        with patch.object(assignment_controller, 'assignment_created') as mock_created:
            assignment_controller.create_assignment(
                "Test Assignment",
                "Complete this assignment",
                datetime.now() + timedelta(days=7),
                100,
                classroom.id
            )
            mock_created.emit.assert_called_once()
        
        # Get created assignment
        assignment = db_session.query(Assignment).filter_by(classroom_id=classroom.id).first()
        
        # Student submits assignment
        submission_controller = SubmissionController()
        
        with patch.object(submission_controller, 'submission_updated') as mock_updated:
            submission_controller.create_or_update_submission(
                assignment.id,
                student,
                "My submission content",
            )
            mock_updated.emit.assert_called_once()
        
        # Verify submission exists
        submission = db_session.query(Submission).filter_by(assignment_id=assignment.id, student_id=student.id).first()
        assert submission is not None
        assert submission.content == "My submission content"


class TestGradingFlow:
    """Test complete grading flow."""
    
    def test_teacher_grades_student_submission(self, db_session, qtbot):
        """Test teacher grades student submission."""
        # Setup: Create complete scenario
        auth_controller = AuthController()
        classroom_controller = ClassroomController()
        assignment_controller = AssignmentController()
        submission_controller = SubmissionController()
        
        # Create users and classroom
        with patch.object(auth_controller, 'signup_successful'):
            auth_controller.signup("teacher@example.com", "password123", "password123", UserRole.teacher.value)
            auth_controller.signup("student@example.com", "password123", "password123", UserRole.student.value)
        
        teacher = db_session.query(User).filter_by(email="teacher@example.com").first()
        student = db_session.query(User).filter_by(email="student@example.com").first()
        
        # Create classroom and add student
        with patch.object(classroom_controller, 'class_created'):
            classroom_controller.create_class("Test Class", "A", teacher)
        
        classroom = db_session.query(Classroom).filter_by(teacher_id=teacher.id).first()
        classroom.students.append(student)
        db_session.commit()
        
        # Create assignment
        with patch.object(assignment_controller, 'assignment_created'):
            assignment_controller.create_assignment(
                "Test Assignment",
                "Complete this assignment",
                datetime.now() + timedelta(days=7),
                100,
                classroom.id
            )
        
        assignment = db_session.query(Assignment).filter_by(classroom_id=classroom.id).first()
        
        # Student submits
        with patch.object(submission_controller, 'submission_updated'):
            submission_controller.create_or_update_submission(
                assignment.id,
                student,
                "My submission content",
            )
        
        submission = db_session.query(Submission).filter_by(assignment_id=assignment.id).first()
        
        # Teacher grades submission
        with patch.object(submission_controller, 'submission_updated') as mock_graded:
            submission_controller.grade_submission(submission.id, 85.5)
            mock_graded.emit.assert_called_once()
        
        # Verify grade was set
        db_session.refresh(submission)
        assert submission.grade == 85.5


class TestAnnouncementFlow:
    """Test complete announcement flow."""
    
    def test_teacher_creates_announcement(self, db_session, qtbot):
        """Test teacher creates announcement."""
        # Setup
        auth_controller = AuthController()
        classroom_controller = ClassroomController()
        announcement_controller = AnnouncementController()
        
        # Create teacher and classroom
        with patch.object(auth_controller, 'signup_successful'):
            auth_controller.signup("teacher@example.com", "password123", "password123", UserRole.teacher.value)
        
        teacher = db_session.query(User).filter_by(email="teacher@example.com").first()
        
        with patch.object(classroom_controller, 'class_created'):
            classroom_controller.create_class("Test Class", "A", teacher)
        
        classroom = db_session.query(Classroom).filter_by(teacher_id=teacher.id).first()
        
        # Teacher creates announcement
        with patch.object(announcement_controller, 'announcement_created') as mock_created:
            announcement_controller.create_announcement(
                "Welcome to the class!",
                classroom.id,
                teacher
            )
            mock_created.emit.assert_called_once()
        
        # Verify announcement exists
        announcement = db_session.query(Announcement).filter_by(classroom_id=classroom.id).first()
        assert announcement is not None
        assert announcement.content == "Welcome to the class!"
        assert announcement.author_id == teacher.id


class TestErrorHandling:
    """Test error handling in integration scenarios."""
    
    def test_database_error_handling(self, db_session, qtbot):
        """Test handling of database errors."""
        auth_controller = AuthController()
        
        # Mock database error
        with patch('base.SessionLocal') as mock_session:
            mock_session.return_value.query.side_effect = Exception("Database connection failed")
            
            with patch.object(auth_controller, 'login_failed') as mock_failed:
                auth_controller.login("test@example.com", "password123")
                mock_failed.emit.assert_called_once()
    
    def test_invalid_data_handling(self, db_session, qtbot):
        """Test handling of invalid data."""
        auth_controller = AuthController()
        
        # Test signup with invalid email
        with patch.object(auth_controller, 'signup_failed') as mock_failed:
            auth_controller.signup("", "password123", "password123", UserRole.teacher.value)
            mock_failed.emit.assert_called_once()
        
        # Test signup with empty password
        with patch.object(auth_controller, 'signup_failed') as mock_failed:
            auth_controller.signup("teacher@example.com", "", "", UserRole.teacher.value)
            mock_failed.emit.assert_called_once()


class TestMainWindowIntegration:
    """Test MainWindow integration."""
    
    def test_main_window_initialization(self, qtbot):
        """Test MainWindow initializes properly."""
        with patch('main.setup_database'):
            window = MainWindow()
            qtbot.addWidget(window)
            
            assert window is not None
            assert hasattr(window, 'auth_controller')
            assert hasattr(window, 'classroom_controller')
            assert hasattr(window, 'assignment_controller')
            assert hasattr(window, 'submission_controller')
            assert hasattr(window, 'announcement_controller')
    
    def test_controller_signal_connections(self, qtbot):
        """Test that controllers are properly connected."""
        with patch('main.setup_database'):
            window = MainWindow()
            qtbot.addWidget(window)
            
            # Test that controllers have required signals (by names actually present)
            assert hasattr(window.auth_controller, 'login_successful')
            assert hasattr(window.classroom_controller, 'class_created')
            assert hasattr(window.assignment_controller, 'assignment_created')
            assert hasattr(window.submission_controller, 'submission_updated')
            assert hasattr(window.announcement_controller, 'announcement_created')


class TestDataConsistency:
    """Test data consistency across operations."""
    
    def test_cascade_deletions(self, db_session, qtbot):
        """Test that cascade deletions work properly."""
        # Create complete scenario
        auth_controller = AuthController()
        classroom_controller = ClassroomController()
        assignment_controller = AssignmentController()
        submission_controller = SubmissionController()
        announcement_controller = AnnouncementController()
        
        # Create teacher and student
        with patch.object(auth_controller, 'signup_successful'):
            auth_controller.signup("teacher@example.com", "password123", "password123", UserRole.teacher.value)
            auth_controller.signup("student@example.com", "password123", "password123", UserRole.student.value)
        
        teacher = db_session.query(User).filter_by(email="teacher@example.com").first()
        student = db_session.query(User).filter_by(email="student@example.com").first()
        
        # Create classroom
        with patch.object(classroom_controller, 'class_created'):
            classroom_controller.create_class("Test Class", "A", teacher)
        
        classroom = db_session.query(Classroom).filter_by(teacher_id=teacher.id).first()
        
        # Add student to classroom
        classroom.students.append(student)
        db_session.commit()
        
        # Create assignment and submission
        with patch.object(assignment_controller, 'assignment_created'):
            assignment_controller.create_assignment("Test Assignment", "Instructions", None, 100, classroom.id)
        
        assignment = db_session.query(Assignment).filter_by(classroom_id=classroom.id).first()
        
        with patch.object(submission_controller, 'submission_updated'):
            submission_controller.create_or_update_submission(assignment.id, student, "Submission")
        
        # Create announcement
        with patch.object(announcement_controller, 'announcement_created'):
            announcement_controller.create_announcement("Announcement", classroom.id, teacher)
        
        # Verify all data exists
        assert db_session.query(Classroom).count() == 1
        assert db_session.query(Assignment).count() == 1
        assert db_session.query(Submission).count() == 1
        assert db_session.query(Announcement).count() == 1
        
        # Delete classroom (should cascade)
        db_session.delete(classroom)
        db_session.commit()
        
        # Verify cascade deletions
        assert db_session.query(Classroom).count() == 0
        assert db_session.query(Assignment).count() == 0
        assert db_session.query(Submission).count() == 0
        assert db_session.query(Announcement).count() == 0