from PySide6.QtCore import QObject, Signal, Slot
from sqlalchemy.orm import joinedload

from base import SessionLocal
from submission import Submission
from user import User


class SubmissionController(QObject):
    """Handles business logic for student submissions."""

    submission_fetched = Signal(object)  # Emits Submission object or None
    submission_updated = Signal(object)
    all_submissions_fetched = Signal(list)
    submission_failed = Signal(str)

    @Slot(int, int)
    def get_submission(self, assignment_id: int, student_id: int):
        """Fetches a student's submission for a specific assignment."""
        db = SessionLocal()
        try:
            submission = (
                db.query(Submission)
                .filter_by(assignment_id=assignment_id, student_id=student_id)
                .first()
            )
            self.submission_fetched.emit(submission)
        finally:
            db.close()

    @Slot(int)
    def get_all_submissions_for_assignment(self, assignment_id: int):
        """Fetches all submissions for a given assignment."""
        db = SessionLocal()
        try:
            submissions = (
                db.query(Submission)
                .options(joinedload(Submission.student))
                .filter_by(assignment_id=assignment_id)
                .all()
            )
            self.all_submissions_fetched.emit(submissions)
        finally:
            db.close()

    @Slot(int, User, str)
    def create_or_update_submission(self, assignment_id: int, student: User, content: str):
        """Creates a new submission or updates an existing one."""
        db = SessionLocal()
        try:
            submission = db.query(Submission).filter_by(assignment_id=assignment_id, student_id=student.id).first()
            if not submission:
                submission = Submission(assignment_id=assignment_id, student_id=student.id)
                db.add(submission)

            submission.content = content
            db.commit()
            db.refresh(submission)
            self.submission_updated.emit(submission)
        except Exception as e:
            self.submission_failed.emit(f"Failed to update submission: {e}")
        finally:
            db.close()

    @Slot(int, float)
    def grade_submission(self, submission_id: int, grade: float):
        """Updates the grade for a specific submission."""
        db = SessionLocal()
        try:
            submission = db.query(Submission).filter_by(id=submission_id).first()
            if submission:
                submission.grade = grade
                db.commit()
                # We can re-emit the updated signal, or a new one if needed
                self.submission_updated.emit(submission)
        except Exception as e:
            self.submission_failed.emit(f"Failed to grade submission: {e}")
        finally:
            db.close()