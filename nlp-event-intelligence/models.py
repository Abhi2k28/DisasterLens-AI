"""
models.py
---------
Plain data structures for a Report (a single incoming message) and
an Event (a real-world disaster situation made of 1+ reports).

Kept as dataclasses (not a database model) because for the MVP the
backend team owns storage -- we just need a clean, agreed-upon shape
to hand them. Field names match what's shown in the project spec's
EVENT OBJECT / REPORT OBJECT sections. Don't add fields the backend
hasn't agreed to.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Report:
    text: str
    disaster_type: Optional[str]
    ai_confidence: Optional[float]
    location: Optional[str]
    timestamp: datetime
    source: str = "demo"

    # NLP-extracted impact signals (None if not mentioned -- never guessed)
    houses_affected: Optional[bool] = None
    people_affected: Optional[bool] = None
    people_stranded: Optional[bool] = None
    road_blocked: Optional[bool] = None
    evacuation: Optional[bool] = None
    infrastructure_damage: Optional[bool] = None
    people_rescued: Optional[int] = None
    injuries: Optional[int] = None
    deaths: Optional[int] = None


@dataclass
class Event:
    event_id: str
    disaster_type: str
    location: Optional[str]
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    first_report_time: datetime = None
    last_report_time: datetime = None
    report_count: int = 0
    severity: str = "LOW"
    event_confidence: float = 0.0
    status: str = "ACTIVE"

    # Kept internally to support matching/merging -- not necessarily
    # sent to the backend as-is unless they want it.
    sources_seen: set = field(default_factory=set)
    reports: list = field(default_factory=list)  # list[Report]

    def to_dict(self):
        """Shape matches the EVENT OBJECT section of the project spec."""
        return {
            "event_id": self.event_id,
            "disaster_type": self.disaster_type,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "first_report_time": self.first_report_time.isoformat() if self.first_report_time else None,
            "last_report_time": self.last_report_time.isoformat() if self.last_report_time else None,
            "report_count": self.report_count,
            "severity": self.severity,
            "event_confidence": round(self.event_confidence, 2),
            "status": self.status,
        }
