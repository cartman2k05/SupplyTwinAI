import pytest
from backend.app.db.database import engine, SessionLocal
from backend.app.db.base import Base
from backend.app.db_loader_helper import ensure_db_initialized

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_db_initialized(db)
    finally:
        db.close()
    yield
