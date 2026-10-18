from app.decision_engine import decide


def test_non_educational():
    result = {
        "educational": False,
        "harmful": False,
        "category": "none",
        "decision": "APPROVE",
        "reason": "Travel guide"
    }

    result = decide(result)

    print(result)

    assert result["decision"] == "REJECT"
    assert result["category"] == "non_educational"


def test_harmful():
    result = {
        "educational": True,
        "harmful": True,
        "category": "extremism",
        "decision": "APPROVE",
        "reason": "Harmful content"
    }

    result = decide(result)

    print(result)

    assert result["decision"] == "REJECT"


def test_safe_educational():
    result = {
        "educational": True,
        "harmful": False,
        "category": "none",
        "decision": "REJECT",
        "reason": "Newton's laws"
    }

    result = decide(result)

    print(result)

    assert result["decision"] == "APPROVE"
    
if __name__ == "__main__":
    test_non_educational()
    test_harmful()
    test_safe_educational()

    print("\nAll tests passed!")