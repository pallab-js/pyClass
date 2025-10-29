from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index, CheckConstraint
from sqlalchemy.orm import relationship

from base import Base


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    instructions = Column(String(2000), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    points = Column(Integer, nullable=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False)
    
    # Add constraints and indexes
    __table_args__ = (
        Index('ix_assignments_classroom_id', 'classroom_id'),
        Index('ix_assignments_due_date', 'due_date'),
        CheckConstraint('points >= 0', name='ck_assignments_points_positive'),
        CheckConstraint('points <= 10000', name='ck_assignments_points_max'),
        CheckConstraint('length(title) <= 200', name='ck_assignments_title_len'),
        CheckConstraint('instructions IS NULL OR length(instructions) <= 2000', name='ck_assignments_instructions_len'),
    )

    submissions = relationship("Submission", back_populates="assignment", cascade="all, delete-orphan")