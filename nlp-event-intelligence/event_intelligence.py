"""
event_intelligence.py
----------------------
Answers ONE question only: "Does this report belong to an existing
real-world event, or should a new one be created?"

Core idea (from the project spec):

    NEW REPORT
        -> compare with existing events
        -> calculate similarity (type + location + time + semantic)
        -> above threshold?  UPDATE existing event
        -> below threshold?  CREATE new event

No sentence-transformers here (no reliable internet to download the
model on this machine right now), so semantic similarity uses
TF-IDF + cosine similarity from scikit-learn, which ships locally
and needs no download. It's the simplest thing that demonstrates
"different words, similar meaning" for short disaster sentences,
per the "do not overengineer" rule in the spec. Swappable later.
"""

from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import MATCH_THRESHOLD, TIME_WINDOW_HOURS, WEIGHTS
from models import Event, Report


def _semantic_similarity(text_a: str, text_b: str) -> float:
    """
    TF-IDF cosine similarity between two short texts.
    Returns 0.0-1.0. Fit fresh each call -- these are single short
    sentences, so this is cheap and avoids needing a shared,
    growing vocabulary/model to manage.
    """
    try:
        vec = TfidfVectorizer(stop_words="english")
        matrix = vec.fit_transform([text_a, text_b])
        sim = cosine_similarity(matrix[0], matrix[1])[0][0]
        return float(sim)
    except ValueError:
        # happens if both texts are only stopwords / empty after cleaning
        return 0.0


def _time_similarity(time_a: datetime, time_b: datetime) -> float:
    """
    1.0 = same moment, decaying linearly to 0.0 at TIME_WINDOW_HOURS
    apart or more. Reports close together in time are more likely
    to describe the same ongoing event (per spec).
    """
    diff_hours = abs((time_a - time_b).total_seconds()) / 3600
    if diff_hours >= TIME_WINDOW_HOURS:
        return 0.0
    return 1.0 - (diff_hours / TIME_WINDOW_HOURS)


def _location_similarity(loc_a, loc_b) -> float:
    """Exact match only for the MVP -- see README for why."""
    if not loc_a or not loc_b:
        return 0.0
    return 1.0 if loc_a.strip().lower() == loc_b.strip().lower() else 0.0


def _type_similarity(type_a, type_b) -> float:
    if not type_a or not type_b:
        return 0.0
    return 1.0 if type_a == type_b else 0.0


def compute_match_score(report: Report, event: Event) -> dict:
    """
    Compares one new report against one existing event and returns
    a breakdown + final weighted score. Returning the breakdown
    (not just the final number) is deliberate: it's what makes this
    matching system "explainable" per the spec, and it's what you'll
    show the jury.

    Two HARD GATES come before the weighted average, because on
    short texts, word-overlap (semantic_score) can look deceptively
    high even when the report is clearly a different event -- e.g.
    "Flooding reported in Vijayawada." vs "Fire reported in
    Vijayawada." share 2 of 3 non-stopwords, which alone would push
    the weighted score above threshold even though the spec is
    explicit that FLOOD + FIRE "probably" means a different event:

      1. Disaster type must match. A flood report can never update
         a fire event, no matter how similar the wording is.
      2. Reports more than TIME_WINDOW_HOURS apart can't be
         considered part of the same ongoing event, even if type,
         location and wording all match -- an identical-sounding
         report a day and a half later is treated as a fresh
         situation, not proof the old one is still active.

    Only reports that pass both gates get scored by the weighted
    formula below.
    """
    type_score = _type_similarity(report.disaster_type, event.disaster_type)
    time_score = _time_similarity(report.timestamp, event.last_report_time)

    location_score = _location_similarity(report.location, event.location)
    representative_text = event.reports[-1].text if event.reports else ""
    semantic_score = _semantic_similarity(report.text, representative_text)

    breakdown = {
        "event_id": event.event_id,
        "type_score": round(type_score, 2),
        "location_score": round(location_score, 2),
        "time_score": round(time_score, 2),
        "semantic_score": round(semantic_score, 2),
    }

    if type_score == 0.0:
        breakdown["final_score"] = 0.0
        breakdown["gate"] = "blocked: disaster type mismatch"
        return breakdown

    if time_score == 0.0:
        breakdown["final_score"] = 0.0
        breakdown["gate"] = "blocked: outside time window"
        return breakdown

    final_score = (
        WEIGHTS["type"] * type_score
        + WEIGHTS["location"] * location_score
        + WEIGHTS["time"] * time_score
        + WEIGHTS["semantic"] * semantic_score
    )
    breakdown["final_score"] = round(final_score, 2)
    return breakdown


def compute_severity(report: Report) -> str:
    """
    Rule-based severity, built only from signals the NLP extractor
    actually found (per spec: "use information provided by AI/ML
    and extracted NLP signals", don't invent a new scoring system).
    """
    high_signals = [
        report.people_stranded,
        report.evacuation,
        report.infrastructure_damage,
        (report.deaths or 0) > 0,
        (report.injuries or 0) > 0,
    ]
    medium_signals = [report.houses_affected, report.road_blocked, report.people_affected]

    if any(high_signals):
        return "HIGH"
    if any(medium_signals):
        return "MEDIUM"
    return "LOW"


def compute_event_confidence(report: Report, match: dict, event: Event) -> float:
    """
    Explainable MVP confidence -- NOT a validated probability
    (per spec's explicit warning about this).

    Combines:
      - the AI/ML team's confidence that this report is a real disaster
      - how well this report matched the event (type/location/time/semantic)
      - a small bonus for source diversity and report count, since
        multiple independent sources agreeing is stronger evidence
        than repeats from one source (per spec's MULTIPLE SOURCES section)
    """
    ai_conf = report.ai_confidence or 0.5
    match_conf = match["final_score"]

    base = 0.6 * ai_conf + 0.4 * match_conf

    diversity_bonus = min(0.05 * len(event.sources_seen), 0.15)
    count_bonus = min(0.02 * event.report_count, 0.10)

    return min(base + diversity_bonus + count_bonus, 0.99)


class EventStore:
    """
    In-memory store of active events for the MVP demo.
    The real backend will own persistence -- this class exists so
    you (NLP/Event Intelligence) can develop and test your logic
    completely independently before the backend is wired up.
    """

    def __init__(self):
        self.events: dict[str, Event] = {}
        self._next_id = 1

    def _new_event_id(self) -> str:
        eid = f"EVENT-{self._next_id:03d}"
        self._next_id += 1
        return eid

    def find_best_match(self, report: Report):
        """
        Compares the report against every ACTIVE event and returns
        (best_event, best_match_dict) or (None, None) if no active
        events exist yet or none score above threshold.
        """
        best_event = None
        best_match = None

        for event in self.events.values():
            if event.status != "ACTIVE":
                continue
            match = compute_match_score(report, event)
            if best_match is None or match["final_score"] > best_match["final_score"]:
                best_event, best_match = event, match

        if best_match and best_match["final_score"] >= MATCH_THRESHOLD:
            return best_event, best_match
        return None, best_match  # best_match returned anyway, for logging/explainability

    def process_report(self, report: Report) -> dict:
        """
        Main entry point. Implements:

            compare -> match? -> UPDATE : CREATE

        Returns a result dict matching the API INTEGRATION section
        of the spec, e.g.:
            {"action": "CREATE", "event_id": "EVENT-002", "event_confidence": 0.89}
        """
        matched_event, match_info = self.find_best_match(report)

        if matched_event:
            action = "UPDATE"
            event = matched_event
            event.report_count += 1
            event.last_report_time = report.timestamp
            event.sources_seen.add(report.source)
            event.reports.append(report)
        else:
            action = "CREATE"
            event = Event(
                event_id=self._new_event_id(),
                disaster_type=report.disaster_type,
                location=report.location,
                first_report_time=report.timestamp,
                last_report_time=report.timestamp,
                report_count=1,
            )
            event.sources_seen.add(report.source)
            event.reports.append(report)
            self.events[event.event_id] = event
            # give it a neutral self-match dict for confidence calc
            match_info = {"final_score": report.ai_confidence or 0.5}

        event.severity = compute_severity(report)
        event.event_confidence = compute_event_confidence(report, match_info, event)

        return {
            "action": action,
            "event_id": event.event_id,
            "event_confidence": round(event.event_confidence, 2),
            "match_breakdown": match_info,
            "event": event.to_dict(),
        }
