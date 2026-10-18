def chunk_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 100
):
    """
    Split text into overlapping chunks.

    chunk_size and overlap are measured in words.
    """

    words = text.split()

    if not words:
        return []

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size

        chunk_words = words[start:end]

        chunks.append(" ".join(chunk_words))

        if end >= len(words):
            break

        start = end - overlap

    return chunks

def chunk_pages(pages, chunk_size=800, overlap=100):
    """
    Chunk extracted PDF pages while preserving page numbers.
    """

    results = []

    for page in pages:
        page_number = page["page"]
        text = page["text"]

        chunks = chunk_text(
            text,
            chunk_size=chunk_size,
            overlap=overlap
        )

        for chunk_number, chunk in enumerate(chunks, start=1):
            results.append({
                "page": page_number,
                "chunk": chunk_number,
                "text": chunk,
                "source": page["source"]
            })

    return results