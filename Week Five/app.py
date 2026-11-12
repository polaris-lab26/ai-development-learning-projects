"""Project and task tracker for the Week Five database exercise."""

import os
import re
import secrets
import sqlite3
from datetime import date
from pathlib import Path

from flask import Flask, abort, g, jsonify, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
ALLOWED_STATUSES = ("todo", "in_progress", "done")
MAX_TITLE_LENGTH = 200
MAX_SIGNUP_NAME_LENGTH = 200
SQLITE_MAX_INTEGER = 2**63 - 1
DUE_DATE_PATTERN = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")

app = Flask(__name__)
app.config["DATABASE"] = str(BASE_DIR / "app.db")


def get_db():
    """Return this application context's SQLite connection."""
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.execute("PRAGMA foreign_keys = ON")
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Apply the initial schema to the configured database."""
    schema = (BASE_DIR / "schema" / "001_initial.sql").read_text(
        encoding="utf-8"
    )
    with app.app_context():
        db = get_db()
        db.executescript(schema)
        db.commit()


def get_project_or_404(project_id):
    if project_id > SQLITE_MAX_INTEGER:
        abort(404)
    project = (
        get_db()
        .execute(
            "SELECT id, name, created_at FROM Project WHERE id = ?",
            (project_id,),
        )
        .fetchone()
    )
    if project is None:
        abort(404)
    return project


def get_task_or_404(task_id):
    if task_id > SQLITE_MAX_INTEGER:
        abort(404)
    task = (
        get_db()
        .execute(
            "SELECT Task.id, Task.project_id, Task.title, Task.status, "
            "Task.due_date, Project.name AS project_name "
            "FROM Task JOIN Project ON Project.id = Task.project_id "
            "WHERE Task.id = ?",
            (task_id,),
        )
        .fetchone()
    )
    if task is None:
        abort(404)
    return task


def is_valid_due_date(value):
    if not DUE_DATE_PATTERN.fullmatch(value):
        return False
    try:
        date(int(value[:4]), int(value[5:7]), int(value[8:10]))
    except ValueError:
        return False
    return True


def validate_project_name(value):
    name = value.strip()
    if not name:
        return None, "Project name is required."
    return name, None


def validate_task(form, include_status=False):
    title = form.get("title", "").strip()
    due_date = form.get("due_date", "").strip()
    status = form.get("status", "todo").strip() if include_status else "todo"
    errors = []

    if not title:
        errors.append("Task title is required.")
    elif len(title) > MAX_TITLE_LENGTH:
        errors.append(
            f"Task title must be {MAX_TITLE_LENGTH} characters or fewer."
        )

    if include_status and status not in ALLOWED_STATUSES:
        errors.append("Choose a valid task status.")

    if due_date and not is_valid_due_date(due_date):
        errors.append("Due date must be a real date in YYYY-MM-DD format.")

    return {
        "title": title,
        "status": status,
        "due_date": due_date or None,
    }, errors


def render_error(status_code, heading, message):
    return (
        render_template(
            "error.html",
            status_code=status_code,
            heading=heading,
            message=message,
        ),
        status_code,
    )


@app.errorhandler(404)
def handle_not_found(error):
    return render_error(
        404, "Not found", "The project, task, or page could not be found."
    )


@app.errorhandler(405)
def handle_method_not_allowed(error):
    return render_error(
        405, "Method not allowed", "That action is not allowed for this address."
    )


@app.context_processor
def inject_statuses():
    return {"statuses": ALLOWED_STATUSES}


@app.post("/hooks/signup")
def signup():
    if not request.is_json:
        return jsonify(error="Content-Type must be application/json."), 415

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="A non-empty JSON object is required."), 400

    required_fields = ("name", "email", "company")
    missing_fields = [
        field
        for field in required_fields
        if not isinstance(data.get(field), str) or not data[field].strip()
    ]
    if missing_fields:
        return (
            jsonify(
                error="Missing or empty required fields: "
                + ", ".join(missing_fields)
            ),
            400,
        )

    name = data["name"].strip()
    email = data["email"].strip()
    if len(name) > MAX_SIGNUP_NAME_LENGTH:
        return (
            jsonify(
                error=f"Name must be {MAX_SIGNUP_NAME_LENGTH} characters or fewer."
            ),
            400,
        )
    if not EMAIL_PATTERN.fullmatch(email):
        return jsonify(error="A valid email address is required."), 400

    customer_reference = (
        f"CB-{date.today():%Y%m%d}-{secrets.randbelow(10_000):04d}"
    )
    return jsonify(customer_reference=customer_reference), 201


@app.get("/")
def index():
    projects = (
        get_db()
        .execute(
            "SELECT Project.id, Project.name, Project.created_at, "
            "COUNT(Task.id) AS task_count "
            "FROM Project LEFT JOIN Task ON Task.project_id = Project.id "
            "GROUP BY Project.id ORDER BY Project.id DESC"
        )
        .fetchall()
    )
    return render_template("index.html", projects=projects)


@app.get("/projects/new")
def new_project_form():
    return render_template("new_project.html", errors=[], name="")


@app.post("/projects")
def create_project():
    name, error = validate_project_name(request.form.get("name", ""))
    if error:
        return render_template(
            "new_project.html", errors=[error], name=request.form.get("name", "")
        ), 400

    db = get_db()
    try:
        cursor = db.execute("INSERT INTO Project (name) VALUES (?)", (name,))
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        return render_template(
            "new_project.html",
            errors=["A project with that name already exists."],
            name=name,
        ), 400

    return redirect(url_for("project_detail", project_id=cursor.lastrowid))


@app.get("/projects/<int:project_id>")
def project_detail(project_id):
    project = get_project_or_404(project_id)
    tasks = (
        get_db()
        .execute(
            "SELECT id, title, status, due_date FROM Task "
            "WHERE project_id = ? ORDER BY id DESC",
            (project_id,),
        )
        .fetchall()
    )
    return render_template("project_detail.html", project=project, tasks=tasks)


@app.post("/projects/<int:project_id>")
def update_project(project_id):
    get_project_or_404(project_id)
    name, error = validate_project_name(request.form.get("name", ""))
    if error:
        return render_template(
            "new_project.html",
            errors=[error],
            name=request.form.get("name", ""),
            project_id=project_id,
        ), 400

    db = get_db()
    try:
        db.execute(
            "UPDATE Project SET name = ? WHERE id = ?",
            (name, project_id),
        )
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        return render_template(
            "new_project.html",
            errors=["A project with that name already exists."],
            name=name,
            project_id=project_id,
        ), 400

    return redirect(url_for("project_detail", project_id=project_id))


@app.get("/projects/<int:project_id>/tasks/new")
def new_task_form(project_id):
    project = get_project_or_404(project_id)
    return render_template(
        "new_task.html",
        project=project,
        errors=[],
        form={"title": "", "due_date": ""},
    )


@app.post("/projects/<int:project_id>/tasks")
def create_task(project_id):
    project = get_project_or_404(project_id)
    cleaned, errors = validate_task(request.form)
    if errors:
        return render_template(
            "new_task.html",
            project=project,
            errors=errors,
            form=request.form,
        ), 400

    db = get_db()
    cursor = db.execute(
        "INSERT INTO Task (project_id, title, due_date) VALUES (?, ?, ?)",
        (project_id, cleaned["title"], cleaned["due_date"]),
    )
    db.commit()
    return redirect(url_for("task_detail", task_id=cursor.lastrowid))


@app.get("/tasks/<int:task_id>")
def task_detail(task_id):
    task = get_task_or_404(task_id)
    return render_template("task_detail.html", task=task)


@app.post("/tasks/<int:task_id>")
def update_task(task_id):
    task = get_task_or_404(task_id)
    cleaned, errors = validate_task(request.form, include_status=True)
    if errors:
        return render_template(
            "task_detail.html",
            task={**dict(task), **request.form},
            errors=errors,
        ), 400

    db = get_db()
    db.execute(
        "UPDATE Task SET title = ?, status = ?, due_date = ? WHERE id = ?",
        (cleaned["title"], cleaned["status"], cleaned["due_date"], task_id),
    )
    db.commit()
    return redirect(url_for("task_detail", task_id=task_id))


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=False)
