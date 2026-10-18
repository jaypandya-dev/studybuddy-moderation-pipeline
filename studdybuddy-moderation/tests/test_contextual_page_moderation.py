from app.pdf_extractor import extract_text
from app.contextual_chunker import create_contextual_chunks
from app.chunk_moderation_service import moderate_chunk_with_risk_scan

PDF_PATH = "../ML.pdf"


def test_moderate_page_250_with_context():
    with open(PDF_PATH, "rb") as f:
        file_bytes = f.read()

    extraction = extract_text(file_bytes)

    contextual_chunks = create_contextual_chunks(
        extraction["pages"]
    )

    page_250 = next(
        chunk
        for chunk in contextual_chunks
        if chunk["page"] == 250
    )

    result = moderate_chunk_with_risk_scan(
        page_250["text"]
    )

    print("\n========== PAGE 250 MODERATION ==========")
    print("Risk scan:", result["risk_scan"])
    print("Moderation:", result["moderation"])
    print("Decision:", result["decision"])
    print("=========================================\n")