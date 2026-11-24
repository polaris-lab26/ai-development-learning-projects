"""Invented demonstration data for the visual skeleton.

Nothing here is stored, changed or read from a database. Each report's status
is derived from its last activity entry, so the data cannot contradict itself.
"""
from datetime import datetime

STATUSES = {"Submitted": "●", "Returned": "↩", "Approved": "✓"}
YEARS = [2026, 2025, 2024, 2023]

# Provisional report fields (not confirmed requirements).
TEXT_FIELDS = [
    ("progress", "Progress summary"),
    ("results", "Key results achieved"),
    ("challenges", "Challenges encountered"),
    ("priorities", "Priorities for next year"),
]

USERS = {
    "officer-1": {"name": "Aoife Murphy", "role": "Project Officer"},
    "officer-2": {"name": "Siobhán Kelly", "role": "Project Officer"},
    "manager-1": {"name": "Daniel Okafor", "role": "Programme Manager"},
}
# Demonstration only: which sample person each demo view is shown as.
DEMO_USERS = {"officer": "officer-1", "manager": "manager-1"}

_STATUS_AFTER = {
    "Submitted": "Submitted",
    "Resubmitted": "Submitted",
    "Returned": "Returned",
    "Approved": "Approved",
}


def _entry(action, user, month, day, hour, minute, comment=""):
    return {
        "action": action,
        "user": user,
        "at": datetime(2026, month, day, hour, minute),
        "comment": comment,
    }


REPORTS = [
    {
        "id": 1,
        "owner": "officer-1",
        "project_name": "Coastal Resilience Pilot",
        "year": 2025,
        "progress": "Seawall repairs reached 70% of the planned length. Community planting days were held in four villages.",
        "results": "About 12 hectares of flood-prone land are now better protected. 340 households have an early-warning contact.",
        "challenges": "Heavy rains delayed construction by six weeks.",
        "priorities": "Finish the remaining seawall sections and start maintenance training.",
        "activity": [
            _entry("Submitted", "officer-1", 11, 14, 10, 42),
        ],
    },
    {
        "id": 2,
        "owner": "officer-1",
        "project_name": "Solar Irrigation Scheme",
        "year": 2025,
        "progress": "Pumps were installed on 18 of 25 farms. Farmer training sessions were completed in two districts.",
        "results": "Water pumped per day increased on all connected farms.",
        "challenges": "Delivery of solar panels arrived late.",
        "priorities": "Connect the remaining farms and agree a maintenance schedule.",
        "activity": [
            _entry("Submitted", "officer-1", 11, 3, 9, 15),
            _entry("Returned", "manager-1", 11, 12, 15, 5,
                   "Please add results against the original targets."),
        ],
    },
    {
        "id": 3,
        "owner": "officer-1",
        "project_name": "Mangrove Restoration",
        "year": 2025,
        "progress": "Two nurseries produced 40,000 seedlings. Planting is complete on three of four sites.",
        "results": "Seedling survival rate measured at 78% after twelve months.",
        "challenges": "Storm damage affected one nursery for three weeks.",
        "priorities": "Plant the final site and begin the monitoring phase.",
        "activity": [
            _entry("Submitted", "officer-1", 10, 28, 11, 20),
            _entry("Returned", "manager-1", 10, 31, 14, 10,
                   "Please clarify how survival rates were measured."),
            _entry("Resubmitted", "officer-1", 11, 3, 16, 45),
            _entry("Approved", "manager-1", 11, 5, 9, 30,
                   "Thank you for the clear update."),
        ],
    },
    {
        "id": 4,
        "owner": "officer-2",
        "project_name": "Wetland Monitoring Network",
        "year": 2025,
        "progress": "Twelve monitoring stations were installed and are reporting data each month.",
        "results": "A first baseline of water quality readings is now available.",
        "challenges": "Two stations needed new sensors after flooding.",
        "priorities": "Extend the network to the northern catchment.",
        "activity": [
            _entry("Submitted", "officer-2", 11, 13, 16, 20),
        ],
    },
    {
        "id": 5,
        "owner": "officer-2",
        "project_name": "Urban Heat Adaptation",
        "year": 2025,
        "progress": "Shade structures were built at six bus stops and two market squares.",
        "results": "Surface temperatures at shaded sites were recorded as lower than at unshaded sites.",
        "challenges": "Permits for tree planting took longer than expected.",
        "priorities": "Plant trees along two main roads and publish a short guide for other towns.",
        "activity": [
            _entry("Submitted", "officer-2", 11, 1, 10, 0),
            _entry("Returned", "manager-1", 11, 6, 11, 30,
                   "Please explain the change in the tree-planting schedule."),
            _entry("Resubmitted", "officer-2", 11, 17, 11, 5),
        ],
    },
]


def _enrich(report):
    """Add the derived fields the templates use."""
    activity = report["activity"]
    for item in activity:
        person = USERS[item["user"]]
        item["name"], item["role"] = person["name"], person["role"]
    report["title"] = f'{report["project_name"]}, APR {report["year"]}'
    report["owner_name"] = USERS[report["owner"]]["name"]
    report["status"] = _STATUS_AFTER[activity[-1]["action"]]
    report["updated"] = activity[-1]["at"]
    report["submitted_at"] = [
        a["at"] for a in activity if a["action"] in ("Submitted", "Resubmitted")
    ][-1]
    report["returns"] = [a for a in activity if a["action"] == "Returned"]
    report["decision"] = activity[-1] if report["status"] != "Submitted" else None
    report["timeline"] = list(reversed(activity))


for _report in REPORTS:
    _enrich(_report)


def get_report(report_id):
    return next((r for r in REPORTS if r["id"] == report_id), None)


def visible_reports(owner_id=None):
    """Reports for one owner, or all reports when owner_id is None; newest first."""
    reports = [r for r in REPORTS if owner_id in (None, r["owner"])]
    return sorted(reports, key=lambda r: r["updated"], reverse=True)


def status_counts(reports):
    return {s: sum(r["status"] == s for r in reports) for s in STATUSES}
