from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel
from PySide6.QtCore import Signal
from stream_view import StreamView
from people_view import PeopleView
from classwork_view import ClassworkView
from view_header import ViewHeader


class ClassWindow(QWidget):
    """The main view for a single class, with tabs for Stream, Classwork, etc."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.header = ViewHeader()
        self.current_classroom = None
        self.current_class_id = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)

        main_layout.addWidget(self.header)

        self.tab_widget = QTabWidget()
        self.tab_widget.setContentsMargins(0, 10, 0, 0)
        self.stream_tab = StreamView()
        self.classwork_tab = ClassworkView()
        self.people_tab = PeopleView()
        self.tab_widget.addTab(self.stream_tab, "Stream")
        self.tab_widget.addTab(self.classwork_tab, "Classwork")
        self.tab_widget.addTab(self.people_tab, "People")

        main_layout.addWidget(self.tab_widget)

    def load_class(self, classroom):
        """Loads the data for a specific class into the view."""
        self.current_classroom = classroom
        self.current_class_id = classroom.id
        self.header.set_title(classroom.name)
        self.stream_tab.display_class_code(classroom.class_code)
        # Clear any previous announcements
        self.classwork_tab.display_assignments([])
        self.people_tab.clear_view()
        self.stream_tab.display_announcements([])