from fastapi import FastAPI
from app.routes.reports import router as reports_router
from app.routes.ai import router as ai_router
from app.routes.events import router as events_router
from app.scheduler import start_scheduler, stop_scheduler
from app.routes.websocket import router as websocket_router
from app.routes.alerts import router as alerts_router
app = FastAPI()

start_scheduler()

app.include_router(reports_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
app.include_router(events_router, prefix="/api")
app.include_router(websocket_router, prefix="/api")
app.include_router(alerts_router, prefix="/api")

@app.get("/")
def home():
    return {"message": "DisasterLens AI Backend is running!"}