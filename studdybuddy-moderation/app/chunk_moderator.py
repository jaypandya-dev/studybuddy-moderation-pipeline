from app.llm_moderator import moderate_chunk


def moderate_chunks(chunks):
    """
    Moderate every chunk individually.

    Each chunk keeps its page number, chunk number,
    source, and moderation result.
    """

    results = []

    for chunk in chunks:

        moderation = moderate_chunk(chunk["text"])

        results.append({
            "page": chunk["page"],
            "chunk": chunk["chunk"],
            "source": chunk["source"],
            "text": chunk["text"],
            "moderation": moderation
        })

    return results