from app.decision_engine import NON_CONTENT_ROLES


EDUCATIONAL_COVERAGE_THRESHOLD = 0.75


def decide_resource(
    chunk_results,
    educational_coverage_threshold=EDUCATIONAL_COVERAGE_THRESHOLD,
):
    processed_chunks = [
        {
            **chunk,
        }
        for chunk in chunk_results
    ]

    # ---------------------------------------------------------
    # SAFETY ALWAYS WINS
    # ---------------------------------------------------------
    # Even if 99% of the document is educational, one harmful
    # chunk must reject the entire resource.
    if any(
        chunk["moderation"]["harmful"]
        for chunk in processed_chunks
    ):
        return {
            "decision": "REJECT",
            "reason": "harmful_content_detected",
            "educational_chunks": 0,
            "non_educational_chunks": 0,
            "ignored_chunks": 0,
            "educational_coverage": 0.0,
            "chunks": processed_chunks,
        }

    # ---------------------------------------------------------
    # IGNORE NON-CONTENT PAGES
    # ---------------------------------------------------------

    substantive_chunks = [
        chunk
        for chunk in processed_chunks
        if chunk.get("page_role", "content")
        not in NON_CONTENT_ROLES
    ]

    ignored_chunks = (
        len(processed_chunks) - len(substantive_chunks)
    )

    # ---------------------------------------------------------
    # EDUCATIONAL VS NON-EDUCATIONAL
    # ---------------------------------------------------------

    educational_count = sum(
        1
        for chunk in substantive_chunks
        if chunk["moderation"]["educational"]
    )

    non_educational_count = (
        len(substantive_chunks) - educational_count
    )

    # No educational material at all.
    if educational_count == 0:
        return {
            "decision": "REJECT",
            "reason": "no_educational_content",
            "educational_chunks": 0,
            "non_educational_chunks": non_educational_count,
            "ignored_chunks": ignored_chunks,
            "educational_coverage": 0.0,
            "chunks": processed_chunks,
        }

    # ---------------------------------------------------------
    # EDUCATIONAL COVERAGE
    # ---------------------------------------------------------

    substantive_count = (
        educational_count + non_educational_count
    )

    educational_coverage = (
        educational_count / substantive_count
    )

    if educational_coverage >= educational_coverage_threshold:
        resource_decision = "APPROVE"
        reason = "sufficient_educational_coverage"
    else:
        resource_decision = "REJECT"
        reason = "insufficient_educational_coverage"

    return {
        "decision": resource_decision,
        "reason": reason,
        "educational_chunks": educational_count,
        "non_educational_chunks": non_educational_count,
        "ignored_chunks": ignored_chunks,
        "educational_coverage": round(
            educational_coverage,
            4,
        ),
        "chunks": processed_chunks,
    }