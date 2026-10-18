import re


RISK_PATTERNS = {
    "sexual": [
        r"\bexplicit sexual\b",
        r"\bsexual intercourse\b",
        r"\bpornograph",
        r"\bsexual arousal\b",
        r"\bsexual stimulation\b",
    ],

    "hate": [
        r"\bracial superiority\b",
        r"\bethnic superiority\b",
        r"\bkill all\b",
        r"\bethnic cleansing\b",
        r"\bdehumaniz",
    ],

    "extremism": [
        r"\bfascist\b",
        r"\bnazi\b",
        r"\bwhite suprem",
        r"\bterrorist\b",
        r"\bterrorism\b",
        r"\bextremist\b",
        r"\bviolent jihad\b",
        r"\beliminate pluralism\b",
        r"\boverthrow the government\b",
    ],

    "political_propaganda": [
        r"\bglory of the (?:party|nation|leader)\b",
        r"\bjoin the movement\b",
        r"\benemies of the state\b",
        r"\bpolitical indoctrination\b",
    ],

    "violence": [
        r"\bhow to kill\b",
        r"\bhow to murder\b",
        r"\bsteps to attack\b",
        r"\bmake a bomb\b",
        r"\bbuild a bomb\b",
        r"\bexplosive device\b",
    ],

    "self_harm": [
        r"\bhow to commit suicide\b",
        r"\bsuicide instructions\b",
        r"\bhow to self[- ]harm\b",
        r"\bways to kill myself\b",
        r"\bencourage suicide\b",
    ],

    "drugs": [
        r"\bhow to make meth\b",
        r"\bhow to manufacture drugs\b",
        r"\bdrug synthesis instructions\b",
        r"\bhow to produce cocaine\b",
    ],

    "fraud": [
        r"\bsteal credentials\b",
        r"\bcredential theft\b",
        r"\bphishing instructions\b",
        r"\bhow to commit fraud\b",
        r"\bunauthorized access\b",
        r"\bstolen credit card\b",
    ],

    "harassment": [
        r"\btarget and harass\b",
        r"\borganized harassment\b",
        r"\bthreaten (?:him|her|them)\b",
        r"\bintimidate\b",
    ],

    "dangerous_activity": [
        r"\bsql injection\b",
        r"\bcommand injection\b",
        r"\bremote code execution\b",
        r"\bcredential dumping\b",
        r"\bbypass authentication\b",
        r"\bexploit a vulnerable\b",
        r"\bpayload\b",
        r"\bextract unauthorized data\b",
        r"\bexploit the system\b",
    ],
}


def prefilter_risk(text: str) -> dict:
    """
    Lightweight deterministic pre-filter.

    This function does NOT decide whether content is harmful.
    It only identifies text that deserves a second LLM safety pass.
    """

    normalized_text = text.lower()

    matches = []

    for category, patterns in RISK_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, normalized_text)

            if match:
                matches.append({
                    "category": category,
                    "matched_text": match.group(0),
                })

    return {
        "risk_signal": bool(matches),
        "matches": matches,
    }