import re
from vello.core.models import ResponseStatus

# Regex patterns for intent detection
POSITIVE_PATTERNS = [
    r'\b(interested|yes|sure|sounds good|tell me more|let\'s talk|call me|schedule|meeting|demo)\b',
    r'\b(want to hear more|would like to|looking forward|excited|great)\b',
    r'\b(please send|send me|share more|more info|more information)\b',
    r'\b(i\'d like|i would like|i want to|keen to|happy to)\b',
]

NEGATIVE_PATTERNS = [
    r'\b(not interested|no thanks|unsubscribe|stop|remove me|don\'t contact)\b',
    r'\b(no longer|not right now|not at this time|pass|decline)\b',
    r'\b(already have|not looking|not needed)\b',
]

UNSUBSCRIBE_PATTERNS = [
    r'\b(unsubscribe|opt out|remove|stop emailing|stop sending)\b',
]

def analyze_intent(text: str) -> ResponseStatus:
    """
    Analyze the intent of an email response using regex patterns.

    Args:
        text: The email response text

    Returns:
        ResponseStatus enum value
    """
    if not text:
        return ResponseStatus.PENDING

    text_lower = text.lower()

    # Check for unsubscribe first (highest priority)
    # If unsubscribe is detected, return immediately without checking positive/negative
    # This ensures unsubscribe requests are handled separately from sentiment analysis
    for pattern in UNSUBSCRIBE_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return ResponseStatus.UNSUBSCRIBED

    # Check for negative intent (only if unsubscribe not detected)
    for pattern in NEGATIVE_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return ResponseStatus.NEGATIVE

    # Check for positive intent
    for pattern in POSITIVE_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return ResponseStatus.POSITIVE

    # Default to pending if no clear intent
    return ResponseStatus.PENDING
