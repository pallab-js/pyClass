from PySide6.QtCore import QObject, Signal, Slot
from base import SessionLocal
from user import User, UserRole


class AuthController(QObject):
    """Handles authentication logic."""

    # Signals to communicate results back to the main application
    login_successful = Signal(User)
    login_failed = Signal(str)
    signup_successful = Signal()
    signup_failed = Signal(str)

    @Slot(str, str)
    def login(self, email: str, password: str):
        """Attempts to log in a user with the given credentials."""
        if not email or not password:
            self.login_failed.emit("Email and password cannot be empty.")
            return

        db_session = SessionLocal()
        try:
            user = db_session.query(User).filter(User.email == email).first()
            if user and user.check_password(password):
                self.login_successful.emit(user)
            else:
                self.login_failed.emit("Invalid email or password.")
        except Exception as e:
            self.login_failed.emit(f"An error occurred: {e}")
        finally:
            db_session.close()

    @Slot(str, str, str, str)
    def signup(self, email: str, password: str, confirm_password: str, role: str):
        """Attempts to register a new user."""
        if not all([email, password, confirm_password, role]):
            self.signup_failed.emit("All fields are required.")
            return
        if password != confirm_password:
            self.signup_failed.emit("Passwords do not match.")
            return
        
        db_session = SessionLocal()
        try:
            # Check if user already exists
            if db_session.query(User).filter(User.email == email).first():
                self.signup_failed.emit("An account with this email already exists.")
                return
            
            new_user = User(
                email=email,
                role=UserRole(role)
            )
            new_user.set_password(password)
            db_session.add(new_user)
            db_session.commit()
            self.signup_successful.emit()
        except Exception as e:
            self.signup_failed.emit(f"An error occurred during signup: {e}")
        finally:
            db_session.close()