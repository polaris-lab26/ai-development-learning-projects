import re
import sqlite3
import subprocess
import sys
from datetime import date
from pathlib import Path
from textwrap import dedent

import pytest

from app import app, get_db, init_db


@pytest.fixture
def client(tmp_path):
    original_database = app.config["DATABASE"]
    app.config.update(TESTING=True, DATABASE=str(tmp_path / "test.db"))
    init_db()

    yield app.test_client()

    app.config.update(TESTING=False, DATABASE=original_database)


def create_project(client, name="Coastal Survey"):
    response = client.post("/projects", data={"name": name})
    assert response.status_code == 302
    return int(response.headers["Location"].rsplit("/", 1)[1])


def valid_signup():
    return {
        "name": "Ada Lovelace",
        "email": "ada@example.com",
        "company": "Analytical Engines",
    }


def test_connections_enable_foreign_keys(client):
    with app.app_context():
        assert get_db().execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_project_create_read_and_update(client):
    project_id = create_project(client)

    detail = client.get(f"/projects/{project_id}")
    assert detail.status_code == 200
    assert b"Coastal Survey" in detail.data

    response = client.post(
        f"/projects/{project_id}",
        data={"name": "Estuary Survey"},
    )
    assert response.status_code == 302
    assert b"Estuary Survey" in client.get(response.headers["Location"]).data

    listing = client.get("/")
    assert listing.status_code == 200
    assert b"Estuary Survey" in listing.data


def test_duplicate_project_names_are_rejected(client):
    create_project(client, "Estuary Survey")

    response = client.post("/projects", data={"name": "Estuary Survey"})

    assert response.status_code == 400
    assert b"already exists" in response.data
    with app.app_context():
        count = get_db().execute(
            "SELECT COUNT(*) FROM Project WHERE name = ?",
            ("Estuary Survey",),
        ).fetchone()[0]
    assert count == 1


def test_task_create_read_and_update_through_application(client):
    project_id = create_project(client)
    response = client.post(
        f"/projects/{project_id}/tasks",
        data={"title": "Collect water samples", "due_date": "2028-02-29"},
    )

    assert response.status_code == 302
    task_url = response.headers["Location"]
    detail = client.get(task_url)
    assert detail.status_code == 200
    assert b"Collect water samples" in detail.data
    assert b"todo" in detail.data

    task_id = int(task_url.rsplit("/", 1)[1])
    updated = client.post(
        f"/tasks/{task_id}",
        data={
            "title": "Review water samples",
            "status": "in_progress",
            "due_date": "2028-03-01",
        },
    )
    assert updated.status_code == 302
    updated_detail = client.get(task_url)
    assert b"Review water samples" in updated_detail.data
    assert b"in_progress" in updated_detail.data
    assert b"2028-03-01" in updated_detail.data

    project_detail = client.get(f"/projects/{project_id}")
    assert b"Review water samples" in project_detail.data


def test_task_with_nonexistent_project_is_rejected_by_database(client):
    with app.app_context():
        db = get_db()
        with pytest.raises(sqlite3.IntegrityError):
            db.execute(
                "INSERT INTO Task (project_id, title) VALUES (?, ?)",
                (999, "Orphan task"),
            )


def test_invalid_task_status_is_rejected_by_database(client):
    project_id = create_project(client)
    with app.app_context():
        db = get_db()
        with pytest.raises(sqlite3.IntegrityError):
            db.execute(
                "INSERT INTO Task (project_id, title, status) VALUES (?, ?, ?)",
                (project_id, "Invalid status task", "blocked"),
            )


def test_task_status_update_rejects_invalid_value(client):
    project_id = create_project(client)
    response = client.post(
        f"/projects/{project_id}/tasks",
        data={"title": "Check sensor"},
    )
    task_id = int(response.headers["Location"].rsplit("/", 1)[1])

    response = client.post(
        f"/tasks/{task_id}",
        data={"title": "Check sensor", "status": "blocked"},
    )

    assert response.status_code == 400
    assert b"valid task status" in response.data
    assert b"todo" in client.get(f"/tasks/{task_id}").data


def test_overlong_task_title_is_rejected(client):
    project_id = create_project(client)
    response = client.post(
        f"/projects/{project_id}/tasks",
        data={"title": "x" * 201},
    )

    assert response.status_code == 400
    assert b"200 characters or fewer" in response.data
    with app.app_context():
        count = get_db().execute(
            "SELECT COUNT(*) FROM Task WHERE project_id = ?",
            (project_id,),
        ).fetchone()[0]
    assert count == 0


def test_database_rejects_overlong_task_title(client):
    project_id = create_project(client)
    with app.app_context():
        db = get_db()
        with pytest.raises(sqlite3.IntegrityError):
            db.execute(
                "INSERT INTO Task (project_id, title) VALUES (?, ?)",
                (project_id, "x" * 201),
            )
        cursor = db.execute(
            "INSERT INTO Task (project_id, title) VALUES (?, ?)",
            (project_id, "x" * 200),
        )
        assert cursor.lastrowid is not None


def test_database_rejects_empty_task_title(client):
    project_id = create_project(client)
    with app.app_context():
        with pytest.raises(sqlite3.IntegrityError):
            get_db().execute(
                "INSERT INTO Task (project_id, title) VALUES (?, ?)",
                (project_id, ""),
            )


def test_database_restricts_project_deletion_when_tasks_exist(client):
    project_id = create_project(client)
    client.post(
        f"/projects/{project_id}/tasks",
        data={"title": "Review shoreline"},
    )

    with app.app_context():
        with pytest.raises(sqlite3.IntegrityError):
            get_db().execute("DELETE FROM Project WHERE id = ?", (project_id,))


def test_missing_task_returns_404(client):
    assert client.get("/tasks/999").status_code == 404


def test_database_survives_application_process_restart(tmp_path):
    database = tmp_path / "persistent.db"
    project_process = dedent(
        """
        import sys
        from app import app, init_db

        app.config["DATABASE"] = sys.argv[1]
        init_db()
        with app.test_client() as client:
            response = client.post("/projects", data={"name": "Restart Study"})
            assert response.status_code == 302
            project_id = response.headers["Location"].rsplit("/", 1)[1]
            response = client.post(
                f"/projects/{project_id}/tasks",
                data={"title": "Read after restart"},
            )
            assert response.status_code == 302
        """
    )
    read_process = dedent(
        """
        import sys
        from app import app, init_db

        app.config["DATABASE"] = sys.argv[1]
        init_db()
        with app.test_client() as client:
            response = client.get("/")
            assert response.status_code == 200
            assert b"Restart Study" in response.data
            response = client.get("/tasks/1")
            assert response.status_code == 200
            assert b"Read after restart" in response.data
        """
    )
    project_root = Path(__file__).resolve().parents[1]

    subprocess.run(
        [sys.executable, "-c", project_process, str(database)],
        check=True,
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [sys.executable, "-c", read_process, str(database)],
        check=True,
        cwd=project_root,
        capture_output=True,
        text=True,
    )


def test_valid_signup_returns_customer_reference(client):
    response = client.post("/hooks/signup", json=valid_signup())

    assert response.status_code == 201
    customer_reference = response.get_json()["customer_reference"]
    assert re.fullmatch(r"CB-\d{8}-\d{4}", customer_reference)
    assert customer_reference.startswith(f"CB-{date.today():%Y%m%d}-")


def test_signup_rejects_missing_or_empty_body_and_required_fields(client):
    response = client.post("/hooks/signup", content_type="application/json")
    assert response.status_code == 400

    for body in ("", '{"name":'):
        response = client.post(
            "/hooks/signup",
            data=body,
            content_type="application/json",
        )
        assert response.status_code == 400

    for field in ("name", "email", "company"):
        data = valid_signup()
        del data[field]
        response = client.post("/hooks/signup", json=data)
        assert response.status_code == 400
        assert field in response.get_json()["error"]


def test_signup_rejects_malformed_email(client):
    data = valid_signup()
    data["email"] = "not-an-email"

    response = client.post("/hooks/signup", json=data)

    assert response.status_code == 400
    assert "email" in response.get_json()["error"]


def test_signup_rejects_non_json_request(client):
    response = client.post(
        "/hooks/signup",
        data="name=Ada",
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 415


def test_signup_rejects_overlong_name(client):
    data = valid_signup()
    data["name"] = "A" * 201

    response = client.post("/hooks/signup", json=data)

    assert response.status_code == 400
    assert "Name must be" in response.get_json()["error"]
