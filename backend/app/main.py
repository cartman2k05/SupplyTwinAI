from fastapi import FastAPI
from backend.app.config import settings
from backend.app.api.v1.router import api_v1_router
from backend.app.db.database import engine, SessionLocal
from backend.app.db.base import Base
from backend.app.db_loader_helper import ensure_db_initialized

app = FastAPI(
    title="SupplyTwinAI API",
    description="Autonomous Multi-Agent Supply Chain Digital Twin REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include Versioned API Routes under /api/v1
app.include_router(api_v1_router)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_db_initialized(db)
    finally:
        db.close()

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "system": "SupplyTwinAI Backend",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
