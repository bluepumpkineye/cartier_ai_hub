import re

BLOCKED_PATTERNS = [
    r"\b(competitor|LVMH secret|Richemont secret|confidential pricing)\b",
    r"\b(hack|exploit|bypass|jailbreak)\b",
    r"\b(personal data dump|export all clients)\b",
]

BRAND_TONE_VIOLATIONS = [
    "cheap", "discount", "bargain", "sale price", "knock-off", "fake"
]


def check_input_guardrails(text: str) -> tuple:
    """
    Check user input for blocked content.
    Returns (is_safe: bool, reason: str)
    """
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return False, "⚠️ Query blocked: Contains restricted content."
    return True, "OK"


def check_output_guardrails(text: str) -> tuple:
    """
    Check LLM output for brand tone violations.
    Returns (is_safe: bool, message: str)
    """
    for word in BRAND_TONE_VIOLATIONS:
        if word in text.lower():
            return False, f"Output flagged: Contains off-brand term '{word}'"
    return True, text


def sanitize_response(text: str) -> str:
    """Remove PII patterns from LLM output."""
    # Redact email addresses
    text = re.sub(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        '[EMAIL REDACTED]',
        text
    )
    # Redact phone numbers
    text = re.sub(
        r'\+?[\d\s\-\(\)]{10,15}',
        '[PHONE REDACTED]',
        text
    )
    return text