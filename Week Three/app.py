"""Atlantic Environmental Research Unit - Task Management Application.

A small Flask + SQLite app for tracking research tasks.
Run it with:  python app.py
"""

import os
import re
import sqlite3
from datetime import date

from flask import Flask, abort, g, redirect, render_template, request, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ALLOWED_STATUSES = ("todo", "in_progress", "done")
MAX_TITLE_LENGTH = 200
SQLITE_MAX_INTEGER = 2**63 - 1  # larger IDs cannot exist in SQLite

# [0-9] (not \d) so that non-ASCII digits are not accepted.
DUE_DATE_PATTERN = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL CHECK (length(title) <= 200),
    description TEXT,
    status      TEXT NOT NULL DEFAULT 'todo'
                CHECK (status IN ('todo', 'in_progress', 'done')),
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date    TEXT
);
"""

app = Flask(__name__)
# Predictable default path, independent of the current working directory.
# Importing this module only sets the path; it never opens the database.
app.config["DATABASE"] = os.path.join(BASE_DIR, "tasks.db")


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------


def get_db():
    """Return this application context's SQLite connection, opening it if needed."""
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    """Close the connection at the end of every application context."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the tasks table in the configured database if it is missing."""
    with app.app_context():
        db = get_db()
        db.executescript(SCHEMA)
        db.commit()


def get_task_or_404(task_id):
    """Return the task row with this id, or abort with HTTP 404."""
    if task_id > SQLITE_MAX_INTEGER:
        abort(404)
    task = (
        get_db()
        .execute(
            "SELECT id, title, description, status, created_at, due_date "
            "FROM tasks WHERE id = ?",
            (task_id,),
        )
        .fetchone()
    )
    if task is None:
        abort(404)
    return task


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def is_valid_due_date(value):
    """True only for a real calendar date written exactly as YYYY-MM-DD."""
    if not DUE_DATE_PATTERN.fullmatch(value):
        return False
    year, month, day = int(value[0:4]), int(value[5:7]), int(value[8:10])
    try:
        date(year, month, day)  # rejects 2026-02-30, month 13, year 0000, ...
    except ValueError:
        return False
    return True


def validate_new_task(form):
    """Validate submitted form data.

    Returns (cleaned, errors). `cleaned` holds the values to store; `errors`
    is a list of human-readable messages (empty when the input is valid).
    """
    title = form.get("title", "").strip()
    description = form.get("description", "").strip()
    due_date = form.get("due_date", "").strip()
    errors = []

    if not title:
        errors.append("Title is required and cannot be blank.")
    elif len(title) > MAX_TITLE_LENGTH:
        errors.append(
            f"Title must be {MAX_TITLE_LENGTH} characters or fewer "
            f"(you entered {len(title)})."
        )

    if due_date and not is_valid_due_date(due_date):
        errors.append(
            "Due date must be a real calendar date in YYYY-MM-DD format, "
            "for example 2026-06-05."
        )

    cleaned = {
        "title": title,
        "description": description or None,
        "due_date": due_date or None,  # missing date is stored as NULL
    }
    return cleaned, errors


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


def render_error(status_code, heading, message):
    """Render the shared error page with the given HTTP status code."""
    page = render_template(
        "error.html",
        status_code=status_code,
        heading=heading,
        message=message,
    )
    return page, status_code


@app.errorhandler(404)
def handle_not_found(error):
    return render_error(
        404, "Not found", "The task or page you requested could not be found."
    )


@app.errorhandler(405)
def handle_method_not_allowed(error):
    return render_error(
        405, "Method not allowed", "That action is not allowed for this address."
    )


@app.context_processor
def inject_statuses():
    """Make the allowed statuses available to every template."""
    return {"statuses": ALLOWED_STATUSES}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/")
def index():
    tasks = (
        get_db()
        .execute(
            "SELECT id, title, status, created_at, due_date "
            "FROM tasks ORDER BY id DESC"
        )
        .fetchall()
    )
    return render_template("index.html", tasks=tasks)


@app.get("/task/new")
def new_task_form():
    return render_template(
        "new_task.html",
        errors=[],
        form={"title": "", "description": "", "due_date": ""},
    )


@app.post("/task")
def create_task():
    cleaned, errors = validate_new_task(request.form)

    if errors:
        # Show the user's original input again, exactly as they typed it.
        form = {
            "title": request.form.get("title", ""),
            "description": request.form.get("description", ""),
            "due_date": request.form.get("due_date", ""),
        }
        return render_template("new_task.html", errors=errors, form=form), 400

    db = get_db()
    cursor = db.execute(
        "INSERT INTO tasks (title, description, status, due_date) "
        "VALUES (?, ?, 'todo', ?)",
        (cleaned["title"], cleaned["description"], cleaned["due_date"]),
    )
    db.commit()
    return redirect(url_for("task_detail", task_id=cursor.lastrowid))


@app.get("/task/<int:task_id>")
def task_detail(task_id):
    task = get_task_or_404(task_id)
    return render_template("task_detail.html", task=task)


@app.post("/task/<int:task_id>/status")
def update_task_status(task_id):
    get_task_or_404(task_id)  # 404 takes priority over status validation

    status = request.form.get("status")
    if status not in ALLOWED_STATUSES:
        return render_error(
            400,
            "Invalid status",
            "Status must be one of: " + ", ".join(ALLOWED_STATUSES) + ".",
        )

    db = get_db()
    db.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    db.commit()
    return redirect(url_for("task_detail", task_id=task_id))


if __name__ == "__main__":
    init_db()  # normal startup: make sure the database exists before serving
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=False)
