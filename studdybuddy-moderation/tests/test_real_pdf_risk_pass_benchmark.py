import time

from app.pdf_extractor import extract_text
from app.risk_prefilter import prefilter_risk
from app.llm_moderator import moderate_chunk


PDF_PATH = "../ML.pdf"


def test_real_pdf_risk_pass_benchmark():
    with open(PDF_PATH, "rb") as f:
        file_bytes = f.read()

    start = time.time()

    extraction = extract_text(file_bytes)
    chunks = extraction["chunks"]

    elapsed = time.time() - start

    prefilter_matches = 0
    category_candidates = 0
    estimated_second_passes = 0

    for chunk in chunks:
        text = chunk["text"]

        prefilter_result = prefilter_risk(text)

        if prefilter_result["risk_signal"]:
            prefilter_matches += 1

        # We cannot know the primary model's category without
        # actually calling it, so this benchmark reports the
        # prefilter-only lower bound.
        #
        # The real number of second passes may be higher because
        # the primary moderation model can identify suspicious
        # categories that the regex prefilter misses.
        if prefilter_result["risk_signal"]:
            estimated_second_passes += 1

    print("\n========== REAL PDF RISK PASS BENCHMARK ==========")
    print(f"Pages: {extraction['page_count']}")
    print(f"Chunks: {len(chunks)}")
    print(f"Extraction + chunking: {elapsed:.2f}s")
    print(f"Chunks with prefilter signal: {prefilter_matches}")
    print(f"Estimated second passes: {estimated_second_passes}")
    print(f"Primary-only chunks: {len(chunks) - estimated_second_passes}")
    print("=================================================\n")

    assert len(chunks) > 0