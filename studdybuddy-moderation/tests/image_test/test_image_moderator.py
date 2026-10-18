from app.images.image_analyzer import analyze_image
from app.images.image_moderator import moderate_image_description


IMAGE_PATH = r"F:\MCA\Mini project\nine_11.png"


def test_image_moderator():
    description = analyze_image(IMAGE_PATH)

    result = moderate_image_description(description)

    print("\n--- DESCRIPTION ---")
    print(description)

    print("\n--- IMAGE MODERATION ---")
    print(result)

    assert result["category"] in {
        "none",
        "sexual",
        "hate",
        "extremism",
        "political_propaganda",
        "violence",
        "self_harm",
        "drugs",
        "fraud",
        "harassment",
        "dangerous_activity",
        "non_educational",
        "other",
    }


if __name__ == "__main__":
    test_image_moderator()