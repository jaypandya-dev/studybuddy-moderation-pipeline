from app.pdf_extractor import extract_text

PDF_PATH = "../ML.pdf"


def test_inspect_neighbors():
    with open(PDF_PATH, "rb") as f:
        file_bytes = f.read()

    extraction = extract_text(file_bytes)

    for page_number in [249, 250, 251]:
        page = next(
            page
            for page in extraction["pages"]
            if page["page"] == page_number
        )

        print(f"\n========== PAGE {page_number} ==========")
        print(f"SOURCE: {page['source']}")
        print(f"CHARACTERS: {page['character_count']}")
        print(page["text"])
        print("======================================")
