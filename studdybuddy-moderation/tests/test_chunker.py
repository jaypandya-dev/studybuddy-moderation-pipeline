from app.text_chunker import chunk_text


text = """
This is a simple test document.
We are testing whether our text chunker correctly splits long text.
The chunks should overlap with each other.
This is important because our moderation system needs to inspect
the entire document without losing context between chunks.
""" * 20


chunks = chunk_text(
    text,
    chunk_size=50,
    overlap=10
)

print("Total chunks:", len(chunks))

for i, chunk in enumerate(chunks, start=1):
    words = len(chunk.split())

    print(f"\nChunk {i}")
    print(f"Words: {words}")
    print(chunk[:150], "...")