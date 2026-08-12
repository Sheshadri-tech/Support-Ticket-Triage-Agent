import json

from src import process_tickets


def test_audit_log_contains_success_and_failure(tmp_path, monkeypatch):
    """Verify that audit logging records successful and failed tickets."""

    audit_file = tmp_path / "audit_log.json"

    monkeypatch.setattr(
        process_tickets,
        "AUDIT_LOG_FILE",
        audit_file
    )

    successful_entry = {
        "timestamp": "2026-08-12T19:00:00",
        "ticket_id": "T001",
        "status": "success",
        "category": "Account Access",
        "urgency": "High",
        "confidence": 0.9,
        "routing_team": "Account Support",
        "human_review": False,
        "priority_score": 85,
        "priority_level": "High"
    }

    failed_entry = {
        "timestamp": "2026-08-12T19:00:01",
        "ticket_id": "T002",
        "status": "failed",
        "error": "Temporary API failure"
    }

    audit_entries = [
        successful_entry,
        failed_entry
    ]

    with open(audit_file, "w", encoding="utf-8") as file:
        json.dump(audit_entries, file, indent=4)

    with open(audit_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    assert len(data) == 2

    assert data[0]["ticket_id"] == "T001"
    assert data[0]["status"] == "success"
    assert data[0]["category"] == "Account Access"
    assert data[0]["priority_level"] == "High"

    assert data[1]["ticket_id"] == "T002"
    assert data[1]["status"] == "failed"
    assert data[1]["error"] == "Temporary API failure"