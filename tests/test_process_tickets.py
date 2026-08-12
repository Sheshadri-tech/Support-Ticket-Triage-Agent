from src.ticket_model import TriageResult


def test_human_review_queue_only_contains_review_tickets():
    results = [
        TriageResult(
            ticket_id="T001",
            category="Account Access",
            urgency="High",
            confidence=0.9,
            routing_team="Account Support",
            human_review=False,
            reasoning="Clear account access issue."
        ),
        TriageResult(
            ticket_id="T005",
            category="Technical Issue",
            urgency="Low",
            confidence=0.4,
            routing_team="Technical Support",
            human_review=True,
            reasoning="Ticket is vague."
        )
    ]

    human_review_results = [
        result for result in results
        if result.human_review
    ]

    assert len(human_review_results) == 1
    assert human_review_results[0].ticket_id == "T005"
    assert human_review_results[0].human_review is True
    