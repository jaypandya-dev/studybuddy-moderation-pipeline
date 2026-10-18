from app.file_validator import validate_file
from app.moderation_service import moderate_pdf


PDF_PATH = "../Exillar.pdf"


def test_exillar_pdf_should_be_rejected():
    with open(PDF_PATH, "rb") as f:
        file_bytes = f.read()

    validation = validate_file(
        file_bytes=file_bytes,
        filename="Exillar.pdf",
        uploaded_mime_type="application/pdf",
    )

    print("\n========== EXILLAR VALIDATION ==========")
    print(validation)
    print("========================================")

    assert validation["valid"] is True
    assert validation["file_type"] == "pdf"

    result = moderate_pdf(file_bytes)

    print("\n========== EXILLAR MODERATION ==========")
    print("Decision:", result["decision"])
    print("Pages:", result["page_count"])
    print("Chunks:", len(result["chunks"]))

    for chunk in result["chunks"]:
        print(
            f"\nPage {chunk['page']} "
            f"Chunk {chunk['chunk']} "
            f"Role={chunk.get('page_role', 'content')}"
        )
        print("Moderation:", chunk["moderation"])
        print("Risk scan:", chunk["risk_scan"])

    print("========================================")

    assert result["decision"] == "REJECT"