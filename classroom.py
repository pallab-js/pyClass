import secrets
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Index, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship

from base import Base


def generate_class_code():
    """Generates a random 10-character alphanumeric code (A-Z, a-z, 0-9)."""
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(secrets.choice(alphabet) for _ in range(10))

# Association Table for the many-to-many relationship between User (student) and Classroom
student_classroom_association = Table(
    "student_classroom", Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("classroom_id", Integer, ForeignKey("classrooms.id"), primary_key=True),
)

class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    section = Column(String(50), nullable=True)
    class_code = Column(String(10), unique=True, default=generate_class_code, nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Add indexes for common queries
    __table_args__ = (
        Index('ix_classrooms_teacher_id', 'teacher_id'),
        Index('ix_classrooms_class_code', 'class_code'),
        CheckConstraint('length(name) <= 100', name='ck_classrooms_name_len'),
        CheckConstraint('length(section) <= 50', name='ck_classrooms_section_len'),
        CheckConstraint('length(class_code) = 10', name='ck_classrooms_class_code_len'),
    )

    teacher = relationship("User", back_populates="classes_taught")
    students = relationship("User", secondary=student_classroom_association, back_populates="classes_joined")
    announcements = relationship("Announcement", backref="classroom", cascade="all, delete-orphan")
    assignments = relationship("Assignment", backref="classroom", cascade="all, delete-orphan")