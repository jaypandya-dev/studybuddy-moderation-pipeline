from PIL import Image
from app.ocr_service import ocr_image


image = Image.open("test_image.png")

text = ocr_image(image)

print("OCR RESULT:")
print(text)