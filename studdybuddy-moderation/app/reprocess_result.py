from app.result_storage import load_moderation_result
from app.resource_decision import decide_resource


def reprocess_moderation_result(job_id: str) -> dict:
    """
    Re-evaluate a previously completed moderation result.

    No PDF extraction, OCR, or LLM calls are performed.
    Only the current resource-level decision policy is applied.
    """
    result = load_moderation_result(job_id)

    if result is None:
        raise FileNotFoundError(
            f"No saved moderation result found for job {job_id}"
        )

    chunks = result.get("chunks", [])

    resource_result = decide_resource(chunks)

    return {
        "job_id": job_id,
        "previous_decision": result.get("decision"),
        "new_decision": resource_result["decision"],
        "reason": resource_result["reason"],
        "educational_chunks": resource_result["educational_chunks"],
        "non_educational_chunks": resource_result[
            "non_educational_chunks"
        ],
        "ignored_chunks": resource_result["ignored_chunks"],
        "educational_coverage": resource_result[
            "educational_coverage"
        ],
    }