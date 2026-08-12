from fastapi.testclient import TestClient
from unittest.mock import patch

from src.api import app
from src.ticket_model import TriageResult


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Support Ticket Triage Agent API"
    assert data["status"] == "running"
    assert data["version"] == "1.0.0"


def test_get_tickets():
    response = client.get("/tickets")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_get_reviews():
    response = client.get("/reviews")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_get_statistics():
    response = client.get("/statistics")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)

    assert "total_tickets" in data
    assert "average_confidence" in data
    assert "human_review_required" in data
    assert "categories" in data
    assert "urgency" in data
    assert "priority" in data


def test_triage_new_ticket():
    mock_result = TriageResult(
        ticket_id="TEST001",
        category="Billing",
        urgency="Medium",
        confidence=0.95,
        routing_team="Billing Support",
        human_review=False,
        reasoning="Test ticket classified as a billing issue.",
        priority_score=40,
        priority_level="Medium",
    )

    ticket = {
        "ticket_id": "TEST001",
        "subject": "I was charged twice",
        "body": "My account was charged twice for the same subscription.",
    }

    with patch(
        "src.api.triage_ticket",
        return_value=mock_result
    ):
        response = client.post(
            "/tickets/triage",
            json=ticket
        )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Ticket triaged successfully"

    result = data["result"]

    assert result["ticket_id"] == "TEST001"
    assert result["category"] == "Billing"
    assert result["urgency"] == "Medium"
    assert result["confidence"] == 0.95
    assert result["routing_team"] == "Billing Support"
    assert result["human_review"] is False
    assert result["priority_level"] == "Medium"
    
    
def test_approve_ticket_review():
    response = client.post(
        "/reviews/T005/approve?reviewer=human-agent"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Ticket review approved successfully"

    result = data["result"]

    assert result["ticket_id"] == "T005"
    assert result["review_status"] == "APPROVED"
    assert result["reviewed_by"] == "human-agent"
    assert result["reviewed_at"] is not None


def test_reject_ticket_review():
    response = client.post(
        "/reviews/T005/reject?reviewer=human-agent"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Ticket review rejected successfully"

    result = data["result"]

    assert result["ticket_id"] == "T005"
    assert result["review_status"] == "REJECTED"
    assert result["reviewed_by"] == "human-agent"
    assert result["reviewed_at"] is not None