from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Alert

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    return db.query(Alert).all()


@router.get("/alerts/{alert_id}")
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(
        Alert.id == alert_id
    ).first()

    if not alert:
        return {"message": "Alert not found"}

    return {
        "id": alert.id,
        "event_id": alert.event_id,
        "message": alert.message,
        "severity": alert.severity,
        "status": alert.status
    }


@router.put("/alerts/{alert_id}/deactivate")
def deactivate_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    alert = db.query(Alert).filter(
        Alert.id == alert_id
    ).first()

    if not alert:
        return {"message": "Alert not found"}

    alert.status = "INACTIVE"

    db.commit()
    db.refresh(alert)

    return {
        "message": "Alert deactivated successfully",
        "alert_id": alert.id,
        "status": alert.status
    }