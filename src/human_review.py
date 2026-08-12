import json
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

HUMAN_REVIEW_FILE = BASE_DIR / "output" / "human_review.json"


def load_review_queue():
    """Load the human review queue."""

    if not HUMAN_REVIEW_FILE.exists():
        return []

    with open(
        HUMAN_REVIEW_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def save_review_queue(queue):
    """Save the human review queue."""

    HUMAN_REVIEW_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        HUMAN_REVIEW_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            queue,
            file,
            indent=4
        )


def get_pending_reviews():
    """Return all tickets that are still pending human review."""

    queue = load_review_queue()

    return [
        ticket
        for ticket in queue
        if ticket.get("review_status", "PENDING") == "PENDING"
    ]


def add_review_metadata(ticket):
    """Add human-review metadata to a triage result."""

    confidence = ticket.get("confidence", 1.0)

    if confidence < 0.70:
        review_reason = "Low confidence classification"
    elif ticket.get("human_review"):
        review_reason = "AI requested human review"
    else:
        review_reason = "Manual review required"

    ticket["review_status"] = "PENDING"
    ticket["review_reason"] = review_reason
    ticket["reviewed_by"] = None
    ticket["reviewed_at"] = None

    return ticket


def approve_review(ticket_id, reviewer):
    """Mark a human-review ticket as approved."""

    queue = load_review_queue()

    for ticket in queue:

        if ticket["ticket_id"] == ticket_id:

            ticket["review_status"] = "APPROVED"
            ticket["reviewed_by"] = reviewer
            ticket["reviewed_at"] = datetime.now().isoformat()

            save_review_queue(queue)

            return ticket

    raise ValueError(
        f"Ticket {ticket_id} was not found in the human review queue."
    )


def reject_review(ticket_id, reviewer):
    """Mark a human-review ticket as rejected."""

    queue = load_review_queue()

    for ticket in queue:

        if ticket["ticket_id"] == ticket_id:

            ticket["review_status"] = "REJECTED"
            ticket["reviewed_by"] = reviewer
            ticket["reviewed_at"] = datetime.now().isoformat()

            save_review_queue(queue)

            return ticket

    raise ValueError(
        f"Ticket {ticket_id} was not found in the human review queue."
    )