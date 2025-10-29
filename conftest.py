"""
Pytest configuration and fixtures for the classroom clone application.
"""
import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from base import Base, SessionLocal
from user import User, UserRole
from classroom import Classroom
from assignment import Assignment
from announcement import Announcement
from submission import Submission


@pytest.fixture(scope="session")
def app():
    """Create QApplication for testing."""
    if not QApplication.instance():
        app = QApplication([])
        yield app
        app.quit()
    else:
        yield QApplication.instance()


@pytest.fixture(scope="function")
def db_session():
    """Create a temporary database session for each test."""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Create engine and session
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal.configure(bind=engine)
    
    session = SessionLocal()
    yield session
    
    # Cleanup
    try:
        session.rollback()
    except:
        pass
    session.close()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def sample_teacher(db_session):
    """Create a sample teacher user."""
    teacher = User(
        full_name="John Teacher",
        email="teacher@example.com",
        role=UserRole.teacher
    )
    teacher.set_password("password123")
    db_session.add(teacher)
    db_session.commit()
    return teacher


@pytest.fixture
def sample_student(db_session):
    """Create a sample student user."""
    student = User(
        full_name="Jane Student",
        email="student@example.com",
        role=UserRole.student
    )
    student.set_password("password123")
    db_session.add(student)
    db_session.commit()
    return student


@pytest.fixture
def sample_classroom(db_session, sample_teacher):
    """Create a sample classroom."""
    classroom = Classroom(
        name="Test Class",
        section="A",
        teacher_id=sample_teacher.id
    )
    db_session.add(classroom)
    db_session.commit()
    return classroom


@pytest.fixture
def sample_assignment(db_session, sample_classroom):
    """Create a sample assignment."""
    from datetime import datetime, timedelta
    assignment = Assignment(
        title="Test Assignment",
        instructions="Complete this test assignment",
        due_date=datetime.now() + timedelta(days=7),
        points=100,
        classroom_id=sample_classroom.id
    )
    db_session.add(assignment)
    db_session.commit()
    return assignment


@pytest.fixture
def sample_announcement(db_session, sample_classroom, sample_teacher):
    """Create a sample announcement."""
    announcement = Announcement(
        content="Welcome to the class!",
        classroom_id=sample_classroom.id,
        author_id=sample_teacher.id
    )
    db_session.add(announcement)
    db_session.commit()
    return announcement


@pytest.fixture
def sample_submission(db_session, sample_assignment, sample_student):
    """Create a sample submission."""
    submission = Submission(
        content="My test submission",
        assignment_id=sample_assignment.id,
        student_id=sample_student.id,
        grade=85.5
    )
    db_session.add(submission)
    db_session.commit()
    return submission


@pytest.fixture
def qt_app(app):
    """Ensure we have a QApplication instance (used by pytest-qt's qtbot)."""
    return app


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "ui: mark test as a UI test"
    )