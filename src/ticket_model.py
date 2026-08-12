from typing import Literal

from pydantic import BaseModel, Field


class SupportTicket(BaseModel):
    ticket_id: str
    subject: str
    body: str


class TriageResult(BaseModel):
    ticket_id: str

    category: Literal[
        "Account Access",
        "Billing",
        "Technical Issue",
        "Product Question",
        "Feature Request",
        "Security",
        "Other"
    ]

    urgency: Literal[
        "Low",
        "Medium",
        "High",
        "Critical"
    ]

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )

    routing_team: Literal[
        "Account Support",
        "Billing Support",
        "Technical Support",
        "Product Support",
        "Security Team",
        "General Support"
    ]

    human_review: bool

    reasoning: str
    
    priority_score: int = 0
    priority_level: str = "Low"