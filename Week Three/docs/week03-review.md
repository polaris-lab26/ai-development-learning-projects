# Week Three Review Record

## Findings and corrections

- Status-update coverage: the prior test checked redirects and page responses for all allowed statuses, but queried the database only after the final `todo` update. It now checks the selected status on the detail page after each permitted update.
- Creation timestamp coverage: the successful-creation test did not verify `created_at`. It now reads the stored value and checks it round-trips through SQLite's `YYYY-MM-DD HH:MM:SS` timestamp format.
- Coursework structure: the task templates duplicated the shared page shell and had no base template. Added `templates/base.html` and converted the four pages to extend it.
- Specification filename: renamed `docs/specification.md.txt` to `docs/specification.md` and updated the README reference.

## Verification

`python -m pytest -p no:cacheprovider --basetemp=.pytest-tmp` — **18 passed** using the Week Three virtual environment on Python 3.15.0.

## Remaining verification

- A clean-clone installation and run has not been performed.
- The scaffold and test fixes have separate commits and are pushed to `origin/master`.
- A pull request and merge have not been completed; the coursework review-and-merge step remains outstanding.
