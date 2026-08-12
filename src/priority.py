def calculate_priority(
    urgency: str,
    confidence: float,
    human_review: bool
) -> tuple[int, str]:
    """
    Calculate ticket priority based on urgency,
    AI confidence, and human-review requirement.
    """

    urgency_scores = {
        "Low": 20,
        "Medium": 40,
        "High": 70,
        "Critical": 90
    }

    score = urgency_scores.get(urgency, 20)

    # Low-confidence predictions need additional attention
    if confidence < 0.70:
        score += 10

    # Human review increases priority
    if human_review:
        score += 10

    # Keep score within 0-100
    score = min(score, 100)

    if score >= 80:
        priority_level = "Critical"
    elif score >= 60:
        priority_level = "High"
    elif score >= 40:
        priority_level = "Medium"
    else:
        priority_level = "Low"

    return score, priority_level
