import json

from src.ticket_model import SupportTicket
from src import triage_engine


class MockMessage:
    def __init__(self, content):
        self.content = content


class MockChoice:
    def __init__(self, content):
        self.message = MockMessage(content)


class MockResponse:
    def __init__(self, content):
        self.choices = [MockChoice(content)]


class MockCompletions:
    def create(self, **kwargs):
        return MockResponse(
            json.dumps({
                "category": "Account Access",
                "urgency": "High",
                "confidence": 0.90,
                "routing_team": "Account Support",
                "human_review": False,
                "reasoning": "The customer is unable to access their account."
            })
        )


class MockChat:
    def __init__(self):
        self.completions = MockCompletions()


class MockClient:
    def __init__(self):
        self.chat = MockChat()


def test_triage_ticket(monkeypatch):

    monkeypatch.setattr(
        triage_engine,
        "client",
        MockClient()
    )

    ticket = SupportTicket(
        ticket_id="T001",
        subject="Unable to login to my account",
        body="I cannot access my account."
    )

    result = triage_engine.triage_ticket(ticket)

    assert result.ticket_id == "T001"
    assert result.category == "Account Access"
    assert result.urgency == "High"
    assert result.confidence == 0.90
    assert result.routing_team == "Account Support"
    assert result.human_review is False