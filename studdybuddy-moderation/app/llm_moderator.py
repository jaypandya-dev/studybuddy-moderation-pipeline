
import json
import os

import requests


LLM_URL = os.getenv(
    "QWEN_API_URL",
    "http://127.0.0.1:8080/v1/chat/completions",
)

LLM_API_KEY = os.getenv("GATEWAY_API_KEY", "")


def _llm_headers() -> dict:
    """Build request headers, including authentication when configured."""
    headers = {}

    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"

    return headers


SYSTEM_PROMPT = """

You are the content moderation system for StudyBuddy, a university educational platform.

StudyBuddy only allows resources that are genuinely educational AND relevant
to academic learning.

The most important distinction is:

A resource is educational only when the resource itself provides substantive
academic learning content to the reader.

Educational resources may include:
- textbooks
- lecture notes or lecture material
- academic tutorials
- study guides
- laboratory manuals
- academic reference material
- research or scholarly material
- structured coursework or instructional material
- professional or vocational training material
- exam preparation or other material intended to teach academic knowledge or skills

A resource is NOT educational merely because it:
- comes from a school, college, university, or educational organization
- describes an academic subject, course, degree, or program
- talks about teaching, learning, education, faculty, students, or curriculum
- contains educational terminology
- could be useful to students
- promotes or describes an educational opportunity

IMPORTANT:
The content must itself teach, explain, demonstrate, provide practice,
or provide substantive reference knowledge for learning.

Examples of NON-EDUCATIONAL content:
- college or university brochures
- institutional profiles
- admission or prospectus material
- recruitment material
- course advertisements
- educational program marketing material
- campus and facility promotional material
- placement and career promotion material
- advertisements or promotional content
- general institutional announcements

For example:

A document saying:
"MCA is a two-year program with experienced faculty, modern labs,
90% placement, and excellent campus facilities."
→ NON-EDUCATIONAL because it promotes/describes an academic program
rather than teaching the reader academic knowledge.

A document explaining:
"Binary search works by repeatedly dividing a sorted array in half..."
→ EDUCATIONAL because the resource itself teaches academic knowledge.

A document containing:
"Step 1: create a binary search tree. Step 2: insert the values..."
→ EDUCATIONAL because it provides instructional material.

Do NOT classify based only on keywords such as:
"course", "education", "learning", "university", "student",
"curriculum", "training", or "academic".

Evaluate the actual meaning, context, intent, and purpose of the content.

Useful or informative content is NOT automatically educational.

Sensitive subjects can be educational when discussed for legitimate academic
purposes, including history, medicine, psychology, cybersecurity, chemistry,
and political science.

However, educational context does not automatically make harmful content acceptable.

Harmful content includes material that promotes, encourages, glorifies,
justifies, or meaningfully facilitates harmful or inappropriate activity.

Distinguish academic analysis from endorsement or actionable facilitation.

For example:
- Historical analysis of extremist propaganda can be educational.
- Teaching cybersecurity students how SQL injection works defensively can be educational.
- Instructions that meaningfully facilitate exploiting real systems are harmful.
- Medical education about suicide risk can be educational.
- Presenting suicide as a desirable or rational solution is harmful.

Determine:
1. Whether the content itself provides substantive academic learning.
2. Whether it contains harmful or inappropriate content.
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

If harmful content is present, category must describe the harmful
content itself, even if the content is also non-educational.

For example:
- extremist endorsement → extremism
- actionable cyber exploitation → dangerous_activity
- explicit sexual material → sexual
- suicide encouragement → self_harm

Use non_educational ONLY when the primary problem is that the
content is not genuinely educational and it is not otherwise harmful.

Return only the requested structured output.

Keep the reason concise: one sentence and no more than 25 words.

"""


SCHEMA = {
    "type": "object",
    "properties": {
        "educational": {
            "type": "boolean"
        },
        "harmful": {
            "type": "boolean"
        },
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
                "other"
            ]
        },
        "reason": {
            "type": "string"
        }
    },
    "required": [
        "educational",
        "harmful",
        "category",
        "reason"
    ],
    "additionalProperties": False
}


def moderate_chunk(text: str) -> dict:
    """
    Send one text chunk to the configured Qwen moderation model.
    """

    payload = {
        "model": "Qwen3-4B-Instruct-2507-Q4_K_M.gguf",
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"""
Classify this content for StudyBuddy.

IMPORTANT:

The question is NOT:
"Does this content talk about education or an academic program?"

The question is:
"Does this content itself teach, explain, demonstrate, provide practice,
or provide substantive academic reference knowledge to the reader?"

Classify as educational ONLY when the content itself functions as
learning material.

Do NOT classify as educational merely because the content:
- describes a university or college
- describes a degree or academic program
- discusses faculty, students, campus, facilities, or placements
- promotes admissions or recruitment
- advertises a course or educational opportunity
- uses educational terminology

Examples of NON-EDUCATIONAL content:
- college brochures
- university prospectuses
- admission material
- institutional profiles
- course advertisements
- placement/marketing material
- travel guides
- vacation recommendations
- restaurant recommendations
- recipes
- personal blogs
- general lifestyle advice
- entertainment content

The following is the content to classify:

--- CONTENT START ---
{text}
--- CONTENT END ---
"""
            }
        ],
        "temperature": 0,
        "max_tokens": 250,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "moderation_result",
                "schema": SCHEMA
            }
        }
    }

    response = requests.post(
        LLM_URL,
        json=payload,
        headers=_llm_headers(),
        timeout=120
    )

    response.raise_for_status()

    data = response.json()
    content = data["choices"][0]["message"]["content"]

    return json.loads(content)


RISK_SCAN_SCHEMA = {
    "type": "object",
    "properties": {
        "risk": {
            "type": "boolean"
        },
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
                "other"
            ]
        },
        "evidence": {
            "type": "string"
        }
    },
    "required": [
        "risk",
        "category",
        "evidence"
    ],
    "additionalProperties": False
}


RISK_SCAN_PROMPT = """
You are the secondary safety reviewer for StudyBuddy, an educational
resource moderation system.

Your task is ONLY to determine whether the provided text contains
harmful or inappropriate content.

Do NOT reject content merely because it discusses a sensitive topic.

Academic discussion is allowed, including:
- history of extremist or authoritarian movements
- political science
- propaganda analysis
- cybersecurity vulnerabilities
- medical sexual health
- suicide prevention
- dangerous technologies studied academically

However, academic framing does NOT make harmful advocacy acceptable.

Mark risk=true when the text:
- promotes, endorses, glorifies, or recommends harmful ideology or behavior
- encourages suppression, persecution, violence, or removal of opponents
- advocates extremist or authoritarian ideology as desirable
- meaningfully encourages harmful real-world action
- provides actionable instructions that facilitate wrongdoing
- presents harmful behavior as something people should adopt, imitate,
  or support

IMPORTANT DISTINCTION:

DESCRIPTION / ANALYSIS:
"Historians study how authoritarian governments suppressed opposition."
→ risk=false

ENDORSEMENT / ADVOCACY:
"Modern governments should restrict opposition and give strong leaders
broad authority to suppress political disagreement."
→ risk=true

The text does NOT need to explicitly use labels such as
"fascist", "extremist", or "terrorist" for endorsement to count as risk.

When judging political or ideological material, distinguish:
1. describing or analyzing an ideology
2. neutrally comparing political systems
3. advocating that people or governments adopt harmful principles

Only the third should be marked harmful.

Return ONLY valid JSON matching the supplied schema.
"""


def scan_chunk_risk(text: str) -> dict:
    """
    First-pass scan for potentially harmful content.

    This does not determine the final moderation decision.
    """

    payload = {
        "model": "Qwen3-4B-Instruct-2507-Q4_K_M.gguf",
        "messages": [
            {
                "role": "system",
                "content": RISK_SCAN_PROMPT
            },
            {
                "role": "user",
                "content": f"""
Scan the following text for potentially harmful content.

--- CONTENT START ---
{text}
--- CONTENT END ---
"""
            }
        ],
        "temperature": 0.1,
        "max_tokens": 200,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "risk_scan_result",
                "schema": RISK_SCAN_SCHEMA
            }
        }
    }

    response = requests.post(
        LLM_URL,
        json=payload,
        headers=_llm_headers(),
        timeout=120
    )

    response.raise_for_status()

    data = response.json()
    content = data["choices"][0]["message"]["content"]

    return json.loads(content)
