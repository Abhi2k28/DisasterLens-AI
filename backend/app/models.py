from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from datetime import datetime

from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100))
    text = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    location = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    disaster_type = Column(String(50), nullable=True)
    severity = Column(String(50), nullable=True)
    confidence = Column(Float, nullable=True)

class DisasterEvent(Base):
    __tablename__ = "disaster_events"

    id = Column(Integer, primary_key=True, index=True)
    disaster_type = Column(String(50))
    location = Column(String(255))
    severity = Column(String(50))
    confidence = Column(Float)
    report_count = Column(Integer, default=1)
    first_detected = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    status = Column(String(50), default="ACTIVE")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, nullable=False)
    message = Column(String(500), nullable=False)
    severity = Column(String(50), nullable=False)
    status = Column(String(50), default="ACTIVE")