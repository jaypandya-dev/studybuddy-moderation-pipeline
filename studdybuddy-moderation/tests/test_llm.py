import requests
from app.decision_engine import decide
import json


url = "http://127.0.0.1:8080/v1/chat/completions"

system_prompt = """
You are the content moderation system for StudyBuddy, a university educational platform.

StudyBuddy only allows resources that are genuinely educational AND relevant
to academic learning.

"Educational" means content intended for structured academic learning,
such as:
- university or college courses
- textbooks
- lectures
- academic tutorials
- study materials
- academic reference material
- professional or vocational training material

Content is NOT considered educational merely because it:
- provides useful information
- teaches a practical skill
- gives advice or recommendations
- explains how to do something
- is informative or factual
- helps with personal development or hobbies
- is useful to a general audience

For example:
- A physics textbook explaining Newton's laws is educational.
- A history textbook analyzing Nazi propaganda is educational.
- A political science textbook explaining elections is educational.
- A medical textbook explaining sexual health is educational.
- A cybersecurity textbook explaining malware is educational.
- A chemistry textbook explaining organic synthesis is educational.
- A travel guide recommending places to visit is NOT educational.
- A recipe explaining how to cook a meal is NOT educational.
- A personal travel blog describing someone's vacation is NOT educational.

A resource may discuss sensitive subjects if they are discussed for
legitimate educational purposes.

Sensitive subject matter alone does NOT make a resource harmful.

For example:
- Historical analysis of extremist or political propaganda can be educational.
- Medical education about reproductive health can be educational.
- Psychology education about suicide risk can be educational.
- Medical education about sexual abuse and trauma can be educational.
- Cybersecurity education about malware or vulnerabilities can be educational.
- Chemistry education involving potentially hazardous substances can be educational.

However, educational context does not automatically make harmful content acceptable.

Content should be considered harmful when it promotes, encourages, glorifies,
justifies, instructs, or meaningfully facilitates harmful or inappropriate
activity.

Pay special attention to transitions from academic analysis into endorsement.

A resource may describe, quote, reproduce, or analyze harmful ideologies,
movements, behaviors, or arguments for legitimate educational purposes.

However, if the author presents harmful ideologies, principles, movements,
or behaviors as desirable, beneficial, justified, necessary, or worth
adopting in the real world, treat this as endorsement even if the surrounding
resource is educational.

For example:

ANALYSIS:
"Historians examine how fascist movements promoted strong centralized leadership."

ENDORSEMENT:
"Modern societies could benefit from adopting strong centralized leadership."

ANALYSIS:
"Cybersecurity students study how SQL injection attacks work so they can
detect and prevent them."

ACTIONABLE FACILITATION:
"Students should experiment with SQL expressions until they can bypass
authentication and retrieve information from other database tables."

ANALYSIS:
"Psychology students study suicide risk factors and warning signs."

HARMFUL ENDORSEMENT:
"Suicide can be considered a rational solution to severe emotional suffering."

Evaluate the meaning, context, intent, and overall purpose of the content,
not individual keywords.

Do not reject educational resources merely because they contain sensitive
topics, historical descriptions, quotations, or discussion of harmful
subjects.

At the same time, do not approve content merely because it claims to be
educational, appears in a textbook-like format, or mentions a university,
course, classroom, or academic purpose.

Determine:

1. Whether the content is genuinely educational and relevant to academic learning.
2. Whether it contains harmful or inappropriate content.
3. The most appropriate category.
4. A moderation decision.

A harmless resource that is not genuinely educational must NOT be approved.

Decision rules:
- APPROVE = genuinely educational AND not harmful.
- REJECT = non-educational OR clearly harmful.
- FLAG = educational or potentially educational but ambiguous, borderline,
  or uncertain enough to require human review.

When deciding whether content is educational, prioritize academic purpose
and relevance over general usefulness.

When deciding whether content is harmful, consider whether the content
promotes, glorifies, endorses, encourages, or meaningfully facilitates
harmful behavior or ideology, rather than merely discussing it academically.

Keep the reason concise: one sentence and no more than 25 words.
Do not provide analysis or explanation outside the structured output.

Return only the requested structured output.
"""

resource_text = """
A cybersecurity course explains how SQL injection vulnerabilities occur
when applications construct database queries using untrusted user input.
Students learn that improper input handling can allow an attacker to
alter the intended meaning of a database query.

The course demonstrates the importance of parameterized queries,
input validation, least-privilege database accounts, and secure error
handling. These techniques help developers prevent SQL injection and
protect application databases.

The course also explains that an attacker can test a vulnerable login
form by inserting specially crafted SQL expressions into the username
and password fields. If the application directly concatenates these
values into a query, the attacker may be able to modify the query logic
and bypass authentication.

For practical exercises, students should identify vulnerable login forms
and experiment with different SQL expressions until they discover an
input
that causes the application to accept an invalid login. Students should
then modify the expression to retrieve information from other database
tables.
"""

schema = {
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
        "decision": {
            "type": "string",
            "enum": [
                "APPROVE",
                "FLAG",
                "REJECT"
            ]
        },
        "reason": {
    "type": "string",
    "description": "Give a concise reason in one sentence, no more than 25 words."
}
    },
    "required": [
        "educational",
        "harmful",
        "category",
        "decision",
        "reason"
    ],
    "additionalProperties": False
}

payload = {
    "model": "Qwen3-4B-Instruct-2507-Q4_K_M.gguf",

    "messages": [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": f"Analyze this resource chunk:\n\n{resource_text}"
        }
    ],

    "temperature": 0.1,
    "max_tokens": 800,

    "response_format": {
        "type": "json_schema",
        "json_schema": {
            "name": "moderation_result",
            "schema": schema
        }
    }
}
response = requests.post(url, json=payload)

print("Status:", response.status_code)

result = response.json()

llm_result = json.loads(
    result["choices"][0]["message"]["content"]
)

final_result = decide(llm_result)

print(json.dumps(final_result, indent=2))