import enum
import bcrypt
from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum, Index, CheckConstraint
from sqlalchemy.orm import relationship
from classroom import student_classroom_association
from base import Base


class UserRole(enum.Enum):
    student = "student"
    teacher = "teacher"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLAlchemyEnum(UserRole), nullable=False)
    
    # Add indexes for common queries
    __table_args__ = (
        Index('ix_users_email_lower', 'email'),  # Case-insensitive email lookups
        CheckConstraint('length(full_name) <= 100', name='ck_users_full_name_len'),
        CheckConstraint('length(email) <= 255', name='ck_users_email_len'),
        CheckConstraint('length(password_hash) <= 255', name='ck_users_password_hash_len'),
    )

    classes_taught = relationship("Classroom", back_populates="teacher")
    classes_joined = relationship("Classroom", secondary=student_classroom_association, back_populates="students")
    announcements_made = relationship("Announcement", back_populates="author")
    submissions = relationship("Submission", back_populates="student")

    def set_password(self, password: str):
        """Hashes and sets the user's password."""
        pwd_bytes = password.encode('utf-8')
        self.password_hash = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Checks if the provided password matches the stored hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))