from app.images.image_moderation_service import moderate_image


IMAGE_PATH = r"F:\MCA\Mini project\propaganda-edu.png"


def test_moderate_image():
    result = moderate_image(IMAGE_PATH)

    print("\n--- FINAL IMAGE RESULT ---")
    print(result)

    assert result["decision"] in {
        "APPROVE",
        "REJECT",
    }

    assert "description" in result
    assert "ocr_text" in result
    assert "moderation" in result


if __name__ == "__main__":
    test_moderate_image()