"""
tests/test_classifier.py

WHAT THIS DOES:
Runs the exact test reports from the project spec (Rule 11 - real
disaster tests, Rule 12 - false positive tests) through the
classifier and prints a pass/fail-style summary.

WHY:
The spec explicitly says "Do not assume the model will always be
correct. Record actual results." This script makes it easy to
actually run and see real results instead of assuming.

HOW TO RUN:
COMMAND PROMPT:
    python tests/test_classifier.py

NOTE: This will load the real model, so it needs the model already
downloaded (or an internet connection to download it the first time).
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.inference import analyze_report


# Rule 11: real disaster reports, with the expected disaster type
REAL_DISASTER_TESTS = [
    ("Heavy flooding has entered several houses in Vijayawada.", "FLOOD"),
    ("Large fire reported near Guntur railway station.", "FIRE"),
    ("Strong earthquake felt in Visakhapatnam.", "EARTHQUAKE"),
    ("Large landslide blocks a road in the hills.", "LANDSLIDE"),
    ("I watched a movie about an earthquake.", "NON_DISASTER"),
]

# Rule 12: false-positive tests -- text that mentions disaster
# keywords but is NOT a real disaster report
FALSE_POSITIVE_TESTS = [
    "The fire in the movie was amazing.",
    "My friend flooded me with messages.",
    "That earthquake documentary was interesting.",
]


def run_real_disaster_tests():
    print("\n===== REAL DISASTER TESTS (Rule 11) =====")
    for text, expected in REAL_DISASTER_TESTS:
        result = analyze_report(text)
        actual = result["disaster_type"] if result["is_disaster"] else "NON_DISASTER"
        status = "MATCH" if actual == expected else "CHECK MANUALLY"
        print(f"\nInput   : {text}")
        print(f"Expected: {expected}")
        print(f"Actual  : {actual}  (is_disaster={result['is_disaster']}, "
              f"confidence={result['confidence']}, severity={result['severity']})")
        print(f"Result  : {status}")


def run_false_positive_tests():
    print("\n===== FALSE POSITIVE TESTS (Rule 12) =====")
    print("(We WANT is_disaster=False for these)")
    for text in FALSE_POSITIVE_TESTS:
        result = analyze_report(text)
        status = "GOOD (correctly rejected)" if not result["is_disaster"] else "FALSE POSITIVE - review"
        print(f"\nInput   : {text}")
        print(f"Actual  : is_disaster={result['is_disaster']}, "
              f"disaster_type={result['disaster_type']}, confidence={result['confidence']}")
        print(f"Result  : {status}")


if __name__ == "__main__":
    run_real_disaster_tests()
    run_false_positive_tests()
    print("\nDone. Review any 'CHECK MANUALLY' or 'FALSE POSITIVE' lines above --")
    print("zero-shot models are not always right, especially on the relevance")
    print("(disaster vs non-disaster) stage. If accuracy is poor, consider")
    print("rephrasing RELEVANCE_LABELS in model/classifier.py and re-testing.")
