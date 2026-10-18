from app.llm_moderator import scan_chunk_risk, moderate_chunk
from app.decision_engine import decide
from app.risk_prefilter import prefilter_risk


def moderate_chunk_with_risk_scan(
    text: str,
    page_role: str = "content",
) -> dict:
    """
    Moderate one chunk.

    The page role is used only after the safety/model passes so that
    document metadata can be ignored for educational relevance, while
    harmful content is never ignored.
    """

    moderation_result = moderate_chunk(text)

    # Apply page-role-aware decision.
    final_result = decide(
        moderation_result,
        page_role=page_role,
    )

    prefilter_result = prefilter_risk(text)

    needs_second_pass = (
        prefilter_result["risk_signal"]
        or moderation_result["harmful"]
        or moderation_result["category"] not in {
            "none",
            "non_educational",
        }
    )

    risk_result = None

    if needs_second_pass:
        risk_result = scan_chunk_risk(text)

        if risk_result["risk"]:
            final_result["harmful"] = True
            final_result["category"] = risk_result["category"]
            final_result["decision"] = "REJECT"

    return {
        "risk_prefilter": prefilter_result,
        "risk_scan": risk_result,
        "moderation": final_result,
        "decision": final_result["decision"],
    }