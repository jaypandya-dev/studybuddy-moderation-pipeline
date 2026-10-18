import time

from app.pdf_extractor import extract_text


PDF_PATH = "../ML.pdf"
def test_real_ml_pdf_extraction():

    with open(PDF_PATH, "rb") as f:
        file_bytes = f.read()

    start = time.time()

    result = extract_text(file_bytes)

    elapsed = time.time() - start

    print("\n========== EXTRACTION TEST ==========")
    print(f"Pages:              {result['page_count']}")
    print(f"Pages with PDF text: {result['pages_with_text']}")
    print(f"Pages using OCR:     {result['pages_ocr']}")
    print(f"Characters:          {result['character_count']}")
    print(f"Chunks:              {len(result['chunks'])}")
    print(f"Time:                {elapsed:.2f} seconds")
    print("=====================================\n")

    assert result["page_count"] == 741
    assert result["character_count"] > 0
    assert len(result["chunks"]) > 0