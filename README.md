# pyClass

A lightweight, desktop classroom manager built with Python and PySide6 (Qt). It provides basic Google Classroom-like workflows for managing classes, classwork, announcements, people, and submissions, backed by a simple SQLite database.

## Features
- Class and people management
- Announcements and stream view
- Classwork and assignments with submissions
- Basic grading panel
- Light/Dark theme via QSS
- Test suite with `pytest`

## Requirements
- Python 3.9+
- macOS, Linux or Windows

See `requirements.txt` for runtime dependencies and `test_requirements.txt` for test-only dependencies.

## Quick start
```bash
# 1) Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate

# 2) Install dependencies
pip install -U pip
pip install -r requirements.txt

# 3) Run the app
python main.py
```

## Running tests
```bash
# In your virtual environment
pip install -r test_requirements.txt
pytest -q
```

## Project layout (high level)
- `main.py`: App entry point
- `*_controller.py`: Controllers for UI flows
- `*.py`: Models and views (PySide6 widgets/windows)
- `tests/`: Unit and integration tests
- `requirements.txt`: App dependencies
- `pytest.ini`: Pytest config
- `Makefile`: Common dev tasks (if any)

## Local database
By default, development uses a local SQLite file (`classroom_clone.db`). This file is ignored in git to avoid committing local data. If you need seed data, create it at runtime or provide fixtures.

## Contributing
- Follow PEP8 style where reasonable
- Prefer clear, descriptive names over abbreviations
- Keep UI responsive and avoid blocking the event loop
- Add/maintain tests for new functionality

## License
This project is licensed under the MIT License. See `LICENSE` for details.
