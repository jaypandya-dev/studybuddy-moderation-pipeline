import pymupdf

from io import BytesIO

from PIL import Image

from app.contextual_chunker import create_contextual_chunks
from app.text_cleaner import clean_text
from app.ocr_service import ocr_image
from app.page_role_classifier import classify_page_role


MIN_EMBEDDED_TEXT_CHARS = 50


def extract_text(file_bytes: bytes):
    """
    Extract text from a PDF.

    Embedded PDF text is preferred when usable.
    OCR is used for pages where embedded text is missing or too short.

    Each page receives:
        - page number
        - extracted text
        - source
        - character count
        - page role

    Moderation chunks use:
        chunk_size = 400 words
        overlap = 80 words
    """

    document = pymupdf.open(
        stream=file_bytes,
        filetype="pdf"
    )

    pages = []

    pages_with_text = 0
    pages_ocr = 0

    for page_number, page in enumerate(document, start=1):

        raw_text = page.get_text()

        embedded_text = clean_text(raw_text)

        has_usable_embedded_text = (
            len(embedded_text) >= MIN_EMBEDDED_TEXT_CHARS
        )

        if has_usable_embedded_text:
            text = embedded_text
            source = "pdf_text"

            pages_with_text += 1

        else:
            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(3, 3)
            )

            image_bytes = pixmap.tobytes("png")

            image = Image.open(
                BytesIO(image_bytes)
            )

            ocr_text = ocr_image(image)

            text = clean_text(ocr_text)

            source = "ocr"

            pages_ocr += 1

        pages.append({
            "page": page_number,
            "text": text,
            "source": source,
            "character_count": len(text),
            "page_role": classify_page_role(text),
        })

    document.close()

    full_text = "\n".join(
        page["text"]
        for page in pages
        if page["text"]
    )

    # Moderation-specific chunking.
    chunks = create_contextual_chunks(
        pages,
        chunk_size=400,
        overlap=80,
        context_pages=1,
        min_page_chars=200,
    )

    return {
        "text": full_text,
        "page_count": len(pages),
        "pages_with_text": pages_with_text,
        "pages_ocr": pages_ocr,
        "character_count": len(full_text),
        "pages": pages,
        "chunks": chunks,
    }