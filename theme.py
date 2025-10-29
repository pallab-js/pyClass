from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QTextStream


class ThemeManager:
    """Manages loading and applying application-wide stylesheets."""

    def __init__(self, app: QApplication):
        self.app = app
        self.themes = {
            "light": self._load_stylesheet("light.qss"),
            "dark": self._load_stylesheet("dark.qss"),
        }
        self.current_theme = "dark"
        self.apply_theme(self.current_theme)

    def _load_stylesheet(self, filename: str) -> str:
        """Loads a QSS file from the assets/styles directory."""
        style_file_path = Path(__file__).parent / filename
        style_file = QFile(str(style_file_path))
        if not style_file.open(QFile.ReadOnly | QFile.Text):
            print(f"Error: Could not open stylesheet {filename}")
            return ""
        return QTextStream(style_file).readAll()

    def apply_theme(self, theme_name: str):
        """Applies a named theme to the application."""
        if theme_name in self.themes:
            self.app.setStyleSheet(self.themes[theme_name])
            self.current_theme = theme_name