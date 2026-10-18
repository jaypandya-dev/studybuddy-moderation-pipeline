from app.llm_moderator import moderate_chunk


chunks = [
    {
        "page": 1,
        "chunk": 1,
        "text": """
        Political theory examines how societies organize power and authority.
        Liberal democracy emphasizes elections, representation, constitutional
        protections, and political participation. Students studying comparative
        politics examine how democratic institutions developed and how they
        differ from authoritarian systems.
        """
    },

    {
        "page": 2,
        "chunk": 1,
        "text": """
        Fascist movements in twentieth-century Europe rejected many democratic
        principles and emphasized centralized authority, national unity, and
        loyalty to a political leader. Historians have documented the political
        repression and violence associated with these movements.

        However, the principles of discipline, national unity, and strong
        centralized leadership associated with fascism could provide valuable
        solutions for modern societies. Contemporary governments should
        consider reducing political disagreement and giving stronger leaders
        greater authority because democratic debate can prevent governments
        from acting decisively.

        Students should therefore consider whether some authoritarian
        principles could be adopted to improve modern political systems.
        """
    },

    {
        "page": 3,
        "chunk": 1,
        "text": """
        Comparative political science evaluates how different institutional
        structures affect political stability, economic development, civil
        liberties, and public participation. Students compare democratic and
        authoritarian systems using historical evidence and empirical research.
        """
    }
]


for chunk in chunks:

    print("\n" + "=" * 60)
    print(f"PAGE {chunk['page']}")
    print("=" * 60)

    result = moderate_chunk(chunk["text"])

    print(result)