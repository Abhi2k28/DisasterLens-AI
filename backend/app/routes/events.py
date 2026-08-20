from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import DisasterEvent

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/events")
def get_events(db: Session = Depends(get_db)):
    events = db.query(DisasterEvent).all()

    return [
        {
            "id": event.id,
            "disaster_type": event.disaster_type,
            "location": event.location,
            "severity": event.severity,
            "confidence": event.confidence,
            "report_count": event.report_count,
            "first_detected": event.first_detected,
            "last_updated": event.last_updated,
            "status": event.status
        }
        for event in events
    ]


# IMPORTANT: summary must come BEFORE /events/{event_id}
@router.get("/events/summary")
def get_event_summary(db: Session = Depends(get_db)):
    events = db.query(DisasterEvent).all()

    return {
        "total_events": len(events),
        "active_events": len(
            [event for event in events if event.status == "ACTIVE"]
        ),
        "high_severity_events": len(
            [event for event in events if event.severity == "HIGH"]
        )
    }


@router.get("/events/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(DisasterEvent).filter(
        DisasterEvent.id == event_id
    ).first()

    if not event:
        return {"message": "Event not found"}

    return {
        "id": event.id,
        "disaster_type": event.disaster_type,
        "location": event.location,
        "severity": event.severity,
        "confidence": event.confidence,
        "report_count": event.report_count,
        "first_detected": event.first_detected,
        "last_updated": event.last_updated,
        "status": event.status
    }