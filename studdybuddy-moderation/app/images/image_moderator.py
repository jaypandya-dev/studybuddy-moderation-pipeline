import json
import os
import requests


LLM_URL = os.getenv(
    "QWEN_API_URL",
    "http://127.0.0.1:8080/v1/chat/completions",
)
LLM_API_KEY = os.getenv("GATEWAY_API_KEY", "")

MODEL_NAME = "Qwen3-4B-Instruct-2507"


IMAGE_SYSTEM_PROMPT = """
You are the image content moderation system for StudyBuddy, a university
educational platform.

Your task is to evaluate a textual description of an image and determine
whether the image itself is genuinely educational and whether it contains
harmful or inappropriate content.

StudyBuddy only allows resources that are genuinely educational and relevant
to academic learning.

An image is educational ONLY when its actual visible content presents,
explains, illustrates, documents, or teaches academic, scientific, technical,
historical, medical, mathematical, or instructional knowledge.

Educational image content can include:
- academic diagrams
- scientific illustrations
- mathematical figures
- programming or technical diagrams
- textbook-style illustrations
- maps, charts, graphs, and educational visualizations
- historical or documentary material presented for study
- medical or anatomy illustrations
- instructional screenshots or demonstrations
- professional or vocational training material

A safe, informative, technical-looking, or interesting image is NOT
automatically educational.

Do NOT classify an image as educational merely because:
- it could be useful to a student
- it could be discussed in a classroom
- someone could potentially use it for teaching
- it is related to software development
- it contains files, folders, software interfaces, or technical objects
- it is famous, important, or historically significant

For example:
- A programming tutorial screenshot showing code and instructional
  explanation can be educational.
- A screenshot of a file explorer containing project files is not educational.
- A normal photograph is not educational merely because it depicts something
  technically interesting.
- A textbook diagram, labeled scientific illustration, mathematical graph,
  instructional diagram, or clearly instructional screenshot can be educational.

Historical and documentary images require special care.

A historical or documentary image MAY be educational when the image itself,
its visible caption, labels, or surrounding visible context clearly presents
a historical subject for study or documentation.

For example:
- A historical photograph documenting a major event with an identifying
  caption can be educational.
- A documentary image illustrating a historical event can be educational.
- A random photograph of a historical location is not automatically
  educational merely because the location is historically significant.

Educational context does not automatically make harmful content acceptable.

Harmful content includes material that promotes, encourages, glorifies,
justifies, or meaningfully facilitates harmful or inappropriate activity.

Distinguish depiction or academic/documentary analysis from endorsement,
promotion, glorification, or actionable facilitation.

Examples:
- A historical photograph documenting a terrorist attack can be educational.
- An academic image explaining extremist propaganda can be educational.
- An extremist propaganda image promoting the ideology is harmful.
- A medical educational illustration involving sexual anatomy can be educational.
- Explicit sexual imagery intended for sexual content is harmful.
- A defensive cybersecurity diagram can be educational.
- An image providing actionable instructions for exploiting real systems
  is harmful.

The provided description may contain statements such as:
"no weapons", "does not contain extremist symbols", or
"there is no visible violence".

These statements are observations about the image and MUST NOT themselves be
treated as harmful content.

Evaluate only the actual image evidence provided in the description and OCR
text. Do not invent facts, intentions, context, course use, or educational
purpose that are not reasonably supported by the evidence.

Determine:
1. Whether the image is genuinely educational.
2. Whether the image contains harmful or inappropriate content.
3. The most appropriate category.

Categories:
none,
sexual,
hate,
extremism,
political_propaganda,
violence,
self_harm,
drugs,
fraud,
harassment,
dangerous_activity,
non_educational,
other

If harmful content is present, category must describe the harmful content
itself, even if the image is also non-educational.

Use non_educational when the image is not genuinely educational and is not
otherwise harmful.

Return ONLY valid JSON in exactly this format:

{
  "educational": true,
  "harmful": false,
  "category": "none",
  "reason": "One concise sentence."
}

Rules for the reason:
- exactly one sentence
- no more than 25 words
- explain the main reason for the classification
""".strip()


IMAGE_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "educational": {"type": "boolean"},
        "harmful": {"type": "boolean"},
        "category": {
            "type": "string",
            "enum": [
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
            ],
        },
        "reason": {"type": "string"},
    },
    "required": [
        "educational",
        "harmful",
        "category",
        "reason",
    ],
    "additionalProperties": False,
}


def moderate_image_description(
    description: str,
    ocr_text: str = "",
) -> dict:
    """
    Moderate image-derived text using Qwen through the model gateway.

    Args:
        description: Visual description produced by SmolVLM2.
        ocr_text: Text extracted from the image using OCR.

    Returns:
        Structured moderation result.
    """

    user_content = f"""
IMAGE VISUAL DESCRIPTION:
{description}

VISIBLE TEXT FROM OCR:
{ocr_text if ocr_text.strip() else "[No OCR text detected]"}

Evaluate the image based only on the provided evidence.
""".strip()

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": IMAGE_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_content,
            },
        ],
        "temperature": 0.1,
        "max_tokens": 250,
        "response_format": {
            "type": "json_schema",
            "schema": IMAGE_RESPONSE_SCHEMA,
        },
    }

    headers = {}
    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"

    response = requests.post(
        LLM_URL,
        json=payload,
        headers=headers,
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()
    content = data["choices"][0]["message"]["content"].strip()
    result = json.loads(content)

    # Normalize the category returned by the model.
    if result["harmful"]:
        if result["category"] in {"none", "non_educational"}:
            result["category"] = "other"
        elif not result["educational"]:
            result["category"] = "non_educational"
    else:
        result["category"] = "none"

# Preserve the original model decision for auditing.
    result["original_harmful"] = result["harmful"]

    return result


def verify_harmful_classification(
    description: str,
    ocr_text: str,
    original_result: dict,
) -> dict:
    """
    Independently verify a potentially harmful image classification.
    """

    verification_prompt = """
You are a second-stage content moderation reviewer for StudyBuddy.

Review the supplied image description, OCR text, and initial
moderation result.

Determine whether the available evidence clearly supports the
specific harmful classification.

Important rules:
- Negative warnings and discussion of risks are not automatically harmful.
- Health, medical, academic, and educational discussions are not hate speech
  merely because they mention danger or negative consequences.
- Do not infer harmful intent without supporting evidence.
- Distinguish actual harmful content from ordinary educational discussion.
- If evidence is ambiguous or insufficient, set uncertain to true.
- Do not assume that a lack of visible text proves an image is safe.

Return ONLY valid JSON in this format:
{
  "confirmed_harmful": false,
  "uncertain": false,
  "category": "none",
  "reason": "One concise sentence."
}
""".strip()

    user_content = f"""
IMAGE DESCRIPTION:
{description}

OCR TEXT:
{ocr_text or "[No OCR text detected]"}

INITIAL MODERATION RESULT:
{json.dumps(original_result, ensure_ascii=False)}
""".strip()

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": verification_prompt,
            },
            {
                "role": "user",
                "content": user_content,
            },
        ],
        "temperature": 0.0,
        "max_tokens": 150,
        "response_format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "confirmed_harmful": {"type": "boolean"},
                    "uncertain": {"type": "boolean"},
                    "category": {
                        "type": "string",
                        "enum": [
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
                            "other",
                        ],
                    },
                    "reason": {"type": "string"},
                },
                "required": [
                    "confirmed_harmful",
                    "uncertain",
                    "category",
                    "reason",
                ],
                "additionalProperties": False,
            },
        },
    }

    headers = {}
    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"

    response = requests.post(
        LLM_URL,
        json=payload,
        headers=headers,
        timeout=120,
    )
    response.raise_for_status()

    data = response.json()
    content = data["choices"][0]["message"]["content"].strip()
    verification = json.loads(content)

    if verification["uncertain"]:
        verification["confirmed_harmful"] = False

    return verification