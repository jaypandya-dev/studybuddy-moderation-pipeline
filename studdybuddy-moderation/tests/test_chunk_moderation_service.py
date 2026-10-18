from unittest.mock import patch

from app.chunk_moderation_service import (
    moderate_chunk_with_risk_scan,
)
from app.risk_prefilter import prefilter_risk


def test_safe_content_has_no_risk_signal():
    result = prefilter_risk(
        "Machine learning uses training data to learn patterns."
    )

    assert result["risk_signal"] is False


def test_extremist_signal_is_detected():
    result = prefilter_risk(
        "The text promotes fascist principles as desirable."
    )

    assert result["risk_signal"] is True


def test_sql_injection_signal_is_detected():
    result = prefilter_risk(
        "The attacker uses SQL injection to bypass authentication."
    )

    assert result["risk_signal"] is True


def test_safe_content_uses_only_primary_llm():
    primary_result = {
        "educational": True,
        "harmful": False,
        "category": "none",
        "reason": "Normal educational content",
    }

    with patch(
        "app.chunk_moderation_service.moderate_chunk",
        return_value=primary_result,
    ), patch(
        "app.chunk_moderation_service.scan_chunk_risk",
    ) as mock_risk_scan:

        result = moderate_chunk_with_risk_scan(
            "Newton's laws describe the relationship between force and motion."
        )

        mock_risk_scan.assert_not_called()

        assert result["risk_scan"] is None
        assert result["decision"] == "APPROVE"


def test_risk_signal_triggers_second_llm_pass():
    primary_result = {
        "educational": True,
        "harmful": False,
        "category": "none",
        "reason": "Looks educational",
    }

    risk_result = {
        "risk": True,
        "category": "extremism",
        "evidence": "The text promotes extremist ideology.",
    }

    with patch(
        "app.chunk_moderation_service.moderate_chunk",
        return_value=primary_result,
    ), patch(
        "app.chunk_moderation_service.scan_chunk_risk",
        return_value=risk_result,
    ) as mock_risk_scan:

        result = moderate_chunk_with_risk_scan(
            "The text promotes fascist principles as desirable."
        )

        mock_risk_scan.assert_called_once()

        assert result["risk_scan"]["risk"] is True
        assert result["decision"] == "REJECT"
        assert result["moderation"]["category"] == "extremism"  