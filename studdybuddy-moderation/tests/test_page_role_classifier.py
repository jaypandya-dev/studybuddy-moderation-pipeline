from app.page_role_classifier import classify_page_role


def test_front_matter():
    assert classify_page_role(
        "Dedicated to\nMy Mother"
    ) == "front_matter"


def test_metadata():
    assert classify_page_role(
        "Copyright © 2022\nISBN: 978-93-89423-42-6\nAll Rights Reserved."
    ) == "metadata"


def test_references():
    assert classify_page_role(
        "References\n"
        "https://example.com/paper\n"
        "https://example.com/book"
    ) == "references"


def test_index():
    assert classify_page_role(
        "Index\n"
        "Bitcoin 25, 40, 72\n"
        "Blockchain 10, 25, 60"
    ) == "index"


def test_glossary():
    assert classify_page_role(
        "Glossary\n"
        "Blockchain: a distributed ledger"
    ) == "glossary"


def test_regular_content():
    assert classify_page_role(
        "1.5 Cryptography\n"
        "Cryptography is the science of secure communication."
    ) == "content"


def test_harmful_content_is_still_content():
    assert classify_page_role(
        "Instructions\n"
        "Use the vulnerability to gain unauthorized access."
    ) == "content"