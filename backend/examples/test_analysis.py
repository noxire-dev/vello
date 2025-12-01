import sys
from pathlib import Path

# Add backend/src to path so we can import vello package
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from vello.core.models import ResponseStatus
from vello.services import analyze_intent


def test_intent_analysis():
    print("Testing intent analysis...\n")

    # Test positive responses
    positive_tests = [
        "Yes, I'm interested in learning more",
        "Sounds good, let's schedule a call",
        "Please send me more information",
        "I'd like to hear more about this",
        "Great! When can we meet?",
    ]

    print("Positive Intent Tests:")
    for text in positive_tests:
        result = analyze_intent(text)
        status = "✓" if result == ResponseStatus.POSITIVE else "✗"
        print(f"{status} '{text}' -> {result.value}")

    # Test negative responses
    negative_tests = [
        "Not interested, thanks",
        "No thanks, we already have a solution",
        "Not at this time",
        "Please don't contact me again",
        "We're not looking for this right now",
    ]

    print("\nNegative Intent Tests:")
    for text in negative_tests:
        result = analyze_intent(text)
        status = "✓" if result == ResponseStatus.NEGATIVE else "✗"
        print(f"{status} '{text}' -> {result.value}")

    # Test unsubscribe
    unsubscribe_tests = [
        "Please unsubscribe me",
        "Stop sending me emails",
        "Remove me from your list",
        "Opt out",
    ]

    print("\nUnsubscribe Tests:")
    for text in unsubscribe_tests:
        result = analyze_intent(text)
        status = "✓" if result == ResponseStatus.UNSUBSCRIBED else "✗"
        print(f"{status} '{text}' -> {result.value}")

    # Test pending (unclear intent)
    pending_tests = [
        "Thanks for reaching out",
        "Got it",
        "Ok",
        "",
    ]

    print("\nPending Intent Tests:")
    for text in pending_tests:
        result = analyze_intent(text)
        status = "✓" if result == ResponseStatus.PENDING else "✗"
        print(f"{status} '{text or '(empty)'}' -> {result.value}")

    print("\nAll tests completed!")

if __name__ == "__main__":
    test_intent_analysis()
