# Automation activity 02: project task workflow

The Flask application writes a project and its task to the local SQLite
database. The project detail page lists its tasks, and the task page can update
the task title, status, and optional due date.

The automated test
`test_database_survives_application_process_restart` creates a project and
task through the Flask test client in one Python process, then reads them
through the application in a second process using the same database file. This
checks that the SQLite data persists after the first process exits. The test
uses a temporary database and synthetic names; it does not connect to an
external service.
