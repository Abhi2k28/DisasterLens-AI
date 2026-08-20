from app.database import SessionLocal
from app.models import Report, DisasterEvent, Alert
from app.services.ai_service import analyze_report
from app.demo_feed import get_demo_reports
import asyncio

from app.websocket import broadcast_event


def process_report(report_data):
    db = SessionLocal()

    try:
        # Analyze the report using AI
        ai_result = analyze_report(report_data["text"])

        # Create report
        new_report = Report(
            source=report_data["source"],
            text=report_data["text"],
            location=report_data["location"],
            latitude=report_data["latitude"],
            longitude=report_data["longitude"],
            disaster_type=ai_result["disaster_type"],
            severity=ai_result["severity"],
            confidence=ai_result["confidence"]
        )

        db.add(new_report)
        db.commit()
        db.refresh(new_report)

        # Create or update disaster event
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

                event_to_broadcast = existing_event

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
                db.flush()

                event_to_broadcast = new_event

            db.commit()

            # Create alert for HIGH severity events
            if event_to_broadcast.severity == "HIGH":
                alert = Alert(
                    event_id=event_to_broadcast.id,
                    message=(
                        f"HIGH severity "
                        f"{event_to_broadcast.disaster_type} "
                        f"detected at "
                        f"{event_to_broadcast.location}"
                    ),
                    severity=event_to_broadcast.severity,
                    status="ACTIVE"
                )

                db.add(alert)
                db.commit()

            # Send event update to connected WebSocket clients
            asyncio.run(broadcast_event(event_to_broadcast))

        return new_report

    finally:
        db.close()


def process_demo_feed():
    reports = get_demo_reports()

    for report in reports:
        process_report(report)

    return {
        "message": "Demo feed processed successfully",
        "reports_processed": len(reports)
    }