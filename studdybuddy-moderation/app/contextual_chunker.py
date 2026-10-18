from app.text_chunker import chunk_text


def create_contextual_chunks(
    pages,
    chunk_size=400,
    overlap=80,
    context_pages=1,
    min_page_chars=200
):
    """
    Create moderation chunks while preserving useful page context.

    Normal pages are chunked normally.

    Short / diagram-heavy pages receive nearby page context so that
    captions, graphs, figures, and image-heavy pages can be understood
    using surrounding educational material.
    """

    results = []

    for index, page in enumerate(pages):
        page_text = page["text"].strip()

        page_role = page.get("page_role", "content")

        # Normal text-heavy page.
        if len(page_text) >= min_page_chars:
            chunks = chunk_text(
                page_text,
                chunk_size=chunk_size,
                overlap=overlap
            )

            for chunk_number, chunk in enumerate(chunks, start=1):
                results.append({
                    "page": page["page"],
                    "chunk": chunk_number,
                    "text": chunk,
                    "source": page["source"],
                    "contextual": False,
                    "page_role": page_role,
                })

            continue

        # Short / diagram-heavy page.
        context_parts = []

        start = max(0, index - context_pages)
        end = min(len(pages), index + context_pages + 1)

        for context_index in range(start, end):
            if context_index == index:
                continue

            context_page = pages[context_index]
            context_text = context_page["text"].strip()

            if context_text:
                context_parts.append(
                    f"PAGE {context_page['page']}:\n"
                    f"{context_text}"
                )

        nearby_context = "\n\n".join(context_parts)

        contextual_text = (
            f"TARGET PAGE: {page['page']}\n\n"
            f"TARGET PAGE CONTENT:\n"
            f"{page_text}\n\n"
            f"NEARBY CONTEXT:\n\n"
            f"{nearby_context}"
        )

        results.append({
            "page": page["page"],
            "chunk": 1,
            "text": contextual_text,
            "source": page["source"],
            "contextual": True,
            "page_role": page_role,
        })

    return results