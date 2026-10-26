# Task Management Application (Week Three)

Atlantic Environmental Research Unit — a small Flask application that replaces a shared spreadsheet for tracking environmental research tasks.

Built for CCT College Dublin, Certificate in Low-Code, No-Code & AI-Assisted Application Development, Session 03.

## What it does

Users can list tasks, create a task, view a task's details, and change a task's status, all through ordinary web pages.

### Main features

- Task list showing the newest tasks first, with an empty state when there are none.
- New-task form with a required title (max 200 characters), an optional description, and an optional due date.
- Clear validation messages; the entered values are kept when the form is shown again with an error.
- Task detail page with title, description, status, creation timestamp (UTC) and due date.
- Status updates limited to `todo`, `in_progress` and `done`.
- Friendly error pages (for example, HTTP 404 for a task that does not exist).

### Limitations

- No login or user accounts; anyone who can reach the app can use it.
- Tasks cannot be edited (other than status) or deleted.
- No search, filtering, pagination or API.
- Intended for local use only (it runs Flask's built-in development server).

## Prerequisites

- Python 3.11 or newer
- `pip` (included with Python)
- Git, with the existing course repository already cloned

## Open the Week Three directory

From the existing repository, change into the `Week Three` folder. The name contains a space, so keep the quotes:

```bash
cd path/to/your-existing-repository
cd "Week Three"
```

Replace `path/to/your-existing-repository` with the location of your own clone. All commands below are run from inside `Week Three`.

## Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**

```bat
py -m venv .venv
.venv\Scripts\activate.bat
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Run the application locally

**Windows (PowerShell):**

```powershell
$env:PORT = "5010"
python app.py
```

**macOS / Linux:**

```bash
PORT=5010 python app.py
```

The application listens on `127.0.0.1` and creates `tasks.db` at startup if it
does not already exist. Open <http://127.0.0.1:5010/> when using the commands
above. Press `Ctrl+C` in the terminal to stop the server.

To use Flask's default port, run `python app.py` without setting `PORT`, then
open <http://127.0.0.1:5000/>.

## Run the automated tests

```bash
python -m pytest
```

Each test uses its own temporary SQLite database, so running the tests never touches your local `tasks.db`.

## Database location and configuration

- Default location: `tasks.db` inside the `Week Three` folder, next to `app.py`. The path is built from the location of `app.py`, so it does not depend on the folder your terminal is in.
- The path is read from `app.config["DATABASE"]`. To use a different file, set that value before the database is initialised, for example in a test or in your own script:

  ```python
  import app as app_module

  app_module.app.config["DATABASE"] = "/path/to/other.db"
  app_module.init_db()
  ```

- `tasks.db` is listed in `.gitignore` and is not committed.
- Importing `app.py` never creates or opens the database; it is created at startup by `python app.py`.

## Routes

| Method | Route                | Purpose                       |
|--------|----------------------|-------------------------------|
| GET    | `/`                  | List all tasks                |
| GET    | `/task/new`          | Display the new-task form     |
| POST   | `/task`              | Validate and create a task    |
| GET    | `/task/<id>`         | Display one task's details    |
| POST   | `/task/<id>/status`  | Validate and update a status  |

## Note on the `due_date` field

The written assignment specification includes an optional `due_date` field on tasks. The course reference SQL schema omits it. This project keeps `due_date` (stored as text in `YYYY-MM-DD` format, or `NULL` when not set) and does not remove it to match the reference schema. See `docs/specification.md` for the full specification.
