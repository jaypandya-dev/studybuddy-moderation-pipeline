import pymupdf

from app.upload_moderation_service import validate_and_moderate_pdf


def create_test_pdf():
    document = pymupdf.open()

    page = document.new_page()

    page.insert_text(
        (50, 50),
        """
        Physics explains how objects move and interact with forces.
        Newton's laws provide a mathematical framework for understanding
        motion. The second law states that force equals mass multiplied
        by acceleration. These principles are fundamental to mechanics.
        """
    )

    pdf_bytes = document.tobytes()
    document.close()

    return pdf_bytes


def test_validate_and_moderate_pdf():
    pdf_bytes = create_test_pdf()

    result = validate_and_moderate_pdf(
        file_bytes=pdf_bytes,
        filename="physics.pdf",
        uploaded_mime_type="application/pdf"
    )

    print("\nVALIDATION:")
    print(result["validation"])

    print("\nFINAL DECISION:")
    print(result["decision"])

    assert result["validation"]["valid"] is True
    assert result["validation"]["file_type"] == "pdf"
    assert result["decision"] == "APPROVE"
    assert result["moderation"] is not None