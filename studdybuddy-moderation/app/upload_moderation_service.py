from app.file_validator import validate_file
from app.moderation_service import moderate_pdf


def validate_and_moderate_pdf(
    file_bytes: bytes,
    filename: str | None = None,
    uploaded_mime_type: str | None = None,
    max_file_size: int | None = None
) -> dict:

    # ---------------------------------------------
    # 1. Validate the uploaded file
    # ---------------------------------------------

    validation = validate_file(
        file_bytes=file_bytes,
        filename=filename,
        uploaded_mime_type=uploaded_mime_type,
        max_file_size=max_file_size
    )

    if not validation["valid"]:
        return {
            "validation": validation,
            "moderation": None,
            "decision": "REJECT"
        }

    # ---------------------------------------------
    # 2. Only PDFs go through PDF moderation
    # ---------------------------------------------

    if validation["file_type"] != "pdf":
        return {
            "validation": validation,
            "moderation": None,
            "decision": "UNSUPPORTED"
        }

    # ---------------------------------------------
    # 3. Run moderation
    # ---------------------------------------------

    moderation = moderate_pdf(file_bytes)

    return {
        "validation": validation,
        "moderation": moderation,
        "decision": moderation["decision"]
    }   