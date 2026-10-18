import time

from app.pdf_extractor import extract_text
from app.contextual_chunker import create_contextual_chunks


PDF_PATH = "../BCT.pdf"


def test_bct_chunk_benchmark():
    with open(PDF_PATH, "rb") as f:
        file_bytes = f.read()

    start = time.time()

    extraction = extract_text(file_bytes)

    chunks = create_contextual_chunks(
        extraction["pages"],
        chunk_size=400,
        overlap=80,
        context_pages=1,
        min_page_chars=200,
    )

    elapsed = time.time() - start

    contextual_count = sum(
        1 for chunk in chunks
        if chunk.get("contextual", False)
    )

    ocr_chunks = sum(
        1 for chunk in chunks
        if chunk["source"] == "ocr"
    )

    print("\n========== BCT PDF BENCHMARK ==========")
    print(f"Pages: {extraction['page_count']}")
    print(f"PDF text pages: {extraction['pages_with_text']}")
    print(f"OCR pages: {extraction['pages_ocr']}")
    print(f"Characters: {extraction['character_count']}")
    print(f"400/80 chunks: {len(chunks)}")
    print(f"Contextual chunks: {contextual_count}")
    print(f"OCR chunks: {ocr_chunks}")
    print(f"Extraction + chunking: {elapsed:.2f}s")
    print("=======================================\n")

    assert extraction["page_count"] == 691
    assert len(chunks) > 0