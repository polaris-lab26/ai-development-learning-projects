import pytest

import data
from app import app


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    return app.test_client()


def valid_report():
    return {
        "project_name": "Test project",
        "year": "2025",
        "progress": "Progress",
        "results": "Results",
        "challenges": "Challenges",
        "priorities": "Priorities",
    }


def test_dashboards_show_role_specific_report_lists(client):
    officer = client.get("/")
    manager = client.get("/?role=manager")

    assert officer.status_code == 200
    assert b"Your reports" in officer.data
    assert b"Wetland Monitoring Network" not in officer.data
    assert manager.status_code == 200
    assert b"Waiting for review" in manager.data
    assert b"Wetland Monitoring Network" in manager.data


def test_role_restrictions_and_missing_report(client):
    assert client.get("/submit?role=manager").status_code == 403
    assert client.get("/review/1").status_code == 403
    assert client.get("/review/999?role=manager").status_code == 404
    assert client.get("/submit/4").status_code == 404


def test_submit_validation_and_demo_confirmation(client):
    invalid = client.post("/submit", data={})
    assert invalid.status_code == 200
    assert b"Enter the project name." in invalid.data
    assert b"Select the reporting year." in invalid.data
    assert b'role="alert"' in invalid.data

    submitted = client.post("/submit", data=valid_report())
    assert submitted.status_code == 302
    assert "notice=submitted" in submitted.headers["Location"]
    dashboard = client.get(submitted.headers["Location"])
    assert b"not permanently saved" in dashboard.data
    assert len(data.REPORTS) == 5


def test_submitted_report_is_displayed_only_in_its_browser_session(client):
    report = valid_report()
    report["project_name"] = "Session display test"
    client.post("/submit", data=report)

    dashboard = client.get("/")
    assert b"Session display test, APR 2025" in dashboard.data
    assert b"Visible in this browser session only" in dashboard.data
    assert b"Session-only demonstration" in dashboard.data

    with app.test_client() as fresh_client:
        assert b"Session display test" not in fresh_client.get("/").data


def test_returned_report_is_prefilled_and_can_be_resubmitted(client):
    form = client.get("/submit/2")
    assert form.status_code == 200
    assert b"Please add results against the original targets." in form.data
    assert b"Pumps were installed on 18 of 25 farms." in form.data

    resubmitted = client.post("/submit/2", data=valid_report())
    assert resubmitted.status_code == 302
    assert "notice=resubmitted" in resubmitted.headers["Location"]
    assert data.get_report(2)["status"] == "Returned"


def test_review_requires_return_comment_and_allows_approval_without_one(client):
    returned = client.post(
        "/review/1?role=manager", data={"decision": "return", "comment": ""}
    )
    assert returned.status_code == 200
    assert b"Enter a comment to return this report." in returned.data

    approved = client.post(
        "/review/1?role=manager", data={"decision": "approve", "comment": ""}
    )
    assert approved.status_code == 302
    assert "notice=approved" in approved.headers["Location"]
    assert data.get_report(1)["status"] == "Submitted"

    returned_with_comment = client.post(
        "/review/1?role=manager",
        data={"decision": "return", "comment": "Add the missing results."},
    )
    assert returned_with_comment.status_code == 302
    assert "notice=returned" in returned_with_comment.headers["Location"]


def test_history_filters_and_preserves_role_scope(client):
    officer_history = client.get("/history?status=Returned")
    manager_history = client.get("/history?role=manager&status=Submitted")

    assert officer_history.status_code == 200
    assert b"Solar Irrigation Scheme" in officer_history.data
    assert b"Mangrove Restoration" not in officer_history.data
    assert manager_history.status_code == 200
    assert b"Wetland Monitoring Network" in manager_history.data
    assert b"Solar Irrigation Scheme" not in manager_history.data
