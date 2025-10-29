from PySide6.QtCore import QObject, Signal, Slot
from sqlalchemy.orm import joinedload

from base import SessionLocal
from assignment import Assignment
from user import User


class AssignmentController(QObject):
    """Handles business logic for assignments."""

    class_assignments_fetched = Signal(list)
    global_assignments_fetched = Signal(list)
    assignment_created = Signal(Assignment)
    assignment_fetched = Signal(Assignment)
    assignment_creation_failed = Signal(str)

    @Slot(int)
    def get_assignments_for_class(self, classroom_id: int):
        """Fetches all assignments for a given class."""
        db = SessionLocal()
        try:
            assignments = (
                db.query(Assignment)
                .filter(Assignment.classroom_id == classroom_id)
                .order_by(Assignment.due_date.desc().nulls_last(), Assignment.id.desc())
                .all()
            )
            self.class_assignments_fetched.emit(assignments)
        finally:
            db.close()

    @Slot(User)
    def get_all_assignments_for_user(self, user: User):
        """Fetches all assignments for a student across all their classes."""
        if user.role.value != 'student':
            self.global_assignments_fetched.emit([]) # Only students have this view
            return

        db = SessionLocal()
        try:
            # Get all class IDs the student is in
            user_in_session = db.merge(user)
            class_ids = [c.id for c in user_in_session.classes_joined]

            assignments = db.query(Assignment).options(joinedload(Assignment.classroom)).filter(
                Assignment.classroom_id.in_(class_ids)
            ).order_by(Assignment.due_date.asc().nulls_last()).all()
            self.global_assignments_fetched.emit(assignments)
        finally:
            db.close()

    @Slot(str, str, object, int, int)
    def create_assignment(self, title: str, instructions: str, due_date, points: int, classroom_id: int):
        """Creates a new assignment."""
        if not title.strip():
            self.assignment_creation_failed.emit("Assignment title cannot be empty.")
            return

        db = SessionLocal()
        try:
            new_assignment = Assignment(
                title=title, instructions=instructions, due_date=due_date, points=points, classroom_id=classroom_id
            )
            db.add(new_assignment)
            db.commit()
            self.assignment_created.emit(new_assignment)
        finally:
            db.close()

    @Slot(int)
    def get_assignment_by_id(self, assignment_id: int):
        """Fetches a single assignment by its ID."""
        db = SessionLocal()
        try:
            assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
            self.assignment_fetched.emit(assignment)
        finally:
            db.close()