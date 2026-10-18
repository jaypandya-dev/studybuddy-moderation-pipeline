from app.pdf_extractor import extract_text
from app.contextual_chunker import create_contextual_chunks

PDF_PATH = "../ML.pdf"


def test_inspect_page_250_context():
    with open(PDF_PATH, "rb") as f:
        file_bytes = f.read()

    extraction = extract_text(file_bytes)

    contextual_chunks = create_contextual_chunks(
        extraction["pages"]
    )

    page_250 = [
        chunk
        for chunk in contextual_chunks
        if chunk["page"] == 250
    ]

    assert len(page_250) == 1

    chunk = page_250[0]

    print("\n========== PAGE 250 CONTEXT ==========")
    print("CONTEXTUAL:", chunk["contextual"])
    print("SOURCE:", chunk["source"])
    print("TEXT:")
    print(chunk["text"])
    print("======================================\n")