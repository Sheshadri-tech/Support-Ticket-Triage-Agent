import os
import json

from dotenv import load_dotenv
from groq import Groq

from src.ticket_model import SupportTicket, TriageResult


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is not found in the .env file.")


# ============================================================
# CREATE GROQ CLIENT
# ============================================================

client = Groq(api_key=api_key)


# ============================================================
# AI SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an expert Support Ticket Triage Agent.

Your job is to analyze customer support tickets and classify them.

For every ticket, determine:

1. category
2. urgency
3. confidence
4. routing_team
5. human_review
6. reasoning


CATEGORY OPTIONS:

- Account Access
- Billing
- Technical Issue
- Product Question
- Feature Request
- Security
- Other


URGENCY OPTIONS:

- Low
- Medium
- High
- Critical


ROUTING TEAM OPTIONS:

- Account Support
- Billing Support
- Technical Support
- Product Support
- Security Team
- General Support


RULES:

- Use the ticket subject and body together.
- Give a confidence score between 0 and 1.
- If the ticket is vague, ambiguous, or you are not sufficiently confident,
  set human_review to true.
- If confidence is below 0.70, set human_review to true.
- Critical security or account-compromise issues should receive high urgency.
- Payment failures, duplicate charges, and billing problems should normally
  go to Billing Support.
- Login and account-access problems should normally go to Account Support.
- Application errors and crashes should normally go to Technical Support.
- General product questions should normally go to Product Support.
- Feature suggestions should normally be classified as Feature Request.
- Do not invent information that is not present in the ticket.


Return ONLY valid JSON.

The JSON must contain exactly these fields:

{
    "category": "...",
    "urgency": "...",
    "confidence": 0.0,
    "routing_team": "...",
    "human_review": false,
    "reasoning": "..."
}
"""


# ============================================================
# TRIAGE A SINGLE SUPPORT TICKET
# ============================================================

def triage_ticket(ticket: SupportTicket) -> TriageResult:

    user_prompt = f"""
Analyze the following support ticket.

Ticket ID:
{ticket.ticket_id}

Subject:
{ticket.subject}

Body:
{ticket.body}

Return the triage result as JSON.
"""

    # ========================================================
    # SEND TICKET TO GROQ
    # ========================================================

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )

    # ========================================================
    # GET AI RESPONSE
    # ========================================================

    raw_response = response.choices[0].message.content

    if not raw_response:
        raise ValueError("AI returned an empty response.")

    raw_response = raw_response.strip()

    # ========================================================
    # CLEAN POSSIBLE MARKDOWN CODE FENCES
    # ========================================================

    if raw_response.startswith("```json"):
        raw_response = raw_response[7:]

    elif raw_response.startswith("```"):
        raw_response = raw_response[3:]

    if raw_response.endswith("```"):
        raw_response = raw_response[:-3]

    raw_response = raw_response.strip()

    # ========================================================
    # DEBUG OUTPUT
    # ========================================================

    print("\nRAW AI RESPONSE:")
    print(raw_response)

    # ========================================================
    # CONVERT JSON STRING TO PYTHON DICTIONARY
    # ========================================================

    try:
        result_data = json.loads(raw_response)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"AI returned invalid JSON: {error}\n"
            f"Raw response: {raw_response}"
        )

    # ========================================================
    # VALIDATE AI RESULT USING PYDANTIC
    # ========================================================

    # Enforce human review when confidence is low
    if result_data.get("confidence", 0.0) < 0.70:
        result_data["human_review"] = True

    result = TriageResult(
        ticket_id=ticket.ticket_id,
        **result_data
    )

    return result