import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.config import settings

# Database URL formulation with SQLite fallback for local test environment
raw_url = settings.DATABASE_URL
sync_db_url = raw_url.replace("+asyncpg", "")

try:
    if "sqlite" in sync_db_url:
        engine = create_engine(sync_db_url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(sync_db_url, pool_pre_ping=True)
    # Test connection
    with engine.connect() as conn:
        pass
except Exception:
    # Fallback to local SQLite file for testing when local Postgres container is not running
    sqlite_url = "sqlite:///./supplytwin_dev.db"
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
