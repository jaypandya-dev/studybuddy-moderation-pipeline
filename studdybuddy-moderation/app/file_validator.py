import filetype


ALLOWED_TYPES = {
    "pdf": [
        "application/pdf"
    ],
    "image": [
        "image/jpeg",
        "image/png",
        "image/webp"
    ],
    "video": [
        "video/mp4",
        "video/webm",
        "video/quicktime"
    ]
}


def get_category_from_mime(mime_type: str | None):
    """
    Return the StudyBuddy category for a supported MIME type.
    """

    if mime_type is None:
        return None

    for category, mime_types in ALLOWED_TYPES.items():
        if mime_type in mime_types:
            return category

    return None


def validate_file(
    file_bytes: bytes,
    filename: str | None = None,
    uploaded_mime_type: str | None = None,
    max_file_size: int | None = None
):
    """
    Validate an uploaded file using:

    1. File size, when a limit is configured
    2. Actual file signature / magic bytes
    3. Uploaded MIME type as supporting evidence
    4. Filename extension for mismatch detection

    The filename and uploaded MIME type are never trusted
    over the actual file contents.

    Args:
        file_bytes:
            Raw uploaded file bytes.

        filename:
            Original filename supplied by the uploader.

        uploaded_mime_type:
            MIME type supplied by the uploader/client.

        max_file_size:
            Optional maximum file size in bytes.
            If None, no application-level size limit is enforced.
    """

    # --------------------------------------------------
    # 1. File size check
    # --------------------------------------------------

    file_size = len(file_bytes)

    if file_size == 0:
        return {
            "valid": False,
            "file_type": None,
            "mime_type": None,
            "status": "invalid",
            "reason": "File is empty"
        }

    if max_file_size is not None and file_size > max_file_size:
        return {
            "valid": False,
            "file_type": None,
            "mime_type": None,
            "status": "invalid",
            "reason": "File exceeds the configured size limit"
        }

    # --------------------------------------------------
    # 2. Detect actual file type from file contents
    # --------------------------------------------------

    kind = filetype.guess(file_bytes)

    if kind is None:
        return {
            "valid": False,
            "file_type": None,
            "mime_type": None,
            "status": "unknown",
            "reason": "Unable to determine file type from file contents"
        }

    detected_mime = kind.mime

    # --------------------------------------------------
    # 3. Determine whether detected type is supported
    # --------------------------------------------------

    detected_category = get_category_from_mime(detected_mime)

    if detected_category is None:
        return {
            "valid": False,
            "file_type": None,
            "mime_type": detected_mime,
            "status": "unsupported",
            "reason": "File type is not supported"
        }

    # --------------------------------------------------
    # 4. Check uploaded MIME type for mismatch
    # --------------------------------------------------

    if uploaded_mime_type is not None:

        if uploaded_mime_type != detected_mime:
            return {
                "valid": False,
                "file_type": None,
                "mime_type": detected_mime,
                "status": "mismatch",
                "reason": (
                    "Uploaded MIME type does not match "
                    "actual file type"
                )
            }

    # --------------------------------------------------
    # 5. Check filename extension
    # --------------------------------------------------

    if filename is not None:

        extension = filename.lower().split(".")[-1]

        expected_extensions = {
            "pdf": ["pdf"],
            "image": ["jpg", "jpeg", "png", "webp"],
            "video": ["mp4", "webm", "mov"]
        }

        if extension not in expected_extensions[detected_category]:

            return {
                "valid": False,
                "file_type": None,
                "mime_type": detected_mime,
                "status": "mismatch",
                "reason": (
                    "Filename extension does not match "
                    "actual file type"
                )
            }

    # --------------------------------------------------
    # 6. Everything matches
    # --------------------------------------------------

    return {
        "valid": True,
        "file_type": detected_category,
        "mime_type": detected_mime,
        "status": "supported",
        "reason": "File type validated successfully"
    }