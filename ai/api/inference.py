"""
api/inference.py

WHAT THIS DOES:
This is the "front door" of your AI/ML component. It:
  1. Loads the model ONCE when the app starts (Rule 16)
  2. Cleans incoming text
  3. Runs it through the classifier
  4. Adds timestamp + location so the output matches what the
     NLP/Event Intelligence teammate expects (Rule 14)
  5. Returns structured JSON

HOW YOUR TEAMMATES USE THIS FILE:
- NLP/Event Intelligence teammate: import `analyze_report()` and
  call it with raw text (+ optional location).
- Backend developer: wire this into whatever API framework they
  use (Flask/FastAPI). We do NOT assume the endpoint contract here
  (Rule 15) -- ask them for the real one. A minimal Flask example
  is included below, commented out, in case you need something
  runnable fast for the demo.
"""

import sys
import os
from datetime import datetime, timezone

# Allow importing sibling packages (model/, preprocessing/) when this
# file is run directly from the api/ folder.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preprocessing.cleaner import clean_text
from model.classifier import DisasterClassifier

# ----------------------------------------------------------------
# Load the model ONCE at import time (Rule 16: never reload per request)
# ----------------------------------------------------------------
_classifier = None


def get_classifier() -> DisasterClassifier:
    """
    Lazily create a single shared DisasterClassifier instance.
    Every call to analyze_report() reuses this same loaded model
    instead of reloading it.
    """
    global _classifier
    if _classifier is None:
        _classifier = DisasterClassifier()
    return _classifier


def analyze_report(raw_text: str, location: str = None) -> dict:
    """
    Full end-to-end analysis of one incoming report.

    Args:
        raw_text: the raw, unprocessed report text
        location: optional location string, if the data engineer's
                  pipeline already extracted one (otherwise None)

    Returns:
        dict matching the NLP/Event Intelligence handoff format
        (Rule 14):

        {
            "is_disaster": bool,
            "disaster_type": str,
            "confidence": float,
            "severity": str,
            "text": str,                # cleaned text
            "timestamp": str,            # ISO 8601 UTC
            "location": str or None
        }
    """
    clf = get_classifier()

    cleaned = clean_text(raw_text)
    result = clf.classify(cleaned)

    result["timestamp"] = datetime.now(timezone.utc).isoformat()
    result["location"] = location

    return result


def analyze_batch(raw_texts: list, locations: list = None) -> list:
    """
    Analyze multiple reports in one call.

    Args:
        raw_texts: list of raw report strings
        locations: optional list of locations, same length/order as
                   raw_texts. Pass None to skip.

    Returns:
        list of result dicts (same order as input)
    """
    if locations is None:
        locations = [None] * len(raw_texts)

    return [
        analyze_report(text, loc)
        for text, loc in zip(raw_texts, locations)
    ]


if __name__ == "__main__":
    # Quick manual test / demo:
    # COMMAND PROMPT:  python api/inference.py
    demo_reports = [
        ("Heavy flooding has entered several houses in Vijayawada.", "Vijayawada"),
        ("Large fire reported near Guntur railway station.", "Guntur"),
        ("Strong earthquake felt in Visakhapatnam.", "Visakhapatnam"),
        ("I watched a movie about an earthquake.", None),
    ]

    for text, loc in demo_reports:
        output = analyze_report(text, loc)
        print(output)


# ----------------------------------------------------------------
# OPTIONAL: minimal Flask wrapper (commented out).
# Uncomment and `pip install flask` if you need a quick runnable
# API endpoint for the demo before the real backend contract is
# defined. Confirm the real route/contract with your backend
# developer (Rule 15) before relying on this.
# ----------------------------------------------------------------
#
# from flask import Flask, request, jsonify
#
# app = Flask(__name__)
#
# @app.route("/api/analyze", methods=["POST"])
# def analyze_endpoint():
#     data = request.get_json()
#     text = data.get("text", "")
#     location = data.get("location")
#     result = analyze_report(text, location)
#     return jsonify(result)
#
# if __name__ == "__main__":
#     app.run(debug=True, port=5000)
