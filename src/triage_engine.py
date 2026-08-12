import json
import time

from groq import Groq

from src.ticket_model import SupportTicket, TriageResult
from src.logger import logger
from src.config import GROQ_API_KEY, GROQ_MODEL, AI_TEMPERATURE

from src.priority import calculate_priority

# Create Groq client
client = Groq(api_key=GROQ_API_KEY)


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


def triage_ticket(ticket: SupportTicket) -> TriageResult:

    logger.info(
        f"Starting triage for ticket {ticket.ticket_id}"
    )

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

    logger.info(
        f"Sending ticket {ticket.ticket_id} to AI model"
    )

    # Retry configuration
    max_retries = 3

    # Retry loop
    for attempt in range(1, max_retries + 1):

        try:
            logger.info(
                f"AI request attempt {attempt}/{max_retries} "
                f"for ticket {ticket.ticket_id}"
            )

            response = client.chat.completions.create(
                model=GROQ_MODEL,
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
                temperature=AI_TEMPERATURE
            )

            logger.info(
                f"AI request successful for ticket "
                f"{ticket.ticket_id} on attempt {attempt}"
            )

            # API call succeeded
            break

        except Exception as e:

            logger.warning(
                f"AI request failed for ticket "
                f"{ticket.ticket_id} on attempt "
                f"{attempt}/{max_retries}: {e}"
            )

            # All retries exhausted
            if attempt == max_retries:

                logger.error(
                    f"AI request failed permanently for ticket "
                    f"{ticket.ticket_id} after "
                    f"{max_retries} attempts"
                )

                raise RuntimeError(
                    f"AI API request failed for ticket "
                    f"{ticket.ticket_id} after "
                    f"{max_retries} attempts: {e}"
                ) from e

            # Exponential backoff
            #
            # Attempt 1 fails -> wait 1 second
            # Attempt 2 fails -> wait 2 seconds
            delay = 2 ** (attempt - 1)

            logger.info(
                f"Waiting {delay} seconds before retrying "
                f"ticket {ticket.ticket_id}"
            )

            time.sleep(delay)

    # Get AI response
    raw_response = response.choices[0].message.content

    logger.info(
        f"AI response received for ticket {ticket.ticket_id}"
    )

    # Clean Markdown code fences if AI returns JSON
    # inside ```json ... ```
    raw_response = raw_response.strip()

    if raw_response.startswith("```json"):
        raw_response = raw_response[7:]

    if raw_response.startswith("```"):
        raw_response = raw_response[3:]

    if raw_response.endswith("```"):
        raw_response = raw_response[:-3]

    raw_response = raw_response.strip()

    # Check for empty response
    if not raw_response:
        raise ValueError(
            f"AI returned an empty response for ticket "
            f"{ticket.ticket_id}."
        )

    print("\nRAW AI RESPONSE:")
    print(raw_response)

    # Parse JSON
    try:
        result_data = json.loads(raw_response)

    except json.JSONDecodeError as e:
        raise ValueError(
            f"AI returned invalid JSON for ticket "
            f"{ticket.ticket_id}: {e}"
        ) from e

    # Check that the AI returned an object
    if not isinstance(result_data, dict):
        raise ValueError(
            f"AI response for ticket {ticket.ticket_id} "
            f"must be a JSON object."
        )

    # Validate required fields
    required_fields = {
        "category",
        "urgency",
        "confidence",
        "routing_team",
        "human_review",
        "reasoning"
    }

    missing_fields = required_fields - result_data.keys()

    if missing_fields:
        raise ValueError(
            f"AI response for ticket {ticket.ticket_id} "
            f"is missing fields: {sorted(missing_fields)}"
        )

    # Create validated Pydantic result
    try:
        priority_score, priority_level = calculate_priority(
            urgency=result_data["urgency"],
            confidence=result_data["confidence"],
            human_review=result_data["human_review"]
        )

        result = TriageResult(
            ticket_id=ticket.ticket_id,
            priority_score=priority_score,
            priority_level=priority_level,
            **result_data
        )

    except Exception as e:
        raise ValueError(
            f"AI response validation failed for ticket "
            f"{ticket.ticket_id}: {e}"
        ) from e

    logger.info(
        f"Triage completed for ticket {ticket.ticket_id}: "
        f"category={result.category}, "
        f"urgency={result.urgency}, "
        f"confidence={result.confidence}, "
        f"priority_score={result.priority_score}, "
        f"priority_level={result.priority_level}"
    )

    return result