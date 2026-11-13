# Week Five: SQLite projects and tasks

This folder is an independent copy of the Week Three Flask project, extended
with a SQLite `Project` and `Task` data model.

From this folder, create and activate a virtual environment and install the
requirements:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the app locally:

```powershell
python app.py
```

At startup, the app applies `schema/001_initial.sql` to the persistent
`app.db` file in this folder. Run the tests with:

```powershell
python -m pytest -q
```

Projects can be created, viewed, and renamed. Tasks can be created within a
project, viewed, and updated. Task creation and updates are validated both by
the application and by SQLite constraints.
