import pytest
from pydantic import ValidationError

from src.ticket_model import SupportTicket, TriageResult


def test_support_ticket_creation():
    ticket = SupportTicket(
        ticket_id="T001",
        subject="Unable to login",
        body="I cannot access my account."
    )

    assert ticket.ticket_id == "T001"
    assert ticket.subject == "Unable to login"
    assert ticket.body == "I cannot access my account."


def test_triage_result_creation():
    result = TriageResult(
        ticket_id="T001",
        category="Account Access",
        urgency="High",
        confidence=0.9,
        routing_team="Account Support",
        human_review=False,
        reasoning="The customer cannot access their account."
    )

    assert result.ticket_id == "T001"
    assert result.category == "Account Access"
    assert result.urgency == "High"
    assert result.confidence == 0.9
    assert result.routing_team == "Account Support"
    assert result.human_review is False


def test_confidence_range():
    result = TriageResult(
        ticket_id="T005",
        category="Technical Issue",
        urgency="Medium",
        confidence=0.4,
        routing_team="Technical Support",
        human_review=True,
        reasoning="The ticket is vague."
    )

    assert 0.0 <= result.confidence <= 1.0


def test_invalid_confidence_is_rejected():
    with pytest.raises(ValidationError):
        TriageResult(
            ticket_id="T001",
            category="Account Access",
            urgency="High",
            confidence=1.5,
            routing_team="Account Support",
            human_review=False,
            reasoning="Test"
        )