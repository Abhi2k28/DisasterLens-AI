from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Report, DisasterEvent
from app.schemas import ReportCreate, ReportResponse
from app.services.ai_service import analyze_report

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/reports")
def get_reports(db: Session = Depends(get_db)):
    return db.query(Report).all()


@router.post("/reports", response_model=ReportResponse)
def create_report(report: ReportCreate, db: Session = Depends(get_db)):
    new_report = Report(
        source=report.source,
        text=report.text,
        location=report.location,
        latitude=report.latitude,
        longitude=report.longitude
    )

    # Send report text to AI
    ai_result = analyze_report(report.text)

    # Save AI results
    new_report.disaster_type = ai_result["disaster_type"]
    new_report.severity = ai_result["severity"]
    new_report.confidence = ai_result["confidence"]

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    # Create or update a disaster event
    if ai_result["is_disaster"]:

     existing_event = db.query(DisasterEvent).filter(
        DisasterEvent.disaster_type == ai_result["disaster_type"],
        DisasterEvent.location == ai_result["location"],
        DisasterEvent.status == "ACTIVE"
    ).first()

    if existing_event:
        existing_event.report_count += 1
        existing_event.confidence = max(
            existing_event.confidence,
            ai_result["confidence"]
        )
        existing_event.severity = ai_result["severity"]

    else:
        new_event = DisasterEvent(
            disaster_type=ai_result["disaster_type"],
            location=ai_result["location"],
            severity=ai_result["severity"],
            confidence=ai_result["confidence"],
            report_count=1,
            status="ACTIVE"
        )

        db.add(new_event)

    db.commit()

    return new_report