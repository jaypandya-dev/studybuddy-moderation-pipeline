from app.pdf_extractor import extract_text


PDF_PATH = "../BCT.pdf"


def test_bct_real_page_roles():
    with open(PDF_PATH, "rb") as f:
        file_bytes = f.read()

    extraction = extract_text(file_bytes)

    pages_to_check = [5, 40, 57, 404]

    print("\n========== BCT REAL PAGE ROLES ==========")

    for page_number in pages_to_check:
        page = next(
            page
            for page in extraction["pages"]
            if page["page"] == page_number
        )

        print(f"\nPAGE {page_number}")
        print(f"Source: {page['source']}")
        print(f"Characters: {page['character_count']}")
        print(f"Role: {page['page_role']}")
        print("Text preview:")
        print(page["text"][:500])

    print("\n==========================================")

    page_map = {
        page["page"]: page
        for page in extraction["pages"]
    }

    # Page 5 is front matter / dedication area.
    assert page_map[5]["page_role"] in {
        "front_matter",
        "metadata",
    }

    # Page 40 is substantive cryptography content.
    assert page_map[40]["page_role"] == "content"

    # Page 57 contains substantive blockchain content plus a diagram.
    assert page_map[57]["page_role"] == "content"

    # Page 404 is a reference page.
    assert page_map[404]["page_role"] == "references"