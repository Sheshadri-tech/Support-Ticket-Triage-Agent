from src.priority import calculate_priority


def test_low_urgency_priority():
    score, level = calculate_priority(
        urgency="Low",
        confidence=0.90,
        human_review=False
    )

    assert score == 20
    assert level == "Low"


def test_medium_urgency_priority():
    score, level = calculate_priority(
        urgency="Medium",
        confidence=0.90,
        human_review=False
    )

    assert score == 40
    assert level == "Medium"


def test_high_urgency_priority():
    score, level = calculate_priority(
        urgency="High",
        confidence=0.90,
        human_review=False
    )

    assert score == 70
    assert level == "High"


def test_critical_urgency_priority():
    score, level = calculate_priority(
        urgency="Critical",
        confidence=0.90,
        human_review=False
    )

    assert score == 90
    assert level == "Critical"


def test_low_confidence_increases_priority():
    score, level = calculate_priority(
        urgency="Low",
        confidence=0.40,
        human_review=False
    )

    assert score == 30
    assert level == "Low"


def test_human_review_increases_priority():
    score, level = calculate_priority(
        urgency="Low",
        confidence=0.90,
        human_review=True
    )

    assert score == 30
    assert level == "Low"


def test_low_confidence_and_human_review():
    score, level = calculate_priority(
        urgency="Low",
        confidence=0.40,
        human_review=True
    )

    assert score == 40
    assert level == "Medium"


def test_priority_score_cannot_exceed_100():
    score, level = calculate_priority(
        urgency="Critical",
        confidence=0.40,
        human_review=True
    )

    assert score == 100
    assert level == "Critical"


def test_unknown_urgency_defaults_to_low():
    score, level = calculate_priority(
        urgency="Unknown",
        confidence=0.90,
        human_review=False
    )

    assert score == 20
    assert level == "Low"