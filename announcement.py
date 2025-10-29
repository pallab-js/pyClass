from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from base import Base


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(2000), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Add indexes for common queries
    __table_args__ = (
        Index('ix_announcements_classroom_id', 'classroom_id'),
        Index('ix_announcements_timestamp', 'timestamp'),
        Index('ix_announcements_author_id', 'author_id'),
        CheckConstraint('length(content) <= 2000', name='ck_announcements_content_len'),
    )

    author = relationship("User", back_populates="announcements_made")