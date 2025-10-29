"""
Test cases for database models.
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from user import User, UserRole
from classroom import Classroom, generate_class_code
from assignment import Assignment
from announcement import Announcement
from submission import Submission


class TestUserModel:
    """Test cases for User model."""
    
    def test_user_creation(self, db_session):
        """Test basic user creation."""
        user = User(
            full_name="Test User",
            email="test@example.com",
            role=UserRole.student
        )
        user.set_password("password123")
        
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.full_name == "Test User"
        assert user.email == "test@example.com"
        assert user.role == UserRole.student
        assert user.password_hash is not None
    
    def test_password_hashing(self, db_session):
        """Test password hashing and verification."""
        user = User(
            full_name="Test User",
            email="test@example.com",
            role=UserRole.student
        )
        user.set_password("password123")
        
        assert user.check_password("password123")
        assert not user.check_password("wrongpassword")
        assert not user.check_password("")
    
    def test_user_email_unique(self, db_session):
        """Test that email addresses must be unique."""
        user1 = User(
            full_name="User 1",
            email="test@example.com",
            role=UserRole.student
        )
        user1.set_password("password123")
        
        user2 = User(
            full_name="User 2",
            email="test@example.com",  # Same email
            role=UserRole.teacher
        )
        user2.set_password("password123")
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_string_length_limits(self, db_session):
        """Test string length constraints."""
        # Test full_name length limit
        user = User(
            full_name="x" * 101,  # Exceeds 100 character limit
            email="test@example.com",
            role=UserRole.student
        )
        user.set_password("password123")
        
        db_session.add(user)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_email_required(self, db_session):
        """Test that email is required."""
        user = User(
            full_name="Test User",
            email=None,
            role=UserRole.student
        )
        user.set_password("password123")
        
        db_session.add(user)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestClassroomModel:
    """Test cases for Classroom model."""
    
    def test_classroom_creation(self, db_session, sample_teacher):
        """Test basic classroom creation."""
        classroom = Classroom(
            name="Test Class",
            section="A",
            teacher_id=sample_teacher.id
        )
        
        db_session.add(classroom)
        db_session.commit()
        
        assert classroom.id is not None
        assert classroom.name == "Test Class"
        assert classroom.section == "A"
        assert classroom.teacher_id == sample_teacher.id
        assert classroom.class_code is not None
        assert len(classroom.class_code) == 10
    
    def test_class_code_generation(self):
        """Test class code generation."""
        code1 = generate_class_code()
        code2 = generate_class_code()
        
        assert len(code1) == 10
        assert len(code2) == 10
        assert code1 != code2  # Should be unique
        assert code1.isalnum()  # Should be alphanumeric
    
    def test_classroom_name_required(self, db_session, sample_teacher):
        """Test that classroom name is required."""
        classroom = Classroom(
            name=None,
            section="A",
            teacher_id=sample_teacher.id
        )
        
        db_session.add(classroom)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_classroom_string_length_limits(self, db_session, sample_teacher):
        """Test string length constraints."""
        # Test name length limit
        classroom = Classroom(
            name="x" * 101,  # Exceeds 100 character limit
            section="A",
            teacher_id=sample_teacher.id
        )
        
        db_session.add(classroom)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_classroom_teacher_relationship(self, db_session, sample_teacher):
        """Test classroom-teacher relationship."""
        classroom = Classroom(
            name="Test Class",
            section="A",
            teacher_id=sample_teacher.id
        )
        
        db_session.add(classroom)
        db_session.commit()
        
        assert classroom.teacher == sample_teacher
        assert classroom in sample_teacher.classes_taught


class TestAssignmentModel:
    """Test cases for Assignment model."""
    
    def test_assignment_creation(self, db_session, sample_classroom):
        """Test basic assignment creation."""
        due_date = datetime.now() + timedelta(days=7)
        assignment = Assignment(
            title="Test Assignment",
            instructions="Complete this assignment",
            due_date=due_date,
            points=100,
            classroom_id=sample_classroom.id
        )
        
        db_session.add(assignment)
        db_session.commit()
        
        assert assignment.id is not None
        assert assignment.title == "Test Assignment"
        assert assignment.instructions == "Complete this assignment"
        assert assignment.due_date == due_date
        assert assignment.points == 100
        assert assignment.classroom_id == sample_classroom.id
    
    def test_assignment_title_required(self, db_session, sample_classroom):
        """Test that assignment title is required."""
        assignment = Assignment(
            title=None,
            instructions="Complete this assignment",
            classroom_id=sample_classroom.id
        )
        
        db_session.add(assignment)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_assignment_points_constraints(self, db_session, sample_classroom):
        """Test points constraints."""
        # Test negative points
        assignment = Assignment(
            title="Test Assignment",
            points=-1,
            classroom_id=sample_classroom.id
        )
        
        db_session.add(assignment)
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()
        
        # Test points too high
        assignment = Assignment(
            title="Test Assignment",
            points=10001,
            classroom_id=sample_classroom.id
        )
        
        db_session.add(assignment)
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()
    
    def test_assignment_string_length_limits(self, db_session, sample_classroom):
        """Test string length constraints."""
        # Test title length limit
        assignment = Assignment(
            title="x" * 201,  # Exceeds 200 character limit
            classroom_id=sample_classroom.id
        )
        
        db_session.add(assignment)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestAnnouncementModel:
    """Test cases for Announcement model."""
    
    def test_announcement_creation(self, db_session, sample_classroom, sample_teacher):
        """Test basic announcement creation."""
        announcement = Announcement(
            content="Welcome to the class!",
            classroom_id=sample_classroom.id,
            author_id=sample_teacher.id
        )
        
        db_session.add(announcement)
        db_session.commit()
        
        assert announcement.id is not None
        assert announcement.content == "Welcome to the class!"
        assert announcement.classroom_id == sample_classroom.id
        assert announcement.author_id == sample_teacher.id
        assert announcement.timestamp is not None
    
    def test_announcement_content_required(self, db_session, sample_classroom, sample_teacher):
        """Test that announcement content is required."""
        announcement = Announcement(
            content=None,
            classroom_id=sample_classroom.id,
            author_id=sample_teacher.id
        )
        
        db_session.add(announcement)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_announcement_string_length_limits(self, db_session, sample_classroom, sample_teacher):
        """Test string length constraints."""
        announcement = Announcement(
            content="x" * 2001,  # Exceeds 2000 character limit
            classroom_id=sample_classroom.id,
            author_id=sample_teacher.id
        )
        
        db_session.add(announcement)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestSubmissionModel:
    """Test cases for Submission model."""
    
    def test_submission_creation(self, db_session, sample_assignment, sample_student):
        """Test basic submission creation."""
        submission = Submission(
            content="My submission content",
            assignment_id=sample_assignment.id,
            student_id=sample_student.id,
            grade=85.5
        )
        
        db_session.add(submission)
        db_session.commit()
        
        assert submission.id is not None
        assert submission.content == "My submission content"
        assert submission.assignment_id == sample_assignment.id
        assert submission.student_id == sample_student.id
        assert submission.grade == 85.5
        assert submission.timestamp is not None
    
    def test_submission_unique_constraint(self, db_session, sample_assignment, sample_student):
        """Test that one submission per student per assignment is allowed."""
        submission1 = Submission(
            content="First submission",
            assignment_id=sample_assignment.id,
            student_id=sample_student.id
        )
        
        submission2 = Submission(
            content="Second submission",
            assignment_id=sample_assignment.id,
            student_id=sample_student.id
        )
        
        db_session.add(submission1)
        db_session.commit()
        
        db_session.add(submission2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_submission_grade_constraints(self, db_session, sample_assignment, sample_student):
        """Test grade constraints."""
        # Test negative grade
        submission = Submission(
            content="My submission",
            assignment_id=sample_assignment.id,
            student_id=sample_student.id,
            grade=-1.0
        )
        
        db_session.add(submission)
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()
        
        # Test grade too high
        submission = Submission(
            content="My submission",
            assignment_id=sample_assignment.id,
            student_id=sample_student.id,
            grade=10001.0
        )
        
        db_session.add(submission)
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()
    
    def test_submission_string_length_limits(self, db_session, sample_assignment, sample_student):
        """Test string length constraints."""
        submission = Submission(
            content="x" * 5001,  # Exceeds 5000 character limit
            assignment_id=sample_assignment.id,
            student_id=sample_student.id
        )
        
        db_session.add(submission)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestModelRelationships:
    """Test cases for model relationships."""
    
    def test_user_classroom_relationships(self, db_session, sample_teacher, sample_student, sample_classroom):
        """Test user-classroom relationships."""
        # Add student to classroom
        sample_classroom.students.append(sample_student)
        db_session.commit()
        
        # Test teacher relationships
        assert sample_classroom in sample_teacher.classes_taught
        assert sample_classroom.teacher == sample_teacher
        
        # Test student relationships
        assert sample_classroom in sample_student.classes_joined
        assert sample_student in sample_classroom.students
    
    def test_classroom_assignment_relationship(self, db_session, sample_classroom, sample_assignment):
        """Test classroom-assignment relationship."""
        assert sample_assignment in sample_classroom.assignments
        assert sample_assignment.classroom == sample_classroom
    
    def test_classroom_announcement_relationship(self, db_session, sample_classroom, sample_announcement):
        """Test classroom-announcement relationship."""
        assert sample_announcement in sample_classroom.announcements
        assert sample_announcement.classroom == sample_classroom
    
    def test_assignment_submission_relationship(self, db_session, sample_assignment, sample_submission):
        """Test assignment-submission relationship."""
        assert sample_submission in sample_assignment.submissions
        assert sample_submission.assignment == sample_assignment
    
    def test_user_submission_relationship(self, db_session, sample_student, sample_submission):
        """Test user-submission relationship."""
        assert sample_submission in sample_student.submissions
        assert sample_submission.student == sample_student