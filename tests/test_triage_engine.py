import pytest

from src.ticket_model import SupportTicket
from src import triage_engine


def test_triage_ticket(monkeypatch):

    ticket = SupportTicket(
        ticket_id="T001",
        subject="Unable to login",
        body="I cannot access my account."
    )

    class MockMessage:
        content = """
        {
            "category": "Account Access",
            "urgency": "High",
            "confidence": 0.9,
            "routing_team": "Account Support",
            "human_review": false,
            "reasoning": "The customer cannot access their account."
        }
        """

    class MockChoice:
        message = MockMessage()

    class MockResponse:
        choices = [MockChoice()]

    def mock_create(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(
        triage_engine.client.chat.completions,
        "create",
        mock_create
    )

    result = triage_engine.triage_ticket(ticket)

    assert result.ticket_id == "T001"
    assert result.category == "Account Access"
    assert result.urgency == "High"
    assert result.confidence == 0.9
    assert result.routing_team == "Account Support"
    assert result.human_review is False


def test_triage_ticket_with_markdown_json(monkeypatch):

    ticket = SupportTicket(
        ticket_id="T002",
        subject="Payment charged twice",
        body="I was charged twice for my subscription."
    )

    class MockMessage:
        content = """```json
{
    "category": "Billing",
    "urgency": "Medium",
    "confidence": 0.9,
    "routing_team": "Billing Support",
    "human_review": false,
    "reasoning": "The customer was charged twice."
}
```"""

    class MockChoice:
        message = MockMessage()

    class MockResponse:
        choices = [MockChoice()]

    def mock_create(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(
        triage_engine.client.chat.completions,
        "create",
        mock_create
    )

    result = triage_engine.triage_ticket(ticket)

    assert result.category == "Billing"
    assert result.routing_team == "Billing Support"

def test_empty_ai_response(monkeypatch):

    ticket = SupportTicket(
        ticket_id="T003",
        subject="Application error",
        body="The application is not working."
    )

    class MockMessage:
        content = ""

    class MockChoice:
        message = MockMessage()

    class MockResponse:
        choices = [MockChoice()]

    def mock_create(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(
        triage_engine.client.chat.completions,
        "create",
        mock_create
    )

    with pytest.raises(ValueError, match="empty response"):
        triage_engine.triage_ticket(ticket)


def test_invalid_json_response(monkeypatch):

    ticket = SupportTicket(
        ticket_id="T004",
        subject="Something is wrong",
        body="The application is not working."
    )

    class MockMessage:
        content = "This is not valid JSON."

    class MockChoice:
        message = MockMessage()

    class MockResponse:
        choices = [MockChoice()]

    def mock_create(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(
        triage_engine.client.chat.completions,
        "create",
        mock_create
    )

    with pytest.raises(ValueError, match="invalid JSON"):
        triage_engine.triage_ticket(ticket)
        
        
def test_api_retry_success(monkeypatch):

    ticket = SupportTicket(
        ticket_id="T999",
        subject="Unable to login",
        body="I cannot login to my account."
    )

    attempts = {"count": 0}

    class MockResponse:

        class Choice:

            class Message:
                content = """
                {
                    "category": "Account Access",
                    "urgency": "High",
                    "confidence": 0.9,
                    "routing_team": "Account Support",
                    "human_review": false,
                    "reasoning": "The customer cannot access their account."
                }
                """

            message = Message()

        choices = [Choice()]

    def mock_api_call(*args, **kwargs):

        attempts["count"] += 1

        # First two attempts fail
        if attempts["count"] < 3:
            raise Exception("Temporary API failure")

        # Third attempt succeeds
        return MockResponse()

    monkeypatch.setattr(
        triage_engine.client.chat.completions,
        "create",
        mock_api_call
    )

    result = triage_engine.triage_ticket(ticket)

    assert result.ticket_id == "T999"
    assert result.category == "Account Access"
    assert result.urgency == "High"
    assert result.confidence == 0.9
    assert result.routing_team == "Account Support"
    assert result.human_review is False

    # Verify that the API was called exactly 3 times
    assert attempts["count"] == 3
    


def test_api_retry_failure(monkeypatch):

    ticket = SupportTicket(
        ticket_id="T998",
        subject="Unable to login",
        body="I cannot login to my account."
    )

    attempts = {"count": 0}

    def mock_api_call(*args, **kwargs):

        attempts["count"] += 1

        # Every API attempt fails
        raise Exception("Permanent API failure")

    monkeypatch.setattr(
        triage_engine.client.chat.completions,
        "create",
        mock_api_call
    )

    with pytest.raises(
        RuntimeError,
        match="after 3 attempts"
    ):
        triage_engine.triage_ticket(ticket)

    # Verify that exactly 3 attempts were made
    assert attempts["count"] == 3
    
    


def test_api_retry_uses_exponential_backoff(monkeypatch):

    ticket = SupportTicket(
        ticket_id="T997",
        subject="Unable to login",
        body="I cannot login to my account."
    )

    attempts = {"count": 0}
    delays = []

    class MockResponse:

        class Choice:

            class Message:
                content = """
                {
                    "category": "Account Access",
                    "urgency": "High",
                    "confidence": 0.9,
                    "routing_team": "Account Support",
                    "human_review": false,
                    "reasoning": "The customer cannot access their account."
                }
                """

            message = Message()

        choices = [Choice()]

    def mock_api_call(*args, **kwargs):

        attempts["count"] += 1

        if attempts["count"] < 3:
            raise Exception("Temporary API failure")

        return MockResponse()

    def mock_sleep(seconds):
        delays.append(seconds)

    monkeypatch.setattr(
        triage_engine.client.chat.completions,
        "create",
        mock_api_call
    )

    monkeypatch.setattr(
        triage_engine.time,
        "sleep",
        mock_sleep
    )

    result = triage_engine.triage_ticket(ticket)

    assert result.ticket_id == "T997"
    assert result.category == "Account Access"

    assert attempts["count"] == 3

    # Verify exponential backoff:
    # first failure -> 1 second
    # second failure -> 2 seconds
    assert delays == [1, 2]