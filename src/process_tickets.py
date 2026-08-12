import json
from pathlib import Path
from datetime import datetime

from src.ticket_model import SupportTicket
from src.triage_engine import triage_ticket

from src.human_review import add_review_metadata

# ============================================================
# Project directories
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "tickets.json"

OUTPUT_FILE = BASE_DIR / "output" / "triage_results.json"

HUMAN_REVIEW_FILE = BASE_DIR / "output" / "human_review.json"

STATISTICS_FILE = BASE_DIR / "output" / "statistics.json"

AUDIT_LOG_FILE = BASE_DIR / "output" / "audit_log.json"


# ============================================================
# Load tickets
# ============================================================

def load_tickets():
    """Load support tickets from the JSON file."""

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        ticket_data = json.load(file)

    return [
        SupportTicket(**ticket)
        for ticket in ticket_data
    ]


# ============================================================
# Generate statistics
# ============================================================

def generate_statistics(results):
    """Generate operational statistics from triage results."""

    total = len(results)

    if total == 0:
        return {
            "total_tickets": 0,
            "average_confidence": 0,
            "human_review_required": 0,
            "categories": {},
            "urgency": {},
            "priority": {}
        }

    category_counts = {}
    urgency_counts = {}
    priority_counts = {}

    human_review_count = 0
    total_confidence = 0

    for result in results:

        category = result["category"]
        urgency = result["urgency"]
        priority = result["priority_level"]

        category_counts[category] = (
            category_counts.get(category, 0) + 1
        )

        urgency_counts[urgency] = (
            urgency_counts.get(urgency, 0) + 1
        )

        priority_counts[priority] = (
            priority_counts.get(priority, 0) + 1
        )

        total_confidence += result["confidence"]

        if result["human_review"]:
            human_review_count += 1

    average_confidence = total_confidence / total

    return {
        "total_tickets": total,
        "average_confidence": round(average_confidence, 2),
        "human_review_required": human_review_count,
        "categories": category_counts,
        "urgency": urgency_counts,
        "priority": priority_counts
    }


# ============================================================
# Process tickets
# ============================================================

def process_tickets():
    """Process every support ticket through the AI triage engine."""

    tickets = load_tickets()

    results = []

    human_review_queue = []

    audit_log = []

    # Processing statistics
    total_tickets = len(tickets)
    successful_tickets = 0
    failed_tickets = 0
    human_review_count = 0

    print("\n" + "=" * 60)
    print("SUPPORT TICKET TRIAGE AGENT")
    print("=" * 60)

    print(f"\nLoaded {total_tickets} support tickets.\n")

    # ========================================================
    # Process every ticket
    # ========================================================

    for ticket in tickets:

        print("-" * 60)
        print(f"Processing Ticket: {ticket.ticket_id}")
        print(f"Subject: {ticket.subject}")

        try:
            # Send ticket to AI triage engine
            result = triage_ticket(ticket)

            # Convert result to dictionary
            result_data = result.model_dump()

            # Save complete triage result
            results.append(result_data)

            successful_tickets += 1

            # Add tickets requiring human review
            if result.human_review:

                review_data = add_review_metadata(
                    result_data.copy()
                )

                human_review_queue.append(review_data)

                human_review_count += 1

            # =================================================
            # Create audit log entry
            # =================================================

            audit_entry = {
                "timestamp": datetime.now().isoformat(),
                "ticket_id": ticket.ticket_id,
                "status": "success",
                "category": result.category,
                "urgency": result.urgency,
                "confidence": result.confidence,
                "routing_team": result.routing_team,
                "human_review": result.human_review,
                "priority_score": result.priority_score,
                "priority_level": result.priority_level
            }

            audit_log.append(audit_entry)

            # Display result
            print(f"Category: {result.category}")
            print(f"Urgency: {result.urgency}")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"Routing Team: {result.routing_team}")
            print(f"Human Review: {result.human_review}")
            print(f"Priority Score: {result.priority_score}")
            print(f"Priority Level: {result.priority_level}")
            print(f"Reasoning: {result.reasoning}")

        except Exception as error:

            failed_tickets += 1

            # Record failed ticket in audit log
            audit_entry = {
                "timestamp": datetime.now().isoformat(),
                "ticket_id": ticket.ticket_id,
                "status": "failed",
                "error": str(error)
            }

            audit_log.append(audit_entry)

            print(
                f"ERROR processing "
                f"{ticket.ticket_id}: {error}"
            )

    # ========================================================
    # Create output directory
    # ========================================================

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # ========================================================
    # Save all triage results
    # ========================================================

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=4
        )

    # ========================================================
    # Save human review queue
    # ========================================================

    with open(
        HUMAN_REVIEW_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            human_review_queue,
            file,
            indent=4
        )

    # ========================================================
    # Generate statistics
    # ========================================================

    statistics = generate_statistics(results)

    # ========================================================
    # Save statistics
    # ========================================================

    with open(
        STATISTICS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            statistics,
            file,
            indent=4
        )

    # ========================================================
    # Save audit log
    # ========================================================

    with open(
        AUDIT_LOG_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            audit_log,
            file,
            indent=4
        )

    # ========================================================
    # Processing complete
    # ========================================================

    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)

    print("\nResults saved to:")
    print(OUTPUT_FILE)

    print("\nHuman review queue saved to:")
    print(HUMAN_REVIEW_FILE)

    print("\nStatistics saved to:")
    print(STATISTICS_FILE)

    print("\nAudit log saved to:")
    print(AUDIT_LOG_FILE)

    print(
        f"\nTickets requiring human review: "
        f"{human_review_count}"
    )

    # ========================================================
    # Processing summary
    # ========================================================

    print("\n" + "=" * 60)
    print("PROCESSING SUMMARY")
    print("=" * 60)

    print(f"Total tickets: {total_tickets}")
    print(f"Successfully processed: {successful_tickets}")
    print(f"Failed: {failed_tickets}")
    print(
        f"Human review required: "
        f"{human_review_count}"
    )

    # ========================================================
    # Ticket statistics
    # ========================================================

    print("\n" + "=" * 60)
    print("TICKET STATISTICS")
    print("=" * 60)

    print(
        f"Average confidence: "
        f"{statistics['average_confidence']:.2f}"
    )

    print("\nCategories:")

    for category, count in statistics["categories"].items():
        print(f"  {category}: {count}")

    print("\nUrgency:")

    for urgency, count in statistics["urgency"].items():
        print(f"  {urgency}: {count}")

    print("\nPriority:")

    for priority, count in statistics["priority"].items():
        print(f"  {priority}: {count}")


# ============================================================
# Program entry point
# ============================================================

if __name__ == "__main__":
    process_tickets()