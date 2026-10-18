import re


NON_CONTENT_ROLES = {
    "front_matter",
    "metadata",
    "references",
    "index",
    "glossary",
}


def _first_non_empty_line(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def classify_page_role(text: str) -> str:
    """
    Classify a PDF page into a coarse document role.

    This classifier is intentionally deterministic and conservative.
    It does not decide whether content is harmful or educational.

    Roles:
        - content
        - front_matter
        - metadata
        - references
        - index
        - glossary
    """

    if not text or not text.strip():
        return "metadata"

    normalized = text.lower().strip()
    first_line = _first_non_empty_line(normalized)

    # Strong section-heading signals.
    if re.match(r"^(references?|bibliography)\s*$", first_line):
        return "references"

    if re.match(r"^(index)\s*$", first_line):
        return "index"

    if re.match(r"^(glossary)\s*$", first_line):
        return "glossary"

    # Strong front-matter headings.
    front_matter_headings = {
        "dedicated to",
        "dedication",
        "about the author",
        "acknowledgements",
        "acknowledgments",
        "preface",
        "foreword",
        "table of contents",
        "contents",
    }

    if first_line in front_matter_headings:
        return "front_matter"

    # Copyright / publisher pages.
    metadata_patterns = [
        r"\bcopyright\b",
        r"\ball rights reserved\b",
        r"\bisbn\b",
        r"\bdisclaimer of warranty\b",
        r"\bpublished by\b",
        r"\bbpb publications\b",
    ]

    if any(re.search(pattern, normalized) for pattern in metadata_patterns):
        return "metadata"

    # Pages dominated by reference-style URLs.
    lines = [
        line.strip()
        for line in normalized.splitlines()
        if line.strip()
    ]

    if lines:
        url_count = sum(
            1 for line in lines
            if re.search(r"https?://|www\.", line)
        )

        if len(lines) >= 3 and url_count >= max(2, len(lines) // 3):
            return "references"

    return "content"