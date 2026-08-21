"""
nlp_extractor.py
----------------
Answers ONE question only: "What useful information is present in
this report?"

It does NOT decide whether something is a real disaster (that's
AI/ML's job) and it does NOT decide whether two reports are the same
event (that's event_intelligence.py's job). Keeping this separation
is intentional -- see the project spec's "MOST IMPORTANT CONCEPT".

No spaCy here: this sandbox / your laptop can't reliably reach the
internet to download spaCy's language model right now, so this uses
regex + keyword matching, which is explainable, fast, and dependency
-light -- a good fit for an 8-hour MVP anyway. You can swap in spaCy
later without changing anything outside this file, as long as
extract_all() keeps returning the same dictionary shape.
"""

import re
from config import KNOWN_PLACES, IMPACT_KEYWORDS, DISASTER_KEYWORDS, NON_EVENT_HINTS


# ---------------------------------------------------------------
# LOCATION EXTRACTION
# ---------------------------------------------------------------
_LOCATION_PATTERN = re.compile(
    r"\b(?:in|near|at|from)\s+([A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)?)"
)


def extract_location(text: str):
    """
    Looks for a capitalized place name after words like
    'in', 'near', 'at', 'from'.

    Example:
        "Heavy flooding reported near Vijayawada." -> "Vijayawada"
        "Flooding reported in the northern region." -> None
            (regex would catch "Northern Region", but neither word
             is a real place, so we fall through to the gazetteer
             check below and return None instead of guessing)

    Returns None if nothing usable is found -- we NEVER invent a
    location.
    """
    matches = _LOCATION_PATTERN.findall(text)

    # Prefer a match that's a known place (higher trust)
    for m in matches:
        if m in KNOWN_PLACES:
            return m

    # Also check known places directly, in case the sentence
    # structure didn't match the preposition pattern
    for place in KNOWN_PLACES:
        if place.lower() in text.lower():
            return place

    # If regex found *something* capitalized after a location
    # preposition but it's not in our gazetteer, we still return it
    # (better than nothing for an MVP demo) -- but a real system
    # would mark this "unverified" for the backend/frontend to flag.
    if matches:
        return matches[0]

    return None


# ---------------------------------------------------------------
# IMPACT / ENTITY EXTRACTION
# ---------------------------------------------------------------
_NUMBER_RESCUED = re.compile(r"(\d+)\s+(?:people|persons|residents)\s+(?:were\s+)?rescued", re.I)
_NUMBER_INJURED = re.compile(r"(\d+)\s+(?:people|persons)?\s*injured", re.I)
_NUMBER_DEAD = re.compile(r"(\d+)\s+(?:people|persons)?\s*(?:dead|died|killed)", re.I)


def extract_impacts(text: str):
    """
    Scans for impact keywords and numeric entities.
    Every field defaults to None (unknown) -- we only set True/a
    number when the text actually supports it. This matches the
    project rule: "Do not assume information that is not present."
    """
    lower = text.lower()
    impacts = {field: None for field in IMPACT_KEYWORDS}

    for field, keywords in IMPACT_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            impacts[field] = True

    rescued = _NUMBER_RESCUED.search(text)
    injured = _NUMBER_INJURED.search(text)
    dead = _NUMBER_DEAD.search(text)

    impacts["people_rescued"] = int(rescued.group(1)) if rescued else None
    impacts["injuries"] = int(injured.group(1)) if injured else None
    impacts["deaths"] = int(dead.group(1)) if dead else None

    return impacts


# ---------------------------------------------------------------
# TEMPORARY disaster-type stub (stand-in for AI/ML teammate)
# ---------------------------------------------------------------
def classify_disaster_type_stub(text: str):
    """
    THIS IS NOT THE REAL CLASSIFIER.

    The AI/ML teammate owns "is this a disaster, and what type?".
    This stub exists only so you can run the full pipeline
    end-to-end today, for your own testing and the demo dry-run.
    Delete/replace this the moment their module is ready --
    just make sure whatever replaces it returns
    (disaster: bool, disaster_type: str|None, confidence: float)
    so the rest of the pipeline doesn't need to change.
    """
    lower = text.lower()

    # crude false-positive guard, matches the FALSE POSITIVE TESTING
    # section of the spec (movie/documentary/casual "flooded me")
    if any(hint in lower for hint in NON_EVENT_HINTS):
        return False, None, 0.05

    for dtype, keywords in DISASTER_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return True, dtype, 0.90

    return False, None, 0.10


# ---------------------------------------------------------------
# PUBLIC ENTRY POINT
# ---------------------------------------------------------------
def extract_all(text: str):
    """
    Runs every NLP extractor and returns one dictionary.
    This is the function the backend / event_intelligence module
    should call.
    """
    location = extract_location(text)
    impacts = extract_impacts(text)

    result = {
        "location": location,
        **impacts,
    }
    return result


if __name__ == "__main__":
    # Quick manual check -- run with:  python nlp_extractor.py
    sample = "Heavy flooding has entered houses near Vijayawada."
    print("Input: ", sample)
    print("Extracted:", extract_all(sample))
