import time

from app.pdf_extractor import extract_text
from app.chunk_moderation_service import moderate_chunk_with_risk_scan
from app.resource_decision import decide_resource


PDF_PATH = "../BCT.pdf"


def test_bct_pipeline_sample():
    with open(PDF_PATH, "rb") as f:
        file_bytes = f.read()

    start = time.time()

    extraction = extract_text(file_bytes)

    # Pick representative real pages.
    target_pages = {5, 40, 57, 404}

    selected_chunks = [
        chunk
        for chunk in extraction["chunks"]
        if chunk["page"] in target_pages
    ]

    print("\n========== BCT PIPELINE SAMPLE ==========")
    print(f"Total PDF pages: {extraction['page_count']}")
    print(f"Total chunks: {len(extraction['chunks'])}")
    print(f"Selected chunks: {len(selected_chunks)}")

    moderated_chunks = []

    for chunk in selected_chunks:
        result = moderate_chunk_with_risk_scan(
    chunk["text"],
    page_role=chunk.get("page_role", "content"),
)

        print("\n========================================")
        print(f"PAGE: {chunk['page']}")
        print(f"CHUNK: {chunk['chunk']}")
        print(f"ROLE: {chunk.get('page_role', 'content')}")
        print(f"SOURCE: {chunk['source']}")
        print(f"CONTEXTUAL: {chunk.get('contextual', False)}")

        print("\nMODERATION:")
        print(result["moderation"])

        print("\nRISK PREFILTER:")
        print(result["risk_prefilter"])

        print("\nRISK SCAN:")
        print(result["risk_scan"])

        print("\nFINAL DECISION:")
        print(result["decision"])

        moderated_chunks.append({
            **chunk,
            "moderation": result["moderation"],
            "risk_scan": result["risk_scan"],
        })

    resource_result = decide_resource(
        moderated_chunks
    )

    elapsed = time.time() - start

    print("\n========================================")
    print("RESOURCE DECISION:")
    print(resource_result["decision"])
    print(f"Total time: {elapsed:.2f}s")
    print("========================================\n")

    page_map = {
        chunk["page"]: chunk
        for chunk in moderated_chunks
    }

    # Page 5 is front matter.
    assert page_map[5]["moderation"]["decision"] == "IGNORE"

    # Page 40 is real educational content.
    assert page_map[40]["moderation"]["decision"] == "APPROVE"

    # Page 57 is real educational content with a diagram.
    assert page_map[57]["moderation"]["decision"] == "APPROVE"

    # Page 404 is references and should not reject the resource
    # merely because it is not substantive lesson content.
    assert page_map[404]["moderation"]["decision"] == "IGNORE"

    # The selected sample contains legitimate educational content,
    # so the sample-level decision should be APPROVE.
    assert resource_result["decision"] == "APPROVE"