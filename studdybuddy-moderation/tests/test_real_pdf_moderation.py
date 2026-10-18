from app.pdf_extractor import extract_text
from app.chunk_moderation_service import moderate_chunk_with_risk_scan


PDF_PATH = "../ML.pdf"


def test_real_pdf_moderation():

    # ---------------------------------------------
    # 1. Extract the real textbook
    # ---------------------------------------------

    with open(PDF_PATH, "rb") as f:
        file_bytes = f.read()

    extraction = extract_text(file_bytes)

    chunks = extraction["chunks"]

    # ---------------------------------------------
    # 2. Select representative pages
    # ---------------------------------------------

    target_pages = [
        35,
        100,
        200,
        300,
        400,
        500,
        600
    ]

    selected = []

    # Pick one normal chunk from each target page
    for page_number in target_pages:

        page_chunks = [
            chunk
            for chunk in chunks
            if chunk["page"] == page_number
        ]

        if page_chunks:
            selected.append(page_chunks[0])

    # ---------------------------------------------
    # 3. Add OCR pages
    # ---------------------------------------------

    ocr_chunks = [
        chunk
        for chunk in chunks
        if chunk["source"] == "ocr"
        and chunk["page"] >= 35
    ]

    for chunk in ocr_chunks:
        if len(selected) >= 10:
            break

        if chunk["page"] not in {
            selected_chunk["page"]
            for selected_chunk in selected
        }:
            selected.append(chunk)

    # ---------------------------------------------
    # 4. Moderate selected chunks
    # ---------------------------------------------

    print("\n========== REAL PDF MODERATION ==========")

    results = []

    for chunk in selected[:10]:

        print(
            f"\nModerating page {chunk['page']} "
            f"(source={chunk['source']})..."
        )

        result = moderate_chunk_with_risk_scan(
            chunk["text"]
        )

        results.append({
            "page": chunk["page"],
            "source": chunk["source"],
            "result": result
        })

        moderation = result["moderation"]

        print(
            f"Decision:    {moderation['decision']}"
        )

        print(
            f"Educational: {moderation['educational']}"
        )

        print(
            f"Harmful:     {moderation['harmful']}"
        )

        print(
            f"Category:    {moderation['category']}"
        )

        print(
            f"Risk scan:   {result['risk_scan']['risk']}"
        )

    print("\n==========================================")

    # ---------------------------------------------
    # 5. Basic sanity checks
    # ---------------------------------------------

    assert len(results) > 0

    for item in results:

        moderation = item["result"]["moderation"]

        assert moderation["decision"] in {
            "APPROVE",
            "REJECT",
            "FLAG"
        }