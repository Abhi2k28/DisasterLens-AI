"""
model/classifier.py

WHAT THIS DOES:
Loads the zero-shot classification model (facebook/bart-large-mnli)
ONCE, and exposes a DisasterClassifier class that:
  1. Decides if a report is genuinely disaster-related vs not
     (handles cases like "I watched a movie about a flood")
  2. If disaster-related, predicts the disaster TYPE
     (flood, fire, earthquake, etc.)
  3. Returns an AI confidence score (NOT a guaranteed probability)
  4. Estimates severity using simple explainable keyword signals

WHY ZERO-SHOT:
We don't have a large labeled disaster dataset. Zero-shot
classification lets us use a model that was already trained to
understand "does this text entail this label" -- without us
training anything ourselves. We just give it candidate labels at
runtime.

IMPORTANT LIMITATIONS (see README):
- This model detects signals in TEXT. It does not detect real
  disasters. It does not guarantee a disaster is occurring.
- Confidence is "AI model confidence", not real-world probability.
- Severity is an MVP estimate, not an official emergency assessment.
"""

from transformers import pipeline

# ----------------------------------------------------------------
# Disaster type classes (from project spec — can be changed later)
# ----------------------------------------------------------------
DISASTER_CLASSES = [
    "flood",
    "fire",
    "earthquake",
    "landslide",
    "cyclone",
    "storm",
    "tsunami",
    "drought",
    "explosion",
    "other",
]

# Labels used for the FIRST-STAGE decision: is this text actually
# describing a real, ongoing/recent disaster event, or not?
# We phrase these as full sentences because NLI-based zero-shot
# models (like BART-MNLI) work better with natural sentence-style
# hypotheses than with single words.
RELEVANCE_LABELS = [
    "a real report describing an ongoing or recent disaster event",
    "not a real disaster event (movie, joke, unrelated, or metaphor)",
]

# Simple, explainable severity signal keywords (Rule 9 of spec).
# This is intentionally simple/rule-based for the MVP — not a model.
HIGH_SEVERITY_KEYWORDS = [
    "died", "death", "dead", "killed", "casualties",
    "trapped", "stranded", "evacuate", "evacuation",
    "collapsed", "destroyed", "missing", "rescue",
    "injured", "injuries", "critical", "emergency",
]

MEDIUM_SEVERITY_KEYWORDS = [
    "damage", "damaged", "blocked", "flooded", "affected",
    "disrupted", "power cut", "displaced", "warning",
]


class DisasterClassifier:
    def __init__(self, device: int = -1):
        """
        Load the zero-shot classification model ONCE.

        Args:
            device: -1 means CPU. If you have a working GPU set up
                    with CUDA, you could pass 0 instead. For the
                    hackathon MVP, CPU (-1) is fine and simplest.

        NOTE: The first time this runs, it will DOWNLOAD the
        facebook/bart-large-mnli model (~1.6 GB) from Hugging Face.
        This requires internet access and may take several minutes
        depending on your connection. After that, it is cached
        locally (usually in C:\\Users\\<you>\\.cache\\huggingface)
        and will NOT be re-downloaded on future runs.
        """
        print("Loading facebook/bart-large-mnli ... (first run may download ~1.6GB)")
        self.pipe = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=device,
        )
        print("Model loaded and ready.")

    def _check_relevance(self, text: str):
        """
        Stage 1: Is this text actually about a real disaster?
        Returns (is_disaster: bool, confidence: float)
        """
        result = self.pipe(text, candidate_labels=RELEVANCE_LABELS)
        top_label = result["labels"][0]
        top_score = float(result["scores"][0])
        is_disaster = top_label == RELEVANCE_LABELS[0]
        return is_disaster, top_score

    def _classify_type(self, text: str):
        """
        Stage 2: Which disaster type does this text describe?
        Returns (disaster_type: str, confidence: float)
        """
        result = self.pipe(text, candidate_labels=DISASTER_CLASSES)
        top_label = result["labels"][0].upper()
        top_score = float(result["scores"][0])
        return top_label, top_score

    def estimate_severity(self, text: str) -> str:
        """
        Simple explainable severity estimate (Rule 9).
        NOT a medical/official assessment -- just a keyword-based
        MVP heuristic so the demo has something reasonable to show.
        """
        lowered = text.lower()

        if any(word in lowered for word in HIGH_SEVERITY_KEYWORDS):
            return "HIGH"
        if any(word in lowered for word in MEDIUM_SEVERITY_KEYWORDS):
            return "MEDIUM"
        return "LOW"

    def classify(self, text: str) -> dict:
        """
        Full pipeline for one cleaned report.

        Returns a dict matching the structured output format from
        the project spec (Rule 13):

        {
            "is_disaster": bool,
            "disaster_type": str,
            "confidence": float,
            "severity": str,
            "text": str
        }
        """
        if not text or not text.strip():
            return {
                "is_disaster": False,
                "disaster_type": "OTHER",
                "confidence": 0.0,
                "severity": "LOW",
                "text": text,
            }

        is_disaster, relevance_conf = self._check_relevance(text)

        if not is_disaster:
            return {
                "is_disaster": False,
                "disaster_type": "OTHER",
                "confidence": round(relevance_conf, 2),
                "severity": "LOW",
                "text": text,
            }

        disaster_type, type_conf = self._classify_type(text)
        severity = self.estimate_severity(text)

        return {
            "is_disaster": True,
            "disaster_type": disaster_type,
            "confidence": round(type_conf, 2),
            "severity": severity,
            "text": text,
        }


if __name__ == "__main__":
    # Quick manual test:
    # COMMAND PROMPT:  python model/classifier.py
    clf = DisasterClassifier()

    sample_reports = [
        "Heavy flooding has entered several houses in Vijayawada.",
        "I watched a movie about a flood yesterday.",
    ]

    for report in sample_reports:
        output = clf.classify(report)
        print(output)
