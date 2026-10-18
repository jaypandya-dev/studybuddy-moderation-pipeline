import time

from app.pdf_extractor import extract_text
from app.contextual_chunker import create_contextual_chunks
from app.llm_moderator import moderate_chunk


PDF_PATH = "../ML.pdf"


def test_real_pdf_primary_sample():
    with open(PDF_PATH, "rb") as f:
        file_bytes = f.read()

    extraction = extract_text(file_bytes)

    chunks = create_contextual_chunks(
        extraction["pages"],
        chunk_size=400,
        overlap=80,
        context_pages=1,
        min_page_chars=200,
    )

    total_chunks = len(chunks)

    # Spread samples across the complete document.
    sample_count = min(20, total_chunks)

    step = total_chunks / sample_count

    selected_indexes = [
        min(int(i * step), total_chunks - 1)
        for i in range(sample_count)
    ]

    # Remove duplicates while preserving order.
    selected_indexes = list(dict.fromkeys(selected_indexes))

    print("\n========== REAL PDF PRIMARY MODEL SAMPLE ==========")
    print(f"Total chunks: {total_chunks}")
    print(f"Sample chunks: {len(selected_indexes)}")
    print("===================================================")

    results = []

    start_time = time.time()

    for sample_number, index in enumerate(selected_indexes, start=1):
        chunk = chunks[index]

        chunk_start = time.time()

        result = moderate_chunk(chunk["text"])

        chunk_elapsed = time.time() - chunk_start

        results.append({
            "page": chunk["page"],
            "chunk": chunk["chunk"],
            "educational": result["educational"],
            "harmful": result["harmful"],
            "category": result["category"],
            "reason": result["reason"],
            "time": chunk_elapsed,
        })

        print(f"\n---------- SAMPLE {sample_number} ----------")
        print(f"Page: {chunk['page']}")
        print(f"Chunk: {chunk['chunk']}")
        print(f"Contextual: {chunk.get('contextual', False)}")
        print(f"Educational: {result['educational']}")
        print(f"Harmful: {result['harmful']}")
        print(f"Category: {result['category']}")
        print(f"Time: {chunk_elapsed:.2f}s")
        print(f"Reason: {result['reason']}")

    total_time = time.time() - start_time

    non_neutral = [
        result
        for result in results
        if result["category"] != "none"
    ]

    harmful = [
        result
        for result in results
        if result["harmful"]
    ]

    non_educational = [
        result
        for result in results
        if not result["educational"]
    ]

    print("\n========== SUMMARY ==========")
    print(f"Sampled chunks: {len(results)}")
    print(f"Total LLM time: {total_time:.2f}s")
    print(f"Average per chunk: {total_time / len(results):.2f}s")
    print(f"Non-none categories: {len(non_neutral)}")
    print(f"Harmful chunks: {len(harmful)}")
    print(f"Non-educational chunks: {len(non_educational)}")

    if non_neutral:
        print("\nNON-NONE CATEGORIES:")
        for result in non_neutral:
            print(
                f"Page {result['page']} "
                f"Chunk {result['chunk']} "
                f"→ {result['category']}"
            )

    print("============================\n")

    assert results