"""GCF APR Review Hub: visual skeleton (student demonstrator).

Demonstration only: no database, authentication, workflow or automation.
Sample data comes from data.py; report submissions are shown only for the
current browser session. The "role" is chosen with ?role=officer or
?role=manager purely so both sets of screens can be evaluated.
"""
import secrets
from datetime import datetime

from flask import Flask, abort, g, redirect, render_template, request, session, url_for

import data

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.jinja_env.globals.update(
    STATUSES=data.STATUSES, YEARS=data.YEARS, TEXT_FIELDS=data.TEXT_FIELDS
)

ROLES = {"officer": "Project Officer", "manager": "Programme Manager"}
NAV = [  # (endpoint, label, roles that see it)
    ("dashboard", "Dashboard", ("officer", "manager")),
    ("submit_report", "Submit Report", ("officer",)),
    ("report_history", "Report History", ("officer", "manager")),
]
NOTICES = {
    "submitted": "Report submitted for review.",
    "resubmitted": "Report resubmitted for review.",
    "approved": "Report approved.",
    "returned": "Report returned with your comment.",
}
DEMO_NOTE = " This is a demonstration; changes are not permanently saved."


@app.before_request
def set_demo_role():
    role = request.args.get("role")
    g.role = role if role in ROLES else "officer"
    g.user_id = data.DEMO_USERS[g.role]
    g.user = data.USERS[g.user_id]


@app.url_defaults
def keep_role(endpoint, values):
    """Carry the demo role through every internal link."""
    if endpoint != "static" and "role" not in values and g.get("role") == "manager":
        values["role"] = "manager"


@app.template_filter("dt")
def format_datetime(value):
    return f"{value.day} {value:%b %Y, %H:%M}"


def role_url(role):
    """Same page, shown as the other demo role."""
    if not request.endpoint:
        return url_for("dashboard", role=role)
    args = {k: v for k, v in request.args.items() if k not in ("role", "notice")}
    return url_for(request.endpoint, **(request.view_args or {}), **args, role=role)


@app.context_processor
def inject_context():
    return {
        "role": g.role,
        "role_label": ROLES[g.role],
        "user": g.user,
        "demo_roles": ROLES,
        "nav_items": NAV,
        "role_url": role_url,
    }


def message(title, text, status):
    return render_template("message.html", title=title, text=text), status


def wrong_role(audience):
    return message(
        f"This page is for {audience}",
        f"You are viewing the application as a {ROLES[g.role]}.",
        403,
    )


@app.errorhandler(404)
def not_found(_error):
    return message("Page not found", "That page or report does not exist.", 404)


def validate_report(form):
    errors = {}
    if not form.get("project_name", "").strip():
        errors["project_name"] = "Enter the project name."
    if form.get("year") not in {str(y) for y in data.YEARS}:
        errors["year"] = "Select the reporting year."
    for name, label in data.TEXT_FIELDS:
        if not form.get(name, "").strip():
            errors[name] = f"Enter the {label.lower()}."
    return errors


@app.route("/")
def dashboard():
    reports = data.visible_reports(g.user_id if g.role == "officer" else None)
    if g.role == "officer":
        reports.extend(
            {
                **report,
                "updated": datetime.fromisoformat(report["updated"]),
                "submitted_at": datetime.fromisoformat(report["submitted_at"]),
            }
            for report in session.get("submitted_reports", [])
        )
    waiting = sorted(
        (r for r in reports if r["status"] == "Submitted"),
        key=lambda r: r["submitted_at"],
    )
    decided = [r for r in reports if r["status"] != "Submitted"]
    return render_template(
        "dashboard.html",
        reports=sorted(reports, key=lambda r: r["status"] != "Returned"),
        counts=data.status_counts(reports),
        waiting=waiting,
        decided=decided,
        notice=NOTICES.get(request.args.get("notice")),
        notice_note=DEMO_NOTE,
    )


@app.route("/submit", methods=["GET", "POST"])
@app.route("/submit/<int:report_id>", methods=["GET", "POST"])
def submit_report(report_id=None):
    if g.role != "officer":
        return wrong_role("Project Officers")
    report = None
    if report_id is not None:
        report = data.get_report(report_id)
        if report is None or report["owner"] != g.user_id:
            abort(404)
        if report["status"] != "Returned":
            return message(
                "This report cannot be amended",
                "Only reports that have been returned can be amended and resubmitted.",
                403,
            )
    values, errors = report or {}, {}
    if request.method == "POST":
        values = request.form
        errors = validate_report(values)
        if not errors:  # demonstration only: new submissions last for this session
            if report is None:
                submitted_reports = session.get("submitted_reports", [])
                submitted_at = datetime.now().isoformat(timespec="minutes")
                submitted_reports.append(
                    {
                        "title": f'{values["project_name"].strip()}, APR {values["year"]}',
                        "year": int(values["year"]),
                        "status": "Submitted",
                        "updated": submitted_at,
                        "submitted_at": submitted_at,
                        "returns": [],
                        "session_only": True,
                    }
                )
                session["submitted_reports"] = submitted_reports
            return redirect(
                url_for("dashboard", notice="resubmitted" if report else "submitted")
            )
    return render_template(
        "submit_report.html",
        report=report,
        returned=report["returns"][-1] if report else None,
        values=values,
        errors=errors,
    )


@app.route("/review/<int:report_id>", methods=["GET", "POST"])
def report_review(report_id):
    if g.role != "manager":
        return wrong_role("Programme Managers")
    report = data.get_report(report_id)
    if report is None:
        abort(404)
    errors, comment = {}, ""
    if request.method == "POST":
        if report["status"] != "Submitted":
            return message(
                "This report has already been decided",
                "Only submitted reports can be approved or returned.",
                403,
            )
        decision = request.form.get("decision")
        comment = request.form.get("comment", "")
        if decision == "return" and not comment.strip():
            errors["comment"] = "Enter a comment to return this report."
        elif decision in ("approve", "return"):  # demonstration only: nothing is saved
            return redirect(
                url_for("dashboard", notice="approved" if decision == "approve" else "returned")
            )
    return render_template(
        "report_review.html", report=report, errors=errors, comment=comment
    )


@app.route("/history")
def report_history():
    status = request.args.get("status", "")
    if status not in data.STATUSES:
        status = ""
    reports = data.visible_reports(g.user_id if g.role == "officer" else None)
    if status:
        reports = [r for r in reports if r["status"] == status]
    return render_template(
        "report_history.html",
        reports=reports,
        status=status,
        open_id=request.args.get("report", type=int),
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
