import pymupdf
from PIL import Image
from io import BytesIO
import pytesseract


PDF_PATH = "group_6.pdf"
PAGE_NUMBER = 8

document = pymupdf.open(PDF_PATH)
page = document[PAGE_NUMBER - 1]

# Render at 3x
pixmap = page.get_pixmap(
    matrix=pymupdf.Matrix(3, 3)
)
image_bytes = pixmap.tobytes("png")
image = Image.open(BytesIO(image_bytes))

for psm in [3, 6, 11]:

    print("\n" + "=" * 60)
    print(f"PSM {psm}")
    print("=" * 60)

    text = pytesseract.image_to_string(
        image,
        config=f"--psm {psm}"
    )

    print(text.strip())

document.close()