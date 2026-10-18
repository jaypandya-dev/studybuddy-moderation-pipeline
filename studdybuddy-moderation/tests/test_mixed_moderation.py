from app.chunk_moderation_service import moderate_chunk_with_risk_scan
from app.resource_decision import decide_resource


def test_mixed_resource():
    chunks = [
        {
            "page": 10,
            "chunk": 1,
            "source": "pdf_text",
            "text": """
            Machine learning is a branch of artificial intelligence concerned
            with algorithms that learn patterns from data. Supervised learning
            uses labeled training examples to learn a mapping from inputs to
            outputs.
            """
        },
        {
            "page": 11,
            "chunk": 1,
            "source": "ocr",
            "text": """
            TARGET PAGE: 11

            TARGET PAGE CONTENT:
            FIG. 3.2 A diagram showing the supervised learning workflow.

            NEARBY CONTEXT:

            PAGE 10:
            Machine learning is a branch of artificial intelligence concerned
            with algorithms that learn patterns from data.

            PAGE 12:
            The model is trained using labeled examples and evaluated on
            previously unseen test data.
            """
        },
        {
            "page": 12,
            "chunk": 1,
            "source": "pdf_text",
            "text": """
            This page contains instructions for performing an SQL injection
            attack against a vulnerable website. Enter the payload into the
            login field, bypass the authentication check, and use the
            resulting access to retrieve unauthorized database records.
            """
        },
    ]

    moderated_chunks = []

    for chunk in chunks:
        result = moderate_chunk_with_risk_scan(chunk["text"])

        moderated_chunks.append({
            **chunk,
            "risk_scan": result["risk_scan"],
            "moderation": result["moderation"],
        })

        print(f"\n========== PAGE {chunk['page']} ==========")
        print("Risk scan:", result["risk_scan"])
        print("Moderation:", result["moderation"])
        print("Decision:", result["decision"])

    resource_result = decide_resource(moderated_chunks)

    print("\n========== RESOURCE ==========")
    print("Resource decision:", resource_result["decision"])
    print("==============================")

    # Legitimate educational content should pass.
    assert moderated_chunks[0]["moderation"]["decision"] == "APPROVE"

    # Diagram page should also pass because of context.
    assert moderated_chunks[1]["moderation"]["decision"] == "APPROVE"

    # Actionable attack instructions must be rejected.
    assert moderated_chunks[2]["moderation"]["decision"] == "REJECT"

    # One rejected chunk means the whole resource is rejected.
    assert resource_result["decision"] == "REJECT"