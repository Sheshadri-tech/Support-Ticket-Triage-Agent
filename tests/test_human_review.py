import json

import pytest

from src import human_review


def test_add_review_metadata():
    ticket = {
        "ticket_id": "T005",
        "category": "Technical Issue",
        "urgency": "Medium",
        "confidence": 0.4,
        "routing_team": "Technical Support",
        "human_review": True,
        "priority_score": 60,
        "priority_level": "High",
        "reasoning": "The ticket is vague."
    }

    result = human_review.add_review_metadata(ticket.copy())

    assert result["review_status"] == "PENDING"
    assert result["review_reason"] == "Low confidence classification"
    assert result["reviewed_by"] is None
    assert result["reviewed_at"] is None


def test_get_pending_reviews(monkeypatch):
    queue = [
        {
            "ticket_id": "T005",
            "review_status": "PENDING"
        },
        {
            "ticket_id": "T006",
            "review_status": "APPROVED"
        },
        {
            "ticket_id": "T007",
            "review_status": "REJECTED"
        }
    ]

    monkeypatch.setattr(
        human_review,
        "load_review_queue",
        lambda: queue
    )

    pending = human_review.get_pending_reviews()

    assert len(pending) == 1
    assert pending[0]["ticket_id"] == "T005"


def test_approve_review(monkeypatch):
    queue = [
        {
            "ticket_id": "T005",
            "review_status": "PENDING",
            "reviewed_by": None,
            "reviewed_at": None
        }
    ]

    monkeypatch.setattr(
        human_review,
        "load_review_queue",
        lambda: queue
    )

    saved_queue = {}

    def mock_save_review_queue(updated_queue):
        saved_queue["queue"] = updated_queue

    monkeypatch.setattr(
        human_review,
        "save_review_queue",
        mock_save_review_queue
    )

    result = human_review.approve_review(
        "T005",
        "Support Agent"
    )

    assert result["ticket_id"] == "T005"
    assert result["review_status"] == "APPROVED"
    assert result["reviewed_by"] == "Support Agent"
    assert result["reviewed_at"] is not None

    assert saved_queue["queue"][0]["review_status"] == "APPROVED"


def test_reject_review(monkeypatch):
    queue = [
        {
            "ticket_id": "T005",
            "review_status": "PENDING",
            "reviewed_by": None,
            "reviewed_at": None
        }
    ]

    monkeypatch.setattr(
        human_review,
        "load_review_queue",
        lambda: queue
    )

    saved_queue = {}

    def mock_save_review_queue(updated_queue):
        saved_queue["queue"] = updated_queue

    monkeypatch.setattr(
        human_review,
        "save_review_queue",
        mock_save_review_queue
    )

    result = human_review.reject_review(
        "T005",
        "Support Agent"
    )

    assert result["ticket_id"] == "T005"
    assert result["review_status"] == "REJECTED"
    assert result["reviewed_by"] == "Support Agent"
    assert result["reviewed_at"] is not None

    assert saved_queue["queue"][0]["review_status"] == "REJECTED"


def test_approve_nonexistent_ticket(monkeypatch):
    monkeypatch.setattr(
        human_review,
        "load_review_queue",
        lambda: []
    )

    with pytest.raises(
        ValueError,
        match="was not found"
    ):
        human_review.approve_review(
            "T999",
            "Support Agent"
        )


def test_reject_nonexistent_ticket(monkeypatch):
    monkeypatch.setattr(
        human_review,
        "load_review_queue",
        lambda: []
    )

    with pytest.raises(
        ValueError,
        match="was not found"
    ):
        human_review.reject_review(
            "T999",
            "Support Agent"
        )