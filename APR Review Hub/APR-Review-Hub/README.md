# GCF APR Review Hub: visual skeleton

**Author:** TR

Student demonstrator (not an official GCF system). A runnable visual skeleton of four screens for Week Six accessibility and usability evaluation, specified in [`docs/APR-Review-Hub-Visual-Skeleton-Spec.md`](docs/APR-Review-Hub-Visual-Skeleton-Spec.md) (Revision 2.4).

It has no database, sign-in, permanent storage, automation or attachments. All sample data is invented and defined in `data.py`. A newly submitted report appears on the submitting browser session's dashboard and is not saved permanently.

## Run locally

Requires Python 3.9 or later.

Windows (PowerShell):

    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    flask --app app run

macOS or Linux:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    flask --app app run

Open http://127.0.0.1:5000 in a browser. The server only listens on your own computer.

## Viewing both roles

There is no sign-in. A "Demonstration only" bar at the top switches between the two roles (Project Officer and Programme Manager). It works by adding `?role=manager` to the address. The default is Project Officer.

## Design

The interface uses a warm cream background, deep-evergreen title, climate graphic, original globe emblem and pill navigation.

- Status colours: Submitted is blue, Approved is green, Returned is burnt orange. Each status also has an icon and a word, so colour is never the only signal.
- The official Green Climate Fund logo is not used. It is a registered trademark and needs written permission. The globe is an original drawing.
- Fonts are system fonts (Segoe UI, Open Sans, Noto Sans and similar). Nothing is loaded from the internet.
- Text colours meet 4.5:1 on the cream and panel surfaces. Control and panel borders use `#8a8163` (at least 3.13:1 on those surfaces); see the specification for measured ratios and scope.

## Project structure

    APR-Review-Hub/
    ├── app.py                  Flask routes and demonstration stubs
    ├── data.py                 Invented demonstration data
    ├── requirements.txt
    ├── requirements-dev.txt    Optional pytest development dependency
    ├── README.md
    ├── docs/
    │   ├── APR-Review-Hub-Visual-Skeleton-Spec.md  As-built visual specification
    │   ├── week06-ui-review.md                     Week Six heuristic and accessibility review
    │   └── portfolio/img/                          Before and after screenshots
    ├── tests/
    │   └── test_app.py         Flask route and form tests
    ├── templates/
    │   ├── base.html           Page frame, header, navigation, confirmation dialog
    │   ├── _macros.html        Shared icons, badge, field, timeline and link macros
    │   ├── dashboard.html
    │   ├── submit_report.html
    │   ├── report_review.html
    │   ├── report_history.html
    │   └── message.html        Wrong-role and not-found pages
    └── static/
        ├── css/styles.css
        ├── img/globe.svg       Original globe emblem
        ├── img/header-art.svg  Green climate graphic (upper-right corner)
        └── js/app.js           Mobile menu and confirmation dialog only

The Week Six review records the test method and any checks that could not be completed. Before/after evidence is in `docs/portfolio/img/`.

## Run tests

Install the optional test dependencies with `pip install -r requirements-dev.txt`, then run:

    python -m pytest -q

## What is not implemented

Database or permanent storage, authentication, real submit/approve/return workflows, automation, attachments, messaging, reminders and analytics. The Submit button validates the form and shows the submitted report on the dashboard for the current browser session. The Review buttons show demonstration messages; workflow decisions are not saved.
