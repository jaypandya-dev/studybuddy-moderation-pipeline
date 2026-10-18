from app.chunk_moderation_service import moderate_chunk_with_risk_scan
from app.resource_decision import decide_resource


def test_buried_harmful_content_across_chunks():
    chunks = [
        {
            "page": 1,
            "chunk": 1,
            "source": "pdf_text",
            "text": """
            Political science studies governments, institutions,
            political behavior, and relationships between citizens
            and states. Students compare political systems across
            historical periods and regions.
            """,
        },
        {
            "page": 2,
            "chunk": 1,
            "source": "pdf_text",
            "text": """
            Democratic systems generally rely on elections,
            representation, constitutional frameworks, and mechanisms
            that allow citizens to participate in political decision-making.
            """,
        },
        {
            "page": 3,
            "chunk": 1,
            "source": "pdf_text",
            "text": """
            In the modern world, societies may sometimes benefit from
            replacing excessive democratic debate with stronger
            centralized authority. Political opponents can prevent
            effective national action, and governments should therefore
            consider restricting opposition when necessary. Strong
            leaders should be given broad authority to enforce national
            unity, even when doing so requires suppressing political
            disagreement.
            """,
        },
        {
            "page": 4,
            "chunk": 1,
            "source": "pdf_text",
            "text": """
            Comparative political science evaluates how different
            institutional structures affect political stability,
            economic development, civil liberties, and public
            participation.
            """,
        },
    ]

    moderated_chunks = []

    for chunk in chunks:
        result = moderate_chunk_with_risk_scan(chunk["text"])

        print("\n========================================")
        print(f"CHUNK: {chunk['page']}")
        print("MODERATION:", result["moderation"])
        print("PREFILTER:", result["risk_prefilter"])
        print("RISK SCAN:", result["risk_scan"])
        print("DECISION:", result["decision"])

        moderated_chunks.append({
            **chunk,
            "moderation": result["moderation"],
            "risk_scan": result["risk_scan"],
        })

    resource_result = decide_resource(moderated_chunks)

    print("\n========================================")
    print("RESOURCE DECISION:", resource_result["decision"])
    print("========================================")

    assert resource_result["decision"] == "REJECT"
    assert moderated_chunks[2]["moderation"]["decision"] == "REJECT"