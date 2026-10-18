from app.chunk_moderator import moderate_chunks


chunks = [
    {
        "page": 1,
        "chunk": 1,
        "source": "pdf_text",
        "text": """
        Newton's laws of motion describe the relationship between
        forces and the motion of objects. This is a fundamental topic
        in undergraduate physics.
        """
    },

    {
        "page": 2,
        "chunk": 1,
        "source": "pdf_text",
        "text": """
        This chapter explains how university students can understand
        the history of political movements and analyze their influence
        on twentieth-century societies.
        """
    },

    {
        "page": 3,
        "chunk": 1,
        "source": "pdf_text",
        "text": """
        Visit Goa during the winter season. Popular destinations include
        beaches, restaurants, nightlife, and tourist attractions.
        """
    }
]


results = moderate_chunks(chunks)


for result in results:
    print("\n-----------------------------")
    print("Page:", result["page"])
    print("Chunk:", result["chunk"])
    print("Result:", result["moderation"])