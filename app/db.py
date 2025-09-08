# Database connection and session management

# ...existing code...
from sqlalchemy import create_engine
from app.core.config import settings  # assuming you load DATABASE_URL from settings
from app.core.database import Base

engine = create_engine(settings.DATABASE_URL, echo=True)

# Create all tables
Base.metadata.create_all(bind=engine)

