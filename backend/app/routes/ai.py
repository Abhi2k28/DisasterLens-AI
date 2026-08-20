from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_service import analyze_report

router = APIRouter()


class AnalyzeRequest(BaseModel):
    text: str


@router.post("/analyze")
def analyze(request: AnalyzeRequest):
    return analyze_report(request.text)