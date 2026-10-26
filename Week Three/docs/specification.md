# Atlantic Environmental Research Unit — Task Management Application: Specification

This document describes the required behavior implemented in `app.py`.

## 1. Purpose

A small server-rendered Flask application that replaces a shared spreadsheet used to track environmental research tasks.

## 2. Technology

- Python 3.11+
- Flask 3.x
- SQLite (standard-library `sqlite3`, no ORM)
- Jinja templates and ordinary HTML forms
- pytest

## 3. Database

SQLite table `tasks`:

| Field         | Requirements                                                                  |
|---------------|-------------------------------------------------------------------------------|
| `id`          | Integer primary key, automatically generated                                  |
| `title`       | Required text, maximum 200 characters                                         |
| `description` | Optional text (stored as `NULL` when blank)                                   |
| `status`      | Required text; one of `todo`, `in_progress`, `done`; default `todo`           |
| `created_at`  | Automatically recorded creation timestamp (SQLite `CURRENT_TIMESTAMP`, UTC)   |
| `due_date`    | Optional date stored as text in exact `YYYY-MM-DD` format; `NULL` when absent |

The database path is `app.config["DATABASE"]`. The default is `tasks.db` in the same directory as `app.py`, independent of the current working directory.

### Known discrepancy: `due_date`

The written assignment specification includes an optional `due_date` field. The course reference SQL schema omits it. This application **preserves `due_date`** as specified in the written assignment. It was not removed to match the reference schema.

## 4. Allowed statuses

`todo`, `in_progress`, `done`. No other values are accepted. New tasks always start as `todo`.

## 5. Routes

| Method | Route                | Purpose                                         |
|--------|----------------------|-------------------------------------------------|
| GET    | `/`                  | List all tasks (newest first)                   |
| GET    | `/task/new`          | Display the new-task form                       |
| POST   | `/task`              | Validate and create a task                      |
| GET    | `/task/<id>`         | Display one task's details                      |
| POST   | `/task/<id>/status`  | Validate and update a task's status             |

`<id>` is matched as an integer. A non-integer ID (for example `/task/abc`) does not match a route and returns 404.

## 6. Task creation and validation

- Title is mandatory. Missing, empty, or whitespace-only titles are rejected.
- Leading and trailing whitespace is trimmed from the title before it is validated and stored.
- A trimmed title longer than 200 characters is rejected.
- Description is optional. It is trimmed, and a blank description is stored as `NULL`.
- Due date is optional. Surrounding whitespace is trimmed and a blank value is stored as SQL `NULL` (never an empty string). If supplied it must:
  1. match exactly `YYYY-MM-DD` (four digits, hyphen, two digits, hyphen, two digits, checked with a strict regular expression), and
  2. be a real calendar date (checked by constructing a `datetime.date`).
- Rejected examples: `2026-02-30`, `2026-6-5`, `06/05/2026`.
- On invalid input the form is shown again with HTTP status 400, a list of clear error messages, and the user's original title, description and due date preserved.
- On success the task is stored with status `todo` and the browser is redirected (POST/Redirect/GET) to the task's detail page.

## 7. Status updates

- The submitted `status` must be one of the three allowed values. A missing or invalid value gives an error page with HTTP status 400 and no change to the task.
- On success the browser is redirected (POST/Redirect/GET) to the task's detail page.
- If the task does not exist, HTTP 404 is returned (this check happens before status validation).

## 8. Error handling

Two different templates are used, depending on the kind of problem:

| Situation                                                     | Template        | HTTP status |
|---------------------------------------------------------------|-----------------|-------------|
| Task or page not found (including non-integer IDs)            | `error.html`    | 404         |
| Unsupported HTTP method for a route (for example `GET /task`) | `error.html`    | 405         |
| Invalid or missing status value on a status update            | `error.html`    | 400         |
| Invalid task-creation input (title or due date)               | `new_task.html` | 400         |

- `error.html` is a simple page showing a heading, a message, the error code and a link back to the task list.
- Invalid task-creation input does **not** use `error.html`. The new-task form is displayed again with the validation messages and the user's entered values, so the user can correct them.

## 9. Security and implementation notes

- All SQL that includes user-supplied values uses parameterised queries.
- Jinja autoescaping is enabled and no user content is marked safe.
- Flask debug mode is off by default.
- No secret key and no sessions (not needed).
- Importing `app.py` does not create or open any database. The database is initialised in `if __name__ == "__main__":` startup, and tests initialise their own temporary databases.
- Connections are stored on `flask.g` and closed in a `teardown_appcontext` handler.

## 10. Out of scope

Authentication and users, editing or deleting tasks, an API, an ORM, a JavaScript framework, pagination, search or filtering, an application factory, deployment, and any feature not listed above.