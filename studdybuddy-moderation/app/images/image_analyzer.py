
import base64
import mimetypes
import os

import requests


LLM_URL = os.getenv(
    "SMOLVLM_API_URL",
    "http://127.0.0.1:8081/v1/chat/completions",
)

SMOLVLM_API_KEY = os.getenv("GATEWAY_API_KEY", "")

MODEL_NAME = "SmolVLM2-2.2B-Instruct"

IMAGE_ANALYSIS_PROMPT = """
Analyze this image for an educational content moderation system.

Describe only what is visibly present.

Include:
- Main objects, people, scenes, and activities.
- Visible text, labels, captions, signs, or symbols.
- Any visible violence, weapons, drugs, sexual content, injuries,
  extremist symbols, hate-related content, or other potentially harmful
  material.
- Whether the image appears to be a diagram, chart, textbook material,
  instructional material, scientific/technical material, historical
  material, advertisement, product image, screenshot, or photograph.

Do not decide whether the image should be approved or rejected.
Do not invent context or infer facts that cannot reasonably be seen.

Your output will be passed to a separate text moderation model.
""".strip()


def analyze_image(image_path: str) -> str:
    """
    Analyze an image using the configured SmolVLM2 server.

    Returns:
        A textual description of the image.

    Raises:
        ValueError: If the file is not a supported image type.
        FileNotFoundError: If the image does not exist.
        requests.RequestException: If the vision server request fails.
        KeyError: If the server response has an unexpected structure.
    """
    mime_type, _ = mimetypes.guess_type(image_path)

    if not mime_type or not mime_type.startswith("image/"):
        raise ValueError(f"Unsupported image type: {mime_type}")

    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    image_data_url = (
        f"data:{mime_type};base64,{image_base64}"
    )

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": IMAGE_ANALYSIS_PROMPT,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data_url,
                        },
                    },
                ],
            }
        ],
        "temperature": 0.1,
        "max_tokens": 500,
    }

    headers = {}

    if SMOLVLM_API_KEY:
        headers["Authorization"] = f"Bearer {SMOLVLM_API_KEY}"

    response = requests.post(
        LLM_URL,
        json=payload,
        headers=headers,
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"].strip()
