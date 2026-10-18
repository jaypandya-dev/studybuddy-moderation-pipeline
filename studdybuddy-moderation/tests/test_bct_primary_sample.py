import time

from app.pdf_extractor import extract_text
from app.contextual_chunker import create_contextual_chunks
from app.llm_moderator import moderate_chunk


PDF_PATH = "../BCT.pdf"


def test_bct_primary_sample():
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

    # Select representative ordinary chunks across the book.
    total = len(chunks)
    regular_indexes = [
        min(int(i * total / 12), total - 1)
        for i in range(12)
    ]

    # Also deliberately select contextual chunks.
    contextual_indexes = [
        index
        for index, chunk in enumerate(chunks)
        if chunk.get("contextual", False)
    ][:8]

    selected_indexes = list(
        dict.fromkeys(
            regular_indexes + contextual_indexes
        )
    )

    print("\n========== BCT PRIMARY MODEL SAMPLE ==========")
    print(f"Total chunks: {total}")
    print(f"Selected chunks: {len(selected_indexes)}")
    print("==============================================")

    results = []
    start_time = time.time()

    for number, index in enumerate(selected_indexes, start=1):
        chunk = chunks[index]

        chunk_start = time.time()

        result = moderate_chunk(chunk["text"])

        elapsed = time.time() - chunk_start

        results.append({
            "page": chunk["page"],
            "chunk": chunk["chunk"],
            "contextual": chunk.get("contextual", False),
            "source": chunk["source"],
            "educational": result["educational"],
            "harmful": result["harmful"],
            "category": result["category"],
            "reason": result["reason"],
            "time": elapsed,
        })

        print(f"\n---------- SAMPLE {number} ----------")
        print(f"Page: {chunk['page']}")
        print(f"Chunk: {chunk['chunk']}")
        print(f"Source: {chunk['source']}")
        print(f"Contextual: {chunk.get('contextual', False)}")
        print(f"Educational: {result['educational']}")
        print(f"Harmful: {result['harmful']}")
        print(f"Category: {result['category']}")
        print(f"Time: {elapsed:.2f}s")
        print(f"Reason: {result['reason']}")

    total_time = time.time() - start_time

    non_none = [
        r for r in results
        if r["category"] != "none"
    ]

    harmful = [
        r for r in results
        if r["harmful"]
    ]

    non_educational = [
        r for r in results
        if not r["educational"]
    ]

    contextual_results = [
        r for r in results
        if r["contextual"]
    ]

    print("\n========== SUMMARY ==========")
    print(f"Sampled chunks: {len(results)}")
    print(f"Contextual samples: {len(contextual_results)}")
    print(f"Total LLM time: {total_time:.2f}s")
    print(f"Average per chunk: {total_time / len(results):.2f}s")
    print(f"Non-none categories: {len(non_none)}")
    print(f"Harmful chunks: {len(harmful)}")
    print(f"Non-educational chunks: {len(non_educational)}")

    if non_none:
        print("\nNON-NONE CATEGORIES:")
        for r in non_none:
            print(
                f"Page {r['page']} "
                f"Chunk {r['chunk']} "
                f"→ {r['category']}"
            )

    print("============================\n")

    assert results