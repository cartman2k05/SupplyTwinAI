from datetime import datetime
from pydantic import BaseModel, Field

class AgentConfigUpdate(BaseModel):
    risk_weight_supplier: float = Field(..., ge=0.0, le=1.0)
    risk_weight_shipment: float = Field(..., ge=0.0, le=1.0)
    risk_weight_inventory: float = Field(..., ge=0.0, le=1.0)
    risk_weight_external: float = Field(..., ge=0.0, le=1.0)
    threshold_low_medium: float = Field(..., ge=0.0, le=100.0)
    threshold_medium_high: float = Field(..., ge=0.0, le=100.0)
    alert_threshold_recommendation: float = Field(..., ge=0.0, le=100.0)

class AgentConfigResponse(BaseModel):
    config_id: int
    risk_weight_supplier: float
    risk_weight_shipment: float
    risk_weight_inventory: float
    risk_weight_external: float
    threshold_low_medium: float
    threshold_medium_high: float
    alert_threshold_recommendation: float
    updated_by: str
    updated_at: datetime

    class Config:
        from_attributes = True
