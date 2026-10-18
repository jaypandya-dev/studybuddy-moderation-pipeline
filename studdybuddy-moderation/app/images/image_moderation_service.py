from pathlib import Path

import pytesseract
from PIL import Image

from app.images.image_analyzer import analyze_image
from app.images.image_moderator import (
    moderate_image_description,
    verify_harmful_classification,
)

ALLOWED_IMAGE_TYPES = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


def extract_image_ocr(image_path: str) -> str:
    """
    Extract visible text from an image using Tesseract OCR.
    """
    image = Image.open(image_path)
    return pytesseract.image_to_string(image).strip()


def decide_image(moderation: dict) -> str:
    """
    Convert the image moderation result into the final decision.
    """

    if moderation["harmful"]:
        return "REJECT"

    if not moderation["educational"]:
        return "REJECT"

    return "APPROVE"


def moderate_image(image_path: str) -> dict:
    """
    Run the complete image moderation pipeline.

    Pipeline:
        Image
          -> SmolVLM2 visual analysis
          -> OCR
          -> Image-specific Qwen3 moderation
          -> final decision
    """

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    if path.suffix.lower() not in ALLOWED_IMAGE_TYPES:
        raise ValueError(
            f"Unsupported image type: {path.suffix}"
        )

    # Step 1: Visual analysis
    description = analyze_image(str(path))

    # Step 2: OCR
    ocr_text = extract_image_ocr(str(path))

    # Step 3: Image-specific moderation
    moderation = moderate_image_description(
        description=description,
        ocr_text=ocr_text,
    )

    # Step 4: Final decision
    # Step 4: Verify potentially harmful classifications
    verification = None

    if moderation["harmful"]:
        verification = verify_harmful_classification(
            description=description,
            ocr_text=ocr_text,
            original_result=moderation,
        )

        if verification["confirmed_harmful"]:
            moderation["harmful"] = True
            moderation["category"] = verification["category"]
        elif verification["uncertain"]:
            moderation["needs_review"] = True
            moderation["verification_reason"] = verification["reason"]
        else:
            moderation["harmful"] = False
            moderation["category"] = (
                "none" if moderation["educational"]
                else "non_educational"
            )
            moderation["verification_reason"] = verification["reason"]

    # Step 5: Final decision
    if moderation.get("needs_review"):
        decision = "REVIEW"
    else:
        decision = decide_image(moderation)

    return {
    "decision": decision,
    "description": description,
    "ocr_text": ocr_text,
    "moderation": moderation,
    "verification": verification,
}