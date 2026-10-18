from app.resource_decision import decide_resource


def make_chunk(
    educational=True,
    harmful=False,
    page_role="content",
):
    return {
        "page": 1,
        "chunk": 1,
        "page_role": page_role,
        "moderation": {
            "educational": educational,
            "harmful": harmful,
            "category": (
                "none"
                if not harmful and educational
                else "non_educational"
            ),
            "reason": "test",
            "decision": "APPROVE" if educational else "REJECT",
        },
    }


def test_all_educational():
    chunks = [
        make_chunk(educational=True)
        for _ in range(10)
    ]

    result = decide_resource(chunks)

    assert result["decision"] == "APPROVE"
    assert result["educational_chunks"] == 10
    assert result["non_educational_chunks"] == 0
    assert result["educational_coverage"] == 1.0


def test_educational_with_some_non_educational():
    chunks = (
        [make_chunk(educational=True) for _ in range(10)]
        + [make_chunk(educational=False) for _ in range(3)]
    )

    result = decide_resource(chunks)

    assert result["decision"] == "APPROVE"
    assert result["educational_chunks"] == 10
    assert result["non_educational_chunks"] == 3


def test_mostly_non_educational():
    chunks = (
        [make_chunk(educational=True) for _ in range(3)]
        + [make_chunk(educational=False) for _ in range(10)]
    )

    result = decide_resource(chunks)

    assert result["decision"] == "REJECT"
    assert result["reason"] == "insufficient_educational_coverage"


def test_harmful_content_always_rejects():
    chunks = (
        [make_chunk(educational=True) for _ in range(10)]
        + [make_chunk(
            educational=True,
            harmful=True,
        )]
    )

    result = decide_resource(chunks)

    assert result["decision"] == "REJECT"
    assert result["reason"] == "harmful_content_detected"


def test_only_non_educational_content():
    chunks = [
        make_chunk(educational=False)
        for _ in range(5)
    ]

    result = decide_resource(chunks)

    assert result["decision"] == "REJECT"
    assert result["reason"] == "no_educational_content"


def test_non_content_pages_are_ignored():
    chunks = (
        [make_chunk(
            educational=False,
            page_role="metadata",
        ) for _ in range(5)]
        + [make_chunk(educational=True) for _ in range(5)]
    )

    result = decide_resource(chunks)

    assert result["decision"] == "APPROVE"
    assert result["ignored_chunks"] == 5
    assert result["educational_chunks"] == 5
    assert result["educational_coverage"] == 1.0


def test_harmful_content_on_ignored_page_still_rejects():
    chunks = [
        make_chunk(
            educational=False,
            harmful=True,
            page_role="metadata",
        ),
        make_chunk(educational=True),
        make_chunk(educational=True),
    ]

    result = decide_resource(chunks)

    assert result["decision"] == "REJECT"
    assert result["reason"] == "harmful_content_detected"