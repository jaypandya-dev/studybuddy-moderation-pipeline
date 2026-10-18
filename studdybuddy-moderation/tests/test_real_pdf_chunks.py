from app.pdf_extractor import extract_text


PDF_PATH = "../ML.pdf"


def test_inspect_real_pdf_chunks():

    with open(PDF_PATH, "rb") as f:
        file_bytes = f.read()

    result = extract_text(file_bytes)

    print("\n========== SAMPLE CHUNKS ==========")

    for chunk in result["chunks"][:10]:
        print("\n--------------------------------")
        print(
            f"Page: {chunk['page']} | "
            f"Chunk: {chunk['chunk']} | "
            f"Source: {chunk['source']}"
        )
        print(chunk["text"][:500])

    print("\n===================================")

    assert len(result["chunks"]) > 0