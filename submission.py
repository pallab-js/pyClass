from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Index, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from base import Base


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(5000), nullable=True)  # Path to file or text content
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    grade = Column(Float, nullable=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Add constraints and indexes
    __table_args__ = (
        Index('ix_submissions_assignment_id', 'assignment_id'),
        Index('ix_submissions_student_id', 'student_id'),
        Index('ix_submissions_timestamp', 'timestamp'),
        UniqueConstraint('assignment_id', 'student_id', name='uq_submission_student_assignment'),
        CheckConstraint('grade >= 0', name='ck_submissions_grade_positive'),
        CheckConstraint('grade <= 10000', name='ck_submissions_grade_max'),
        CheckConstraint('content IS NULL OR length(content) <= 5000', name='ck_submissions_content_len'),
    )

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", back_populates="submissions")