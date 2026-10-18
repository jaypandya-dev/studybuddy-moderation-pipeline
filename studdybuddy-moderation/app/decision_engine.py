NON_CONTENT_ROLES = {
    "front_matter",
    "metadata",
    "references",
    "index",
    "glossary",
}


def decide(
    result: dict,
    page_role: str = "content"
) -> dict:
    """
    Convert the moderation result into a chunk decision.

    Safety always takes priority.

    Harmful content:
        REJECT

    Supporting document material:
        IGNORE

    Genuine educational content:
        APPROVE

    Non-educational substantive content:
        REJECT
    """

    educational = result["educational"]
    harmful = result["harmful"]

    # Safety always wins.
    if harmful:
        result["decision"] = "REJECT"
        return result

    # Supporting document material does not determine whether the
    # overall resource is educational.
    if page_role in NON_CONTENT_ROLES:
        result["decision"] = "IGNORE"
        return result

    # Substantive content must actually be educational.
    if not educational:
        result["decision"] = "REJECT"
        return result

    result["decision"] = "APPROVE"

    return result