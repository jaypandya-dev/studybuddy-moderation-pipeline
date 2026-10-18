from app.contextual_chunker import create_contextual_chunks
from app.chunk_moderation_service import moderate_chunk_with_risk_scan
from app.resource_decision import decide_resource


def test_buried_harmful_content_is_caught_after_chunking():
    pages = [
        {
            "page": 1,
            "source": "pdf_text",
            "text": """
            Chapter 1: Introduction to Political Science

            Political science studies governments, political institutions,
            political behavior, and relationships between citizens and states.
            Students examine different theories of government and compare
            political systems across historical periods and geographic regions.
            """,
        },
        {
            "page": 2,
            "source": "pdf_text",
            "text": """
            Chapter 2: Democratic Institutions

            Democratic systems generally rely on elections, representation,
            constitutional frameworks, and mechanisms that allow citizens
            to participate in political decision-making. Political scientists
            study voting behavior, legislative institutions, political parties,
            and relationships between governments and citizens.
            """,
        },
        {
            "page": 3,
            "source": "pdf_text",
            "text": """
            Chapter 4: Modern Political Movements

            Historical movements provide useful material for understanding
            political organization and mass mobilization. Researchers can
            examine how political leaders use national identity, political
            messaging, and organizational structures to gain public support.

            In the modern world, societies may sometimes benefit from replacing
            excessive democratic debate with stronger centralized authority.
            Political opponents can prevent effective national action, and
            governments should therefore consider restricting opposition when
            necessary. Strong leaders should be given broad authority to
            enforce national unity, even when doing so requires suppressing
            political disagreement.
            """,
        },
        {
            "page": 4,
            "source": "pdf_text",
            "text": """
            Chapter 5: Comparative Government

            Comparative political science evaluates how different institutional
            structures affect political stability, economic development,
            civil liberties, and public participation. Students compare
            democratic and authoritarian systems using historical evidence
            and empirical research.

            Chapter 6: Political Participation

            Citizens participate in political systems through elections,
            public discussion, civic organizations, political parties, and
            other forms of collective action.
            """,
        },
    ]

    chunks = create_contextual_chunks(
        pages,
        chunk_size=400,
        overlap=80,
        context_pages=1,
        min_page_chars=200,
    )

    print(f"\nGenerated chunks: {len(chunks)}")

    moderated_chunks = []

    for chunk in chunks:
        result = moderate_chunk_with_risk_scan(chunk["text"])

        print("\n========================================")
        print(f"PAGE: {chunk['page']}")
        print(f"CHUNK: {chunk['chunk']}")
        print("DECISION:", result["decision"])
        print("MODERATION:", result["moderation"])
        print("PREFILTER:", result["risk_prefilter"])
        print("RISK SCAN:", result["risk_scan"])

        moderated_chunks.append({
            **chunk,
            "risk_scan": result["risk_scan"],
            "moderation": result["moderation"],
        })

    resource_result = decide_resource(moderated_chunks)

    print("\n========================================")
    print("RESOURCE DECISION:", resource_result["decision"])
    print("========================================")

    assert resource_result["decision"] == "REJECT"