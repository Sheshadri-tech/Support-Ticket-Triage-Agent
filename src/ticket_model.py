from pydantic import BaseModel, Field


class SupportTicket(BaseModel):
    ticket_id: str
    subject: str
    body: str


class TriageResult(BaseModel):
    ticket_id: str
    category: str
    urgency: str
    confidence: float = Field(ge=0.0, le=1.0)
    routing_team: str
    human_review: bool
    reasoning: str