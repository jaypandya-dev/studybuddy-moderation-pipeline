from app.images.image_analyzer import analyze_image
from app.chunk_moderation_service import moderate_chunk_with_risk_scan


IMAGE_PATH = r"F:\MCA\Mini project\nine_11.png"


def test_image_moderation_flow():
    description = analyze_image(IMAGE_PATH)

    result = moderate_chunk_with_risk_scan(description)

    print("\n--- IMAGE DESCRIPTION ---")
    print(description)

    print("\n--- MODERATION RESULT ---")
    print(result)

    assert result["decision"] in {"APPROVE", "REJECT", "IGNORE"}


if __name__ == "__main__":
    test_image_moderation_flow()