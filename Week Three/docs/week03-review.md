# Week Three Review Record

## Findings and corrections

- Status-update coverage: the prior test checked redirects and page responses for all allowed statuses, but queried the database only after the final `todo` update. It now checks the selected status on the detail page after each permitted update.
- Creation timestamp coverage: the successful-creation test did not verify `created_at`. It now reads the stored value and checks it round-trips through SQLite's `YYYY-MM-DD HH:MM:SS` timestamp format.
- Coursework structure: the task templates duplicated the shared page shell and had no base template. Added `templates/base.html` and converted the four pages to extend it.
- Specification filename: renamed `docs/specification.md.txt` to `docs/specification.md` and updated the README reference.

## Verification

`python -m pytest -p no:cacheprovider --basetemp=.pytest-tmp` — **18 passed** using the Week Three virtual environment on Python 3.15.0.

### Clean-clone test — 26 October 2026

- Created a fresh clone in a separate temporary directory from commit `64f8f39e079609157f187532c78e1b1a7887775a`.
- Installed dependencies successfully.
- Ran `python -m pytest` — **18 passed**.
- Started the Flask application successfully on port 5011 because port 5010 was occupied at the time.
- Verified the dashboard, task form, and stylesheet returned HTTP 200; a missing task returned the expected HTTP 404.
- Confirmed the browser rendered the dashboard successfully.
- The clone's Git working tree remained clean.
- The clone test did not modify the original repository or its Git history.

## Remaining verification

- The scaffold and test fixes have separate commits and are pushed to `origin/master`.
- A pull request and merge have not been completed; both remain outstanding.
