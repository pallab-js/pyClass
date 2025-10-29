from PySide6.QtCore import QObject, Signal, Slot
from sqlalchemy.orm import joinedload

from base import SessionLocal
from announcement import Announcement
from user import User


class AnnouncementController(QObject):
    """Handles business logic for announcements."""

    announcements_fetched = Signal(list)
    announcement_created = Signal(Announcement)
    announcement_creation_failed = Signal(str)

    @Slot(int)
    def get_announcements_for_class(self, classroom_id: int):
        """Fetches all announcements for a given class, ordered by time."""
        db = SessionLocal()
        try:
            announcements = (
                db.query(Announcement)
                .options(joinedload(Announcement.author))
                .filter(Announcement.classroom_id == classroom_id)
                .order_by(Announcement.timestamp.desc())
                .all()
            )
            self.announcements_fetched.emit(announcements)
        finally:
            db.close()

    @Slot(str, int, User)
    def create_announcement(self, content: str, classroom_id: int, author: User):
        """Creates a new announcement."""
        if not content.strip():
            self.announcement_creation_failed.emit("Announcement cannot be empty.")
            return

        db = SessionLocal()
        try:
            new_announcement = Announcement(content=content, classroom_id=classroom_id, author_id=author.id)
            db.add(new_announcement)
            db.commit()
            db.refresh(new_announcement, ["author"]) # Eagerly load author
            self.announcement_created.emit(new_announcement)
        finally:
            db.close()