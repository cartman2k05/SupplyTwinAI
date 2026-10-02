from datetime import datetime
from pydantic import BaseModel
from typing import Dict, Any

class ETLLoadResponse(BaseModel):
    status: str
    duration_seconds: float
    seed: int
    counts: Dict[str, int]

class ETLRunResponse(BaseModel):
    run_id: int
    seed: int
    raw_file_name: str
    loaded_records: int
    rejected_records: int
    flagged_records: int
    duration_seconds: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
