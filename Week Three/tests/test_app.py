import sqlite3
from contextlib import closing

import pytest

from app import app, init_db


@pytest.fixture
def client(tmp_path):
    original_database = app.config["DATABASE"]
    database = tmp_path / "tasks.db"
    app.config.update(TESTING=True, DATABASE=str(database))
    init_db()

    yield app.test_client()

    app.config.update(TESTING=False, DATABASE=original_database)


def task_count(database):
    with closing(sqlite3.connect(database)) as connection:
        return connection.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]


def test_dashboard_and_static_stylesheet_load(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"There are no tasks yet" in response.data
    assert b"All tasks" in response.data

    stylesheet = client.get("/static/style.css")
    assert stylesheet.status_code == 200
    assert b".app-shell" in stylesheet.data


def test_new_task_form_loads(client):
    response = client.get("/task/new")

    assert response.status_code == 200
    assert b'name="title"' in response.data
    assert b'name="description"' in response.data
    assert b'name="due_date"' in response.data


def test_create_task_trims_values_and_redirects_to_detail(client):
    response = client.post(
        "/task",
        data={
            "title": "  Coastal survey  ",
            "description": "  Collect shoreline samples.  ",
            "due_date": "  2028-02-29  ",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/task/1")

    detail = client.get("/task/1")
    assert detail.status_code == 200
    assert b"Coastal survey" in detail.data
    assert b"Collect shoreline samples." in detail.data
    assert b"2028-02-29" in detail.data
    assert b"To do" in detail.data


def test_blank_optional_fields_are_stored_as_null(client):
    client.post(
        "/task",
        data={"title": "Water sample review", "description": "  ", "due_date": "  "},
    )

    with closing(sqlite3.connect(app.config["DATABASE"])) as connection:
        row = connection.execute(
            "SELECT description, due_date FROM tasks WHERE id = 1"
        ).fetchone()

    assert row == (None, None)


@pytest.mark.parametrize(
    ("data", "message"),
    [
        ({}, b"Title is required"),
        ({"title": " \t "}, b"Title is required"),
        ({"title": "x" * 201}, b"Title must be 200 characters or fewer"),
        ({"title": "Task", "due_date": "2026-02-30"}, b"Due date must be"),
        ({"title": "Task", "due_date": "2026-6-5"}, b"Due date must be"),
        ({"title": "Task", "due_date": "06/05/2026"}, b"Due date must be"),
    ],
)
def test_invalid_task_input_is_rejected_without_inserting(client, data, message):
    response = client.post("/task", data=data)

    assert response.status_code == 400
    assert message in response.data
    assert task_count(app.config["DATABASE"]) == 0


def test_invalid_task_input_preserves_submitted_values(client):
    response = client.post(
        "/task",
        data={
            "title": "  Draft field plan  ",
            "description": "  Notes for the team  ",
            "due_date": "2026-02-30",
        },
    )

    assert response.status_code == 400
    assert b"  Draft field plan  " in response.data
    assert b"  Notes for the team  " in response.data
    assert b"2026-02-30" in response.data


def test_task_detail_not_found_and_non_integer_id(client):
    for path in ("/task/999", "/task/abc", "/task/9223372036854775808"):
        response = client.get(path)
        assert response.status_code == 404
        assert b"Not found" in response.data


def test_dashboard_lists_newest_tasks_first(client):
    client.post("/task", data={"title": "First task"})
    client.post("/task", data={"title": "Second task"})

    response = client.get("/")

    assert response.status_code == 200
    assert response.data.index(b"Second task") < response.data.index(b"First task")


def test_status_update_accepts_allowed_values(client):
    client.post("/task", data={"title": "Inspect inlet"})

    for status in ("in_progress", "done", "todo"):
        response = client.post("/task/1/status", data={"status": status})
        assert response.status_code == 302
        detail = client.get("/task/1")
        assert detail.status_code == 200
        assert f'value="{status}" selected'.encode() in detail.data

    with closing(sqlite3.connect(app.config["DATABASE"])) as connection:
        status = connection.execute(
            "SELECT status FROM tasks WHERE id = 1"
        ).fetchone()[0]
    assert status == "todo"


@pytest.mark.parametrize("data", [{}, {"status": "blocked"}])
def test_invalid_status_is_rejected_without_changing_task(client, data):
    client.post("/task", data={"title": "Inspect inlet"})

    response = client.post("/task/1/status", data=data)

    assert response.status_code == 400
    assert b"Invalid status" in response.data
    with closing(sqlite3.connect(app.config["DATABASE"])) as connection:
        status = connection.execute(
            "SELECT status FROM tasks WHERE id = 1"
        ).fetchone()[0]
    assert status == "todo"


def test_missing_task_status_update_returns_404_before_validating_status(client):
    response = client.post("/task/999/status", data={"status": "invalid"})

    assert response.status_code == 404


def test_unsupported_method_uses_error_page(client):
    response = client.get("/task")

    assert response.status_code == 405
    assert b"Method not allowed" in response.data
