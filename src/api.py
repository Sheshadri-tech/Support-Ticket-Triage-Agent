import json
from pathlib import Path

from fastapi import FastAPI, HTTPException

from src.ticket_model import SupportTicket
from src.triage_engine import triage_ticket
from src.human_review import approve_review, reject_review


# ---------------------------------------------------------
# Project directories
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "output"

TRIAGE_RESULTS_FILE = OUTPUT_DIR / "triage_results.json"
HUMAN_REVIEW_FILE = OUTPUT_DIR / "human_review.json"
STATISTICS_FILE = OUTPUT_DIR / "statistics.json"


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="Support Ticket Triage Agent",
    description="AI-powered support ticket classification and triage API",
    version="1.0.0",
)


# ---------------------------------------------------------
# Helper function
# ---------------------------------------------------------

def load_json_file(file_path: Path):
    """Load JSON data from a file."""

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {file_path.name}"
        )

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid JSON data in {file_path.name}: {error}"
        )


# ---------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------

@app.get("/")
def root():
    """Health check endpoint."""

    return {
        "message": "Support Ticket Triage Agent API",
        "status": "running",
        "version": "1.0.0"
    }


# ---------------------------------------------------------
# Get all triage results
# ---------------------------------------------------------

@app.get("/tickets")
def get_tickets():
    """Return all processed ticket results."""

    return load_json_file(TRIAGE_RESULTS_FILE)


# ---------------------------------------------------------
# Get pending human reviews
# ---------------------------------------------------------

@app.get("/reviews")
def get_pending_reviews():
    """Return tickets waiting for human review."""

    reviews = load_json_file(HUMAN_REVIEW_FILE)

    return [
        review
        for review in reviews
        if review.get("review_status") == "PENDING"
    ]


# ---------------------------------------------------------
# Approve human review
# ---------------------------------------------------------

@app.post("/reviews/{ticket_id}/approve")
def approve_ticket_review(
    ticket_id: str,
    reviewer: str = "human-agent"
):
    """
    Approve a ticket after human review.
    """

    result = approve_review(
        ticket_id=ticket_id,
        reviewer=reviewer
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ticket {ticket_id} not found"
        )

    return {
        "message": "Ticket review approved successfully",
        "result": result
    }


# ---------------------------------------------------------
# Reject human review
# ---------------------------------------------------------

@app.post("/reviews/{ticket_id}/reject")
def reject_ticket_review(
    ticket_id: str,
    reviewer: str = "human-agent"
):
    """
    Reject a ticket after human review.
    """

    result = reject_review(
        ticket_id=ticket_id,
        reviewer=reviewer
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ticket {ticket_id} not found"
        )

    return {
        "message": "Ticket review rejected successfully",
        "result": result
    }


# ---------------------------------------------------------
# Get statistics
# ---------------------------------------------------------

@app.get("/statistics")
def get_statistics():
    """Return ticket processing statistics."""

    return load_json_file(STATISTICS_FILE)


# ---------------------------------------------------------
# Submit a new ticket for AI triage
# ---------------------------------------------------------

@app.post("/tickets/triage")
def triage_new_ticket(ticket: SupportTicket):
    """
    Submit a new support ticket to the AI triage engine.
    """

    try:
        result = triage_ticket(ticket)

        return {
            "message": "Ticket triaged successfully",
            "result": result.model_dump()
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Ticket triage failed: {error}"
        )

