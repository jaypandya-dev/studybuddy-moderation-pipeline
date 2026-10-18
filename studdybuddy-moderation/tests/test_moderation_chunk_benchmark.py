import time

from app.pdf_extractor import extract_text
from app.contextual_chunker import create_contextual_chunks


PDF_PATH = "../ML.pdf"


def test_moderation_chunk_benchmark():
    with open(PDF_PATH, "rb") as f:
        file_bytes = f.read()

    extraction = extract_text(file_bytes)

    start = time.time()

    chunks = create_contextual_chunks(
        extraction["pages"],
        chunk_size=400,
        overlap=80,
        context_pages=1,
        min_page_chars=200,
    )

    elapsed = time.time() - start

    print("\n========== MODERATION CHUNK BENCHMARK ==========")
    print(f"Pages: {extraction['page_count']}")
    print(f"Characters: {extraction['character_count']}")
    print(f"Chunks at 400/80: {len(chunks)}")
    print(f"Chunking time: {elapsed:.2f}s")
    print("===============================================\n")

    assert len(chunks) > 0