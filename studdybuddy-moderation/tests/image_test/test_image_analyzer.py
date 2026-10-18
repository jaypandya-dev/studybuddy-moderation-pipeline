from app.images.image_analyzer import analyze_image

IMAGE_PATH = r"F:\MCA\Mini project\nine_11.png"


def test_analyze_image():
    description = analyze_image(IMAGE_PATH)

    assert description
    assert isinstance(description, str)

    print("\nImage description:")
    print(description)


if __name__ == "__main__":
    test_analyze_image()