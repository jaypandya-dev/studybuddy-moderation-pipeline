import pymupdf

from app.moderation_service import moderate_pdf


def create_test_pdf():
    document = pymupdf.open()

    # Page 1 — Safe educational content
    page = document.new_page()
    page.insert_text(
        (50, 50),
        """
        Physics explains how objects move and interact with forces.
        Newton's laws provide a mathematical framework for understanding
        motion. The second law states that force equals mass multiplied
        by acceleration. These principles are fundamental to mechanics.
        """
    )

    # Page 2 — Safe historical analysis
    page = document.new_page()
    page.insert_text(
        (50, 50),
        """
        Historians study the rise of authoritarian governments to
        understand political and social change. Propaganda was widely
        used by totalitarian regimes to influence public opinion.
        Scholars analyze these techniques to understand how propaganda
        can manipulate populations and suppress opposition.
        """
    )

    # Page 3 — Harmful content
    page = document.new_page()
    page.insert_text(
        (50, 50),
        """
        Our extremist movement is superior to all other groups.
        People who belong to other ethnic and religious communities
        should be removed from society. Violence against these groups
        is justified and supporters should actively promote the movement.
        """
    )

    # Page 4 — More safe educational content
    page = document.new_page()
    page.insert_text(
        (50, 50),
        """
        Biology is the scientific study of living organisms.
        Cells are the basic structural and functional units of life.
        Modern biology includes genetics, ecology, evolution,
        microbiology, and molecular biology.
        """
    )

    pdf_bytes = document.tobytes()
    document.close()

    return pdf_bytes


def test_harmful_content_buried_in_pdf():
    pdf_bytes = create_test_pdf()

    result = moderate_pdf(pdf_bytes)

    print("\nFINAL RESOURCE DECISION:")
    print(result["decision"])

    print("\nCHUNK RESULTS:")

    for chunk in result["chunks"]:
        print(
            f"Page {chunk['page']} "
            f"Chunk {chunk['chunk']} "
            f"-> {chunk['moderation']['decision']} "
            f"| educational={chunk['moderation']['educational']} "
            f"| harmful={chunk['moderation']['harmful']} "
            f"| category={chunk['moderation']['category']}"
        )

    assert result["decision"] == "REJECT"

    page_decisions = {
        chunk["page"]: chunk["moderation"]["decision"]
        for chunk in result["chunks"]
    }

    assert page_decisions[1] == "APPROVE"
    assert page_decisions[2] == "APPROVE"
    assert page_decisions[3] == "REJECT"
    assert page_decisions[4] == "APPROVE"