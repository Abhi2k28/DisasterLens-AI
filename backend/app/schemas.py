from pydantic import BaseModel


class ReportCreate(BaseModel):
    source: str
    text: str
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None

class ReportResponse(BaseModel):
    id: int
    source: str
    text: str
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    disaster_type: str | None = None
    severity: str | None = None
    confidence: float | None = None

    class Config:
        from_attributes = True