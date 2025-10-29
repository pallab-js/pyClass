from PySide6.QtCore import QObject, Signal, Slot

from base import SessionLocal
from user import User


class SettingsController(QObject):
    """Handles business logic for user settings."""

    settings_updated = Signal(User)
    settings_update_failed = Signal(str)

    @Slot(User, str)
    def update_user_settings(self, user: User, full_name: str):
        """Updates the user's profile information."""
        # Basic validation
        if not full_name or not full_name.strip():
            self.settings_update_failed.emit("Full name cannot be empty.")
            return
        if len(full_name) > 100:
            self.settings_update_failed.emit("Full name must be 100 characters or less.")
            return

        db = SessionLocal()
        try:
            user_to_update = db.query(User).filter(User.id == user.id).first()
            if not user_to_update:
                self.settings_update_failed.emit("User not found.")
                return

            user_to_update.full_name = full_name
            db.commit()
            db.refresh(user_to_update)
            self.settings_updated.emit(user_to_update)
        except Exception as e:
            self.settings_update_failed.emit(f"Failed to update settings: {e}")
        finally:
            db.close()