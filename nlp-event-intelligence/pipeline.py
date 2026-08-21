"""
pipeline.py
-----------
Wires together (for demo/testing purposes only):

    raw text -> AI/ML stub (disaster type) -> NLP extraction -> Event Intelligence

In the real system, the backend calls AI/ML and NLP separately and
only sends YOUR module a report that's already been classified. This
file exists so you can test and demo your own part end-to-end without
waiting on teammates. See nlp_extractor.classify_disaster_type_stub
for why this stub is temporary.
"""

from datetime import datetime

from models import Report
from nlp_extractor import extract_all, classify_disaster_type_stub
from event_intelligence import EventStore


def process_raw_report(text: str, timestamp: datetime, source: str, store: EventStore) -> dict:
    """
    Full pipeline for ONE incoming report:
      1. (stub) classify disaster type -- normally AI/ML's job
      2. NLP extraction -- location + impact entities
      3. Event Intelligence -- match/create/update
    Returns the same result shape process_report() returns.
    """
    is_disaster, disaster_type, ai_confidence = classify_disaster_type_stub(text)

    nlp_data = extract_all(text)

    if not is_disaster:
        return {
            "action": "IGNORED",
            "reason": "Not classified as a disaster-related report",
            "text": text,
        }

    report = Report(
        text=text,
        disaster_type=disaster_type,
        ai_confidence=ai_confidence,
        location=nlp_data["location"],
        timestamp=timestamp,
        source=source,
        houses_affected=nlp_data["houses_affected"],
        people_affected=nlp_data["people_affected"],
        people_stranded=nlp_data["people_stranded"],
        road_blocked=nlp_data["road_blocked"],
        evacuation=nlp_data["evacuation"],
        infrastructure_damage=nlp_data["infrastructure_damage"],
        people_rescued=nlp_data["people_rescued"],
        injuries=nlp_data["injuries"],
        deaths=nlp_data["deaths"],
    )

    return store.process_report(report)
