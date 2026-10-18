from app.contextual_chunker import create_contextual_chunks


def test_short_page_gets_context():

    pages = [
        {
            "page": 1,
            "text": (
                "Machine learning is the study of algorithms that learn "
                "from data. These algorithms identify patterns in data "
                "and use those patterns to make predictions or decisions. "
                "Machine learning is widely used in classification, "
                "regression, clustering, recommendation systems, and "
                "many other applications."
            ),
            "source": "pdf_text"
        },
        {
            "page": 2,
            "text": "FIG. 1.1 Machine learning workflow",
            "source": "ocr"
        },
        {
            "page": 3,
            "text": (
                "Training data is used to learn patterns that can be "
                "applied to new examples. A machine learning model "
                "typically learns parameters from training data and "
                "is then evaluated using appropriate performance "
                "measures. The process may involve preprocessing, "
                "training, validation, and testing."
            ),
            "source": "pdf_text"
        }
    ]

    chunks = create_contextual_chunks(
        pages,
        min_page_chars=100
    )

    contextual_chunks = [
        chunk
        for chunk in chunks
        if chunk.get("contextual") is True
    ]

    assert len(contextual_chunks) == 1

    text = contextual_chunks[0]["text"]

    assert "[Page 1]" in text
    assert "[Page 2]" in text
    assert "[Page 3]" in text