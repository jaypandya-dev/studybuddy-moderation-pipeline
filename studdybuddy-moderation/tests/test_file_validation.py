import pymupdf

from app.file_validator import validate_file


def create_test_pdf():
    document = pymupdf.open()

    page = document.new_page()

    page.insert_text(
        (50, 50),
        "This is a valid educational PDF."
    )

    pdf_bytes = document.tobytes()
    document.close()

    return pdf_bytes


def test_valid_pdf():
    pdf_bytes = create_test_pdf()

    result = validate_file(
        file_bytes=pdf_bytes,
        filename="textbook.pdf",
        uploaded_mime_type="application/pdf"
    )

    assert result["valid"] is True
    assert result["file_type"] == "pdf"
    assert result["status"] == "supported"


def test_fake_pdf_extension():
    fake_pdf = b"This is not actually a PDF file."

    result = validate_file(
        file_bytes=fake_pdf,
        filename="textbook.pdf",
        uploaded_mime_type="application/pdf"
    )

    assert result["valid"] is False
    assert result["status"] == "unknown"


def test_wrong_mime_type():
    pdf_bytes = create_test_pdf()

    result = validate_file(
        file_bytes=pdf_bytes,
        filename="textbook.pdf",
        uploaded_mime_type="image/png"
    )

    assert result["valid"] is False
    assert result["status"] == "mismatch"


def test_empty_file():
    result = validate_file(
        file_bytes=b"",
        filename="empty.pdf",
        uploaded_mime_type="application/pdf"
    )

    assert result["valid"] is False
    assert result["status"] == "invalid"