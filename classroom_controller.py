from PySide6.QtCore import QObject, Signal, Slot
from sqlalchemy.orm import joinedload
from base import SessionLocal
from classroom import Classroom
from user import User, UserRole
from classroom import student_classroom_association


class ClassroomController(QObject):
    """Handles business logic for classrooms."""

    class_created = Signal(Classroom)
    class_creation_failed = Signal(str)
    class_joined = Signal(Classroom)
    join_class_failed = Signal(str)
    class_fetched = Signal(Classroom)
    classes_fetched = Signal(list)

    @Slot(str, str, User)
    def create_class(self, name: str, section: str, teacher: User):
        """Creates a new classroom."""
        if not name:
            self.class_creation_failed.emit("Class name cannot be empty.")
            return

        db_session = SessionLocal()
        try:
            new_class = Classroom(
                name=name,
                section=section,
                teacher_id=teacher.id
            )
            db_session.add(new_class)
            db_session.commit()
            # Refresh to get DB-generated values and eager load the teacher relationship
            db_session.refresh(new_class, ["teacher"])
            self.class_created.emit(new_class)
        finally:
            db_session.close()

    @Slot(str, User)
    def join_class(self, class_code: str, student: User):
        """Adds a student to a classroom using a class code."""
        if not class_code:
            self.join_class_failed.emit("Class code cannot be empty.")
            return

        db_session = SessionLocal()
        try:
            classroom = db_session.query(Classroom).filter(Classroom.class_code == class_code).first()
            if not classroom:
                self.join_class_failed.emit("Invalid class code.")
                return

            # Re-attach student to this session to avoid DetachedInstanceError
            student_in_session = db_session.merge(student)
            if student_in_session in classroom.students:
                self.join_class_failed.emit("You are already in this class.")
                return

            classroom.students.append(student_in_session)
            db_session.commit()
            self.class_joined.emit(classroom)
        finally:
            db_session.close()

    @Slot(User)
    def get_classes_for_user(self, user: User):
        """Fetches all classrooms a user is associated with."""
        db_session = SessionLocal()
        try:
            # Re-attach user to this session to avoid DetachedInstanceError
            user_in_session = db_session.merge(user)

            if user_in_session.role == UserRole.teacher:
                # Eagerly load the teacher relationship for all classes taught by this user
                classes = db_session.query(Classroom).options(joinedload(Classroom.teacher)).filter(Classroom.teacher_id == user_in_session.id).all()
            else: # student
                # For students, construct a query to eager load the teacher for each class
                # to avoid the N+1 query problem when displaying class cards.
                classes = (
                    db_session.query(Classroom)
                    .options(joinedload(Classroom.teacher))
                    .join(student_classroom_association)
                    .filter(student_classroom_association.c.user_id == user_in_session.id)
                ).all()

            self.classes_fetched.emit(list(classes))
        finally:
            db_session.close()

    @Slot(int)
    def get_class_by_id(self, classroom_id: int):
        """Fetches a single classroom by its ID, eagerly loading teacher and students."""
        db = SessionLocal()
        try:
            classroom = (
                db.query(Classroom)
                .options(joinedload(Classroom.teacher), joinedload(Classroom.students))
                .filter(Classroom.id == classroom_id).first()
            )
            self.class_fetched.emit(classroom)
        finally:
            db.close()