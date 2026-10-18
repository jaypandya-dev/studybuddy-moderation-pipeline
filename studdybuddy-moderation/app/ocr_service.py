import pytesseract
from PIL import Image, ImageEnhance


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Prepare an image for OCR.
    """

    # Convert to grayscale
    image = image.convert("L")

    # Increase contrast
    image = ImageEnhance.Contrast(image).enhance(2.0)

    # Upscale the image
    width, height = image.size

    image = image.resize(
        (width * 2, height * 2),
        Image.Resampling.LANCZOS
    )

    return image


def ocr_image(image: Image.Image) -> str:
    """
    Extract text from a PIL image using Tesseract OCR.
    """

    image = preprocess_image(image)

    text = pytesseract.image_to_string(
        image,
        config="--psm 3"
    )

    return text.strip()