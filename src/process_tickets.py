import json
from pathlib import Path

from src.ticket_model import SupportTicket
from src.triage_engine import triage_ticket


# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "tickets.json"
OUTPUT_FILE = BASE_DIR / "output" / "triage_results.json"


def load_tickets():
    """Load support tickets from the JSON file."""

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        ticket_data = json.load(file)

    return [
        SupportTicket(**ticket)
        for ticket in ticket_data
    ]


def process_tickets():
    """Process every support ticket through the AI triage engine."""

    tickets = load_tickets()
    results = []

    print("\n" + "=" * 60)
    print("SUPPORT TICKET TRIAGE AGENT")
    print("=" * 60)

    print(f"\nLoaded {len(tickets)} support tickets.\n")

    for ticket in tickets:

        print("-" * 60)
        print(f"Processing Ticket: {ticket.ticket_id}")
        print(f"Subject: {ticket.subject}")

        try:
            result = triage_ticket(ticket)

            results.append(result.model_dump())

            print(f"Category: {result.category}")
            print(f"Urgency: {result.urgency}")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"Routing Team: {result.routing_team}")
            print(f"Human Review: {result.human_review}")
            print(f"Reasoning: {result.reasoning}")

        except Exception as error:
            print(f"ERROR processing {ticket.ticket_id}: {error}")

    # Save results
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)

    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)

    print(f"\nResults saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    process_tickets()