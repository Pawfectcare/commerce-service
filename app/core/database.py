import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    logger.info("Database connection pool initialized successfully.")
except Exception as e:
    logger.error(f"Failed to create database connection pool: {e}")
    raise

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
