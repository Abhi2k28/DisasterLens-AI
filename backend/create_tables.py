from app.database import engine, Base
from app.models import Report, DisasterEvent

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")