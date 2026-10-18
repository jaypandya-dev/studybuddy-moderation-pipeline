
from app.pdf_extractor import extract_text
from app.chunk_moderation_service import moderate_chunk_with_risk_scan
from app.resource_decision import decide_resource


class ModerationCancelled(Exception):
    """Raised when a PDF moderation job is cancelled."""


def moderate_pdf(
    file_bytes: bytes,
    progress_callback=None,
    cancellation_check=None,
) -> dict:
    """
    Moderate a complete PDF, with optional cooperative cancellation.

    cancellation_check:
        Optional callable returning True when cancellation is requested.
        Cancellation is checked before extraction, between chunks, and
        before the final resource decision.
    """

    def check_cancelled():
        if cancellation_check is not None and cancellation_check():
            raise ModerationCancelled("MODERATION_CANCELLED")

    # 1. Extract text, OCR pages where necessary, and chunk.
    check_cancelled()
    extraction = extract_text(file_bytes)
    check_cancelled()

    chunks = extraction["chunks"]
    total_chunks = len(chunks)
    moderated_chunks = []

    # 2. Moderate every chunk.
    for processed_count, chunk in enumerate(chunks, start=1):
        check_cancelled()

        moderation_result = moderate_chunk_with_risk_scan(
            chunk["text"],
            page_role=chunk.get("page_role", "content"),
        )

        # Do not retain or report another chunk if cancellation arrived
        # while this chunk was being moderated.
        check_cancelled()

        moderated_chunks.append({
            "page": chunk["page"],
            "chunk": chunk["chunk"],
            "source": chunk["source"],
            "text": chunk["text"],
            "contextual": chunk.get("contextual", False),
            "page_role": chunk.get("page_role", "content"),
            "risk_prefilter": moderation_result["risk_prefilter"],
            "risk_scan": moderation_result["risk_scan"],
            "moderation": moderation_result["moderation"],
        })

        if progress_callback is not None:
            progress_callback(processed_count, total_chunks)

    # 3. Do not produce a final decision for a cancelled or partial job.
    check_cancelled()

    # 4. Aggregate chunk decisions into a resource decision.
    resource_result = decide_resource(moderated_chunks)

    check_cancelled()

    # 5. Return the complete moderation result.
    return {
        "decision": resource_result["decision"],
        "page_count": extraction["page_count"],
        "pages_with_text": extraction["pages_with_text"],
        "pages_ocr": extraction["pages_ocr"],
        "character_count": extraction["character_count"],
        "chunks": resource_result["chunks"],
    }
